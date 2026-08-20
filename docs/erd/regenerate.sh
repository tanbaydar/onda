#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)

python3 "$SCRIPT_DIR/render_erd.py" "$REPO_ROOT/docs/onda.dbml" "$SCRIPT_DIR"
