# LETS 二次开发与上游版本更新规范

适用范围：以 LETS 通用课程管理系统为基础，创建独立的课程项目，并希望以后接收 LETS 的正式版本。下文称 LETS 原仓库为“上游”，课程项目仓库为“下游”。上游仓库地址保持为 `git@github.com:yumiazusa/classmanagemernt.git`。

## 必须遵守的原则

1. **从固定版本标签开始，并保留上游 Git 历史。** `main`、`development`、`v1.0` 是可移动分支；正式标签固定一个发布提交。由于上游同时有 `v1.0` 分支和标签，引用标签时写 `refs/tags/v1.0`。本规范随 `v1.0.1` 文档修订版提供，新项目优先从 `refs/tags/v1.0.1` 起步；它与 V1.0 使用同一套功能代码。
2. **一个下游项目用自己的远程仓库和数据库。** 上游 remote 命名为 `upstream`，下游 remote 命名为 `origin`。下游代码和数据不能推回 LETS 上游。
3. **课程定制尽量集中在独立模块。** 课程页面放入 `frontend/src/course-experiences/<key>/`，在前端 `registry.js` 与后端 `course_experiences.py` 登记同一键；独立 API、数据表以 `course_id` 关联。通用代码必须修改时，保持提交小而明确，记录原因和受影响文件。具体接口边界见 [课程模块接入指南](COURSE_MODULE_EXTENSION_GUIDE.md)。
4. **升级必须走独立分支。** 先合并上游正式标签，再解决冲突、迁移数据库、验证三类角色的关键路径；验收后才合入下游 `development` 和 `main`。不直接覆盖文件、不强推、不移动已发布标签。
5. **代码版本与数据库版本一起管理。** `.env`、运行库数据、备份文件不进 Git。`Base.metadata.create_all()` 不能修改已有表结构；上游版本涉及模型变更时，需要明确迁移和回滚脚本，并在测试库先验证。

## 方式 A：下游是独立仓库，应用代码位于仓库根目录（推荐）

先在 GitHub 创建**空的**下游仓库。执行下列命令，把占位符换成实际仓库地址；不要在已有未提交改动的目录执行。

```bash
git clone git@github.com:yumiazusa/classmanagemernt.git lets-course-project
cd lets-course-project
git fetch origin --tags
git switch -C main refs/tags/v1.0.1
git remote rename origin upstream
git remote add origin git@github.com:你的用户名/你的课程项目.git
git push -u origin main
git switch -c development
git push -u origin development
```

在下游新增 `UPSTREAM_VERSION.md`，记录起始标签、每次升级目标标签、迁移脚本、冲突决策和验收结果。新功能从下游 `development` 拉取后建 `feature/<任务>` 分支，审查合入 `development`；下游 `main` 只保存已部署版本。不要直接在 `upstream/v1.0` 或上游标签上开发。

初始记录示例：

```markdown
# LETS 上游版本记录

- 引入版本：v1.0.1
- 引入日期：YYYY-MM-DD
- 引入方式：保留完整历史 / git subtree
- 本项目定制位置：列出模块目录、配置和接口
- 最近一次升级：尚无
- 数据库迁移与回滚：尚无
```

当上游发布新的正式标签（以下以 `v1.1.0` 为例）：

```bash
git status --short --branch
git switch development
git pull --ff-only origin development
git fetch upstream --tags
git switch -c upgrade/lets-v1.1.0
git merge --no-ff refs/tags/v1.1.0
```

若提示冲突，逐文件保留需要的上游修复和下游定制，完成后执行 `git add <已解决文件>`、`git commit`。合并前可用 `git log --oneline refs/tags/v1.0.1..refs/tags/v1.1.0` 和两个标签之间的差异检查上游变更；升级分支中不要用 `git reset --hard` 或直接复制新版文件掩盖冲突。

随后更新 `UPSTREAM_VERSION.md`，按该版本说明备份并迁移测试库，执行前端构建、后端启动与接口检查，实际验证管理员、教师、学生的登录、课程可见性、文档和课程模块。通过后：

```bash
git push -u origin upgrade/lets-v1.1.0
# 审查并合入下游 development；验证部署后再合入下游 main
```

下游发布自己的标签，例如 `course-project-v1.2.0`，避免把下游标签命名为 `v1.1.0` 与上游标签混淆。下游版本号和上游版本号分别记录。

## 方式 B：LETS 放在另一仓库的子目录

如果 LETS 只是较大项目的 `classmanagement/` 子目录，从首次引入就使用 `git subtree`，不要使用一次性的 `git read-tree` 或文件复制：

```bash
cd /你的/现有项目
git status --short --branch
git remote add lets git@github.com:yumiazusa/classmanagemernt.git
git fetch lets --tags
git subtree add --prefix=classmanagement lets refs/tags/v1.0.1 --squash
```

以后在干净的升级分支中执行：

```bash
git fetch lets --tags
git switch -c upgrade/lets-v1.1.0
git subtree pull --prefix=classmanagement lets refs/tags/v1.1.0 --squash
```

处理冲突和数据库迁移、验证的方法与方式 A 相同。子目录方式下，不要把上游仓库的 `main` 直接合并到下游仓库根目录。如果此前已经用 `git read-tree` 或复制文件导入，先整理现有定制并建立清晰的上游基线，再切换为 subtree；直接运行 `git subtree pull` 通常无法识别此前的一次性导入。

## 升级前检查清单

- 已确认目标是上游**正式标签**，并阅读其变更记录、部署要求和数据库迁移说明。
- 下游当前工作区干净，现有版本已提交、推送且可回滚。
- 测试库和生产库分别备份；迁移在测试库验证后才进入生产。
- 课程模块注册键、权限检查、配置项、前端路由与上游改动逐一核对。
- 升级分支构建和角色关键流程通过，`UPSTREAM_VERSION.md` 已写明合并结果。

如果上游缺少某版本的迁移或回滚说明，应先补齐并验证，再部署涉及数据库结构变化的更新。
