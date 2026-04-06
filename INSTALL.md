# 安装指南 / Installation Guide

## 快速安装（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/KeWang0622/pantheon-skill.git

# 2. 复制到 Claude Code skills 目录
mkdir -p ~/.claude/skills
cp -r pantheon-skill ~/.claude/skills/pantheon-skill

# 3.（可选）安装照片分析依赖
pip install Pillow
```

安装完成后，在 Claude Code 中输入 `/pantheon-create` 即可开始。

## 手动安装

如果只想安装核心 skill 文件：

```bash
mkdir -p ~/.claude/skills/pantheon-skill/{prompts,tools,references}

# 下载核心文件
curl -o ~/.claude/skills/pantheon-skill/SKILL.md \
  https://raw.githubusercontent.com/KeWang0622/pantheon-skill/main/SKILL.md

# 下载 prompts
for f in intake memory_analyzer soul_analyzer soul_builder memory_builder merger correction_handler; do
  curl -o ~/.claude/skills/pantheon-skill/prompts/${f}.md \
    https://raw.githubusercontent.com/KeWang0622/pantheon-skill/main/prompts/${f}.md
done

# 下载 tools
for f in wechat_parser sms_parser photo_analyzer social_parser skill_writer version_manager; do
  curl -o ~/.claude/skills/pantheon-skill/tools/${f}.py \
    https://raw.githubusercontent.com/KeWang0622/pantheon-skill/main/tools/${f}.py
done

# 下载参考文件
for f in soul-framework soul-template; do
  curl -o ~/.claude/skills/pantheon-skill/references/${f}.md \
    https://raw.githubusercontent.com/KeWang0622/pantheon-skill/main/references/${f}.md
done
```

## 系统要求

- **Claude Code** — 任何版本
- **Python 3.9+** — 用于数据解析工具
- **Pillow**（可选）— 仅用于照片 EXIF 元数据提取

## 数据准备建议

在创建灵魂档案之前，建议先准备好以下素材：

### 微信聊天记录导出

推荐使用以下工具导出：
- [WeChatMsg](https://github.com/LC044/WeChatMsg) — 最流行的微信记录导出工具
- [PyWxDump](https://github.com/xaoyaoo/PyWxDump) — 微信数据库解密工具
- [LiuHen](https://github.com/Jinnrry/LiuHen) — 微信消息导出

导出为 txt 或 csv 格式即可。

### 短信 / iMessage

- **iPhone**: 使用 iMazing 或 PhoneView 导出
- **Mac iMessage**: 直接读取 `~/Library/Messages/chat.db`
- **Android**: 使用 SMS Backup & Restore 导出为 XML

### 照片

将包含与亲人相关的照片放在一个文件夹中。工具会自动提取 EXIF 时间和地点信息。

### 其他文本

邮件、日记、书信、朋友圈截图等，直接提供文件路径或粘贴文本即可。

## 验证安装

安装后在 Claude Code 中输入：

```
/pantheon
```

如果看到万神殿欢迎界面，说明安装成功。
