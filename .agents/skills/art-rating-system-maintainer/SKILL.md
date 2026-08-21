---
name: art-rating-system-maintainer
description: Modify, fix, review, document, or maintain the artRatingSystem repository. Use for any project-specific request involving its FastAPI backend, Vue frontend, SQLite data layer, Nginx configuration, tools, documentation, or Git delivery workflow.
---

# Art Rating System Maintainer

接收用户对本项目的任何输入，先判断它是后端、前端、全栈、部署脚本还是文档任务，再在对应范围内完成修改、验证和交付。不要将此 Skill 用于其他仓库。

## 开始时必须执行

1. 确认当前工作区是 `artRatingSystem`，并检查 `git status --short`。保留用户已有改动，不覆盖、不清理、不重置。
2. 在读取和修改任务文件之前执行：

   ```bash
   git pull origin main
   ```

   `git pull` 是本 Skill 的修改前置条件。若工作区改动、冲突、网络、权限或远端状态导致拉取失败，停止修改，向用户报告具体原因；不要用 `reset --hard`、强制检出或自动丢弃改动来绕过。
3. 拉取成功后，向用户展示下面的精简项目结构，并明确本次将在哪个目录和哪些文件中修改。

```text
artRatingSystem/
├─ backend/                       Python / FastAPI 后端
│  ├─ app/controllers/            HTTP 路由、参数和响应
│  ├─ app/services/               业务规则与流程
│  ├─ app/repositories/           SQLite 数据访问
│  ├─ app/core/                   配置、数据库、会话
│  ├─ main.py                     ASGI 入口
│  └─ requirements.txt            Python 依赖
├─ frontend/                      JavaScript / Vue 3 前端
│  ├─ src/views/                  路由页面
│  ├─ src/components/             可复用组件
│  ├─ src/services/               API 与登录状态
│  ├─ src/router/                 路由和权限守卫
│  ├─ src/assets/                 样式与主题
│  ├─ package.json                npm 依赖和命令
│  └─ vite.config.js              Vite 服务及代理
├─ nginx/                         Nginx 反向代理配置
├─ tools/                         Windows/Linux 启停和 Git 工具
├─ .agents/skills/                项目专用 Codex Skills
└─ README.md                      架构、运行与维护文档
```

## 读取和修改边界

先根据请求选定范围，不要为了“了解全项目”重复浏览无关文件。

- **仅后端任务**：只读取 `backend/`、必要的 `nginx/` 或 `tools/` 配置以及 README 中相关段落。不得读取 `frontend/` 下的任何文件。修改路由时放在 `controllers/`，业务逻辑放在 `services/`，SQL 放在 `repositories/`，配置、建表和迁移放在 `core/`。
- **仅前端任务**：主要读取和修改 `frontend/`。只有在必须确认真实 API 契约且现有前端代码或 README 无法回答时，才读取对应后端 controller；不要浏览无关后端模块。
- **全栈任务**：先列出前后端契约和两侧目标文件，再只读取这些文件。保持请求字段、响应结构、路由和代理配置一致。
- **部署或脚本任务**：读取 `tools/`、`nginx/` 及必要的端口/环境配置。所有项目脚本集中在 `tools/`，并应从脚本目录执行 `cd ..` 返回项目根目录。
- **文档任务**：以实际代码和配置为准更新 `README.md`；只读取验证文档所需的源码范围。

若任务范围在执行中确实扩大，先告诉用户新增的目标目录和原因，然后再读取它。

## 技术语言和项目职责

- 后端使用 **Python**，框架为 **FastAPI/Uvicorn**。负责登录会话、权限、邀请码、作品管理、文件上传、评分校验与统计、静态上传文件服务。
- 数据存储使用 **SQLite**。`backend/app/core/database.py` 负责建表和轻量迁移，repository 层负责 SQL；运行数据库为 `backend/data.db`。
- 图片处理使用 **Pillow**，上传内容保存在 `backend/uploads/`。
- 前端使用 **JavaScript、Vue 3、Vue Router、Vite、HTML/CSS**。负责登录注册页面、作品浏览与评分、管理后台、上传界面、主题和交互状态。
- 开发环境中 Vite 监听 `7999`，将 `/api` 和 `/static/uploads` 代理到监听 `8000` 的 FastAPI。
- `nginx/` 负责 Linux 反向代理示例；`tools/` 负责 Windows/Linux 本地启停与仓库同步。

遵守现有 `controller -> service -> repository -> SQLite` 后端分层。修改数据库结构时必须提供对已有数据库安全、可重复执行的迁移。不要提交 `data.db`、上传文件、虚拟环境、`node_modules`、构建产物或密钥。

## 修改与验证

1. 修改前再次用 `git status --short` 区分拉取前已有改动和本次改动，避免把无关文件混入提交。
2. 使用适合范围的最小验证：
   - Python：至少进行相关模块导入/编译检查；有测试时运行相关测试。
   - Vue：至少运行相关 lint/test；项目没有对应命令时运行 `npm run build`。
   - PowerShell/批处理/Shell：检查语法、路径定位和退出码；不要为测试而执行会推送代码的辅助脚本。
   - 文档：核对命令、路径、端口和文件职责与当前仓库一致。
3. 检查 `git diff --check` 和 `git diff`，确认没有调试内容、敏感信息或无关改动。
4. 若验证失败，先修复并重新验证。无法修复时不要提交或推送，清楚报告阻塞原因。

## 检查通过后必须发布

验证全部通过后执行以下交付流程：

```bash
git add <本次修改文件>
git commit -m "<准确概括本次修改>"
git push origin main
```

- 提交前用 `git status --short` 检查暂存范围。若存在用户原有的无关改动，不得擅自把它们提交；只暂存本次任务文件，并向用户说明未包含的改动。
- 提交信息应描述实际修改，不使用 `auto commit` 等无意义文本。
- 没有实际差异时不要创建空提交；报告无需推送。
- 禁止 `push --force`。推送被拒绝、发生冲突或需要新权限时停止并报告，不得改写用户或远端历史。
- 最终回复给出修改位置、验证结果、提交哈希和推送结果。
