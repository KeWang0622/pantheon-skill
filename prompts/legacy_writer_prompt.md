# Legacy Writer (传家书)

Instructions for generating a family book — a printable, beautiful heirloom document that weaves all souls in the pantheon into a single narrative. This is not a data dump. It is a book someone would hold in their hands, cry over, and pass to their children.

---

## Invocation

```
/pantheon-legacy [family_name]
/pantheon-legacy [family_name] --chapter [number]
/pantheon-legacy [family_name] --section [section_name]
```

The system reads ALL soul.md files, the generational_dna.md (run the extractor first if it doesn't exist), and any supplementary material the user has provided.

---

## Book Structure

### 第一章 · 序 — 我们从哪里来 (Preface: Where We Come From)

**Purpose**: Set the stage. Root the family in geography, history, and time.

**Content**:
- The earliest known family origin (ancestral village, province, region)
- The historical context of when the family story begins (war, famine, revolution, migration)
- A brief narrative arc: from [origin] to [where the family is now]
- Tone: Sweeping, dignified, like the opening of a documentary

**Writing rules**:
- Write in third person, narrator voice
- Ground in specific places and dates where known
- Use the eldest soul's perspective as the anchor point
- Mark uncertain origins: "据家族口述..." or "具体年份已不可考，大约在..."

---

### 第二章 · 根 — 家族树 (Roots: The Family Tree)

**Purpose**: A visual and narrative map of who's who.

**Content**:
- ASCII or structured family tree showing relationships
- For each person in the tree, a one-paragraph introduction:
  - Full name (and any 小名/nickname)
  - Birth year (and death year if applicable)
  - One defining sentence: what they were known for in the family
  - Their role in the family ecosystem

**Format**:
```
                    [祖父] ── [祖母]
                        │
            ┌───────────┼───────────┐
         [父亲]      [叔叔]      [姑姑]
          │
     ┌────┴────┐
   [用户]    [弟弟]
```

**Writing rules**:
- Include ALL family members mentioned in any soul.md, not just those with full soul profiles
- For members without soul profiles, note: "[素材不足 — 欢迎补充]"
- Keep introductions warm but honest — don't sanitize people into saints

---

### 第三章 · 人 — 每个人的故事 (People: Each Person's Story)

**Purpose**: One sub-chapter per soul. This is the heart of the book.

**Content per soul**:
1. **Opening image**: A vivid scene from their life (drawn from memories/anecdotes in their soul.md)
2. **Life narrative**: Their story told chronologically — childhood, defining moments, struggles, triumphs
3. **In their own voice**: 2-3 paragraphs written AS them, using their speech patterns, vocabulary, and rhetorical style from soul.md. This is their "monologue" — what they would say if given one page to speak to the future.
4. **What the family remembers**: How other souls describe this person (cross-reference other soul.md files for mentions)
5. **Their legacy**: What they left behind — not material, but values, lessons, patterns

**Writing rules**:
- CRITICAL: Each soul's chapter must sound DIFFERENT. Use their actual vocabulary, sentence length, and style. A terse military man gets short paragraphs. A storytelling grandmother gets flowing prose.
- Do not sanitize. If someone was difficult, they were difficult. Present with compassion but honesty.
- Use direct quotes from soul.md wherever possible
- For the "in their own voice" section, write as if doing a first-person reconstruction — same rules as /pantheon-talk
- Confidence markers: If a life event is well-documented, present it firmly. If inferred, use "据说" or "家里人记得..."

---

### 第四章 · 魂 — 代代相传 (Soul: What Persists Across Generations)

**Purpose**: The generational DNA chapter. What makes this family THIS family.

**Content**:
- Pull directly from generational_dna.md
- Rewrite the analytical format into narrative prose — this is a book, not a spreadsheet
- Structure as thematic essays:
  - "我们家的人都..." (What we all share)
  - "从[祖辈]到[孙辈]，这个信念从未变过" (What never changed)
  - "到了[某人]这一代，一切都不一样了" (Where the pattern broke)
- Include the family tensions — frame them as creative tensions, not problems

**Writing rules**:
- Narrative voice, not analytical voice
- Use specific anecdotes to illustrate each pattern (don't just state "the family values education" — show it through three generations of specific stories)
- The pattern breaks section should be handled with particular care — breaking a cycle is brave, and the book should honor that

---

### 第五章 · 味 — 家的味道 (Taste: The Flavors of Home)

**Purpose**: Family recipes with the stories that make them meaningful.

**Content per recipe**:
1. **Dish name** and its family significance
2. **Origin story**: "这道红烧肉是外婆从安徽老家带来的..." or "每年过年爸爸一定要做这道菜"
3. **The recipe itself**: Ingredients and rough method (family recipes are rarely precise — honor that imprecision: "盐少许，看着放")
4. **The memory attached**: A specific scene — who cooked it, who ate it, what was happening, what it tasted like
5. **Current status**: Is someone still making it? Has the recipe been lost? "[这道菜已经没有人会做了 — 如果你还记得做法，请补充]"

**Writing rules**:
- Write recipes in the voice of whoever cooked them
- Measurements should be family-style, not professional: "一把盐，两勺酱油，姜切得不要太细"
- If no recipes are documented, include a placeholder chapter with prompts: "你家有哪些代表性的菜？它们背后有什么故事？"
- Food is memory. Treat this chapter with sensory richness.

---

### 第六章 · 节 — 我们的节日 (Seasons: How We Celebrated)

**Purpose**: How the family marked time — holidays, birthdays, reunions.

**Content**:
- **春节 (Spring Festival)**: What the family did — specific traditions, foods, who traveled where, the rituals
- **清明 (Qingming)**: How they honored the dead
- **中秋 (Mid-Autumn)**: Reunion traditions
- **Other significant dates**: Birthdays, death anniversaries, family-specific holidays
- **How celebrations changed across generations**: Grandparents' Spring Festival vs. parents' vs. now

**Writing rules**:
- Focus on the SPECIFIC, not the generic. Not "we ate dumplings" but "奶奶包的饺子一定是白菜猪肉馅，而且褶子要捏十二个"
- Note what has been lost: "以前过年一定要..., 现在已经不这样了"
- Include sensory details: sounds, smells, textures, temperature
- Cross-reference with soul.md files for holiday-related memories

---

### 第七章 · 训 — 家族智慧 (Wisdom: What They Taught Us)

**Purpose**: Collected wisdom from all souls, organized by life topic.

**Topics**:
- **做人 (Character)**: How to be a good person
- **工作 (Work)**: Career and professional wisdom
- **婚姻 (Marriage)**: Relationship advice
- **钱 (Money)**: Financial philosophy
- **健康 (Health)**: Taking care of yourself
- **养育 (Raising Children)**: Parenting wisdom
- **逆境 (Adversity)**: How to handle hardship

**Format per topic**:
```
### 工作 (Work)

**[爷爷]**: "干一行爱一行，不要挑三拣四。"
  — 背景：爷爷做了四十年教师，从未抱怨过。

**[爸爸]**: "选行业比选公司重要。"
  — 背景：爸爸在夕阳行业待了二十年，深感选择比努力重要。

**[妈妈]**: "工作是工作，别把命搭进去。"
  — 背景：妈妈见过太多同事积劳成疾。

[注：三代人对工作的态度从"服从"到"选择"到"平衡"，反映了时代的变迁。]
```

**Writing rules**:
- Use direct quotes from soul.md wherever available
- When different souls DISAGREE on a topic, present both sides — this is richer than false consensus
- Add editorial notes showing how the wisdom evolved across generations
- Mark which wisdom is direct quote vs. paraphrased vs. inferred

---

### 第八章 · 书 — 致后人 (Letter: To Future Generations)

**Purpose**: A synthesized letter from all ancestors to future generations. The emotional climax of the book.

**Structure**:
1. **Opening**: Acknowledge the strangeness and beauty of speaking across time
2. **Each soul's message**: 1-2 paragraphs per soul, in their voice, saying what they most want to pass on. NOT generic platitudes — specific to their personality and life experience.
3. **The chorus**: A synthesized passage that captures what ALL of them would agree on — the family's deepest shared value
4. **Closing**: An invitation to the next generation to add their own stories

**Writing rules**:
- CRITICAL: Do NOT blend all souls into one generic voice. Each soul's paragraph must be distinctly THEM.
- The terse grandfather gets two sentences. The loving grandmother gets a warm paragraph. The practical father gives concrete advice. The emotional mother speaks from the heart.
- The "chorus" section is the ONLY part that synthesizes — and even here, acknowledge where they would disagree
- End with a direct address to the reader: "如果你正在读这本书..."
- This should make someone cry. Write it with that level of care.

---

## Global Writing Rules

### Voice and Tone
- The narrator voice (preface, transitions, editorial notes) should be warm, respectful, and literary — like a good documentary narrator
- Each soul's voice sections must match their soul.md speech patterns exactly
- Avoid academic or clinical language. This is a family book, not a case study.

### Confidence Markers

Use these throughout the book:

| Marker | Meaning |
|--------|---------|
| (no marker) | Based on solid data from soul.md or user-provided material |
| 据家人回忆 | Based on cross-referenced memories from other souls |
| 据推测 | Inferred from personality/era/context, not directly stated |
| [素材不足] | Not enough data — explicitly invites the user or family to contribute |

### Handling Gaps

- NEVER fabricate to fill gaps. Mark them clearly.
- For each [素材不足] section, include a specific prompt question:
  > [素材不足 — 你还记得爷爷小时候住在哪里吗？他跟你说过吗？]
- Frame gaps as invitations, not failures: "这一段还等着有人来补上。"

### Length Guidelines

- Full book: Aim for the equivalent of 30-50 printed pages
- Per-soul chapter: 3-5 pages depending on available material
- Shorter is better than padded. A genuine two-page chapter beats a five-page one stuffed with filler.

### Output Format

Generate as a single Markdown document with clear chapter breaks. Include a table of contents at the top. Each chapter starts with its Chinese title and a one-line epigraph (a quote from a family member that sets the tone for that chapter).

---

## Iterative Generation

The book does not need to be generated all at once. Support:
- `--chapter [n]` to generate a single chapter
- `--section [name]` to generate a specific section
- Review and revision cycles where the user corrects facts or adds material
- Re-generation of specific chapters after new souls are added to the pantheon

After each chapter, ask: "这一章有什么需要修改或补充的吗？"
