---
name: skill-creator
description: Guide for creating effective Agent Skills. Covers design principles, SKILL.md spec, YAML frontmatter, description writing, resource classification, progressive disclosure patterns, tool permissions, and troubleshooting. Use when creating, reviewing, or optimizing Agent Skills.
---

# Agent Skills 创建最佳实践

创建高质量、可发现、易维护的 Agent Skills。

## 核心设计原则

### 上下文窗口是公共资源

Skills 与系统提示、对话历史、其他 Skills 元数据共享上下文窗口。每一行内容都有 token 成本。

**默认假设：AI Agent 已经非常聪明。** 只添加 Agent 不具备的知识。对每段内容自问：
- "Agent 真的需要这个解释吗？"
- "这段内容值得它的 token 成本吗？"

**优先用简洁示例代替冗长解释。**

### 自由度匹配

根据任务的脆弱性和可变性，匹配不同级别的指令粒度：

| 自由度 | 适用场景 | 形式 |
|-------|---------|------|
| **高** | 多种方案均可、依赖上下文判断 | 文本指导 |
| **中** | 有推荐模式、允许一定变化 | 伪代码或带参数的脚本 |
| **低** | 操作脆弱易错、一致性关键 | 具体脚本、少量参数 |

类比：窄桥悬崖需要严格护栏（低自由度），开阔平原允许多条路线（高自由度）。

### 保持专注

每个 Skill 解决一个明确的问题领域。宽泛的 Skill 难以触发、难以维护。

## Skill 结构

### 目录布局

```
skill-name/
├── SKILL.md              # 必需：主定义文件
├── scripts/              # 可选：确定性可执行脚本
│   └── rotate_pdf.py
├── references/           # 可选：按需加载的参考文档
│   └── schema.md
└── assets/               # 可选：输出用素材（不进入上下文）
    └── template.html
```

### 三类资源的区分

| 类型 | 用途 | 何时使用 | 示例 |
|------|------|---------|------|
| **scripts/** | 确定性执行代码 | 同样的代码反复被重写；需要可靠执行 | `rotate_pdf.py`, `merge.py` |
| **references/** | 按需加载的领域知识 | Agent 执行时需要参考的文档；不必常驻上下文 | `schema.md`, `api_docs.md` |
| **assets/** | 输出用素材 | 最终产出中使用的文件；不需要读入上下文 | `logo.png`, `template.html` |

**关键区别**：scripts 被执行，references 被阅读，assets 被复制/引用。

### 不应包含的文件

Skill 只包含 AI Agent 完成任务所需的文件。**不要**创建：

- README.md、INSTALLATION_GUIDE.md、CHANGELOG.md
- Version History 段落
- 面向人类的使用说明或安装指南
- 关于创建过程的说明文档

## SKILL.md 规范

### YAML Frontmatter

```yaml
---
name: your-skill-name
description: 功能描述 + 使用时机 + 触发关键词
---
```

| 字段 | 要求 | 说明 |
|-----|------|------|
| `name` | 必需 | 仅小写字母、数字、连字符，最多 64 字符 |
| `description` | 必需 | 功能和使用时机，最多 1024 字符 |
| `allowed-tools` | 可选 | 限制可用工具（如 `Read, Grep, Glob`） |

**命名规则**：小写连字符格式，动词优先，简短明确（如 `pdf-editor`、`gh-address-comments`）。

### allowed-tools 字段

限制 Skill 激活时 Agent 可使用的工具：

```yaml
allowed-tools: Read, Grep, Glob
```

适用于只读操作、安全敏感工作流、限定范围的任务。

### Description 编写

`description` 是 Agent 发现 Skill 的**唯一依据**——所有"何时使用"的信息都必须在这里，而非 body 中（body 在触发后才加载）。

✅ **好的 Description**：
```yaml
description: Extract text, fill forms, merge PDFs. Use when working with PDF files, forms, or document extraction. Requires pypdf and pdfplumber.
```
- 说明做什么 + 何时用 + 触发关键词 + 文件类型

❌ **差的 Description**：
```yaml
description: Helps with data
```
- 太笼统、缺少触发词、无法被正确匹配

**避免冲突**——相似 Skills 必须用不同的领域关键词区分：
```yaml
# Skill 1
description: Analyze sales data in Excel files. Use for sales reports and revenue tracking.
# Skill 2
description: Analyze log files and system metrics. Use for performance monitoring and debugging.
```

### Body 内容结构

使用祈使语气编写。核心结构：

```markdown
# Skill 名称

简要说明。

## Instructions
分步指导 Agent **如何执行**，而非实现原理。

## Examples
具体使用示例和代码。
```

可选增加 `## Requirements`（外部依赖）等段落。

## 渐进式披露

Skills 使用三级加载机制管理上下文：

1. **元数据（name + description）** — 始终在上下文中（~100 词）
2. **SKILL.md body** — 触发后加载（控制在 500 行以内）
3. **bundled resources** — Agent 按需加载（无限制）

### 披露模式

**模式 1：高层指南 + 引用文件**

```markdown
## Quick Start
基础用法...

For form filling, see [FORMS.md](FORMS.md).
For API reference, see [REFERENCE.md](REFERENCE.md).
```

**模式 2：按领域分组**

```
bigquery-skill/
├── SKILL.md
└── references/
    ├── finance.md
    ├── sales.md
    └── product.md
```

用户问销售指标时，Agent 只读 `sales.md`。

**模式 3：条件展开**

```markdown
## Creating Documents
Use docx-js. See [DOCX-JS.md](DOCX-JS.md).

## Editing Documents
For simple edits, modify XML directly.
**For tracked changes**: See [REDLINING.md](REDLINING.md)
```

### 关键规则

- 引用文件保持一层深度，从 SKILL.md 直接链接
- 超过 100 行的引用文件加目录（TOC）
- 超过 10k 词的引用文件在 SKILL.md 中提供 grep 搜索模式
- 信息不要在 SKILL.md 和引用文件中重复

## 创建流程

### 1. 理解使用场景

明确 Skill 要解决的具体问题和使用方式。收集或设想用户的典型请求。

### 2. 规划可复用资源

分析每个使用场景，识别需要的 scripts、references、assets：
- 反复重写的代码 → `scripts/`
- 执行时需要的领域知识 → `references/`
- 输出中使用的模板/素材 → `assets/`

### 3. 编写 SKILL.md

先写 frontmatter（精心打磨 description），再写 body（简洁的操作指导）。

### 4. 验证

- 检查 YAML frontmatter 格式（`---` 分隔符、空格非 Tab）
- 用匹配 description 的问题测试触发
- 验证文件路径使用正斜杠（`scripts/helper.py` ✅ 而非 `scripts\helper.py` ❌）
- 确认 Skills 之间无冲突

### 5. 迭代

在真实任务中使用，发现问题后改进 SKILL.md 和资源文件。

## Examples

### 示例 1：只读 Skill

```yaml
---
name: code-reviewer
description: Review code for best practices, potential bugs, and security issues. Use when reviewing code, checking PRs, or analyzing code quality.
allowed-tools: Read, Grep, Glob
---

# Code Reviewer

## Instructions

1. Read the target files
2. Check for: code structure, error handling, performance, security, test coverage
3. Provide actionable feedback with severity levels
```

### 示例 2：带脚本的多文件 Skill

```
pdf-processing/
├── SKILL.md
├── references/
│   ├── FORMS.md
│   └── API.md
└── scripts/
    ├── extract.py
    └── merge.py
```

**SKILL.md** 内容：

```yaml
---
name: pdf-processing
description: Extract text, fill forms, merge PDFs. Use when working with PDF files, forms, or document extraction. Requires pypdf and pdfplumber.
---
```

```markdown
# PDF Processing

## Quick Start

Extract text with pdfplumber:
  import pdfplumber
  with pdfplumber.open("doc.pdf") as pdf:
      text = pdf.pages[0].extract_text()

For form filling, see [FORMS.md](references/FORMS.md).
For API details, see [API.md](references/API.md).

## Requirements
  pip install pypdf pdfplumber
```

## 常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| Agent 不使用 Skill | description 太笼统；YAML 语法错误 | 加入具体触发词；检查 `---` 分隔符 |
| Skill 加载但不工作 | 文件路径用了反斜杠；缺少依赖 | 使用正斜杠；在 description 中声明依赖 |
| 多个 Skills 冲突 | description 关键词重叠 | 用不同领域关键词明确区分使用场景 |
| 上下文溢出 | SKILL.md 过长；信息重复 | 拆分到 references/；删除冗余内容 |
