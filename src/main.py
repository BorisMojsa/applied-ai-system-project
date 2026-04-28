"""
Command line runner for the Music Recommender Simulation.

Run: python -m src.main [--mode genre_first|mood_first]
"""

import argparse

from tabulate import tabulate

from src.recommender import load_songs, recommend_songs
from src.guardrails import allowed_values_from_catalog
from src.prefs_rag import prefs_from_query_with_rag
from src.run_log import JsonlLogger


def _recommendation_table(recommendations: list) -> str:
    """Build a tabulate table including per-song reasons (stretch: transparency)."""
    rows = []
    for i, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        rows.append(
            [
                i,
                song["title"],
                song["artist"],
                song["genre"],
                song["mood"],
                f"{score:.3f}",
                explanation,
            ]
        )
    headers = ["#", "Title", "Artist", "Genre", "Mood", "Score", "Reasons"]
    return tabulate(
        rows,
        headers=headers,
        tablefmt="github",
        stralign="left",
        # Keep reasons on one logical row (wide terminal); narrow cols for metadata only.
        maxcolwidths=[None, 24, 20, 14, 12, 8, None],
    )


def _print_recommendations(
    title: str,
    user_prefs: dict,
    songs: list,
    k: int = 5,
    ranking_mode: str = "genre_first",
) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)
    print(f"Ranking mode: {ranking_mode}")
    print(f"Profile: {user_prefs}")
    recommendations = recommend_songs(
        user_prefs, songs, k=k, ranking_mode=ranking_mode
    )
    print(f"\nTop {k} recommendations:\n")
    print(_recommendation_table(recommendations))
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Music recommender CLI (content-based scoring)."
    )
    parser.add_argument(
        "--mode",
        choices=["genre_first", "mood_first"],
        default="genre_first",
        help="genre_first: default weights; mood_first: boost mood vs genre for ties and nuance.",
    )
    parser.add_argument(
        "--query",
        default="",
        help="Optional free-text vibe request (enables RAG-based preference parsing).",
    )
    parser.add_argument(
        "--kb_dir",
        default="knowledge_base",
        help="Directory containing markdown docs used for retrieval (RAG).",
    )
    args = parser.parse_args()
    ranking_mode = args.mode

    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    logger = JsonlLogger()
    allowed_genres, allowed_moods = allowed_values_from_catalog(songs)

    if args.query.strip():
        rag = prefs_from_query_with_rag(
            args.query,
            songs_catalog=songs,
            kb_dir=args.kb_dir,
            allowed_genres=allowed_genres,
            allowed_moods=allowed_moods,
        )
        title = "Free-text query (RAG) — Parsed preferences"
        print("\n" + "=" * 72)
        print(title)
        print("=" * 72)
        print(f"Query: {args.query!r}")
        print(f"Parsed prefs: {rag.prefs}")
        if rag.warnings:
            print("Warnings:")
            for w in rag.warnings:
                print(f"- {w}")
        if rag.retrieved:
            print("\nRetrieved context:")
            for r in rag.retrieved:
                print(f"- {r.title} (score={r.score:.3f})")
        _print_recommendations(title, rag.prefs, songs, k=5, ranking_mode=ranking_mode)
        logger.log(
            "rag_run",
            {
                "query": args.query,
                "prefs": rag.prefs,
                "warnings": rag.warnings,
                "retrieved": rag.retrieved,
                "ranking_mode": ranking_mode,
            },
        )
    else:
        profiles = [
            (
                "Profile A — High-Energy Pop",
                {"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False},
            ),
            (
                "Profile B — Chill Lofi",
                {"genre": "lofi", "mood": "chill", "energy": 0.38, "likes_acoustic": True},
            ),
            (
                "Profile C — Deep Intense Rock",
                {"genre": "rock", "mood": "intense", "energy": 0.92, "likes_acoustic": False},
            ),
            (
                "Profile D — Adversarial (high energy + sad mood)",
                {"genre": "pop", "mood": "sad", "energy": 0.95, "likes_acoustic": False},
            ),
            (
                "Profile E — Adversarial (conflicting: chill genre hint + metal taste)",
                {"genre": "metal", "mood": "relaxed", "energy": 0.5, "likes_acoustic": True},
            ),
        ]

        for title, prefs in profiles:
            _print_recommendations(title, prefs, songs, k=5, ranking_mode=ranking_mode)


if __name__ == "__main__":
    main()
