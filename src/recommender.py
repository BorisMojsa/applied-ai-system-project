import csv
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

# Baseline recipe (Phase 2). Set RECOMMENDER_EXPERIMENT=1 to double energy weight and halve genre weight.
_EXPERIMENT = os.environ.get("RECOMMENDER_EXPERIMENT", "").strip() in ("1", "true", "yes")

WEIGHT_GENRE = 1.0 if _EXPERIMENT else 2.0
WEIGHT_MOOD = 1.0
WEIGHT_ENERGY_SIM = 2.0 if _EXPERIMENT else 1.0
WEIGHT_ACOUSTIC_SIM = 0.5

_RANKING_MODES = frozenset({"genre_first", "mood_first"})


def score_weights(ranking_mode: str) -> Tuple[float, float, float, float]:
    """Return (genre_w, mood_w, energy_sim_w, acoustic_sim_w) for a named ranking strategy."""
    if ranking_mode not in _RANKING_MODES:
        raise ValueError(
            f"Unknown ranking_mode {ranking_mode!r}; use one of {sorted(_RANKING_MODES)}"
        )
    g, m, e, a = WEIGHT_GENRE, WEIGHT_MOOD, WEIGHT_ENERGY_SIM, WEIGHT_ACOUSTIC_SIM
    if ranking_mode == "mood_first":
        return (g * 0.75, m * 2.0, e, a)
    return (g, m, e, a)


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def _user_profile_to_prefs(user: UserProfile) -> Dict:
    return {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "likes_acoustic": user.likes_acoustic,
    }


def _song_to_dict(song: Song) -> Dict:
    return {
        "id": song.id,
        "title": song.title,
        "artist": song.artist,
        "genre": song.genre,
        "mood": song.mood,
        "energy": song.energy,
        "tempo_bpm": song.tempo_bpm,
        "valence": song.valence,
        "danceability": song.danceability,
        "acousticness": song.acousticness,
    }


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song], ranking_mode: str = "genre_first"):
        self.songs = songs
        self._ranking_mode = ranking_mode

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return up to k songs ranked highest for this user."""
        prefs = _user_profile_to_prefs(user)
        scored: List[Tuple[float, Song]] = []
        for song in self.songs:
            total, _reasons = score_song(
                prefs, _song_to_dict(song), ranking_mode=self._ranking_mode
            )
            scored.append((total, song))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [song for _score, song in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return the same reason strings score_song uses for this song."""
        prefs = _user_profile_to_prefs(user)
        _total, reasons = score_song(
            prefs, _song_to_dict(song), ranking_mode=self._ranking_mode
        )
        return "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv into dict rows with numeric fields coerced."""
    print(f"Loading songs from {csv_path}...")
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs


def score_song(
    user_prefs: Dict,
    song: Dict,
    ranking_mode: str = "genre_first",
) -> Tuple[float, List[str]]:
    """Return total score and human-readable reason strings for one song."""
    wg, wm, we, wa = score_weights(ranking_mode)
    score = 0.0
    reasons: List[str] = []

    genre_pref = str(user_prefs.get("genre", "")).lower().strip()
    mood_pref = str(user_prefs.get("mood", "")).lower().strip()
    target_energy = float(user_prefs.get("energy", 0.5))
    likes_acoustic = bool(user_prefs.get("likes_acoustic", False))

    song_genre = str(song.get("genre", "")).lower().strip()
    song_mood = str(song.get("mood", "")).lower().strip()

    if genre_pref and song_genre == genre_pref:
        score += wg
        reasons.append(f"genre match (+{wg})")

    if mood_pref and song_mood == mood_pref:
        score += wm
        reasons.append(f"mood match (+{wm})")

    song_energy = float(song["energy"])
    energy_gap = abs(song_energy - target_energy)
    energy_points = we * (1.0 - energy_gap)
    score += energy_points
    reasons.append(f"energy closeness (+{energy_points:.2f}; gap={energy_gap:.2f})")

    acoustic = float(song["acousticness"])
    acoustic_target = 0.85 if likes_acoustic else 0.2
    acoustic_gap = abs(acoustic - acoustic_target)
    acoustic_points = wa * (1.0 - acoustic_gap)
    score += acoustic_points
    reasons.append(f"acoustic fit (+{acoustic_points:.2f}; target={acoustic_target:.2f})")

    return score, reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    ranking_mode: str = "genre_first",
) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort by score descending, return the top k results."""
    ranked: List[Tuple[Dict, float, str]] = []
    for song in songs:
        total, reasons = score_song(user_prefs, song, ranking_mode=ranking_mode)
        explanation = "; ".join(reasons)
        ranked.append((song, total, explanation))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked[:k]
