"""Stretch: ranking mode weights stay consistent and switchable."""

from src.recommender import score_weights


def test_mood_first_boosts_mood_over_genre_relative_to_genre_first():
    g1, m1, e1, a1 = score_weights("genre_first")
    g2, m2, e2, a2 = score_weights("mood_first")
    assert m2 > m1
    assert g2 < g1
    assert e1 == e2 and a1 == a2
