# Course Module Extension Guide

## 新增一门课程的最短路径

1. 管理员创建教师账号和学生账号。
2. 创建或同步班级 `ClassGroup`。
3. 在 `/admin/courses` 创建 `Course`，状态设为 `published`。
4. 绑定课程教师 `CourseTeacher` 和班级 `CourseClass`。
5. 创建 `CourseModule` 组织章节、周次或主题。
6. 创建 `CourseTask`，选择任务类型并填写说明。
7. 如有资料，创建 `CourseResource`。

## 新增任务类型

当前 `CourseTask.task_type` 支持：

- `reading`
- `assignment`
- `quiz`
- `file_upload`
- `text_response`
- `external_link`
- `custom`

扩展步骤：

1. 后端在 `backend/app/schemas/course.py` 的 `TaskType` 中加入新枚举值。
2. 前端在 `frontend/src/config/platform.js` 的 `taskTypeLabels` 中加入中文标签。
3. 如只是展示和基础提交，复用 `TaskDetailView.vue` 即可。
4. 如需要特殊交互，在 `TaskDetailView.vue` 中按 `task.task_type` 增加分支组件。
5. 复杂配置写入 `CourseTask.config`，避免为每种任务过早新增字段。
6. 教师批阅如需额外评分维度，可先写入 `TaskSubmission.review_comment` 或扩展 `TaskSubmission` 字段。

## 新增课程类型

课程类型建议先不要新增硬字段，优先使用：

- `Course.status`
- `Course.cover_color`
- `Course.description`
- `CourseModule`
- `CourseResource`
- `CourseTask.config`

只有当多个课程都需要稳定结构化能力时，再新增字段或新表。

## 数据库注意事项

本项目当前不兼容旧库。扩展表结构时面向新库直接演进，必要时提供清晰的初始化脚本或迁移说明。
