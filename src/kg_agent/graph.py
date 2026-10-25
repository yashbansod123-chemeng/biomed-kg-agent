"""Tiny biomedical knowledge graph: loading and deterministic queries."""
from __future__ import annotations

import csv
import os
from difflib import get_close_matches
from functools import lru_cache
from itertools import pairwise
from pathlib import Path

import networkx as nx

DEFAULT_DATA = Path(__file__).resolve().parents[2] / "data" / "triples.csv"


class EntityNotFound(LookupError):
    pass


def load_graph(path: str | Path | None = None) -> nx.MultiDiGraph:
    path = Path(path or os.getenv("KG_DATA", DEFAULT_DATA))
    g = nx.MultiDiGraph()
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            s, p, o = (row[k].strip() for k in ("subject", "predicate", "object"))
            g.add_node(s, type=row["subject_type"].strip())
            g.add_node(o, type=row["object_type"].strip())
            g.add_edge(s, o, key=p, relation=p)
    return g


@lru_cache(maxsize=1)
def get_graph() -> nx.MultiDiGraph:
    return load_graph()


def resolve(g: nx.MultiDiGraph, name: str) -> str:
    """Case-insensitive entity lookup with 'did you mean' hints."""
    lookup = {n.lower(): n for n in g.nodes}
    key = name.strip().lower()
    if key in lookup:
        return lookup[key]
    hints = [lookup[h] for h in get_close_matches(key, lookup, n=3, cutoff=0.6)]
    msg = f"'{name}' not in graph"
    raise EntityNotFound(msg + (f"; did you mean {hints}?" if hints else ""))


def _out(g, node, rel):
    return sorted(v for _, v, k in g.out_edges(node, keys=True) if k == rel)


def _in(g, node, rel):
    return sorted(u for u, _, k in g.in_edges(node, keys=True) if k == rel)


def targets_of_drug(g, drug: str) -> list[tuple]:
    d = resolve(g, drug)
    return [(d, "TARGETS", t) for t in _out(g, d, "TARGETS")]


def drugs_for_disease(g, disease: str, include_subtypes: bool = True) -> list[tuple]:
    d = resolve(g, disease)
    diseases = [d] + (_in(g, d, "SUBTYPE_OF") if include_subtypes else [])
    return [(drug, "TREATS", dis) for dis in diseases for drug in _in(g, dis, "TREATS")]


def repurposing_candidates(g, drug: str) -> list[dict]:
    """2-hop hypothesis: drug -TARGETS-> gene -ASSOCIATED_WITH-> disease not yet treated."""
    d = resolve(g, drug)
    treated = set(_out(g, d, "TREATS"))
    return [
        {"disease": dis, "evidence": [(d, "TARGETS", t), (t, "ASSOCIATED_WITH", dis)]}
        for t in _out(g, d, "TARGETS")
        for dis in _out(g, t, "ASSOCIATED_WITH")
        if dis not in treated
    ]


def connection_path(g, a: str, b: str) -> list[tuple]:
    s, t = resolve(g, a), resolve(g, b)
    path = nx.shortest_path(g.to_undirected(as_view=True), s, t)
    triples = []
    for u, v in pairwise(path):
        head, tail = (u, v) if g.has_edge(u, v) else (v, u)
        triples.append((head, next(iter(g[head][tail])), tail))
    return triples
