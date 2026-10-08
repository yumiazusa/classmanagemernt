# LETS V1.0 本地开发检查清单

先阅读 [项目首页](../README.md) 与 [技术文档](TECHNICAL_V1.0.md)。当前默认后端端口为 8083，前端端口为 8082，数据库名为 `teaching_framework`。

1. 按 `backend/.env.example` 创建 `backend/.env`，配置本地 MySQL 8 账号；在 `backend` 安装 Python 3.11+ 依赖。
2. 运行 `python -m app.db.init_db --seed-demo` 创建两名教师、八名学生、两个班级、两门未连接的示例课程及课程文档。该命令可重复执行，不覆盖同名记录；如需替换现有数据，先备份后运行 `--reset-demo`，仅保留已有 `admin`。演示数据仅用于本地/测试库。
3. 在 `backend` 执行 `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8083`，检查 `http://127.0.0.1:8083/health`。
4. 在 `frontend` 执行 `npm ci`、`npm run dev`，打开 `http://127.0.0.1:8082`。Vite 默认将 `/api` 代理到 8083；后端地址不同则设置 `VITE_PROXY_TARGET`。
5. 修改前端后执行 `npm run build`；修改后端后至少做模块导入、数据库初始化和对应接口的实际检查。

若本机没有 Node，可使用已有 Docker 容器：`docker exec e0c /bin/bash -lc 'cd /www/wwwroot/classmanagement/frontend && npm run build'`。这条命令只用于构建验证，实际启动地址取决于容器端口映射。

生产部署见 [部署文档](DEPLOYMENT_V1.0.md)。
