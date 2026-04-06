#!/usr/bin/env python3
"""
ritual_engine.py - 家族仪式与传统引擎

保存和检索家族的传统、食谱、节日习俗、家规、口头传统。
每个仪式不只是一个条目——它关联着特定的人、特定的时代、特定的故事。

这就是一个家的味道：不是抽象的文化，而是"外婆每年除夕都要做的那道红烧肉"。
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

PREFIX = "[ritual_engine]"
DEFAULT_FAMILY_DIR = os.path.expanduser("~/.pantheon")
RITUALS_DIR_NAME = "family/rituals"

# ---------------------------------------------------------------------------
# 仪式类型
# ---------------------------------------------------------------------------

RITUAL_TYPES = {
    "recipe": "食谱",
    "holiday": "节日习俗",
    "rule": "家规",
    "ceremony": "仪式",
    "oral": "口头传统",
}

# 月份与传统节日的映射（农历近似）
SEASONAL_CALENDAR = {
    1: ["春节", "元旦", "腊八节"],
    2: ["元宵节", "春节（可能延续）"],
    3: ["清明节", "春分"],
    4: ["清明节"],
    5: ["端午节", "母亲节"],
    6: ["端午节（可能）", "父亲节"],
    7: ["七夕"],
    8: ["中元节", "处暑"],
    9: ["中秋节", "重阳节", "教师节"],
    10: ["重阳节", "国庆节"],
    11: ["感恩节（如果家族有此传统）"],
    12: ["冬至", "腊八", "除夕准备"],
}


def _log(msg: str) -> None:
    print(f"{PREFIX} {msg}")


# ---------------------------------------------------------------------------
# 存储层
# ---------------------------------------------------------------------------

def _rituals_dir(family_dir: str) -> Path:
    """获取仪式存储目录。"""
    d = Path(family_dir) / RITUALS_DIR_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d


def _ritual_slug(name: str) -> str:
    """从仪式名称生成文件安全的标识符。"""
    # 保留中文和英文字母数字，其他替换为连字符
    slug = re.sub(r"[^\u4e00-\u9fff\w]", "-", name.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "unnamed"


def _ritual_to_md(ritual: Dict[str, Any]) -> str:
    """将仪式数据转换为 Markdown 格式。"""
    lines = [
        f"# {ritual['name']}",
        "",
        f"类型: {RITUAL_TYPES.get(ritual.get('type', ''), ritual.get('type', '未分类'))}",
    ]

    if ritual.get("season"):
        lines.append(f"时节: {ritual['season']}")
    if ritual.get("associated_souls"):
        lines.append(f"相关人: {'、'.join(ritual['associated_souls'])}")
    if ritual.get("era"):
        lines.append(f"年代: {ritual['era']}")

    lines.append("")
    lines.append("## 描述")
    lines.append("")
    lines.append(ritual.get("description", ""))
    lines.append("")

    if ritual.get("story"):
        lines.append("## 背后的故事")
        lines.append("")
        lines.append(ritual["story"])
        lines.append("")

    if ritual.get("ingredients"):
        lines.append("## 食材")
        lines.append("")
        for ing in ritual["ingredients"]:
            lines.append(f"- {ing}")
        lines.append("")

    if ritual.get("steps"):
        lines.append("## 步骤")
        lines.append("")
        for i, step in enumerate(ritual["steps"], 1):
            lines.append(f"{i}. {step}")
        lines.append("")

    if ritual.get("sayings"):
        lines.append("## 相关口头语")
        lines.append("")
        for saying in ritual["sayings"]:
            lines.append(f"> {saying}")
        lines.append("")

    if ritual.get("notes"):
        lines.append("## 备注")
        lines.append("")
        lines.append(ritual["notes"])
        lines.append("")

    return "\n".join(lines)


def _md_to_ritual(filepath: Path) -> Optional[Dict[str, Any]]:
    """从 Markdown 文件解析仪式数据。"""
    if not filepath.exists():
        return None

    try:
        text = filepath.read_text(encoding="utf-8")
    except IOError:
        return None

    ritual: Dict[str, Any] = {
        "file": str(filepath),
        "slug": filepath.stem,
    }

    # 提取标题
    title_match = re.search(r"^#\s+(.+)", text, re.MULTILINE)
    if title_match:
        ritual["name"] = title_match.group(1).strip()

    # 提取元数据
    type_match = re.search(r"^类型[：:]\s*(.+)", text, re.MULTILINE)
    if type_match:
        type_cn = type_match.group(1).strip()
        # 反向映射
        for k, v in RITUAL_TYPES.items():
            if v == type_cn or k == type_cn:
                ritual["type"] = k
                break
        else:
            ritual["type"] = type_cn

    season_match = re.search(r"^时节[：:]\s*(.+)", text, re.MULTILINE)
    if season_match:
        ritual["season"] = season_match.group(1).strip()

    souls_match = re.search(r"^相关人[：:]\s*(.+)", text, re.MULTILINE)
    if souls_match:
        ritual["associated_souls"] = [
            s.strip() for s in re.split(r"[,，、]", souls_match.group(1)) if s.strip()
        ]

    era_match = re.search(r"^年代[：:]\s*(.+)", text, re.MULTILINE)
    if era_match:
        ritual["era"] = era_match.group(1).strip()

    # 按 ## 分割提取内容段
    sections: Dict[str, str] = {}
    current_section = "_header"
    section_lines: List[str] = []

    for line in text.splitlines():
        h2 = re.match(r"^##\s+(.+)", line)
        if h2:
            if section_lines:
                sections[current_section] = "\n".join(section_lines).strip()
            current_section = h2.group(1).strip()
            section_lines = []
        else:
            section_lines.append(line)

    if section_lines:
        sections[current_section] = "\n".join(section_lines).strip()

    ritual["description"] = sections.get("描述", "")
    ritual["story"] = sections.get("背后的故事", "")
    ritual["notes"] = sections.get("备注", "")

    # 食材列表
    ingredients_text = sections.get("食材", "")
    if ingredients_text:
        ritual["ingredients"] = [
            re.sub(r"^[-*]\s*", "", ln).strip()
            for ln in ingredients_text.splitlines()
            if ln.strip() and ln.strip().startswith(("-", "*"))
        ]

    # 步骤列表
    steps_text = sections.get("步骤", "")
    if steps_text:
        ritual["steps"] = [
            re.sub(r"^\d+\.\s*", "", ln).strip()
            for ln in steps_text.splitlines()
            if ln.strip() and re.match(r"^\d+\.", ln.strip())
        ]

    # 口头语
    sayings_text = sections.get("相关口头语", "")
    if sayings_text:
        ritual["sayings"] = [
            ln.strip().lstrip("> ").strip()
            for ln in sayings_text.splitlines()
            if ln.strip().startswith(">")
        ]

    return ritual


# ---------------------------------------------------------------------------
# 核心 API
# ---------------------------------------------------------------------------

def add_ritual(
    name: str,
    ritual_type: str,
    description: str,
    associated_souls: Optional[List[str]] = None,
    story: Optional[str] = None,
    season: Optional[str] = None,
    era: Optional[str] = None,
    ingredients: Optional[List[str]] = None,
    steps: Optional[List[str]] = None,
    sayings: Optional[List[str]] = None,
    notes: Optional[str] = None,
    family_dir: str = DEFAULT_FAMILY_DIR,
) -> Dict[str, Any]:
    """
    添加一个家族仪式/传统。

    Args:
        name: 仪式名称（如"外婆的红烧肉"）
        ritual_type: 类型 (recipe/holiday/rule/ceremony/oral)
        description: 描述
        associated_souls: 关联灵魂名称列表
        story: 背后的故事
        season: 时节（如"春节"、"冬至"）
        era: 年代（如"1970s"）
        ingredients: 食材列表（仅食谱类型）
        steps: 步骤列表（仅食谱类型）
        sayings: 相关口头语
        notes: 备注

    Returns:
        保存的仪式数据
    """
    if ritual_type not in RITUAL_TYPES:
        _log(f"警告：未知仪式类型 '{ritual_type}'，可选：{list(RITUAL_TYPES.keys())}")

    ritual = {
        "name": name,
        "type": ritual_type,
        "description": description,
        "associated_souls": associated_souls or [],
        "story": story or "",
        "season": season or "",
        "era": era or "",
        "ingredients": ingredients or [],
        "steps": steps or [],
        "sayings": sayings or [],
        "notes": notes or "",
        "created_at": datetime.now().isoformat(),
    }

    slug = _ritual_slug(name)
    ritual["slug"] = slug

    rdir = _rituals_dir(family_dir)
    filepath = rdir / f"{slug}.md"

    md_content = _ritual_to_md(ritual)
    filepath.write_text(md_content, encoding="utf-8")

    _log(f"已保存仪式：{name} ({ritual_type}) → {filepath}")
    return ritual


def get_all_rituals(family_dir: str = DEFAULT_FAMILY_DIR) -> List[Dict]:
    """获取所有仪式。"""
    rdir = _rituals_dir(family_dir)
    rituals = []

    for f in sorted(rdir.glob("*.md")):
        ritual = _md_to_ritual(f)
        if ritual:
            rituals.append(ritual)

    _log(f"共加载 {len(rituals)} 个仪式")
    return rituals


def get_rituals_by_type(
    ritual_type: str,
    family_dir: str = DEFAULT_FAMILY_DIR,
) -> List[Dict]:
    """按类型筛选仪式。"""
    all_rituals = get_all_rituals(family_dir)
    filtered = [r for r in all_rituals if r.get("type") == ritual_type]
    _log(f"类型 '{RITUAL_TYPES.get(ritual_type, ritual_type)}' 共 {len(filtered)} 个仪式")
    return filtered


def get_rituals_by_soul(
    slug: str,
    family_dir: str = DEFAULT_FAMILY_DIR,
) -> List[Dict]:
    """查找某个灵魂参与的所有仪式。"""
    all_rituals = get_all_rituals(family_dir)
    filtered = []

    for r in all_rituals:
        souls = r.get("associated_souls", [])
        # 匹配 slug 或名称
        if slug in souls or any(slug in s for s in souls):
            filtered.append(r)

    _log(f"灵魂 '{slug}' 关联 {len(filtered)} 个仪式")
    return filtered


def get_seasonal_rituals(
    month: Optional[int] = None,
    family_dir: str = DEFAULT_FAMILY_DIR,
) -> List[Dict]:
    """
    获取当前时节（或指定月份）相关的家族传统。

    结合传统节日日历和仪式的 season 字段进行匹配。
    """
    if month is None:
        month = datetime.now().month

    # 当前月份对应的传统节日
    seasonal_keywords = SEASONAL_CALENDAR.get(month, [])
    _log(f"{month} 月相关节日：{'、'.join(seasonal_keywords) if seasonal_keywords else '无'}")

    all_rituals = get_all_rituals(family_dir)
    matched = []

    for r in all_rituals:
        season = r.get("season", "")
        description = r.get("description", "")
        combined = (season + " " + description).lower()

        # 检查是否匹配当前月份的节日关键词
        for kw in seasonal_keywords:
            if kw.lower() in combined or kw.lower() in r.get("name", "").lower():
                matched.append(r)
                break

    _log(f"{month} 月有 {len(matched)} 个应季仪式")
    return matched


def get_recipe_book(family_dir: str = DEFAULT_FAMILY_DIR) -> str:
    """生成家族食谱集锦（Markdown）。"""
    recipes = get_rituals_by_type("recipe", family_dir)
    if not recipes:
        return "暂无家族食谱记录。"

    lines = ["# 家的味道 — 家族食谱集", ""]
    for r in recipes:
        lines.append(f"## {r.get('name', '无名菜')}")
        lines.append("")
        if r.get("associated_souls"):
            lines.append(f"传承人：{'、'.join(r['associated_souls'])}")
        if r.get("era"):
            lines.append(f"年代：{r['era']}")
        lines.append("")

        if r.get("story"):
            lines.append(f"> {r['story']}")
            lines.append("")

        if r.get("description"):
            lines.append(r["description"])
            lines.append("")

        if r.get("ingredients"):
            lines.append("**食材：**")
            for ing in r["ingredients"]:
                lines.append(f"- {ing}")
            lines.append("")

        if r.get("steps"):
            lines.append("**做法：**")
            for i, step in enumerate(r["steps"], 1):
                lines.append(f"{i}. {step}")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="家族仪式与传统引擎")
    parser.add_argument("--action", required=True,
                        choices=["add", "list", "seasonal", "by-soul", "by-type", "recipes"],
                        help="操作类型")
    parser.add_argument("--name", help="仪式名称")
    parser.add_argument("--type", dest="ritual_type",
                        choices=list(RITUAL_TYPES.keys()),
                        help="仪式类型")
    parser.add_argument("--description", help="描述")
    parser.add_argument("--souls", nargs="*", help="关联灵魂")
    parser.add_argument("--story", help="背后的故事")
    parser.add_argument("--season", help="时节")
    parser.add_argument("--era", help="年代")
    parser.add_argument("--slug", help="灵魂标识符（by-soul 模式）")
    parser.add_argument("--month", type=int, help="月份（seasonal 模式）")
    parser.add_argument("--family-dir", default=DEFAULT_FAMILY_DIR,
                        help="家族数据目录")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    if args.action == "add":
        if not args.name or not args.ritual_type or not args.description:
            parser.error("添加仪式需要 --name、--type 和 --description")
        ritual = add_ritual(
            name=args.name,
            ritual_type=args.ritual_type,
            description=args.description,
            associated_souls=args.souls,
            story=args.story,
            season=args.season,
            era=args.era,
            family_dir=args.family_dir,
        )
        if args.json:
            print(json.dumps(ritual, ensure_ascii=False, indent=2))
        else:
            print(f"已添加仪式：{ritual['name']} ({RITUAL_TYPES.get(ritual['type'], ritual['type'])})")

    elif args.action == "list":
        rituals = get_all_rituals(args.family_dir)
        if args.json:
            print(json.dumps(rituals, ensure_ascii=False, indent=2, default=str))
        else:
            if not rituals:
                print("暂无仪式记录。")
            for r in rituals:
                rtype = RITUAL_TYPES.get(r.get("type", ""), r.get("type", ""))
                souls_str = "、".join(r.get("associated_souls", [])) or "未关联"
                print(f"  [{rtype}] {r.get('name', '?')} — {souls_str}")

    elif args.action == "seasonal":
        rituals = get_seasonal_rituals(args.month, args.family_dir)
        month = args.month or datetime.now().month
        if args.json:
            print(json.dumps(rituals, ensure_ascii=False, indent=2, default=str))
        else:
            holidays = SEASONAL_CALENDAR.get(month, [])
            print(f"\n{month} 月的节日：{'、'.join(holidays) if holidays else '无传统节日'}")
            print(f"相关家族传统：")
            if not rituals:
                print("  暂无记录。")
            for r in rituals:
                print(f"  - {r.get('name', '?')}：{r.get('description', '')[:60]}...")

    elif args.action == "by-soul":
        if not args.slug:
            parser.error("by-soul 模式需要 --slug")
        rituals = get_rituals_by_soul(args.slug, args.family_dir)
        if args.json:
            print(json.dumps(rituals, ensure_ascii=False, indent=2, default=str))
        else:
            print(f"\n{args.slug} 参与的家族传统：")
            if not rituals:
                print("  暂无记录。")
            for r in rituals:
                rtype = RITUAL_TYPES.get(r.get("type", ""), r.get("type", ""))
                print(f"  [{rtype}] {r.get('name', '?')}")
                if r.get("story"):
                    print(f"    故事：{r['story'][:80]}...")

    elif args.action == "by-type":
        if not args.ritual_type:
            parser.error("by-type 模式需要 --type")
        rituals = get_rituals_by_type(args.ritual_type, args.family_dir)
        if args.json:
            print(json.dumps(rituals, ensure_ascii=False, indent=2, default=str))
        else:
            type_cn = RITUAL_TYPES.get(args.ritual_type, args.ritual_type)
            print(f"\n类型「{type_cn}」的仪式：")
            if not rituals:
                print("  暂无记录。")
            for r in rituals:
                print(f"  - {r.get('name', '?')}")

    elif args.action == "recipes":
        print(get_recipe_book(args.family_dir))


if __name__ == "__main__":
    main()
