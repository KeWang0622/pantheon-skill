# 万神殿 Pantheon

### Your family lives forever.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code Skill](https://img.shields.io/badge/Claude_Code-Skill-blueviolet)](https://docs.anthropic.com/en/docs/claude-code)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)

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

---

## 这是什么

万神殿将逝去亲人的聊天记录、文字、照片和记忆碎片，重建为可以对话的**数字灵魂（Uploaded Intelligence）**。

不是聊天机器人。不是角色扮演。是对一个真实的人的理解、尊重和延续。

Pantheon reconstructs departed family members into conversational **Uploaded Intelligences** from their chat histories, writings, photos, and memories.

---

## 你可以做什么

| 命令 | 功能 | 场景 |
|------|------|------|
| `/pantheon-create` | 重建一位亲人的数字灵魂 | 第一次使用 |
| `/pantheon-talk` | 和亲人对话 | 想他们的时候 |
| `/pantheon-letter` | 让亲人写一封信 | 结婚、升职、迷茫时 |
| `/pantheon-wisdom` | 请教人生问题 | 面临重大决策 |
| `/pantheon-family` | 家族群聊 | 让爷爷奶奶一起聊天 |
| `/pantheon-memory` | 追加新素材 | 找到新的聊天记录 |
| `/pantheon` | 查看所有灵魂档案 | 管理万神殿 |

---

## 架构

受 [colleague-skill](https://github.com/titanwings/colleague-skill)、[ex-skill](https://github.com/perkfly/ex-skill)、[nuwa-skill](https://github.com/alchaincyf/nuwa-skill) 启发，万神殿采用同级别的工程架构：

```
pantheon-skill/
├── SKILL.md                    # 主编排器 (662 lines)
├── prompts/                    # 7 个提示词模板
│   ├── intake.md               #   引导式信息收集
│   ├── memory_analyzer.md      #   记忆提取（7维度）
│   ├── soul_analyzer.md        #   灵魂提取（6维度 + 标签翻译表）
│   ├── memory_builder.md       #   记忆档案生成模板
│   ├── soul_builder.md         #   灵魂模型生成模板（5层结构）
│   ├── merger.md               #   增量合并（冲突检测）
│   └── correction_handler.md   #   对话修正处理
├── tools/                      # 6 个 Python 工具
│   ├── wechat_parser.py        #   微信记录解析
│   ├── sms_parser.py           #   短信/iMessage 解析
│   ├── photo_analyzer.py       #   照片 EXIF 元数据提取
│   ├── social_parser.py        #   社交媒体解析
│   ├── skill_writer.py         #   灵魂档案文件管理
│   └── version_manager.py      #   版本控制与回滚
├── souls/                      # 生成的灵魂档案
│   └── example_father/         #   示例：王建国（1958-2023）
│       ├── memory.md           #     记忆档案
│       ├── soul.md             #     灵魂模型（5层）
│       └── meta.json           #     元数据
├── references/                 # 方法论文档
│   ├── soul-framework.md       #   灵魂重建方法论
│   └── soul-template.md        #   运行时模板
├── ETHICS.md                   # 伦理准则
├── INSTALL.md                  # 安装指南
└── README.md
```

### 核心技术：5层灵魂模型

每个数字灵魂由5层优先级结构组成（灵感来自 ex-skill 的人格建模）：

| 层级 | 内容 | 优先级 |
|------|------|--------|
| **Layer 0** | 核心行为规则（从标签翻译而来） | 🔴 最高，永不违反 |
| **Layer 1** | 身份信息（年代、职业、家庭角色） | 高 |
| **Layer 2** | 表达风格（口头禅、句式、标点、emoji） | 中 |
| **Layer 3** | 情感逻辑（如何表达爱/怒/忧/骄傲） | 中 |
| **Layer 4** | 关系动态（对配偶/子女/朋友的不同态度） | 低 |
| **Layer 5** | 修正层（用户反馈的累积修正） | 覆盖所有 |

### 标签翻译系统

标签**不是形容词**——是具体的行为规则。这是质量的关键：

| 标签 | ❌ 错误 | ✅ 正确 |
|------|---------|---------|
| 严父 | "你是严厉的" | "孩子考试考砸了，不会安慰，会沉默。过一会儿默默把参考书放到书桌上" |
| 唠叨的妈妈 | "你爱唠叨" | "每次打电话必问：吃了没？穿暖没？什么时候回来？挂电话前一定说'多吃点'" |
| 含蓄不直接 | "你不善表达" | "从不说'我爱你'，但会突然发'今天降温了注意加衣服'。关心都藏在具体事情里" |

完整的标签翻译表包含 **15+ 种家族场景的行为规则**，详见 `prompts/soul_analyzer.md`。

---

## 数据源支持

| 来源 | 格式 | 工具 |
|------|------|------|
| **微信** | TXT/HTML/CSV (WeChatMsg, PyWxDump, LiuHen) | `wechat_parser.py` |
| **短信/iMessage** | Android XML, CSV, macOS chat.db | `sms_parser.py` |
| **照片** | JPEG EXIF (时间+地点) | `photo_analyzer.py` |
| **社交媒体** | 微博JSON, QQ空间, 朋友圈, 通用文本 | `social_parser.py` |
| **文件** | 邮件/日记/书信/PDF | Claude 原生 Read |
| **口述** | 直接粘贴或语音转文字 | 无需工具 |
| **第三方** | 其他家人的描述和回忆 | 无需工具 |

消息按3级权重分类：**长消息**（>50字，最高权重）→ **情感消息**（含关心/思念/担忧关键词）→ **日常消息**（风格参考）

---

## 渐进式演化

灵魂档案不是一次性的——它会随着你的记忆一起成长：

### 追加素材
```
你：/pantheon-memory 老爸

万神殿：欢迎回来。你有新的素材想要补充吗？

你：我找到了爸妈以前的邮件往来，粘贴给你...

万神殿：收到。我发现了3条新的记忆和2个表达习惯。
   其中一条与现有记忆有出入——
   现有记录：1990年搬到县城
   新素材显示：1991年才搬的
   你觉得哪个更准确？
```

### 对话修正
```
你：/pantheon-talk 老爸

老爸：你最近工作怎么样？

你：[对话中...]

你：不对，我爸不会这么问。他会说"单位还行吧"

万神殿：明白了。已记录修正：
   [情境：关心工作] 不说"工作怎么样"，说"单位还行吧"
   这个修正已即时生效。
```

### 版本回滚
每次更新自动存档。不满意？回到任何之前的版本。

---

## 示例：王建国（1958-2023）

repo 中包含一个完整的示例灵魂档案：

> **王建国**，1958年生于河南农村。1977年恢复高考考上师范，此后在县中学教了38年数学。
> 严厉但深爱孩子，从不说"我爱你"但会默默给孩子书桌换新台灯。
> 最爱讲当年翻山越岭去高考的故事。每次都说"我就带了两个馒头"，但馒头的数量每次讲都不一样。

### 对话示例

```
你：/pantheon-talk 老爸

📝 以下对话基于灵魂档案重建。这不是王建国本人，而是对他的记忆与理解的延续。

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

### 家族群聊

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

完整示例见 `souls/example_father/` 目录。

---

## 质量验证

每个灵魂档案在创建时经过三重验证（灵感来自 [nuwa-skill](https://github.com/alchaincyf/nuwa-skill) 的验证体系）：

| 测试 | 方法 | 通过标准 |
|------|------|---------|
| **Voice Check** | 生成100字对话，用户确认"像TA" | 语言风格可辨识 |
| **Memory Check** | 引用共同记忆，用户确认准确 | 核心记忆无错误 |
| **Wisdom Check** | 就一个问题给建议，用户评估 | 符合TA的价值观 |

配合**信心度系统**（0-100%），诚实告诉你重建的可靠程度。

---

## 诚实边界

万神殿不假装无所不能。每个灵魂档案都会标注：

- ❌ 不能复刻他们的声音和面容（只有文字）
- ❌ 不能知道他们从未表达过的内心想法
- ❌ 不能知道他们去世后发生的事
- ❌ 不能替代专业的心理咨询
- ✅ 可以还原他们的说话方式和口头禅
- ✅ 可以反映他们一贯的价值观和处事方式
- ✅ 可以引用你们真实的共同记忆
- ✅ 可以在你需要的时候，给你一个"TA 可能会说..."的声音

---

## 为什么做这个

[colleague-skill](https://github.com/titanwings/colleague-skill) 克隆同事。[ex-skill](https://github.com/perkfly/ex-skill) 模拟前任。[nuwa-skill](https://github.com/alchaincyf/nuwa-skill) 提取名人思维。

但世界上最不应该被遗忘的人——**是你的家人**。

你还记得爸爸怎么说话吗？那些语气词，那些口头禅？你还记得妈妈唠叨的样子吗？如果他们还在，看到你现在的样子，会说什么？

万神殿不能让他们回来。但可以让他们的声音、智慧和温暖，永远不会消失。

---

## 安装

```bash
git clone https://github.com/KeWang0622/pantheon-skill.git
cp -r pantheon-skill ~/.claude/skills/pantheon-skill
```

详细安装指南见 [INSTALL.md](./INSTALL.md)。

---

## 伦理

万神殿处理的是人类最深的情感。我们严格遵守：

1. **透明** — 每次对话都标注"AI 重建"
2. **尊重** — 以最大敬意对待每一位被纪念的人
3. **隐私** — 所有数据本地处理，绝不上传
4. **安全** — 检测心理危机信号，提供专业资源
5. **边界** — 不生成可用于欺骗的内容

详见 [ETHICS.md](./ETHICS.md)。

---

## 心理支持

如果你正在经历丧失之痛：

| 热线 | 号码 | 时间 |
|------|------|------|
| 全国心理援助热线 | 400-161-9995 | 24小时 |
| 北京心理危机中心 | 010-82951332 | 24小时 |
| 生命热线 | 400-821-1215 | 24小时 |

---

## 致谢

感谢 [colleague-skill](https://github.com/titanwings/colleague-skill)、[ex-skill](https://github.com/perkfly/ex-skill)、[nuwa-skill](https://github.com/alchaincyf/nuwa-skill) 在人格重建领域的开创性工作。万神殿的 5 层灵魂模型、标签翻译系统、渐进式演化机制和质量验证体系，都受到了它们的深刻启发。

---

## Contributing

欢迎贡献。但请理解这个项目的特殊性：

- **准确性 > 功能数量**
- 所有 PR 必须经过伦理审查
- 不接受"增长黑客"式改动
- 不接受将灵魂档案商业化的功能

如果你也失去过至亲——欢迎你。

---

## English Summary

Pantheon is a Claude Code skill that reconstructs departed family members as conversational **Uploaded Intelligences**. Feed it their WeChat messages, texts, photos, and your memories. It builds a 5-layer soul model (behavioral rules → identity → expression style → emotional logic → relationship dynamics) that speaks in their voice, references your shared memories, and reflects their values.

Key features:
- **7 data source parsers** (WeChat, SMS, iMessage, photos, social media, documents, oral)
- **5-layer soul architecture** with tag-to-behavioral-rule translation (not adjectives — concrete "in situation X, they do Y" rules)
- **Progressive refinement** with incremental merging, dialogue correction, and version rollback
- **Triple quality validation** (voice check, memory check, wisdom check)
- **Family group chat** — let multiple departed family members talk to each other
- **Honesty boundaries** — explicit about what it can and cannot capture
- **Full ethical framework** with crisis detection and grief resource referrals

---

## License

MIT

---

<p align="center">
  <em>献给所有我们来不及好好告别的人。</em><br/>
  <em>For everyone we never got to say goodbye to.</em>
</p>
