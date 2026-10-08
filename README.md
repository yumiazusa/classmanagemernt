# LETS课程管理系统 V1.0

面向学生、教师和管理员的教学管理底座。课程是授课班级、教师和独立课程模块之间的连接记录；系统不预装标准课程。

## 核心能力

- 登录、改密、个人中心
- 学生、教师、管理员三类角色与权限
- 管理员用户管理、教师管理、管理员账号管理
- 教师学生管理、学生导入、启停账号、批量重置密码
- 学生端“我的课程”，进入已启用课程对应的独立模块
- 教师端课程看板、班级/学生管理
- 管理员课程管理、班级管理、平台资料管理
- 课程管理：名称、模块连接、启停、授课教师和班级
- 课程模块注册机制：各课程按需接入独立页面和数据

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
uvicorn app.main:app --reload --host 0.0.0.0 --port 8083
```

如需一套演示账号、两个班级、两门未连接的示例课程及课程文档：

```bash
python -m app.db.init_db --seed-demo
```

此命令可重复执行，不覆盖现有同名记录。如需清除现有非 `admin` 数据并重建整套演示数据，先备份本地/测试库，再执行 `python -m app.db.init_db --reset-demo`；原 `admin` 账号和密码保持不变。演示账号使用固定初始密码，新建账号首次登录需改密；详情见 [技术文档](docs/TECHNICAL_V1.0.md)。

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端开发地址为 `http://localhost:8082`，`/api` 请求由 Vite 转发到后端 `http://127.0.0.1:8083`。

## 主要文档

- [backend/README.md](backend/README.md)：后端启动、接口与数据库说明
- [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)：长期项目上下文
- [docs/COURSE_MODULE_EXTENSION_GUIDE.md](docs/COURSE_MODULE_EXTENSION_GUIDE.md)：新增课程类型或任务类型指南
- [docs/TECHNICAL_V1.0.md](docs/TECHNICAL_V1.0.md)：V1.0 技术架构与功能边界
- [docs/DEPLOYMENT_V1.0.md](docs/DEPLOYMENT_V1.0.md)：生产部署、验证与回滚
- [docs/VERSION_CONTROL.md](docs/VERSION_CONTROL.md)：分支、版本发布与多设备同步
