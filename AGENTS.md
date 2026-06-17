# AGENTS.md

## 项目身份

本仓库是一个 AI-Ops 平台，用于 Apptainer 容器打包和远程服务器压测执行。

已确认技术栈如下：

```text
前端：Vue 3 + TypeScript + Vite + Element Plus + Pinia + Axios
后端：Python 3.11+ + Django + Django REST Framework
数据库：MySQL 8，用于业务元数据
异步任务：Celery + Redis
远程执行：Paramiko SSH/SFTP
AI 模型：DeepSeek API
知识库：MySQL 元数据 + 关键词检索起步
文件存储：MVP 阶段使用本地文件系统
部署：优先 Docker Compose，后续按需升级 Kubernetes
```

除非项目负责人明确要求，否则不要将后端切换为 Java、Node.js、NestJS、Go 或其他框架。

完整架构说明文档应放置在：

```text
docs/AI-Ops_完整架构与开发说明.md
```

该文档是产品设计和架构细节的主要依据。

---

## 产品范围

系统包含三个核心业务领域。

### 1. Apptainer 容器打包

用户通过自然语言描述容器环境需求。后端检索相关知识库内容，调用 DeepSeek API，生成 Apptainer definition file，保存文件版本，并可选择在远程服务器上执行构建。

预期流程：

```text
用户需求
  -> 知识库检索
  -> DeepSeek 生成
  -> Apptainer definition 校验
  -> 保存 definition 版本
  -> 选择远程服务器和工作目录
  -> 创建构建任务
  -> Celery 执行 SSH/SFTP 流程
  -> 远程执行 apptainer build
  -> 采集日志
  -> 保存产物元数据
```

### 2. 远程服务器压测

用户上传 CPU、硬盘、GPU、混合或自定义压测脚本。后端将脚本上传到目标服务器，使用受控参数执行脚本，采集日志，等待报告生成，并将报告下载回平台。

预期流程：

```text
上传压测脚本
  -> 创建压测任务
  -> 校验脚本、参数、服务器和工作目录
  -> 通过 SFTP 上传脚本
  -> chmod +x 脚本
  -> 使用受控参数执行脚本
  -> 采集 stdout/stderr 日志
  -> 等待报告文件生成
  -> 下载报告
  -> 保存产物元数据
```

### 3. 知识库增强生成

系统应使用用户上传的内部文档、历史 Apptainer 文件、压测脚本说明、服务器环境说明和错误日志来提升 DeepSeek 输出质量。

MVP 阶段可使用关键词检索。后续可升级为 SQLite FTS5、Chroma、FAISS、PostgreSQL 或 pgvector。

---

## 不可违背的架构规则

必须严格遵守以下规则：

1. Vue 只负责 UI 和用户交互。
2. Django 负责业务逻辑、权限、参数校验、API 响应和任务创建。
3. DeepSeek 只负责文本生成和分析。
4. DeepSeek 输出绝不能被直接执行。
5. Celery 负责长耗时任务。
6. Paramiko 负责受控 SSH/SFTP 执行。
7. MySQL 保存业务元数据。
8. 大文件、日志、上传脚本、报告和生成的 definition 文件必须保存在文件系统中.
9. 前端绝不能提交任意 shell 命令。
10. 远程命令必须由后端 action 模板生成。
11. 每个远程操作都必须经过命令策略校验。
12. 每个远程操作都必须可审计。

不要削弱以上规则。

---

## 预期仓库结构

除非另有说明，使用以下仓库结构：

```text
aiops-platform/
  AGENTS.md
  README.md

  docs/
    AI-Ops_完整架构与开发说明.md

  backend/
    manage.py
    requirements.txt
    .env.example

    config/
      __init__.py
      settings.py
      urls.py
      asgi.py
      wsgi.py
      celery.py

    apps/
      accounts/
      projects/
      chat/
      knowledge/
      apptainer/
      benchmark/
      servers/
      artifacts/
      audit/
      common/

    infrastructure/
      llm/
      ssh/
      storage/
      rag/
      security/

    data/
      db.sqlite3
      uploads/
      artifacts/
      logs/
      reports/
      tmp/

  frontend/
    package.json
    vite.config.ts
    tsconfig.json
    src/
      api/
      views/
      components/
      stores/
      router/
      types/
      utils/
      styles/

  deploy/
    docker-compose.yml
    nginx.conf
```

---

## 后端开发规则

后端必须使用 Django 和 Django REST Framework。

每个 Django app 在适用时应遵循以下结构：

```text
models.py       数据库模型
serializers.py  请求校验和响应序列化
views.py        API 入口
services.py     业务流程
tasks.py        Celery 任务
validators.py   复杂校验规则
urls.py         路由注册
admin.py        Django 管理后台注册
```

规则：

- view 层保持轻量。
- 请求校验放在 serializer 中。
- 业务逻辑放在 service 中。
- 长耗时操作放在 Celery task 中。
- 外部集成放在 `backend/infrastructure/` 下。
- 不要把 SSH 执行逻辑写在 views 中。
- 不要把 DeepSeek HTTP 调用写在 views 中。
- 不要把大文件存入 SQLite。
- 不要把长日志存入 SQLite。
- SQLite 只保存路径和元数据。
- 优先使用 Django ORM 标准字段，以便后续迁移到 PostgreSQL。

---

## 后端 App 职责

使用以下 Django app 和职责划分。

### accounts

负责：

```text
用户认证
用户资料
角色管理
基础权限
```

推荐角色：

```text
admin
developer
operator
viewer
```

### projects

负责：

```text
项目空间
项目成员
项目级资源隔离
```

所有业务资源都应归属于某个项目。

### chat

负责：

```text
对话记录
消息记录
DeepSeek 调用编排
Prompt 构造
知识库上下文注入
LLM 调用记录
```

### knowledge

负责：

```text
文档上传
文档解析
文本清洗
文本切片
关键词检索
知识库搜索 API
```

### apptainer

负责：

```text
Apptainer definition 管理
Definition 版本管理
Definition 校验
构建任务创建
构建任务状态
构建日志读取
```

### benchmark

负责：

```text
压测脚本上传
脚本元数据
压测任务创建
压测参数校验
压测报告回传
```

### servers

负责：

```text
服务器元数据
SSH 凭据元数据
明文密钥或密码
允许远程目录
SSH 连接测试
服务器环境检测
```

### artifacts

负责：

```text
文件元数据
文件下载接口
产物类型管理
存储路径记录
```

### audit

负责：

```text
用户行为审计
远程执行审计
安全相关事件审计
```

### common

负责：

```text
统一响应
分页
异常
常量
基础权限
通用校验器
```

---

## 基础设施层规则

外部系统集成应放在 `backend/infrastructure/` 下。

预期模块：

```text
infrastructure/
  llm/
    deepseek_client.py
  ssh/
    executor.py
    sftp.py
    policy.py
    path_utils.py
  storage/
    local_storage.py
  rag/
    splitter.py
    keyword_search.py
    retriever.py
  security/
    command_sanitizer.py
    secret_masker.py
```

规则：

- DeepSeek API 调用必须通过 `infrastructure/llm/deepseek_client.py`。
- SSH 命令执行必须通过 `infrastructure/ssh/executor.py`。
- SFTP 上传和下载必须通过 `infrastructure/ssh/sftp.py`。
- 命令校验必须通过 `infrastructure/ssh/policy.py`。
- 文件系统操作必须通过 `infrastructure/storage/local_storage.py`。

---

## 前端开发规则

前端必须使用 Vue 3 和 TypeScript。

前端规则：

- API 封装必须放在 `frontend/src/api/`。
- 共享状态必须放在 `frontend/src/stores/` 下的 Pinia store 中。
- 页面级视图必须放在 `frontend/src/views/`。
- 通用 UI 组件必须放在 `frontend/src/components/`。
- 可复用 TypeScript 类型必须放在 `frontend/src/types/`。
- 不要在 Vue 组件里硬编码后端 URL。
- 使用 `src/api/request.ts` 中的统一 Axios 封装。
- 使用 Element Plus 构建管理控制台界面。
- 使用代码编辑器组件展示和编辑 Apptainer definition 文件与脚本。
- MVP 阶段使用轮询或 SSE 展示任务日志。
- 不允许前端用户提交原始 shell 命令。

预期前端页面：

```text
Login
Dashboard
Projects
ChatWorkbench
KnowledgeBase
ApptainerDefinitionList
ApptainerDefinitionEditor
ApptainerBuildJobList
ApptainerBuildJobDetail
BenchmarkScriptList
BenchmarkJobList
BenchmarkJobDetail
Servers
Artifacts
AuditLogs
Settings
```

---

## 数据库规则

MVP 使用 MySQL 8 保存业务元数据。

MySQL 应保存：

```text
用户和角色
项目和成员关系
对话和消息
LLM 调用元数据
知识库文档元数据
知识库切片
服务器元数据
明文服务器凭据记录
服务器允许目录
Apptainer definition 元数据
Apptainer 构建任务元数据
压测脚本元数据
压测任务元数据
文件产物元数据
审计日志
```

MySQL 不应保存：

```text
大文件
上传脚本的二进制内容
长流式日志
压测报告
Apptainer SIF 镜像文件
高频日志行
大型 embedding
```

未来迁移路径：

```text
SQLite
  -> PostgreSQL
  -> PostgreSQL + pgvector
```

模型设计需要保持对 PostgreSQL 迁移友好。

---

## 文件存储规则

MVP 使用本地文件系统存储。

预期数据目录：

```text
backend/data/
  db.sqlite3
  uploads/
    knowledge/
    benchmark/
  artifacts/
    apptainer/
      definitions/
      logs/
      outputs/
    benchmark/
      scripts/
      logs/
      reports/
  logs/
    django/
    celery/
    jobs/
  reports/
  tmp/
```

规则：

- SQLite 只保存文件元数据和路径。
- 实际文件保存在 `backend/data/`。
- 上传文件内部重新命名。
- 原始文件名只作为元数据保留。
- 防止路径穿越。
- 校验文件扩展名。
- 校验文件大小。
- 所有文件下载必须检查用户权限。

---

## AI 与 DeepSeek 规则

DeepSeek 用于：

```text
自然语言对话
Apptainer definition 生成
执行计划解释
错误分析
报告摘要
知识库问答
```

DeepSeek 不用于：

```text
直接命令执行
直接访问服务器
处理凭据
权限决策
安全策略决策
```

Prompt 构造应包含：

```text
System role
用户请求
对话上下文
相关知识库片段
输出格式要求
安全约束
生成 definition 时的 Apptainer 特定规则
```

生成的 Apptainer definition 必须先校验，再保存或构建。

不安全的模型输出必须被拒绝或标记。

---

## 知识库规则

知识库文档流程：

```text
上传文件
  -> 保存原始文件
  -> 创建 KnowledgeDocument
  -> Celery 解析文档
  -> 清洗文本
  -> 切分文本
  -> 保存 KnowledgeChunk 记录
  -> 标记文档为 READY
```

MVP 支持文件类型：

```text
.txt
.md
.log
.sh
.def
.json
.yaml
.yml
```

后续可支持：

```text
.pdf
.docx
.xlsx
```

切片建议：

```text
chunk_size：约 800 个中文字符
chunk_overlap：100 到 150 个中文字符
```

KnowledgeChunk 应保留元数据：

```text
document id
file name
title
chunk index
project id
```

---

## Apptainer 模块规则

Apptainer definition 可以通过以下方式创建：

```text
AI 对话生成
手动编辑器输入
文件上传
```

Definition 文件最低校验要求：

```text
必须包含 Bootstrap:
必须包含 From:
安装依赖时应包含 %post
需要环境变量时应包含 %environment
需要运行入口时应包含 %runscript
不能包含危险 shell 模式
```

危险模式包括：

```text
rm -rf /
mkfs
dd if=
curl ... | bash
wget ... | bash
chmod -R 777 /
/etc/shadow
useradd
passwd
visudo
systemctl
reboot
shutdown
:(){ :|:& };:
```

构建任务流程：

```text
创建构建任务
  -> 校验服务器
  -> 校验 workdir
  -> 校验 definition
  -> 创建远程工作目录
  -> 上传 definition 文件
  -> 执行 apptainer build
  -> 写入任务日志
  -> 校验输出文件
  -> 保存产物元数据
  -> 更新任务状态
```

允许的构建命令模板：

```bash
cd {workdir} && apptainer build {output_name} {definition_file}
```

不允许任意构建命令。

---

## 压测模块规则

压测脚本类型：

```text
cpu
disk
gpu
mixed
custom
```

压测任务输入应包含：

```text
project_id
script_id
server_id
workdir
params
```

前端不得提交原始命令。

后端必须基于安全模板生成受控命令。

压测参数必须拒绝：

```text
;
&&
|
`
$(
>
<
```

报告文件名必须是普通文件名，不允许绝对路径。

压测任务流程：

```text
创建压测任务
  -> 校验脚本
  -> 校验参数
  -> 校验服务器
  -> 校验 workdir
  -> 上传脚本
  -> chmod +x 脚本
  -> 执行脚本
  -> 写入日志
  -> 等待报告
  -> 下载报告
  -> 保存产物元数据
  -> 更新任务状态
```

---

## 远程执行安全规则

远程执行是高风险区域。

必须严格遵守：

1. 不允许任意 shell 命令执行。
2. 不允许前端提交 raw command 字段。
3. 不允许直接执行 DeepSeek 输出。
4. 只能使用基于 action 的后端命令模板。
5. 生成命令前必须校验所有参数。
6. 必须规范化并校验 workdir 是否位于允许目录内。
7. 必须记录所有远程执行尝试。
8. 必须脱敏所有密钥。
9. 必须使用超时。
10. 日志写入文件，不做高频数据库写入。

允许 action：

```text
apptainer_build
apptainer_test
benchmark_run
collect_report
cleanup_workdir
detect_environment
```

如果实现绕过 `CommandPolicy`，应拒绝该实现。

---

## Celery 规则

长耗时任务必须使用 Celery。

预期任务：

```text
parse_knowledge_document_task
generate_apptainer_definition_task
run_apptainer_build_task
run_benchmark_job_task
collect_report_task
detect_server_environment_task
cleanup_temp_files_task
```

任务状态值：

```text
PENDING
VALIDATING
UPLOADING
RUNNING
COLLECTING
SUCCESS
FAILED
CANCELLED
TIMEOUT
```

任务规则：

- 在主要步骤更新状态。
- 设置 `started_at` 和 `finished_at`。
- 将日志写入任务日志文件。
- 保存清晰的错误信息。
- 避免高频数据库写入。
- 使用远程命令超时。
- 保留足够信息用于排查失败。

---

## API 设计规则

所有 API 路由应使用以下前缀：

```text
/api/v1/
```

标准成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

标准错误响应：

```json
{
  "code": 40001,
  "message": "参数错误",
  "data": {}
}
```

主要 API 分组：

```text
/api/v1/auth/
/api/v1/projects/
/api/v1/chat/
/api/v1/knowledge/
/api/v1/apptainer/
/api/v1/benchmark/
/api/v1/servers/
/api/v1/artifacts/
/api/v1/audit/
```

常用错误码：

```text
0       success
40001   参数错误
40101   未登录
40301   无权限
40401   资源不存在
50001   系统错误
60001   SSH 连接失败
60002   远程目录不允许
60003   命令被安全策略拒绝
60004   文件上传失败
60005   文件下载失败
70001   DeepSeek 调用失败
70002   知识库检索失败
80001   文件格式不支持
80002   文件过大
```

---

## 安全规则

密钥：

- 不要硬编码 DeepSeek API Key。
- 不要硬编码服务器密码。
- 不要打印密码或私钥。
- 不要将服务器密码或私钥返回给前端。
- 服务器凭据按项目负责人要求以明文保存到数据库，仅后端运行时可读取。
- 只提交 `.env.example`，不要提交真实 `.env`。

文件上传：

- 校验扩展名。
- 校验大小。
- 内部重命名文件。
- 防止路径穿越。
- 扫描脚本中的危险模式。
- 下载文件时检查权限。

需要审计的动作：

```text
user.login
project.create
knowledge.upload
knowledge.parse
chat.complete
apptainer.generate
apptainer.definition.create
apptainer.build.start
apptainer.build.success
apptainer.build.failed
benchmark.script.upload
benchmark.job.start
benchmark.job.success
benchmark.job.failed
server.create
server.update
server.test
artifact.download
```

---

## 环境变量

预期环境变量：

```text
DJANGO_SECRET_KEY=
DJANGO_DEBUG=
DJANGO_ALLOWED_HOSTS=

DATA_ROOT=

REDIS_URL=

DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=
DEEPSEEK_MODEL=

MAX_UPLOAD_SIZE_MB=
JOB_LOG_TAIL_LINES=
```

不要提交真实值。

---

## 开发命令

后端初始化：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

Celery Worker：

```bash
cd backend
celery -A config worker -l info
```

Redis：

```bash
redis-server
```

前端初始化：

```bash
cd frontend
npm install
npm run dev
```

后端测试：

```bash
cd backend
python manage.py test
```

前端检查：

```bash
cd frontend
npm run lint
npm run build
```

如果 lint 脚本尚不存在，不要假装执行成功。需要新增脚本或在文档中说明。

---

## 完成标准

只有满足以下条件，变更才算完成：

1. 遵守本 AGENTS.md。
2. 不与 `docs/AI-Ops_完整架构与开发说明.md` 冲突。
3. 后端继续使用 Django。
4. 不引入任意远程命令执行。
5. 不将大文件或日志存入 SQLite。
6. 使用标准 API 响应格式。
7. 校验用户输入。
8. 清晰处理错误。
9. 对安全相关或远程执行动作写入审计日志。
10. 行为变化时更新相关文档。

---

## 禁止事项

不要：

```text
未经明确批准切换后端框架
直接执行 DeepSeek 输出
新增任意 shell 命令 API
在代码中保存 API Key
将报告存入 SQLite
将长日志存入 SQLite
把 SSH 逻辑写进 views
把 DeepSeek HTTP 调用写进 views
硬编码本机绝对路径
跳过 workdir 校验
跳过命令策略校验
跳过远程执行审计日志
```

---

## 需求不明确时

如果需求不明确：

1. 优先遵循架构文档。
2. 保持安全模型不变。
3. 保持 MVP 实现简单。
4. 不增加不必要的基础设施。
5. 不改变已确认技术栈。
6. 修改核心架构前先确认。
