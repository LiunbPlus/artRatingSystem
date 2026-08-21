#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_DIR="$PROJECT_DIR/logs"
mkdir -p "$RUN_DIR"

start_process() {
  local name="$1"
  local workdir="$2"
  shift 2
  local pid_file="$RUN_DIR/$name.pid"
  local log_file="$RUN_DIR/$name.log"

  if [[ -f "$pid_file" ]] && kill -0 "$(<"$pid_file")" 2>/dev/null; then
    echo "$name 已在运行（PID $(<"$pid_file")）"
    return
  fi
  (
    cd "$workdir"
    setsid "$@" >>"$log_file" 2>&1 &
    echo $! >"$pid_file"
  )
  sleep 1
  if ! kill -0 "$(<"$pid_file")" 2>/dev/null; then
    echo "$name 启动失败，请查看 $log_file" >&2
    exit 1
  fi
  echo "$name 已启动（PID $(<"$pid_file")）"
}

start_process backend "$PROJECT_DIR/backend" \
  "$PROJECT_DIR/backend/venv/bin/python" -m uvicorn main:app --host 0.0.0.0 --port 8000
start_process frontend "$PROJECT_DIR/frontend" \
  npm run dev

echo "前端：http://127.0.0.1:7999"
echo "后端：http://127.0.0.1:8000"
