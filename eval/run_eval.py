"""LLM-in-the-loop evaluation: tool selection, answer content, and grounding."""
import json
import os
import sys
from pathlib import Path

from kg_agent.agent import ask_with_trace, build_agent

CASES = json.loads(Path(__file__).with_name("cases.json").read_text())
PASS_THRESHOLD = 0.8


def score(case: dict, answer: str, tools: list[str]) -> dict:
    a = answer.lower()
    return {
        "tool_ok": set(case["expected_tools"]) <= set(tools),
        "content_ok": all(s.lower() in a for s in case.get("must_contain", [])),
        "grounded_ok": not any(s.lower() in a for s in case.get("must_not_contain", [])),
    }


def main() -> int:
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set - skipping LLM eval.")
        return 0
    agent, rows = build_agent(), []
    for c in CASES:
        answer, tools = ask_with_trace(c["question"], agent)
        s = score(c, answer, tools)
        rows.append(s)
        print(f"[{'PASS' if all(s.values()) else 'FAIL'}] {c['question']}\n    tools={tools} {s}")
    rate = sum(all(r.values()) for r in rows) / len(rows)
    print(f"\npass rate: {rate:.0%} (threshold {PASS_THRESHOLD:.0%})")
    return 0 if rate >= PASS_THRESHOLD else 1


if __name__ == "__main__":
    sys.exit(main())
