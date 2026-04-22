#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: scripts/render_docx.sh input.md output.docx [--obsidian]" >&2
  exit 1
fi

CALLER_DIR="$(pwd)"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export UV_INDEX_URL="${UV_INDEX_URL:-https://pypi.tuna.tsinghua.edu.cn/simple}"

cd "$ROOT_DIR"

if [ ! -x ".venv/bin/python" ]; then
  echo "[ERROR] missing .venv; run scripts/bootstrap_uv.sh first" >&2
  exit 1
fi

INPUT_ARG="$1"
OUTPUT_ARG="$2"
shift 2

INPUT_ABS="$(python3 - <<'PY' "$CALLER_DIR" "$INPUT_ARG"
from pathlib import Path
import sys
base = Path(sys.argv[1])
path = Path(sys.argv[2]).expanduser()
print((path if path.is_absolute() else base / path).resolve())
PY
)"

OUTPUT_ABS="$(python3 - <<'PY' "$CALLER_DIR" "$OUTPUT_ARG"
from pathlib import Path
import sys
base = Path(sys.argv[1])
path = Path(sys.argv[2]).expanduser()
print((path if path.is_absolute() else base / path).resolve())
PY
)"

./.venv/bin/python scripts/md_to_docx.py \
  "$INPUT_ABS" \
  "$OUTPUT_ABS" \
  "$@"
