import os

from langchain.agents import create_agent

from .tools import TOOLS

SYSTEM_PROMPT = (
    "You answer questions about a small biomedical knowledge graph. "
    "Use the tools for every factual claim and never answer from your own memory. "
    "Cite the triples you relied on as (subject, relation, object). "
    "If a tool returns an error or the graph has no answer, say so plainly."
)


def build_agent(model: str | None = None):
    return create_agent(
        model=model or os.getenv("KG_MODEL", "anthropic:claude-sonnet-5-5"),
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )


def ask_with_trace(question: str, agent=None) -> tuple[str, list[str]]:
    agent = agent or build_agent()
    state = agent.invoke({"messages": [{"role": "user", "content": question}]})
    tools_called = [
        tc["name"] for m in state["messages"] for tc in (getattr(m, "tool_calls", None) or [])
    ]
    return state["messages"][-1].text, tools_called
