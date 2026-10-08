# 课程模块接入指南

## 基础框架负责什么

`Course` 保存课程名称和启停状态；`CourseTeacher` 与 `CourseClass` 分配授课教师和班级；`course_experiences.experience_key` 连接课程模块。课程内部的章节、任务、内容和交互由接入的模块决定，基础课程管理页不配置这些内容。

当前没有预装课程模块。新建课程可以暂不连接模块，此时课程保持停用，不会出现在学生或教师的课程列表。已有未绑定或旧模块键的记录在管理页显示为“未连接模块”，不会自动转成标准课程。

## 接入一门课程

1. 在 `backend/app/services/course_experiences.py` 的 `EXPERIENCES` 注册稳定的模块键、名称和说明。
2. 在 `frontend/src/course-experiences/registry.js` 注册相同的键，并懒加载该模块的 Vue 页面，例如 `frontend/src/course-experiences/<key>/CourseView.vue`。
3. 模块页面通过 `course` 属性接收当前课程数据；如需独立数据，为模块创建自己的表和 API，以 `course_id` 关联 `courses`。
4. 每个模块 API 都要校验当前用户对 `course_id` 的访问权限，可复用 `crud_course.can_access_course`。不要把数据库里的模块键当成 URL 或动态导入路径。
5. 在 `/admin/courses` 新建课程，在 `/admin/courses/:id` 连接模块、分配教师和班级并启用。学生与教师通过 `/courses/:id/experience` 进入对应模块。

一个模块可以服务多门课程；若两门课程的业务完全不同，也可以分别注册两个模块键。模块的内部管理页面和交互由模块自行实现，基础课程管理不限定课程形态。

## 可选共享能力

项目仍保留 `CourseModule / CourseTask / CourseResource / TaskSubmission` 等数据结构和部分接口，供未来模块按需复用。它们不是所有课程必须遵循的标准课程流程，也不会在基础课程管理页自动出现。

## 数据库

`course_experiences` 表由应用启动时的 `Base.metadata.create_all()` 创建。新环境初始化不创建任何课程；`--seed-demo` 仅建立演示账号和班级。现有课程数据不会被自动删除。
