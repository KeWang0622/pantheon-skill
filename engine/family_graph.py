#!/usr/bin/env python3
"""
family_graph.py - 家族图谱引擎

将家族关系建模为有向图，支持跨代关系查询、共同祖先查找、世系路径追溯。
数据以 JSON 格式存储在 ~/.pantheon/family/tree.json。

与 ex-skill 的本质区别：这不是重建一个人，而是重建一整个家族系统。
每个节点是一个灵魂（soul），边是血缘或姻亲关系，承载着代际信息。
"""

import argparse
import json
import os
import sys
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PREFIX = "[family_graph]"
DEFAULT_TREE_PATH = os.path.expanduser("~/.pantheon/family/tree.json")

# ---------------------------------------------------------------------------
# 关系类型常量
# ---------------------------------------------------------------------------
REL_PARENT_CHILD = "parent-child"
REL_SPOUSE = "spouse"
REL_SIBLING = "sibling"

VALID_REL_TYPES = {REL_PARENT_CHILD, REL_SPOUSE, REL_SIBLING}

# ---------------------------------------------------------------------------
# 中文关系名称映射（用于自然语言描述）
# ---------------------------------------------------------------------------
_PATERNAL_TITLES = {
    (1, "male"): "父亲",
    (1, "female"): "母亲",
    (2, "male"): "祖父",
    (2, "female"): "祖母",
    (3, "male"): "曾祖父",
    (3, "female"): "曾祖母",
    (-1, "male"): "儿子",
    (-1, "female"): "女儿",
    (-2, "male"): "孙子",
    (-2, "female"): "孙女",
}


def _log(msg: str) -> None:
    print(f"{PREFIX} {msg}")


# ---------------------------------------------------------------------------
# 图谱数据结构
# ---------------------------------------------------------------------------

def _empty_tree() -> Dict[str, Any]:
    """返回空的家族图谱结构。"""
    return {
        "meta": {
            "version": "1.0",
            "description": "Pantheon 家族图谱"
        },
        "souls": {},
        "edges": []
    }


def _load_tree(path: str = DEFAULT_TREE_PATH) -> Dict[str, Any]:
    """加载家族图谱 JSON，不存在则返回空结构。"""
    p = Path(path)
    if p.exists():
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            _log(f"已加载图谱：{p} ({len(data.get('souls', {}))} 个灵魂)")
            return data
        except (json.JSONDecodeError, IOError) as exc:
            _log(f"警告：读取图谱失败 ({exc})，使用空结构")
    return _empty_tree()


def _save_tree(tree: Dict[str, Any], path: str = DEFAULT_TREE_PATH) -> None:
    """持久化家族图谱到 JSON 文件。"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)
    _log(f"图谱已保存：{p}")


# ---------------------------------------------------------------------------
# 核心 API
# ---------------------------------------------------------------------------

def add_soul(
    name: str,
    slug: str,
    relationship_to: Optional[str] = None,
    rel_type: str = REL_PARENT_CHILD,
    gender: str = "unknown",
    birth_year: Optional[int] = None,
    death_year: Optional[int] = None,
    generation: Optional[int] = None,
    tree_path: str = DEFAULT_TREE_PATH,
) -> Dict[str, Any]:
    """
    添加一个灵魂节点到家族图谱。

    Args:
        name: 显示名称（可中文）
        slug: 唯一标识符（英文，如 grandpa-wang）
        relationship_to: 与哪个已有灵魂关联（slug）
        rel_type: 关系类型 (parent-child / spouse / sibling)
        gender: male / female / unknown
        birth_year: 出生年份
        death_year: 去世年份（None 表示在世）
        generation: 代际编号（0 = 最早祖先，自动推算）
        tree_path: 图谱文件路径

    Returns:
        新增灵魂的节点数据
    """
    if rel_type not in VALID_REL_TYPES:
        raise ValueError(f"无效关系类型 '{rel_type}'，可选：{VALID_REL_TYPES}")

    tree = _load_tree(tree_path)
    souls = tree["souls"]
    edges = tree["edges"]

    if slug in souls:
        _log(f"灵魂 '{slug}' 已存在，跳过")
        return souls[slug]

    # 自动推算 generation
    if generation is None:
        if relationship_to and relationship_to in souls:
            ref_gen = souls[relationship_to].get("generation", 0)
            if rel_type == REL_PARENT_CHILD:
                # relationship_to 是父母 → 新节点是子女
                generation = ref_gen + 1
            elif rel_type == REL_SPOUSE:
                generation = ref_gen
            elif rel_type == REL_SIBLING:
                generation = ref_gen
        else:
            generation = 0  # 根节点

    soul_node = {
        "slug": slug,
        "name": name,
        "gender": gender,
        "birth_year": birth_year,
        "death_year": death_year,
        "generation": generation,
    }
    souls[slug] = soul_node

    # 添加关系边
    if relationship_to and relationship_to in souls:
        edge = {
            "from": relationship_to,
            "to": slug,
            "type": rel_type,
        }
        edges.append(edge)
        # 配偶和兄弟关系是双向的
        if rel_type in (REL_SPOUSE, REL_SIBLING):
            edges.append({
                "from": slug,
                "to": relationship_to,
                "type": rel_type,
            })

    _save_tree(tree, tree_path)
    _log(f"已添加灵魂：{name} ({slug})，第 {generation} 代")
    return soul_node


def get_tree(tree_path: str = DEFAULT_TREE_PATH) -> str:
    """
    返回家族图谱的格式化文本展示。

    按代际分组，显示每个灵魂及其关系。
    """
    tree = _load_tree(tree_path)
    souls = tree["souls"]
    edges = tree["edges"]

    if not souls:
        return f"{PREFIX} 图谱为空，请先添加灵魂。"

    # 按代际分组
    generations: Dict[int, List[Dict]] = {}
    for soul in souls.values():
        gen = soul.get("generation", 0)
        generations.setdefault(gen, []).append(soul)

    # 构建邻接表用于显示关系
    adj: Dict[str, List[Tuple[str, str]]] = {}
    for e in edges:
        adj.setdefault(e["from"], []).append((e["to"], e["type"]))

    lines = ["=" * 50, "        家 族 图 谱", "=" * 50, ""]

    for gen_num in sorted(generations.keys()):
        members = generations[gen_num]
        lines.append(f"--- 第 {gen_num} 代 ---")
        for s in members:
            life = ""
            if s.get("birth_year"):
                life = f" ({s['birth_year']}"
                if s.get("death_year"):
                    life += f"-{s['death_year']})"
                else:
                    life += "-)"
            gender_icon = {"male": "[男]", "female": "[女]"}.get(s.get("gender", ""), "")
            lines.append(f"  {s['name']} ({s['slug']}) {gender_icon}{life}")

            # 显示此灵魂的关系
            for target_slug, rtype in adj.get(s["slug"], []):
                target = souls.get(target_slug, {})
                rtype_cn = {
                    REL_PARENT_CHILD: "→ 子女",
                    REL_SPOUSE: "♥ 配偶",
                    REL_SIBLING: "~ 兄弟姐妹",
                }.get(rtype, rtype)
                lines.append(f"    {rtype_cn}: {target.get('name', target_slug)}")
        lines.append("")

    lines.append(f"共 {len(souls)} 个灵魂，{len(edges)} 条关系")
    return "\n".join(lines)


def _build_undirected_adj(tree: Dict) -> Dict[str, List[Tuple[str, str]]]:
    """构建无向邻接表（用于路径搜索）。"""
    adj: Dict[str, List[Tuple[str, str]]] = {}
    for e in tree["edges"]:
        adj.setdefault(e["from"], []).append((e["to"], e["type"]))
        if e["type"] == REL_PARENT_CHILD:
            # 反向：子女 → 父母
            adj.setdefault(e["to"], []).append((e["from"], "child-parent"))
    return adj


def get_relationship(
    slug_a: str,
    slug_b: str,
    tree_path: str = DEFAULT_TREE_PATH,
) -> str:
    """
    推算两个灵魂之间的关系并用自然语言描述。

    使用 BFS 在无向家族图中找到最短路径，然后根据路径中的边类型
    和代际差推算出中文称谓。
    """
    tree = _load_tree(tree_path)
    souls = tree["souls"]

    if slug_a not in souls:
        return f"找不到灵魂：{slug_a}"
    if slug_b not in souls:
        return f"找不到灵魂：{slug_b}"
    if slug_a == slug_b:
        return f"{souls[slug_a]['name']} 就是自己。"

    adj = _build_undirected_adj(tree)

    # BFS 找最短路径
    visited = {slug_a}
    queue: deque = deque()
    queue.append((slug_a, [(slug_a, None)]))

    found_path: Optional[List[Tuple[str, Optional[str]]]] = None
    while queue:
        current, path = queue.popleft()
        for neighbor, rtype in adj.get(current, []):
            if neighbor not in visited:
                new_path = path + [(neighbor, rtype)]
                if neighbor == slug_b:
                    found_path = new_path
                    break
                visited.add(neighbor)
                queue.append((neighbor, new_path))
        if found_path:
            break

    if not found_path:
        return f"{souls[slug_a]['name']} 与 {souls[slug_b]['name']} 之间没有找到关系路径。"

    name_a = souls[slug_a]["name"]
    name_b = souls[slug_b]["name"]
    gen_a = souls[slug_a].get("generation", 0)
    gen_b = souls[slug_b].get("generation", 0)
    gen_diff = gen_b - gen_a  # positive = B is younger generation

    distance = len(found_path) - 1

    # 尝试用代际差给出称谓
    gender_b = souls[slug_b].get("gender", "unknown")
    title_key = (gen_diff, gender_b)
    title = _PATERNAL_TITLES.get(title_key)

    if title:
        return f"{name_a} 的{title}是 {name_b}（关系距离：{distance}步）"

    # 同代关系
    rel_types_in_path = [r for _, r in found_path if r]
    if gen_diff == 0 and REL_SPOUSE in rel_types_in_path:
        return f"{name_a} 与 {name_b} 是配偶关系"
    if gen_diff == 0 and REL_SIBLING in rel_types_in_path:
        return f"{name_a} 与 {name_b} 是兄弟姐妹关系"

    direction = "长辈" if gen_diff < 0 else "晚辈" if gen_diff > 0 else "同辈"
    return (
        f"{name_a} 与 {name_b} 的关系：{direction}，"
        f"代际差 {abs(gen_diff)} 代，关系距离 {distance} 步"
    )


def get_generation(slug: str, tree_path: str = DEFAULT_TREE_PATH) -> Optional[int]:
    """返回某个灵魂的代际编号。"""
    tree = _load_tree(tree_path)
    soul = tree["souls"].get(slug)
    if soul is None:
        _log(f"找不到灵魂：{slug}")
        return None
    return soul.get("generation", 0)


def get_lineage(slug: str, tree_path: str = DEFAULT_TREE_PATH) -> List[Dict]:
    """
    追溯某个灵魂的祖先路径，从自己回溯到最早的祖先。

    Returns:
        从 slug 到根祖先的灵魂列表（包含自己）
    """
    tree = _load_tree(tree_path)
    souls = tree["souls"]

    if slug not in souls:
        _log(f"找不到灵魂：{slug}")
        return []

    # 构建子→父映射（只看 parent-child 类型的边）
    child_to_parents: Dict[str, List[str]] = {}
    for e in tree["edges"]:
        if e["type"] == REL_PARENT_CHILD:
            child_to_parents.setdefault(e["to"], []).append(e["from"])

    lineage = [souls[slug]]
    current = slug
    visited = {current}

    while current in child_to_parents:
        parents = child_to_parents[current]
        # 选第一个父母（优先 generation 更小的）
        parent = None
        for p in parents:
            if p not in visited and p in souls:
                parent = p
                break
        if parent is None:
            break
        visited.add(parent)
        lineage.append(souls[parent])
        current = parent

    return lineage


def find_common_ancestors(
    slug_a: str,
    slug_b: str,
    tree_path: str = DEFAULT_TREE_PATH,
) -> List[Dict]:
    """找到两个灵魂的共同祖先。"""
    lineage_a = {s["slug"] for s in get_lineage(slug_a, tree_path)}
    lineage_b_list = get_lineage(slug_b, tree_path)

    common = [s for s in lineage_b_list if s["slug"] in lineage_a]
    return common


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="家族图谱引擎")
    parser.add_argument("--action", required=True,
                        choices=["add", "show", "relationship", "lineage", "generation", "ancestors"],
                        help="操作类型")
    parser.add_argument("--name", help="灵魂名称")
    parser.add_argument("--slug", help="灵魂标识符")
    parser.add_argument("--relationship-to", help="关联灵魂 slug")
    parser.add_argument("--rel-type", default=REL_PARENT_CHILD,
                        help=f"关系类型: {VALID_REL_TYPES}")
    parser.add_argument("--gender", default="unknown", help="性别: male/female/unknown")
    parser.add_argument("--birth-year", type=int, help="出生年份")
    parser.add_argument("--death-year", type=int, help="去世年份")
    parser.add_argument("--generation", type=int, help="代际编号（通常自动推算）")
    parser.add_argument("--slug-a", help="关系查询：灵魂 A")
    parser.add_argument("--slug-b", help="关系查询：灵魂 B")
    parser.add_argument("--tree-path", default=DEFAULT_TREE_PATH, help="图谱文件路径")

    args = parser.parse_args()

    if args.action == "add":
        if not args.name or not args.slug:
            parser.error("添加灵魂需要 --name 和 --slug")
        result = add_soul(
            name=args.name,
            slug=args.slug,
            relationship_to=args.relationship_to,
            rel_type=args.rel_type,
            gender=args.gender,
            birth_year=args.birth_year,
            death_year=args.death_year,
            generation=args.generation,
            tree_path=args.tree_path,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "show":
        print(get_tree(args.tree_path))

    elif args.action == "relationship":
        if not args.slug_a or not args.slug_b:
            parser.error("关系查询需要 --slug-a 和 --slug-b")
        print(get_relationship(args.slug_a, args.slug_b, args.tree_path))

    elif args.action == "lineage":
        if not args.slug:
            parser.error("世系查询需要 --slug")
        lineage = get_lineage(args.slug, args.tree_path)
        if lineage:
            print("世系追溯（从自己到祖先）：")
            for i, s in enumerate(lineage):
                indent = "  " * i
                print(f"{indent}└─ {s['name']} ({s['slug']})，第 {s.get('generation', '?')} 代")
        else:
            print("未找到世系信息。")

    elif args.action == "generation":
        if not args.slug:
            parser.error("代际查询需要 --slug")
        gen = get_generation(args.slug, args.tree_path)
        if gen is not None:
            print(f"{args.slug} 属于第 {gen} 代")

    elif args.action == "ancestors":
        if not args.slug_a or not args.slug_b:
            parser.error("共同祖先查询需要 --slug-a 和 --slug-b")
        ancestors = find_common_ancestors(args.slug_a, args.slug_b, args.tree_path)
        if ancestors:
            print("共同祖先：")
            for a in ancestors:
                print(f"  - {a['name']} ({a['slug']})，第 {a.get('generation', '?')} 代")
        else:
            print("未找到共同祖先。")


if __name__ == "__main__":
    main()
