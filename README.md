# “大众创享”作品评分系统

一个供管理员上传和管理作品、供评委浏览并评分的 Web 应用。项目采用前后端分离结构：后端是 FastAPI + SQLite，前端是 Vue 3 + Vite；开发环境由 Vite 将 API 和上传文件请求代理到 FastAPI。

## 主要功能

- 管理员上传摄影、文字、视频和手工作品，编辑、隐藏或删除作品。
- 邀请码注册评委账号，使用 Cookie 保存登录会话。
- 评委按“创意、表现力、完成度”三个维度进行 1～10 分评分。
- 展示作品平均分、评分人数和当前用户的评分状态。
- 图片多图展示和缩略图、MP4 视频播放、明暗主题切换。

## 技术栈

| 层次 | 技术 |
| --- | --- |
| 后端 | Python、FastAPI、Uvicorn |
| 数据库 | SQLite（开启 WAL 和外键约束） |
| 前端 | Vue 3、Vue Router、Vite |
| 文件处理 | Pillow（图片缩略图） |
| 可选反向代理 | Nginx |

## 在 Windows 上运行

### 环境要求

- Windows 10/11
- Python 3.10 或更高版本（`py` 或 `python` 命令可用）
- Node.js 20 LTS 或更高版本（包含 `npm`）

在 `tools` 文件夹中双击 `start.bat`，或在项目根目录的 PowerShell / CMD 中运行：

```bat
tools\start.bat
```

首次运行会自动：

1. 在 `backend/venv` 创建 Windows Python 虚拟环境；
2. 安装 `backend/requirements.txt` 中的后端依赖；
3. 在缺少 `frontend/node_modules` 时执行 `npm install`；
4. 分别打开“后端”和“前端”两个可见终端窗口，并在各自窗口内直接运行服务、显示日志。

启动后访问：

- 前端：http://127.0.0.1:7999
- 后端：http://127.0.0.1:8000
- FastAPI 接口文档：http://127.0.0.1:8000/docs

脚本不会把服务注册为后台服务。关闭后端终端只会停止后端，关闭前端终端只会停止前端；也可以在对应窗口按 `Ctrl+C` 停止服务。依赖已经安装后，可跳过安装检查以加快启动：

```bat
tools\start.bat -SkipInstall
```

实际启动逻辑位于 `tools/start-windows.ps1`，`tools/start.bat` 是方便双击和从 CMD 调用的入口。所有工具脚本都会先从 `tools/` 返回项目根目录，因此从任意当前目录调用都能正确定位项目文件。

### Windows 常见问题

- `py`/`python` 找不到：重新安装 Python，并勾选“Add Python to PATH”。
- `npm.cmd` 找不到：安装 Node.js 后重新打开终端。
- 端口占用：释放 7999（前端）或 8000（后端）端口。当前 Vite 配置启用了 `strictPort`，不会自动改用其他端口。
- 从 Linux 复制了 `backend/venv`：虚拟环境不能跨系统使用，请删除该目录后重新运行 `tools\start.bat`。该目录只包含可重新安装的依赖，不应提交到 Git。

## 在 Linux 上运行

先准备依赖：

```bash
python3 -m venv backend/venv
backend/venv/bin/python -m pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
```

然后使用仓库已有脚本：

```bash
./tools/start.sh
./tools/stop.sh
```

Linux 的 `tools/start.sh` 会将服务放到后台，并把 PID 和日志写入 `logs/`；这与 Windows 前台运行脚本的行为不同。

## 项目结构

```text
artRatingSystem/
├─ backend/                    FastAPI 后端、SQLite 数据和上传文件
│  ├─ app/
│  │  ├─ controllers/         HTTP 路由与请求/响应处理
│  │  ├─ core/                配置、数据库和会话等基础设施
│  │  ├─ repositories/        SQLite 数据访问层
│  │  └─ services/            业务规则和跨数据表流程
│  ├─ main.py                 ASGI 应用入口
│  └─ requirements.txt        Python 依赖
├─ frontend/                  Vue 单页应用
│  ├─ src/
│  │  ├─ assets/              全局样式和主题逻辑
│  │  ├─ components/          可复用界面组件
│  │  ├─ router/              页面路由与权限守卫
│  │  ├─ services/            API 和前端登录状态封装
│  │  └─ views/               路由页面
│  ├─ index.html              Vite HTML 入口
│  ├─ package.json            npm 依赖和命令
│  ├─ package-lock.json       npm 锁定版本
│  └─ vite.config.js          开发服务器和后端代理配置
├─ nginx/                     Linux 部署用 Nginx 配置
├─ tools/                     全部运行与 Git 同步脚本
│  ├─ start.bat              Windows 前台启动入口
│  ├─ start-windows.ps1      Windows 环境准备和进程管理
│  ├─ start.sh / stop.sh     Linux 后台启动与停止脚本
│  └─ upload.* / download.*  简单的 Git 推送/拉取辅助脚本
└─ .gitignore                 运行产物和本地配置忽略规则
```

### 后端目录与文件

后端采用 `controller -> service -> repository -> SQLite` 的分层方式。

#### `backend/app/controllers/`

- `auth.py`：登录、注册、退出和修改密码接口。
- `works.py`：作品列表、未评分列表、详情、上传、修改、删除和隐藏接口。
- `ratings.py`：评分维度、个人评分查询和提交评分接口。
- `admin.py`：邀请码生成/查询和用户列表接口，仅管理员可用。
- `__init__.py`：标记控制器 Python 包。

控制器只负责解析 HTTP 参数、检查权限和组织响应，主要业务判断应继续放在 `services/`。

#### `backend/app/core/`

- `config.py`：项目路径、上传目录、数据库路径、应用信息、密钥和 CORS 来源；启动时创建上传子目录。
- `database.py`：SQLite 连接、建表和轻量迁移。数据库首次启动时自动生成 `backend/data.db`。
- `session.py`：使用 `itsdangerous` 签名 Cookie，并提供登录/管理员权限检查。
- `__init__.py`：标记基础设施 Python 包。

#### `backend/app/repositories/`

- `user_repository.py`：用户查询、创建、密码哈希/校验和密码修改。
- `invite_repository.py`：邀请码生成和列表查询。
- `work_repository.py`：作品增删改查、排序、隐藏状态和多图路径解析。
- `rating_repository.py`：用户评分的新增/更新和作品评分查询。
- `__init__.py`：标记数据访问 Python 包。

Repository 层集中编写 SQL。调整表结构时，应同时更新 `core/database.py` 的建表或迁移逻辑。

#### `backend/app/services/`

- `auth_service.py`：用户名和密码规则、登录、注册与改密流程。评委密码目前限定为 4 位数字，管理员新密码至少 6 位。
- `rating_service.py`：评分维度、分数校验和聚合统计。
- `work_service.py`：作品查询组合、上传格式校验、文件保存、缩略图生成和删除清理。
- `__init__.py`：标记业务服务 Python 包。

#### 其他后端文件

- `backend/app/application.py`：创建 FastAPI 实例，注册 CORS、上传文件静态路径和全部路由，并在生命周期开始时初始化数据库。
- `backend/main.py`：Uvicorn 使用的 `main:app` 入口，也支持直接执行 Python 文件。
- `backend/requirements.txt`：后端运行依赖。

### 前端目录与文件

#### `frontend/src/views/`

- `LoginView.vue`：登录页。
- `RegisterView.vue`：邀请码注册页。
- `HomeView.vue`：作品浏览、详情和评分主页面。
- `AdminView.vue`：邀请码、用户和作品管理页面。
- `UploadView.vue`：管理员上传作品页面，包含多文件预览。
- `ChangePasswordView.vue`：登录用户修改密码页面。

#### `frontend/src/components/`

- `AppNavbar.vue`：导航栏、管理员入口、主题切换、改密和退出。
- `WorkMedia.vue`：统一渲染文字、视频、单图或多图作品。

#### `frontend/src/services/`

- `api.js`：封装 `fetch`、Cookie 携带、401 跳转和媒体 URL。可通过 `VITE_API_BASE_URL` 指定独立后端地址。
- `auth.js`：在 Vue 响应式状态和 `localStorage` 中维护当前用户，并封装退出操作。

#### 其他前端文件夹和入口

- `frontend/src/router/index.js`：页面路由、登录守卫和管理员守卫。
- `frontend/src/assets/style.css`：全局布局、组件、响应式和明暗主题样式。
- `frontend/src/assets/theme.js`：主题初始化、持久化和系统主题监听。
- `frontend/src/App.vue`：顶层路由出口。
- `frontend/src/main.js`：创建 Vue 应用并加载路由、样式和主题逻辑。
- `frontend/index.html`：浏览器 HTML 外壳和 `#app` 挂载点。
- `frontend/vite.config.js`：监听 `0.0.0.0:7999`，并将 `/api`、`/static/uploads` 代理到 `127.0.0.1:8000`。

### 部署与辅助目录

- `nginx/artRatingSystem.conf`：Nginx 示例；监听 80，将普通页面代理到 Vite，将 API 和上传文件代理到 FastAPI，并允许最大 500 MB 请求体。
- `tools/`：集中存放所有脚本；每个脚本启动后都会先执行 `cd ..`（批处理使用 `cd /d`）回到项目根目录。
- `tools/start-windows.ps1`：Windows 环境准备，并为前后端分别打开直接运行服务的可见终端窗口。
- `logs/`：Linux 启动脚本运行时生成的 PID 与日志目录，已被 Git 忽略。
- `backend/uploads/`：运行时生成，按 `images/`、`videos/`、`objects/`、`thumbnails/` 保存上传内容，已被 Git 忽略。
- `backend/venv/`、`frontend/node_modules/`、`frontend/dist/`：本地依赖或构建产物，均不应提交。

## 运行时数据

后端第一次启动时会创建 `backend/data.db`，包含以下表：

| 表 | 用途 |
| --- | --- |
| `users` | 用户、密码摘要、盐、角色 |
| `invite_codes` | 注册邀请码及使用状态 |
| `works` | 作品元数据、文件路径、正文、隐藏状态 |
| `ratings` | 每名用户对每件作品的各维度评分 |

`data.db` 和上传文件都被 `.gitignore` 排除。备份或迁移时应同时复制 `backend/data.db` 与 `backend/uploads/`，否则数据库中的媒体路径会失效。

注意：当前代码只负责建表，不会自动创建初始管理员、默认用户或邀请码。全新数据库需要预先写入一个 `role='admin'` 的账号，管理员登录后才能生成邀请码并上传作品。不要直接写入明文密码；账号密码字段必须使用 `user_repository.hash_password()` 生成的摘要与盐。

## 配置

后端读取以下环境变量：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `APP_SECRET_KEY` | 开发用固定字符串 | Cookie 签名密钥；生产环境必须替换为随机强密钥 |
| `CORS_ORIGINS` | `http://localhost:7999,http://127.0.0.1:7999` | 逗号分隔的允许来源 |

前端构建时可使用：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `VITE_API_BASE_URL` | 空（同源请求） | API 与媒体文件的后端根地址 |

PowerShell 临时设置示例：

```powershell
$env:APP_SECRET_KEY = "请替换为足够长的随机字符串"
$env:CORS_ORIGINS = "https://example.com"
tools\start.bat -SkipInstall
```

## API 概览

- 认证：`POST /api/login`、`POST /api/register`、`POST /api/logout`、`POST /api/change-password`
- 作品：`GET /api/works`、`GET /api/works/unrated`、`GET /api/works/{id}`
- 管理作品：`POST /api/works/upload`、`PUT/DELETE /api/works/{id}`、`POST /api/works/{id}/toggle-hidden`
- 评分：`GET /api/works/{id}/dimensions`、`GET /api/works/{id}/my-rating`、`POST /api/works/{id}/rate`
- 管理：`GET/POST /api/admin/invite-codes`、`GET /api/admin/users`

请求字段和可交互调试页面以运行后的 `/docs` 为准。

## 修改指南

- 新增页面：在 `frontend/src/views/` 创建页面，并在 `frontend/src/router/index.js` 注册路由。
- 新增通用 UI：放入 `frontend/src/components/`；全局样式放入 `frontend/src/assets/style.css`。
- 新增接口：在 `backend/app/controllers/` 定义路由；业务规则放入 `services/`；SQL 放入 `repositories/`。
- 修改数据库结构：更新 `backend/app/core/database.py`，为已有数据库补充幂等迁移，并同步修改 repository。
- 新增作品类型：同时修改后端 `work_service.py` 的分类/扩展名规则、评分或存储逻辑，以及前端筛选、上传与媒体展示组件。
- 修改开发端口：同步检查 `frontend/package.json`、`frontend/vite.config.js`、启动脚本、CORS 默认值和 Nginx 配置。

`tools/upload.bat/.sh` 会直接提交并推送 `main`，`tools/download.bat/.sh` 会拉取远端 `main`。使用这些脚本前应先检查 `git status`，避免误提交本地改动。
