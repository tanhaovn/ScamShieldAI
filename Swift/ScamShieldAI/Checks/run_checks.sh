#!/bin/bash
set -euo pipefail
CHECK_ROOT="$(cd "$(dirname "$0")" && pwd)"
SOURCE_ROOT="$CHECK_ROOT/../ScamShieldAI"
CHECK_BUILD="$(mktemp -d /tmp/scamshield-checks.XXXXXX)"
trap 'rm -rf "$CHECK_BUILD"' EXIT
for CHECK_NAME in MultiSourceCheck HistoryStorageCheck; do
  swiftc -D DEBUG -swift-version 5 -module-cache-path "$CHECK_BUILD/modules" \
    "$SOURCE_ROOT"/Networking/*.swift \
    "$SOURCE_ROOT"/Services/*.swift \
    "$SOURCE_ROOT"/Models/*.swift \
    "$SOURCE_ROOT"/Utils/Constants.swift \
    "$SOURCE_ROOT"/Utils/L10n.swift \
    "$CHECK_ROOT/$CHECK_NAME.swift" -o "$CHECK_BUILD/$CHECK_NAME"
  "$CHECK_BUILD/$CHECK_NAME"
done
