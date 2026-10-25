import sys

from .agent import ask_with_trace


def main() -> None:
    question = " ".join(sys.argv[1:]) or "Which drugs treat asthma?"
    answer, tools = ask_with_trace(question)
    print(answer)
    print(f"\n[tools called: {', '.join(tools) or 'none'}]", file=sys.stderr)


if __name__ == "__main__":
    main()
