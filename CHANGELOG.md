# 变更记录

本文件用于记录 AI-Ops 平台的重要代码、配置、文档和架构变更。

## 2026-06-12

- 初始化本地 Git 仓库。
- 新增 `.gitignore`，避免提交本地数据、密钥、依赖目录、构建产物和日志文件。
- 建立变更记录文件，后续修改需要在本文件补充说明。
- 配置 GitHub 远程仓库 `https://github.com/Chen-DR/ai-work-CICD.git`。
- 合并远程仓库已有的 `LICENSE` 初始提交。
- 修复本机 Claude Code 配置：将默认模型切换为 `claude-qwen3.6-35b`，修正 `.bashrc` 中网关模型发现变量的错误写法，并新增 Windows 用户级 `.wslconfig` 以支持 WSL mirrored networking。
