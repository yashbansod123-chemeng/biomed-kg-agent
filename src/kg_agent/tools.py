import json

import networkx as nx
from langchain.tools import tool

from . import graph as kg


def _run(fn, *args) -> str:
    try:
        return json.dumps({"result": fn(kg.get_graph(), *args)})
    except (kg.EntityNotFound, nx.NetworkXNoPath) as e:
        return json.dumps({"error": str(e)})


@tool
def targets_of_drug(drug: str) -> str:
    """Return molecular targets of a drug as (drug, TARGETS, target) triples."""
    return _run(kg.targets_of_drug, drug)


@tool
def drugs_for_disease(disease: str) -> str:
    """Return drugs that treat a disease, including drugs for its subtypes."""
    return _run(kg.drugs_for_disease, disease)


@tool
def repurposing_candidates(drug: str) -> str:
    """Propose diseases linked to a drug's targets that the drug is not yet recorded as treating."""
    return _run(kg.repurposing_candidates, drug)


@tool
def connection_path(entity_a: str, entity_b: str) -> str:
    """Return the shortest chain of triples connecting two entities in the graph."""
    return _run(kg.connection_path, entity_a, entity_b)


TOOLS = [targets_of_drug, drugs_for_disease, repurposing_candidates, connection_path]
