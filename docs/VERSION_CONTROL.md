# LETS 版本与分支管理

## 分支职责

| 名称 | 用途 | 同步方式 |
| --- | --- | --- |
| `main` | 已验证、可部署的最新正式版本 | 仅合入发布版本；服务器拉此分支或固定标签 |
| `development` | 下一版本的集成分支 | 日常协作从这里拉取，功能完成后合入 |
| `codex/<任务>` 或 `feature/<任务>` | 一个明确功能或修复 | 从 `development` 建立，检查后合入 |
| `v1.0` | V1.0 版本维护线 | 可加入 1.0.x 修补；首发标签 `v1.0` 固定 |

`dev` 是本机历史分支，远程已不存在对应分支。本方案统一使用 `development`，保留本地 `dev` 供历史查阅。分支可移动，已发布标签和 `main` 历史不重写。

`v1.0.1` 是 V1.0 的文档修订版，补充二次开发项目的上游更新规范，功能代码与 `v1.0` 相同。新二次开发项目应从 `refs/tags/v1.0.1` 起步，并遵守 [二次开发与上游版本更新规范](DOWNSTREAM_UPDATE_GUIDE.md)。原 `v1.0` 标签保持不变。

## 日常开发与多设备拉取

首次在另一设备同步：

```bash
git clone git@github.com:yumiazusa/classmanagemernt.git
cd classmanagemernt
git fetch origin --prune --tags
git switch development
```

每次开始任务：

```bash
git switch development
git pull --ff-only origin development
git switch -c codex/<任务名>
```

完成后提交并推送功能分支，经 PR 或审查合入 `development`。若只有自己开发，也先检查差异与构建结果。另一设备拉取前运行 `git status --short --branch`；有未提交改动时先在功能分支提交，避免覆盖现场。

## 发布新版本

1. 在 `development` 确认范围，更新版本号、文档和变更记录，完成构建与数据库联调。
2. 从该提交创建 `release/v1.1.0`，仅做发版修复；验证通过后合入 `main`。
3. 在 `main` 对实际部署提交打带注释标签 `v1.1.0`，推送 `main` 和标签；将发版修复同步回 `development`。
4. 服务器固定检出 `v1.1.0`；若选择滚动正式版，执行 `git pull --ff-only origin main`。

版本号按 `主版本.次版本.修订版本`：不兼容变更升主版本，新兼容功能升次版本，兼容修复升修订版本。Git 标签使用 `v1.1.0`，界面可显示 `V1.1`。已发布数据库结构变更必须附迁移和回滚说明。

## V1.0 修补

从 `v1.0` 分支修复并验证，提交后打 `v1.0.1` 标签；将修复合入 `main`，再同步到 `development`。若 `main` 已发布更高版本，将修复挑选到对应版本线，不用旧版本分支覆盖 `main`。生产部署以标签为准。

## 建议的远程设置

GitHub 默认分支设为 `main`；禁止强推与删除。多人协作时要求 PR 和必要检查通过；`development` 也建议禁止强推。分支保护由仓库管理员按团队权限配置。
