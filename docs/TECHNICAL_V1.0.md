# LETS课程管理系统 V1.0 技术文档

## 定位与范围

LETS V1.0 是学生、教师、管理员共用的课程管理底座。管理员维护账号、班级、课程、授课教师和班级分配；教师查看负责课程并管理相应学生；学生查看已开放课程及文档。具体课程的教学内容与交互由注册模块提供。当前前后端注册表均为空，因此初始系统没有可启用的课程模块；教师批阅页是“开发中”占位页。

本版本使用全新的 `teaching_framework` 数据库，不提供旧库迁移或旧数据兼容。

## 架构与依赖

```text
浏览器 → Vue 3 / Vite 静态页面 → 同源 /api → FastAPI → SQLAlchemy → MySQL
                              /health → FastAPI
```

| 层 | 技术 | 位置 |
| --- | --- | --- |
| 前端 | Vue 3、Vue Router、Axios、Vite、Markdown 渲染 | `frontend/src` |
| 后端 | Python 3.11+、FastAPI、Pydantic Settings、SQLAlchemy 2、PyMySQL | `backend/app` |
| 数据 | MySQL 8.0+，`utf8mb4` | `backend/app/models` |
| 认证 | 用户名密码登录、JWT、角色权限 | `backend/app/api/v1/endpoints/auth.py`、`backend/app/core` |

Node.js 18+ 和 npm 9+ 用于构建前端。生产包位于 `frontend/dist`。生产环境建议由 Nginx 提供静态文件并将同源 `/api` 转发给 FastAPI；开发环境由 Vite 代理，默认端口分别为 8082 和 8083。

## 主要业务流程

1. 管理员创建用户、班级与课程，并把教师、班级关联到课程。
2. 在前后端课程模块注册表中登记相同的稳定模块键，再在管理页连接课程模块并启用课程。
3. 教师在课程看板进入负责课程，管理对应班级学生；学生从“我的课程”进入已开放课程。
4. 平台文档由管理员维护；课程文档在课程管理页编辑，发布后供该课程成员阅读。

课程模块接入步骤见 [课程模块接入指南](COURSE_MODULE_EXTENSION_GUIDE.md)。基础课程管理只管理课程连接与授课范围。保留的 `CourseModule`、`CourseTask`、`CourseResource`、`TaskSubmission` 是可选共享模型，不代表 V1.0 已提供完整实验、提交和批阅流程。

## 代码结构

| 路径 | 职责 |
| --- | --- |
| `backend/app/api/v1/endpoints` | 认证、课程、教师、管理员、文档等 HTTP 接口 |
| `backend/app/crud` | 数据读写与课程可见性判断 |
| `backend/app/models` | SQLAlchemy 数据表定义 |
| `backend/app/schemas` | 请求与响应数据结构 |
| `backend/app/services/course_experiences.py` | 后端课程模块键注册与校验 |
| `frontend/src/router/index.js` | 页面路由和登录、角色导航限制 |
| `frontend/src/course-experiences/registry.js` | 前端课程模块页面注册 |
| `frontend/src/config/platform.js` | 平台名称、角色和状态显示文案 |

主要页面入口：`/login`、学生 `/dashboard` 与 `/courses`、教师 `/teacher/courses` 与 `/teacher/students`、管理员 `/admin`、`/admin/courses`、`/admin/classes` 和 `/admin/docs`。后端接口统一在 `/api` 下；`GET /health` 返回 `{"status":"ok"}`。FastAPI 的交互式接口文档也使用后端 `/docs`，但前端同样使用 `/docs` 路径；生产同域部署如需查看 Swagger，应配置独立后端管理入口。

## 数据模型与初始化

核心关系：`User` ↔ `ClassMember` ↔ `ClassGroup`；`Course` ↔ `CourseTeacher` / `CourseClass` / `CourseExperience` / `CourseDoc`。`Doc` 保存平台文档。模型定义以 `backend/app/models` 为准。

`python -m app.db.init_db` 会创建数据库、缺失的表及默认平台文档；后端每次启动也会执行这些步骤。`--seed-demo` 幂等创建以下演示数据：

| 类型 | 样本 | 初始密码 |
| --- | --- | --- |
| 管理员 | `admin`，仅在不存在时创建 | 新建时 `admin123` |
| 教师 | `teacher_wang` 王宁、`teacher_chen` 陈思 | `Teacher@2026` |
| 学生 | `202601001` 至 `202601004`、`202602001` 至 `202602004`，共 8 人 | `Student@2026` |
| 班级 | 2026级数字经济1班、2026级工商管理2班 | — |
| 课程 | 数字经济案例与分析（示例）、平台经济学（示例） | — |
| 文档 | 2 份平台默认文档、每门课程 1 份课程学习指南 | — |

每门课程都关联一名主讲教师和一个班级。示例课程保持草稿、停用、`unlinked`，接入课程模块后方可启用。新建演示账号首次登录需改密。`--reset-demo` 仅供本地/测试库使用：清除非 `admin` 用户及原课程、班级、文档等数据，保留现有 `admin` 的密码等属性并重建演示集；执行前先备份。生产库用 `--bootstrap-admin` 交互创建初始管理员，不使用固定演示密码。`create_all()` 只创建缺失表，不迁移已有表结构；后续版本修改字段时必须准备单独的迁移脚本，先备份并在测试库验证。

## 配置与安全边界

后端配置来自 `backend/.env`，示例为 `backend/.env.example`，由 `backend/app/core/config.py` 读取。关键项：`MYSQL_*`、`JWT_SECRET_KEY`、`ACCESS_TOKEN_EXPIRE_MINUTES`、`APP_ENV`、`APP_DEBUG` 和 `CORS_*`。生产环境将 `APP_ENV=production`、`APP_DEBUG=false`，使用随机且独立的 JWT 密钥，通过 HTTPS 提供服务。`.env` 不提交到 Git。

前端默认请求同源 `/api`；仅在需要独立 API 域名时设置构建时变量 `VITE_API_BASE_URL`。`VITE_PROXY_TARGET` 只控制 Vite 开发代理，不影响生产包。部署命令和 Nginx 示例见 [部署文档](DEPLOYMENT_V1.0.md)。

## V1.0 验收边界

- 前端构建成功，后端模块可导入，`/health` 返回正常。
- 新库初始化后可登录，管理员可配置账号、班级和课程；教师与学生仅看到有权限且已启用的课程。
- 课程模块未注册时保持“未连接”，不能启用，也不会出现在学生、教师课程列表。
- 课程文档发布后按成员权限可见；未发布文档不对普通成员开放。

这份文档描述当前代码及预期部署验收项；数据库联调和完整角色操作需在目标环境执行。
