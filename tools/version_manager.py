#!/usr/bin/env python3
"""
灵魂档案版本管理工具

功能:
  - archive  — 将当前状态保存为新版本 versions/v{N}/
  - list     — 显示所有版本及其时间戳
  - rollback — 回滚到指定版本 (安全: 先保存当前状态到 before_rollback)
  - cleanup  — 清理超过 MAX_VERSIONS 的旧版本

用法:
  python version_manager.py --slug <slug> --action <archive|list|rollback|cleanup> [--version <vN>]
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

PANTHEON_HOME = os.path.expanduser("~/.pantheon")
SOULS_DIR = os.path.join(PANTHEON_HOME, "souls")
MAX_VERSIONS = 10

# 需要版本管理的文件
VERSIONED_FILES = ["memory.md", "soul.md", "meta.json", "SKILL.md"]


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def get_soul_dir(slug: str, base_dir: str = SOULS_DIR) -> str:
    """获取灵魂目录路径"""
    return os.path.join(base_dir, slug)


def get_versions_dir(soul_dir: str) -> str:
    """获取版本目录路径"""
    return os.path.join(soul_dir, "versions")


def load_meta(soul_dir: str) -> dict[str, Any]:
    """加载 meta.json"""
    meta_path = os.path.join(soul_dir, "meta.json")
    if os.path.isfile(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_meta(soul_dir: str, meta: dict[str, Any]) -> None:
    """保存 meta.json"""
    meta_path = os.path.join(soul_dir, "meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def get_existing_versions(versions_dir: str) -> list[str]:
    """获取已存在的版本列表，按版本号排序"""
    if not os.path.isdir(versions_dir):
        return []
    versions = []
    for d in os.listdir(versions_dir):
        if d.startswith("v") and os.path.isdir(os.path.join(versions_dir, d)):
            try:
                int(d[1:])
                versions.append(d)
            except ValueError:
                continue
    versions.sort(key=lambda v: int(v[1:]))
    return versions


def get_next_version_number(versions_dir: str) -> int:
    """获取下一个版本号"""
    existing = get_existing_versions(versions_dir)
    if not existing:
        return 1
    return max(int(v[1:]) for v in existing) + 1


def copy_soul_files(src_dir: str, dst_dir: str) -> list[str]:
    """复制灵魂文件到目标目录"""
    os.makedirs(dst_dir, exist_ok=True)
    copied = []
    for fname in VERSIONED_FILES:
        src = os.path.join(src_dir, fname)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(dst_dir, fname))
            copied.append(fname)
    return copied


# ---------------------------------------------------------------------------
# 操作: archive
# ---------------------------------------------------------------------------

def action_archive(soul_dir: str) -> None:
    """将当前状态保存为新版本"""
    versions_dir = get_versions_dir(soul_dir)
    os.makedirs(versions_dir, exist_ok=True)

    version_num = get_next_version_number(versions_dir)
    version_name = f"v{version_num}"
    version_path = os.path.join(versions_dir, version_name)

    print(f"[version_manager] 创建版本 {version_name}...")

    copied = copy_soul_files(soul_dir, version_path)
    if not copied:
        print("[version_manager] 警告: 没有找到可归档的文件")
        return

    # 写入版本元信息
    version_meta = {
        "version": version_name,
        "created_at": datetime.now().isoformat(),
        "files": copied,
    }
    with open(os.path.join(version_path, "_version.json"), "w", encoding="utf-8") as f:
        json.dump(version_meta, f, ensure_ascii=False, indent=2)

    # 更新 meta.json
    meta = load_meta(soul_dir)
    meta["version"] = version_num
    meta["updated_at"] = datetime.now().isoformat()
    save_meta(soul_dir, meta)

    print(f"[version_manager] 版本 {version_name} 创建成功")
    print(f"  路径: {version_path}")
    print(f"  文件: {', '.join(copied)}")


# ---------------------------------------------------------------------------
# 操作: list
# ---------------------------------------------------------------------------

def action_list(soul_dir: str) -> None:
    """列出所有版本"""
    versions_dir = get_versions_dir(soul_dir)
    versions = get_existing_versions(versions_dir)

    if not versions:
        print("[version_manager] 没有找到任何版本")
        return

    print(f"[version_manager] 共 {len(versions)} 个版本:\n")
    print(f"{'版本':<10} {'创建时间':<24} {'文件数':<8}")
    print("-" * 44)

    for v in versions:
        v_path = os.path.join(versions_dir, v)
        v_meta_path = os.path.join(v_path, "_version.json")

        created_at = "未知"
        file_count = 0

        if os.path.isfile(v_meta_path):
            with open(v_meta_path, "r", encoding="utf-8") as f:
                try:
                    v_meta = json.load(f)
                    created_at = v_meta.get("created_at", "未知")
                    file_count = len(v_meta.get("files", []))
                except json.JSONDecodeError:
                    pass
        else:
            # 从目录修改时间推断
            try:
                mtime = os.path.getmtime(v_path)
                created_at = datetime.fromtimestamp(mtime).isoformat()
            except OSError:
                pass
            file_count = len([
                f for f in os.listdir(v_path)
                if f in VERSIONED_FILES
            ])

        # 截断时间显示
        if len(created_at) > 22:
            created_at = created_at[:22]

        print(f"{v:<10} {created_at:<24} {file_count} 个文件")

    # 显示当前版本
    meta = load_meta(soul_dir)
    current = meta.get("version", "未知")
    print(f"\n当前版本: v{current}" if isinstance(current, int) else f"\n当前版本: {current}")


# ---------------------------------------------------------------------------
# 操作: rollback
# ---------------------------------------------------------------------------

def action_rollback(soul_dir: str, target_version: str) -> None:
    """回滚到指定版本"""
    versions_dir = get_versions_dir(soul_dir)

    # 验证目标版本
    if not target_version.startswith("v"):
        target_version = f"v{target_version}"

    target_path = os.path.join(versions_dir, target_version)
    if not os.path.isdir(target_path):
        print(f"[version_manager] 错误: 版本 {target_version} 不存在", file=sys.stderr)
        existing = get_existing_versions(versions_dir)
        if existing:
            print(f"  可用版本: {', '.join(existing)}")
        sys.exit(1)

    # 安全: 先保存当前状态
    print("[version_manager] 安全备份: 保存当前状态到 before_rollback...")
    backup_path = os.path.join(versions_dir, "before_rollback")
    if os.path.isdir(backup_path):
        # 已有备份则加时间戳
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(versions_dir, f"before_rollback_{ts}")
    copied = copy_soul_files(soul_dir, backup_path)
    if copied:
        # 记录备份元信息
        backup_meta = {
            "version": "before_rollback",
            "created_at": datetime.now().isoformat(),
            "files": copied,
            "reason": f"rollback to {target_version}",
        }
        with open(os.path.join(backup_path, "_version.json"), "w", encoding="utf-8") as f:
            json.dump(backup_meta, f, ensure_ascii=False, indent=2)
        print(f"  已保存到 {backup_path}")

    # 执行回滚: 从目标版本复制文件回来
    print(f"[version_manager] 回滚到 {target_version}...")
    restored = []
    for fname in VERSIONED_FILES:
        src = os.path.join(target_path, fname)
        dst = os.path.join(soul_dir, fname)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            restored.append(fname)

    # 更新 meta.json 的回滚记录
    meta = load_meta(soul_dir)
    rollback_record = {
        "from_version": meta.get("version"),
        "to_version": target_version,
        "timestamp": datetime.now().isoformat(),
        "backup": backup_path,
    }
    if "rollback_history" not in meta:
        meta["rollback_history"] = []
    meta["rollback_history"].append(rollback_record)
    meta["updated_at"] = datetime.now().isoformat()
    try:
        meta["version"] = int(target_version[1:])
    except ValueError:
        meta["version"] = target_version
    save_meta(soul_dir, meta)

    print(f"[version_manager] 回滚完成!")
    print(f"  恢复文件: {', '.join(restored)}")
    print(f"  备份位置: {backup_path}")


# ---------------------------------------------------------------------------
# 操作: cleanup
# ---------------------------------------------------------------------------

def action_cleanup(soul_dir: str) -> None:
    """清理超过 MAX_VERSIONS 的旧版本"""
    versions_dir = get_versions_dir(soul_dir)
    versions = get_existing_versions(versions_dir)

    # 不计入 before_rollback 目录
    if len(versions) <= MAX_VERSIONS:
        print(f"[version_manager] 当前 {len(versions)} 个版本，未超过上限 {MAX_VERSIONS}，无需清理")
        return

    to_remove = versions[:len(versions) - MAX_VERSIONS]
    print(f"[version_manager] 当前 {len(versions)} 个版本，将清理 {len(to_remove)} 个旧版本...")

    for v in to_remove:
        v_path = os.path.join(versions_dir, v)
        try:
            shutil.rmtree(v_path)
            print(f"  已删除 {v}")
        except OSError as e:
            print(f"  删除 {v} 失败: {e}", file=sys.stderr)

    remaining = get_existing_versions(versions_dir)
    print(f"[version_manager] 清理完成，剩余 {len(remaining)} 个版本")

    # 也清理旧的 before_rollback 目录 (保留最新一个)
    rollback_dirs = sorted([
        d for d in os.listdir(versions_dir)
        if d.startswith("before_rollback") and os.path.isdir(os.path.join(versions_dir, d))
    ])
    if len(rollback_dirs) > 1:
        for d in rollback_dirs[:-1]:
            d_path = os.path.join(versions_dir, d)
            try:
                shutil.rmtree(d_path)
                print(f"  已删除旧备份 {d}")
            except OSError:
                pass


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="灵魂档案版本管理工具 — 归档、列表、回滚、清理"
    )
    parser.add_argument("--slug", required=True, help="灵魂标识符")
    parser.add_argument(
        "--action",
        required=True,
        choices=["archive", "list", "rollback", "cleanup"],
        help="操作类型",
    )
    parser.add_argument("--version", help="目标版本 (用于 rollback，如 v3)")
    parser.add_argument("--base-dir", default=SOULS_DIR, help=f"灵魂存储基础目录 (默认: {SOULS_DIR})")
    args = parser.parse_args()

    soul_dir = get_soul_dir(args.slug, args.base_dir)

    if not os.path.isdir(soul_dir):
        print(f"[version_manager] 错误: 灵魂目录不存在 — {soul_dir}", file=sys.stderr)
        print(f"  请先使用 skill_writer.py 创建灵魂档案")
        sys.exit(1)

    print(f"[version_manager] 灵魂: {args.slug} ({soul_dir})")
    print(f"[version_manager] 操作: {args.action}")

    if args.action == "archive":
        action_archive(soul_dir)
    elif args.action == "list":
        action_list(soul_dir)
    elif args.action == "rollback":
        if not args.version:
            print("[version_manager] 错误: rollback 需要 --version 参数", file=sys.stderr)
            sys.exit(1)
        action_rollback(soul_dir, args.version)
    elif args.action == "cleanup":
        action_cleanup(soul_dir)


if __name__ == "__main__":
    main()
