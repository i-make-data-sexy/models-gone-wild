#!/bin/bash

# ========================================================================
#   About This File
# ========================================================================

# Records the URL list for a git ref locally: every path urls.sh prints,
# requested from the ref's own scripts/serve.py, with the status, the
# Location header, the canonical tag, and the robots meta. The ref runs
# from a detached worktree under /tmp/mgw-url-list, outside the repo and
# Dropbox. The list itself comes from this checkout, so two refs are
# always measured against the same paths, and diff of two lists is the
# proof that nothing moved.
#
# Usage: scripts/url-list/run.sh <ref>
#        e.g., run.sh main, then diff /tmp/mgw-url-list/main.tsv with the branch's
#
# Output: /tmp/mgw-url-list/<ref>.tsv, with any slash in the ref turned
# into a hyphen.



# ================================================
#   Setup
# ================================================

set -u
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
HERE="$REPO/scripts/url-list"
PY="$REPO/venv/bin/python3"
WORK="${MGW_URL_DIR:-/tmp/mgw-url-list}"
REF="${1:?ref}"
OUT="$WORK/$(printf "%s" "$REF" | tr / -).tsv"
SRV=""

case "$WORK" in
    "$REPO"*|*Dropbox*) echo "MGW_URL_DIR must be outside the repo and Dropbox"; exit 2 ;;
esac

cd "$REPO" || exit 2
mkdir -p "$WORK"
git worktree remove --force "$WORK/wt" 2>/dev/null

trap '[ -n "$SRV" ] && kill "$SRV" 2>/dev/null' EXIT



# ================================================
#   Worktree and Server
# ================================================

git worktree add -q --detach "$WORK/wt" "$REF" || exit 2

PORT="$("$PY" -c "import socket; s = socket.socket(); s.bind((\"127.0.0.1\", 0)); print(s.getsockname()[1]); s.close()")"
BASE="http://127.0.0.1:$PORT"
(cd "$WORK/wt" && exec "$PY" scripts/serve.py --port "$PORT") > "$WORK/server.log" 2>&1 &
SRV=$!

for _ in $(seq 1 30); do
    curl -s -o /dev/null "$BASE/tools/models-gone-wild/" && break
    sleep 1
done



# ================================================
#   The List
# ================================================

"$HERE/urls.sh" | "$HERE/probe.sh" "$BASE" > "$OUT"
STATUS=$?

kill "$SRV" 2>/dev/null
wait "$SRV" 2>/dev/null
SRV=""
git worktree remove --force "$WORK/wt"

echo "$REF ($(git rev-parse --short "$REF")): $(($(wc -l < "$OUT") - 1)) URLs in $OUT"
exit $STATUS