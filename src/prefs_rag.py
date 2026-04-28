from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Set, Tuple

from src.guardrails import PrefsValidation, validate_and_normalize_prefs
from src.rag import RetrievedChunk, load_knowledge_base, parse_synonym_map, retrieve


@dataclass(frozen=True)
class RagPrefsResult:
    prefs: Dict
    retrieved: List[RetrievedChunk]
    warnings: List[str]


_ENERGY_HINTS = [
    (re.compile(r"\b(workout|gym|run|hype|intense|adrenaline|heavy)\b", re.I), 0.9),
    (re.compile(r"\b(dance|party|upbeat|festival|club)\b", re.I), 0.8),
    (re.compile(r"\b(focus|study|background|calm|cozy)\b", re.I), 0.35),
    (re.compile(r"\b(relax|unwind|sleep|mellow)\b", re.I), 0.3),
]


def _match_label(query: str, label_map: Dict[str, List[str]], allowed: Set[str]) -> Optional[str]:
    q = query.lower()
    for canonical, syns in label_map.items():
        if allowed and canonical not in allowed:
            continue
        for s in syns:
            if s and re.search(rf"\b{re.escape(s)}\b", q):
                return canonical
    return None


def prefs_from_query_with_rag(
    query: str,
    *,
    songs_catalog: Sequence[Dict],
    kb_dir: str = "knowledge_base",
    allowed_genres: Optional[Set[str]] = None,
    allowed_moods: Optional[Set[str]] = None,
) -> RagPrefsResult:
    """
    RAG behavior:
    - retrieve relevant passages from the KB
    - parse synonym maps out of the retrieved context
    - extract (genre, mood, energy) from the free-text query using the retrieved map
    - apply guardrails to ensure the output fits the actual song catalog
    """
    warnings: List[str] = []
    docs = load_knowledge_base(kb_dir)
    retrieved = retrieve(query, docs, top_k=3)

    ctx = [r.chunk_text for r in retrieved]
    syn_map = parse_synonym_map(ctx)

    # Split the synonym map into genre-like and mood-like sets using catalog allowlists.
    genre_map: Dict[str, List[str]] = {}
    mood_map: Dict[str, List[str]] = {}
    for k, v in syn_map.items():
        if allowed_genres and k in allowed_genres:
            genre_map[k] = v
        if allowed_moods and k in allowed_moods:
            mood_map[k] = v

    genre = _match_label(query, genre_map, allowed_genres or set())
    mood = _match_label(query, mood_map, allowed_moods or set())

    energy: Optional[float] = None
    for rx, val in _ENERGY_HINTS:
        if rx.search(query):
            energy = val
            break

    likes_acoustic = bool(re.search(r"\b(acoustic|unplugged)\b", query, re.I))

    raw = {
        "genre": genre or "",
        "mood": mood or "",
        "energy": energy if energy is not None else 0.6,
        "likes_acoustic": likes_acoustic,
    }

    validation: PrefsValidation = validate_and_normalize_prefs(
        raw,
        allowed_genres=allowed_genres,
        allowed_moods=allowed_moods,
    )
    warnings.extend(validation.warnings)

    # If retrieval failed to give anything useful, surface that (still functional, just less smart).
    if not retrieved:
        warnings.append("no KB passages retrieved; used heuristic parsing + defaults")

    return RagPrefsResult(
        prefs=validation.normalized_prefs,
        retrieved=retrieved,
        warnings=warnings,
    )

