from __future__ import annotations

import json
from dataclasses import asdict
from typing import Dict, List, Tuple

from src.guardrails import allowed_values_from_catalog
from src.prefs_rag import prefs_from_query_with_rag
from src.recommender import load_songs, recommend_songs


def _confidence(retrieved_top_score: float, warnings: List[str]) -> float:
    base = min(1.0, max(0.0, retrieved_top_score * 2.0))
    penalty = min(0.6, 0.1 * len(warnings))
    return max(0.0, min(1.0, base - penalty))


def run_eval() -> Tuple[int, int]:
    songs = load_songs("data/songs.csv")
    allowed_genres, allowed_moods = allowed_values_from_catalog(songs)

    cases = [
        ("Upbeat synth-pop workout playlist", {"genre": "pop"}),
        ("Cozy study beats, calm background music", {"genre": "lofi"}),
        ("Aggressive heavy guitars, adrenaline", {"mood": "intense"}),
    ]

    passed = 0
    results: List[Dict] = []
    for query, expectations in cases:
        rag = prefs_from_query_with_rag(
            query,
            songs_catalog=songs,
            kb_dir="knowledge_base",
            allowed_genres=allowed_genres,
            allowed_moods=allowed_moods,
        )
        recs = recommend_songs(rag.prefs, songs, k=3)
        top_score = rag.retrieved[0].score if rag.retrieved else 0.0
        conf = _confidence(top_score, rag.warnings)

        ok = True
        for k, v in expectations.items():
            if rag.prefs.get(k) != v:
                ok = False
        if not recs:
            ok = False

        passed += 1 if ok else 0
        results.append(
            {
                "query": query,
                "prefs": rag.prefs,
                "warnings": rag.warnings,
                "confidence": conf,
                "top3": [
                    {"title": s["title"], "artist": s["artist"], "score": float(score)}
                    for (s, score, _exp) in recs
                ],
                "pass": ok,
            }
        )

    total = len(cases)
    print(json.dumps({"passed": passed, "total": total, "results": results}, indent=2))
    return passed, total


if __name__ == "__main__":
    run_eval()

