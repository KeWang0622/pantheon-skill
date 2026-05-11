# When you'd actually use Pantheon

Eight concrete scenarios people walk in with, ordered roughly from "easiest to get started" to "deepest emotional work." Every example uses the bundled `/pantheon-demo` Wang family so you can try each one immediately without uploading any personal data.

---

## 🧭 You're facing a hard decision and you wish you could ask your whole family

> *"Should I take the job in Toronto and move away from my parents, or stay close?"*

```bash
/pantheon-council father_wangjianguo grandma_zhangxiuying mother_lishufen
```

Dad weighs the practical (salary, growth, *"做事跟解方程一样，一步步来"* — *"do things one step at a time, like solving an equation"*). Grandma weighs the emotional (*"who will make sure you eat?"*). Mom mediates between them. You get the **full spectrum** of how your family system would weigh this — not consensus, but every voice. You decide.

The council is structured (not free-form group chat): elders speak first, the decision-maker speaks last, real family disagreements are preserved rather than smoothed over.

---

## 📞 Your parents are aging and you suddenly realize you don't really know them

> *"My mom is 78. She's still here, but she's started repeating stories — and I just realized I don't actually know how she met my father."*

```bash
/pantheon-create mother
```

Pantheon walks you through structured interviews — easier than free-form recording, because the questions are designed to surface the specific layer of memory you'd otherwise lose first (origin, formative years, working-life, key turning points, day-to-day texture, things she's never told anyone). The archive grows with you. When the day comes — and it will — what you need is already there.

**This is the proactive use case the rest of the griefbot space doesn't address well.** You don't have to be in mourning. You just have to recognize that the window is open and won't be open forever.

---

## 🔁 You catch yourself doing the exact thing your parent did

> *"I went silent in the middle of an argument with my partner. Just like Dad did with Mom. I swore I wouldn't be that guy."*

```bash
/pantheon-dna
```

The Generational DNA engine traces the pattern back: *"This isn't yours alone. The root is Grandpa, who hid stomach pain for six months until he collapsed at the factory. It transformed through Dad, who hid his own diagnosis for three months before telling anyone. It's expressing differently in you — going silent in arguments — but the shape is the same: 报喜不报忧, only-share-good-news, never-the-bad."*

You can't change what you can't name. This is therapy-adjacent self-awareness work — pre-therapy or alongside it.

---

## 💌 You want a letter from someone who's gone, for a moment they should have been at

> *"Dad died eight months before my wedding. I want him there in some form. Not a clone of him — a letter, in his voice, that he could have written."*

```bash
/pantheon-letter father_wangjianguo --occasion "son's wedding"
```

The letter is generated from his actual soul archive — his catchphrases, his sentence rhythm, his way of expressing pride without ever saying *"I'm proud of you."* Pantheon refuses to invent feelings Dad never expressed, but it will surface the artifacts he left behind: *"Read what's in his desk drawer. The pencil notebook. He logged every paper you ever wrote."*

Some users include the letter in the wedding program. Some read it at the toast. Some keep it private. The letter is yours.

---

## 🕰️ You want to meet the version of your grandparent who existed before you did

> *"I knew Grandma as the woman who fed me. I never knew her as the 23-year-old textile worker who hid books under the floorboards during the Cultural Revolution."*

```bash
/pantheon-era grandma_zhangxiuying 1958
```

The Era Engine recalibrates her language, her references, and her worldview to the year you pick. Same soul model. Earlier life. The person who existed before you were a person. This is the most popular `/pantheon-era` use — meeting your young grandparents on their own terms.

Worth knowing: the older era versions of someone are typically the most surprising. You'll meet a version of your father at 25 who hadn't yet developed the catchphrases you grew up hearing.

---

## 🍳 You want to preserve a recipe that exists only in someone's hands

> *"Grandma made the red-braised pork every Spring Festival for forty-five years. She's gone. Mom tried to recreate it. It's close. Something's missing."*

```bash
/pantheon-ritual --add grandma_hongshaorou
```

The Ritual Engine captures the recipe **and the story around it** — who taught whom, what mattered, why Grandpa always said it was too sweet but ate three bowls anyway, why Mom's version is good but not quite right. The recipe is the surface artifact. The meaning is the system.

The recipe shows up in `/pantheon-legacy` automatically as a memoir chapter.

---

## 📖 You want to give your kids access to the great-grandparents they'll never meet

> *"My son was born after Dad died. I want him to know who his grandfather was — beyond the photographs."*

```bash
/pantheon-legacy father_wangjianguo --audience children
```

Legacy Writer generates an age-appropriate chapter — the stories your son can read in twenty years, told the way Dad would have told them. Not a sanitized PR version. The actual man, framed for a kid.

For an adult audience, drop the `--audience` flag and you get the full chapter — the layoffs, the silences, the funeral, the parts no one filmed.

---

## 🫀 You want to process the conversation you never got to have

> *"I never apologized. I never asked why. I never got to say I love you the way I meant it."*

```bash
/pantheon-talk father_wangjianguo
```

This is not therapy. Pantheon is honest about that and shows the crisis-line resources at the top of every dialog. But sometimes hearing what your father — reconstructed from his actual recorded words — *might* have said, in his actual voice, is enough to begin.

The honesty boundaries mean the reconstruction won't lie to you about forgiveness, or fabricate a feeling he never expressed. What it *can* do is point you back to the things he left behind, so you can hear them in the right voice.

---

## Choosing where to start

If you're new to Pantheon and not in acute grief, the highest-impact first move is **#2 — capture aging parents now**. Everyone has a closing window with someone, and most people don't realize the window is open until it's closed.

If you've already lost someone close, the highest-impact first move is **#1 — the family council**. It's a structured, dignified way to invite the person back into your decisions — without putting the entire weight of grief on a single conversation.

If you're a writer, researcher, or family historian, **#7 — legacy writer** turns Pantheon into a memoir-generation tool.

Whichever path you choose, the data lives in `~/.pantheon/` on your machine and **never leaves**.
