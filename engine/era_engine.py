#!/usr/bin/env python3
"""
era_engine.py - 时代语言与文化适配引擎

让每一代人说出属于他们那个时代的话。1940年代出生的爷爷和80年代出生的叔叔，
他们的用词、语气、文化参照完全不同。这个引擎捕捉那些时代烙印。

核心理念：一个人的语言不只是个性，更是时代的投影。
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Optional

PREFIX = "[era_engine]"

# ---------------------------------------------------------------------------
# 时代档案数据库
# ---------------------------------------------------------------------------

ERA_PROFILES: Dict[str, Dict[str, Any]] = {
    "1930s": {
        "era_name": "民国/战争年代",
        "birth_range": "1930-1939",
        "historical_context": "出生于民国末期或抗战时期，童年在战火中度过",
        "vocabulary": [
            "吃苦", "熬过来", "那个年代", "打仗的时候", "逃难",
            "有口饭吃就不错了", "旧社会", "解放前", "当年",
            "莫说", "自然是", "想当年", "不容易啊",
        ],
        "grammar_patterns": [
            "倒装句较多：「苦啊，那时候。」",
            "省略主语：「挨过饿的人才知道。」",
            "感叹式回忆：「那会儿哪有这个条件！」",
        ],
        "cultural_references": [
            "抗日战争", "解放战争", "走西口", "逃荒",
            "大户人家", "地主", "长工", "私塾",
        ],
        "taboo_topics": [
            "对政治变迁极为敏感",
            "不轻易谈论失去的家产或社会地位变化",
        ],
        "communication_norms": {
            "directness": "间接，常用比喻和故事",
            "emotional_expression": "含蓄，苦难轻描淡写",
            "authority_style": "严父慈母传统，长幼有序",
            "typical_sentence_enders": ["啊", "呢", "罢了", "也就是了"],
        },
        "speech_markers": [
            "我跟你说啊", "想当年", "你们这代人不懂",
            "那时候哪有", "苦是苦，但是",
        ],
    },
    "1940s": {
        "era_name": "战后/建国前后",
        "birth_range": "1940-1949",
        "historical_context": "在新旧交替中成长，经历了从民国到新中国的巨变",
        "vocabulary": [
            "解放", "翻身", "新社会", "旧社会", "运动",
            "改造", "成分", "组织", "觉悟", "进步",
            "有觉悟", "过去", "那阵子",
        ],
        "grammar_patterns": [
            "叙事从容：「那时候我们……」",
            "对比句式：「旧社会……新社会……」",
            "习惯性总结：「这就是命啊。」",
        ],
        "cultural_references": [
            "土改", "建国大典", "抗美援朝", "合作社",
            "扫盲运动", "《白毛女》", "《南征北战》",
        ],
        "taboo_topics": [
            "家庭成分问题",
            "运动中受到的影响",
        ],
        "communication_norms": {
            "directness": "较间接，讲究措辞",
            "emotional_expression": "隐忍，不轻易流露",
            "authority_style": "家长制，但开始有新思想",
            "typical_sentence_enders": ["嘛", "啊", "了", "吧"],
        },
        "speech_markers": [
            "我年轻的时候", "那个年代", "说起来",
            "你听我讲", "这个事情是这样的",
        ],
    },
    "1950s": {
        "era_name": "建国一代",
        "birth_range": "1950-1959",
        "historical_context": "生在红旗下，集体主义教育，经历大跃进",
        "vocabulary": [
            "同志", "为人民服务", "组织", "集体", "革命",
            "先进", "落后", "批评与自我批评", "积极分子",
            "大锅饭", "铁饭碗", "单位", "领导",
        ],
        "grammar_patterns": [
            "排比句：「要学习……要进步……要为人民……」",
            "口号式表达：「团结就是力量！」",
            "汇报式叙事：「在组织的关怀下……」",
        ],
        "cultural_references": [
            "大跃进", "人民公社", "雷锋", "铁人王进喜",
            "苏联老大哥", "《东方红》", "广播体操",
            "「好好学习天天向上」",
        ],
        "taboo_topics": [
            "对三年困难时期避而不谈或淡化",
            "政治立场敏感",
        ],
        "communication_norms": {
            "directness": "直接但用政治化语言包装",
            "emotional_expression": "集体化，个人情感让位于集体",
            "authority_style": "崇尚组织、领导、集体决策",
            "typical_sentence_enders": ["嘛", "么", "呗", "的"],
        },
        "speech_markers": [
            "我们那个年代", "单位里", "组织上",
            "凭良心讲", "实事求是地说",
        ],
    },
    "1960s": {
        "era_name": "三年困难+文革一代",
        "birth_range": "1960-1969",
        "historical_context": "童年经历困难时期，青少年时期正逢文革",
        "vocabulary": [
            "上山下乡", "知青", "插队", "回城", "拨乱反正",
            "恢复高考", "铁饭碗", "下海", "万元户",
            "伤痕", "反思", "那十年",
        ],
        "grammar_patterns": [
            "欲言又止：「那时候……算了不说了。」",
            "反讽式幽默：「我们上过山下过乡，什么没见过。」",
            "比较级：「比起以前，现在好多了。」",
        ],
        "cultural_references": [
            "文化大革命", "知青下乡", "恢复高考",
            "邓丽君", "《伤痕》", "朦胧诗",
            "改革开放", "77/78级", "万元户",
        ],
        "taboo_topics": [
            "文革中的个人经历（除非主动提起）",
            "曾经的政治表态",
            "失去的受教育机会",
        ],
        "communication_norms": {
            "directness": "谨慎，善于察言观色",
            "emotional_expression": "压抑中带坚韧，幽默常含苦涩",
            "authority_style": "有权威感但也有反思",
            "typical_sentence_enders": ["呗", "嘛", "就是了", "算了"],
        },
        "speech_markers": [
            "我们这代人", "当年下乡的时候", "那阵子",
            "说白了", "你不懂", "经历过的人才知道",
        ],
    },
    "1970s": {
        "era_name": "改革开放前夜 / 转型一代",
        "birth_range": "1970-1979",
        "historical_context": "童年在旧体制尾声，青年期迎来市场经济大潮",
        "vocabulary": [
            "下海", "个体户", "南下", "打工", "搞活",
            "市场经济", "承包", "倒爷", "国企改制",
            "下岗", "买断", "自己闯",
        ],
        "grammar_patterns": [
            "务实直白：「日子是自己过出来的。」",
            "经验之谈：「我吃过亏才知道……」",
            "过渡语气：「以前不一样，现在……」",
        ],
        "cultural_references": [
            "改革开放", "深圳速度", "春晚", "港台文化",
            "金庸武侠", "琼瑶", "四大天王", "下海潮",
            "97回归", "《渴望》", "BP机",
        ],
        "taboo_topics": [
            "下岗经历（如果有）",
            "市场化转型中的失落",
        ],
        "communication_norms": {
            "directness": "比上一代更直接，务实",
            "emotional_expression": "开始表达但仍含蓄",
            "authority_style": "讲道理为主，偶尔家长式",
            "typical_sentence_enders": ["吧", "呢", "嘛", "得了"],
        },
        "speech_markers": [
            "我跟你说", "这事儿", "实话实说",
            "凭本事吃饭", "社会就是这样",
        ],
    },
    "1980s": {
        "era_name": "改革开放一代",
        "birth_range": "1980-1989",
        "historical_context": "独生子女政策下成长，经济高速发展，信息爆炸初期",
        "vocabulary": [
            "独生子女", "小皇帝", "高考", "大学扩招",
            "房价", "北漂", "白领", "月光族",
            "QQ", "网吧", "MP3", "选秀",
        ],
        "grammar_patterns": [
            "自嘲式：「我们80后就是这样。」",
            "网络化口语渗透：「确实挺无语的。」",
            "中英混用开始出现",
        ],
        "cultural_references": [
            "春晚小品", "周杰伦", "超级女声", "非诚勿扰",
            "《还珠格格》", "灌篮高手", "哈利波特",
            "QQ", "网吧", "2008奥运", "汶川地震",
        ],
        "taboo_topics": [
            "独生子女养老压力",
            "房贷压力",
        ],
        "communication_norms": {
            "directness": "较直接，敢表达个人观点",
            "emotional_expression": "更开放，但对父母辈仍收敛",
            "authority_style": "倾向平等对话",
            "typical_sentence_enders": ["啊", "呢", "吧", "了"],
        },
        "speech_markers": [
            "我觉得", "说实话", "怎么说呢",
            "其实吧", "讲真",
        ],
    },
    "1990s": {
        "era_name": "互联网一代",
        "birth_range": "1990-1999",
        "historical_context": "完全成长于和平与经济发展时期，互联网原住民",
        "vocabulary": [
            "佛系", "内卷", "躺平", "打工人", "社恐",
            "emo", "破防", "YYDS", "绝绝子",
            "网络冲浪", "刷手机", "外卖",
        ],
        "grammar_patterns": [
            "缩写和梗：「太真实了」「绝了」",
            "反讽自嘲密集",
            "表情包思维（语言碎片化）",
        ],
        "cultural_references": [
            "微信", "抖音", "B站", "双十一",
            "选秀偶像", "漫威", "二次元",
            "移动支付", "共享经济", "996",
        ],
        "taboo_topics": [
            "可能对催婚催育敏感",
            "职业焦虑",
        ],
        "communication_norms": {
            "directness": "直接，习惯网络化表达",
            "emotional_expression": "外放，但真正深层情感可能通过段子表达",
            "authority_style": "反权威，追求平等",
            "typical_sentence_enders": ["了", "啊", "哈", "吧"],
        },
        "speech_markers": [
            "我感觉", "真的假的", "绝了",
            "不是吧", "怎么说", "就挺突然的",
        ],
    },
}


def _log(msg: str) -> None:
    print(f"{PREFIX} {msg}")


# ---------------------------------------------------------------------------
# 核心 API
# ---------------------------------------------------------------------------

def get_era_profile(birth_decade: str) -> Optional[Dict[str, Any]]:
    """
    获取某个出生年代的完整时代档案。

    Args:
        birth_decade: 如 "1960" 或 "1960s"

    Returns:
        时代档案字典，找不到则返回 None
    """
    # 标准化输入
    decade = birth_decade.rstrip("s")
    if len(decade) == 4:
        decade = decade[:3] + "0s"
    elif not decade.endswith("s"):
        decade = decade + "s"
    else:
        decade = birth_decade

    # 尝试精确匹配
    if decade in ERA_PROFILES:
        _log(f"已加载时代档案：{ERA_PROFILES[decade]['era_name']} ({decade})")
        return ERA_PROFILES[decade]

    # 尝试模糊匹配
    for key in ERA_PROFILES:
        if decade[:3] == key[:3]:
            _log(f"已加载时代档案：{ERA_PROFILES[key]['era_name']} ({key})")
            return ERA_PROFILES[key]

    _log(f"未找到 {birth_decade} 对应的时代档案")
    return None


def get_cultural_references(birth_decade: str) -> List[str]:
    """
    获取某个出生年代的文化参照列表。

    这些是那代人共同的记忆坐标——歌曲、电影、事件、口号。
    """
    profile = get_era_profile(birth_decade)
    if profile:
        return profile.get("cultural_references", [])
    return []


def adapt_language(
    text: str,
    birth_decade: str,
    context: str = "general",
) -> str:
    """
    将通用文本调整为符合特定时代语言风格的版本。

    这不是简单的词汇替换，而是模拟那个年代的人说话的方式：
    - 加入时代标志性的语气词
    - 调整表达的直接程度
    - 融入时代特有的参照框架

    Args:
        text: 原始文本
        birth_decade: 出生年代（如 "1960"）
        context: 语境（general / advice / storytelling / scolding / comforting）

    Returns:
        经过时代适配的文本
    """
    profile = get_era_profile(birth_decade)
    if not profile:
        _log(f"无法适配：未找到 {birth_decade} 的时代档案")
        return text

    norms = profile.get("communication_norms", {})
    markers = profile.get("speech_markers", [])
    enders = norms.get("typical_sentence_enders", [])

    result = text

    # 1. 根据语境选择开场白
    context_openers = {
        "advice": {
            "1930s": "我活了这么大岁数，",
            "1940s": "听我一句劝，",
            "1950s": "我跟你说个道理，",
            "1960s": "我们那时候吃过亏的，",
            "1970s": "我跟你说实话，",
            "1980s": "我觉得吧，",
            "1990s": "讲真，",
        },
        "storytelling": {
            "1930s": "想当年啊，",
            "1940s": "说起来那时候，",
            "1950s": "我们那个年代，",
            "1960s": "那阵子，",
            "1970s": "以前吧，",
            "1980s": "说实话，那会儿",
            "1990s": "就是说，之前",
        },
        "comforting": {
            "1930s": "孩子啊，",
            "1940s": "别难过了，",
            "1950s": "有什么困难组织上都能解决，",
            "1960s": "比起以前，这都不算什么，",
            "1970s": "日子会好起来的，",
            "1980s": "其实吧，",
            "1990s": "别emo了，",
        },
        "scolding": {
            "1930s": "你怎么这么不懂事！",
            "1940s": "你给我听好了，",
            "1950s": "你的觉悟呢？",
            "1960s": "你知不知道以前的人多不容易？",
            "1970s": "你自己好好想想，",
            "1980s": "我跟你说啊，",
            "1990s": "不是吧，",
        },
    }

    decade_key = birth_decade.rstrip("s")
    if len(decade_key) == 4:
        decade_key = decade_key[:3] + "0s"

    if context in context_openers and decade_key in context_openers[context]:
        opener = context_openers[context][decade_key]
        # 如果原文没有以开场白开头，加上
        if not any(result.startswith(m) for m in markers):
            result = opener + result

    # 2. 替换过于现代或过于古旧的词汇
    decade_num = int(birth_decade.rstrip("s")[:4])

    if decade_num <= 1959:
        # 老一辈不会用的词 → 替换
        modern_to_old = {
            "手机": "电话",
            "网上": "外面",
            "APP": "东西",
            "OK": "好",
            "没问题": "行",
        }
        for modern, old in modern_to_old.items():
            result = result.replace(modern, old)

    if decade_num >= 1980:
        # 年轻一辈不会用的词 → 替换
        old_to_modern = {
            "同志": "朋友",
            "组织上": "公司",
        }
        for old, modern in old_to_modern.items():
            result = result.replace(old, modern)

    # 3. 调整句尾语气词
    if enders:
        # 检查最后一个句子是否已有语气词
        sentences = re.split(r"[。！？]", result)
        sentences = [s for s in sentences if s.strip()]
        if sentences:
            last = sentences[-1].strip()
            has_ender = any(last.endswith(e) for e in enders)
            if not has_ender and enders:
                # 给最后一句加上时代语气词
                result = result.rstrip("。！？") + enders[0] + "。"

    _log(f"已完成时代语言适配（{profile['era_name']}）")
    return result


def get_era_context_for_prompt(birth_decade: str) -> str:
    """
    为 LLM prompt 生成时代背景说明。

    返回一段描述性文本，可以直接嵌入到 system prompt 中，
    帮助 LLM 在角色扮演时保持时代一致性。
    """
    profile = get_era_profile(birth_decade)
    if not profile:
        return ""

    norms = profile.get("communication_norms", {})
    lines = [
        f"## 时代背景：{profile['era_name']}（{profile['birth_range']}出生）",
        "",
        f"历史背景：{profile['historical_context']}",
        "",
        "### 语言特征",
        f"- 常用词汇：{'、'.join(profile.get('vocabulary', [])[:8])}",
        f"- 说话习惯：{'；'.join(profile.get('grammar_patterns', [])[:3])}",
        f"- 常用开头：{'；'.join(profile.get('speech_markers', [])[:4])}",
        "",
        "### 沟通风格",
        f"- 直接程度：{norms.get('directness', '未知')}",
        f"- 情感表达：{norms.get('emotional_expression', '未知')}",
        f"- 权威风格：{norms.get('authority_style', '未知')}",
        "",
        "### 文化坐标",
        f"- {'、'.join(profile.get('cultural_references', [])[:6])}",
        "",
        "### 敏感话题",
    ]
    for t in profile.get("taboo_topics", []):
        lines.append(f"- {t}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="时代语言与文化适配引擎")
    parser.add_argument("--birth-decade", required=True,
                        help="出生年代，如 1960 或 1960s")
    parser.add_argument("--action", required=True,
                        choices=["profile", "references", "adapt", "prompt-context"],
                        help="操作类型")
    parser.add_argument("--text", help="要适配的文本（adapt 模式）")
    parser.add_argument("--context", default="general",
                        choices=["general", "advice", "storytelling", "scolding", "comforting"],
                        help="语境（adapt 模式）")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    if args.action == "profile":
        profile = get_era_profile(args.birth_decade)
        if profile:
            if args.json:
                print(json.dumps(profile, ensure_ascii=False, indent=2))
            else:
                print(f"时代：{profile['era_name']}（{profile['birth_range']}）")
                print(f"背景：{profile['historical_context']}")
                print(f"\n常用词汇：{'、'.join(profile['vocabulary'])}")
                print(f"\n语法特征：")
                for g in profile["grammar_patterns"]:
                    print(f"  - {g}")
                print(f"\n文化坐标：{'、'.join(profile['cultural_references'])}")
                print(f"\n敏感话题：")
                for t in profile["taboo_topics"]:
                    print(f"  - {t}")
                norms = profile["communication_norms"]
                print(f"\n沟通风格：")
                print(f"  直接程度：{norms['directness']}")
                print(f"  情感表达：{norms['emotional_expression']}")
                print(f"  权威风格：{norms['authority_style']}")
        else:
            print(f"未找到 {args.birth_decade} 的时代档案", file=sys.stderr)
            sys.exit(1)

    elif args.action == "references":
        refs = get_cultural_references(args.birth_decade)
        if refs:
            if args.json:
                print(json.dumps(refs, ensure_ascii=False, indent=2))
            else:
                print(f"文化坐标（{args.birth_decade}s 出生）：")
                for r in refs:
                    print(f"  - {r}")
        else:
            print(f"未找到 {args.birth_decade} 的文化参照", file=sys.stderr)
            sys.exit(1)

    elif args.action == "adapt":
        if not args.text:
            parser.error("adapt 模式需要 --text 参数")
        result = adapt_language(args.text, args.birth_decade, args.context)
        print(result)

    elif args.action == "prompt-context":
        ctx = get_era_context_for_prompt(args.birth_decade)
        if ctx:
            print(ctx)
        else:
            print(f"未找到 {args.birth_decade} 的时代档案", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
