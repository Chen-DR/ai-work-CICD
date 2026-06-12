# AI-Ops 容器打包与服务器压测平台：完整架构与开发说明

版本：v1.0  
技术栈：Vue 3 + Django + Django REST Framework + SQLite + Celery + Redis + Paramiko + DeepSeek API  
数据库方案：SQLite 轻量化起步，后续可升级 PostgreSQL / pgvector  
部署形态：单机 Docker Compose 起步，后续可升级 Kubernetes  
文档用途：项目架构说明、开发说明、接口规划、数据库设计、MVP 开发指导

---

# 目录

1. 项目概述  
2. 需求范围  
3. 总体技术选型  
4. 系统总体架构  
5. 前端架构设计  
6. 后端架构设计  
7. SQLite 数据库设计  
8. 文件存储设计  
9. 知识库设计  
10. DeepSeek 对话与 AI 编排设计  
11. Apptainer 容器打包设计  
12. 服务器压测设计  
13. 远程执行与安全策略  
14. Celery 异步任务设计  
15. 实时日志与报告回传设计  
16. API 接口设计  
17. Django 目录结构与开发规范  
18. Vue 目录结构与开发规范  
19. 关键代码骨架  
20. 部署方案  
21. 环境变量说明  
22. 安全设计  
23. 日志、监控与审计  
24. MVP 开发计划  
25. 后续演进路线  
26. 风险点与解决方案  
27. 验收标准  
28. 附录：示例配置与模板

---

# 1. 项目概述

本项目是一个基于 AI 对话的容器打包与服务器压测平台。系统通过 Vue 前端提供操作界面，通过 Django 后端提供业务 API，通过 DeepSeek API 实现自然语言生成能力，通过知识库实现 RAG 增强，通过 Celery 执行长耗时任务，通过 Paramiko 远程连接服务器执行 Apptainer 构建和压测脚本，通过 SQLite 保存轻量业务数据。

系统需要支持两条核心业务链路：

第一条链路是容器打包：

```text
用户自然语言描述容器需求
  ↓
系统检索知识库
  ↓
调用 DeepSeek API 生成 Apptainer definition file
  ↓
用户确认或编辑 definition file
  ↓
选择服务器、账号、目录
  ↓
后端创建构建任务
  ↓
Celery Worker 通过 SSH/SFTP 上传文件
  ↓
远程执行 apptainer build
  ↓
采集日志
  ↓
记录构建结果
```

第二条链路是服务器压测：

```text
用户上传 CPU / 硬盘 / GPU 压测脚本
  ↓
选择目标服务器
  ↓
填写账号、密码、目录、压测参数
  ↓
后端校验参数和目录
  ↓
Celery Worker 上传脚本
  ↓
远程执行压测
  ↓
等待脚本生成报告
  ↓
SFTP 下载报告到本地
  ↓
前端展示任务结果并提供下载
```

知识库贯穿对话生成过程，用于提升 DeepSeek 生成质量，使生成结果优先符合项目内部规范、历史经验、服务器环境说明、Apptainer 编写要求和压测脚本说明。

---

# 2. 需求范围

## 2.1 容器打包需求

容器打包模块需要支持：

1. 用户通过对话描述 Apptainer 容器环境需求。
2. 后端调用 DeepSeek API 生成 Apptainer definition file。
3. 生成过程中优先使用知识库内容。
4. 用户可以查看、编辑、保存生成的 definition file。
5. 系统保存 definition file 的历史版本。
6. 用户可以选择指定服务器和指定目录执行构建。
7. 系统通过 SSH/SFTP 上传 definition file。
8. 系统远程执行 `apptainer build`。
9. 系统采集构建日志。
10. 构建完成后记录 SIF 文件路径。
11. 构建失败时记录错误日志和失败原因。

## 2.2 服务器压测需求

服务器压测模块需要支持：

1. 用户上传压测脚本。
2. 脚本类型包括 CPU、硬盘、GPU、混合、自定义。
3. 用户配置服务器 IP、端口、账号、密码或 SSH key。
4. 用户配置远程工作目录。
5. 用户填写压测参数。
6. 系统校验参数和目录是否合法。
7. 系统上传脚本到远程服务器。
8. 系统在指定目录执行压测脚本。
9. 系统采集压测日志。
10. 压测脚本生成报告后，系统自动回传到本地。
11. 用户可以下载报告。
12. 用户可以查看历史压测任务。

## 2.3 知识库需求

知识库模块需要支持：

1. 上传内部文档。
2. 上传历史 Apptainer def 文件。
3. 上传压测脚本说明。
4. 上传服务器环境说明。
5. 上传错误日志和解决方案。
6. 文档解析、切片、检索。
7. 对话时优先检索知识库内容。
8. 支持项目级知识库隔离。

## 2.4 管理需求

系统需要支持：

1. 用户登录。
2. 项目空间。
3. 服务器管理。
4. 任务管理。
5. 文件产物管理。
6. 审计日志。
7. 错误追踪。
8. 基础权限控制。

---

# 3. 总体技术选型

## 3.1 前端

```text
Vue 3
TypeScript
Vite
Element Plus
Pinia
Vue Router
Axios
Monaco Editor 或 CodeMirror
SSE / 轮询
```

说明：

- Vue 3 用于构建前端控制台。
- TypeScript 提升代码可维护性。
- Element Plus 提供后台系统 UI 组件。
- Pinia 管理用户、项目、任务状态。
- Monaco Editor 或 CodeMirror 用于编辑 Apptainer definition file、脚本和查看日志。
- SSE 或轮询用于实时日志展示。

## 3.2 后端

```text
Python 3.11+
Django 4.2 LTS 或 Django 5.x
Django REST Framework
Celery
Redis
SQLite
Paramiko
Requests / httpx
python-dotenv
cryptography
```

说明：

- Django 提供成熟的业务模型、权限、管理后台能力。
- DRF 提供 REST API 能力。
- Celery 负责长耗时任务。
- Redis 作为 Celery Broker 和状态缓存。
- SQLite 用于轻量级数据库。
- Paramiko 用于远程 SSH/SFTP。
- cryptography 用于加密服务器密码和私钥。

## 3.3 AI 模型

```text
DeepSeek API
```

后端封装统一 LLM Client。业务层不直接调用 HTTP API，而是通过 `DeepSeekClient` 调用，便于后续更换模型或增加模型路由。

## 3.4 数据库

MVP 使用：

```text
SQLite
```

后续可升级：

```text
PostgreSQL
PostgreSQL + pgvector
```

SQLite 使用原则：

- 只保存业务元数据。
- 不存大文件。
- 不高频写入日志。
- 文件和报告保存到文件系统。
- 通过 Django ORM 保持迁移兼容性。

## 3.5 文件存储

MVP 使用：

```text
本地文件系统
```

后续可升级：

```text
MinIO
S3
企业对象存储
```

---

# 4. 系统总体架构

## 4.1 总体架构图

```text
┌──────────────────────────────────────────────────────────────┐
│                           用户层                              │
│                                                              │
│  管理员 / 开发人员 / 运维人员 / 测试人员                       │
└───────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│                         Vue 前端层                            │
│                                                              │
│  登录 / 项目 / 对话 / 知识库 / Apptainer / 压测 / 服务器 / 报告 │
└───────────────────────────────┬──────────────────────────────┘
                                │ HTTP / SSE / 轮询
                                ▼
┌──────────────────────────────────────────────────────────────┐
│                       Django API 层                           │
│                                                              │
│  DRF ViewSet / Serializer / Permission / Pagination / Filter  │
└───────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────┐
│                       Django 业务层                           │
│                                                              │
│  accounts    用户与权限                                       │
│  projects    项目空间                                         │
│  chat        对话与 DeepSeek 调用                              │
│  knowledge   知识库                                            │
│  apptainer   容器定义与构建任务                                 │
│  benchmark   压测脚本与压测任务                                 │
│  servers     服务器与凭据管理                                   │
│  artifacts   文件产物                                          │
│  audit       审计日志                                          │
└───────────────────────────────┬──────────────────────────────┘
                                │
          ┌─────────────────────┼──────────────────────┐
          ▼                     ▼                      ▼
┌───────────────────┐ ┌───────────────────┐  ┌───────────────────┐
│    Celery Worker   │ │      SQLite        │  │   文件系统/MinIO    │
│                   │ │                   │  │                   │
│  远程构建           │ │  业务元数据         │  │  def 文件           │
│  远程压测           │ │  任务状态           │  │  压测脚本           │
│  报告回传           │ │  对话记录           │  │  报告               │
│  知识库解析         │ │  知识库索引         │  │  日志               │
└─────────┬─────────┘ └───────────────────┘  └───────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────────────────┐
│                         远程服务器                            │
│                                                              │
│  Apptainer build / CPU 压测 / 硬盘压测 / GPU 压测 / 报告生成     │
└──────────────────────────────────────────────────────────────┘
```

## 4.2 系统核心原则

系统必须遵守以下原则：

1. 前端只负责交互，不负责拼接远程命令。
2. DeepSeek 只负责生成和分析，不直接执行服务器命令。
3. Django 负责业务规则、权限、安全校验、任务创建。
4. Celery 负责长耗时任务。
5. Paramiko 只执行经过后端模板生成和安全策略校验的命令。
6. SQLite 只保存业务元数据。
7. 日志、脚本、报告、def 文件保存到文件系统。
8. 所有远程执行动作必须有审计记录。
9. 所有服务器凭据必须加密保存。
10. 用户执行任务前必须明确选择服务器和目录。

---

# 5. 前端架构设计

## 5.1 前端目录结构

```text
frontend/
  package.json
  vite.config.ts
  tsconfig.json
  index.html
  src/
    main.ts
    App.vue

    router/
      index.ts

    stores/
      user.ts
      project.ts
      job.ts
      app.ts

    api/
      request.ts
      auth.ts
      projects.ts
      chat.ts
      knowledge.ts
      apptainer.ts
      benchmark.ts
      servers.ts
      artifacts.ts
      audit.ts

    views/
      Login/
        index.vue
      Dashboard/
        index.vue
      Projects/
        index.vue
      ChatWorkbench/
        index.vue
      KnowledgeBase/
        index.vue
      Apptainer/
        DefinitionList.vue
        DefinitionEditor.vue
        BuildJobList.vue
        BuildJobDetail.vue
      Benchmark/
        ScriptList.vue
        ScriptUpload.vue
        JobList.vue
        JobDetail.vue
      Servers/
        ServerList.vue
        ServerForm.vue
        ServerDetail.vue
      Artifacts/
        index.vue
      AuditLogs/
        index.vue
      Settings/
        index.vue

    components/
      ChatPanel/
        ChatMessage.vue
        ChatInput.vue
        ReferencePanel.vue
      CodeEditor/
        index.vue
      FileUploader/
        index.vue
      LogViewer/
        index.vue
      JobStatusTag/
        index.vue
      ServerSelector/
        index.vue
      ProjectSelector/
        index.vue
      ReportViewer/
        index.vue

    types/
      user.ts
      project.ts
      chat.ts
      knowledge.ts
      apptainer.ts
      benchmark.ts
      server.ts
      artifact.ts

    utils/
      auth.ts
      date.ts
      file.ts
      sse.ts
      validators.ts

    styles/
      global.scss
```

## 5.2 前端页面清单

### 5.2.1 登录页

功能：

- 用户输入用户名和密码。
- 调用登录接口。
- 保存 token。
- 登录后跳转到仪表盘。
- token 失效后自动跳转登录页。

### 5.2.2 仪表盘

展示：

- 项目数量。
- 知识库文档数量。
- Apptainer 构建任务数量。
- 压测任务数量。
- 最近失败任务。
- 最近生成报告。

### 5.2.3 项目空间页

功能：

- 创建项目。
- 编辑项目。
- 删除项目。
- 切换当前项目。
- 查看项目成员。

说明：

项目是数据隔离边界。服务器、知识库、任务、报告均归属于项目。

### 5.2.4 对话工作台

功能：

- 创建对话。
- 发送消息。
- 开启或关闭知识库增强。
- 查看知识库引用。
- 保存 DeepSeek 生成内容。
- 一键生成 Apptainer definition file。
- 从对话结果跳转到 definition 编辑器。

布局建议：

```text
左侧：对话列表
中间：聊天内容
右侧：知识库引用 / 生成结果 / 操作按钮
```

### 5.2.5 知识库管理页

功能：

- 上传文档。
- 查看解析状态。
- 查看切片结果。
- 删除文档。
- 手动触发重新解析。
- 测试检索。

MVP 支持文件格式：

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

后续支持：

```text
.pdf
.docx
.xlsx
```

### 5.2.6 Apptainer 定义文件页

功能：

- 查看 definition 文件列表。
- 创建 definition。
- 编辑 definition。
- 查看版本。
- 校验 definition。
- 创建构建任务。

### 5.2.7 Apptainer 构建任务页

功能：

- 查看构建任务列表。
- 查看任务状态。
- 查看构建日志。
- 查看失败原因。
- 查看 SIF 输出路径。
- 下载日志。
- 取消任务。

### 5.2.8 压测脚本页

功能：

- 上传压测脚本。
- 设置脚本类型。
- 填写脚本说明。
- 管理脚本版本。
- 删除脚本。

### 5.2.9 压测任务页

功能：

- 创建压测任务。
- 选择服务器。
- 选择脚本。
- 填写参数。
- 查看执行日志。
- 下载报告。
- 查看历史任务。

### 5.2.10 服务器管理页

功能：

- 新增服务器。
- 编辑服务器信息。
- 配置认证方式。
- 配置允许目录。
- 测试连接。
- 检测环境。
- 删除服务器。

### 5.2.11 文件产物页

功能：

- 查看 def 文件。
- 查看构建日志。
- 查看压测脚本。
- 查看压测报告。
- 下载文件。
- 删除文件。

### 5.2.12 审计日志页

功能：

- 查看用户操作记录。
- 查看远程执行记录。
- 查看服务器访问记录。
- 根据用户、项目、任务、时间过滤。

---

# 6. 后端架构设计

## 6.1 Django 项目目录结构

```text
backend/
  manage.py
  requirements.txt
  .env.example
  README.md

  config/
    __init__.py
    settings.py
    urls.py
    asgi.py
    wsgi.py
    celery.py

  apps/
    accounts/
      __init__.py
      models.py
      serializers.py
      views.py
      permissions.py
      urls.py
      admin.py

    projects/
      __init__.py
      models.py
      serializers.py
      views.py
      urls.py
      admin.py

    chat/
      __init__.py
      models.py
      serializers.py
      views.py
      services.py
      prompts.py
      urls.py
      admin.py

    knowledge/
      __init__.py
      models.py
      serializers.py
      views.py
      services.py
      parsers.py
      search.py
      tasks.py
      urls.py
      admin.py

    apptainer/
      __init__.py
      models.py
      serializers.py
      views.py
      services.py
      validators.py
      tasks.py
      urls.py
      admin.py

    benchmark/
      __init__.py
      models.py
      serializers.py
      views.py
      services.py
      validators.py
      tasks.py
      urls.py
      admin.py

    servers/
      __init__.py
      models.py
      serializers.py
      views.py
      services.py
      crypto.py
      urls.py
      admin.py

    artifacts/
      __init__.py
      models.py
      serializers.py
      views.py
      services.py
      urls.py
      admin.py

    audit/
      __init__.py
      models.py
      serializers.py
      views.py
      services.py
      urls.py
      admin.py

    common/
      __init__.py
      models.py
      exceptions.py
      response.py
      pagination.py
      permissions.py
      storage.py
      constants.py
      validators.py

  infrastructure/
    llm/
      __init__.py
      base.py
      deepseek_client.py

    ssh/
      __init__.py
      executor.py
      policy.py
      sftp.py
      path_utils.py

    storage/
      __init__.py
      local_storage.py
      minio_storage.py

    rag/
      __init__.py
      splitter.py
      keyword_search.py
      retriever.py

    security/
      __init__.py
      encryptor.py
      command_sanitizer.py
      secret_masker.py

  data/
    db.sqlite3
    uploads/
    artifacts/
    logs/
    reports/
    knowledge/
    apptainer/
    benchmark/
```

## 6.2 Django App 职责

### accounts

负责用户、认证、权限。

MVP 可使用：

- Django 默认 User。
- DRF TokenAuthentication 或 JWT。
- 简单角色字段。

角色建议：

```text
admin
developer
operator
viewer
```

权限说明：

```text
admin      管理所有资源
developer  创建知识库、生成容器文件
operator   执行构建和压测任务
viewer     只读任务、日志、报告
```

### projects

负责项目空间。

项目下包含：

- 会话。
- 知识库。
- 服务器。
- 容器定义。
- 构建任务。
- 压测脚本。
- 压测任务。
- 文件产物。
- 审计日志。

### chat

负责：

- 会话管理。
- 消息管理。
- DeepSeek 调用。
- Prompt 构造。
- RAG 注入。
- 生成 Apptainer def。

### knowledge

负责：

- 文档上传。
- 文档解析。
- 文档切片。
- 关键词检索。
- 后续向量检索扩展。

### apptainer

负责：

- definition file 管理。
- 版本管理。
- definition 校验。
- 构建任务创建。
- 构建日志查询。

### benchmark

负责：

- 压测脚本管理。
- 压测任务管理。
- 参数校验。
- 报告回传状态。

### servers

负责：

- 服务器配置。
- SSH 凭据。
- 允许目录。
- 连接测试。
- 环境检测。

### artifacts

负责：

- 文件元数据。
- 文件下载。
- 文件删除。
- 文件归档。

### audit

负责：

- 用户行为审计。
- 远程执行审计。
- 任务状态变更审计。

---

# 7. SQLite 数据库设计

## 7.1 数据库设计原则

SQLite 适合轻量单机部署，但不适合高并发写入。因此设计时要注意：

1. 数据库只存业务元数据。
2. 大文件不入库。
3. 长日志不逐行入库。
4. 报告文件不入库。
5. 脚本文件不入库。
6. knowledge chunk 可以入库，但文档原文件放文件系统。
7. 任务日志保存文件路径。
8. 尽量使用 Django ORM 标准字段，方便迁移 PostgreSQL。

## 7.2 状态枚举

任务状态统一：

```text
PENDING       等待执行
VALIDATING    校验中
UPLOADING     上传中
RUNNING       运行中
COLLECTING    收集报告中
SUCCESS       成功
FAILED        失败
CANCELLED     已取消
TIMEOUT       超时
```

知识库文档状态：

```text
UPLOADED      已上传
PARSING       解析中
READY         可用
FAILED        失败
```

服务器状态：

```text
ACTIVE        可用
DISABLED      禁用
UNKNOWN       未检测
FAILED        连接失败
```

## 7.3 数据表设计

### users

如果使用 Django 默认 User，则不需要手写用户表。可以扩展 Profile：

```text
UserProfile
  id
  user
  display_name
  role
  created_at
  updated_at
```

### projects

```text
Project
  id
  name
  description
  owner_id
  created_at
  updated_at
```

### project_members

```text
ProjectMember
  id
  project_id
  user_id
  role
  created_at
```

### conversations

```text
Conversation
  id
  project_id
  user_id
  title
  model_name
  created_at
  updated_at
```

### messages

```text
Message
  id
  conversation_id
  role
  content
  created_at
```

role：

```text
user
assistant
system
tool
```

### llm_calls

```text
LLMCall
  id
  project_id
  conversation_id
  provider
  model_name
  request_payload
  response_payload
  prompt_tokens
  completion_tokens
  latency_ms
  status
  error_message
  created_at
```

### knowledge_documents

```text
KnowledgeDocument
  id
  project_id
  title
  file_name
  file_type
  storage_path
  status
  error_message
  created_by_id
  created_at
  updated_at
```

### knowledge_chunks

```text
KnowledgeChunk
  id
  document_id
  project_id
  chunk_index
  content
  metadata
  created_at
```

说明：

- metadata 可使用 JSONField。
- SQLite 阶段不强制保存 embedding。
- 后续迁移 PostgreSQL 后可增加 vector 字段。

### servers

```text
Server
  id
  project_id
  name
  host
  port
  username
  auth_type
  status
  created_at
  updated_at
```

auth_type：

```text
password
ssh_key
```

### server_credentials

```text
ServerCredential
  id
  server_id
  credential_type
  encrypted_secret
  secret_hint
  created_at
  updated_at
```

### server_allowed_dirs

```text
ServerAllowedDir
  id
  server_id
  path
  purpose
  created_at
```

purpose：

```text
build
benchmark
report
general
```

### apptainer_definitions

```text
ApptainerDefinition
  id
  project_id
  conversation_id
  name
  version
  content
  storage_path
  created_by_id
  created_at
  updated_at
```

### apptainer_build_jobs

```text
ApptainerBuildJob
  id
  project_id
  definition_id
  server_id
  workdir
  output_name
  status
  celery_task_id
  log_path
  remote_output_path
  started_at
  finished_at
  error_message
  created_by_id
  created_at
  updated_at
```

### benchmark_scripts

```text
BenchmarkScript
  id
  project_id
  name
  script_type
  version
  file_name
  storage_path
  description
  created_by_id
  created_at
  updated_at
```

script_type：

```text
cpu
disk
gpu
mixed
custom
```

### benchmark_jobs

```text
BenchmarkJob
  id
  project_id
  script_id
  server_id
  workdir
  params
  status
  celery_task_id
  log_path
  report_path
  remote_report_path
  started_at
  finished_at
  error_message
  created_by_id
  created_at
  updated_at
```

### artifacts

```text
Artifact
  id
  project_id
  job_type
  job_id
  artifact_type
  file_name
  storage_path
  file_size
  checksum
  created_at
```

artifact_type：

```text
knowledge_file
apptainer_def
build_log
sif_path_record
benchmark_script
benchmark_log
benchmark_report
```

### audit_logs

```text
AuditLog
  id
  project_id
  user_id
  action
  resource_type
  resource_id
  ip_address
  detail
  created_at
```

## 7.4 数据库关系图

```text
User
  ├── Project
  │     ├── ProjectMember
  │     ├── Conversation
  │     │     ├── Message
  │     │     └── LLMCall
  │     ├── KnowledgeDocument
  │     │     └── KnowledgeChunk
  │     ├── Server
  │     │     ├── ServerCredential
  │     │     └── ServerAllowedDir
  │     ├── ApptainerDefinition
  │     │     └── ApptainerBuildJob
  │     ├── BenchmarkScript
  │     │     └── BenchmarkJob
  │     ├── Artifact
  │     └── AuditLog
```

## 7.5 SQLite 设置

settings.py：

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "data" / "db.sqlite3",
        "OPTIONS": {
            "timeout": 30,
        },
    }
}
```

建议启用 WAL：

```python
# apps/common/apps.py

from django.apps import AppConfig
from django.db import connection

class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"

    def ready(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.execute("PRAGMA synchronous=NORMAL;")
                cursor.execute("PRAGMA busy_timeout=30000;")
        except Exception:
            pass
```

---

# 8. 文件存储设计

## 8.1 本地存储目录

建议：

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

## 8.2 存储原则

1. 数据库只保存 storage_path。
2. 文件名必须重新生成，避免用户上传文件名污染路径。
3. 原始文件名可保存到 file_name。
4. 禁止路径穿越。
5. 文件下载必须做权限校验。
6. 定期清理临时文件。

## 8.3 Artifact 设计

Artifact 是统一文件产物索引。所有文件都应该能通过 Artifact 查询。

示例：

```json
{
  "project_id": 1,
  "job_type": "benchmark",
  "job_id": 12,
  "artifact_type": "benchmark_report",
  "file_name": "report.html",
  "storage_path": "data/artifacts/benchmark/reports/job_12/report.html",
  "file_size": 123456,
  "checksum": "sha256..."
}
```

---

# 9. 知识库设计

## 9.1 知识库内容类型

知识库建议包含：

1. Apptainer 编写规范。
2. 历史 definition file。
3. 服务器环境说明。
4. CUDA / Python / 编译器版本说明。
5. 压测脚本说明。
6. 常见错误日志。
7. 内部 SOP。
8. 项目 README。
9. 部署手册。

## 9.2 知识库处理流程

```text
上传文件
  ↓
保存原始文件
  ↓
创建 KnowledgeDocument
  ↓
Celery 解析文档
  ↓
清洗文本
  ↓
切片
  ↓
保存 KnowledgeChunk
  ↓
状态变为 READY
```

## 9.3 文档切片规则

建议：

```text
chunk_size = 800 中文字符左右
chunk_overlap = 100～150 字符
```

保留 metadata：

```json
{
  "file_name": "apptainer-guide.md",
  "chunk_index": 1,
  "title": "Apptainer 构建规范"
}
```

## 9.4 检索策略

MVP 可采用关键词检索：

```text
query
  ↓
提取关键词
  ↓
KnowledgeChunk.content icontains 查询
  ↓
简单评分
  ↓
返回 Top-K
```

后续增强：

```text
SQLite FTS5
本地 Chroma / FAISS
PostgreSQL + pgvector
```

## 9.5 RAG 注入格式

Prompt 中注入：

```text
以下是知识库中与用户问题相关的内容，请优先参考：

[知识片段 1]
文档：xxx.md
内容：...

[知识片段 2]
文档：yyy.md
内容：...
```

---

# 10. DeepSeek 对话与 AI 编排设计

## 10.1 LLM Client

文件：

```text
infrastructure/llm/deepseek_client.py
```

职责：

1. 封装 DeepSeek API。
2. 统一请求格式。
3. 统一响应格式。
4. 处理异常。
5. 记录调用日志。
6. 支持超时和重试。
7. 支持模型名从环境变量读取。

伪代码：

```python
import httpx

class DeepSeekClient:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def chat(self, messages: list[dict], temperature: float = 0.2) -> dict:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        with httpx.Client(timeout=120) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()
```

## 10.2 对话流程

```text
用户发送消息
  ↓
Django 接收请求
  ↓
读取 Conversation 历史消息
  ↓
如果 use_knowledge=true，检索知识库
  ↓
构造 system prompt
  ↓
构造 messages
  ↓
调用 DeepSeek
  ↓
保存用户消息
  ↓
保存助手消息
  ↓
保存 LLMCall
  ↓
返回前端
```

## 10.3 生成 Apptainer Prompt

示例：

```text
你是一个 Apptainer 容器构建专家。
请根据用户需求和知识库上下文生成 Apptainer definition file。

要求：
1. 输出内容必须适用于 Apptainer。
2. 必须包含 Bootstrap 和 From。
3. 尽量包含 %post、%environment、%runscript。
4. 不要生成危险命令。
5. 不要直接使用 sudo rm、curl | bash、wget | bash。
6. 如果用户没有说明基础镜像，请使用合理默认值并说明假设。
7. 如果用户提到 GPU，请考虑 CUDA、驱动兼容和运行时环境。
8. 输出先给 definition file，再给简短说明。
```

## 10.4 输出校验

DeepSeek 生成后，后端需要校验：

1. 是否包含 `Bootstrap:`。
2. 是否包含 `From:`。
3. 是否包含危险命令。
4. 是否含有路径穿越。
5. 是否含有高风险系统修改。
6. 是否符合基本 Apptainer def 结构。

---

# 11. Apptainer 容器打包设计

## 11.1 Definition 文件管理

用户可以通过三种方式创建 definition：

1. 对话生成。
2. 手动创建。
3. 上传已有 def 文件。

保存字段：

```text
name
version
content
storage_path
project
created_by
```

版本规则：

```text
v1
v2
v3
```

或：

```text
1
2
3
```

## 11.2 生成流程

```text
用户输入需求
  ↓
Chat Service 获取上下文
  ↓
Knowledge Service 检索相关片段
  ↓
Prompt Builder 组装 prompt
  ↓
DeepSeek 生成 def 内容
  ↓
Apptainer Validator 校验
  ↓
保存 ApptainerDefinition
  ↓
返回前端
```

## 11.3 构建流程

```text
用户选择 definition
  ↓
选择服务器
  ↓
输入 workdir
  ↓
输入 output_name
  ↓
后端校验
  ↓
创建 ApptainerBuildJob
  ↓
提交 Celery 任务
  ↓
任务状态 PENDING
  ↓
Celery 开始执行
  ↓
状态 VALIDATING
  ↓
状态 UPLOADING
  ↓
SFTP 上传 definition file
  ↓
状态 RUNNING
  ↓
执行 apptainer build
  ↓
写入日志
  ↓
状态 COLLECTING
  ↓
检查输出文件
  ↓
保存 Artifact
  ↓
状态 SUCCESS 或 FAILED
```

## 11.4 构建命令模板

```bash
cd {workdir} && apptainer build {output_name} {definition_file}
```

可扩展参数：

```bash
apptainer build --fakeroot {output_name} {definition_file}
apptainer build --force {output_name} {definition_file}
```

MVP 阶段建议只开放基础构建参数，不让用户自由输入命令。

## 11.5 构建日志

日志保存：

```text
data/artifacts/apptainer/logs/build_job_{job_id}.log
```

数据库：

```text
ApptainerBuildJob.log_path
```

前端通过 logs API 读取日志尾部。

---

# 12. 服务器压测设计

## 12.1 压测脚本管理

脚本字段：

```text
name
script_type
version
file_name
storage_path
description
created_by
```

脚本类型：

```text
cpu
disk
gpu
mixed
custom
```

## 12.2 压测参数

params 使用 JSON 保存：

```json
{
  "duration": 300,
  "threads": 16,
  "mode": "gpu",
  "report_file": "report.html"
}
```

参数要求：

1. 参数名只能包含字母、数字、下划线、中划线。
2. 参数值不能包含 `;`、`&&`、`|`、反引号、`$()`。
3. report_file 只能是文件名，不能是绝对路径。
4. workdir 必须在服务器 allowed_dirs 内。
5. duration 必须有最大限制。

## 12.3 压测执行流程

```text
用户创建压测任务
  ↓
后端创建 BenchmarkJob
  ↓
提交 Celery 任务
  ↓
Celery 校验服务器和脚本
  ↓
SFTP 上传脚本
  ↓
chmod +x
  ↓
执行脚本
  ↓
采集 stdout/stderr
  ↓
等待报告生成
  ↓
SFTP 下载报告
  ↓
保存 Artifact
  ↓
更新任务状态
```

## 12.4 压测命令模板

```bash
cd {workdir} && chmod +x {script_file} && ./{script_file} --duration {duration} --threads {threads} --report-file {report_file}
```

禁止用户传入完整 shell 命令。

## 12.5 报告回传

报告查找规则：

1. 用户明确提供 `report_file`。
2. 或脚本约定输出到 `reports/` 目录。
3. 后端在远程目录检查报告是否存在。
4. 存在后 SFTP 下载。
5. 本地保存到：

```text
data/artifacts/benchmark/reports/job_{job_id}/
```

---

# 13. 远程执行与安全策略

## 13.1 远程执行原则

远程执行是系统最高风险模块，必须遵守：

1. 不允许前端传完整 shell。
2. 不允许 DeepSeek 输出直接被执行。
3. 只允许后端 action 模板生成命令。
4. 所有命令执行前必须经过策略校验。
5. 所有参数必须白名单校验。
6. 所有目录必须在 allowed_dirs 内。
7. 所有执行必须记录审计日志。

## 13.2 SSH Executor

文件：

```text
infrastructure/ssh/executor.py
```

接口：

```python
class SSHExecutor:
    def test_connection(self, server):
        pass

    def run_command(self, server, command, timeout=None, log_callback=None):
        pass

    def upload_file(self, server, local_path, remote_path):
        pass

    def download_file(self, server, remote_path, local_path):
        pass

    def file_exists(self, server, remote_path):
        pass

    def mkdir(self, server, remote_path):
        pass
```

## 13.3 Command Policy Engine

文件：

```text
infrastructure/ssh/policy.py
```

允许 action：

```text
apptainer_build
apptainer_test
benchmark_run
collect_report
cleanup_workdir
detect_environment
```

禁止命令特征：

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

## 13.4 目录白名单

每台服务器配置 allowed_dirs：

```text
/data/builds
/data/benchmark
/home/user/aiops
```

检查：

```python
def is_allowed_path(workdir: str, allowed_dirs: list[str]) -> bool:
    normalized = os.path.abspath(workdir)
    return any(normalized.startswith(os.path.abspath(base)) for base in allowed_dirs)
```

需要防止：

```text
/data/builds/../../etc
```

---

# 14. Celery 异步任务设计

## 14.1 Celery 架构

```text
Django API
  ↓
创建 Job
  ↓
Celery delay(job_id)
  ↓
Redis Broker
  ↓
Celery Worker
  ↓
远程执行
  ↓
更新 Job 状态
```

## 14.2 Celery 配置

```python
# config/celery.py

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("aiops")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```

settings.py：

```python
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/1"
CELERY_TASK_TIME_LIMIT = 7200
CELERY_TASK_SOFT_TIME_LIMIT = 7000
```

## 14.3 任务清单

```text
parse_knowledge_document_task
generate_apptainer_definition_task
run_apptainer_build_task
run_benchmark_job_task
collect_report_task
detect_server_environment_task
cleanup_temp_files_task
```

## 14.4 Apptainer 构建任务步骤

```text
1. 读取 job。
2. 状态更新为 VALIDATING。
3. 校验服务器和目录。
4. 校验 definition。
5. 状态更新为 UPLOADING。
6. 创建远程目录。
7. 上传 definition file。
8. 状态更新为 RUNNING。
9. 执行 apptainer build。
10. 将 stdout/stderr 写入日志文件。
11. 状态更新为 COLLECTING。
12. 检查 SIF 文件是否存在。
13. 保存 artifact。
14. 状态更新为 SUCCESS。
15. 如果异常，状态更新为 FAILED。
```

## 14.5 压测任务步骤

```text
1. 读取 job。
2. 状态更新为 VALIDATING。
3. 校验脚本、参数、服务器、目录。
4. 状态更新为 UPLOADING。
5. 上传脚本。
6. 状态更新为 RUNNING。
7. chmod +x。
8. 执行脚本。
9. 写日志。
10. 状态更新为 COLLECTING。
11. 检查报告文件。
12. 下载报告。
13. 保存 artifact。
14. 状态更新为 SUCCESS。
15. 如果异常，状态更新为 FAILED。
```

---

# 15. 实时日志与报告回传设计

## 15.1 日志保存策略

不建议逐行写数据库。建议写本地文件：

```text
data/logs/jobs/apptainer_build_{job_id}.log
data/logs/jobs/benchmark_{job_id}.log
```

Job 表中保存：

```text
log_path
```

## 15.2 日志读取接口

示例：

```text
GET /api/v1/apptainer/build-jobs/{id}/logs/?tail=200
GET /api/v1/benchmark/jobs/{id}/logs/?tail=200
```

后端读取日志最后 N 行返回。

## 15.3 日志展示方案

MVP：

```text
前端每 2 秒轮询 logs API
```

增强版：

```text
SSE
```

再增强：

```text
Django Channels WebSocket
```

建议 MVP 使用轮询或 SSE，简单稳定。

## 15.4 报告回传

报告下载流程：

```text
远程报告路径
  ↓
SFTP 下载
  ↓
保存本地 artifacts/reports
  ↓
创建 Artifact
  ↓
前端展示下载按钮
```

---

# 16. API 接口设计

## 16.1 通用响应格式

成功：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

失败：

```json
{
  "code": 40001,
  "message": "参数错误",
  "data": {
    "field": "server_id"
  }
}
```

## 16.2 错误码

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

## 16.3 认证接口

```text
POST /api/v1/auth/login/
POST /api/v1/auth/logout/
GET  /api/v1/auth/me/
```

登录请求：

```json
{
  "username": "admin",
  "password": "password"
}
```

## 16.4 项目接口

```text
GET    /api/v1/projects/
POST   /api/v1/projects/
GET    /api/v1/projects/{id}/
PUT    /api/v1/projects/{id}/
DELETE /api/v1/projects/{id}/
```

## 16.5 对话接口

```text
GET    /api/v1/chat/conversations/
POST   /api/v1/chat/conversations/
GET    /api/v1/chat/conversations/{id}/
DELETE /api/v1/chat/conversations/{id}/

GET    /api/v1/chat/conversations/{id}/messages/
POST   /api/v1/chat/conversations/{id}/messages/
POST   /api/v1/chat/complete/
```

complete 请求：

```json
{
  "project_id": 1,
  "conversation_id": 12,
  "message": "帮我生成 Ubuntu 22.04 + Python 3.10 + CUDA 的 Apptainer",
  "use_knowledge": true
}
```

返回：

```json
{
  "answer": "生成内容...",
  "references": [
    {
      "document_id": 1,
      "document_title": "cuda-guide.md",
      "chunk_id": 3,
      "content": "相关知识片段"
    }
  ]
}
```

## 16.6 知识库接口

```text
GET    /api/v1/knowledge/documents/
POST   /api/v1/knowledge/documents/
GET    /api/v1/knowledge/documents/{id}/
DELETE /api/v1/knowledge/documents/{id}/
POST   /api/v1/knowledge/documents/{id}/parse/
GET    /api/v1/knowledge/search/
```

检索请求：

```json
{
  "project_id": 1,
  "query": "CUDA 12.1 Apptainer",
  "top_k": 5
}
```

## 16.7 Apptainer 接口

```text
GET    /api/v1/apptainer/definitions/
POST   /api/v1/apptainer/definitions/
GET    /api/v1/apptainer/definitions/{id}/
PUT    /api/v1/apptainer/definitions/{id}/
DELETE /api/v1/apptainer/definitions/{id}/

POST   /api/v1/apptainer/generate/
POST   /api/v1/apptainer/build-jobs/
GET    /api/v1/apptainer/build-jobs/
GET    /api/v1/apptainer/build-jobs/{id}/
GET    /api/v1/apptainer/build-jobs/{id}/logs/
POST   /api/v1/apptainer/build-jobs/{id}/cancel/
```

生成请求：

```json
{
  "project_id": 1,
  "conversation_id": 12,
  "requirement": "Ubuntu 22.04 + Python 3.10 + CUDA 12.1 + PyTorch",
  "use_knowledge": true
}
```

构建请求：

```json
{
  "project_id": 1,
  "definition_id": 10,
  "server_id": 2,
  "workdir": "/data/builds/job_1001",
  "output_name": "my_image.sif"
}
```

## 16.8 压测接口

```text
GET    /api/v1/benchmark/scripts/
POST   /api/v1/benchmark/scripts/
GET    /api/v1/benchmark/scripts/{id}/
DELETE /api/v1/benchmark/scripts/{id}/

POST   /api/v1/benchmark/jobs/
GET    /api/v1/benchmark/jobs/
GET    /api/v1/benchmark/jobs/{id}/
GET    /api/v1/benchmark/jobs/{id}/logs/
POST   /api/v1/benchmark/jobs/{id}/cancel/
```

创建任务请求：

```json
{
  "project_id": 1,
  "script_id": 5,
  "server_id": 2,
  "workdir": "/data/benchmark/job_2001",
  "params": {
    "duration": 300,
    "threads": 16,
    "report_file": "report.html"
  }
}
```

## 16.9 服务器接口

```text
GET    /api/v1/servers/
POST   /api/v1/servers/
GET    /api/v1/servers/{id}/
PUT    /api/v1/servers/{id}/
DELETE /api/v1/servers/{id}/
POST   /api/v1/servers/{id}/test/
POST   /api/v1/servers/{id}/detect/
```

## 16.10 文件产物接口

```text
GET    /api/v1/artifacts/
GET    /api/v1/artifacts/{id}/
GET    /api/v1/artifacts/{id}/download/
DELETE /api/v1/artifacts/{id}/
```

## 16.11 审计接口

```text
GET /api/v1/audit/logs/
```

---

# 17. Django 目录结构与开发规范

## 17.1 分层规范

Django 每个 app 建议分层：

```text
models.py       数据模型
serializers.py  参数校验和响应序列化
views.py        API 入口
services.py     业务逻辑
tasks.py        异步任务
validators.py   复杂校验
urls.py         路由
admin.py        管理后台
```

不要把复杂业务写在 view 里。

## 17.2 业务逻辑位置

推荐：

```text
view        接收请求、调用 serializer、调用 service
serializer  参数校验
service     业务流程
task        长任务编排
executor    外部系统交互
```

## 17.3 命名规范

类名：

```text
ApptainerBuildJob
BenchmarkJob
KnowledgeDocument
```

函数名：

```text
create_build_job
run_benchmark_job
validate_remote_workdir
```

变量名：

```text
project_id
server_id
workdir
output_name
```

## 17.4 Python 工具

建议使用：

```text
black
isort
ruff
pytest
```

## 17.5 Git 提交规范

```text
feat: 新功能
fix: 修复
docs: 文档
refactor: 重构
test: 测试
chore: 工程配置
```

示例：

```text
feat: add apptainer build job api
fix: sanitize benchmark params
docs: update deployment guide
```

---

# 18. Vue 目录结构与开发规范

## 18.1 API 封装

所有 API 请求放在 `src/api`。

示例：

```ts
// src/api/apptainer.ts

import request from "./request"

export function createBuildJob(data: any) {
  return request.post("/api/v1/apptainer/build-jobs/", data)
}
```

## 18.2 状态管理

Pinia store：

```text
userStore      用户信息、token
projectStore   当前项目
jobStore       当前任务状态
```

## 18.3 组件规范

通用组件：

```text
LogViewer
CodeEditor
FileUploader
ServerSelector
JobStatusTag
```

页面组件不直接写复杂工具逻辑，复杂逻辑封装到 composables 或 api。

## 18.4 日志展示

MVP：

```text
setInterval 每 2 秒请求 logs API
```

后续可改 SSE：

```text
EventSource('/api/v1/jobs/{id}/stream/')
```

---

# 19. 关键代码骨架

## 19.1 Django Model 示例

```python
from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

```python
class Server(models.Model):
    AUTH_PASSWORD = "password"
    AUTH_SSH_KEY = "ssh_key"

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    host = models.CharField(max_length=128)
    port = models.IntegerField(default=22)
    username = models.CharField(max_length=128)
    auth_type = models.CharField(max_length=32)
    status = models.CharField(max_length=32, default="UNKNOWN")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

```python
class ApptainerBuildJob(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("VALIDATING", "Validating"),
        ("UPLOADING", "Uploading"),
        ("RUNNING", "Running"),
        ("COLLECTING", "Collecting"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
        ("TIMEOUT", "Timeout"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    definition = models.ForeignKey("apptainer.ApptainerDefinition", on_delete=models.CASCADE)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    workdir = models.CharField(max_length=512)
    output_name = models.CharField(max_length=256)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="PENDING")
    celery_task_id = models.CharField(max_length=128, blank=True)
    log_path = models.CharField(max_length=512, blank=True)
    remote_output_path = models.CharField(max_length=512, blank=True)
    error_message = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 19.2 SSH Executor 示例

```python
import paramiko
import socket

class SSHExecutor:
    def __init__(self, host, port, username, password=None, pkey=None, timeout=30):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.pkey = pkey
        self.timeout = timeout

    def connect(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            pkey=self.pkey,
            timeout=self.timeout,
        )
        return client

    def run_command(self, command, timeout=None, log_callback=None):
        client = self.connect()
        try:
            stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
            for line in iter(stdout.readline, ""):
                if log_callback:
                    log_callback(line)
            err = stderr.read().decode("utf-8", errors="ignore")
            exit_code = stdout.channel.recv_exit_status()
            return exit_code, err
        finally:
            client.close()
```

## 19.3 参数安全校验示例

```python
import re

DANGEROUS_PATTERNS = [
    "rm -rf /",
    "mkfs",
    "dd if=",
    "| bash",
    "curl",
    "wget",
    "/etc/shadow",
    "shutdown",
    "reboot",
]

def validate_safe_command(command: str):
    lower = command.lower()
    for pattern in DANGEROUS_PATTERNS:
        if pattern in lower:
            raise ValueError(f"命令包含危险内容: {pattern}")

def validate_param_value(value: str):
    forbidden = [";", "&&", "|", "`", "$(", ">"]
    for item in forbidden:
        if item in str(value):
            raise ValueError("参数包含非法字符")
```

## 19.4 Celery 构建任务示例

```python
from celery import shared_task
from django.utils import timezone

@shared_task(bind=True)
def run_apptainer_build_task(self, job_id):
    from apps.apptainer.models import ApptainerBuildJob

    job = ApptainerBuildJob.objects.get(id=job_id)
    job.status = "VALIDATING"
    job.started_at = timezone.now()
    job.save(update_fields=["status", "started_at"])

    try:
        # 1. 校验 definition、服务器、目录
        # 2. 创建日志文件
        # 3. SSH 上传 def 文件
        # 4. 执行 apptainer build
        # 5. 检查输出文件
        # 6. 保存 artifact
        job.status = "SUCCESS"
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "finished_at"])

    except Exception as exc:
        job.status = "FAILED"
        job.error_message = str(exc)
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "error_message", "finished_at"])
        raise
```

## 19.5 Vue 请求封装示例

```ts
import axios from "axios"

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 120000,
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default request
```

---

# 20. 部署方案

## 20.1 本地开发

后端：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

Redis：

```bash
redis-server
```

Celery：

```bash
cd backend
celery -A config worker -l info
```

前端：

```bash
cd frontend
npm install
npm run dev
```

## 20.2 Docker Compose

服务：

```text
nginx
frontend
backend
celery-worker
redis
```

可选：

```text
flower
minio
```

docker-compose 示例：

```yaml
version: "3.9"

services:
  redis:
    image: redis:7
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
      - ./data:/app/data
    ports:
      - "8000:8000"
    depends_on:
      - redis
    env_file:
      - .env

  celery-worker:
    build: ./backend
    command: celery -A config worker -l info
    volumes:
      - ./backend:/app
      - ./data:/app/data
    depends_on:
      - redis
    env_file:
      - .env

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    env_file:
      - .env
```

---

# 21. 环境变量说明

```text
DJANGO_SECRET_KEY=django-secret
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=*

DATA_ROOT=./data

REDIS_URL=redis://127.0.0.1:6379/0

DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

ENCRYPTION_KEY=base64-fernet-key

MAX_UPLOAD_SIZE_MB=100
JOB_LOG_TAIL_LINES=200
```

说明：

- DEEPSEEK_API_KEY 不允许写入代码。
- ENCRYPTION_KEY 必须固定保存，丢失后无法解密已有服务器凭据。
- DATA_ROOT 应挂载到持久化目录。

---

# 22. 安全设计

## 22.1 服务器凭据安全

MVP：

```text
使用 cryptography.Fernet 加密
密钥来自 ENCRYPTION_KEY
数据库只保存密文
```

生产：

```text
Vault
KMS
企业密钥管理系统
```

## 22.2 命令执行安全

禁止：

```text
用户直接输入 shell 命令
DeepSeek 输出直接执行
前端提交 command 字段
```

允许：

```text
前端提交 action + params
后端生成命令
安全策略校验后执行
```

## 22.3 文件上传安全

限制：

1. 文件大小。
2. 文件后缀。
3. 文件名重命名。
4. 禁止路径穿越。
5. 脚本内容做危险关键字扫描。
6. 文件下载必须权限校验。

## 22.4 日志脱敏

需要脱敏：

```text
密码
SSH 私钥
DeepSeek API Key
Token
Authorization Header
```

## 22.5 权限控制

MVP 权限：

```text
admin      全部权限
developer  知识库、对话、生成 definition
operator   服务器构建、压测
viewer     查看任务和报告
```

---

# 23. 日志、监控与审计

## 23.1 Django 日志

保存：

```text
data/logs/django/app.log
```

## 23.2 Celery 日志

保存：

```text
data/logs/celery/worker.log
```

## 23.3 Job 日志

保存：

```text
data/logs/jobs/{job_type}_{job_id}.log
```

## 23.4 审计日志动作

建议记录：

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

# 24. MVP 开发计划

## 阶段一：项目初始化

目标：

- 创建 Django 项目。
- 创建 Vue 项目。
- 配置 SQLite。
- 配置 Redis 和 Celery。
- 配置基础登录。
- 配置项目空间。

交付：

```text
用户可以登录
用户可以创建项目
前端可以调用后端 API
```

## 阶段二：服务器管理

目标：

- 服务器 CRUD。
- 密码加密保存。
- allowed_dirs 配置。
- SSH 连接测试。

交付：

```text
用户可以添加服务器并测试连接
```

## 阶段三：知识库

目标：

- 上传文档。
- 保存文件。
- 解析文本。
- 切片。
- 简单关键词检索。

交付：

```text
用户可以上传知识库，系统可以检索知识片段
```

## 阶段四：DeepSeek 对话

目标：

- 封装 DeepSeek Client。
- 实现对话接口。
- 实现知识库增强。
- 保存会话和消息。

交付：

```text
用户可以与 DeepSeek 对话，回答中可以使用知识库
```

## 阶段五：Apptainer 生成

目标：

- 根据对话生成 def。
- 保存 definition。
- 校验 definition。
- 前端编辑器展示。

交付：

```text
用户可以生成并保存 Apptainer definition file
```

## 阶段六：Apptainer 构建

目标：

- 创建构建任务。
- Celery 异步执行。
- 上传 def。
- 远程执行 apptainer build。
- 采集日志。
- 更新状态。

交付：

```text
用户可以在指定服务器目录执行 Apptainer 构建
```

## 阶段七：压测任务

目标：

- 上传压测脚本。
- 创建压测任务。
- 上传脚本到远程服务器。
- 执行脚本。
- 回传报告。

交付：

```text
用户可以执行 CPU / 硬盘 / GPU 压测并下载报告
```

## 阶段八：审计与完善

目标：

- 审计日志。
- 错误码。
- 文件下载权限。
- 任务取消。
- 日志查看优化。

交付：

```text
系统具备基本运维和安全能力
```

---

# 25. 后续演进路线

## 25.1 数据库演进

```text
SQLite
  ↓
PostgreSQL
  ↓
PostgreSQL + pgvector
```

触发条件：

- 多用户并发增加。
- 知识库数量增加。
- 需要语义向量检索。
- 任务数量和日志量明显增加。

## 25.2 文件存储演进

```text
本地文件系统
  ↓
MinIO
  ↓
S3 / 企业对象存储
```

## 25.3 任务系统演进

```text
Celery
  ↓
Celery + Flower + 重试策略
  ↓
Temporal
```

## 25.4 远程执行演进

```text
Paramiko SSH
  ↓
AsyncSSH
  ↓
Slurm Executor
  ↓
Kubernetes Job Executor
```

## 25.5 知识库演进

```text
关键词检索
  ↓
SQLite FTS5
  ↓
本地 Chroma / FAISS
  ↓
PostgreSQL + pgvector
```

---

# 26. 风险点与解决方案

## 26.1 任意命令执行风险

风险：

用户或 AI 生成危险命令，导致服务器被破坏。

解决：

- 禁止提交完整 command。
- 后端 action 模板。
- Command Policy Engine。
- 参数白名单。
- 审计日志。

## 26.2 凭据泄露风险

风险：

服务器密码、SSH key、API key 泄露。

解决：

- 加密保存。
- 日志脱敏。
- 环境变量管理。
- 不在前端返回密文。
- 后续接 Vault。

## 26.3 SQLite 锁风险

风险：

多任务同时写数据库导致锁等待。

解决：

- 开启 WAL。
- 减少高频写入。
- 日志写文件。
- 任务状态低频更新。
- 必要时迁移 PostgreSQL。

## 26.4 任务长时间运行风险

风险：

构建或压测长时间不结束。

解决：

- Celery time limit。
- SSH 命令 timeout。
- 记录远程 PID。
- 支持取消任务。
- 状态标记 TIMEOUT。

## 26.5 报告无法回传

风险：

脚本没有生成报告或报告路径不对。

解决：

- report_file 参数明确。
- 执行结束后检查远程报告文件。
- 失败时记录日志。
- 支持手动重新收集报告。

---

# 27. 验收标准

## 27.1 基础功能验收

- 用户可登录。
- 用户可创建项目。
- 用户可配置服务器。
- 用户可测试 SSH 连接。
- 用户可上传知识库。
- 用户可进行对话。
- 对话可使用知识库内容。
- 用户可生成 Apptainer def 文件。
- 用户可远程构建 Apptainer。
- 用户可上传压测脚本。
- 用户可执行压测任务。
- 用户可下载报告。
- 用户可查看任务日志。

## 27.2 安全验收

- 服务器密码不明文保存。
- API key 不出现在日志中。
- 前端无法提交任意 shell 命令。
- workdir 不在 allowed_dirs 内时拒绝执行。
- 参数包含危险字符时拒绝执行。
- 所有远程执行均有审计记录。

## 27.3 稳定性验收

- 构建失败能记录错误。
- 压测失败能记录错误。
- Celery Worker 重启后不会影响已完成任务记录。
- 日志文件可查看。
- 报告可下载。

---

# 28. 附录：示例配置与模板

## 28.1 requirements.txt 示例

```text
Django>=4.2
djangorestframework
django-cors-headers
celery
redis
paramiko
httpx
python-dotenv
cryptography
```

## 28.2 .env.example

```text
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=*

DATA_ROOT=./data

REDIS_URL=redis://127.0.0.1:6379/0

DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

ENCRYPTION_KEY=
MAX_UPLOAD_SIZE_MB=100
JOB_LOG_TAIL_LINES=200
```

## 28.3 Apptainer definition 示例

```text
Bootstrap: docker
From: ubuntu:22.04

%post
    apt-get update
    apt-get install -y python3 python3-pip
    pip3 install numpy pandas

%environment
    export LC_ALL=C

%runscript
    exec python3 "$@"
```

## 28.4 压测脚本调用示例

```bash
./gpu_benchmark.sh --duration 300 --report-file report.html
```

## 28.5 任务状态流转

```text
PENDING
  ↓
VALIDATING
  ↓
UPLOADING
  ↓
RUNNING
  ↓
COLLECTING
  ↓
SUCCESS
```

失败流转：

```text
PENDING / VALIDATING / UPLOADING / RUNNING / COLLECTING
  ↓
FAILED
```

超时流转：

```text
RUNNING
  ↓
TIMEOUT
```

取消流转：

```text
PENDING / RUNNING
  ↓
CANCELLED
```

---

# 29. 最终总结

本项目采用：

```text
Vue 3 前端控制台
+
Django REST Framework 后端 API
+
SQLite 轻量数据库
+
Celery + Redis 异步任务
+
Paramiko SSH/SFTP 远程执行
+
DeepSeek API 智能生成
+
本地文件系统保存脚本、日志、报告
+
知识库检索增强
```

核心职责划分：

```text
Vue：负责页面交互
Django：负责业务接口、权限、安全和数据
DeepSeek：负责自然语言生成和分析
知识库：负责上下文增强
Celery：负责长耗时任务
Paramiko：负责远程服务器执行
SQLite：负责轻量元数据
文件系统：负责大文件、日志、报告
Audit：负责审计追踪
```

一句话定义：

```text
这是一个基于 Vue + Django + SQLite + Celery + DeepSeek 的轻量级 AI-Ops 平台，
用于通过知识库增强对话生成 Apptainer 容器定义文件，
并在指定服务器目录完成远程构建、服务器压测和报告回传。
```
