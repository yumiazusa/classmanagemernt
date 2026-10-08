# PROJECT_CONTEXT.md

本文档是当前“LETS课程管理系统 V1.0”的长期主上下文。新协作者接手时，应先阅读本文件，再阅读 `README.md`、`backend/README.md` 和 `AGENTS.md`。

## 项目定位

本项目定位为通用教学管理底座。当前不预装标准课程或学科课程模块，不兼容旧数据库。

V1.0 发布资料见 `docs/TECHNICAL_V1.0.md`、`docs/DEPLOYMENT_V1.0.md`、`docs/VERSION_CONTROL.md`；二次开发和上游升级见 `docs/DOWNSTREAM_UPDATE_GUIDE.md`。

目标是提供一个可扩展的教学基础平台：

- 学生进入自己班级已开放的课程模块。
- 教师管理学生并进入负责的课程模块。
- 管理员维护用户、班级、课程名称、模块连接与授课范围。

## 用户角色

- 学生：登录、查看“我的课程”、进入课程模块。
- 教师：课程看板、学生管理、学生导入、进入课程模块。
- 管理员：用户管理、教师管理、管理员管理、课程管理、班级管理、平台资料管理。

## 技术栈

- 后端：FastAPI、SQLAlchemy、MySQL、Python 3.11+
- 前端：Vue 3、Vite、Vue Router、Axios、Markdown 渲染
- 数据库：MySQL 8.0+

## 本地开发与验证环境

- Node 开发环境在 Docker 宝塔容器 `e0c` 中，容器内项目路径为 `/www/wwwroot/classmanagement/`。
- 可通过 `docker exec e0c /bin/bash -lc 'cd /www/wwwroot/classmanagement/frontend && npm run build'` 验证前端构建；交互排查时可用 `docker exec -it e0c /bin/bash`。

## 前端页面

- `/login`：登录
- `/courses`：学生端“我的课程”
- `/courses/:id/experience`：课程模块入口
- `/dashboard`：学生个人主页
- `/teacher/courses`：教师课程看板，仅列出分配给当前教师的课程；卡片入口包含课程模块、学生管理、文档阅读和批阅开发中页面
- `/teacher/students`、`/teacher/student-import`：教师全局学生管理与导入，仅覆盖负责课程关联的班级
- `/teacher/courses/:id/students`、`/teacher/courses/:id/students/import`：单门课程的学生管理与导入
- `/teacher/courses/:id/submissions`：批阅功能开发中静态页面，不加载提交数据
- `/admin`：管理员概览
- `/admin/users`、`/admin/teachers`、`/admin/admin-users`：账号管理
- `/admin/courses`：课程管理
- `/admin/courses/:id`：课程名称、模块连接、启停、授课教师和班级配置
- `/admin/courses/:id/docs`：当前课程的文档编辑管理
- `/admin/classes`：班级管理
- `/admin/docs`：平台文档管理（平台指南、管理员手册）
- `/docs`：平台文档浏览
- `/courses/:id/docs`：课程成员浏览本课程文档

## 后端接口

- `/api/courses`
- `/api/courses/{course_id}`
- `/api/courses/{course_id}/modules`
- `/api/courses/{course_id}/tasks`
- `/api/tasks/{task_id}`
- `/api/tasks/{task_id}/submissions`
- `/api/admin/courses`
- `/api/admin/courses/{course_id}/docs`（课程文档管理）
- `/api/courses/{course_id}/docs`（课程已发布文档）
- `/api/admin/classes`
- `/api/teacher/courses`
- `/api/teacher/courses/{course_id}`
- `/api/teacher/classes`

账号、登录、改密、学生导入、启用停用、重置密码等接口沿用原权限体系。

## 数据模型

- `Course`：课程主记录；管理员维护名称和启停，内部标识由后端生成。
- `CourseExperience`：课程与注册模块的连接，未连接标识为 `unlinked`。
- `ClassGroup`：班级或教学班。
- `ClassMember`：班级成员，绑定用户。
- `CourseTeacher`：课程教师绑定。
- `CourseClass`：课程和班级绑定。
- `CourseModule / CourseTask / CourseResource / TaskSubmission`：保留的可选共享能力，不在基础课程管理中配置；将来由具体课程模块决定是否使用。
- `CourseDoc`：绑定单门课程的文档；由课程编辑页管理，发布后对本课程成员开放。
- `Doc`：平台文档；分类为“平台指南”和“管理员手册”，由文档管理页维护。

## 前端配置

`frontend/src/config/platform.js` 集中维护：

- `platformName`
- `defaultHomeByRole`
- `roleLabels`
- `taskTypeLabels`
- `courseStatusLabels`

新增角色标签、任务类型标签或课程状态标签时，优先改这里。

## 设计约束

延续 AGENTS.md 中的浅色、淡蓝、极简教学风。学生优先，界面要清晰、克制、反馈明确，不做花哨堆砌。

## 后续开发原则

- 课程通过 `course_experiences.experience_key` 连接注册模块。没有连接或模块未安装的课程视为 `unlinked`，不能启用，也不向学生/教师显示。当前没有预装课程模块。

- 学科课程按需通过注册模块接入，通用框架不预装课程模块。
- 不兼容旧数据库，变更直接面向 `teaching_framework` 新库。
- 每门课程的教学内容和交互由独立模块提供，基础课程管理只管连接、启停和授课范围。

## 当前进度

- 2026-10-08：整理 LETS课程管理系统 V1.0 品牌、技术文档、部署文档和版本管理方案；本地演示库保留原 `admin`，重建为两名教师、八名学生、两个班级、两门未连接示例课程与课程文档。
- 2026-10-08：补充二次开发与上游版本更新规范，明确从固定标签建下游仓库、升级分支合并及数据库迁移检查。
