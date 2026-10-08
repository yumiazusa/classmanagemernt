# LETS课程管理系统 V1.0 部署文档

以下以 Linux、MySQL 8、Nginx、systemd 为例。部署以 `v1.0` 标签固定的提交为准；项目目录示例 `/opt/lets`，域名示例 `lets.example.com`，执行前须替换。

## 1. 准备代码和环境

需要 Python 3.11+、Node.js 18+、npm 9+、MySQL 8.0+、Nginx、Git，以及服务器访问仓库的权限。准备域名、HTTPS 证书、独立数据库账号和随机 JWT 密钥。V1.0 只支持全新库；已有数据升级必须先设计迁移。

```bash
git clone git@github.com:yumiazusa/classmanagemernt.git /opt/lets
cd /opt/lets
git fetch --tags origin
git checkout --detach v1.0
```

服务器若跟踪最新已发布版本，可检出 `main` 并在发版后执行 `git pull --ff-only origin main`；固定标签便于精确回滚。

## 2. 数据库

在 MySQL 管理会话中执行，替换示例密码：

```sql
CREATE DATABASE teaching_framework CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'lets_app'@'127.0.0.1' IDENTIFIED BY '替换为强密码';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, DROP, REFERENCES
ON teaching_framework.* TO 'lets_app'@'127.0.0.1';
```

当前后端启动时会执行 `CREATE DATABASE IF NOT EXISTS` 和 `create_all()`，因此初始化账号需要相应 CREATE/DDL 权限。初始化后可按实际运行需要收紧权限；结构迁移需独立授权流程。

## 3. 后端

```bash
cd /opt/lets/backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

编辑 `backend/.env`，至少设置：

```dotenv
APP_NAME=LETS Course Management API
APP_ENV=production
APP_DEBUG=false
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=lets_app
MYSQL_PASSWORD=替换为强密码
MYSQL_DB=teaching_framework
JWT_SECRET_KEY=替换为随机长密钥
CORS_ALLOW_ORIGINS=https://lets.example.com
```

同源 `/api` 代理不依赖跨域配置，但应避免示例文件中的 `*`。随后执行：

```bash
chmod 600 .env
.venv/bin/python -m app.db.init_db
.venv/bin/python -m app.db.init_db --bootstrap-admin
```

`--bootstrap-admin` 会交互设置至少 12 位的初始密码；若 `admin` 已存在则不改动。生产环境不要执行 `--seed-demo`，该选项会创建带固定示例密码的账号。完成后将 `backend/.env` 的所有权交给后端服务账号，保持 600 权限。创建 `/etc/systemd/system/lets-api.service`；`User`、`Group` 改成有权读取项目及 `.env` 的服务账号：

```ini
[Unit]
Description=LETS Course Management API
After=network-online.target mysql.service
Wants=network-online.target

[Service]
Type=simple
User=lets
Group=lets
WorkingDirectory=/opt/lets/backend
Environment=APP_ENV=production
ExecStart=/opt/lets/backend/.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8083 --workers 2
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

先创建并授权 `lets` 系统账号，确保其可读取 `.env`；若 MySQL 单元名不同，修改 `After`。例如账号创建后执行 `sudo chown lets:lets /opt/lets/backend/.env`。启用与验证：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now lets-api
sudo systemctl status lets-api
curl --fail http://127.0.0.1:8083/health
```

启动失败时查看 `journalctl -u lets-api -n 100`。

## 4. 前端和 Nginx

```bash
cd /opt/lets/frontend
npm ci
npm run build
```

默认生产包请求同源 `/api`。以下内容放到启用 HTTPS 的 Nginx 站点配置中：

```nginx
server {
    listen 443 ssl;
    server_name lets.example.com;
    ssl_certificate /etc/letsencrypt/live/lets.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/lets.example.com/privkey.pem;

    root /opt/lets/frontend/dist;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8083;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location = /health {
        proxy_pass http://127.0.0.1:8083/health;
    }
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Nginx 账号须能遍历 `/opt/lets` 并读取 `frontend/dist`，无需读取 `backend/.env`。执行 `sudo nginx -t` 后重载 Nginx，并为 HTTP 配置 HTTPS 重定向。证书和防火墙配置依服务器环境而定。

## 5. 验收与回滚

1. `curl --fail https://lets.example.com/health` 返回 `{"status":"ok"}`；打开 `/login` 并刷新子路由。
2. 用实际创建的管理员账号登录，检查班级、课程、模块连接和平台文档；用教师、学生账号验证课程可见性。初始无模块时课程应保持未连接。
3. 查看浏览器 `/api` 请求、`journalctl -u lets-api` 和 Nginx 日志。

本地或测试库如需完整演示数据，可执行 `cd /opt/lets/backend && .venv/bin/python -m app.db.init_db --seed-demo`，生成管理员、两名教师、八名学生、两个班级、两门未连接示例课程及其文档；该命令可重复运行且不覆盖同名记录。若要替换已有演示数据，先备份，再运行 `--reset-demo`；它保留 `admin` 并清除其他业务数据。固定初始密码列在技术文档中，测试后应修改。

新版本先在测试库验证迁移，再备份生产库并部署。仅更新代码时，`git fetch --tags origin`、`git checkout --detach <新标签>`、重新安装锁定依赖、构建并重启。回滚代码时检出上一个标签，重新安装依赖、构建、重启并验证。数据库字段若已迁移，代码回滚未必足够，需按该版本迁移/备份方案恢复数据库。数据库备份与 `.env` 保存在仓库外。
