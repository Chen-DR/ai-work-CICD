# AI-Ops 平台 — 启动与部署指南

## 目录

1. [开发环境要求](#1-开发环境要求)
2. [后端启动](#2-后端启动)
3. [前端启动](#3-前端启动)
4. [Celery 异步任务](#4-celery-异步任务)
5. [后端 API 一览](#5-后端-api-一览)
6. [Docker Compose 部署](#6-docker-compose-部署)
7. [环境变量说明](#7-环境变量说明)

---

## 1. 开发环境要求

| 工具 | 版本要求 |
|------|---------|
| Python | ≥ 3.11 |
| Node.js | ≥ 18 |
| Redis | ≥ 7（Celery 依赖） |
| MySQL | ≥ 8.0（业务元数据） |

---

## 2. 后端启动

### 2.1 初始化

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2.2 配置环境变量

```bash
# 复制示例配置
cp .env.example .env
```

编辑 `.env`，至少配置：

```bash
DJANGO_SECRET_KEY=your-random-secret-key-here
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
ENCRYPTION_KEY=your-fernet-key-for-credentials
DB_NAME=aiops
DB_USER=aiops
DB_PASSWORD=your-db-password
DB_HOST=127.0.0.1
DB_PORT=3306
```

> `ENCRYPTION_KEY` 生成方式：
> ```python
> from cryptography.fernet import Fernet
> print(Fernet.generate_key().decode())
> ```

### 2.3 初始化数据库

```bash
source .venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
```

### 2.4 启动开发服务器

```bash
python manage.py runserver 0.0.0.0:8000
```

API 地址：`http://localhost:8000/api/v1/`

---

## 3. 前端启动

### 3.1 安装依赖

```bash
cd frontend
npm install
```

### 3.2 配置环境变量（可选）

```bash
# frontend/.env
VITE_API_BASE_URL=/api/v1
```

默认开发模式下 Vite 代理 `/api/v1` 到 `http://127.0.0.1:8000`（配置在 `vite.config.ts` 中）。

### 3.3 启动开发服务器

```bash
npm run dev
```

访问地址：`http://localhost:5173`

### 3.4 构建生产包

```bash
npm run build
# 输出在 frontend/dist/
```

---

## 4. Celery 异步任务

### 4.1 启动 Redis

```bash
# 方式一：直接启动
redis-server

# 方式二：Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### 4.2 启动 Celery Worker

```bash
cd backend
source .venv/bin/activate
celery -A config worker -l info --concurrency=4
```

### 4.3 可选的 Celery 监控（Flower）

```bash
celery -A config flower --port=5555
```

访问 `http://localhost:5555`

### 4.4 任务清单

| 任务 | 说明 | 触发 |
|------|------|------|
| `run_apptainer_build_task` | 远程构建 Apptainer 容器 | 创建构建任务时自动提交 |
| `run_benchmark_job_task` | 远程执行压测脚本 | 创建压测任务时自动提交 |
| `parse_knowledge_document_task` | 解析知识库文档 | 上传文档后调用 |

---

## 5. 后端 API 一览

认证方式：`Authorization: Bearer <token>`

### 5.1 认证

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login/` | 登录，返回 token + user |
| POST | `/api/v1/auth/logout/` | 登出 |
| GET  | `/api/v1/auth/me/` | 当前用户信息 |

### 5.2 项目管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/v1/projects/` | 项目列表 / 新建 |
| GET/PUT/DELETE | `/api/v1/projects/{id}/` | 项目详情 / 更新 / 删除 |

### 5.3 对话 / AI

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/v1/chat/conversations/` | 对话列表 / 新建 |
| GET/DELETE | `/api/v1/chat/conversations/{id}/` | 对话详情 / 删除 |
| GET | `/api/v1/chat/conversations/{id}/messages/` | 消息列表 |
| POST | `/api/v1/chat/complete/` | **AI 对话**（含知识库增强） |

请求体：
```json
{
  "project_id": 1,
  "conversation_id": 1,
  "message": "帮我生成 Ubuntu 22.04 + CUDA 的 Apptainer",
  "use_knowledge": true
}
```

### 5.4 知识库

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/v1/knowledge/documents/` | 文档列表 / 上传 |
| DELETE | `/api/v1/knowledge/documents/{id}/` | 删除文档 |
| POST | `/api/v1/knowledge/documents/{id}/parse/` | 触发重新解析 |
| POST | `/api/v1/knowledge/search/` | 检索知识库 |

### 5.5 Apptainer

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/v1/apptainer/definitions/` | Definition 列表 / 新建 |
| PUT/DELETE | `/api/v1/apptainer/definitions/{id}/` | 编辑 / 删除 |
| POST | `/api/v1/apptainer/generate/` | **AI 生成 Definition** |
| POST | `/api/v1/apptainer/build-jobs/` | 创建构建任务 |
| GET | `/api/v1/apptainer/build-jobs/{id}/` | 任务详情 |
| GET | `/api/v1/apptainer/build-jobs/{id}/logs/` | 构建日志 |
| POST | `/api/v1/apptainer/build-jobs/{id}/cancel/` | 取消任务 |

### 5.6 压测

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/v1/benchmark/scripts/` | 脚本列表 / 上传 |
| DELETE | `/api/v1/benchmark/scripts/{id}/` | 删除脚本 |
| POST | `/api/v1/benchmark/jobs/` | 创建压测任务 |
| GET | `/api/v1/benchmark/jobs/{id}/logs/` | 压测日志 |
| POST | `/api/v1/benchmark/jobs/{id}/cancel/` | 取消任务 |

### 5.7 服务器

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/v1/servers/` | 服务器列表 / 新增 |
| PUT/DELETE | `/api/v1/servers/{id}/` | 编辑 / 删除 |
| POST | `/api/v1/servers/{id}/test/` | 测试 SSH 连接 |
| POST | `/api/v1/servers/{id}/detect/` | 检测服务器环境 |

### 5.8 文件产物

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/artifacts/` | 产物列表（可筛选） |
| GET | `/api/v1/artifacts/{id}/download/` | 下载文件 |
| DELETE | `/api/v1/artifacts/{id}/` | 删除 |

### 5.9 审计日志

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/audit/logs/` | 审计日志列表（可筛选） |

---

## 6. Docker Compose 部署

### 6.1 完整部署（全部容器化）

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 填入真实值

# 2. 一键启动
docker-compose -f deploy/docker-compose.yml up -d

# 3. 初始化数据库
docker-compose -f deploy/docker-compose.yml exec backend python manage.py migrate
docker-compose -f deploy/docker-compose.yml exec backend python manage.py createsuperuser

# 4. 查看状态
docker-compose -f deploy/docker-compose.yml ps

# 5. 查看日志
docker-compose -f deploy/docker-compose.yml logs -f

# 6. 停止
docker-compose -f deploy/docker-compose.yml down
```

### 6.2 服务架构

```
Nginx :80
  ├── / → frontend (:5173)
  └── /api/ + /admin/ → backend (:8000)

Backend → MySQL (:3306)
        → Redis (:6379) → Celery Worker
                                └── SSH/SFTP → Remote Servers
```

### 6.3 分步启动（开发调试）

```bash
# 终端 1：Redis
redis-server

# 终端 2：后端
cd backend && source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# 终端 3：Celery
cd backend && source .venv/bin/activate
celery -A config worker -l info

# 终端 4：前端
cd frontend && npm run dev
```

---

## 7. 环境变量说明

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `DJANGO_SECRET_KEY` | ✅ | - | Django 密钥，生产环境必须更换 |
| `DJANGO_DEBUG` | | `false` | 调试模式，开发时设为 `true` |
| `DJANGO_ALLOWED_HOSTS` | | `*` | 逗号分隔的允许域名 |
| `DATA_ROOT` | | `./data` | 文件存储根目录 |
| `DB_NAME` | ✅ | `aiops` | MySQL 数据库名 |
| `DB_USER` | ✅ | `aiops` | MySQL 用户名 |
| `DB_PASSWORD` | ✅ | - | MySQL 用户密码 |
| `DB_HOST` | ✅ | `127.0.0.1` | MySQL 主机，Docker 中为 `mysql` |
| `DB_PORT` | | `3306` | MySQL 端口 |
| `DB_CONN_MAX_AGE` | | `60` | 数据库连接复用秒数 |
| `DB_CONNECT_TIMEOUT` | | `10` | 数据库连接超时秒数 |
| `REDIS_URL` | ✅ | `redis://127.0.0.1:6379/0` | Redis 连接地址 |
| `DEEPSEEK_API_KEY` | ✅ | - | DeepSeek API 密钥 |
| `DEEPSEEK_BASE_URL` | | `https://api.deepseek.com` | API 端点 |
| `DEEPSEEK_MODEL` | | `deepseek-chat` | 模型名 |
| `ENCRYPTION_KEY` | ✅ | - | 凭据加密密钥（Fernet 格式） |
| `MAX_UPLOAD_SIZE_MB` | | `100` | 上传文件大小限制 |
| `JOB_LOG_TAIL_LINES` | | `200` | 日志尾部读取行数 |

---

## 8. 常见问题

### Q: 前端请求后端报 401
A: 登录后才能获取 token，请求需带 `Authorization: Bearer <token>`。开发阶段可注释掉 `router/index.ts` 的登录守卫。

### Q: Celery 任务不执行
A: 确认 Redis 已启动且有 `celery worker` 在运行中。查看 `celery -A config worker -l info` 的输出。

### Q: 构建/压测任务一直 PENDING
A: Celery Worker 未启动或无法连接 Redis。检查 Redis 地址是否与 `.env` 一致。
