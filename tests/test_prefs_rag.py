from src.guardrails import allowed_values_from_catalog
from src.prefs_rag import prefs_from_query_with_rag


def test_prefs_from_query_with_rag_outputs_allowed_labels():
    songs = [
        {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.2},
        {"genre": "lofi", "mood": "chill", "energy": 0.4, "acousticness": 0.9},
        {"genre": "rock", "mood": "intense", "energy": 0.9, "acousticness": 0.1},
    ]
    allowed_genres, allowed_moods = allowed_values_from_catalog(songs)

    res = prefs_from_query_with_rag(
        "Upbeat synth-pop workout playlist",
        songs_catalog=songs,
        kb_dir="knowledge_base",
        allowed_genres=allowed_genres,
        allowed_moods=allowed_moods,
    )

    assert res.prefs["genre"] in allowed_genres
    assert res.prefs["mood"] in allowed_moods
    assert 0.0 <= float(res.prefs["energy"]) <= 1.0
    # The KB contains enough hints that retrieval should return something.
    assert len(res.retrieved) >= 1


def test_prefs_from_query_with_rag_defaults_on_unknown_terms():
    songs = [{"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.2}]
    allowed_genres, allowed_moods = allowed_values_from_catalog(songs)

    res = prefs_from_query_with_rag(
        "music like glorp blorp please",
        songs_catalog=songs,
        kb_dir="knowledge_base",
        allowed_genres=allowed_genres,
        allowed_moods=allowed_moods,
    )

    assert res.prefs["genre"] == "pop"
    assert res.prefs["mood"] == "happy"

