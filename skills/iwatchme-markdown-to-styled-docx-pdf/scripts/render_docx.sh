#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: scripts/render_docx.sh input.md output.docx [--obsidian] [--docx-only]" >&2
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

DOCX_ONLY=false
PASS_THROUGH_ARGS=()
for arg in "$@"; do
  if [ "$arg" = "--docx-only" ]; then
    DOCX_ONLY=true
  else
    PASS_THROUGH_ARGS+=("$arg")
  fi
done

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
  "${PASS_THROUGH_ARGS[@]}" \
  --docx-only

if [ "$DOCX_ONLY" = true ]; then
  exit 0
fi

PROFILE_DIR="${LIBREOFFICE_PROFILE_DIR:-/tmp/codex-libreoffice-profile}"
mkdir -p "$PROFILE_DIR"

PROFILE_URI="$(python3 - <<'PY' "$PROFILE_DIR"
from pathlib import Path
import sys
path = Path(sys.argv[1]).expanduser()
if not path.is_absolute():
    path = Path.cwd() / path
print(path.absolute().as_uri())
PY
)"

if [ -x "/Applications/LibreOffice.app/Contents/MacOS/soffice" ]; then
  SOFFICE_BIN="/Applications/LibreOffice.app/Contents/MacOS/soffice"
elif command -v soffice >/dev/null 2>&1; then
  SOFFICE_BIN="$(command -v soffice)"
else
  echo "[ERROR] 未检测到 LibreOffice/soffice，请先安装 LibreOffice，或改用 --docx-only 仅生成 docx。" >&2
  exit 1
fi

cd "$CALLER_DIR"
exec "$SOFFICE_BIN" \
  "-env:UserInstallation=$PROFILE_URI" \
  --headless \
  --convert-to pdf \
  --outdir "$(dirname "$OUTPUT_ABS")" \
  "$OUTPUT_ABS"
