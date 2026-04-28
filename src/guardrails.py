from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple


@dataclass(frozen=True)
class PrefsValidation:
    ok: bool
    warnings: List[str]
    normalized_prefs: Dict


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def allowed_values_from_catalog(songs: Iterable[Dict]) -> Tuple[Set[str], Set[str]]:
    genres: Set[str] = set()
    moods: Set[str] = set()
    for s in songs:
        g = str(s.get("genre", "")).strip().lower()
        m = str(s.get("mood", "")).strip().lower()
        if g:
            genres.add(g)
        if m:
            moods.add(m)
    return genres, moods


def validate_and_normalize_prefs(
    prefs: Dict,
    *,
    allowed_genres: Optional[Set[str]] = None,
    allowed_moods: Optional[Set[str]] = None,
    default_genre: str = "pop",
    default_mood: str = "happy",
    default_energy: float = 0.6,
) -> PrefsValidation:
    warnings: List[str] = []

    genre = str(prefs.get("genre", "")).strip().lower()
    mood = str(prefs.get("mood", "")).strip().lower()

    try:
        energy = float(prefs.get("energy", default_energy))
    except Exception:
        energy = default_energy
        warnings.append("energy was not a number; defaulted to 0.6")
    energy = _clamp(energy, 0.0, 1.0)

    likes_acoustic = bool(prefs.get("likes_acoustic", False))

    if allowed_genres and genre and genre not in allowed_genres:
        warnings.append(f"genre {genre!r} not in catalog; defaulted to {default_genre!r}")
        genre = default_genre
    if not genre:
        warnings.append(f"genre missing; defaulted to {default_genre!r}")
        genre = default_genre

    if allowed_moods and mood and mood not in allowed_moods:
        warnings.append(f"mood {mood!r} not in catalog; defaulted to {default_mood!r}")
        mood = default_mood
    if not mood:
        warnings.append(f"mood missing; defaulted to {default_mood!r}")
        mood = default_mood

    normalized = {
        "genre": genre,
        "mood": mood,
        "energy": energy,
        "likes_acoustic": likes_acoustic,
    }
    return PrefsValidation(ok=True, warnings=warnings, normalized_prefs=normalized)

