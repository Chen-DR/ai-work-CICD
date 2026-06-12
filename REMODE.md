# REMODE.md

## 1. 项目熟读结果

本项目是一个 AI-Ops 前后端分离平台，围绕 Apptainer 容器打包、远程服务器压测、知识库增强对话、产物管理、审计日志和仪表盘展开。

### 技术栈

| 层级 | 技术 |
|---|---|
| 前端 | Vue 3、TypeScript、Vite、Element Plus、Pinia、Vue Router、Axios、ECharts |
| 后端 | Python 3.11、Django、Django REST Framework |
| 数据库 | MySQL 8 |
| 异步任务 | Celery + Redis |
| 远程执行 | Paramiko SSH/SFTP |
| AI 模型 | DeepSeek API |
| 文件存储 | 本地文件系统，挂载到 `DATA_ROOT` |
| 部署 | Docker Compose + Nginx + Gunicorn |

### 核心目录

| 路径 | 说明 |
|---|---|
| `backend/config/` | Django settings、URL、Celery、WSGI/ASGI |
| `backend/apps/accounts/` | 登录、登出、当前用户 |
| `backend/apps/projects/` | 项目和项目成员 |
| `backend/apps/chat/` | 对话、消息、LLM 调用 |
| `backend/apps/knowledge/` | 知识库文档上传、解析、检索 |
| `backend/apps/apptainer/` | Apptainer definition 生成和远程构建 |
| `backend/apps/benchmark/` | 压测脚本上传和远程执行 |
| `backend/apps/servers/` | 服务器、凭据、允许目录、环境检测、指标采集 |
| `backend/apps/artifacts/` | 构建/压测产物元数据和下载 |
| `backend/apps/audit/` | 审计日志 |
| `backend/infrastructure/` | LLM、SSH、SFTP、存储、安全等基础设施适配 |
| `frontend/src/` | Vue 前端源码 |
| `deploy/` | Docker Compose 与 Nginx 部署配置 |

### 主业务链路

```text
浏览器页面
  -> frontend/src/api/*.ts
  -> /api/v1/*
  -> backend/config/urls.py
  -> backend/apps/*/views.py
  -> serializers.py / services.py / tasks.py
  -> ORM / DATA_ROOT / DeepSeek / SSH / SFTP / Celery
  -> API 响应或异步任务状态
```

## 2. 本次改造目标

1. 将后端主数据库从 SQLite 改为 MySQL。
2. 修复远程任务链路中的高风险问题。
3. 接入校验、远程目录策略、Artifact 记录和审计日志。
4. 将知识库上传改为异步解析。
5. 统一认证注释和函数视图权限声明。
6. 保存项目熟读与改造说明到本文件。

## 3. MySQL 改造

### 涉及文件

- `backend/config/settings.py`
- `backend/apps/common/apps.py`
- `backend/requirements.txt`
- `backend/Dockerfile`
- `.env.example`
- `backend/.env.example`
- `deploy/docker-compose.yml`

### 环境变量

```env
DB_NAME=aiops
DB_USER=aiops
DB_PASSWORD=change-me-db-password
DB_HOST=mysql
DB_PORT=3306
DB_CONN_MAX_AGE=60
DB_CONNECT_TIMEOUT=10
MYSQL_ROOT_PASSWORD=change-me-root-password
```

### 配置说明

- Django 使用 `django.db.backends.mysql`。
- MySQL 字符集使用 `utf8mb4`。
- SQL mode 使用 `STRICT_TRANS_TABLES`，避免静默截断。
- Docker Compose 新增 `mysql:8.4` 服务和 `mysql_data` 数据卷。
- 后端和 Celery worker 依赖 MySQL healthcheck 与 Redis。
- SQLite WAL PRAGMA 已限制为仅 SQLite vendor 时执行，避免 MySQL 启动时执行 SQLite 专用语句。

### SQLite 旧数据迁移提示

如果已有 SQLite 数据，需要先备份，再按环境情况迁移：

```bash
cd backend
python manage.py dumpdata --natural-foreign --natural-primary -o sqlite-backup.json
# 切换 MySQL 环境变量并完成 migrate 后
python manage.py loaddata sqlite-backup.json
```

生产数据建议先在测试环境演练，不直接对线上库执行。

## 4. 已处理问题清单

### 4.1 Apptainer definition 未落盘

问题：`ApptainerDefinition.storage_path` 有字段，但生成流程只保存数据库内容，构建任务却依赖文件路径。

处理：

- 创建/生成 definition 时写入 `DATA_ROOT/apptainer/definitions/` 下的安全文件路径。
- 保存 `storage_path`。
- 构建任务启动前检查 `storage_path` 非空且文件存在。

### 4.2 SFTP 失败未中断

问题：`SFTPClient.mkdir/upload_file/download_file` 返回 `bool`，调用方未检查。

处理：

- Apptainer 构建任务检查 `mkdir` 和 `upload_file` 返回值。
- Benchmark 任务检查 `mkdir`、`upload_file` 和 `download_file` 返回值。
- 失败时任务进入 `FAILED`，并写入 `error_message` 和 job 日志。

### 4.3 校验器未接入主链路

问题：Apptainer 和 Benchmark validators 存在，但创建任务和执行任务没有统一接入。

处理：

- Apptainer definition 内容创建时校验 `Bootstrap:`、`From:` 和危险模式。
- Apptainer build job 创建和任务执行前校验 workdir/output_name。
- Benchmark job 创建和任务执行前校验 params。

### 4.4 ServerAllowedDir 未进入执行策略

问题：服务器允许目录可以配置，但远程任务使用硬编码目录或没有校验。

处理：

- 新增远程执行 guard，统一读取 `server.allowed_dirs`。
- 使用 `normalize_remote_path` 和 `is_subpath` 校验 workdir、远程脚本、远程报告、远程 SIF 路径。
- 未配置 allowed dir 时拒绝执行远程任务。

### 4.5 CommandPolicy 使用不完整

问题：远程命令缺少统一安全检查。

处理：

- 在 Apptainer 和 Benchmark 执行命令前调用 `CommandPolicy.is_safe_command`。
- 远程脚本名、definition 文件名改为后端生成的安全固定名，避免用户原始文件名进入命令。

### 4.6 Artifact 主流程未创建记录

问题：Artifact 模型和 API 存在，但构建/压测成功后未创建产物记录。

处理：

- Apptainer 成功后创建 `sif_path_record` 和 `build_log`。
- Benchmark 成功后创建 `benchmark_log` 和 `benchmark_report`。
- 本地产物记录 `file_size` 和 `checksum`。
- 远程 SIF 当前记录为路径记录，不代表本地可直接下载文件。

### 4.7 审计日志未接入关键动作

问题：`log_action` 存在，但核心业务入口未调用。

处理：

- 为登录、登出、服务器创建/测试/检测/允许目录创建、知识库上传/解析、Apptainer definition 创建/生成、构建任务创建、Benchmark 脚本上传、Benchmark job 创建、Artifact 下载/删除接入审计。
- 审计 detail 会脱敏 password、token、secret、private_key、ssh_key、credential、key 等字段。

### 4.8 知识库上传同步解析

问题：上传接口同步解析文档，大文件可能阻塞请求。

处理：

- 上传接口只保存文件和记录。
- 上传后派发 `parse_knowledge_document_task`。
- 解析任务调用 `KnowledgeService._parse_document`。
- 重解析前删除旧 chunks，避免重复切片。
- 解析失败时写入 `status=FAILED` 和 `error_message`。

### 4.9 认证注释和权限声明不一致

问题：认证类注释声称支持 Bearer 和 Token，但实际只配置 Bearer；部分函数视图依赖全局默认权限。

处理：

- 修正认证类注释为 `Authorization: Bearer <token>`。
- 为 logout、me、knowledge search 等函数视图显式补充 `IsAuthenticated`。

## 5. 关键运行命令

### 后端本地

```bash
cd backend
pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py test
python manage.py runserver 0.0.0.0:8000
```

### Celery

```bash
cd backend
celery -A config worker -l info --concurrency=4
```

### 前端

```bash
cd frontend
npm install
npm run build
npm run dev
```

### Docker Compose

```bash
cd deploy
docker compose config
docker compose up -d mysql redis
docker compose run --rm backend python manage.py check
docker compose run --rm backend python manage.py migrate
docker compose up -d
```

## 6. 需要重点验证的场景

1. MySQL 容器可启动，Django 可完成 `migrate`。
2. 创建 Apptainer definition 后，`storage_path` 非空且文件存在。
3. 创建构建任务时，服务器未配置 allowed dir 会被拒绝。
4. SFTP 上传失败时任务状态为 `FAILED`。
5. Apptainer 成功后创建 `sif_path_record` 和 `build_log` Artifact。
6. Benchmark 成功后创建 `benchmark_report` Artifact。
7. 上传知识库文档后接口快速返回，Celery 解析后状态变为 `READY`。
8. 关键操作产生 AuditLog，且不含密码、token、私钥。
9. 前端 `npm run build` 成功。

## 7. 风险与回滚

### 风险

- MySQL 与 SQLite 类型和严格模式行为不同，历史脏数据可能无法导入。
- `mysqlclient` 依赖系统库，容器构建必须验证。
- 远程 allowed dir 策略收紧后，旧服务器配置如果未添加允许目录，构建/压测会被拒绝。
- 知识库异步解析依赖 Celery worker，worker 未运行时文档会停留在未解析状态。
- 远程 SIF 目前只记录路径，不自动下载到平台本地。

### 回滚

- 代码回滚到切换 MySQL 前版本。
- 保留 MySQL 数据卷备份。
- 如需临时恢复 SQLite，需要恢复 `DATABASES` 配置、移除 MySQL 依赖和 Compose MySQL 服务，并确认 SQLite 数据文件存在。

## 8. 后续建议

- 为 Apptainer/Benchmark task 增加单元测试和 mock SFTP/SSH 测试。
- 为 Artifact 增加 remote/local 类型字段，避免远程路径记录和本地可下载文件混淆。
- 为 ServerAllowedDir 增加默认初始化或管理端引导。
- 为 Knowledge 文档解析增加重试策略和前端解析状态提示。
- 为 MySQL 数据迁移编写正式迁移脚本，而不是只依赖 dumpdata/loaddata。
