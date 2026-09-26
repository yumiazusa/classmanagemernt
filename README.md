# 通用教学管理框架

面向课堂教学、课程任务、班级管理和提交批阅的三端教学管理框架。项目已从原 Python 在线实验系统改造为通用课程平台，不兼容旧数据库，也不再提供 Python 代码运行作为主路径。

## 核心能力

- 登录、改密、个人中心
- 学生、教师、管理员三类角色与权限
- 管理员用户管理、教师管理、管理员账号管理
- 教师学生管理、学生导入、启停账号、批量重置密码
- 学生端“我的课程”、课程详情、任务详情与提交入口
- 教师端课程看板、班级/学生管理、任务提交批阅
- 管理员课程管理、班级管理、平台资料管理
- 通用课程模型：课程、班级、成员、模块、任务、资源、提交

## 数据库

本版本不兼容旧库。请新建数据库，推荐默认库名：

```sql
CREATE DATABASE IF NOT EXISTS teaching_framework DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

后端默认 `MYSQL_DB=teaching_framework`。

## 快速启动

### 后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.db.init_db
uvicorn app.main:app --reload --port 8081
```

如需少量演示账号、课程、班级和任务：

```bash
python -m app.db.init_db --seed-demo
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 主要文档

- [backend/README.md](backend/README.md)：后端启动、接口与数据库说明
- [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)：长期项目上下文
- [docs/COURSE_MODULE_EXTENSION_GUIDE.md](docs/COURSE_MODULE_EXTENSION_GUIDE.md)：新增课程类型或任务类型指南
