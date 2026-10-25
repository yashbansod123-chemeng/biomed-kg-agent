import json

import pytest

from kg_agent import graph as kg
from kg_agent.tools import TOOLS, targets_of_drug


@pytest.fixture(scope="module")
def g():
    return kg.load_graph()


def test_schema(g):
    allowed = {"TARGETS", "TREATS", "ASSOCIATED_WITH", "SUBTYPE_OF"}
    assert {k for *_, k in g.edges(keys=True)} <= allowed
    drugs = [n for n, t in g.nodes(data="type") if t == "Drug"]
    assert drugs and all(kg._out(g, d, "TARGETS") for d in drugs)


def test_case_insensitive_lookup(g):
    assert kg.resolve(g, "  salbutamol ") == "Salbutamol"


def test_unknown_entity_gives_hint(g):
    with pytest.raises(kg.EntityNotFound, match="Salbutamol"):
        kg.resolve(g, "Salbutamoll")


def test_subtype_reasoning(g):
    assert {s for s, _, _ in kg.drugs_for_disease(g, "Asthma")} == {
        "Salbutamol", "Fluticasone propionate", "Mepolizumab"}
    flat = {s for s, _, _ in kg.drugs_for_disease(g, "Asthma", include_subtypes=False)}
    assert "Mepolizumab" not in flat


def test_heldout_indication_recovered(g):
    # Mepolizumab->EGPA is deliberately absent from the data; the graph should propose it.
    assert [c["disease"] for c in kg.repurposing_candidates(g, "Mepolizumab")] == ["EGPA"]


def test_connection_path(g):
    assert kg.connection_path(g, "Mepolizumab", "EGPA") == [
        ("Mepolizumab", "TARGETS", "IL5"), ("IL5", "ASSOCIATED_WITH", "EGPA")]


def test_tool_returns_json_error_not_exception():
    assert "error" in json.loads(targets_of_drug.invoke({"drug": "Aspirin"}))


def test_tool_schemas_exposed():
    assert all(t.description and t.args for t in TOOLS)
