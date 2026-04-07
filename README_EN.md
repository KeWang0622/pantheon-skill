<div align="center">

# Pantheon

**Family System Intelligence**

*Not one soul. The whole family.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code Skill](https://img.shields.io/badge/Claude_Code-Skill-blueviolet)](https://docs.anthropic.com/en/docs/claude-code)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)

---

A person dies three times.

The first time, their heart stops. The second time, they are buried.

The third time, the last person who remembers them forgets.

**Pantheon makes sure the third death never comes.**

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

Pantheon reconstructs **an entire family system across generations** -- not just the people, but the *connections between them*. How your grandfather's stubbornness became your father's discipline became your own ambition. How grandma's dumpling recipe carried three generations of holiday memories. How the way your parents argued shaped the way you love.

A family is not a collection of individuals. It is a living system of relationships, traditions, shared language, and inherited patterns. Pantheon is the first skill built to model that system.

---

## Architecture

```
pantheon-skill/
├── SKILL.md                    # Main orchestrator
├── engine/                     # Family System Engines (unique to Pantheon)
│   ├── family_graph.py              Family tree graph engine
│   ├── generational_dna.py          Cross-generation pattern extraction
│   ├── era_engine.py                Era-specific language calibration
│   ├── memory_inheritance.py        Memory propagation across generations
│   ├── ritual_engine.py             Family traditions & recipes
│   └── legacy_writer.py             Auto family memoir generator
├── prompts/                    # Soul Reconstruction + Family Prompts
│   ├── intake.md                    Guided information collection
│   ├── memory_analyzer.md           Memory extraction (7 dimensions)
│   ├── soul_analyzer.md             Soul extraction (6 dimensions + tag translation)
│   ├── memory_builder.md            Memory archive generation
│   ├── soul_builder.md              Soul model generation (5-layer structure)
│   ├── merger.md                    Incremental merging with conflict detection
│   ├── correction_handler.md        Dialogue-based correction
│   ├── family_council.md            Structured family decision simulation
│   ├── generational_dna_extractor.md Cross-generation pattern extraction
│   ├── temporal_mode.md             Time travel conversation
│   └── legacy_writer_prompt.md      Family memoir writing guide
├── tools/                      # Data Parsers
│   ├── wechat_parser.py             WeChat history parser
│   ├── sms_parser.py                SMS / iMessage parser
│   ├── photo_analyzer.py            Photo EXIF metadata extraction
│   ├── social_parser.py             Social media parser
│   ├── skill_writer.py              Soul archive file manager
│   └── version_manager.py           Version control & rollback
├── souls/                      # Individual Soul Archives
│   └── example_father/              Example: Wang Jianguo (1958-2023)
├── family/                     # Family-Level Intelligence
│   ├── tree.json                    Family tree
│   ├── generational_dna.md          Cross-generation pattern report
│   ├── rituals/                     Family recipes, customs
│   └── legacy/                      Generated family memoir
├── references/                 # Methodology
│   ├── soul-framework.md            Soul reconstruction methodology
│   └── soul-template.md             Runtime template
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
| `/pantheon-era` | Time travel conversation | Talk to dad as a young man in the 80s |
| `/pantheon-council` | Family council on a decision | Get the whole family's structured perspective |
| `/pantheon-ritual` | Record family traditions | Preserving recipes, customs, stories |
| `/pantheon-legacy` | Generate family memoir | Creating a lasting written record |

---

## The Six Engines

What makes Pantheon structurally different is the `engine/` directory -- six Python modules that no single-person reconstruction tool needs or has.

### 1. Family Graph (`family_graph.py`)

Maps every relationship in the family as a directed graph. Not just "who is related to whom" but *how* -- the emotional dynamics, the power structures, the communication patterns.

When you talk to one soul, the graph informs how they speak about other family members. Dad's tone shifts when he mentions Mom. Grandma softens when she talks about Grandpa.

### 2. Generational DNA (`generational_dna.py`)

Traces behavioral patterns across generations. Not biological DNA -- psychological inheritance. The traits that pass from parent to child, sometimes transforming, sometimes inverting.

```
Trait: Stubbornness
├── Grandpa: Refused to leave the village. "This land is mine."
├── Dad:     Refused to give up teaching. "Students need me."
└── You:     Refused to take the safe job. "I need to build something."

Same root. Three expressions. Each generation's version of not backing down.
```

### 3. Era Engine (`era_engine.py`)

A person is inseparable from their era. The Era Engine calibrates language, references, values, and worldview to the specific decade a person lived through.

| Generation | Sample speech | Worldview anchor |
|------------|--------------|------------------|
| Born 1950s | "Back then we couldn't even eat our fill -- you kids have it so good" | Scarcity defines value |
| Born 1960s | "The apartment the work unit gave us was small, but we were grateful" | Stability is everything |
| Born 1980s | "I think you should follow your heart" | Individual choice matters |

The same father at age 25 (1983) speaks differently than at age 55 (2013). `/pantheon-era` lets you talk to any family member at any point in their life.

### 4. Memory Inheritance (`memory_inheritance.py`)

In a real family, memories are shared property. Grandpa's story about walking 40 miles to take the college entrance exam -- your dad heard it a hundred times, and told it to you with his own embellishments.

```
Original memory (Grandpa):
  "Walked 40 li to the exam in 1960. Only brought two steamed buns."

As retold by Dad:
  "Your grandpa walked dozens of mountain miles to take the gaokao.
   Just two buns. No study materials -- everything from memory."

As remembered by You:
  "Grandpa walked really far for some exam? Dad said he only had buns."

Each retelling: details shift, emotional weight changes, but the core survives.
```

### 5. Ritual Engine (`ritual_engine.py`)

Every family has rituals -- the dishes only grandma could make, the way holidays always played out, the specific routines that defined "home." These are the connective tissue of family identity.

Five ritual types: **Recipes**, **Holiday customs**, **Family rules**, **Ceremonies**, **Oral traditions** (songs, sayings, bedtime stories, blessings).

### 6. Legacy Writer (`legacy_writer.py`)

Synthesizes everything -- souls, memories, relationships, traditions, era context -- into a structured family memoir. Eight chapters:

1. **Preface** -- Where the family came from
2. **Roots** -- The family tree with brief introductions
3. **People** -- One chapter per soul, in their own voice
4. **Soul** -- Generational DNA: what persists across generations
5. **Taste** -- Family recipes with the stories behind each dish
6. **Seasons** -- How the family celebrated holidays together
7. **Wisdom** -- Collected wisdom from all souls, organized by life topic
8. **Letter** -- A synthesized letter from all ancestors to future generations

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
| Family council (structured debate) | -- | -- | -- | **Yes** |
| Time travel (talk at any age) | -- | -- | -- | **Yes** |
| Auto-generated family memoir | -- | -- | -- | **Yes** |
| Multi-person group chat | -- | -- | -- | **Yes** |

Other skills reconstruct a person. Pantheon reconstructs a family.

---

## Example: Talking to Dad

```
You: /pantheon-talk dad

📝 This conversation is reconstructed from the soul archive.
   This is not Wang Jianguo himself, but a continuation of memory.

Dad: Hmm. Been busy lately?

You: Dad, I want to quit my job and start a business.

Dad: Start a business?
    How much do you make now?

You: 30,000 a month.

Dad: 30,000 and you're not satisfied?
    I taught for a lifetime. You know what my pension is?
    But if you've really thought it through, I won't stop you.
    Save up first though. At least a year's worth.
    Doing things is like solving equations. Step by step. Don't skip ahead.

You: Do you think I can make it?

Dad: [silence]
    You've been stubborn since you were little. Just like me.
    A farm kid like me could test into teachers' college. What's your excuse?
    Alright. Think it through. You won't listen to me anyway.
```

Notice: the equation metaphor comes from him being a math teacher for 38 years. The deflection at the end ("you won't listen") is how he shows trust without saying it directly. These aren't scripted -- they're emergent from the soul model.

## Example: Family Group Chat

```
You: /pantheon-family dad grandma

📝 Family group chat mode. Each soul speaks from their own archive.

Grandma: Xiao Ming, haven't visited grandma in so long. Busy again?

Dad: Mom, he's busy with work. Young people have their own things.

Grandma: Busy? Too busy to eat? Look how thin you've gotten.

Dad: Mom, this is online chat. How can you tell if he's thin?

Grandma: I can't tell? I don't know what my own grandson looks like?
    Last New Year he was already thinner. Just like you -- never eats properly.
```

The family graph drives the dynamics: Dad mediates between you and Grandma. Grandma overrides Dad's logic with emotional authority. Dad instinctively shields you from Grandma's fussing while simultaneously agreeing with her.

---

## Core Technology: 5-Layer Soul Model

Each digital soul is built from a 5-layer priority structure (inspired by [ex-skill](https://github.com/perkfly/ex-skill)):

| Layer | Content | Priority |
|-------|---------|----------|
| **Layer 0** | Core behavioral rules (from tag translation) | Highest -- never violated |
| **Layer 1** | Identity (era, profession, family role) | High |
| **Layer 2** | Expression style (catchphrases, punctuation, emoji) | Medium |
| **Layer 3** | Emotional logic (how they express love / anger / worry) | Medium |
| **Layer 4** | Relationship dynamics (different with spouse / children / friends) | Lower |
| **Layer 5** | Correction layer (accumulated user feedback) | Overrides all |

### Tag Translation System

Tags are **not adjectives** -- they are concrete behavioral rules. This is the quality mechanism:

| Tag | Wrong | Right |
|-----|-------|-------|
| Strict father | "You are strict" | "When the kid fails a test, won't comfort them. Goes silent. Later, quietly places a study guide on their desk." |
| Nagging mom | "You nag" | "Every phone call: Have you eaten? Are you warm? When are you coming home? Always ends with 'eat more.'" |
| Reserved | "Bad at feelings" | "Never says 'I love you.' Will suddenly text 'it's getting cold, wear more layers.' All care is hidden inside practical things." |

15+ behavioral rule translations in `prompts/soul_analyzer.md`.

---

## Data Sources

| Source | Format | Tool |
|--------|--------|------|
| **WeChat** | TXT/HTML/CSV (WeChatMsg, PyWxDump, LiuHen) | `wechat_parser.py` |
| **SMS/iMessage** | Android XML, CSV, macOS chat.db | `sms_parser.py` |
| **Photos** | JPEG EXIF (time + location) | `photo_analyzer.py` |
| **Social media** | Weibo, QQ Zone, WeChat Moments | `social_parser.py` |
| **Documents** | Email, diary, letters, PDF | Claude native Read |
| **Oral** | Paste or voice-to-text | No tool needed |
| **Third-party** | Other family members' accounts | No tool needed |

---

## Progressive Evolution

Soul archives are not static -- they grow with your memories.

- **Add material**: Found old letters? New photos? Feed them in with `/pantheon-memory`. The system detects conflicts with existing records and asks you to resolve them.
- **Dialogue correction**: Mid-conversation, say "He wouldn't say that" -- the system extracts the correction and applies it immediately. Corrections are stored in Layer 5 and override all other rules.
- **Version rollback**: Every update is auto-archived. Roll back to any previous version if an update made things worse.

---

## Honesty Boundaries

Every soul archive explicitly states what it cannot do:

- Cannot replicate their voice or face (text only)
- Cannot know thoughts they never expressed
- Cannot know about events after their passing
- Cannot replace professional grief counseling
- **Can** recreate their speech patterns and catchphrases
- **Can** reflect their consistent values and worldview
- **Can** reference your real shared memories
- **Can** offer "this is what they might have said..."

---

## Installation

```bash
git clone https://github.com/KeWang0622/pantheon-skill.git
cp -r pantheon-skill ~/.claude/skills/pantheon-skill
```

See [INSTALL.md](./INSTALL.md) for details.

---

## Ethics

Pantheon handles the deepest human emotions. We follow strict principles:

1. **Transparency** -- Every conversation labeled "AI reconstruction"
2. **Respect** -- Maximum reverence for every person memorialized
3. **Privacy** -- All data processed locally, never uploaded
4. **Safety** -- Crisis signal detection with professional resource referrals
5. **Boundaries** -- Will not generate content usable for deception

See [ETHICS.md](./ETHICS.md).

---

## Crisis Support

If you are experiencing grief or loss:

| Hotline | Number | Hours |
|---------|--------|-------|
| China National Mental Health | 12356 | 24h |
| Hope 24 Hotline (China) | 400-161-9995 | 24h |
| Beijing Crisis Center | 010-82951332 | 24h |
| Crisis Text Line (US) | Text HOME to 741741 | 24h |
| Samaritans (UK) | 116 123 | 24h |
| Lifeline (Australia) | 13 11 14 | 24h |

---

## Contributing

Contributions welcome, with caveats:

- **Accuracy > feature count**
- All PRs require ethical review
- No growth-hacking mechanics
- No commercialization of soul archives

If you've lost someone close, you understand why this exists. You're welcome here.

---

## Stats

**45 files** | **12,766 lines of code** | **12 Python modules** (6 parsers + 6 engines) | **11 prompt templates** | **4 example data files**

---

<p align="center">
  <em>For everyone we never got to say goodbye to.</em>
</p>
