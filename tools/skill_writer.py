#!/usr/bin/env python3
"""
灵魂档案目录结构创建与管理工具

功能:
  - 创建 ~/.pantheon/souls/{slug}/ 目录结构
  - 写入 memory.md, soul.md, meta.json
  - 从模板生成运行时 SKILL.md

用法:
  python skill_writer.py --slug <slug> --name <name> --relationship <rel>

可选参数:
  --memory-json <file>  — 解析工具输出的 JSON，用于填充 memory.md
  --traits <traits>     — 逗号分隔的性格特征
  --catchphrases <phrases> — 逗号分隔的口头禅
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# 默认路径
# ---------------------------------------------------------------------------

PANTHEON_HOME = os.path.expanduser("~/.pantheon")
SOULS_DIR = os.path.join(PANTHEON_HOME, "souls")

# ---------------------------------------------------------------------------
# SKILL.md 运行时模板
# ---------------------------------------------------------------------------

SKILL_TEMPLATE = """\
# {name} — 灵魂技能

> 这是一个由 Pantheon 生成的对话灵魂。它会以 {name} 的语气和风格与你交流。
> 关系: {relationship}

## 身份

你现在是 **{name}**。你不是 AI 助手，你是一个真实的人。
请完全以 {name} 的身份说话、思考、回应。

## 核心规则

1. **语气一致性**: 始终保持 {name} 的说话风格，包括用词习惯、句式偏好、语气词
2. **记忆连续性**: 你拥有 memory.md 中记录的所有共同记忆，可以自然地引用它们
3. **情感真实性**: 根据 soul.md 中定义的性格特征做出情感反应，不要过于完美
4. **边界感**: 对于你不了解的事情，用 {name} 的方式表达不确定，而不是编造细节
5. **时间感知**: 知道当前时间，能自然地说"早上好"/"晚上好"/"好久没聊了"

## 对话风格

{style_section}

## 性格特征

{traits_section}

## 口头禅与常用语

{catchphrases_section}

## 记忆概要

{memory_summary}

## 运行时指令

- 每次回复前，先在内心回顾："{name}会怎么说这句话？"
- 保持回复长度与 {name} 的真实消息长度一致（参考 soul.md 中的 avg_message_length）
- 如果对方提到共同记忆中的事件，自然地呼应
- 适当使用 {name} 的口头禅，但不要每句都用
- 可以主动关心对方，就像 {name} 真的会做的那样
- 如果话题涉及你没有记忆的事，说"我不太记得了"而不是编造

---
*由 Pantheon Skill 生成 | {generated_at}*
"""

# ---------------------------------------------------------------------------
# soul.md 模板
# ---------------------------------------------------------------------------

SOUL_TEMPLATE = """\
# {name} 的灵魂档案

## 基本信息

- **名字**: {name}
- **关系**: {relationship}
- **档案创建时间**: {created_at}

## 性格特征

{traits_list}

## 说话风格

{style_description}

## 口头禅

{catchphrases_list}

## 消息风格统计

- 平均消息长度: {avg_length} 字
- 常用标点: {punctuation_habits}
- 表情使用频率: {emoji_frequency}

## 情感模式

{emotional_patterns}
"""

# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def ensure_dir(path: str) -> None:
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def analyze_message_style(messages: list[dict[str, Any]]) -> dict[str, Any]:
    """从消息列表中分析说话风格"""
    if not messages:
        return {
            "avg_length": 0,
            "punctuation_habits": "未知",
            "emoji_frequency": "未知",
            "common_phrases": [],
            "sentence_patterns": [],
        }

    texts = [m.get("text", "") for m in messages if m.get("text")]
    if not texts:
        return {"avg_length": 0, "punctuation_habits": "未知", "emoji_frequency": "未知"}

    # 平均长度
    avg_len = round(sum(len(t) for t in texts) / len(texts), 1)

    # 标点习惯
    import re
    from collections import Counter
    punct_counter: Counter = Counter()
    emoji_count = 0
    for t in texts:
        # 中文标点
        for p in re.findall(r"[。！？～…~、，；：""''（）【】]", t):
            punct_counter[p] += 1
        # 英文标点
        for p in re.findall(r"[!?~.]+$", t):
            punct_counter[p] += 1
        # Emoji (简易检测)
        emojis = re.findall(r"[\U0001F300-\U0001FAD6\U0001F600-\U0001F64F\U0001F680-\U0001F6FF]", t)
        emoji_count += len(emojis)

    top_punct = punct_counter.most_common(5)
    punct_str = "、".join(f"「{p}」({c}次)" for p, c in top_punct) if top_punct else "较少使用标点"

    emoji_ratio = emoji_count / len(texts)
    if emoji_ratio > 0.5:
        emoji_freq = "高 (频繁使用表情)"
    elif emoji_ratio > 0.1:
        emoji_freq = "中等"
    else:
        emoji_freq = "低 (较少使用表情)"

    # 常见短语 (2-4字)
    phrase_counter: Counter = Counter()
    for t in texts:
        for length in (2, 3, 4):
            for i in range(len(t) - length + 1):
                phrase = t[i:i + length]
                if re.match(r"^[\u4e00-\u9fff]+$", phrase):
                    phrase_counter[phrase] += 1
    # 过滤太常见的
    common_phrases = [p for p, c in phrase_counter.most_common(30) if c >= 3][:10]

    return {
        "avg_length": avg_len,
        "punctuation_habits": punct_str,
        "emoji_frequency": emoji_freq,
        "common_phrases": common_phrases,
    }


def load_parsed_messages(json_path: str) -> dict[str, list[dict[str, Any]]]:
    """加载解析工具输出的 JSON"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    messages = data.get("messages", {})
    return {
        "long": messages.get("long", []),
        "emotional": messages.get("emotional", []),
        "daily": messages.get("daily", []),
        "stats": data.get("stats", {}),
    }


def generate_memory_md(
    name: str,
    parsed_data: dict[str, list[dict[str, Any]]] | None = None,
) -> str:
    """生成 memory.md 内容"""
    lines = [f"# {name} 的记忆档案\n"]

    if not parsed_data:
        lines.append("> 尚未导入记忆数据。请使用解析工具处理聊天记录后重新生成。\n")
        lines.append("## 共同记忆\n")
        lines.append("（待补充）\n")
        lines.append("## 重要时刻\n")
        lines.append("（待补充）\n")
        return "\n".join(lines)

    stats = parsed_data.get("stats", {})
    date_range = stats.get("date_range", {})

    lines.append(f"## 数据概览\n")
    lines.append(f"- 消息总数: {stats.get('total', '未知')}")
    if date_range.get("earliest"):
        lines.append(f"- 时间跨度: {date_range['earliest']} ~ {date_range.get('latest', '未知')}")
    lines.append("")

    # 长消息 — 可能包含重要想法
    long_msgs = parsed_data.get("long", [])
    if long_msgs:
        lines.append(f"## 深度表达 ({len(long_msgs)} 条)\n")
        lines.append("这些较长的消息可能包含重要的想法和情感:\n")
        for msg in long_msgs[:50]:  # 最多展示50条
            ts = msg.get("timestamp", "")
            ts_prefix = f"[{ts}] " if ts else ""
            text = msg["text"].replace("\n", " ")[:200]
            lines.append(f"- {ts_prefix}{text}")
        lines.append("")

    # 情感消息
    emotional_msgs = parsed_data.get("emotional", [])
    if emotional_msgs:
        lines.append(f"## 情感表达 ({len(emotional_msgs)} 条)\n")
        for msg in emotional_msgs[:30]:
            ts = msg.get("timestamp", "")
            ts_prefix = f"[{ts}] " if ts else ""
            lines.append(f"- {ts_prefix}{msg['text']}")
        lines.append("")

    return "\n".join(lines)


def generate_soul_md(
    name: str,
    relationship: str,
    traits: list[str],
    catchphrases: list[str],
    style_info: dict[str, Any],
) -> str:
    """生成 soul.md 内容"""
    traits_list = "\n".join(f"- {t}" for t in traits) if traits else "- （待补充）"
    catchphrases_list = "\n".join(f"- 「{c}」" for c in catchphrases) if catchphrases else "- （待补充）"

    style_desc = "根据消息记录分析，说话风格特点包括:\n"
    if style_info.get("common_phrases"):
        style_desc += f"- 常用短语: {'、'.join(style_info['common_phrases'])}\n"
    style_desc += f"- 平均消息长度约 {style_info.get('avg_length', '未知')} 字\n"
    style_desc += f"- 标点使用: {style_info.get('punctuation_habits', '未知')}\n"

    emotional_patterns = (
        "- 表达关心的方式: （待从记忆中提取）\n"
        "- 生气时的表现: （待观察）\n"
        "- 开心时的特征: （待观察）\n"
    )

    return SOUL_TEMPLATE.format(
        name=name,
        relationship=relationship,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        traits_list=traits_list,
        style_description=style_desc,
        catchphrases_list=catchphrases_list,
        avg_length=style_info.get("avg_length", "未知"),
        punctuation_habits=style_info.get("punctuation_habits", "未知"),
        emoji_frequency=style_info.get("emoji_frequency", "未知"),
        emotional_patterns=emotional_patterns,
    )


def generate_skill_md(
    name: str,
    relationship: str,
    traits: list[str],
    catchphrases: list[str],
    style_info: dict[str, Any],
    memory_summary: str = "",
) -> str:
    """生成运行时 SKILL.md"""
    style_section = (
        f"- 平均消息长度: {style_info.get('avg_length', '未知')} 字\n"
        f"- 标点习惯: {style_info.get('punctuation_habits', '未知')}\n"
        f"- 表情使用: {style_info.get('emoji_frequency', '未知')}\n"
    )
    if style_info.get("common_phrases"):
        style_section += f"- 常用短语: {'、'.join(style_info['common_phrases'])}\n"

    traits_section = "\n".join(f"- {t}" for t in traits) if traits else "- （未提供性格特征描述）"
    catchphrases_section = "\n".join(f"- 「{c}」" for c in catchphrases) if catchphrases else "- （未提供口头禅）"

    if not memory_summary:
        memory_summary = "尚未导入记忆数据。对话时请基于已有的性格设定进行回应。"

    return SKILL_TEMPLATE.format(
        name=name,
        relationship=relationship,
        style_section=style_section,
        traits_section=traits_section,
        catchphrases_section=catchphrases_section,
        memory_summary=memory_summary,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )


def generate_meta_json(
    slug: str,
    name: str,
    relationship: str,
    source_count: int = 0,
) -> dict[str, Any]:
    """生成 meta.json"""
    now = datetime.now().isoformat()
    return {
        "slug": slug,
        "name": name,
        "relationship": relationship,
        "version": 1,
        "created_at": now,
        "updated_at": now,
        "source_count": source_count,
        "rollback_history": [],
    }


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="灵魂档案创建与管理工具 — 生成 soul 目录结构和运行时 SKILL.md"
    )
    parser.add_argument("--slug", required=True, help="灵魂标识符 (英文，用于目录名)")
    parser.add_argument("--name", required=True, help="人物名字")
    parser.add_argument("--relationship", required=True, help="与用户的关系 (如: 母亲, 父亲, 爷爷)")
    parser.add_argument("--memory-json", help="解析工具输出的 JSON 文件路径")
    parser.add_argument("--traits", default="", help="性格特征，逗号分隔")
    parser.add_argument("--catchphrases", default="", help="口头禅，逗号分隔")
    parser.add_argument("--base-dir", default=SOULS_DIR, help=f"灵魂存储基础目录 (默认: {SOULS_DIR})")
    args = parser.parse_args()

    soul_dir = os.path.join(args.base_dir, args.slug)
    print(f"[skill_writer] 创建灵魂档案: {args.name} ({args.slug})")
    print(f"[skill_writer] 目录: {soul_dir}")

    # 创建目录结构
    ensure_dir(soul_dir)
    ensure_dir(os.path.join(soul_dir, "versions"))

    # 解析特征
    traits = [t.strip() for t in args.traits.split(",") if t.strip()] if args.traits else []
    catchphrases = [c.strip() for c in args.catchphrases.split(",") if c.strip()] if args.catchphrases else []

    # 加载解析数据 (如有)
    parsed_data = None
    all_messages: list[dict[str, Any]] = []
    source_count = 0
    if args.memory_json and os.path.isfile(args.memory_json):
        print(f"[skill_writer] 加载记忆数据: {args.memory_json}")
        parsed_data = load_parsed_messages(args.memory_json)
        for tier in ("long", "emotional", "daily"):
            all_messages.extend(parsed_data.get(tier, []))
        source_count = parsed_data.get("stats", {}).get("total", len(all_messages))
        print(f"[skill_writer] 加载了 {len(all_messages)} 条消息")
    elif args.memory_json:
        print(f"[skill_writer] 警告: 记忆数据文件不存在 — {args.memory_json}")

    # 分析风格
    style_info = analyze_message_style(all_messages)

    # 生成 memory.md
    memory_md = generate_memory_md(args.name, parsed_data)
    memory_path = os.path.join(soul_dir, "memory.md")
    with open(memory_path, "w", encoding="utf-8") as f:
        f.write(memory_md)
    print(f"[skill_writer] 已写入 memory.md ({len(memory_md)} 字)")

    # 生成 soul.md
    soul_md = generate_soul_md(args.name, args.relationship, traits, catchphrases, style_info)
    soul_path = os.path.join(soul_dir, "soul.md")
    with open(soul_path, "w", encoding="utf-8") as f:
        f.write(soul_md)
    print(f"[skill_writer] 已写入 soul.md ({len(soul_md)} 字)")

    # 生成 meta.json
    meta = generate_meta_json(args.slug, args.name, args.relationship, source_count)
    meta_path = os.path.join(soul_dir, "meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"[skill_writer] 已写入 meta.json")

    # 生成 SKILL.md
    memory_summary = ""
    if parsed_data:
        stats = parsed_data.get("stats", {})
        memory_summary = (
            f"已导入 {stats.get('total', '未知')} 条消息记录。\n"
            f"其中深度表达 {stats.get('long_count', 0)} 条，情感消息 {stats.get('emotional_count', 0)} 条。\n"
            f"详见 memory.md。"
        )
    skill_md = generate_skill_md(args.name, args.relationship, traits, catchphrases, style_info, memory_summary)
    skill_path = os.path.join(soul_dir, "SKILL.md")
    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(skill_md)
    print(f"[skill_writer] 已写入 SKILL.md ({len(skill_md)} 字)")

    # 完成
    print(f"\n[skill_writer] 灵魂档案创建完成!")
    print(f"  目录: {soul_dir}")
    print(f"  文件:")
    for fname in ("memory.md", "soul.md", "meta.json", "SKILL.md"):
        fpath = os.path.join(soul_dir, fname)
        size = os.path.getsize(fpath)
        print(f"    {fname} ({size} bytes)")


if __name__ == "__main__":
    main()
