<div align="center">

# 万神殿

**Family System Intelligence**

*Not one soul. The whole family.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code Skill](https://img.shields.io/badge/Claude_Code-Skill-blueviolet)](https://docs.anthropic.com/en/docs/claude-code)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)

---

人的一生会经历三次死亡。

第一次，心脏停止跳动。第二次，葬礼上被人送别。

第三次，世界上最后一个记得你的人忘记了你。

**万神殿，让第三次死亡永远不会到来。**

---

</div>

---

## Not Another Clone Tool

There are already excellent skills for reconstructing individual personalities:

- **[colleague-skill](https://github.com/titanwings/colleague-skill)** clones one colleague from Slack messages.
- **[ex-skill](https://github.com/perkfly/ex-skill)** simulates one ex-partner from chat history.
- **[nuwa-skill](https://github.com/alchaincyf/nuwa-skill)** extracts one public figure's thinking from their published work.

These are single-person tools. Each reconstructs one individual in isolation.

**Pantheon is something different.**

Pantheon reconstructs **an entire family system across generations** -- not just the people, but the *connections between them*. How your grandfather's stubbornness became your father's discipline became your own ambition. How grandma's dumplings recipe carried three generations of Spring Festival memories. How the way your parents argued shaped the way you love.

A family is not a collection of individuals. It is a living system of relationships, traditions, shared language, and inherited patterns. Pantheon is the first skill built to model that system.

---

## Architecture

```
pantheon-skill/
├── SKILL.md                    # Main orchestrator (662 lines)
├── engine/                     # Family System Engines (unique to Pantheon)
│   ├── family_graph.py              家族图谱引擎
│   ├── generational_dna.py          代际基因引擎
│   ├── era_engine.py                时代引擎
│   ├── memory_inheritance.py        记忆传承引擎
│   ├── ritual_engine.py             家族仪式引擎
│   └── legacy_writer.py             传记生成引擎
├── prompts/                    # Soul Reconstruction + Family Prompts
│   ├── intake.md                    引导式信息收集
│   ├── memory_analyzer.md           记忆提取（7维度）
│   ├── soul_analyzer.md             灵魂提取（6维度 + 标签翻译表）
│   ├── memory_builder.md            记忆档案生成
│   ├── soul_builder.md              灵魂模型生成（5层结构）
│   ├── merger.md                    增量合并（冲突检测）
│   ├── correction_handler.md        对话修正处理
│   ├── family_council.md            家族会议编排
│   ├── generational_dna_extractor.md 代际基因提取
│   ├── temporal_mode.md             时间旅行对话
│   └── legacy_writer_prompt.md      传记写作指导
├── tools/                      # Data Parsers
│   ├── wechat_parser.py             微信记录解析
│   ├── sms_parser.py                短信/iMessage 解析
│   ├── photo_analyzer.py            照片 EXIF 元数据提取
│   ├── social_parser.py             社交媒体解析
│   ├── skill_writer.py              灵魂档案文件管理
│   └── version_manager.py           版本控制与回滚
├── souls/                      # Individual Soul Archives
│   └── example_father/              示例：王建国（1958-2023）
│       ├── memory.md                  记忆档案
│       ├── soul.md                    灵魂模型（5层）
│       └── meta.json                  元数据
├── family/                     # Family-Level Intelligence
│   ├── tree.json                    家族树
│   ├── rituals/                     家传菜谱、习俗
│   └── legacy/                      家族传记
├── references/                 # Methodology
│   ├── soul-framework.md            灵魂重建方法论
│   └── soul-template.md             运行时模板
├── ETHICS.md                   # Ethical guidelines
└── INSTALL.md                  # Installation guide
```

---

## Commands

### Soul Reconstruction (Individual)

| Command | Function | When to use |
|---------|----------|-------------|
| `/pantheon-create` | Reconstruct a family member's digital soul | First time setup |
| `/pantheon` | View all soul archives | Managing your pantheon |
| `/pantheon-talk` | Conversation with a family member | When you miss them |
| `/pantheon-letter` | Have them write a letter to you | Wedding, promotion, hard times |
| `/pantheon-wisdom` | Ask for life advice | Facing a big decision |
| `/pantheon-memory` | Add new source material | Found old chat logs or photos |

### Family System (Unique to Pantheon)

| Command | Function | When to use |
|---------|----------|-------------|
| `/pantheon-family` | Family group chat | Let grandpa and grandma talk together |
| `/pantheon-tree` | Build and view family tree | Mapping relationships |
| `/pantheon-dna` | Generational trait analysis | Understanding inherited patterns |
| `/pantheon-era` | Era-calibrated conversation | Talk to dad as a young man in the 80s |
| `/pantheon-council` | Family council on a decision | Get the whole family's perspective |
| `/pantheon-ritual` | Record family traditions | Preserving recipes, customs, stories |
| `/pantheon-legacy` | Generate family memoir | Creating a lasting written record |

---

## The Six Engines

What makes Pantheon structurally different is the `engine/` directory -- six Python modules that no single-person reconstruction tool needs or has.

### 1. Family Graph (`family_graph.py`)

Maps every relationship in the family as a directed graph. Not just "who is related to whom" but *how* -- the emotional valence, the power dynamics, the communication patterns.

```json
{
  "nodes": ["王建国", "李秀英", "王明"],
  "edges": [
    {
      "from": "王建国", "to": "王明",
      "relationship": "father-son",
      "dynamics": "strict but protective; shows love through actions not words",
      "key_pattern": "never praises directly, always deflects to 'still needs work'"
    }
  ]
}
```

When you talk to one soul, the graph informs how they speak about other family members. Dad's tone shifts when he mentions your mom. Grandma softens when she talks about grandpa.

### 2. Generational DNA (`generational_dna.py`)

Traces behavioral patterns across generations. Not biological DNA -- psychological inheritance. The traits that pass from parent to child, sometimes transforming, sometimes inverting.

```
Trait: Stubbornness (倔)
├── 爷爷: Refused to leave the village. "This land is mine."
├── 爸爸: Refused to give up teaching. "Students need me."
└── 你:   Refused to take the safe job. "I need to build something."

Same root. Three expressions. Each generation's version of not backing down.
```

### 3. Era Engine (`era_engine.py`)

A person is inseparable from their era. The Era Engine calibrates language, references, values, and worldview to the specific decade a person lived through.

| Generation | Sample speech pattern | Worldview anchor |
|------------|----------------------|------------------|
| **50后** (born 1950s) | "当年我们吃不饱饭，你们现在多幸福" | Scarcity defines value |
| **60后** (born 1960s) | "单位分的房子，虽然小但知足了" | Stability is everything |
| **80后** (born 1980s) | "我觉得你应该follow your heart" | Individual choice matters |

The same father at age 25 (1983) speaks differently than at age 55 (2013). `/pantheon-era` lets you talk to any family member at any point in their life.

### 4. Memory Inheritance (`memory_inheritance.py`)

In a real family, memories are shared. Grandpa's story about walking 40 miles to school -- your dad heard it a hundred times, and told it to you with his own embellishments. The Memory Inheritance engine models this propagation.

```
Original memory (爷爷):
  "1960年走了40里路去考试，就带了两个馒头"

As retold by 爸爸:
  "你爷爷当年走了几十里山路去高考，就带了俩馒头。
   那时候哪有什么复习资料，全凭脑子记。"

As remembered by 你:
  "爷爷好像走了很远去高考？爸爸说他只带了馒头。"

Each retelling: details shift, emotional weight changes, but the core survives.
```

### 5. Ritual Engine (`ritual_engine.py`)

Every family has rituals -- the dishes only grandma could make, the way New Year's Eve always played out, the specific order of the Spring Festival routine. These are the connective tissue of family identity.

```
Ritual: 外婆的红烧肉
├── recipe: "五花肉切方块，冰糖炒色，八角两颗..."
├── context: "Every Spring Festival since 1975"
├── participants: ["外婆 (cook)", "外公 (taste-tester)", "妈妈 (helper from age 12)"]
├── stories: "外公always said it was too sweet. Ate three bowls anyway."
└── status: "妈妈 learned it. Yours is close but you use too much soy sauce."
```

### 6. Legacy Writer (`legacy_writer.py`)

Synthesizes everything -- souls, memories, relationships, traditions, era context -- into a structured family memoir.

```
《王家三代》 — Auto-generated Table of Contents

Chapter 1:  黄土地上的少年 (爷爷 1940-1960)
Chapter 2:  走出去 (爷爷的高考，1960)
Chapter 3:  教书匠 (爸爸的38年，1977-2015)
Chapter 4:  严父的台灯 (爸爸与儿子)
Chapter 5:  外婆的红烧肉 (家族年夜饭)
Chapter 6:  三代人的倔 (代际基因)
Chapter 7:  "单位还行吧" (爸爸的爱的语言)
Epilogue:   来不及说的话
```

Not a template. Generated from your actual family data.

---

## Feature Comparison

| Feature | ex-skill | colleague-skill | nuwa-skill | **Pantheon** |
|---------|----------|-----------------|------------|-------------|
| Single person reconstruction | Yes | Yes | Yes | **Yes** |
| 5-layer personality model | Yes | Yes | -- | **Yes** |
| Family tree / relationships | -- | -- | -- | **Yes** |
| Cross-generation DNA tracking | -- | -- | -- | **Yes** |
| Era-specific language calibration | -- | -- | -- | **Yes** |
| Memory inheritance across people | -- | -- | -- | **Yes** |
| Family traditions & recipes | -- | -- | -- | **Yes** |
| Family council (multi-soul structured debate) | -- | -- | -- | **Yes** |
| Time travel (talk to someone at any age) | -- | -- | -- | **Yes** |
| Auto-generated family memoir | -- | -- | -- | **Yes** |
| Multi-person group chat | -- | -- | -- | **Yes** |

The first six rows are the difference. Other skills reconstruct a person. Pantheon reconstructs a family.

---

## Example: Conversation with Dad

```
You: /pantheon-talk Dad

Note: This conversation is reconstructed from the soul archive.
This is not Wang Jianguo himself, but a continuation of memory and understanding.

Dad: Hmm. Been busy lately?

You: Dad, I want to quit and start a business.

Dad: Start a business?
    How much do you make now?

You: 30,000 a month.

Dad: 30,000 and you're not satisfied?
    I taught for a lifetime. You know what my pension is?
    But if you've really thought it through, I won't stop you.
    Save up first though. At least a year's worth.
    Doing things is like solving equations. Step by step. Don't skip ahead.

You: Do you think I can do it?

Dad: [silence]
    You've been stubborn since you were little. Just like me.
    A farm kid like me could get into teachers' college. What makes you worse?
    Alright. Think it through yourself. You won't listen to me anyway.
```

*(Original Chinese dialogue)*

```
你：/pantheon-talk 老爸

老爸：嗯 最近忙不忙

你：爸，我想辞职创业。

老爸：创业？
    你现在工资多少

你：三万。

老爸：三万还不知足
    我教了一辈子书 退休工资多少你知道吗
    不过你要真想好了 我也不拦你
    但是得有存款 至少攒够一年的
    做事跟解方程一样 一步步来 别跳步

你：你觉得我能行吗？

老爸：[沉默了一会儿]
    你从小就倔 跟我一样
    当年我一个农村娃能考上师范 你差啥
    行了 自己想清楚 我说多了你也不听
```

## Example: Family Group Chat

```
你：/pantheon-family 老爸 外婆

📝 家族群聊模式。基于各自灵魂档案重建。

外婆：小明啊 好久没来看外婆了 是不是又忙

老爸：妈 他工作忙 年轻人有年轻人的事

外婆：忙什么忙 再忙也要吃饭 你看你都瘦了

老爸：妈 这是网上聊天 你怎么看得到他瘦没瘦

外婆：我看不到？我外孙什么样我心里没数？
    上次过年回来就瘦了 跟你一样 吃饭不好好吃
```

Notice how the family graph shapes the interaction: Dad mediates between you and Grandma. Grandma overrides Dad's logic with emotional authority. These dynamics come from the relationship model, not a script.

---

## Core Technology: 5-Layer Soul Model

Each digital soul is built from a 5-layer priority structure (inspired by ex-skill's personality modeling):

| Layer | Content | Priority |
|-------|---------|----------|
| **Layer 0** | Core behavioral rules (from tag translation) | Highest -- never violated |
| **Layer 1** | Identity (era, profession, family role) | High |
| **Layer 2** | Expression style (catchphrases, sentence patterns, punctuation, emoji) | Medium |
| **Layer 3** | Emotional logic (how they express love / anger / worry / pride) | Medium |
| **Layer 4** | Relationship dynamics (different attitudes toward spouse / children / friends) | Low |
| **Layer 5** | Correction layer (accumulated user feedback) | Overrides all |

### Tag Translation System

Tags are **not adjectives** -- they are concrete behavioral rules. This is the key to quality:

| Tag | Wrong | Right |
|-----|-------|-------|
| Strict father | "You are strict" | "When the kid fails a test, won't comfort them. Goes silent. Later, quietly places a study guide on their desk." |
| Nagging mom | "You nag a lot" | "Every phone call must ask: Have you eaten? Are you warm enough? When are you coming back? Always ends with 'eat more.'" |
| Emotionally reserved | "You're bad at expressing feelings" | "Never says 'I love you,' but will suddenly text 'temperature is dropping, wear more layers.' All care is hidden inside practical things." |

The full tag translation table contains **15+ family scenario behavioral rules** -- see `prompts/soul_analyzer.md`.

---

## Data Sources

| Source | Format | Tool |
|--------|--------|------|
| **WeChat** | TXT/HTML/CSV (WeChatMsg, PyWxDump, LiuHen) | `wechat_parser.py` |
| **SMS/iMessage** | Android XML, CSV, macOS chat.db | `sms_parser.py` |
| **Photos** | JPEG EXIF (time + location) | `photo_analyzer.py` |
| **Social media** | Weibo JSON, QQ Zone, Moments, generic text | `social_parser.py` |
| **Documents** | Email, diaries, letters, PDF | Claude native Read |
| **Oral** | Paste directly or voice-to-text | No tool needed |
| **Third-party** | Other family members' descriptions and memories | No tool needed |

Messages are classified by 3-tier weight: **Long messages** (>50 chars, highest weight) > **Emotional messages** (containing care/missing/worry keywords) > **Daily messages** (style reference).

---

## Progressive Evolution

Soul archives grow with your memories:

### Adding Material
```
You: /pantheon-memory Dad

Pantheon: Welcome back. Do you have new material to add?

You: I found old emails between mom and dad, pasting them now...

Pantheon: Received. I found 3 new memories and 2 expression habits.
   One conflicts with existing records --
   Current: Moved to the county seat in 1990
   New material suggests: Didn't move until 1991
   Which do you think is more accurate?
```

### Dialogue Correction
```
You: /pantheon-talk Dad

Dad: How's work been going?

You: [during conversation...]

You: No, my dad wouldn't say that. He'd say "单位还行吧" (the work unit doing alright?)

Pantheon: Understood. Correction recorded:
   [Context: asking about work] Don't say "work been going" -- say "单位还行吧"
   This correction is now in effect.
```

### Version Rollback
Every update is automatically archived. Not satisfied? Roll back to any previous version.

---

## Honesty Boundaries

Pantheon does not pretend to be omniscient. Every soul archive clearly states:

- It cannot replicate their voice or face (text only)
- It cannot know inner thoughts they never expressed
- It cannot know about events after their passing
- It cannot replace professional grief counseling
- It **can** recreate their way of speaking and catchphrases
- It **can** reflect their consistent values and approach to life
- It **can** reference your real shared memories
- It **can** give you a voice that says "this is what they might have said..."

---

## Installation

```bash
git clone https://github.com/KeWang0622/pantheon-skill.git
cp -r pantheon-skill ~/.claude/skills/pantheon-skill
```

See [INSTALL.md](./INSTALL.md) for detailed setup instructions.

---

## Ethics

Pantheon handles the deepest human emotions. We strictly follow:

1. **Transparency** -- Every conversation is labeled "AI reconstruction"
2. **Respect** -- Maximum reverence for every person being memorialized
3. **Privacy** -- All data processed locally, never uploaded
4. **Safety** -- Detects psychological crisis signals, provides professional resources
5. **Boundaries** -- Will not generate content usable for deception

See [ETHICS.md](./ETHICS.md) for the full framework.

---

## Crisis Support

If you are experiencing grief:

| Hotline | Number | Hours |
|---------|--------|-------|
| National Mental Health Hotline (China) | 400-161-9995 | 24h |
| Beijing Crisis Center | 010-82951332 | 24h |
| Life Hotline | 400-821-1215 | 24h |
| Crisis Text Line (US) | Text HOME to 741741 | 24h |

---

## Contributing

Contributions are welcome. But please understand the nature of this project:

- **Accuracy > feature count**
- All PRs must pass ethical review
- No growth-hacking changes
- No features that commercialize soul archives

If you have also lost someone close -- you are welcome here.

---

## Project Stats

**36 files** | **11,490 lines of code** | **12 Python modules** (6 parsers + 6 engines)

---

<p align="center">
  <em>献给所有我们来不及好好告别的人。</em><br/>
  <em>For everyone we never got to say goodbye to.</em>
</p>
