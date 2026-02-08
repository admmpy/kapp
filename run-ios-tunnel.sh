#!/usr/bin/env bash
set -euo pipefail

PORT=${PORT:-4173}
ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)

command -v ngrok >/dev/null 2>&1 || {
  echo "ngrok not found. Install with: brew install ngrok/ngrok/ngrok" >&2
  exit 1
}

command -v caddy >/dev/null 2>&1 || {
  echo "caddy not found. Install with: brew install caddy" >&2
  exit 1
}

# Ensure backend venv
if [ ! -f "$ROOT_DIR/backend/venv/bin/activate" ]; then
  echo "Creating backend venv..."
  python3 -m venv "$ROOT_DIR/backend/venv"
  "$ROOT_DIR/backend/venv/bin/pip" install -r "$ROOT_DIR/backend/requirements.txt"
fi

# Build web with same-origin API
VITE_API_URL= npm run web:build

# Start backend
pushd "$ROOT_DIR/backend" >/dev/null
source venv/bin/activate
python app.py > /tmp/kapp-backend.log 2>&1 &
BACKEND_PID=$!
popd >/dev/null

# Start Caddy reverse proxy
pushd "$ROOT_DIR" >/dev/null
caddy run --config scripts/Caddyfile.ios > /tmp/kapp-caddy.log 2>&1 &
CADDY_PID=$!
popd >/dev/null

cleanup() {
  if kill -0 "$CADDY_PID" 2>/dev/null; then
    kill "$CADDY_PID" || true
  fi
  if kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" || true
  fi
}
trap cleanup EXIT

# Wait for proxy to be reachable
for _ in $(seq 1 30); do
  if curl -sf "http://localhost:${PORT}" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

if ! curl -sf "http://localhost:${PORT}" >/dev/null 2>&1; then
  echo "Local proxy did not start. Check /tmp/kapp-caddy.log" >&2
  exit 1
fi

echo "Local proxy running on http://localhost:${PORT}"

# Start ngrok tunnel (foreground) so URL is visible
if [ -n "${NGROK_AUTHTOKEN:-}" ]; then
  ngrok config add-authtoken "$NGROK_AUTHTOKEN" >/dev/null 2>&1 || true
fi
ngrok http "$PORT"
