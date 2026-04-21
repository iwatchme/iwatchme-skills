#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export UV_INDEX_URL="${UV_INDEX_URL:-https://pypi.tuna.tsinghua.edu.cn/simple}"

cd "$ROOT_DIR"

if [ ! -x ".venv/bin/python" ]; then
  echo "[ERROR] missing .venv; run scripts/bootstrap_uv.sh first" >&2
  exit 1
fi

uv run --python .venv/bin/python python scripts/md_to_docx.py "$@"
