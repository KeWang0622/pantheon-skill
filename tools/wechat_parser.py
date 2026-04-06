#!/usr/bin/env python3
"""
微信聊天记录解析工具

支持格式:
  - TXT 导出 (WechatExporter / WeChatMsg / PyWxDump / 留痕)
  - HTML 导出
  - CSV 导出

用法:
  python wechat_parser.py --input <file> --target-name <name> --output <output.json>
"""

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

# 情感关键词列表
EMOTIONAL_KEYWORDS = [
    "想你", "爱你", "担心", "生气", "对不起", "注意身体",
    "吃了没", "冷不冷", "早点睡", "保重", "心疼", "想家",
    "辛苦了", "别累着", "好想你", "挂念", "牵挂", "舍不得",
    "抱歉", "原谅", "感谢", "谢谢你", "幸福", "开心",
    "难过", "伤心", "委屈", "害怕", "紧张", "加油",
    "照顾好自己", "别熬夜", "多喝水", "穿厚点", "路上小心",
    "到家了吗", "安全到了吗", "想念", "在吗", "你还好吗",
    "我错了", "别生气", "乖", "宝贝", "亲爱的",
]

# 每个层级最大消息数
MAX_DAILY_MESSAGES = 200
LONG_MESSAGE_THRESHOLD = 50


def classify_message(text: str) -> str:
    """将消息分为三个层级: long / emotional / daily"""
    if len(text) > LONG_MESSAGE_THRESHOLD:
        return "long"
    for kw in EMOTIONAL_KEYWORDS:
        if kw in text:
            return "emotional"
    return "daily"


def parse_timestamp(ts_str: str) -> str | None:
    """尝试多种格式解析时间戳，返回 ISO 格式字符串"""
    ts_str = ts_str.strip()
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%Y年%m月%d日 %H:%M:%S",
        "%Y年%m月%d日 %H:%M",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(ts_str, fmt)
            return dt.isoformat()
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# TXT 解析 — 支持多种导出工具的格式
# ---------------------------------------------------------------------------

# 常见 TXT 格式:
#   [2023-01-15 14:30:22] 张三:
#   消息内容
#
#   2023-01-15 14:30:22 张三
#   消息内容
#
#   张三 2023-01-15 14:30:22
#   消息内容

# 匹配模式: 时间戳在前 或 在后
_TXT_PATTERNS = [
    # [2023-01-15 14:30:22] Name:
    re.compile(
        r"^\[(\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}(?::\d{2})?)\]\s*(.+?)[:：]\s*$"
    ),
    # 2023-01-15 14:30:22 Name
    re.compile(
        r"^(\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}(?::\d{2})?)\s+(.+?)\s*$"
    ),
    # Name 2023-01-15 14:30:22
    re.compile(
        r"^(.+?)\s+(\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}(?::\d{2})?)\s*$"
    ),
    # 2023年01月15日 14:30:22 Name
    re.compile(
        r"^(\d{4}年\d{1,2}月\d{1,2}日\s+\d{1,2}:\d{2}(?::\d{2})?)\s+(.+?)\s*$"
    ),
]


def parse_txt(filepath: str, target_name: str) -> list[dict[str, Any]]:
    """解析 TXT 格式的微信聊天记录"""
    print(f"[wechat_parser] 解析 TXT 文件: {filepath}")
    messages: list[dict[str, Any]] = []
    current_sender: str | None = None
    current_ts: str | None = None
    current_lines: list[str] = []

    def flush():
        if current_sender and current_lines:
            text = "\n".join(current_lines).strip()
            if text and current_sender == target_name:
                messages.append({
                    "text": text,
                    "timestamp": current_ts,
                    "sender": current_sender,
                })

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            matched = False
            for i, pat in enumerate(_TXT_PATTERNS):
                m = pat.match(line)
                if m:
                    flush()
                    if i == 2:
                        # Name timestamp 格式
                        current_sender = m.group(1).strip()
                        current_ts = parse_timestamp(m.group(2))
                    else:
                        current_ts = parse_timestamp(m.group(1))
                        current_sender = m.group(2).strip()
                    current_lines = []
                    matched = True
                    break
            if not matched:
                current_lines.append(line)
        flush()

    print(f"[wechat_parser] 从 TXT 提取 {len(messages)} 条 {target_name} 的消息")
    return messages


# ---------------------------------------------------------------------------
# HTML 解析
# ---------------------------------------------------------------------------

class WeChatHTMLParser(HTMLParser):
    """解析微信 HTML 导出文件中的消息"""

    def __init__(self, target_name: str):
        super().__init__()
        self.target_name = target_name
        self.messages: list[dict[str, Any]] = []
        self._in_sender = False
        self._in_message = False
        self._in_time = False
        self._current_sender = ""
        self._current_text = ""
        self._current_ts = ""
        self._tag_stack: list[str] = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        cls = attr_dict.get("class", "")
        self._tag_stack.append(tag)

        # 常见 class 名: nickname / sender / msg_sender
        if any(k in cls for k in ("nickname", "sender", "msg_sender", "display_name")):
            self._in_sender = True
            self._current_sender = ""
        # 常见 class 名: message / msg_content / plain / content
        elif any(k in cls for k in ("message", "msg_content", "plain", "content", "msg_text")):
            self._in_message = True
            self._current_text = ""
        # 常见 class 名: time / timestamp / msg_time
        elif any(k in cls for k in ("time", "timestamp", "msg_time")):
            self._in_time = True
            self._current_ts = ""

    def handle_endtag(self, tag):
        if self._tag_stack:
            self._tag_stack.pop()

        if self._in_sender and tag in ("span", "div", "p"):
            self._in_sender = False
        elif self._in_message and tag in ("span", "div", "p", "td"):
            self._in_message = False
            if self._current_sender.strip() == self.target_name and self._current_text.strip():
                self.messages.append({
                    "text": self._current_text.strip(),
                    "timestamp": parse_timestamp(self._current_ts) if self._current_ts else None,
                    "sender": self._current_sender.strip(),
                })
        elif self._in_time and tag in ("span", "div", "p", "td"):
            self._in_time = False

    def handle_data(self, data):
        if self._in_sender:
            self._current_sender += data
        elif self._in_message:
            self._current_text += data
        elif self._in_time:
            self._current_ts += data


def parse_html(filepath: str, target_name: str) -> list[dict[str, Any]]:
    """解析 HTML 格式的微信聊天记录"""
    print(f"[wechat_parser] 解析 HTML 文件: {filepath}")
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    parser = WeChatHTMLParser(target_name)
    parser.feed(content)
    print(f"[wechat_parser] 从 HTML 提取 {len(parser.messages)} 条 {target_name} 的消息")
    return parser.messages


# ---------------------------------------------------------------------------
# CSV 解析
# ---------------------------------------------------------------------------

def parse_csv(filepath: str, target_name: str) -> list[dict[str, Any]]:
    """解析 CSV 格式的微信聊天记录

    支持的列名变体:
      发送者/sender/nickname/from + 内容/content/message/msg + 时间/time/timestamp/date
    """
    print(f"[wechat_parser] 解析 CSV 文件: {filepath}")
    messages: list[dict[str, Any]] = []

    # 检测编码
    with open(filepath, "rb") as fb:
        raw = fb.read(4096)
    encoding = "utf-8"
    if b"\xff\xfe" in raw[:4] or b"\xfe\xff" in raw[:4]:
        encoding = "utf-16"
    elif raw[:3] == b"\xef\xbb\xbf":
        encoding = "utf-8-sig"

    with open(filepath, "r", encoding=encoding, errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("[wechat_parser] 错误: CSV 文件没有表头")
            return []

        # 映射列名
        fields_lower = {fn.lower().strip(): fn for fn in reader.fieldnames}
        sender_col = None
        content_col = None
        time_col = None

        for alias, target_col_ref in [
            (["发送者", "sender", "nickname", "from", "talker", "发送人", "昵称"], "sender"),
            (["内容", "content", "message", "msg", "消息", "消息内容", "text"], "content"),
            (["时间", "time", "timestamp", "date", "日期", "发送时间", "createtime"], "time"),
        ]:
            for a in alias:
                if a in fields_lower:
                    if target_col_ref == "sender":
                        sender_col = fields_lower[a]
                    elif target_col_ref == "content":
                        content_col = fields_lower[a]
                    else:
                        time_col = fields_lower[a]
                    break

        if not sender_col or not content_col:
            print(f"[wechat_parser] 警告: 无法识别必要列 (sender/content)。可用列: {reader.fieldnames}")
            return []

        for row in reader:
            sender = (row.get(sender_col) or "").strip()
            text = (row.get(content_col) or "").strip()
            ts_raw = (row.get(time_col) or "").strip() if time_col else ""
            if sender == target_name and text:
                messages.append({
                    "text": text,
                    "timestamp": parse_timestamp(ts_raw) if ts_raw else None,
                    "sender": sender,
                })

    print(f"[wechat_parser] 从 CSV 提取 {len(messages)} 条 {target_name} 的消息")
    return messages


# ---------------------------------------------------------------------------
# 分类与输出
# ---------------------------------------------------------------------------

def classify_and_output(
    messages: list[dict[str, Any]],
    target_name: str,
    output_path: str,
) -> None:
    """对消息分层分类并输出 JSON"""
    if not messages:
        print("[wechat_parser] 警告: 没有提取到任何消息")
        result = {
            "target_name": target_name,
            "stats": {"total": 0},
            "messages": {"long": [], "emotional": [], "daily": []},
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"[wechat_parser] 已写入空结果到 {output_path}")
        return

    # 分类
    buckets: dict[str, list[dict[str, Any]]] = {"long": [], "emotional": [], "daily": []}
    for msg in messages:
        tier = classify_message(msg["text"])
        entry = {
            "text": msg["text"],
            "timestamp": msg.get("timestamp"),
            "tier": tier,
        }
        buckets[tier].append(entry)

    # 对 daily 进行截断
    if len(buckets["daily"]) > MAX_DAILY_MESSAGES:
        # 均匀采样
        step = len(buckets["daily"]) / MAX_DAILY_MESSAGES
        sampled = [buckets["daily"][int(i * step)] for i in range(MAX_DAILY_MESSAGES)]
        buckets["daily"] = sampled

    # 统计
    timestamps = [m["timestamp"] for m in messages if m.get("timestamp")]
    timestamps_sorted = sorted([t for t in timestamps if t])
    lengths = [len(m["text"]) for m in messages]

    stats = {
        "total": len(messages),
        "long_count": len(buckets["long"]),
        "emotional_count": len(buckets["emotional"]),
        "daily_count": len(buckets["daily"]),
        "avg_length": round(sum(lengths) / len(lengths), 1) if lengths else 0,
        "date_range": {
            "earliest": timestamps_sorted[0] if timestamps_sorted else None,
            "latest": timestamps_sorted[-1] if timestamps_sorted else None,
        },
    }

    result = {
        "target_name": target_name,
        "stats": stats,
        "messages": buckets,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[wechat_parser] 分类完成:")
    print(f"  总消息数: {stats['total']}")
    print(f"  长消息 (>{LONG_MESSAGE_THRESHOLD}字): {stats['long_count']}")
    print(f"  情感消息: {stats['emotional_count']}")
    print(f"  日常消息 (截取≤{MAX_DAILY_MESSAGES}): {stats['daily_count']}")
    print(f"  平均长度: {stats['avg_length']} 字")
    if timestamps_sorted:
        print(f"  时间范围: {timestamps_sorted[0]} ~ {timestamps_sorted[-1]}")
    print(f"[wechat_parser] 结果已写入 {output_path}")


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def detect_format(filepath: str) -> str:
    """根据扩展名和内容自动检测文件格式"""
    ext = Path(filepath).suffix.lower()
    if ext == ".csv":
        return "csv"
    if ext in (".html", ".htm"):
        return "html"
    if ext == ".txt":
        return "txt"
    # 尝试通过内容判断
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        head = f.read(1024)
    if "<html" in head.lower() or "<!doctype" in head.lower():
        return "html"
    if "," in head.split("\n")[0] and len(head.split("\n")[0].split(",")) >= 3:
        return "csv"
    return "txt"


def main():
    parser = argparse.ArgumentParser(
        description="微信聊天记录解析工具 — 支持 TXT/HTML/CSV 格式"
    )
    parser.add_argument("--input", required=True, help="输入文件路径")
    parser.add_argument("--target-name", required=True, help="目标人物的显示名称")
    parser.add_argument("--output", required=True, help="输出 JSON 文件路径")
    parser.add_argument(
        "--format",
        choices=["txt", "html", "csv", "auto"],
        default="auto",
        help="文件格式 (默认自动检测)",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"[wechat_parser] 错误: 文件不存在 — {args.input}", file=sys.stderr)
        sys.exit(1)

    fmt = args.format if args.format != "auto" else detect_format(args.input)
    print(f"[wechat_parser] 检测到格式: {fmt}")

    if fmt == "txt":
        messages = parse_txt(args.input, args.target_name)
    elif fmt == "html":
        messages = parse_html(args.input, args.target_name)
    elif fmt == "csv":
        messages = parse_csv(args.input, args.target_name)
    else:
        print(f"[wechat_parser] 错误: 不支持的格式 — {fmt}", file=sys.stderr)
        sys.exit(1)

    # 确保输出目录存在
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    classify_and_output(messages, args.target_name, args.output)


if __name__ == "__main__":
    main()
