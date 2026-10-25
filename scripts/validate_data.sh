#!/usr/bin/env bash
set -euo pipefail
f="${1:-data/triples.csv}"
expected="subject,subject_type,predicate,object,object_type"

[[ -f "$f" ]] || { echo "ERROR: $f not found" >&2; exit 1; }
header=$(head -n1 "$f" | tr -d '\r')
[[ "$header" == "$expected" ]] || { echo "ERROR: bad header: $header" >&2; exit 1; }

bad=$(awk -F',' 'NR>1 && NF!=5 {print NR}' "$f")
[[ -z "$bad" ]] || { echo "ERROR: wrong field count on lines: $bad" >&2; exit 1; }

empty=$(awk -F',' 'NR>1 {for (i=1;i<=NF;i++) if ($i=="") {print NR; break}}' "$f")
[[ -z "$empty" ]] || { echo "ERROR: empty fields on lines: $empty" >&2; exit 1; }

badrel=$(awk -F',' 'NR>1 && $3 !~ /^(TARGETS|TREATS|ASSOCIATED_WITH|SUBTYPE_OF)$/ {print NR": "$3}' "$f")
[[ -z "$badrel" ]] || { echo "ERROR: unknown predicates: $badrel" >&2; exit 1; }

dups=$(tail -n +2 "$f" | sort | uniq -d)
[[ -z "$dups" ]] || { echo "ERROR: duplicate triples: $dups" >&2; exit 1; }

echo "OK: $(( $(wc -l < "$f") - 1 )) triples validated"
