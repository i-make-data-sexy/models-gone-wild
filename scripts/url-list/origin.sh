#!/bin/bash

# ========================================================================
#   About This File
# ========================================================================

# Records the URL list at an origin: the same paths run.sh checks,
# requested on the server from nginx at https://127.0.0.1 with the given
# Host header, past Cloudflare. Staging lets loopback through without its
# password, so both hosts answer. One ssh carries probe.sh and the path
# list over and brings the rows back.
#
# Usage: scripts/url-list/origin.sh <host>
#        e.g., origin.sh www.annielytics.com
#        origin.sh staging.annielytics.com
#
# Output: /tmp/mgw-url-list/<host>.tsv



# ================================================
#   Setup
# ================================================

set -u
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
HERE="$REPO/scripts/url-list"
WORK="${MGW_URL_DIR:-/tmp/mgw-url-list}"
HOST="${1:?host}"
OUT="$WORK/$HOST.tsv"
SERVER="anniecushing@208.109.215.51"
KEY="$HOME/.ssh/id_ed25519_imds"

case "$HOST" in
    *[!a-z0-9.-]*) echo "The host may hold only lowercase letters, digits, dots, and hyphens"; exit 2 ;;
esac

mkdir -p "$WORK"
"$HERE/urls.sh" > "$WORK/paths.txt" || exit 2



# ================================================
#   The List
# ================================================

COPYFILE_DISABLE=1 tar --no-xattrs --no-mac-metadata -cf - -C "$HERE" probe.sh -C "$WORK" paths.txt \
    | ssh -i "$KEY" "$SERVER" "d=\"\$(mktemp -d)\" && tar -C \"\$d\" -xf - && bash \"\$d/probe.sh\" https://127.0.0.1 $HOST < \"\$d/paths.txt\"; s=\$?; rm -rf \"\$d\"; exit \$s" \
    > "$OUT"
STATUS=$?

echo "$HOST: $(($(wc -l < "$OUT") - 1)) URLs in $OUT"
exit $STATUS