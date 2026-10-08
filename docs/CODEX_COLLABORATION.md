# Codex 多设备协作

当前仓库的分支职责、拉取、推送和发布步骤统一见 [版本与分支管理](VERSION_CONTROL.md)。远程仓库为 `git@github.com:yumiazusa/classmanagemernt.git`。新设备先 `git fetch origin --prune --tags`，再从 `development` 开始新任务。

每台设备在切换或拉取前先运行 `git status --short --branch`。未提交改动应先在自己的功能分支提交；避免在两台设备同时修改同一分支的同一部分。共享项目上下文以 `AGENTS.md`、`PROJECT_CONTEXT.md` 和仓库文档为准，聊天记录不能替代 Git 提交。
