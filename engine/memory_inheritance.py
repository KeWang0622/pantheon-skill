#!/usr/bin/env python3
"""
memory_inheritance.py - 记忆传承引擎

模拟记忆在家族中的流动方式。爷爷的故事会传到爸爸耳中，
爸爸会在饭桌上跟你说"你爷爷以前总说……"。

核心洞察：家族记忆不是个人记忆——它在代际间传递、变形、放大、遗忘。
一个故事从爷爷嘴里说出来是一个样，到爸爸嘴里又是另一个样。
"""

import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

PREFIX = "[memory_inheritance]"
DEFAULT_FAMILY_DIR = os.path.expanduser("~/.pantheon")


def _log(msg: str) -> None:
    print(f"{PREFIX} {msg}")


# ---------------------------------------------------------------------------
# 数据加载
# ---------------------------------------------------------------------------

def _load_family_tree(family_dir: str) -> Dict[str, Any]:
    """加载家族图谱。"""
    tree_path = Path(family_dir) / "family" / "tree.json"
    if tree_path.exists():
        try:
            with open(tree_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as exc:
            _log(f"警告：读取图谱失败 ({exc})")
    return {"souls": {}, "edges": []}


def _load_memory_md(soul_dir: Path) -> List[Dict[str, Any]]:
    """
    解析一个灵魂的 memory.md 文件，提取记忆条目。

    支持的格式：
    - ## 记忆标题 / ### 记忆标题
    - 正文段落
    - 可选元数据行：年份:、地点:、相关人:、类型:
    """
    memory_file = soul_dir / "memory.md"
    if not memory_file.exists():
        return []

    try:
        text = memory_file.read_text(encoding="utf-8")
    except IOError:
        return []

    memories = []
    current: Optional[Dict[str, Any]] = None

    for line in text.splitlines():
        heading = re.match(r"^#{2,3}\s+(.+)", line)
        if heading:
            if current and current.get("content"):
                memories.append(current)
            current = {
                "title": heading.group(1).strip(),
                "content": "",
                "year": None,
                "location": None,
                "related_souls": [],
                "type": "personal",
                "source_slug": soul_dir.name,
            }
            continue

        if current is None:
            continue

        # 尝试提取元数据
        meta_match = re.match(r"^(年份|year|时间)[：:]\s*(.+)", line, re.IGNORECASE)
        if meta_match:
            try:
                current["year"] = int(re.search(r"\d{4}", meta_match.group(2)).group())
            except (AttributeError, ValueError):
                current["year_text"] = meta_match.group(2).strip()
            continue

        loc_match = re.match(r"^(地点|location|地方)[：:]\s*(.+)", line, re.IGNORECASE)
        if loc_match:
            current["location"] = loc_match.group(2).strip()
            continue

        rel_match = re.match(r"^(相关人|related|人物)[：:]\s*(.+)", line, re.IGNORECASE)
        if rel_match:
            current["related_souls"] = [
                s.strip() for s in re.split(r"[,，、]", rel_match.group(2)) if s.strip()
            ]
            continue

        type_match = re.match(r"^(类型|type)[：:]\s*(.+)", line, re.IGNORECASE)
        if type_match:
            current["type"] = type_match.group(2).strip()
            continue

        # 正文
        if line.strip():
            current["content"] += line.strip() + "\n"

    if current and current.get("content"):
        memories.append(current)

    return memories


def _load_all_memories(family_dir: str) -> Dict[str, List[Dict]]:
    """加载所有灵魂的记忆，按 slug 索引。"""
    souls_dir = Path(family_dir) / "souls"
    all_memories: Dict[str, List[Dict]] = {}

    if not souls_dir.exists():
        _log(f"灵魂目录不存在：{souls_dir}")
        return all_memories

    for soul_dir in sorted(souls_dir.iterdir()):
        if soul_dir.is_dir():
            memories = _load_memory_md(soul_dir)
            if memories:
                all_memories[soul_dir.name] = memories
                _log(f"加载 {soul_dir.name} 的 {len(memories)} 条记忆")

    total = sum(len(v) for v in all_memories.values())
    _log(f"共加载 {total} 条记忆")
    return all_memories


# ---------------------------------------------------------------------------
# 家族关系工具
# ---------------------------------------------------------------------------

def _build_parent_child_map(tree: Dict) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    构建父母→子女和子女→父母的映射。

    Returns:
        (parent_to_children, child_to_parents)
    """
    p2c: Dict[str, List[str]] = defaultdict(list)
    c2p: Dict[str, List[str]] = defaultdict(list)

    for edge in tree.get("edges", []):
        if edge["type"] == "parent-child":
            p2c[edge["from"]].append(edge["to"])
            c2p[edge["to"]].append(edge["from"])

    return dict(p2c), dict(c2p)


def _get_ancestors(slug: str, c2p: Dict[str, List[str]], max_depth: int = 10) -> List[Tuple[str, int]]:
    """获取祖先列表，附带代际距离。"""
    ancestors = []
    visited = {slug}
    frontier = [(slug, 0)]

    while frontier:
        current, depth = frontier.pop(0)
        if depth > max_depth:
            break
        for parent in c2p.get(current, []):
            if parent not in visited:
                visited.add(parent)
                ancestors.append((parent, depth + 1))
                frontier.append((parent, depth + 1))

    return ancestors


def _get_descendants(slug: str, p2c: Dict[str, List[str]], max_depth: int = 10) -> List[Tuple[str, int]]:
    """获取后代列表，附带代际距离。"""
    descendants = []
    visited = {slug}
    frontier = [(slug, 0)]

    while frontier:
        current, depth = frontier.pop(0)
        if depth > max_depth:
            break
        for child in p2c.get(current, []):
            if child not in visited:
                visited.add(child)
                descendants.append((child, depth + 1))
                frontier.append((child, depth + 1))

    return descendants


def _get_soul_name(slug: str, tree: Dict) -> str:
    """获取灵魂的显示名称。"""
    soul = tree.get("souls", {}).get(slug, {})
    return soul.get("name", slug)


# ---------------------------------------------------------------------------
# 记忆传承核心逻辑
# ---------------------------------------------------------------------------

def _compute_memory_distortion(memory: Dict, generations_passed: int) -> Dict:
    """
    模拟记忆在代际传递中的变形。

    规则：
    - 1代传承：基本准确，但加入传述者的视角
    - 2代传承：细节模糊，数字可能夸大，情感色彩增强
    - 3代+传承：成为家族传说，可能严重变形

    Returns:
        变形后的记忆描述
    """
    distortion = {
        "original": memory,
        "generations_passed": generations_passed,
        "distortion_level": "none",
        "notes": [],
    }

    if generations_passed == 0:
        distortion["distortion_level"] = "none"
        distortion["retelling"] = memory["content"]

    elif generations_passed == 1:
        distortion["distortion_level"] = "mild"
        distortion["notes"] = [
            "基本准确，但融入了传述者的理解和情感",
            "可能省略了原始记忆中的某些细节",
            "时间和地点可能略有模糊",
        ]
        distortion["retelling_prefix"] = "听{ancestor}说过，"
        distortion["retelling"] = memory["content"]

    elif generations_passed == 2:
        distortion["distortion_level"] = "moderate"
        distortion["notes"] = [
            "细节开始模糊，数字可能被夸大",
            "故事的情感核心被保留，但具体情节可能简化",
            "可能与其他故事混淆",
        ]
        distortion["retelling_prefix"] = "老一辈常提起，"
        distortion["retelling"] = _simplify_content(memory["content"])

    else:
        distortion["distortion_level"] = "heavy"
        distortion["notes"] = [
            "已成为家族传说，细节高度概括",
            "可能被美化或戏剧化",
            "核心教训/情感被保留，但故事本身可能面目全非",
        ]
        distortion["retelling_prefix"] = "家里一直流传着一个故事，"
        distortion["retelling"] = _legendify_content(memory["content"])

    return distortion


def _simplify_content(content: str) -> str:
    """模拟二代传述的简化效果。"""
    lines = content.strip().splitlines()
    if len(lines) <= 2:
        return content
    # 保留首尾，中间概括
    return lines[0] + "\n（中间的细节已经不太记得了）\n" + lines[-1]


def _legendify_content(content: str) -> str:
    """模拟三代以上传述的传说化效果。"""
    # 提取第一句作为核心
    first_sentence = re.split(r"[。！？\n]", content)[0]
    if first_sentence:
        return first_sentence + "……具体的细节，每个人说的都不太一样了。"
    return "具体的故事，已经说不清了，但家里人都知道这件事。"


def get_inherited_memories(
    slug: str,
    family_dir: str = DEFAULT_FAMILY_DIR,
) -> List[Dict]:
    """
    获取某个灵魂会知道的所有继承记忆。

    一个人不仅有自己的记忆，还有从长辈那里听来的故事。
    爸爸会跟你讲爷爷的故事，妈妈会讲外婆的故事。

    Args:
        slug: 灵魂标识符
        family_dir: 家族数据目录

    Returns:
        记忆列表，每条包含来源、代际距离、变形程度
    """
    _log(f"正在追溯 {slug} 的继承记忆...")

    tree = _load_family_tree(family_dir)
    all_memories = _load_all_memories(family_dir)
    _, c2p = _build_parent_child_map(tree)

    # 获取祖先链
    ancestors = _get_ancestors(slug, c2p)

    inherited = []

    # 自己的记忆（0代距离）
    for mem in all_memories.get(slug, []):
        inherited.append({
            "memory": mem,
            "source_slug": slug,
            "source_name": _get_soul_name(slug, tree),
            "inherited_from": None,
            "generations_passed": 0,
            "distortion": _compute_memory_distortion(mem, 0),
        })

    # 祖先的记忆
    for ancestor_slug, distance in ancestors:
        ancestor_name = _get_soul_name(ancestor_slug, tree)
        for mem in all_memories.get(ancestor_slug, []):
            inherited.append({
                "memory": mem,
                "source_slug": ancestor_slug,
                "source_name": ancestor_name,
                "inherited_from": ancestor_slug,
                "generations_passed": distance,
                "distortion": _compute_memory_distortion(mem, distance),
            })

    _log(f"{slug} 共有 {len(inherited)} 条记忆（含继承）")
    return inherited


def get_shared_event_perspectives(
    event_description: str,
    family_dir: str = DEFAULT_FAMILY_DIR,
) -> List[Dict]:
    """
    找出同一事件在不同家族成员记忆中的不同版本。

    家族中的共同事件（如过年、搬家、某次争吵），每个人记住的侧面不同。
    爷爷记得的是花了多少钱，妈妈记得的是厨房里的忙碌，小孩记得的是放鞭炮。

    Args:
        event_description: 事件关键词或描述
        family_dir: 家族数据目录

    Returns:
        不同视角的记忆列表
    """
    _log(f"正在搜索与「{event_description}」相关的多视角记忆...")

    tree = _load_family_tree(family_dir)
    all_memories = _load_all_memories(family_dir)

    # 分词（简单处理）
    keywords = set(re.findall(r"[\u4e00-\u9fff]{2,}|[a-zA-Z]{3,}", event_description.lower()))

    perspectives = []

    for slug, memories in all_memories.items():
        for mem in memories:
            content_lower = (mem.get("title", "") + " " + mem.get("content", "")).lower()
            # 计算关键词匹配度
            matched = sum(1 for kw in keywords if kw in content_lower)
            if matched > 0:
                relevance = matched / max(len(keywords), 1)
                soul = tree.get("souls", {}).get(slug, {})
                perspectives.append({
                    "slug": slug,
                    "name": soul.get("name", slug),
                    "generation": soul.get("generation", "?"),
                    "memory_title": mem.get("title", "无题"),
                    "content": mem.get("content", ""),
                    "year": mem.get("year"),
                    "relevance": relevance,
                })

    # 按相关度排序
    perspectives.sort(key=lambda x: x["relevance"], reverse=True)

    _log(f"找到 {len(perspectives)} 个相关视角")
    return perspectives


def build_inheritance_map(
    family_dir: str = DEFAULT_FAMILY_DIR,
) -> Dict[str, Dict]:
    """
    构建完整的记忆传承地图。

    显示哪个灵魂知道哪些其他灵魂的故事，以及通过什么路径传递。

    Returns:
        {slug: {"own_memories": N, "inherited_memories": N, "knows_about": [slugs]}}
    """
    _log("正在构建记忆传承地图...")

    tree = _load_family_tree(family_dir)
    all_memories = _load_all_memories(family_dir)
    _, c2p = _build_parent_child_map(tree)

    inheritance_map = {}

    for slug in tree.get("souls", {}):
        ancestors = _get_ancestors(slug, c2p)
        own_count = len(all_memories.get(slug, []))

        # 此灵魂能接触到的祖先记忆
        inherited_sources = []
        total_inherited = 0
        for anc_slug, distance in ancestors:
            anc_memories = all_memories.get(anc_slug, [])
            if anc_memories:
                inherited_sources.append({
                    "slug": anc_slug,
                    "name": _get_soul_name(anc_slug, tree),
                    "distance": distance,
                    "memory_count": len(anc_memories),
                })
                total_inherited += len(anc_memories)

        inheritance_map[slug] = {
            "name": _get_soul_name(slug, tree),
            "own_memories": own_count,
            "inherited_memory_count": total_inherited,
            "total_accessible": own_count + total_inherited,
            "knows_about": inherited_sources,
        }

    _log(f"传承地图构建完成，覆盖 {len(inheritance_map)} 个灵魂")
    return inheritance_map


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="记忆传承引擎")
    parser.add_argument("--slug", help="灵魂标识符")
    parser.add_argument("--action", required=True,
                        choices=["inherited", "shared-event", "map"],
                        help="操作类型")
    parser.add_argument("--event", help="事件描述（shared-event 模式）")
    parser.add_argument("--family-dir", default=DEFAULT_FAMILY_DIR,
                        help="家族数据目录")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    if args.action == "inherited":
        if not args.slug:
            parser.error("inherited 模式需要 --slug")
        memories = get_inherited_memories(args.slug, args.family_dir)

        if args.json:
            print(json.dumps(memories, ensure_ascii=False, indent=2, default=str))
        else:
            print(f"\n{args.slug} 的记忆档案（含继承）")
            print("=" * 50)
            for m in memories:
                dist = m["generations_passed"]
                dist_label = "亲身经历" if dist == 0 else f"继承自 {m['source_name']}（{dist}代前）"
                distortion = m["distortion"]["distortion_level"]
                print(f"\n[{dist_label}] (变形程度: {distortion})")
                print(f"  标题: {m['memory']['title']}")
                content_preview = m["memory"]["content"][:100].replace("\n", " ")
                print(f"  内容: {content_preview}...")
                if dist > 0:
                    prefix = m["distortion"].get("retelling_prefix", "")
                    if prefix:
                        ancestor = m["source_name"]
                        print(f"  转述: {prefix.format(ancestor=ancestor)}")
                    for note in m["distortion"].get("notes", []):
                        print(f"  · {note}")

    elif args.action == "shared-event":
        if not args.event:
            parser.error("shared-event 模式需要 --event")
        perspectives = get_shared_event_perspectives(args.event, args.family_dir)

        if args.json:
            print(json.dumps(perspectives, ensure_ascii=False, indent=2))
        else:
            print(f"\n关于「{args.event}」的多视角记忆")
            print("=" * 50)
            if not perspectives:
                print("未找到相关记忆。")
            for p in perspectives:
                print(f"\n[{p['name']} · 第{p['generation']}代] (相关度: {p['relevance']:.0%})")
                print(f"  {p['memory_title']}")
                content_preview = p["content"][:150].replace("\n", " ")
                print(f"  {content_preview}...")

    elif args.action == "map":
        imap = build_inheritance_map(args.family_dir)

        if args.json:
            print(json.dumps(imap, ensure_ascii=False, indent=2))
        else:
            print("\n记忆传承地图")
            print("=" * 50)
            for slug, info in imap.items():
                print(f"\n{info['name']} ({slug})")
                print(f"  自有记忆: {info['own_memories']} 条")
                print(f"  继承记忆: {info['inherited_memory_count']} 条")
                print(f"  可触及总量: {info['total_accessible']} 条")
                if info["knows_about"]:
                    print(f"  知晓以下先人的故事:")
                    for src in info["knows_about"]:
                        print(f"    - {src['name']} ({src['distance']}代前, {src['memory_count']}条)")


if __name__ == "__main__":
    main()
