# Frontend (Vue 3 + Vite)

## 环境要求

- Node.js 18+
- npm 9+

## 安装依赖

```bash
npm install
```

## 启动开发服务

```bash
npm run dev
```

开发服务默认运行在 `http://localhost:8082`，`/api` 请求会代理到 `http://127.0.0.1:8083`。如后端运行在其他地址，可在 `frontend/.env.development` 中修改 `VITE_PROXY_TARGET`。

## 构建生产包

```bash
npm run build
```
