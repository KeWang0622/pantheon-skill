#!/usr/bin/env python3
"""
照片元数据分析工具 — 构建记忆时间线

功能:
  - 提取 EXIF 数据: 拍摄日期、GPS 位置
  - 按日期/位置将照片分组为"事件"
  - 输出时间线 JSON

依赖: Pillow (可选，优雅降级到标准库)

用法:
  python photo_analyzer.py --input-dir <dir> --output <output.json>
"""

import argparse
import json
import os
import struct
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# 支持的图片扩展名
IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".heic", ".heif",
    ".webp", ".bmp", ".gif",
}

# 事件分组阈值: 同一天且距离 < 阈值(km) 归为同一事件
EVENT_TIME_GAP_HOURS = 4
EVENT_DISTANCE_KM = 5.0


# ---------------------------------------------------------------------------
# EXIF 读取 — 优先使用 Pillow，否则回退到基础解析
# ---------------------------------------------------------------------------

def _try_pillow_exif(filepath: str) -> dict[str, Any] | None:
    """使用 Pillow 读取 EXIF 数据"""
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS, GPSTAGS
    except ImportError:
        return None

    try:
        img = Image.open(filepath)
        exif_data = img._getexif()
        if not exif_data:
            return {}
    except Exception:
        return {}

    result: dict[str, Any] = {}

    for tag_id, value in exif_data.items():
        tag_name = TAGS.get(tag_id, str(tag_id))

        if tag_name == "DateTimeOriginal":
            result["datetime_original"] = str(value)
        elif tag_name == "DateTime":
            if "datetime_original" not in result:
                result["datetime_original"] = str(value)
        elif tag_name == "GPSInfo":
            gps = {}
            for gps_tag_id, gps_value in value.items():
                gps_tag_name = GPSTAGS.get(gps_tag_id, str(gps_tag_id))
                gps[gps_tag_name] = gps_value
            result["gps_info"] = gps

    return result


def _parse_exif_date(date_str: str) -> datetime | None:
    """解析 EXIF 日期字符串"""
    formats = [
        "%Y:%m:%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y:%m:%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


def _gps_to_decimal(gps_info: dict) -> tuple[float, float] | None:
    """将 GPS EXIF 数据转换为十进制经纬度"""
    try:
        lat_data = gps_info.get("GPSLatitude")
        lat_ref = gps_info.get("GPSLatitudeRef", "N")
        lon_data = gps_info.get("GPSLongitude")
        lon_ref = gps_info.get("GPSLongitudeRef", "E")

        if not lat_data or not lon_data:
            return None

        def to_degrees(values):
            """转换 (度, 分, 秒) 到十进制"""
            d = float(values[0])
            m = float(values[1])
            s = float(values[2])
            return d + m / 60.0 + s / 3600.0

        lat = to_degrees(lat_data)
        lon = to_degrees(lon_data)

        if lat_ref == "S":
            lat = -lat
        if lon_ref == "W":
            lon = -lon

        return (round(lat, 6), round(lon, 6))
    except (TypeError, ValueError, IndexError, KeyError):
        return None


def _fallback_date_from_filename(filepath: str) -> datetime | None:
    """从文件名尝试提取日期 (常见命名: IMG_20230115_143022.jpg)"""
    name = Path(filepath).stem
    patterns = [
        r"(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})",
        r"(\d{4})-(\d{2})-(\d{2})[ _](\d{2})-(\d{2})-(\d{2})",
        r"(\d{4})(\d{2})(\d{2})",
    ]
    import re
    for pat in patterns:
        m = re.search(pat, name)
        if m:
            groups = m.groups()
            try:
                if len(groups) >= 6:
                    return datetime(
                        int(groups[0]), int(groups[1]), int(groups[2]),
                        int(groups[3]), int(groups[4]), int(groups[5]),
                    )
                else:
                    return datetime(int(groups[0]), int(groups[1]), int(groups[2]))
            except ValueError:
                continue
    return None


def extract_photo_metadata(filepath: str) -> dict[str, Any]:
    """提取单张照片的元数据"""
    meta: dict[str, Any] = {
        "file": filepath,
        "filename": os.path.basename(filepath),
    }

    # 尝试 Pillow
    exif = _try_pillow_exif(filepath)

    date_taken = None
    gps_coords = None

    if exif is not None:
        # 日期
        if "datetime_original" in exif:
            date_taken = _parse_exif_date(exif["datetime_original"])
        # GPS
        if "gps_info" in exif:
            gps_coords = _gps_to_decimal(exif["gps_info"])
    else:
        # Pillow 不可用 — 仅从文件名和修改时间推断
        pass

    # 回退: 文件名
    if not date_taken:
        date_taken = _fallback_date_from_filename(filepath)

    # 回退: 文件修改时间
    if not date_taken:
        try:
            mtime = os.path.getmtime(filepath)
            date_taken = datetime.fromtimestamp(mtime)
            meta["date_source"] = "file_mtime"
        except OSError:
            pass
    else:
        meta["date_source"] = "exif" if (exif and "datetime_original" in exif) else "filename"

    if date_taken:
        meta["date"] = date_taken.strftime("%Y-%m-%d")
        meta["datetime"] = date_taken.isoformat()
    if gps_coords:
        meta["latitude"] = gps_coords[0]
        meta["longitude"] = gps_coords[1]

    return meta


# ---------------------------------------------------------------------------
# 事件分组
# ---------------------------------------------------------------------------

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """计算两点间的大圆距离 (km)"""
    import math
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def group_into_events(photos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """将照片按时间和位置分组为事件"""
    if not photos:
        return []

    # 按日期排序
    dated = [p for p in photos if p.get("datetime")]
    undated = [p for p in photos if not p.get("datetime")]

    dated.sort(key=lambda p: p["datetime"])

    events: list[dict[str, Any]] = []
    current_event: list[dict[str, Any]] = []

    for photo in dated:
        if not current_event:
            current_event.append(photo)
            continue

        last = current_event[-1]
        last_dt = datetime.fromisoformat(last["datetime"])
        curr_dt = datetime.fromisoformat(photo["datetime"])
        time_gap = (curr_dt - last_dt).total_seconds() / 3600

        # 检查位置距离
        close_location = True
        if (
            "latitude" in photo and "latitude" in last
            and photo["latitude"] and last["latitude"]
        ):
            dist = haversine_km(
                last["latitude"], last["longitude"],
                photo["latitude"], photo["longitude"],
            )
            if dist > EVENT_DISTANCE_KM:
                close_location = False

        if time_gap <= EVENT_TIME_GAP_HOURS and close_location:
            current_event.append(photo)
        else:
            events.append(_summarize_event(current_event))
            current_event = [photo]

    if current_event:
        events.append(_summarize_event(current_event))

    # 未定日期的照片归为一个特殊事件
    if undated:
        events.append({
            "event_id": f"undated",
            "date": None,
            "date_range": None,
            "location": None,
            "photo_count": len(undated),
            "photos": [p["filename"] for p in undated],
        })

    return events


def _summarize_event(photos: list[dict[str, Any]]) -> dict[str, Any]:
    """生成事件摘要"""
    dates = sorted([p["date"] for p in photos if p.get("date")])
    lats = [p["latitude"] for p in photos if p.get("latitude")]
    lons = [p["longitude"] for p in photos if p.get("longitude")]

    location = None
    if lats and lons:
        location = {
            "latitude": round(sum(lats) / len(lats), 6),
            "longitude": round(sum(lons) / len(lons), 6),
        }

    date_start = dates[0] if dates else None
    date_end = dates[-1] if dates else None

    return {
        "event_id": f"{date_start}_{len(photos)}",
        "date": date_start,
        "date_range": {
            "start": date_start,
            "end": date_end,
        } if date_start != date_end else {"start": date_start, "end": date_start},
        "location": location,
        "photo_count": len(photos),
        "photos": [p["filename"] for p in photos],
    }


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def scan_photos(input_dir: str) -> list[str]:
    """递归扫描目录下的所有图片文件"""
    photos = []
    for root, dirs, files in os.walk(input_dir):
        # 跳过隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if Path(f).suffix.lower() in IMAGE_EXTENSIONS:
                photos.append(os.path.join(root, f))
    return sorted(photos)


def main():
    parser = argparse.ArgumentParser(
        description="照片元数据分析工具 — 从照片 EXIF 构建记忆时间线"
    )
    parser.add_argument("--input-dir", required=True, help="照片目录路径")
    parser.add_argument("--output", required=True, help="输出 JSON 文件路径")
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"[photo_analyzer] 错误: 目录不存在 — {args.input_dir}", file=sys.stderr)
        sys.exit(1)

    # 扫描照片
    print(f"[photo_analyzer] 扫描目录: {args.input_dir}")
    photo_files = scan_photos(args.input_dir)
    print(f"[photo_analyzer] 找到 {len(photo_files)} 张图片")

    if not photo_files:
        print("[photo_analyzer] 没有找到任何图片文件")
        result = {"events": [], "stats": {"total_photos": 0, "total_events": 0}}
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        return

    # 提取元数据
    print("[photo_analyzer] 提取 EXIF 元数据...")
    all_meta: list[dict[str, Any]] = []
    exif_count = 0
    gps_count = 0
    errors = 0

    for i, fpath in enumerate(photo_files, 1):
        if i % 50 == 0 or i == len(photo_files):
            print(f"[photo_analyzer] 进度: {i}/{len(photo_files)}")
        try:
            meta = extract_photo_metadata(fpath)
            all_meta.append(meta)
            if meta.get("date_source") == "exif":
                exif_count += 1
            if meta.get("latitude"):
                gps_count += 1
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"[photo_analyzer] 警告: 无法读取 {fpath}: {e}")

    # 分组
    print("[photo_analyzer] 按日期/位置分组为事件...")
    events = group_into_events(all_meta)

    # 统计
    dates = sorted([m["date"] for m in all_meta if m.get("date")])
    stats = {
        "total_photos": len(all_meta),
        "total_events": len(events),
        "photos_with_exif_date": exif_count,
        "photos_with_gps": gps_count,
        "parse_errors": errors,
        "date_range": {
            "earliest": dates[0] if dates else None,
            "latest": dates[-1] if dates else None,
        },
    }

    result = {
        "stats": stats,
        "events": events,
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[photo_analyzer] 分析完成:")
    print(f"  照片总数: {stats['total_photos']}")
    print(f"  事件数量: {stats['total_events']}")
    print(f"  有 EXIF 日期: {exif_count}")
    print(f"  有 GPS 数据: {gps_count}")
    if dates:
        print(f"  时间跨度: {dates[0]} ~ {dates[-1]}")
    print(f"[photo_analyzer] 结果已写入 {args.output}")


if __name__ == "__main__":
    main()
