# 王家 — The Wang Family (Example)

A fictional three-generation Chinese family, shipped with Pantheon so you can experience the skill end-to-end without uploading your own family's data.

> ⚠️ **Everyone in this family is fictional.** Names, dates, and stories are composites drawn from common Chinese family archetypes. Any resemblance to real people is coincidental. The dialogue and details are written to demonstrate Pantheon's behavior — not to represent any actual person.

## Family at a glance

| Slug | 姓名 | Relationship | Born — Passed | Generation |
|------|------|-------------|---------------|------------|
| `grandpa_wanglaoxiansheng` | 王老先生 | 祖父 / Grandpa | 1932 — 2015 | 1 |
| `grandma_zhangxiuying` | 张秀英 | 祖母 / Grandma | 1935 — 2020 | 1 |
| `father_wangjianguo` | 王建国 | 父亲 / Father | 1958 — 2023 | 2 |

Three souls are fully built so you can run every Pantheon command immediately:

- `/pantheon-talk father_wangjianguo` — talk to Dad
- `/pantheon-family grandma_zhangxiuying father_wangjianguo` — group chat
- `/pantheon-tree` — view the family graph
- `/pantheon-dna` — see how stubbornness propagates across three generations
- `/pantheon-ritual` — read about 外婆的红烧肉 and 春节年夜饭
- `/pantheon-legacy` — auto-generate the 王家三代 memoir

## How to load this example

```bash
/pantheon-demo
```

That copies this entire directory into `~/.pantheon/` and prints the available commands. To restore, just re-run `/pantheon-demo` — your real archives in `~/.pantheon/souls/` are never touched (demo souls install side-by-side with the `_demo_` prefix only if a conflict exists).

## What's inside

```
wang_family/
├── README.md                       # this file
├── souls/
│   ├── grandpa_wanglaoxiansheng/   # 王老先生 (1932-2015) — factory worker
│   │   ├── meta.json
│   │   ├── memory.md
│   │   └── soul.md
│   ├── grandma_zhangxiuying/       # 张秀英 (1935-2020) — textile worker
│   │   ├── meta.json
│   │   ├── memory.md
│   │   └── soul.md
│   └── father_wangjianguo/         # 王建国 (1958-2023) — mechanical engineer
│       ├── meta.json
│       ├── memory.md
│       └── soul.md
└── family/
    ├── tree.json                   # family graph (already in /family/ at root)
    ├── generational_dna.md         # three-generation trait analysis
    └── rituals/
        ├── grandma_hongshaorou.md
        └── spring_festival.md
```

The root-level `/family/` directory in this repo is the canonical version of the tree, DNA, and rituals; the same files are mirrored here so the demo example is self-contained.

## Why the Wang family

This isn't meant to be a "perfect" family. The Wangs were chosen because they hit common emotional patterns from late-20th-century Chinese family life:

- A grandfather who never finished elementary school but bought his son a set of *十万个为什么*
- A grandmother who worked thirty-two years of three-shifts at a textile factory and never once said her hands hurt
- A father who taught for thirty-eight years, expressed love through correcting your homework, and once said *"单位还行吧"* every time someone asked how work was going

If you're a Chinese-speaker, these will feel familiar. If you're not, the README of each soul includes an English mirror so you can follow along.

## License & ethics

The example souls are released under the same MIT license as Pantheon. You are welcome to:
- Use the example family to test, demo, or learn
- Fork these archetypes into your own family templates
- Cite them in papers, posts, or talks

You are not welcome to:
- Pass the example souls off as real people
- Use the example souls in any context that misrepresents the line between a real person and a fictional composite

See [`ETHICS.md`](../../ETHICS.md) for Pantheon's full ethical framework.
