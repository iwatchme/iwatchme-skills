#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export UV_INDEX_URL="${UV_INDEX_URL:-https://pypi.tuna.tsinghua.edu.cn/simple}"

cd "$ROOT_DIR"

if [ ! -x ".venv/bin/python" ]; then
  uv venv .venv
fi

uv pip install --python .venv/bin/python python-docx lxml

echo "[OK] uv environment ready at $ROOT_DIR/.venv"
