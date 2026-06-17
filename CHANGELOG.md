# 变更记录

本文件用于记录 AI-Ops 平台的重要代码、配置、文档和架构变更。

## 2026-06-16

- 新增独立脚本管理模块：支持 `.sh`、`.bash`、`.py` 脚本上传、列表、删除、内容查看与在线编辑保存。
- 新增脚本执行任务：后端通过 Celery 运行已上传脚本，使用 `SCRIPT_ALLOWED_CWDS` 限制执行目录，使用 `SCRIPT_DEFAULT_TIMEOUT` 控制默认超时，并支持终止运行中任务。
- 新增脚本执行 SSE 日志流，前端脚本管理页可实时展示 stdout、stderr、退出码并支持复制、清空和自动滚动。
- 更新 `.env.example` 与 `backend/.env.example`，补充脚本执行目录白名单和默认超时配置。

## 2026-06-15

- 新增本地开发专用 `deploy/docker-compose.local.yml`，仅启动 MySQL 8.4 和 Redis 7 容器，支持后端、Celery、前端代码继续在本机启动调试。
- 更新 `backend/.env.example` 与 `deploy/README.md`，补充本地中间件容器启动、停止、清空数据和本地代码连接配置。
- 补充 `mysqlclient` 本地安装故障说明；在 conda `aiops` 环境中安装 `mysqlclient` 并完成本地 MySQL 数据库迁移验证。
- 修复构建和压测 Celery 任务二次解密服务器凭据的问题。
- 按项目负责人要求，将服务器凭据存储从加密字段调整为数据库明文字段，移除运行配置中的 `ENCRYPTION_KEY`，并同步更新 `AGENTS.md` 安全约束说明。
- 新增普通用户注册接口 `/api/v1/auth/register/`，并在前端登录页增加“登录 / 注册”切换入口。
- 修复服务器允许工作目录管理：前端详情页接入目录查询、添加和删除 API，后端补充目录路径校验与删除审计，并为当前云服务器配置 `/opt` 构建目录。
- 修复远程工作目录已存在时 SFTP 创建失败的问题，目录存在且为目录时视为可用，并支持递归创建子目录。
- 调整 Apptainer Definition 内容校验：允许 definition 中出现 `rm -rf /` 片段，用于容器构建过程中的清理场景；远程命令执行策略仍保留该高危命令拦截。
- 修复 SSH 远程命令日志采集阻塞问题，改为执行期间持续读取 stdout/stderr，避免长时间构建任务只显示启动命令。

## 2026-06-12

- 初始化本地 Git 仓库。
- 新增 `.gitignore`，避免提交本地数据、密钥、依赖目录、构建产物和日志文件。
- 建立变更记录文件，后续修改需要在本文件补充说明。
- 配置 GitHub 远程仓库 `https://github.com/Chen-DR/ai-work-CICD.git`。
- 合并远程仓库已有的 `LICENSE` 初始提交。
- 修复本机 Claude Code 配置：将默认模型切换为 `claude-qwen3.6-35b`，修正 `.bashrc` 中网关模型发现变量的错误写法，并新增 Windows 用户级 `.wslconfig` 以支持 WSL mirrored networking。
- 脱敏本机 Claude 历史和 shell 配置中残留的明文 token 形态。
