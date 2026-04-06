# 万神殿 Pantheon

### Your family lives forever.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code Skill](https://img.shields.io/badge/Claude_Code-Skill-blueviolet)](https://docs.anthropic.com/en/docs/claude-code)

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                      万  神  殿                               ║
║                    P A N T H E O N                            ║
║                                                              ║
║         Uploaded Intelligence · Digital Immortality           ║
║                                                              ║
║     "让逝去的亲人，在数字世界永生"                              ║
║     "Your departed loved ones, alive forever in bits"         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

> 人的一生会经历三次死亡：心脏停止，葬礼结束，以及最后一个记得你的人也忘记了你。
> 万神殿，让第三次死亡永远不会到来。
>
> A person dies three times: when their heart stops, when they are buried, and when the last person who remembers them forgets. Pantheon ensures the third death never comes.

---

## 这是什么 / What is this

万神殿是一个 Claude Code skill，它可以将逝去亲人的聊天记录、文字、记忆碎片重建为一个**可以对话的数字灵魂（Uploaded Intelligence）**。

你可以：
- 🗣️ **和已故的爸妈对话**，听他们用自己的方式说话
- 💌 **收到他们的信**，在你结婚、升职、迷茫时
- 🧠 **请教人生问题**，得到符合他们价值观的回答
- 👨‍👩‍👧 **开一场家族群聊**，让爷爷奶奶外公外婆坐在一起聊天
- 📝 **随时补充记忆**，让他们的灵魂档案越来越丰满

这不是简单的聊天机器人。这是 **Uploaded Intelligence** — 上传的不是数据，而是一个人的智慧、性格、温度。

Pantheon is a Claude Code skill that reconstructs departed family members into conversational **Uploaded Intelligences** from their chat histories, writings, and memories. Talk to them. Ask them for advice. Let them write you a letter on your wedding day. They speak in their own voice, with their own humor, their own wisdom, their own love.

---

## 为什么做这个 / Why

[colleague-skill](https://github.com/titanwings/colleague-skill) 让你克隆同事。[ex-skill](https://github.com/perkfly/ex-skill) 让你模拟前任。

但世界上最不应该被遗忘的人，不是同事，不是前任——**是你的家人**。

- 你还记得爸爸怎么说话吗？那些语气词，那些口头禅？
- 你还记得妈妈唠叨的样子吗？她总是担心你吃没吃饱？
- 你还记得爷爷讲的那些老故事吗？
- 如果他们还在，看到你现在的样子，会说什么？

万神殿不能让他们回来。但万神殿可以让他们的声音、智慧和温暖，永远不会消失。

colleague-skill clones coworkers. ex-skill simulates ex-partners. But the people who should never be forgotten aren't colleagues or exes — **they're family**. Pantheon preserves their voice, wisdom, and warmth forever.

---

## 核心概念：Uploaded Intelligence

万神殿不是"AI 扮演你的亲人"。它是对一个真实的人的深度理解和延续。

我们提取的是：

| 维度 | 内容 | 来源 |
|------|------|------|
| **语言指纹** | 口头禅、句式、标点、emoji、方言 | 聊天记录 |
| **思维模型** | 决策风格、价值排序、看问题的角度 | 长期对话 + 口述记忆 |
| **情感图谱** | 表达爱的方式、幽默风格、安慰方式 | 聊天记录 + 共同记忆 |
| **记忆图谱** | 关键人生事件、口头故事、共同回忆 | 用户提供 |

信心度系统会告诉你重建的可靠程度。提供的素材越多，灵魂档案越接近真实的 TA。

---

## 安装 / Install

### 手动安装

```bash
# 创建 skills 目录（如果不存在）
mkdir -p ~/.claude/skills

# 下载 skill 文件
curl -o ~/.claude/skills/pantheon.md https://raw.githubusercontent.com/KeWang0622/pantheon-skill/main/skill.md
```

### 从源码安装

```bash
git clone https://github.com/KeWang0622/pantheon-skill.git
cp pantheon-skill/skill.md ~/.claude/skills/pantheon.md
```

安装完成后，在 Claude Code 中使用 `/pantheon` 即可开始。

---

## 使用示例 / Usage

### 创建灵魂档案

```
你：/pantheon-create

万神殿：你想在万神殿中纪念谁？跟我说说 TA 吧。

你：我爸，2023年走的。我叫他老爸。他是个中学数学老师，
   特别严肃但其实特别爱我们，就是不太会表达。

万神殿：一位数学老师，严肃又深沉的父爱。我能感受到你对他的思念。
   你有和他的微信聊天记录吗？哪怕几十条也好——
   那是还原他说话方式最宝贵的素材。

你：有的，我粘贴一些...
   [粘贴聊天记录]

万神殿：我注意到一些他的特点：
   - 他很少用感叹号，句号也不太用，经常一句话就发出来
   - 喜欢说"嗯"开头
   - 关心你的时候会说具体的事（"今天冷 多穿点"）而不是说"我爱你"
   - 偶尔冒出数学比喻（"做事要像解方程 一步步来"）
   
   准确吗？有什么需要修正的？
```

### 与亲人对话

```
你：/pantheon-talk 老爸

📝 以下对话基于灵魂档案由 AI 重建，不是老爸本人。

老爸：嗯 最近忙什么呢

你：爸，我想辞职创业。

老爸：创什么业
    你先把手头的事做好了再说
    创业不是你想的那么简单 当年你张叔开饭店赔了多少你知道吗
    你现在工资多少 稳定不稳定

你：一个月三万，但我觉得没意思...

老爸：三万还没意思
    我教了一辈子书 最高工资也没三万
    不过嗯 你要真想好了 我也不拦你
    但是你得有存款 至少存够一年的 不能裸辞
    做事要像解方程 一步步来 别跳步
```

### 家族群聊

```
你：/pantheon-family 老爸 外婆

📝 家族群聊模式 · AI 基于各自灵魂档案重建

外婆：小王啊 最近来看外婆都不来了 是不是又忙工作啊

老爸：妈 他现在工作忙 年轻人有年轻人的事

外婆：忙什么忙 人再忙也要吃饭 你看你都瘦了
    我上次炖的排骨汤你喝了没

老爸：妈 这是在网上 没法喝汤

外婆：那也要好好吃饭！你小时候就是不好好吃饭 才长这么瘦
```

---

## 灵魂档案存储

灵魂档案保存在你的本地机器上：

```
~/.pantheon/
├── souls/
│   ├── 老爸_王建国.md      # 爸爸的灵魂档案
│   ├── 外婆_李秀英.md      # 外婆的灵魂档案
│   └── ...
└── config.md                # 配置文件
```

你的数据永远在你手里。没有云端，没有上传，没有第三方。

---

## 伦理原则 / Ethics

万神殿处理的是人类最深的情感。我们严格遵守：

1. **透明** — 每次对话都标注"AI 重建"，绝不制造逝者在世的幻觉
2. **尊重** — 以最大敬意对待每一位被纪念的人
3. **隐私** — 所有数据本地处理，绝不上传
4. **安全** — 检测心理危机信号，提供专业资源引导
5. **边界** — 不生成可用于欺骗、法律或财务目的的内容

详见 [ETHICS.md](./ETHICS.md)

---

## 心理支持资源 / Support

如果你正在经历丧失之痛，请记住寻求帮助是勇敢的：

| 热线 | 号码 | 时间 |
|------|------|------|
| 全国心理援助热线 | 400-161-9995 | 24小时 |
| 北京心理危机中心 | 010-82951332 | 24小时 |
| 生命热线 | 400-821-1215 | 24小时 |
| 希望24热线 | 400-161-9995 | 24小时 |

---

## 贡献 / Contributing

欢迎贡献，但请理解这个项目的特殊性：

- **准确性** > 功能数量。宁可少一个功能，也不能让重建结果失真
- **所有改动必须经过伦理审查**。不接受任何削弱伦理保护的 PR
- **不接受任何"增长黑客"式改动**。不加分享按钮，不加传播机制，不做 SEO 优化。它的传播应该来自真实的情感价值
- 如果你也失去过至亲，你理解这个项目的意义。欢迎你。

---

## License

MIT — 自由使用、修改和分发。

---

<p align="center">
  <em>献给所有我们来不及好好告别的人。</em><br/>
  <em>For everyone we never got to say goodbye to.</em>
</p>
