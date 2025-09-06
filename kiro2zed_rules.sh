#!/bin/bash
set -euo pipefail

OUT=".rules"
echo "<!-- generated from .kiro on $(date -Iseconds) -->" > "$OUT"

# steering 먼저
for f in .kiro/steering/*.md; do
  echo -e "\n\n---\n# $(basename "$f")\n" >> "$OUT"
  cat "$f" >> "$OUT"
done

# specs 전체
for f in .kiro/specs/*/*.md; do
  echo -e "\n\n---\n# $(basename "$f")\n" >> "$OUT"
  cat "$f" >> "$OUT"
done
