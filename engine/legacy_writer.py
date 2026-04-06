#!/usr/bin/env python3
"""
legacy_writer.py - 家族传记生成引擎

从所有灵魂档案、家族图谱、代际 DNA、仪式记录中综合生成一本家族书。
这不是简单的拼接——是一个家族精神遗产的结晶。

输出一本结构完整的 Markdown 家族书：
序言 → 家族树 → 每一代 → 传家宝 → 家的味道 → 节日记忆 → 家训 → 致后人
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

PREFIX = "[legacy_writer]"
DEFAULT_FAMILY_DIR = os.path.expanduser("~/.pantheon")
DEFAULT_OUTPUT = os.path.expanduser("~/.pantheon/family/legacy/family_book.md")


def _log(msg: str) -> None:
    print(f"{PREFIX} {msg}")


# ---------------------------------------------------------------------------
# 数据加载（复用其他引擎的数据格式）
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> Optional[Dict]:
    """加载 JSON 文件。"""
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return None


def _load_md(path: Path) -> str:
    """加载 Markdown 文件内容。"""
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except IOError:
            pass
    return ""


def _load_family_tree(family_dir: str) -> Dict:
    """加载家族图谱。"""
    tree = _load_json(Path(family_dir) / "family" / "tree.json")
    return tree or {"souls": {}, "edges": []}


def _load_all_souls(family_dir: str) -> Dict[str, Dict]:
    """加载所有灵魂的 soul.md 内容，按 slug 索引。"""
    souls_dir = Path(family_dir) / "souls"
    souls = {}

    if not souls_dir.exists():
        return souls

    for soul_dir in sorted(souls_dir.iterdir()):
        if soul_dir.is_dir():
            soul_md = soul_dir / "soul.md"
            content = _load_md(soul_md)
            if content:
                souls[soul_dir.name] = {
                    "slug": soul_dir.name,
                    "content": content,
                    "dir": str(soul_dir),
                }
                # 尝试提取名称
                name_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
                if name_match:
                    souls[soul_dir.name]["name"] = name_match.group(1).strip()

    return souls


def _load_all_memories(family_dir: str) -> Dict[str, str]:
    """加载所有灵魂的 memory.md 内容。"""
    souls_dir = Path(family_dir) / "souls"
    memories = {}

    if not souls_dir.exists():
        return memories

    for soul_dir in sorted(souls_dir.iterdir()):
        if soul_dir.is_dir():
            mem_md = soul_dir / "memory.md"
            content = _load_md(mem_md)
            if content:
                memories[soul_dir.name] = content

    return memories


def _load_rituals(family_dir: str) -> List[Dict]:
    """加载所有仪式记录。"""
    rituals_dir = Path(family_dir) / "family" / "rituals"
    rituals = []

    if not rituals_dir.exists():
        return rituals

    for f in sorted(rituals_dir.glob("*.md")):
        content = _load_md(f)
        if content:
            ritual = {"file": str(f), "slug": f.stem, "content": content}
            name_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
            if name_match:
                ritual["name"] = name_match.group(1).strip()

            type_match = re.search(r"^类型[：:]\s*(.+)", content, re.MULTILINE)
            if type_match:
                ritual["type"] = type_match.group(1).strip()

            rituals.append(ritual)

    return rituals


def _load_generational_dna(family_dir: str) -> str:
    """加载代际 DNA 报告（如果存在）。"""
    candidates = [
        Path(family_dir) / "generational_dna.md",
        Path(family_dir) / "family" / "generational_dna.md",
    ]
    for p in candidates:
        content = _load_md(p)
        if content:
            return content
    return ""


# ---------------------------------------------------------------------------
# 章节生成
# ---------------------------------------------------------------------------

def _generate_preface(tree: Dict, souls: Dict) -> str:
    """序言：家族起源故事。"""
    lines = ["# 序言"]
    lines.append("")

    soul_count = len(tree.get("souls", {}))
    if soul_count == 0:
        lines.append("这是一个家族的记忆之书。")
        lines.append("它还在等待被书写。")
        return "\n".join(lines)

    # 找到最早的祖先（generation 最小）
    earliest = None
    earliest_gen = float("inf")
    for slug, soul in tree.get("souls", {}).items():
        gen = soul.get("generation", 0)
        if gen < earliest_gen:
            earliest_gen = gen
            earliest = soul

    lines.append("这本书，记录的不是历史，而是一个家族的温度。")
    lines.append("")

    if earliest:
        name = earliest.get("name", earliest.get("slug", "祖先"))
        birth = earliest.get("birth_year", "")
        birth_str = f"（{birth}年生）" if birth else ""
        lines.append(f"从 **{name}**{birth_str} 开始，到如今第 {soul_count} 位家人被记录在此。")
        lines.append("每一代人的故事，都是下一代人的根。")
    else:
        lines.append(f"这里记录了 {soul_count} 位家人的故事。")

    lines.append("")
    lines.append("翻开这些文字，你会听到他们的声音、闻到他们厨房的味道、")
    lines.append("感受到他们曾经给过你的那些不曾说出口的爱。")
    lines.append("")

    return "\n".join(lines)


def _generate_family_tree_visual(tree: Dict) -> str:
    """家族树：Mermaid 图 + ASCII 备选。"""
    lines = ["# 家族树"]
    lines.append("")

    souls = tree.get("souls", {})
    edges = tree.get("edges", [])

    if not souls:
        lines.append("_家族树尚未建立。_")
        return "\n".join(lines)

    # Mermaid 图
    lines.append("```mermaid")
    lines.append("graph TD")

    for slug, soul in souls.items():
        name = soul.get("name", slug)
        birth = soul.get("birth_year", "")
        death = soul.get("death_year", "")
        life_span = ""
        if birth:
            life_span = f"<br/>{birth}"
            if death:
                life_span += f"-{death}"
            else:
                life_span += "-"
        lines.append(f"    {slug}[\"{name}{life_span}\"]")

    for edge in edges:
        src = edge["from"]
        dst = edge["to"]
        rtype = edge.get("type", "")
        if rtype == "parent-child":
            lines.append(f"    {src} --> {dst}")
        elif rtype == "spouse":
            # 只画一个方向避免重复
            if src < dst:
                lines.append(f"    {src} -.- {dst}")

    lines.append("```")
    lines.append("")

    # ASCII 文本备选
    lines.append("### 文字版")
    lines.append("")

    generations: Dict[int, List[Dict]] = defaultdict(list)
    for soul in souls.values():
        gen = soul.get("generation", 0)
        generations[gen].append(soul)

    for gen_num in sorted(generations.keys()):
        members = generations[gen_num]
        names = [f"{s.get('name', s.get('slug', '?'))}" for s in members]
        indent = "  " * gen_num
        connector = "└─ " if gen_num > 0 else ""
        lines.append(f"{indent}{connector}第{gen_num}代：{'、'.join(names)}")

    lines.append("")
    return "\n".join(lines)


def _generate_generation_chapters(tree: Dict, souls_data: Dict, memories: Dict) -> str:
    """每一代：以代际为章节，为关键成员画像。"""
    lines = ["# 每一代的故事"]
    lines.append("")

    souls = tree.get("souls", {})
    if not souls:
        lines.append("_尚无家族成员记录。_")
        return "\n".join(lines)

    generations: Dict[int, List[Dict]] = defaultdict(list)
    for soul in souls.values():
        gen = soul.get("generation", 0)
        generations[gen].append(soul)

    for gen_num in sorted(generations.keys()):
        members = generations[gen_num]
        lines.append(f"## 第 {gen_num} 代")
        lines.append("")

        for member in members:
            slug = member.get("slug", "")
            name = member.get("name", slug)
            gender = {"male": "男", "female": "女"}.get(member.get("gender", ""), "")
            birth = member.get("birth_year", "")
            death = member.get("death_year", "")

            title_parts = [f"### {name}"]
            if gender:
                title_parts.append(f"（{gender}）")
            if birth:
                life = f"{birth}"
                if death:
                    life += f"-{death}"
                else:
                    life += "-"
                title_parts.append(f"（{life}）")
            lines.append(" ".join(title_parts))
            lines.append("")

            # 嵌入 soul.md 摘要
            soul_info = souls_data.get(slug, {})
            content = soul_info.get("content", "")
            if content:
                # 取前几段作为画像
                paragraphs = [p.strip() for p in content.split("\n\n") if p.strip() and not p.strip().startswith("#")]
                for para in paragraphs[:3]:
                    # 去掉 markdown 标题行
                    clean_lines = [ln for ln in para.splitlines() if not ln.startswith("#")]
                    if clean_lines:
                        lines.append(" ".join(clean_lines))
                        lines.append("")

            # 嵌入记忆摘要
            mem_content = memories.get(slug, "")
            if mem_content:
                # 取前200字
                mem_preview = mem_content[:300].strip()
                if mem_preview:
                    lines.append(f"**{name}的记忆片段：**")
                    lines.append("")
                    lines.append(f"> {mem_preview}...")
                    lines.append("")

            lines.append("---")
            lines.append("")

    return "\n".join(lines)


def _generate_dna_chapter(dna_content: str) -> str:
    """传家宝：代际 DNA 章节。"""
    lines = ["# 传家宝 — 家族精神基因"]
    lines.append("")

    if dna_content:
        # 移除原始标题，嵌入内容
        cleaned = re.sub(r"^#\s+.+\n", "", dna_content).strip()
        lines.append(cleaned)
    else:
        lines.append("_代际 DNA 分析尚未运行。请先执行 `generational_dna.py` 生成报告。_")
        lines.append("")
        lines.append("当家族中的多个灵魂档案被建立后，")
        lines.append("这里会呈现跨代传承的价值观、口头禅、行为模式——")
        lines.append("那些让这个家族之所以是「这个家」的精神密码。")

    lines.append("")
    return "\n".join(lines)


def _generate_food_chapter(rituals: List[Dict]) -> str:
    """家的味道：食谱和食物传统。"""
    lines = ["# 家的味道"]
    lines.append("")
    lines.append("一个家的味道，是在灶台前传承的。")
    lines.append("")

    recipes = [r for r in rituals if r.get("type") == "食谱" or "recipe" in str(r.get("type", "")).lower()]

    if recipes:
        for r in recipes:
            lines.append(f"## {r.get('name', '无名菜')}")
            lines.append("")
            # 取内容但跳过标题
            content = r.get("content", "")
            for ln in content.splitlines():
                if not ln.startswith("# "):
                    lines.append(ln)
            lines.append("")
            lines.append("---")
            lines.append("")
    else:
        lines.append("_暂无食谱记录。_")
        lines.append("")
        lines.append("每个家庭都有属于自己的味道。")
        lines.append("也许是妈妈的番茄炒蛋，也许是奶奶的饺子馅。")
        lines.append("把它们记录下来吧——在味道消失之前。")

    lines.append("")
    return "\n".join(lines)


def _generate_holiday_chapter(rituals: List[Dict]) -> str:
    """节日记忆：家族怎么过节。"""
    lines = ["# 节日记忆"]
    lines.append("")
    lines.append("家族的温度，在节日里最浓。")
    lines.append("")

    holidays = [r for r in rituals if r.get("type") == "节日习俗" or "holiday" in str(r.get("type", "")).lower()]

    if holidays:
        for r in holidays:
            lines.append(f"## {r.get('name', '节日')}")
            lines.append("")
            content = r.get("content", "")
            for ln in content.splitlines():
                if not ln.startswith("# "):
                    lines.append(ln)
            lines.append("")
            lines.append("---")
            lines.append("")
    else:
        lines.append("_暂无节日传统记录。_")
        lines.append("")
        lines.append("春节怎么过？清明谁来负责祭扫？中秋围坐在哪里赏月？")
        lines.append("这些传统值得被记住。")

    lines.append("")
    return "\n".join(lines)


def _generate_wisdom_chapter(tree: Dict, souls_data: Dict) -> str:
    """家训：从所有灵魂中提炼的家族智慧。"""
    lines = ["# 家训 — 家族的智慧"]
    lines.append("")

    # 从 soul.md 中搜集价值观和教导
    all_wisdom: List[str] = []

    for slug, soul_info in souls_data.items():
        content = soul_info.get("content", "")
        name = soul_info.get("name", slug)

        # 查找包含价值观、教导、常说的话的段落
        for line in content.splitlines():
            cleaned = line.strip().lstrip("-*+ ").strip()
            if not cleaned or cleaned.startswith("#"):
                continue
            # 启发式：包含引号或教导性词汇的句子
            if any(marker in cleaned for marker in [
                "\"", "'", """, """, "「", "」",
                "教导", "总说", "常说", "告诫", "叮嘱", "座右铭",
            ]):
                all_wisdom.append(f"**{name}**：{cleaned}")

    if all_wisdom:
        for w in all_wisdom[:20]:  # 最多 20 条
            lines.append(f"- {w}")
            lines.append("")
    else:
        lines.append("_家族智慧正在收集中……_")
        lines.append("")
        lines.append("每一位长辈都留下过一些话。")
        lines.append("也许当时觉得啰嗦，后来才发现那是最珍贵的遗产。")

    lines.append("")
    return "\n".join(lines)


def _generate_letter_to_future(tree: Dict, souls_data: Dict) -> str:
    """致后人：综合所有灵魂智慧写给未来的信。"""
    lines = ["# 致后人"]
    lines.append("")

    souls = tree.get("souls", {})
    names = [s.get("name", s.get("slug", "")) for s in souls.values()]

    lines.append("亲爱的后来人：")
    lines.append("")
    lines.append("当你翻开这本书的时候，书中的一些人也许已经不在了。")
    lines.append("但他们的故事还在，他们的声音还在，他们的爱还在。")
    lines.append("")

    if names:
        lines.append(f"这本书里记录了 {'、'.join(names[:5])}{'等人' if len(names) > 5 else ''} 的生命痕迹。")
        lines.append("他们曾在这个世界上认真地活过——吃过苦，爱过人，犯过错，也留下过温暖。")
        lines.append("")

    lines.append("我们希望你知道：")
    lines.append("")
    lines.append("- 你从哪里来。每一个先人的选择，都通向了今天的你。")
    lines.append("- 你不是一个人。在你身后，站着一整个家族的力量。")
    lines.append("- 你可以打破旧的模式，也可以继承好的传统。这个选择权在你手中。")
    lines.append("- 记住家的味道。它比任何道理都真实。")
    lines.append("")
    lines.append("无论世界怎么变，家是你永远的根。")
    lines.append("")
    lines.append("---")
    lines.append(f"_此书生成于 {datetime.now().strftime('%Y年%m月%d日')}_")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 主生成函数
# ---------------------------------------------------------------------------

def generate_family_book(
    family_dir: str = DEFAULT_FAMILY_DIR,
    output_path: Optional[str] = None,
) -> str:
    """
    生成完整的家族传记。

    从所有数据源综合生成一本结构完整的 Markdown 家族书。

    Args:
        family_dir: 家族数据目录
        output_path: 输出文件路径

    Returns:
        家族书的完整 Markdown 文本
    """
    _log("开始生成家族传记...")

    # 加载所有数据
    _log("加载家族图谱...")
    tree = _load_family_tree(family_dir)

    _log("加载灵魂档案...")
    souls_data = _load_all_souls(family_dir)

    _log("加载记忆档案...")
    memories = _load_all_memories(family_dir)

    _log("加载仪式记录...")
    rituals = _load_rituals(family_dir)

    _log("加载代际 DNA...")
    dna_content = _load_generational_dna(family_dir)

    # 统计
    soul_count = len(tree.get("souls", {}))
    memory_count = len(memories)
    ritual_count = len(rituals)
    _log(f"数据概览：{soul_count} 个灵魂，{memory_count} 份记忆，{ritual_count} 个仪式")

    # 生成各章节
    chapters = []

    # 封面
    chapters.append("---")
    chapters.append(f"title: 家族传记")
    chapters.append(f"generated: {datetime.now().isoformat()}")
    chapters.append(f"souls: {soul_count}")
    chapters.append("---")
    chapters.append("")

    _log("生成序言...")
    chapters.append(_generate_preface(tree, souls_data))

    _log("生成家族树...")
    chapters.append(_generate_family_tree_visual(tree))

    _log("生成各代故事...")
    chapters.append(_generate_generation_chapters(tree, souls_data, memories))

    _log("生成传家宝章节...")
    chapters.append(_generate_dna_chapter(dna_content))

    _log("生成家的味道...")
    chapters.append(_generate_food_chapter(rituals))

    _log("生成节日记忆...")
    chapters.append(_generate_holiday_chapter(rituals))

    _log("生成家训...")
    chapters.append(_generate_wisdom_chapter(tree, souls_data))

    _log("生成致后人...")
    chapters.append(_generate_letter_to_future(tree, souls_data))

    book = "\n\n".join(chapters)

    # 保存
    if output_path is None:
        output_path = DEFAULT_OUTPUT

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(book, encoding="utf-8")
    _log(f"家族传记已生成：{out}")
    _log(f"共 {len(book)} 字符，{book.count(chr(10))} 行")

    return book


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="家族传记生成引擎")
    parser.add_argument("--family-dir", default=DEFAULT_FAMILY_DIR,
                        help="家族数据目录（默认 ~/.pantheon）")
    parser.add_argument("--output", default=None,
                        help="输出文件路径（默认 ~/.pantheon/family/legacy/family_book.md）")

    args = parser.parse_args()

    book = generate_family_book(args.family_dir, args.output)
    _log("完成！")


if __name__ == "__main__":
    main()
