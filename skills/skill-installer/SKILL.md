---
name: skill-installer
description: Install and manage skills from the company Git repo into the current project. Use when a user asks to list available skills, install a skill by name, check installed skills, or install skills from the company skills repository.
---

# Skill Installer

从公司 Skills 仓库安装 Skills 到**当前项目**。

默认仓库：`git@git.chuanyuapp.com:frontend/skills.git`

## 重要：项目级安装

Skills 始终安装到当前项目的 `.agents/skills/` 目录，**不要安装到系统级目录**（如 `~/.codex/skills`、`~/.claude/skills` 等）。

检查是否已安装时，也只检查项目级 `.agents/skills/` 目录。

## Scripts

所有脚本需要网络和 git 访问权限。脚本会自动检测项目根目录（通过 `git rev-parse --show-toplevel`）。

- **列出可用 Skills**：`scripts/list-skills.py`
- **列出已安装 Skills**：`scripts/list-skills.py --installed-only`
- **JSON 格式输出**：`scripts/list-skills.py --format json`
- **安装 Skill**：`scripts/install-skill.py <name> [<name> ...]`
- **指定分支**：`scripts/install-skill.py <name> --ref develop`

## Behavior

- 默认从 `git@git.chuanyuapp.com:frontend/skills.git` 的 `master` 分支获取
- 通过 SSH 访问仓库，使用本机已配置的 git 凭据
- 安装到 `<项目根目录>/.agents/skills/<skill-name>/`
- 可通过 `--dest` 或 `SKILLS_HOME` 环境变量覆盖安装路径
- 已存在的同名 Skill 不会覆盖，需先手动删除
- 跳过以 `.` 开头的目录（如 `.git`、`.github`）

## Communication

列出 Skills 时，输出格式：
"""
公司 Skills 仓库可用列表：
  1. skill-creator - Guide for creating effective Agent Skills (已安装)
  2. some-skill - Does something useful
  3. another-skill - Another capability

输入名称即可安装，例如：安装 some-skill
"""

安装完成后告知用户 Skill 已安装到项目 `.agents/skills/` 目录。
