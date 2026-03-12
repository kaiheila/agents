---
name: init-mcp-config
description: 创建统一的项目级 MCP 服务器配置。以 .agents/mcp.json 为单一源，LLM 按需转换为各 AI 工具的原生格式（Cursor、Claude Code、Gemini CLI、Codex、OpenCode）。用于初始化 MCP 配置、添加 MCP 服务器、跨工具同步 MCP 配置。
---

# 统一 MCP 配置

> 以 `.agents/mcp.json` 为单一配置源，LLM 根据当前工具自动转换为对应格式。

## 核心思路

各 AI 编码工具的 MCP 配置格式互不相同，维护多份配置成本高。解决方案：

1. **`.agents/mcp.json`** 作为唯一配置源，定义项目需要的所有 MCP 服务器
2. LLM 读取此文件后，按当前工具的格式生成对应配置
3. 本地 MCP 服务器代码放在 `mcp-servers/` 目录（可选）

## 目录结构

```
project/
├─ .agents/
│  ├─ mcp.json              # 统一 MCP 配置（单一源）
│  ├─ skills/
│  └─ agents/
│
├─ mcp-servers/              # 本地 MCP 服务器（可选）
│  ├─ <server-a>/
│  │  ├─ index.js
│  │  └─ package.json
│  └─ <server-b>/
│     └─ index.js
│
├─ .cursor/mcp.json          # Cursor 配置（自动生成，可提交）
├─ .mcp.json                 # Claude Code 项目配置（自动生成）
├─ .gemini/settings.json     # Gemini CLI 配置（自动生成）
└─ src/
```

## .agents/mcp.json 格式

```json
{
  "$schema": "https://agents.md/mcp.json",
  "servers": {
    "<server-name>": {
      "type": "local",
      "command": "<executable>",
      "args": ["<arg1>", "<arg2>"],
      "env": {
        "<ENV_VAR>": "<value or ${ENV_VAR}>"
      },
      "enabled": true
    },
    "<remote-server>": {
      "type": "remote",
      "url": "https://example.com/mcp",
      "headers": {
        "Authorization": "Bearer ${TOKEN}"
      },
      "enabled": true
    }
  }
}
```

### 字段说明

| 字段 | 必需 | 说明 |
|------|------|------|
| `type` | 否 | `local`（默认）或 `remote` |
| `command` | local 必需 | 可执行文件路径 |
| `args` | 否 | 命令参数数组 |
| `env` | 否 | 环境变量，`${VAR}` 表示引用系统环境变量 |
| `url` | remote 必需 | 远程 MCP 服务端点 |
| `headers` | 否 | HTTP 请求头 |
| `enabled` | 否 | `false` 可临时禁用 |

### 示例

```json
{
  "servers": {
    "web-search": {
      "command": "node",
      "args": ["./mcp-servers/web-search/index.js"]
    },
    "browser": {
      "command": "node",
      "args": ["./mcp-servers/browser/index.js"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp"
    }
  }
}
```

## 各工具格式对照

LLM 读取 `.agents/mcp.json` 后，按以下规则转换：

### Cursor — `.cursor/mcp.json`

```json
{
  "mcpServers": {
    "<name>": {
      "command": "<command>",
      "args": ["<args>"],
      "env": { "<key>": "<value>" }
    },
    "<remote>": {
      "url": "<url>",
      "headers": { "<key>": "<value>" }
    }
  }
}
```

转换规则：`servers` → `mcpServers`，其余字段直接映射，去掉 `type` 和 `enabled`。

### Claude Code — `.mcp.json`（项目根目录）

```json
{
  "mcpServers": {
    "<name>": {
      "command": "<command>",
      "args": ["<args>"],
      "env": { "<key>": "<value>" }
    }
  }
}
```

转换规则：同 Cursor，`servers` → `mcpServers`。远程服务用 `url` 字段。

### Gemini CLI — `.gemini/settings.json`

```json
{
  "mcpServers": {
    "<name>": {
      "command": "<command>",
      "args": ["<args>"],
      "env": { "<key>": "<value>" }
    }
  }
}
```

转换规则：同 Cursor，`servers` → `mcpServers`。`${VAR}` 语法 Gemini 原生支持。

### Codex — `.codex/config.toml`

```toml
[mcp_servers.<name>]
command = "<command>"
args = ["<args>"]
env = { "<key>" = "<value>" }
```

转换规则：JSON → TOML，`servers` → `mcp_servers`，每个 server 一个 TOML table。

### OpenCode — `opencode.json`

```json
{
  "mcp": {
    "<name>": {
      "type": "local",
      "command": ["<command>", "<args>"],
      "enabled": true,
      "environment": { "<key>": "<value>" }
    },
    "<remote>": {
      "type": "remote",
      "url": "<url>",
      "enabled": true,
      "headers": { "<key>": "<value>" }
    }
  }
}
```

转换规则：`servers` → `mcp`，`command` + `args` 合并为 `command` 数组，`env` → `environment`。

## 转换速查表

| 源字段 (.agents/mcp.json) | Cursor / Claude / Gemini | Codex | OpenCode |
|---|---|---|---|
| `servers` | `mcpServers` | `mcp_servers` | `mcp` |
| `command` | `command` | `command` | `command[0]` |
| `args` | `args` | `args` | `command[1..]` |
| `env` | `env` | `env` | `environment` |
| `type: remote` | 用 `url` 字段 | 用 `url` 字段 | `type: "remote"` |
| `enabled: false` | 忽略该条目 | `enabled = false` | `enabled: false` |

## 执行步骤

### 1. 创建配置文件

```bash
mkdir -p .agents
```

在 `.agents/mcp.json` 中声明项目所需的 MCP 服务器。

### 2. 创建本地 MCP 服务器（可选）

```bash
mkdir -p mcp-servers/<server-name>
```

本地服务器放在 `mcp-servers/` 下，`command` 使用相对路径引用。

### 3. 生成工具配置

告诉 LLM：

> 读取 `.agents/mcp.json`，按当前工具格式生成 MCP 配置。

LLM 会自动判断当前运行的工具（Cursor / Claude Code / Gemini / Codex / OpenCode），并输出到对应位置。

### 4. .gitignore 配置

```gitignore
# MCP 配置中的密钥不要提交
# 使用 ${ENV_VAR} 引用环境变量代替硬编码

# 各工具自动生成的配置（可选提交）
# .cursor/mcp.json
# .mcp.json
# .gemini/settings.json
```

## 注意事项

- **密钥处理**：env 中使用 `${ENV_VAR}` 引用环境变量，不要硬编码密钥
- **相对路径**：本地 MCP 服务器路径使用 `./mcp-servers/...` 相对于项目根目录
- **enabled 字段**：设为 `false` 可临时禁用，无需删除配置
- **按需生成**：不必预生成所有工具的配置，谁用谁生成即可
