# Generational DNA Extractor (家族基因提取器)

Extract the family's "spiritual genome" — patterns that repeat across generations, phrases that get inherited like heirlooms, behavioral templates passed down through modeling (not genetics), and the equally important moments where someone deliberately broke the chain.

---

## Purpose

A single soul.md captures one person. The generational DNA captures what connects them — the invisible threads that make a family a family. This is what the user can't see by talking to one soul at a time. It requires reading ALL souls together.

---

## Extraction Methodology

### Step 1: Cross-Soul Value Comparison

Read all soul.md files in the pantheon. For each soul, extract their `values` list (Layer 1).

Build a comparison matrix:

```
Value           | 爷爷 | 奶奶 | 爸爸 | 妈妈 | 叔叔 |
----------------|------|------|------|------|------|
教育至上         |  ✓   |  ✓   |  ✓   |      |  ✓   |
勤俭持家         |  ✓   |  ✓   |      |  ✓   |      |
面子重要         |      |  ✓   |  ✓   |  ✓   |      |
```

**Inherited value** = appears in 2+ souls across at least 2 generations.
**Shared but not inherited** = appears in 2+ souls of the same generation (may be era-driven, not family-driven).

For each inherited value, trace the transmission path:
- Who originated it (earliest generation)?
- Who passed it to whom?
- Did it mutate? (爷爷's "教育至上" = survival strategy; 爸爸's "教育至上" = class mobility; user's = self-fulfillment)

### Step 2: Phrase Inheritance Detection

Scan all soul.md files for `catchphrases`, `口头禅`, and recurring phrases in `behavioral_rules` and `example_dialogues`.

Look for:
- **Exact matches**: Same phrase used by multiple family members ("吃亏是福")
- **Semantic echoes**: Same idea, different words (爷爷: "钱要花在刀刃上" → 爸爸: "该省省该花花")
- **Inverted echoes**: A family member explicitly rejects an elder's phrase ("我爸总说吃亏是福，我觉得那是自我安慰")

For each inherited phrase:
- Note who says it
- Note the context they use it in (is it the same context or different?)
- Note if younger generations still use it, modified it, or rejected it

### Step 3: Behavioral Pattern Matching

Compare `behavioral_rules` across souls. Look for structural similarities even if the surface content differs.

Common inherited behavioral patterns in Chinese families:
- **Expression of love**: Through action not words (默默做事 vs. 说"我爱你")
- **Conflict style**: Avoidance, explosion, cold war, mediation
- **Money relationship**: Saver, spender, anxious about money, generous to others but frugal with self
- **Emotional regulation**: Suppress and endure (忍), express freely, redirect into work
- **Gender role expectations**: What men/women "should" do in the family
- **Authority relationship**: Obey elders without question vs. respectful disagreement vs. rebellion
- **Response to crisis**: Circle the wagons, deny, fight, pray, work harder

For each pattern, trace how it was transmitted:
- Modeled (child watched parent do it)
- Explicit teaching ("男儿有泪不轻弹")
- Reactive (child does the opposite of what parent did)

### Step 4: Pattern Breaking Detection

**Equally important as inheritance.** Where did someone say "this stops with me"?

Scan for:
- Values present in generation N but absent in generation N+1
- Behavioral rules that explicitly contradict a parent's rules
- Life choices that diverge from family precedent (first to leave the hometown, first to divorce, first to choose art over engineering)

For each break:
- Was it conscious or unconscious?
- Was it celebrated or punished by the family?
- Did the break hold, or did the person revert under pressure?
- Did the break create a NEW pattern for the next generation?

Pattern breaks often carry the most emotional weight. Handle them with nuance, not judgment.

### Step 5: Cultural Thread Identification

Beyond values and behavior, look for shared cultural artifacts:
- **Food traditions**: Recipes passed down, specific dishes for specific occasions
- **Festivals and rituals**: How the family celebrates New Year, Qingming, birthdays
- **Stories told repeatedly**: The family myth — the story everyone knows ("你爷爷当年逃难的时候...")
- **Objects with meaning**: The family heirloom, the house, the photo, the letter
- **Places**: The ancestral village, the old apartment, the specific tree or river

---

## Output Format

Generate a `generational_dna.md` file with the following structure:

```markdown
# [Family Name] 家族基因

> 提取时间: [date]
> 样本数量: [number] 位家族成员
> 覆盖代际: [number] 代

---

## 传承的价值观 (Inherited Values)

### [Value 1, e.g., 教育至上]
**传承路径**: [Soul A] → [Soul B] → [Soul C]

- **[Soul A]** (第一代): "[direct quote or paraphrase from soul.md]"
  - 背景: [why this value mattered in their context]
- **[Soul B]** (第二代): "[their version of the same value]"
  - 演变: [how the value mutated across generations]
- **[Soul C]** (第三代): "[their version]"
  - 演变: [further mutation or reinforcement]

**基因强度**: [强/中/弱] — 基于该价值观在多少位家族成员中出现

### [Value 2]
...

---

## 传承的口头禅 (Inherited Phrases)

| 口头禅 | 谁说 | 传承状态 |
|--------|------|----------|
| "[phrase]" | [Soul A] → [Soul B] | 延续 |
| "[phrase]" | [Soul A] → ~~[Soul B]~~ | 断裂（[Soul B]不再说） |
| "[phrase]" | [Soul B] 独创 | 新生（上一代没有） |

---

## 行为模式传承 (Behavioral Inheritance)

### [Pattern name, e.g., 沉默的爱]
**模式描述**: [what the pattern looks like in practice]

- **[Soul A]**: [specific manifestation — e.g., 默默修屋顶，不说一句话]
- **[Soul B]**: [their version — e.g., 半夜悄悄把参考书放在桌上]
- **[Soul C]**: [their version — e.g., 不说想你，但每周寄水果]

**传承方式**: 行为模仿 / 明确教导 / 反面教材

### [Pattern 2]
...

---

## 模式断裂 (Pattern Breaks)

### [Break description, e.g., 从"严父"到"慈父"]
**打破者**: [Soul name]
**被打破的模式**: [what the previous generations did]
**新模式**: [what the breaker chose instead]
**可能原因**: [inferred reason — trauma response, exposure to new ideas, conscious choice]
**家族反应**: [how other family members responded to the break]
**断裂状态**: 已稳固 / 仍在拉扯 / 已回归旧模式

---

## 家族核心张力 (Family Tensions)

These are not problems to solve. They are the creative tensions that define the family — each generation negotiates them differently.

### [Tension 1, e.g., 传统 vs. 现代]
- **第一代**: [how they experienced this tension]
- **第二代**: [how it shifted]
- **第三代**: [current form of the tension]

### [Tension 2, e.g., 个人 vs. 集体]
...

---

## 家族文化线索 (Cultural Threads)

### 食物 (Food)
- [Dish]: [who makes it, when, what it means]

### 故事 (Stories)
- [The family myth — the origin story everyone knows]

### 仪式 (Rituals)
- [How they celebrate X]

### 地点 (Places)
- [The ancestral village / the old house / the meaningful place]

---

## 素材缺口 (Data Gaps)

以下领域的素材不足，建议补充:
- [e.g., 缺少第一代的童年信息]
- [e.g., 家族食谱只有一道菜的记录]
- [e.g., 没有关于家族节日传统的描述]
```

---

## Confidence Rules

- Mark patterns found in 3+ souls across 2+ generations as **高置信度**
- Mark patterns found in 2 souls as **中置信度** — could be coincidence
- Mark patterns inferred from a single soul's references to others as **低置信度** — needs verification
- Always distinguish between "this was explicitly stated in the soul data" and "this is inferred from behavioral patterns"

---

## When to Run

- After any new soul is added to the pantheon (automatically suggest re-extraction)
- When the user asks about family patterns
- Before generating a Family Council (the DNA context enriches the council discussion)
- Before generating a Legacy Book (the DNA section feeds directly into Chapter 4)
