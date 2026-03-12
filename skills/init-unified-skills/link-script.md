# 软链接脚本参考

> 创建软链接脚本时使用此参考。

## Bash 脚本（Unix + Git Bash on Windows）

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT_DIR"

link_skills() {
  local target="$1"   # e.g. .claude/skills
  local source="$2"   # e.g. .agents/skills

  if [ -L "$target" ] || [ -d "$target" ]; then
    echo "[skip] $target already exists"
    return
  fi

  mkdir -p "$(dirname "$target")"

  if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    # Windows: use junction (no admin required)
    local abs_source
    abs_source="$(cd "$source" && pwd -W 2>/dev/null || cd "$source" && pwd)"
    local abs_target
    abs_target="$(cd "$(dirname "$target")" && pwd -W 2>/dev/null || cd "$(dirname "$target")" && pwd)/$(basename "$target")"
    cmd //c "mklink /J \"$abs_target\" \"$abs_source\""
  else
    # Unix: relative symlink
    ln -s "../$source" "$target"
  fi

  echo "[done] $target -> $source"
}

echo "=== Linking agent skills ==="

link_skills ".claude/skills" ".agents/skills"

echo "=== All done ==="
```

## PowerShell 脚本（Windows 原生）

```powershell
$Root = Split-Path -Parent $PSScriptRoot

Push-Location $Root

function Link-Skills {
  param([string]$Target, [string]$Source)

  if (Test-Path $Target) {
    Write-Host "[skip] $Target already exists"
    return
  }

  $parent = Split-Path -Parent $Target
  if ($parent -and -not (Test-Path $parent)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
  }

  $absSource = (Resolve-Path $Source).Path
  cmd /c "mklink /J `"$Target`" `"$absSource`""
  Write-Host "[done] $Target -> $Source"
}

Write-Host "=== Linking agent skills ==="

Link-Skills ".claude\skills" ".agents\skills"

Write-Host "=== All done ==="

Pop-Location
```

## 手动创建命令

### Windows（CMD，无需管理员）

```cmd
mklink /J .claude\skills .agents\skills
```

### Windows（PowerShell）

```powershell
cmd /c "mklink /J .claude\skills .agents\skills"
```

### macOS / Linux

```bash
ln -s ../.agents/skills .claude/skills
```

## .gitignore 配置参考

```gitignore
# Agent 本地配置（不提交）
.claude/settings.local.json

# 以下内容应提交：
# .agents/           - skill 源文件
# .claude/skills     - 软链接（Git 记录链接本身）
```
