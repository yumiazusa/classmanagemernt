#!/usr/bin/env sh
set -eu

# 用法:
#   ./start_backend.sh
#   ./start_backend.sh 8083
#   ./start_backend.sh 8083 0.0.0.0 app.main:app
#
# 参数:
#   $1 port (默认 8083)
#   $2 host (默认 0.0.0.0)
#   $3 app  (默认 app.main:app)

PORT="${1:-8083}"
HOST="${2:-0.0.0.0}"
APP_MODULE="${3:-app.main:app}"
APP_ENV="${APP_ENV:-development}"
UVICORN_WORKERS="${UVICORN_WORKERS:-2}"

if [ ! -d "app" ]; then
  echo "请在 backend 目录执行该脚本。当前目录: $(pwd)"
  exit 1
fi

echo "[start_backend] 检查端口占用: ${PORT}"

if command -v lsof >/dev/null 2>&1; then
  PIDS="$(lsof -tiTCP:"${PORT}" -sTCP:LISTEN || true)"
  if [ -n "${PIDS}" ]; then
    echo "[start_backend] 端口 ${PORT} 已被进程 ${PIDS} 占用；请先确认并停止对应服务，或指定其他端口。"
    exit 1
  fi
elif command -v ss >/dev/null 2>&1; then
  if ss -ltn 2>/dev/null | grep -Eq ":${PORT}[[:space:]]"; then
    echo "[start_backend] 端口 ${PORT} 已被占用；请先确认并停止对应服务，或指定其他端口。"
    exit 1
  fi
else
  echo "[start_backend] 未找到 lsof/ss，跳过端口占用检查。"
fi

if [ "${APP_ENV}" = "production" ]; then
  if [ "${UVICORN_WORKERS}" -lt 1 ] 2>/dev/null; then
    UVICORN_WORKERS=1
  fi
  echo "[start_backend] 生产模式启动: python3 -m uvicorn ${APP_MODULE} --host ${HOST} --port ${PORT} --workers ${UVICORN_WORKERS}"
  exec python3 -m uvicorn "${APP_MODULE}" --host "${HOST}" --port "${PORT}" --workers "${UVICORN_WORKERS}"
else
  echo "[start_backend] 开发模式启动: python3 -m uvicorn ${APP_MODULE} --reload --host ${HOST} --port ${PORT}"
  exec python3 -m uvicorn "${APP_MODULE}" --reload --host "${HOST}" --port "${PORT}"
fi
