#!/bin/bash

# ========================================================================
#   About This File
# ========================================================================

# Prints every URL path the URL list checks, one per line: each page and
# permalink, the redirects, each asset at the root and under a view and a
# poster permalink, and the repo files that must stay private. Reads the
# site from public/ when it exists and from the repo root otherwise, so a
# checkout before and after the move prints the same list.
#
# Usage: scripts/url-list/urls.sh



# ================================================
#   Setup
# ================================================

set -u
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
SITE="$REPO"
PREFIX="/tools/models-gone-wild"

[ -d "$REPO/public" ] && SITE="$REPO/public"

SLUGS="$(grep -o 'slug:"[a-z0-9-]*"' "$SITE/js/cases.js" | sed 's/^slug:"\(.*\)"$/\1/')"
FIRST="$(printf "%s\n" "$SLUGS" | head -1)"
ASSETS="$(cd "$SITE" && git ls-files css js fonts img | grep -v '\.md$')"



# ================================================
#   Pages and Redirects
# ================================================

for page in "/" "/index.html" "/threat-matrix/" "/lab-counts/"; do
    echo "$PREFIX$page"
done

printf "%s\n" "$SLUGS" | while IFS= read -r slug; do
    echo "$PREFIX/poster/$slug/"
done

for page in "/methodology/" "/methodology/index.html" "/threat-matrix/index.html" "/poster/$FIRST/index.html" "/no-such-page/" "" "/threat-matrix" "/poster/$FIRST" "/?view=matrix" "/?view=labs"; do
    echo "$PREFIX$page"
done



# ================================================
#   Assets
# ================================================

for base in "" "/threat-matrix" "/poster/$FIRST"; do
    printf "%s\n" "$ASSETS" | while IFS= read -r asset; do
        echo "$PREFIX$base/$asset"
    done
done



# ================================================
#   Private Files
# ================================================

for private in DEPLOY.md UPDATE.md scripts/serve.py deploy/nginx/headers.conf scripts/git-hooks/pre-commit scripts/git-hooks/format-languages scripts/screenshot-diff/run.sh .claude/skills/models-gone-wild-add-case/SKILL.md .git/config js/vendor/VENDORED.md; do
    echo "$PREFIX/$private"
done