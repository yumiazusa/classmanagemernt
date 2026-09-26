# PROJECT_CONTEXT.md

本文档是当前“通用教学管理框架”的长期主上下文。新协作者接手时，应先阅读本文件，再阅读 `README.md`、`backend/README.md` 和 `AGENTS.md`。

## 项目定位

本项目已经从 Python 在线实验系统改造为通用教学管理框架。它不再绑定 Python 课程、不保留代码运行器主路径，也不兼容旧数据库。

目标是提供一个可扩展的教学基础平台：

- 学生快速进入课程、理解模块任务、提交学习成果。
- 教师管理学生、查看课程看板、批阅任务提交。
- 管理员维护用户、课程、班级和平台资料。

## 用户角色

- 学生：登录、查看“我的课程”、进入课程详情、完成任务、提交文本/链接/附件。
- 教师：课程看板、学生管理、学生导入、任务提交批阅。
- 管理员：用户管理、教师管理、管理员管理、课程管理、班级管理、平台资料管理。

## 技术栈

- 后端：FastAPI、SQLAlchemy、MySQL、Python 3.11+
- 前端：Vue 3、Vite、Vue Router、Axios、Markdown 渲染
- 数据库：MySQL 8.0+

## 前端页面

- `/login`：登录
- `/courses`：学生端“我的课程”
- `/courses/:id`：课程详情，展示模块和任务
- `/tasks/:id`：任务详情和提交入口
- `/dashboard`：学生个人主页
- `/teacher/courses`：教师课程看板
- `/teacher/students`：教师学生管理
- `/teacher/student-import`：学生导入
- `/teacher/submissions`：任务提交批阅
- `/admin`：管理员概览
- `/admin/users`、`/admin/teachers`、`/admin/admin-users`：账号管理
- `/admin/courses`：课程管理
- `/admin/classes`：班级管理
- `/admin/docs`：平台资料管理
- `/docs`：平台资料

## 后端接口

- `/api/courses`
- `/api/courses/{course_id}`
- `/api/courses/{course_id}/modules`
- `/api/courses/{course_id}/tasks`
- `/api/tasks/{task_id}`
- `/api/tasks/{task_id}/submissions`
- `/api/admin/courses`
- `/api/admin/classes`
- `/api/teacher/courses`
- `/api/teacher/classes`
- `/api/teacher/tasks/{task_id}/submissions`
- `/api/teacher/submissions/{submission_id}/review`

账号、登录、改密、学生导入、启用停用、重置密码等接口沿用原权限体系。

## 数据模型

- `Course`：课程。包含标题、slug、简介、状态、排序、启用状态。
- `ClassGroup`：班级或教学班。
- `ClassMember`：班级成员，绑定用户。
- `CourseTeacher`：课程教师绑定。
- `CourseClass`：课程和班级绑定。
- `CourseModule`：课程模块，可表示章节、周次或主题单元。
- `CourseTask`：课程任务，支持 `reading / assignment / quiz / file_upload / text_response / external_link / custom`。
- `CourseResource`：课程资料。
- `TaskSubmission`：任务提交和批阅结果。

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

- 不恢复旧 Python 课程主路径。
- 不兼容旧数据库，变更直接面向 `teaching_framework` 新库。
- 新课程类型优先通过 `CourseModule / CourseTask / CourseResource / config` 扩展。
- 复杂任务交互应先新增 task type，再扩展任务详情页和提交/批阅结构。
