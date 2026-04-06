#!/usr/bin/env python3
"""
短信 / iMessage 聊天记录解析工具

支持格式:
  - Android SMS Backup XML (SMS Backup & Restore 等)
  - CSV 导出
  - 纯文本 (每行一条消息，带时间戳)
  - macOS iMessage chat.db (SQLite)

用法:
  python sms_parser.py --input <file> --target-name <name> --output <output.json>
"""

import argparse
import csv
import json
import os
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# 与 wechat_parser 共享的分类逻辑
EMOTIONAL_KEYWORDS = [
    "想你", "爱你", "担心", "生气", "对不起", "注意身体",
    "吃了没", "冷不冷", "早点睡", "保重", "心疼", "想家",
    "辛苦了", "别累着", "好想你", "挂念", "牵挂", "舍不得",
    "抱歉", "原谅", "感谢", "谢谢你", "幸福", "开心",
    "难过", "伤心", "委屈", "害怕", "紧张", "加油",
    "照顾好自己", "别熬夜", "多喝水", "穿厚点", "路上小心",
    "到家了吗", "安全到了吗", "想念", "miss you", "love you",
    "i miss you", "take care", "be safe", "thinking of you",
]

MAX_DAILY_MESSAGES = 200
LONG_MESSAGE_THRESHOLD = 50


def classify_message(text: str) -> str:
    """将消息分为三个层级"""
    if len(text) > LONG_MESSAGE_THRESHOLD:
        return "long"
    text_lower = text.lower()
    for kw in EMOTIONAL_KEYWORDS:
        if kw in text_lower:
            return "emotional"
    return "daily"


def parse_timestamp(ts_str: str) -> str | None:
    """尝试多种格式解析时间戳"""
    ts_str = ts_str.strip()
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%b %d, %Y %I:%M:%S %p",
        "%b %d, %Y %I:%M %p",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(ts_str, fmt)
            return dt.isoformat()
        except ValueError:
            continue
    # 尝试 Unix 时间戳 (毫秒或秒)
    try:
        val = int(ts_str)
        if val > 1e12:
            val = val / 1000
        dt = datetime.fromtimestamp(val, tz=timezone.utc)
        return dt.isoformat()
    except (ValueError, OSError):
        pass
    return None


# ---------------------------------------------------------------------------
# Android SMS Backup XML
# ---------------------------------------------------------------------------

def parse_android_xml(filepath: str, target_name: str) -> list[dict[str, Any]]:
    """解析 Android SMS Backup & Restore XML 格式

    XML 结构:
      <smses>
        <sms address="+1234" contact_name="张三" date="1672531200000"
             type="1" body="消息内容" />
      </smses>

    type=1 表示收到的消息, type=2 表示发送的消息
    """
    print(f"[sms_parser] 解析 Android XML: {filepath}")
    messages: list[dict[str, Any]] = []

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"[sms_parser] XML 解析错误: {e}", file=sys.stderr)
        return []

    for sms in root.iter("sms"):
        contact = sms.get("contact_name", "").strip()
        address = sms.get("address", "").strip()
        body = sms.get("body", "").strip()
        date_ms = sms.get("date", "")
        sms_type = sms.get("type", "")

        # 匹配目标: 按名字或电话号码
        name_match = (contact == target_name) or (address == target_name)
        # type=1 是接收的消息 (对方发来的)
        is_incoming = sms_type == "1"

        if name_match and is_incoming and body:
            ts = parse_timestamp(date_ms) if date_ms else None
            messages.append({
                "text": body,
                "timestamp": ts,
                "sender": contact or address,
            })

    # 也检查 MMS
    for mms in root.iter("mms"):
        contact = mms.get("contact_name", "").strip()
        address = mms.get("address", "").strip()
        date_ms = mms.get("date", "")
        msg_type = mms.get("msg_box", "")  # 1=received

        if not ((contact == target_name) or (address == target_name)):
            continue
        if msg_type != "1":
            continue

        # MMS 文本在 parts 里
        for part in mms.iter("part"):
            ct = part.get("ct", "")
            if "text/plain" in ct:
                text = part.get("text", "").strip()
                if text:
                    ts = parse_timestamp(date_ms) if date_ms else None
                    messages.append({
                        "text": text,
                        "timestamp": ts,
                        "sender": contact or address,
                    })

    print(f"[sms_parser] 从 XML 提取 {len(messages)} 条来自 {target_name} 的消息")
    return messages


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

def parse_csv(filepath: str, target_name: str) -> list[dict[str, Any]]:
    """解析 CSV 格式的短信记录"""
    print(f"[sms_parser] 解析 CSV 文件: {filepath}")
    messages: list[dict[str, Any]] = []

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
            print("[sms_parser] 错误: CSV 无表头")
            return []

        fields_lower = {fn.lower().strip(): fn for fn in reader.fieldnames}

        sender_col = None
        content_col = None
        time_col = None
        type_col = None

        for aliases, ref in [
            (["contact_name", "sender", "from", "name", "address", "number", "phone"], "sender"),
            (["body", "content", "message", "msg", "text", "sms_body"], "content"),
            (["date", "time", "timestamp", "sent_at", "readable_date"], "time"),
            (["type", "sms_type", "direction", "msg_type"], "type"),
        ]:
            for a in aliases:
                if a in fields_lower:
                    if ref == "sender":
                        sender_col = fields_lower[a]
                    elif ref == "content":
                        content_col = fields_lower[a]
                    elif ref == "time":
                        time_col = fields_lower[a]
                    elif ref == "type":
                        type_col = fields_lower[a]
                    break

        if not content_col:
            print(f"[sms_parser] 警告: 找不到消息内容列。可用列: {reader.fieldnames}")
            return []

        for row in reader:
            sender = (row.get(sender_col) or "").strip() if sender_col else ""
            text = (row.get(content_col) or "").strip()
            ts_raw = (row.get(time_col) or "").strip() if time_col else ""
            msg_type = (row.get(type_col) or "").strip() if type_col else ""

            # 判断是否是目标人物的消息
            if sender_col and target_name not in sender:
                continue
            # 如果有 type 列，1=received / incoming
            if msg_type and msg_type.lower() not in ("1", "received", "incoming", "inbox"):
                continue
            if text:
                messages.append({
                    "text": text,
                    "timestamp": parse_timestamp(ts_raw) if ts_raw else None,
                    "sender": sender,
                })

    print(f"[sms_parser] 从 CSV 提取 {len(messages)} 条消息")
    return messages


# ---------------------------------------------------------------------------
# 纯文本
# ---------------------------------------------------------------------------

_TXT_PATTERN = re.compile(
    r"^[\[\(]?(\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}(?::\d{2})?)[\]\)]?\s+"
    r"(.+?)[:：]\s*(.+)$"
)

_TXT_PATTERN_ALT = re.compile(
    r"^(.+?)[:：]\s*[\[\(]?(\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}(?::\d{2})?)[\]\)]?\s*(.+)$"
)


def parse_txt(filepath: str, target_name: str) -> list[dict[str, Any]]:
    """解析纯文本格式 — 每行一条消息"""
    print(f"[sms_parser] 解析纯文本: {filepath}")
    messages: list[dict[str, Any]] = []

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # 格式1: [时间] 名字: 内容
            m = _TXT_PATTERN.match(line)
            if m:
                ts, sender, text = m.group(1), m.group(2).strip(), m.group(3).strip()
                if sender == target_name and text:
                    messages.append({
                        "text": text,
                        "timestamp": parse_timestamp(ts),
                        "sender": sender,
                    })
                continue

            # 格式2: 名字: [时间] 内容
            m = _TXT_PATTERN_ALT.match(line)
            if m:
                sender, ts, text = m.group(1).strip(), m.group(2), m.group(3).strip()
                if sender == target_name and text:
                    messages.append({
                        "text": text,
                        "timestamp": parse_timestamp(ts),
                        "sender": sender,
                    })

    print(f"[sms_parser] 从纯文本提取 {len(messages)} 条消息")
    return messages


# ---------------------------------------------------------------------------
# macOS iMessage chat.db
# ---------------------------------------------------------------------------

def parse_imessage_db(filepath: str, target_name: str) -> list[dict[str, Any]]:
    """解析 macOS iMessage 的 chat.db (SQLite)

    chat.db 通常位于:
      ~/Library/Messages/chat.db

    target_name 可以是联系人姓名或电话号码/Apple ID
    """
    print(f"[sms_parser] 解析 iMessage chat.db: {filepath}")
    messages: list[dict[str, Any]] = []

    if not os.path.isfile(filepath):
        print(f"[sms_parser] 错误: 数据库文件不存在 — {filepath}", file=sys.stderr)
        return []

    try:
        conn = sqlite3.connect(f"file:{filepath}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # iMessage 时间戳的纪元: 2001-01-01 (Core Data / NSDate epoch)
        # 单位可能是纳秒(10^9)或秒，取决于 macOS 版本
        # date 字段在 macOS 10.13+ 以纳秒为单位

        # 查找与目标关联的 handle
        cursor.execute(
            "SELECT ROWID, id FROM handle WHERE id LIKE ? OR id LIKE ?",
            (f"%{target_name}%", f"%{target_name}%"),
        )
        handles = cursor.fetchall()

        if not handles:
            print(f"[sms_parser] 未找到匹配 '{target_name}' 的联系人")
            conn.close()
            return []

        handle_ids = [h["ROWID"] for h in handles]
        print(f"[sms_parser] 找到 {len(handle_ids)} 个匹配的联系人 handle")

        placeholders = ",".join("?" * len(handle_ids))
        query = f"""
            SELECT
                m.text,
                m.date,
                m.is_from_me,
                h.id as sender_id
            FROM message m
            JOIN handle h ON m.handle_id = h.ROWID
            WHERE m.handle_id IN ({placeholders})
              AND m.is_from_me = 0
              AND m.text IS NOT NULL
              AND m.text != ''
            ORDER BY m.date ASC
        """
        cursor.execute(query, handle_ids)

        # 检测时间戳单位
        NSDATE_EPOCH = datetime(2001, 1, 1, tzinfo=timezone.utc)

        for row in cursor:
            text = row["text"].strip()
            if not text:
                continue

            date_val = row["date"]
            ts = None
            if date_val:
                try:
                    # 纳秒
                    if date_val > 1e15:
                        seconds = date_val / 1e9
                    # 毫秒
                    elif date_val > 1e12:
                        seconds = date_val / 1e3
                    else:
                        seconds = date_val

                    from datetime import timedelta
                    dt = NSDATE_EPOCH + timedelta(seconds=seconds)
                    ts = dt.isoformat()
                except (OverflowError, OSError):
                    pass

            messages.append({
                "text": text,
                "timestamp": ts,
                "sender": target_name,
            })

        conn.close()

    except sqlite3.Error as e:
        print(f"[sms_parser] SQLite 错误: {e}", file=sys.stderr)
        print("[sms_parser] 提示: 如果是权限问题，请先复制 chat.db 到可访问的位置")
        return []

    print(f"[sms_parser] 从 iMessage 提取 {len(messages)} 条消息")
    return messages


# ---------------------------------------------------------------------------
# 分类与输出 (与 wechat_parser 相同逻辑)
# ---------------------------------------------------------------------------

def classify_and_output(
    messages: list[dict[str, Any]],
    target_name: str,
    output_path: str,
) -> None:
    """对消息分层分类并输出 JSON"""
    if not messages:
        print("[sms_parser] 警告: 没有提取到任何消息")
        result = {
            "target_name": target_name,
            "stats": {"total": 0},
            "messages": {"long": [], "emotional": [], "daily": []},
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"[sms_parser] 已写入空结果到 {output_path}")
        return

    buckets: dict[str, list[dict[str, Any]]] = {"long": [], "emotional": [], "daily": []}
    for msg in messages:
        tier = classify_message(msg["text"])
        buckets[tier].append({
            "text": msg["text"],
            "timestamp": msg.get("timestamp"),
            "tier": tier,
        })

    if len(buckets["daily"]) > MAX_DAILY_MESSAGES:
        step = len(buckets["daily"]) / MAX_DAILY_MESSAGES
        buckets["daily"] = [buckets["daily"][int(i * step)] for i in range(MAX_DAILY_MESSAGES)]

    timestamps_sorted = sorted([m["timestamp"] for m in messages if m.get("timestamp")])
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

    print(f"[sms_parser] 分类完成:")
    print(f"  总消息数: {stats['total']}")
    print(f"  长消息: {stats['long_count']}")
    print(f"  情感消息: {stats['emotional_count']}")
    print(f"  日常消息: {stats['daily_count']}")
    print(f"  平均长度: {stats['avg_length']} 字")
    print(f"[sms_parser] 结果已写入 {output_path}")


# ---------------------------------------------------------------------------
# 格式检测与主入口
# ---------------------------------------------------------------------------

def detect_format(filepath: str) -> str:
    """自动检测文件格式"""
    ext = Path(filepath).suffix.lower()
    if ext == ".xml":
        return "xml"
    if ext == ".csv":
        return "csv"
    if ext in (".db", ".sqlite", ".sqlite3"):
        return "imessage"
    if ext == ".txt":
        return "txt"

    # 内容探测
    with open(filepath, "rb") as f:
        head = f.read(256)
    if head[:15] == b"SQLite format 3":
        return "imessage"
    head_str = head.decode("utf-8", errors="replace")
    if head_str.strip().startswith("<?xml") or "<smses" in head_str:
        return "xml"
    return "txt"


def main():
    parser = argparse.ArgumentParser(
        description="短信/iMessage 聊天记录解析工具 — 支持 XML/CSV/TXT/chat.db"
    )
    parser.add_argument("--input", required=True, help="输入文件路径")
    parser.add_argument("--target-name", required=True, help="目标人物名称或号码")
    parser.add_argument("--output", required=True, help="输出 JSON 文件路径")
    parser.add_argument(
        "--format",
        choices=["xml", "csv", "txt", "imessage", "auto"],
        default="auto",
        help="文件格式 (默认自动检测)",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"[sms_parser] 错误: 文件不存在 — {args.input}", file=sys.stderr)
        sys.exit(1)

    fmt = args.format if args.format != "auto" else detect_format(args.input)
    print(f"[sms_parser] 检测到格式: {fmt}")

    if fmt == "xml":
        messages = parse_android_xml(args.input, args.target_name)
    elif fmt == "csv":
        messages = parse_csv(args.input, args.target_name)
    elif fmt == "txt":
        messages = parse_txt(args.input, args.target_name)
    elif fmt == "imessage":
        messages = parse_imessage_db(args.input, args.target_name)
    else:
        print(f"[sms_parser] 错误: 不支持的格式 — {fmt}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    classify_and_output(messages, args.target_name, args.output)


if __name__ == "__main__":
    main()
