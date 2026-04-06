#!/usr/bin/env python3
"""
社交媒体导出数据解析工具

支持平台:
  - 微博 (JSON 导出)
  - QQ空间 (HTML/JSON 导出)
  - 朋友圈 (文本导出)
  - 通用文本/Markdown

用法:
  python social_parser.py --input <file> --platform <weibo|qq|wechat_moments|text> --output <output.json>
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

# 情感关键词 (与其他解析器一致)
EMOTIONAL_KEYWORDS = [
    "想你", "爱你", "担心", "生气", "对不起", "注意身体",
    "吃了没", "冷不冷", "早点睡", "保重", "心疼", "想家",
    "辛苦了", "别累着", "好想你", "挂念", "牵挂", "舍不得",
    "抱歉", "原谅", "感谢", "谢谢你", "幸福", "开心",
    "难过", "伤心", "委屈", "害怕", "紧张", "加油",
    "照顾好自己", "别熬夜", "多喝水", "穿厚点", "路上小心",
    "想念", "思念", "珍惜", "感动", "温暖", "陪伴",
]

MAX_DAILY_MESSAGES = 200
LONG_MESSAGE_THRESHOLD = 50


def classify_message(text: str) -> str:
    """将内容分为三个层级"""
    if len(text) > LONG_MESSAGE_THRESHOLD:
        return "long"
    for kw in EMOTIONAL_KEYWORDS:
        if kw in text:
            return "emotional"
    return "daily"


def parse_timestamp(ts_str: str) -> str | None:
    """通用时间戳解析"""
    ts_str = ts_str.strip()
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y年%m月%d日 %H:%M",
        "%Y年%m月%d日 %H:%M:%S",
        "%a %b %d %H:%M:%S %z %Y",  # 微博格式: Tue Jan 15 14:30:22 +0800 2023
        "%m/%d/%Y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(ts_str, fmt)
            return dt.isoformat()
        except ValueError:
            continue

    # Unix 时间戳
    try:
        val = int(ts_str)
        if val > 1e12:
            val = val / 1000
        dt = datetime.utcfromtimestamp(val)
        return dt.isoformat()
    except (ValueError, OSError):
        pass
    return None


# ---------------------------------------------------------------------------
# 微博 JSON 解析
# ---------------------------------------------------------------------------

def parse_weibo(filepath: str) -> list[dict[str, Any]]:
    """解析微博 JSON 导出

    常见结构 (微博数据下载):
      [{"id": ..., "text": "...", "created_at": "...", "user": {...}}, ...]
    或
      {"statuses": [{"text": "...", "created_at": "..."}, ...]}
    """
    print(f"[social_parser] 解析微博 JSON: {filepath}")
    posts: list[dict[str, Any]] = []

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[social_parser] JSON 解析错误: {e}", file=sys.stderr)
            return []

    # 标准化: 找到帖子列表
    items = []
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        for key in ("statuses", "data", "weibo", "cards", "list", "posts"):
            if key in data and isinstance(data[key], list):
                items = data[key]
                break
        # 嵌套: data -> cards -> mblog
        if not items and "data" in data and isinstance(data["data"], dict):
            cards = data["data"].get("cards", [])
            for card in cards:
                if "mblog" in card:
                    items.append(card["mblog"])

    if not items:
        print("[social_parser] 警告: 未找到微博数据列表")
        return []

    for item in items:
        if not isinstance(item, dict):
            continue

        # 提取文本 — 多种字段名
        text = ""
        for text_key in ("text", "content", "status_text", "raw_text", "status"):
            if text_key in item and isinstance(item[text_key], str):
                text = item[text_key]
                break

        # 清理 HTML 标签
        text = re.sub(r"<[^>]+>", "", text).strip()

        if not text:
            continue

        # 提取时间
        ts_raw = ""
        for ts_key in ("created_at", "created_time", "time", "publish_time"):
            if ts_key in item:
                ts_raw = str(item[ts_key])
                break

        # 提取类型 (原创 / 转发 / 评论)
        post_type = "post"
        if item.get("retweeted_status") or item.get("retweet"):
            post_type = "retweet"

        posts.append({
            "text": text,
            "timestamp": parse_timestamp(ts_raw) if ts_raw else None,
            "type": post_type,
            "source": "weibo",
        })

    print(f"[social_parser] 从微博提取 {len(posts)} 条内容")
    return posts


# ---------------------------------------------------------------------------
# QQ空间解析
# ---------------------------------------------------------------------------

class QZoneHTMLParser(HTMLParser):
    """解析 QQ空间 HTML 导出"""

    def __init__(self):
        super().__init__()
        self.posts: list[dict[str, Any]] = []
        self._in_content = False
        self._in_time = False
        self._current_text = ""
        self._current_ts = ""

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class", "")
        if any(k in cls for k in ("content", "txt-box", "feed_text", "msgContent", "shuoshuo")):
            self._in_content = True
            self._current_text = ""
        elif any(k in cls for k in ("time", "date", "feed_time", "pubtime")):
            self._in_time = True
            self._current_ts = ""

    def handle_endtag(self, tag):
        if self._in_content and tag in ("div", "p", "span", "td"):
            self._in_content = False
            text = self._current_text.strip()
            if text:
                self.posts.append({
                    "text": text,
                    "timestamp": parse_timestamp(self._current_ts) if self._current_ts.strip() else None,
                    "type": "post",
                    "source": "qq",
                })
        elif self._in_time and tag in ("div", "p", "span", "td"):
            self._in_time = False

    def handle_data(self, data):
        if self._in_content:
            self._current_text += data
        elif self._in_time:
            self._current_ts += data


def parse_qq(filepath: str) -> list[dict[str, Any]]:
    """解析 QQ空间导出 (HTML 或 JSON)"""
    print(f"[social_parser] 解析 QQ空间: {filepath}")

    ext = Path(filepath).suffix.lower()

    # JSON 格式
    if ext == ".json":
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"[social_parser] JSON 解析错误: {e}", file=sys.stderr)
                return []

        items = data if isinstance(data, list) else data.get("data", data.get("msglist", []))
        posts = []
        for item in items:
            if not isinstance(item, dict):
                continue
            text = item.get("content", item.get("text", item.get("msg", "")))
            text = re.sub(r"<[^>]+>", "", str(text)).strip()
            if not text:
                continue
            ts_raw = item.get("created_time", item.get("time", item.get("pubtime", "")))
            posts.append({
                "text": text,
                "timestamp": parse_timestamp(str(ts_raw)) if ts_raw else None,
                "type": "post",
                "source": "qq",
            })
        print(f"[social_parser] 从 QQ空间 JSON 提取 {len(posts)} 条")
        return posts

    # HTML 格式
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    parser = QZoneHTMLParser()
    parser.feed(content)
    print(f"[social_parser] 从 QQ空间 HTML 提取 {len(parser.posts)} 条")
    return parser.posts


# ---------------------------------------------------------------------------
# 朋友圈文本解析
# ---------------------------------------------------------------------------

def parse_wechat_moments(filepath: str) -> list[dict[str, Any]]:
    """解析微信朋友圈文本导出

    常见格式:
      ---
      2023-01-15 14:30
      这是一条朋友圈
      [图片]
      ---

    或:
      【2023年1月15日】
      今天天气真好，出去散步了
    """
    print(f"[social_parser] 解析朋友圈: {filepath}")
    posts: list[dict[str, Any]] = []

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # 策略1: 以分隔线分割
    if "---" in content:
        blocks = content.split("---")
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            lines = block.split("\n")
            ts = None
            text_lines = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # 尝试解析为时间戳
                if not ts:
                    parsed = parse_timestamp(line)
                    if parsed:
                        ts = parsed
                        continue
                # 跳过 [图片] [视频] 等标记
                if re.match(r"^\[.{1,4}\]$", line):
                    continue
                text_lines.append(line)

            text = "\n".join(text_lines).strip()
            if text:
                posts.append({
                    "text": text,
                    "timestamp": ts,
                    "type": "moment",
                    "source": "wechat_moments",
                })

    # 策略2: 以日期开头的段落
    else:
        date_pattern = re.compile(
            r"^[【\[]?(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?)[】\]]?\s*$"
        )
        paragraphs = re.split(r"\n\s*\n", content)
        current_ts = None

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            lines = para.split("\n")
            first_line = lines[0].strip()

            m = date_pattern.match(first_line)
            if m:
                current_ts = parse_timestamp(m.group(1).replace("年", "-").replace("月", "-").replace("日", ""))
                text = "\n".join(l.strip() for l in lines[1:] if l.strip() and not re.match(r"^\[.{1,4}\]$", l.strip()))
            else:
                text = "\n".join(l.strip() for l in lines if l.strip() and not re.match(r"^\[.{1,4}\]$", l.strip()))

            if text:
                posts.append({
                    "text": text,
                    "timestamp": current_ts,
                    "type": "moment",
                    "source": "wechat_moments",
                })

    print(f"[social_parser] 从朋友圈提取 {len(posts)} 条")
    return posts


# ---------------------------------------------------------------------------
# 通用文本/Markdown
# ---------------------------------------------------------------------------

def parse_generic_text(filepath: str) -> list[dict[str, Any]]:
    """解析通用文本或 Markdown 文件

    每个段落 (空行分隔) 视为一条内容。
    如果段落首行是日期，提取为时间戳。
    """
    print(f"[social_parser] 解析通用文本: {filepath}")
    posts: list[dict[str, Any]] = []

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # 移除 Markdown 标题标记 (保留内容)
    content = re.sub(r"^#{1,6}\s+", "", content, flags=re.MULTILINE)

    paragraphs = re.split(r"\n\s*\n", content)

    date_line_pattern = re.compile(
        r"^[\[\(【]?(\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?)[\]\)】]?"
    )

    for para in paragraphs:
        para = para.strip()
        if not para or len(para) < 2:
            continue

        lines = para.split("\n")
        first_line = lines[0].strip()
        ts = None

        m = date_line_pattern.match(first_line)
        if m:
            ts = parse_timestamp(m.group(1))
            if ts and len(lines) > 1:
                # 日期行单独一行的情况
                text = "\n".join(l.strip() for l in lines[1:] if l.strip())
            elif ts:
                # 日期在同一行
                remainder = first_line[m.end():].strip()
                rest = "\n".join(l.strip() for l in lines[1:] if l.strip())
                text = f"{remainder}\n{rest}".strip() if remainder else rest
            else:
                text = para
        else:
            text = para

        if text:
            posts.append({
                "text": text,
                "timestamp": ts,
                "type": "post",
                "source": "text",
            })

    print(f"[social_parser] 从文本提取 {len(posts)} 条内容")
    return posts


# ---------------------------------------------------------------------------
# 分类与输出
# ---------------------------------------------------------------------------

def classify_and_output(
    posts: list[dict[str, Any]],
    platform: str,
    output_path: str,
) -> None:
    """对内容分层分类并输出 JSON"""
    if not posts:
        print("[social_parser] 警告: 没有提取到任何内容")
        result = {
            "platform": platform,
            "stats": {"total": 0},
            "messages": {"long": [], "emotional": [], "daily": []},
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"[social_parser] 已写入空结果到 {output_path}")
        return

    buckets: dict[str, list[dict[str, Any]]] = {"long": [], "emotional": [], "daily": []}
    for post in posts:
        tier = classify_message(post["text"])
        buckets[tier].append({
            "text": post["text"],
            "timestamp": post.get("timestamp"),
            "tier": tier,
            "type": post.get("type", "post"),
        })

    # 限制 daily
    if len(buckets["daily"]) > MAX_DAILY_MESSAGES:
        step = len(buckets["daily"]) / MAX_DAILY_MESSAGES
        buckets["daily"] = [buckets["daily"][int(i * step)] for i in range(MAX_DAILY_MESSAGES)]

    timestamps_sorted = sorted([p["timestamp"] for p in posts if p.get("timestamp")])
    lengths = [len(p["text"]) for p in posts]

    stats = {
        "total": len(posts),
        "long_count": len(buckets["long"]),
        "emotional_count": len(buckets["emotional"]),
        "daily_count": len(buckets["daily"]),
        "avg_length": round(sum(lengths) / len(lengths), 1) if lengths else 0,
        "date_range": {
            "earliest": timestamps_sorted[0] if timestamps_sorted else None,
            "latest": timestamps_sorted[-1] if timestamps_sorted else None,
        },
        "type_breakdown": {},
    }

    # 类型分布
    type_counts: dict[str, int] = {}
    for post in posts:
        t = post.get("type", "post")
        type_counts[t] = type_counts.get(t, 0) + 1
    stats["type_breakdown"] = type_counts

    result = {
        "platform": platform,
        "stats": stats,
        "messages": buckets,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[social_parser] 分类完成:")
    print(f"  平台: {platform}")
    print(f"  总内容数: {stats['total']}")
    print(f"  长内容: {stats['long_count']}")
    print(f"  情感内容: {stats['emotional_count']}")
    print(f"  日常内容: {stats['daily_count']}")
    print(f"  类型分布: {type_counts}")
    print(f"[social_parser] 结果已写入 {output_path}")


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

PLATFORM_PARSERS = {
    "weibo": parse_weibo,
    "qq": parse_qq,
    "wechat_moments": parse_wechat_moments,
    "text": parse_generic_text,
}


def main():
    parser = argparse.ArgumentParser(
        description="社交媒体导出数据解析工具 — 支持微博/QQ空间/朋友圈/通用文本"
    )
    parser.add_argument("--input", required=True, help="输入文件路径")
    parser.add_argument(
        "--platform",
        required=True,
        choices=list(PLATFORM_PARSERS.keys()),
        help="数据来源平台",
    )
    parser.add_argument("--output", required=True, help="输出 JSON 文件路径")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"[social_parser] 错误: 文件不存在 — {args.input}", file=sys.stderr)
        sys.exit(1)

    parse_fn = PLATFORM_PARSERS[args.platform]
    posts = parse_fn(args.input)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    classify_and_output(posts, args.platform, args.output)


if __name__ == "__main__":
    main()
