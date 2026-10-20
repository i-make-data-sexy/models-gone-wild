#!/bin/bash

# ========================================================================
#   About This File
# ========================================================================

# Requests each URL path read from stdin, without following redirects, and
# prints a tab-separated row per path: the status, the Location header, the
# canonical tag, the robots meta, the canonical Link header, the meta
# description, og:url, and og:image. A dash marks a missing value. With a
# host, every request carries that Host header, and a Location naming that
# host is shortened to its path so staging and production lists compare.
#
# Usage: scripts/url-list/probe.sh <base> [host] < paths
#        e.g., probe.sh http://127.0.0.1:8899 < paths.txt
#        probe.sh https://127.0.0.1 www.annielytics.com < paths.txt



# ================================================
#   Setup
# ================================================

set -u
BASE="${1:?base URL}"
HOST="${2:-}"
TMP="$(mktemp -d)"
ARGS=(-sk --max-time 20)

trap 'rm -rf "$TMP"' EXIT

[ -n "$HOST" ] && ARGS+=(-H "Host: $HOST")



# ================================================
#   Rows
# ================================================

printf "path\tstatus\tlocation\tcanonical\trobots\tlink\tdescription\tog_url\tog_image\n"

while IFS= read -r path; do
    : > "$TMP/body"
    status="$(curl "${ARGS[@]}" -o "$TMP/body" -D "$TMP/head" -w "%{http_code}" "$BASE$path")"
    location="$(tr -d '\r' < "$TMP/head" | sed -n 's/^[Ll]ocation: *//p' | head -1)"
    link="$(tr -d '\r' < "$TMP/head" | sed -n 's/^[Ll]ink: *//p' | head -1)"
    canonical=""
    robots=""
    description=""
    og_url=""
    og_image=""

    [ -n "$HOST" ] && location="${location#https://$HOST}"

    if tr -d '\r' < "$TMP/head" | grep -qi '^content-type: *text/html'; then
        canonical="$(grep -aio '<link[^>]*rel="canonical"[^>]*>' "$TMP/body" | sed -n 's/.*href="\([^"]*\)".*/\1/p' | head -1)"
        robots="$(grep -aio '<meta[^>]*name="robots"[^>]*>' "$TMP/body" | sed -n 's/.*content="\([^"]*\)".*/\1/p' | head -1)"
        description="$(grep -aio '<meta[^>]*name="description"[^>]*>' "$TMP/body" | sed -n 's/.*content="\([^"]*\)".*/\1/p' | head -1)"
        og_url="$(grep -aio '<meta[^>]*property="og:url"[^>]*>' "$TMP/body" | sed -n 's/.*content="\([^"]*\)".*/\1/p' | head -1)"
        og_image="$(grep -aio '<meta[^>]*property="og:image"[^>]*>' "$TMP/body" | sed -n 's/.*content="\([^"]*\)".*/\1/p' | head -1)"
    fi

    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$path" "$status" "${location:--}" "${canonical:--}" "${robots:--}" \
        "${link:--}" "${description:--}" "${og_url:--}" "${og_image:--}"
done