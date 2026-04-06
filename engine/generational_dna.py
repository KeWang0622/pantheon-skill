#!/usr/bin/env python3
"""
generational_dna.py - 代际基因提取引擎

扫描整个家族的灵魂档案，发现跨代传承的精神 DNA：
重复出现的价值观、口头禅、行为模式、打破的模式、文化传承。

这是 pantheon-skill 独有的能力——不是理解一个人，而是理解一个家族的精神基因组。
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

PREFIX = "[generational_dna]"
DEFAULT_FAMILY_DIR = os.path.expanduser("~/.pantheon")
DEFAULT_OUTPUT = "generational_dna.md"


def _log(msg: str) -> None:
    print(f"{PREFIX} {msg}")


# ---------------------------------------------------------------------------
# 灵魂档案解析
# ---------------------------------------------------------------------------

def _parse_soul_md(filepath: Path) -> Dict[str, Any]:
    """
    解析 soul.md 文件，提取结构化字段。

    支持的字段格式（Markdown 标题或键值对）：
    - ## 价值观 / Values
    - ## 口头禅 / Catchphrases
    - ## 性格 / Personality
    - ## 教育方式 / Parenting
    - ## 习惯 / Habits
    - ## 传统 / Traditions
    """
    result: Dict[str, Any] = {
        "file": str(filepath),
        "slug": filepath.parent.name,
        "values": [],
        "catchphrases": [],
        "personality": [],
        "parenting": [],
        "habits": [],
        "traditions": [],
        "raw_sections": {},
    }

    if not filepath.exists():
        return result

    try:
        text = filepath.read_text(encoding="utf-8")
    except IOError:
        _log(f"警告：无法读取 {filepath}")
        return result

    # 提取元信息（如果有 YAML front-matter 或简单键值）
    name_match = re.search(r"^#\s+(.+)", text, re.MULTILINE)
    if name_match:
        result["name"] = name_match.group(1).strip()

    # 按 ## 标题分割
    current_section = "_preamble"
    sections: Dict[str, List[str]] = defaultdict(list)

    for line in text.splitlines():
        heading_match = re.match(r"^##\s+(.+)", line)
        if heading_match:
            current_section = heading_match.group(1).strip().lower()
            continue
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            sections[current_section].append(stripped)

    result["raw_sections"] = dict(sections)

    # 映射到标准字段
    _section_map = {
        "values": ["价值观", "values", "核心价值", "信念", "beliefs"],
        "catchphrases": ["口头禅", "catchphrases", "口癖", "经常说的话", "语录", "quotes"],
        "personality": ["性格", "personality", "个性", "特点", "character"],
        "parenting": ["教育方式", "parenting", "育儿", "教育理念", "管教方式"],
        "habits": ["习惯", "habits", "日常", "生活习惯", "routines"],
        "traditions": ["传统", "traditions", "文化", "cultural", "习俗", "customs"],
    }

    for field, keywords in _section_map.items():
        for sec_name, sec_lines in sections.items():
            if any(kw in sec_name for kw in keywords):
                # 提取列表项（去掉 markdown 列表符号）
                items = []
                for ln in sec_lines:
                    cleaned = re.sub(r"^[-*+]\s*", "", ln).strip()
                    if cleaned:
                        items.append(cleaned)
                result[field].extend(items)

    return result


def _load_all_souls(family_dir: str) -> List[Dict[str, Any]]:
    """加载所有灵魂档案。"""
    souls_dir = Path(family_dir) / "souls"
    souls = []

    if not souls_dir.exists():
        _log(f"灵魂目录不存在：{souls_dir}")
        return souls

    for soul_dir in sorted(souls_dir.iterdir()):
        if not soul_dir.is_dir():
            continue
        soul_md = soul_dir / "soul.md"
        if soul_md.exists():
            soul = _parse_soul_md(soul_md)
            souls.append(soul)
            _log(f"已加载：{soul.get('name', soul['slug'])} ({soul['slug']})")

    _log(f"共加载 {len(souls)} 个灵魂档案")
    return souls


def _load_family_tree(family_dir: str) -> Dict[str, Any]:
    """加载家族图谱以获取代际信息。"""
    tree_path = Path(family_dir) / "family" / "tree.json"
    if tree_path.exists():
        try:
            with open(tree_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"souls": {}, "edges": []}


# ---------------------------------------------------------------------------
# 代际 DNA 分析
# ---------------------------------------------------------------------------

def _find_repeated_values(souls: List[Dict]) -> List[Dict]:
    """找出在多个灵魂中重复出现的价值观。"""
    # 对每个价值观进行标准化和计数
    value_to_souls: Dict[str, List[str]] = defaultdict(list)

    for soul in souls:
        name = soul.get("name", soul["slug"])
        for v in soul.get("values", []):
            # 简单标准化：去标点、转小写
            normalized = re.sub(r"[，。、！？,.!?]", "", v).strip().lower()
            if normalized:
                value_to_souls[normalized].append(name)

    # 也做模糊匹配——如果两个值有共同关键词
    keyword_to_values: Dict[str, Set[str]] = defaultdict(set)
    for v in value_to_souls:
        # 中文按字/词分，英文按空格分
        words = set(re.findall(r"[\u4e00-\u9fff]+|[a-z]+", v))
        for w in words:
            if len(w) >= 2:  # 至少两个字/字母才有意义
                keyword_to_values[w].add(v)

    results = []
    seen = set()
    for value, holders in value_to_souls.items():
        if len(holders) >= 2 and value not in seen:
            seen.add(value)
            results.append({
                "type": "repeated_value",
                "value": value,
                "souls": holders,
                "count": len(holders),
            })

    return sorted(results, key=lambda x: x["count"], reverse=True)


def _find_inherited_phrases(souls: List[Dict]) -> List[Dict]:
    """找出跨代传承的口头禅。"""
    phrase_to_souls: Dict[str, List[str]] = defaultdict(list)

    for soul in souls:
        name = soul.get("name", soul["slug"])
        for phrase in soul.get("catchphrases", []):
            normalized = phrase.strip().strip("\"'""''「」")
            if normalized:
                phrase_to_souls[normalized].append(name)

    results = []
    for phrase, holders in phrase_to_souls.items():
        if len(holders) >= 2:
            results.append({
                "type": "inherited_phrase",
                "phrase": phrase,
                "souls": holders,
                "count": len(holders),
            })

    # 也找相似短语（一个包含另一个）
    all_phrases = list(phrase_to_souls.keys())
    for i, p1 in enumerate(all_phrases):
        for p2 in all_phrases[i + 1:]:
            if p1 in p2 or p2 in p1:
                holders = list(set(phrase_to_souls[p1] + phrase_to_souls[p2]))
                if len(holders) >= 2:
                    results.append({
                        "type": "inherited_phrase_variant",
                        "phrase": f"{p1} ↔ {p2}",
                        "souls": holders,
                        "count": len(holders),
                    })

    return results


def _find_behavioral_patterns(souls: List[Dict]) -> List[Dict]:
    """找出行为模式的代际传承。"""
    results = []

    # 比较教育方式
    parenting_styles: Dict[str, List[str]] = defaultdict(list)
    for soul in souls:
        name = soul.get("name", soul["slug"])
        for p in soul.get("parenting", []):
            normalized = re.sub(r"[，。、,.!?]", "", p).strip().lower()
            if normalized:
                parenting_styles[normalized].append(name)

    for style, holders in parenting_styles.items():
        if len(holders) >= 2:
            results.append({
                "type": "behavioral_pattern",
                "category": "教育方式",
                "pattern": style,
                "souls": holders,
            })

    # 比较习惯
    habit_keywords: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    for soul in souls:
        name = soul.get("name", soul["slug"])
        for h in soul.get("habits", []):
            words = set(re.findall(r"[\u4e00-\u9fff]{2,}|[a-z]{3,}", h.lower()))
            for w in words:
                habit_keywords[w].append((name, h))

    for keyword, entries in habit_keywords.items():
        unique_souls = list(set(e[0] for e in entries))
        if len(unique_souls) >= 2:
            results.append({
                "type": "behavioral_pattern",
                "category": "共同习惯",
                "pattern": f"关键词「{keyword}」",
                "souls": unique_souls,
                "details": [e[1] for e in entries],
            })

    return results


def _find_breaking_patterns(souls: List[Dict]) -> List[Dict]:
    """
    找出代际中被打破的模式。

    基于对比：如果一个灵魂的教育方式/性格与其祖先明显不同，
    这可能是一个有意识的突破。
    """
    results = []

    # 简单启发式：查找包含"但是""不同""改变""不像"等词的描述
    break_keywords = ["但是", "不同", "改变", "不像", "相反", "决定不", "选择了",
                      "unlike", "different", "changed", "break", "chose"]

    for soul in souls:
        name = soul.get("name", soul["slug"])
        all_text = " ".join(
            soul.get("parenting", []) +
            soul.get("personality", []) +
            soul.get("values", [])
        )
        for kw in break_keywords:
            if kw in all_text.lower():
                results.append({
                    "type": "breaking_pattern",
                    "soul": name,
                    "hint": f"在 {name} 的描述中发现可能的代际突破（关键词：{kw}）",
                    "context": all_text[:200],
                })
                break  # 每个灵魂只记一次

    return results


def _find_cultural_inheritance(souls: List[Dict]) -> List[Dict]:
    """找出文化传承：共同的传统、食物、信仰。"""
    tradition_to_souls: Dict[str, List[str]] = defaultdict(list)

    for soul in souls:
        name = soul.get("name", soul["slug"])
        for t in soul.get("traditions", []):
            normalized = t.strip().lower()
            if normalized:
                tradition_to_souls[normalized].append(name)

    results = []
    for tradition, holders in tradition_to_souls.items():
        if len(holders) >= 2:
            results.append({
                "type": "cultural_inheritance",
                "tradition": tradition,
                "souls": holders,
                "count": len(holders),
            })

    return results


# ---------------------------------------------------------------------------
# 综合分析 & 输出
# ---------------------------------------------------------------------------

def analyze_generational_dna(
    family_dir: str = DEFAULT_FAMILY_DIR,
) -> Dict[str, List[Dict]]:
    """
    执行完整的代际 DNA 分析。

    Returns:
        包含所有发现的字典，按类型分组
    """
    _log("开始代际 DNA 分析...")
    souls = _load_all_souls(family_dir)

    if not souls:
        _log("没有找到灵魂档案，无法分析")
        return {}

    results = {
        "repeated_values": _find_repeated_values(souls),
        "inherited_phrases": _find_inherited_phrases(souls),
        "behavioral_patterns": _find_behavioral_patterns(souls),
        "breaking_patterns": _find_breaking_patterns(souls),
        "cultural_inheritance": _find_cultural_inheritance(souls),
    }

    total = sum(len(v) for v in results.values())
    _log(f"分析完成，共发现 {total} 个代际 DNA 模式")
    return results


def generate_dna_report(
    family_dir: str = DEFAULT_FAMILY_DIR,
    output_path: Optional[str] = None,
) -> str:
    """
    生成代际 DNA 报告（Markdown 格式）。

    Args:
        family_dir: 家族数据目录
        output_path: 输出文件路径（None 则只返回不写文件）

    Returns:
        Markdown 格式的报告文本
    """
    dna = analyze_generational_dna(family_dir)

    lines = [
        "# 家族精神基因组",
        "",
        "> 由 Pantheon 代际 DNA 引擎自动生成",
        "",
    ]

    # --- 重复价值观 ---
    lines.append("## 🧬 代代相传的价值观")
    lines.append("")
    repeated = dna.get("repeated_values", [])
    if repeated:
        for item in repeated:
            souls_str = "、".join(item["souls"])
            lines.append(f"- **{item['value']}** — 出现在：{souls_str}")
    else:
        lines.append("_暂未发现跨代重复的价值观，可能需要更多灵魂档案。_")
    lines.append("")

    # --- 传承口头禅 ---
    lines.append("## 💬 代际口头禅")
    lines.append("")
    phrases = dna.get("inherited_phrases", [])
    if phrases:
        for item in phrases:
            souls_str = "、".join(item["souls"])
            ptype = "变体" if item["type"] == "inherited_phrase_variant" else "原句"
            lines.append(f"- 「{item['phrase']}」（{ptype}）— {souls_str}")
    else:
        lines.append("_暂未发现跨代传承的口头禅。_")
    lines.append("")

    # --- 行为模式 ---
    lines.append("## 🔄 行为模式传承")
    lines.append("")
    patterns = dna.get("behavioral_patterns", [])
    if patterns:
        for item in patterns:
            souls_str = "、".join(item["souls"])
            lines.append(f"- [{item['category']}] {item['pattern']} — {souls_str}")
            if "details" in item:
                for d in item["details"][:3]:
                    lines.append(f"  - {d}")
    else:
        lines.append("_暂未发现跨代行为模式。_")
    lines.append("")

    # --- 打破的模式 ---
    lines.append("## ✊ 被打破的代际模式")
    lines.append("")
    breaks = dna.get("breaking_patterns", [])
    if breaks:
        for item in breaks:
            lines.append(f"- **{item['soul']}**: {item['hint']}")
            if item.get("context"):
                lines.append(f"  > {item['context'][:150]}...")
    else:
        lines.append("_暂未发现明显的代际突破模式。_")
    lines.append("")

    # --- 文化传承 ---
    lines.append("## 🏮 文化传承")
    lines.append("")
    cultural = dna.get("cultural_inheritance", [])
    if cultural:
        for item in cultural:
            souls_str = "、".join(item["souls"])
            lines.append(f"- **{item['tradition']}** — {souls_str}")
    else:
        lines.append("_暂未发现共同的文化传统记录。_")
    lines.append("")

    # --- 总结 ---
    total = sum(len(v) for v in dna.values())
    lines.append("---")
    lines.append(f"_共分析发现 {total} 个代际 DNA 模式。_")

    report = "\n".join(lines)

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        _log(f"报告已保存：{out}")

    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="代际 DNA 提取引擎")
    parser.add_argument("--family-dir", default=DEFAULT_FAMILY_DIR,
                        help="家族数据目录（默认 ~/.pantheon）")
    parser.add_argument("--output", default=None,
                        help="输出文件路径（默认仅打印）")
    parser.add_argument("--json", action="store_true",
                        help="以 JSON 格式输出原始分析结果")

    args = parser.parse_args()

    if args.json:
        results = analyze_generational_dna(args.family_dir)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        report = generate_dna_report(args.family_dir, args.output)
        print(report)


if __name__ == "__main__":
    main()
