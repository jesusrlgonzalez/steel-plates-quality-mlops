#!/usr/bin/env bash
# Builds a release evidence ZIP from a git ref and an assets list. Used by .github/workflows/release.yml
# and by tests/test_release_p02.py, so the published bundle and the tested one are the same.
# Usage: deploy/build_release_bundle.sh <ref> <out.zip> <assets list>
set -euo pipefail
ref=$1 out=$2 list=$3
keep=()
while IFS= read -r p || [ -n "$p" ]; do
  p=${p%%#*}; p=${p%"${p##*[![:space:]]}"}
  [ -z "$p" ] && continue
  git cat-file -e "$ref:$p" 2>/dev/null && keep+=("$p")
done < "$list"
git archive --format=zip -o "$out" "$ref" -- "${keep[@]}"
