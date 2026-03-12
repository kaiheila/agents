---
name: init-unified-skills
description: 创建统一的多 Agent 兼容 skill 目录结构。以 .agents/skills/ 为单一源，通过软链接兼容 Claude Code (.claude/skills/) 等工具。用于初始化项目 skill 目录、配置跨 Agent 兼容性、创建软链接脚本。
---

# 初始化统一 Skill 目录

> 以 `.agents/skills/` 为单一数据源，通过软链接让所有 AI 编码工具共享同一套 skills。

## 兼容性矩阵

| 工具 | Skill 读取路径 | AGENTS.md | 对接方式 |
|------|---------------|-----------|---------|
| **Cursor** | `.agents/skills/` | ✅ 自动加载 | 原生支持，无需额外配置 |
| **Claude Code** | `.claude/skills/` | ✅ 自动加载 | 软链接 `.claude/skills/` → `.agents/skills/` |
| **Codex** | `.agents/skills/` | ✅ 自动加载 | 原生支持，无需额外配置 |
| **Gemini CLI** | `.agents/skills/` | ✅ 自动加载 | 原生支持，`.agents/skills/` 优先于 `.gemini/skills/` |
| **OpenCode** | — | ✅ 自动加载 | 通过 AGENTS.md 索引，无独立 skill 目录 |

## 目录结构

```
repo/
├─ .agents/                    # 单一数据源（提交到 Git）
│  ├─ skills/                  # 所有 skill 存放于此
│  │  ├─ <skill-name>/
│  │  │  ├─ SKILL.md           # 主文件（必需）
│  │  │  └─ *.md / scripts/    # 参考文件（可选）
│  │  └─ ...
│  └─ agents/                  # Agent 人设定义（可选）
│     └─ <agent-name>.md
│
├─ .claude/                    # Claude Code 兼容层
│  ├─ skills → ../.agents/skills/   # 软链接
│  └─ settings.local.json      # Claude Code 权限配置
│
├─ AGENTS.md                   # 所有 Agent 通用入口
├─ CLAUDE.md                   # Claude 专用补充（@AGENTS.md）
└─ scripts/
   └─ link-agent-skills.sh     # 软链接创建脚本
```

## 执行步骤

### 1. 创建 .agents 目录

```bash
mkdir -p .agents/skills .agents/agents
```

### 2. 创建软链接脚本

在项目根目录创建 `scripts/link-agent-skills.sh`（详见 [link-script.md](link-script.md)）。

脚本核心逻辑：
- 检测操作系统（Windows 用 junction，Unix 用 symlink）
- 为 `.claude/skills/` 创建指向 `.agents/skills/` 的链接
- 幂等执行：已存在则跳过

### 3. 配置 .gitignore

```gitignore
# Agent 工具本地配置（不提交）
.claude/settings.local.json

# 提交到 Git 的内容：
# - .agents/          （skill 源文件）
# - .claude/skills    （软链接，Git 会记录为链接）
# - scripts/link-agent-skills.sh
```

**注意**：Git 会将软链接记录为链接本身（非展开内容），团队成员 clone 后需运行 `scripts/link-agent-skills.sh` 重建链接。

### 4. 配置 AGENTS.md 索引

在 AGENTS.md 中添加 skill 相关说明：

```markdown
## 初始化

- 克隆后执行 `scripts/link-agent-skills.sh` -- 建立 .claude 软链接
```

## Skill 文件规范

每个 skill 存放在 `.agents/skills/<skill-name>/` 目录下：

```
<skill-name>/
├─ SKILL.md          # 主文件（必需，<500 行）
├─ reference.md      # 详细参考（可选）
├─ templates.md      # 模板（可选）
└─ scripts/          # 工具脚本（可选）
```

### SKILL.md 格式

```markdown
---
name: skill-name
description: 一句话描述功能和使用场景。包含 WHAT（做什么）和 WHEN（何时用）。
---

# Skill 标题

## 说明
核心指令，简洁可执行。

## 参考
- 详见 [reference.md](reference.md)
```

### 命名规则

- 全小写，连字符分隔：`init-agent-docs`、`state-management`
- 动词开头表示操作类：`debug-workspace-package`、`migrate-to-base`
- 名词表示知识类：`module-federation`、`event-emitter`

## 软链接 vs 目录拷贝

**始终使用软链接**，不要拷贝目录：

- 软链接保证单一数据源，修改 `.agents/skills/` 即时生效
- 拷贝会导致多份 skill 内容不同步
- Git 追踪软链接本身（几个字节），不会重复存储

### Windows 注意事项

- Windows 上使用 **junction**（目录联接），不需要管理员权限
- 命令：`cmd /c mklink /J .claude\skills .agents\skills`
- junction 对应用透明，Claude Code 正常读取

### Unix 注意事项

- 使用相对路径 symlink：`ln -s ../.agents/skills .claude/skills`
- 相对路径确保仓库移动后链接仍有效

## 团队协作流程

### 新成员 clone 后

```bash
git clone <repo>
cd <repo>
bash scripts/link-agent-skills.sh   # 建立软链接
```

### 添加新 skill

1. 在 `.agents/skills/<new-skill>/` 下创建 SKILL.md
2. 所有工具（Cursor、Claude Code、Codex、Gemini）自动识别
3. 提交到 Git

### 修改已有 skill

1. 直接编辑 `.agents/skills/<skill>/SKILL.md`
2. 所有工具立即生效（软链接指向同一目录）
3. 提交到 Git
