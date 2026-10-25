#!/usr/bin/env bash
set -euo pipefail
IMAGE="${1:-kg-agent:local}"
out=$(docker run --rm --entrypoint python "$IMAGE" -c \
  "from kg_agent.graph import get_graph, repurposing_candidates as r; print(r(get_graph(), 'Mepolizumab')[0]['disease'])")
[[ "$out" == "EGPA" ]] || { echo "smoke test failed: got '$out'" >&2; exit 1; }
echo "smoke test OK"
