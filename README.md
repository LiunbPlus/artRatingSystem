# artRatingSystem 工具与 Skills 指南

本文档只介绍仓库中的 `tools/` 工具脚本和 `.agents/skills/` 项目 Skills，包括各文件的用途、调用方法，以及将 Skill 导入 Codex、Trae 和 Claude Code 的方式。

## 目录

```text
artRatingSystem/
├─ tools/
│  ├─ start.bat
│  ├─ start.sh
│  ├─ stop.sh
│  ├─ download.bat
│  ├─ download.sh
│  ├─ upload.bat
│  └─ upload.sh
└─ .agents/
   └─ skills/
      └─ art-rating-system-maintainer/
         ├─ SKILL.md
         └─ agents/
            └─ openai.yaml
```

所有 `tools/` 脚本都会先进入脚本所在目录，再通过 `cd ..` 返回项目根目录，因此可以从项目根目录调用，也可以直接在文件管理器中运行 Windows 批处理脚本。

## tools 工具脚本

### 前置准备

运行服务前应已准备好：

- 后端 Windows 虚拟环境：`backend/venv/Scripts/python.exe`
- 后端 Linux 虚拟环境：`backend/venv/bin/python`
- 前端依赖：`frontend/node_modules/`
- 可用的 `npm` 命令

Git 同步脚本要求：

- 当前目录属于有效的 Git 仓库；
- 已配置名为 `origin` 的远端；
- 当前账号有拉取或推送 `main` 分支的权限；
- 推送前已经确认工作区中没有不应提交的文件。

### `start.bat`

Windows 服务启动脚本。

作用：

- 打开名为 `Art Rating System - Backend` 的 CMD 窗口；
- 在 `backend/` 中使用 `backend/venv/Scripts/python.exe main.py` 启动后端；
- 打开名为 `Art Rating System - Frontend` 的 CMD 窗口；
- 在 `frontend/` 中执行 `npm.cmd run dev` 启动前端；
- 两个服务窗口相互独立，关闭某个窗口即可结束该窗口中的服务。

从项目根目录运行：

```bat
tools\start.bat
```

也可以在 Windows 文件管理器中双击 `tools/start.bat`。

该脚本只负责启动，不会创建虚拟环境，也不会安装 Python 或 npm 依赖。

### `start.sh`

Linux 服务启动脚本。

作用：

- 使用 `backend/venv/bin/python -m uvicorn` 启动后端；
- 使用 `npm run dev` 启动前端；
- 通过 `setsid` 将前后端放到后台运行；
- 将 PID 写入 `logs/backend.pid` 和 `logs/frontend.pid`；
- 将日志写入 `logs/backend.log` 和 `logs/frontend.log`；
- 如果 PID 文件对应的进程仍然存在，则不会重复启动。

首次使用时确保脚本可执行：

```bash
chmod +x tools/start.sh tools/stop.sh
```

从项目根目录运行：

```bash
./tools/start.sh
```

启动后可查看日志：

```bash
tail -f logs/backend.log
tail -f logs/frontend.log
```

### `stop.sh`

Linux 服务停止脚本，与 `start.sh` 配套使用。

作用：

- 读取 `logs/frontend.pid` 和 `logs/backend.pid`；
- 优先正常终止对应进程组；
- 等待进程退出，必要时再强制结束；
- 删除已经处理的 PID 文件；
- 只适用于由 `tools/start.sh` 启动并记录 PID 的服务。

调用方式：

```bash
./tools/stop.sh
```

### `download.bat`

Windows Git 拉取脚本。

实际执行：

```bash
git pull origin main
```

调用方式：

```bat
tools\download.bat
```

该操作会把远端 `main` 合并到当前分支。工作区存在未提交改动时可能产生拒绝或冲突，应先运行 `git status`。

### `download.sh`

Linux Git 拉取脚本，作用与 `download.bat` 相同。

调用方式：

```bash
./tools/download.sh
```

实际执行：

```bash
git pull origin main
```

### `upload.bat`

Windows Git 提交和推送脚本。

依次执行：

```bash
git add *
git commit -m "auto commit 2"
git push origin main
```

调用方式：

```bat
tools\upload.bat
```

注意：该脚本会直接暂存、提交和推送，不提供确认步骤。`git add *` 的暂存范围也不如手动指定文件精确，使用前必须检查：

```bash
git status --short
git diff
```

### `upload.sh`

Linux Git 提交和推送脚本。

依次执行：

```bash
git add *
git commit -m "auto commit"
git push origin main
```

调用方式：

```bash
./tools/upload.sh
```

该脚本同样会直接提交和推送。建议在正式使用前手动确认变更范围；需要准确提交信息或只提交部分文件时，应直接使用 Git 命令，不要使用该脚本。

## 项目 Skills

仓库当前包含一个项目 Skill：`art-rating-system-maintainer`。

### `art-rating-system-maintainer`

位置：

```text
.agents/skills/art-rating-system-maintainer/
├─ SKILL.md
└─ agents/openai.yaml
```

作用：

- 接收本项目的修改、修复、审查、文档和维护请求；
- 修改前检查工作区并执行 `git pull origin main`；
- 根据任务区分后端、前端、全栈、部署脚本和文档范围；
- 后端任务禁止无关地读取前端文件；
- 告知用户本次修改将在哪些目录和文件中进行；
- 约束后端分层、数据库迁移、依赖和敏感文件处理；
- 按任务范围执行检查，确认无误后暂存本次文件、提交并推送远端 `main`；
- 禁止强推、覆盖用户改动或为了拉取而丢弃工作区内容。

`SKILL.md` 是主要指令文件。`agents/openai.yaml` 提供 Codex/ChatGPT 桌面端显示名称、简短说明和默认提示词。

在 Codex 中可以显式调用：

```text
$art-rating-system-maintainer 修改 tools/start.sh
```

当请求内容与 Skill 的 `description` 匹配时，Codex 也可以自动选择它。

## 导入 Codex

### 项目级导入（推荐）

当前仓库已经采用 Codex 官方支持的项目级结构，无需额外安装：

```text
.agents/skills/art-rating-system-maintainer/SKILL.md
```

在仓库根目录或其子目录中启动 Codex。Codex 会从当前目录向上扫描到仓库根目录，并发现 `.agents/skills/` 中的 Skill。

如果新增或修改的 Skill 没有立即出现，重新启动 Codex。

### 用户级导入

如果希望该 Skill 在所有仓库中可用，将整个 Skill 文件夹复制到用户级目录：

macOS/Linux：

```bash
mkdir -p ~/.agents/skills
cp -R .agents/skills/art-rating-system-maintainer ~/.agents/skills/
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
Copy-Item -Recurse -Force ".agents\skills\art-rating-system-maintainer" "$HOME\.agents\skills\"
```

项目级和用户级存在同名 Skill 时，Codex 不会合并它们，选择器中可能同时出现两个版本。对本项目而言，保留项目级版本通常更容易随 Git 同步。

Codex 官方文档：[Build skills](https://learn.chatgpt.com/docs/build-skills)。

## 导入 Trae

Trae 使用项目规则，而不是 Codex/Claude 的原生 Skill 目录。项目规则目录为：

```text
.trae/rules/
```

因此需要把 Skill 转换成 Trae 项目规则：

1. 在项目根目录创建 `.trae/rules/`；
2. 复制 `SKILL.md` 的指令正文；
3. 保存为 `.trae/rules/art-rating-system-maintainer.md`；
4. 在 Trae 设置中心确认项目规则已经被识别；
5. 根据需要设置规则的应用模式、`description` 或 `globs`。

macOS/Linux 示例：

```bash
mkdir -p .trae/rules
cp .agents/skills/art-rating-system-maintainer/SKILL.md \
  .trae/rules/art-rating-system-maintainer.md
```

Windows PowerShell 示例：

```powershell
New-Item -ItemType Directory -Force ".trae\rules" | Out-Null
Copy-Item ".agents\skills\art-rating-system-maintainer\SKILL.md" ".trae\rules\art-rating-system-maintainer.md"
```

复制后建议把 Codex 专用的 UI 元数据和显式 `$skill-name` 调用说明改写为普通 Trae 规则。Trae 会递归读取 `.trae/rules/`，但不会使用 `agents/openai.yaml`。

Trae 还支持在项目根目录复用 `AGENTS.md`、`CLAUDE.md` 和 `CLAUDE.local.md`。如果需要多个 AI 工具共享同一套项目规则，也可以把核心维护约束整理到根目录 `AGENTS.md`，再保留各工具自己的格式文件。

Trae 官方文档：[Rules](https://docs.trae.ai/ide/rules)。

## 导入 Claude Code

Claude Code 原生 Skill 的项目级目录为：

```text
.claude/skills/<skill-name>/SKILL.md
```

### 项目级导入（推荐）

macOS/Linux：

```bash
mkdir -p .claude/skills
cp -R .agents/skills/art-rating-system-maintainer \
  .claude/skills/art-rating-system-maintainer
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force ".claude\skills" | Out-Null
Copy-Item -Recurse -Force ".agents\skills\art-rating-system-maintainer" ".claude\skills\art-rating-system-maintainer"
```

Claude Code 读取的是 `SKILL.md`。复制后可以删除 `.claude/skills/art-rating-system-maintainer/agents/openai.yaml`，因为它是 Codex/ChatGPT 的 UI 元数据，Claude Code 不使用它。

启动 Claude Code 后，可以让 Claude 根据描述自动选择 Skill，也可以显式调用：

```text
/art-rating-system-maintainer
```

### 用户级导入

希望在所有项目中使用时，将 Skill 复制到：

```text
~/.claude/skills/art-rating-system-maintainer/
```

macOS/Linux：

```bash
mkdir -p ~/.claude/skills
cp -R .agents/skills/art-rating-system-maintainer ~/.claude/skills/
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force ".agents\skills\art-rating-system-maintainer" "$HOME\.claude\skills\art-rating-system-maintainer"
```

Claude Code 会从启动目录及其父目录到仓库根目录发现项目 Skills。将 Skill 放到仓库内更适合团队共享和版本管理。

Claude Code 官方文档：[Extend Claude with skills](https://code.claude.com/docs/en/skills)。

## 跨工具维护建议

- 以 `.agents/skills/art-rating-system-maintainer/SKILL.md` 作为本仓库的主要 Skill 来源；
- 修改 Skill 后，同步更新 Trae 规则和 Claude Code 副本，避免规则不一致；
- Codex 的 `agents/openai.yaml` 不需要复制到 Trae，复制到 Claude Code 后也可以删除；
- 不要把虚拟环境、依赖目录、日志、数据库、上传文件或密钥放入 Skill 目录；
- 导入后先用一个只读请求验证规则是否触发，再执行会提交或推送代码的任务。
