#!/bin/bash

# ========================================================================
#   About This File
# ========================================================================

# Lists every Content Security Policy violation the app's pages cause, by
# visiting every page and home page state with Chrome under the policy the
# ref ships in deploy/nginx/headers.conf. An empty list means no page loses
# anything to the policy. A port of AI Strategy's scripts/csp-walk/.
#
# Usage: scripts/csp-walk/run.sh [ref]     (ref defaults to HEAD)
#
# Reuses the screenshot diff's setup: the ref runs from a detached worktree
# under /tmp/mgw-csp-walk, outside the repo and Dropbox, served by that
# ref's own scripts/serve.py on a free port. The walk itself is this
# checkout's walk.py, so a ref from before the walk existed can be walked.
#
# Output: /tmp/mgw-csp-walk/report.json, the downloaded poster beside it,
# and a summary on stdout. Exits 1 when any violation or JavaScript error
# turns up.


# ================================================
#   Setup
# ================================================

set -u
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
HERE="$REPO/scripts/csp-walk"
PY="$REPO/venv/bin/python3"
WORK="${MGW_CSP_DIR:-/tmp/mgw-csp-walk}"
REF="${1:-HEAD}"

case "$WORK" in
    "$REPO"*|*Dropbox*) echo "MGW_CSP_DIR must be outside the repo and Dropbox"; exit 2 ;;
esac

"$PY" -c "import playwright" 2>/dev/null || { echo "$PY needs Playwright; run pip install -r requirements-dev.txt"; exit 2; }

cd "$REPO" || exit 2
git worktree remove --force "$WORK/wt" 2>/dev/null
rm -rf "$WORK"
mkdir -p "$WORK"

# Stop the server this script started, however it exits
SRV=""
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
#   The Walk
# ================================================

echo "Walking $REF ($(git rev-parse --short "$REF"))"
echo "Header: $(curl -sI "$BASE/tools/models-gone-wild/" | grep -i '^content-security' | cut -d: -f1)"
"$PY" "$HERE/walk.py" "$BASE" "$WORK/report.json"

kill "$SRV" 2>/dev/null
wait "$SRV" 2>/dev/null
SRV=""
git worktree remove --force "$WORK/wt"


# ================================================
#   Summary
# ================================================

if [ ! -s "$WORK/report.json" ]; then
    echo "The walk wrote no report"
    exit 2
fi

"$PY" - "$WORK/report.json" <<'PYEOF'
import json, sys
rows = json.load(open(sys.argv[1]))
bad = [r for r in rows if r["violations"] or r["console"] or r["errors"]]
print(f"\n{len(rows)} pages and states walked, {len(bad)} with findings")
for r in bad:
    print(f"\n{r['page']} ({r['path']})")
    for v in r["violations"]:
        print(f"  VIOLATION {v['disposition']} {v['directive']} blocked {v['blocked']!r} "
              f"in {v['source']}:{v['line']} sample {v['sample']!r}")
    for c in r["console"]:
        print(f"  CONSOLE   {c[:240]}")
    for e in r["errors"]:
        print(f"  JS ERROR  {e}")
sys.exit(1 if bad else 0)
PYEOF