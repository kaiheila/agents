---
name: skill-publisher
description: Publish a skill from the current project to the company skills repo. Use when a user wants to publish, share, submit, or push a skill to the company repository for others to install.
---

# Skill Publisher

将当前项目中的 Skill 发布到公司 Skills 仓库。

默认仓库：`git@git.chuanyuapp.com:frontend/skills.git`

## 重要：发布流程

发布不会直接合入 master，而是创建分支并推送，由团队通过 Merge Request 审核后合入。

## Scripts

- **发布 Skill**：`scripts/publish-skill.py <skill-name>`
- **发布并更新已有 Skill**：`scripts/publish-skill.py <skill-name> --update`
- **指定来源目录**：`scripts/publish-skill.py <skill-name> --src <path>`
- **指定目标分支**：`scripts/publish-skill.py <skill-name> --target master`

## Behavior

- 默认从当前项目的 `.agents/skills/<skill-name>/` 读取 Skill
- 发布前自动验证：目录存在、SKILL.md 存在、frontmatter 格式正确
- 创建 `publish/<skill-name>` 分支，推送到远程仓库
- 利用 GitLab push options 自动创建 Merge Request
- 已存在同名 Skill 时默认拒绝，加 `--update` 允许覆盖更新

## Communication

发布成功后输出 Merge Request 链接，提示用户去审核合入。

发布失败时说明具体原因（验证失败、权限不足、分支已存在等）。
