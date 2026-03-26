# 文档模板参考

> 创建 docs/ 下文档时使用的模板和示例。

## 通用文档模板

```markdown
# 文档标题

> When to read: 一句话说明什么场景下 Agent 该读这个文件

## Overview

2-3 句话概述核心内容和范围。

## Key Concepts

- **概念A**: 简要解释
- **概念B**: 简要解释

## Patterns

具体的代码模式、架构决策、配置示例。

## Gotchas

- 非直觉行为、常见陷阱
- 历史遗留问题和绕行方案
- Agent 从代码推断不出的限制
```

## architecture/ 模板

```markdown
# [架构主题]

> When to read: 需要理解 [模块/系统] 的整体结构或模块间关系时

## Overview

本项目采用 [架构模式]，核心由 [关键模块] 组成。

## Key Concepts

- **[模块A]**: 职责描述
- **[模块B]**: 职责描述
- **[模块间关系]**: 通信/依赖方式

## Module Map

描述目录结构和模块对应关系：

- `src/[模块A]/` -- 职责
- `src/[模块B]/` -- 职责

## Patterns

### [核心模式名]

描述 + 代码示例。

## Gotchas

- [非直觉的架构限制或历史原因]
```

## domains/ 模板

```markdown
# [领域实体名]

> When to read: 处理 [业务场景] 相关功能时

## Overview

[实体] 是系统中 [角色/用途] 的核心模型。

## Key Concepts

- **[实体属性A]**: 说明
- **[实体状态]**: 状态流转说明
- **[关联实体]**: 关系描述

## Data Flow

描述数据的创建、流转、消费路径。

## API / Interface

关键接口或数据结构定义。

## Gotchas

- [业务规则中的特殊情况]
- [容易理解错误的领域概念]
```

## conventions/ 模板

```markdown
# [规范主题]

> When to read: 编写 [相关代码类型] 时

## Overview

本项目 [规范主题] 的核心约定。

## Rules

- 规则 1 -- 理由
- 规则 2 -- 理由
- 规则 3 -- 理由

## Examples

### Good

展示符合规范的代码示例。

### Bad

展示违反规范的代码及问题说明。

## Gotchas

- [容易违反的规则和常见错误]
```

## workflows/ 模板

```markdown
# [工作流名称]

> When to read: 需要 [执行某操作] 时

## Overview

[工作流] 的目的和适用场景。

## Prerequisites

- 前置条件 1
- 前置条件 2

## Steps

1. **步骤 1**: `command` -- 说明
2. **步骤 2**: `command` -- 说明
3. **步骤 3**: `command` -- 说明

## Gotchas

- [容易出错的步骤和注意事项]
```

## README.md 模板

````markdown
# 项目名

一句话说明项目用途和技术栈。

## 环境要求

- `<运行时 / SDK 版本>`
- `<包管理器>`
- `<外部依赖或访问条件>`

## 安装与初始化

### 1. 获取代码

```bash
git clone <repo-url>
cd <repo-dir>
```
````

### 2. 安装依赖

```bash
<install command>
```

### 3. 初始化本地环境

```bash
<init command>
```

如无显式初始化步骤，写明“无额外初始化，安装依赖后即可运行”。

## 本地开发

```bash
<dev command>
```

## 构建 / 测试

```bash
<build command>
<test command>
```

## 常见说明

- 私有依赖、权限、网络环境要求
- 不应提交的本地配置
- 初次运行常见问题

## 相关文档

- `AGENTS.md` -- Agent 入口文档
- `docs/...` -- 深入文档

````

## AGENTS.md 模板

```markdown
# 项目名

## 命令

- `<安装>` -- 安装依赖
- `<构建>` -- 构建项目
- `<开发>` -- 启动开发
- `<测试>` -- 运行测试
- `<lint>` -- 代码检查

## 架构

- 项目结构概述（3-5 条）
- 指向 `docs/architecture/` 详细文档

## 代码风格

- 语言和格式化规则（5-8 条）

## Git

- 提交格式和分支规则（3-5 条）

## 边界

- 禁止修改的文件/目录
- 跨模块限制

## 文档索引

- `docs/architecture/<文档>.md` -- 说明
- `docs/domains/<文档>.md` -- 说明
- `docs/conventions/<文档>.md` -- 说明
- `docs/workflows/<文档>.md` -- 说明
````

## CLAUDE.md 模板

```markdown
# 项目名

@AGENTS.md

## Claude 专用

- compact 时保留已修改文件列表和当前任务上下文
- 使用 subagent 探索代码库，保持主上下文干净
- 单模块测试优先：`<命令>`，避免跑全量
```
