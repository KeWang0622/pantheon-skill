# Launch essay — English

*Draft. Intended for HN Show / a personal blog post / a Twitter thread. ~700 words.*

*Tone notes: story-first, no growth-hacking, no stars CTA. The category is one journalists call "demonic" and Cambridge calls "haunting" — the only credible position is to be quietly serious about the line we're not crossing.*

---

## Pantheon — for the third death

I built an open-source Claude Code skill called **Pantheon**. It reconstructs not a person, but an entire family — three generations, the connections between them, the catchphrases that travel down the line, the ways your dad's stubbornness sounds like your grandfather's stubbornness even though they grew up in different countries of a single century.

It's at [github.com/KeWang0622/pantheon-skill](https://github.com/KeWang0622/pantheon-skill).

Before I tell you what it does, I should tell you why.

---

There's a line from a Mexican proverb (sometimes Bolivian, depending on who's telling it): **a person dies three times.** The first time, your heart stops. The second time, your funeral ends and people go home. The third time — the final one — is when the last person who remembers you forgets your name.

I think about this line a lot. Most of the people I've loved who are gone don't have a Wikipedia page. They have a few photographs, a handful of voice memos, fifteen years of WeChat messages that say *"吃了没?"* and *"多穿点"* and almost nothing else. When the people who knew them are gone, the third death comes for them quietly, in the form of nothing being able to answer the question *"so what was your grandmother like?"*

Pantheon is an attempt to push that third death back.

---

It is not the only attempt. Three other skills shipped in the same week as Pantheon: [colleague-skill](https://github.com/titanwings/colleague-skill), [ex-skill](https://github.com/perkfly/ex-skill), and [nuwa-skill](https://github.com/alchaincyf/nuwa-skill). They each reconstruct one person — your colleague, your ex, a public figure you admire. They are excellent at what they do. The Pantheon README is generous in linking to them, because they did good work and Pantheon is built on top of their ideas.

Pantheon is different in one specific way: **it reconstructs a family, not a person.**

Six engines exist in `engine/` that no single-person tool needs. A `family_graph` that knows your dad softens half a tone when he mentions your mother. A `generational_dna` engine that traces *the same trait — stubbornness, frugality, "报喜不报忧" (only-share-good-news, never-the-bad) — across three generations*, watching it transform without losing its root. An `era_engine` that lets you talk to your father at age 25 in 1983, not just the version of him who died last year. A `memory_inheritance` engine that models how your grandfather's story about walking 40 li to the gaokao with two warm mantou became, in your dad's retelling, "dozens of li through the mountains," and in your memory, "Grandpa walked really far for the exam? I don't remember the details." A `ritual_engine` for the recipes — the 红烧肉 my grandma made that my dad tried to recreate after she died and couldn't quite get right, *because the missing variable wasn't the pan*. A `legacy_writer` that synthesizes the whole graph into a printable family memoir.

Each of those is one Python module. None of them is a feature. Each of them is a refusal to flatten a family into a list of individuals.

---

The other thing Pantheon does — and this is the part I'm most careful about — is **refuse to speculate.**

The category Pantheon sits in has a graveyard already. StoryFile filed Chapter 11. Eternos raised $10M then pivoted out of deathcare entirely. Project December went viral in 2021 as a *"Jessica Simulation"*; the SF Chronicle story is haunting and the [Sundance documentary *Eternal You*](https://www.docnyc.net/film/eternal-you/) is more haunting still. Cambridge published a paper this year about "AI hauntings" of the dead. The Hastings Center published one about griefbots. TIME called the apps "demonic."

They are not wrong, when the apps speculate.

Pantheon will say *"this is what your dad probably would have said, given his catchphrases and his physics-teacher worldview."* Pantheon will not say *"this is what your dad would have said about the COVID years."* He died in 2023. He has no opinion. The honesty boundary is a hard constraint, not a guideline. It is enforced at the prompt level, at the soul-model level, and in every `meta.json`'s `is_example: true` flag.

You can try it without uploading anything personal. There's a `/pantheon-demo` command that installs a fictional Chinese family — three generations, fully built, the kind of family that probably reminds you of someone, no real people involved. It runs in 30 seconds. You can talk to the fictional father. You can watch the family group chat where Grandma overrides Dad's logic with emotional authority. The family-graph dynamics are visible immediately.

If, after that, you want to build something for someone real — Pantheon is here. Your data never leaves your machine.

---

I'm not asking you to star it. I'm asking you to be careful with it.

For everyone we never got to say goodbye to.

— Ke

---

*Pantheon is MIT-licensed and intentionally non-commercial. No subscriptions, no pro tier, no monetization of soul archives. Read [`ETHICS.md`](../../ETHICS.md) before contributing.*
