#!/bin/bash

# ========================================================================
#   About This File
# ========================================================================

# Proves a CSS, script, or page change is pixel perfect, or shows exactly
# what it moved. Captures every page in capture.py at four widths for two
# git refs, then diffs the two image sets pixel for pixel.
#
# Usage: scripts/screenshot-diff/run.sh <before-ref> <after-ref>
#        e.g. run.sh main standards-format-css
#        run.sh main main   checks the harness itself (must be clean)
#
# Runs locally because Cloudflare blocks automated browsers on staging
# and production. Each ref runs from a detached git worktree under
# /tmp/mgw-screenshots, outside the repo and Dropbox, served by that
# ref's own scripts/serve.py on a free port. Chrome aborts every request
# except the local server and Google Fonts.
#
# Output: /tmp/mgw-screenshots/shots-before, shots-after, and diff/ with a
# red-highlight image for each difference. Exits 1 when anything differs.


# ================================================
#   Setup
# ================================================

set -u
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
HERE="$REPO/scripts/screenshot-diff"
PY="$REPO/venv/bin/python3"
WORK="${MGW_SHOTS_DIR:-/tmp/mgw-screenshots}"
BEFORE="${1:?before ref}"
AFTER="${2:?after ref}"

case "$WORK" in
    "$REPO"*|*Dropbox*) echo "MGW_SHOTS_DIR must be outside the repo and Dropbox"; exit 2 ;;
esac

"$PY" -c "import playwright, PIL" 2>/dev/null || { echo "$PY needs Playwright and Pillow; run pip install -r requirements-dev.txt"; exit 2; }

mkdir -p "$WORK"
cd "$REPO" || exit 2

# Stop any server this script started, however it exits
SERVERS=()
trap 'for s in "${SERVERS[@]:-}"; do [ -n "$s" ] && kill "$s" 2>/dev/null; done' EXIT


# ================================================
#   Worktrees
# ================================================

for side in before after; do
    git worktree remove --force "$WORK/wt-$side" 2>/dev/null
done
git worktree add -q --detach "$WORK/wt-before" "$BEFORE" || exit 2
git worktree add -q --detach "$WORK/wt-after" "$AFTER" || exit 2


# ================================================
#   Capture one side at a time
# ================================================

free_port() {
    "$PY" -c "import socket; s = socket.socket(); s.bind((\"127.0.0.1\", 0)); print(s.getsockname()[1]); s.close()"
}

capture() {
    local side="$1" port
    port="$(free_port)"
    (cd "$WORK/wt-$side" && exec "$PY" scripts/serve.py --port "$port") > "$WORK/server-$side.log" 2>&1 &
    local srv=$!
    SERVERS+=("$srv")
    for _ in $(seq 1 30); do
        curl -s -o /dev/null "http://127.0.0.1:$port/tools/models-gone-wild/" && break
        sleep 1
    done
    rm -rf "$WORK/shots-$side"
    "$PY" "$HERE/capture.py" "http://127.0.0.1:$port" "$WORK/shots-$side"
    kill "$srv" 2>/dev/null
    wait "$srv" 2>/dev/null
}

# A fresh font cache per run: the before side records, the after side replays
rm -rf "$WORK/font-cache"
capture before
capture after

for side in before after; do
    git worktree remove --force "$WORK/wt-$side"
done

"$PY" "$HERE/diff.py" "$WORK/shots-before" "$WORK/shots-after" "$WORK/diff"