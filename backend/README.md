# Backend (FastAPI)

通用教学管理框架后端。当前版本不兼容旧数据库，请新建 `teaching_framework` 数据库后初始化。

## 环境要求

- Python 3.11+
- MySQL 8.0+

## 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 配置

```bash
cp .env.example .env
```

关键变量：

- `MYSQL_HOST`、`MYSQL_PORT`、`MYSQL_USER`、`MYSQL_PASSWORD`
- `MYSQL_DB`：建议 `teaching_framework`
- `JWT_SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

## 初始化数据库

```sql
CREATE DATABASE IF NOT EXISTS teaching_framework DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

```bash
python -m app.db.init_db
```

可选演示数据：

```bash
python -m app.db.init_db --seed-demo
```

## 启动

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8081
```

或：

```bash
./start_backend.sh
```

## 主要接口

- `GET /health`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/change-password`
- `POST /api/auth/update-profile`
- `GET /api/student/dashboard`
- `GET /api/courses`
- `GET /api/courses/{course_id}`
- `GET /api/courses/{course_id}/modules`
- `GET /api/courses/{course_id}/tasks`
- `GET /api/tasks/{task_id}`
- `POST /api/tasks/{task_id}/submissions`
- `GET /api/admin/courses`
- `POST /api/admin/courses`
- `PUT /api/admin/courses/{course_id}`
- `DELETE /api/admin/courses/{course_id}`
- `POST /api/admin/courses/{course_id}/modules`
- `POST /api/admin/courses/{course_id}/tasks`
- `GET /api/admin/classes`
- `POST /api/admin/classes`
- `PUT /api/admin/classes/{class_id}`
- `GET /api/teacher/courses`
- `GET /api/teacher/classes`
- `GET /api/teacher/tasks/{task_id}/submissions`
- `POST /api/teacher/submissions/{submission_id}/review`
- `GET /api/teacher/students`
- `POST /api/teacher/students/import`
- `GET /api/admin/users`
- `POST /api/admin/users/{user_id}/enable`
- `POST /api/admin/users/{user_id}/disable`
- `POST /api/admin/users/{user_id}/reset-password`

## 新表概览

- `courses`
- `class_groups`
- `class_members`
- `course_teachers`
- `course_classes`
- `course_modules`
- `course_tasks`
- `course_resources`
- `task_submissions`
- `users`
- `docs`
