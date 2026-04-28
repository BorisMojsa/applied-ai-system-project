# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeRank CLI 1.0** — a tiny, transparent content-based recommender for a classroom catalog.

---

## 2. Intended Use  

This system suggests up to five songs from a fixed CSV based on a dictionary of preferences (favorite genre, mood, target energy, and whether the listener likes acoustic textures). It is for learning and demonstration only. It is not for real users, not personalized from streaming history, and not a measure of song quality.

---

## 3. How the Model Works  

The recommender is **content-based**: each song is judged only from its own attributes in the file, not from what other listeners clicked. It adds points when the user’s genre and mood strings exactly match the song’s genre and mood (case-insensitive). It adds extra points when the song’s **energy** is numerically close to the user’s target energy, using “closer is better” rather than “higher is always better.” A smaller **acoustic fit** term nudges songs toward high acousticness when `likes_acoustic` is true, and toward lower acousticness when it is false. Every song gets a numeric score; the **ranking rule** is simply “sort scores from high to low and take the top k.”

---

## 4. Data  

The catalog is **18 songs** in `data/songs.csv` (starter 10 plus eight added rows). Features include `genre`, `mood`, `energy` (0–1), `tempo_bpm`, `valence`, `danceability`, and `acousticness`. Genres include pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip hop, classical, metal, country, folk, electronic, blues, and reggae. Moods include happy, chill, intense, relaxed, focused, moody, confident, reflective, aggressive, nostalgic, melancholic, euphoric, and soulful. The set is still tiny and creator-chosen, so it cannot represent global music culture.

---

## 5. Strengths  

The scoring is easy to read: each recommendation lists the exact reasons that fired. It separates **intense rock** from **chill lofi** cleanly when genre and mood both match, because those matches add the largest discrete chunks of points. For a default **pop / happy / high energy** profile, bright pop tracks with matching mood rank first, which matches everyday intuition about “same vibe.”

---

## 6. Limitations and Bias  

Because **genre match is worth more than mood match**, a user who only matches genre can still see very “wrong mood” songs high on the list if energy and acoustic terms align—especially when the dataset has no rows for **a** requested mood like `sad`. **Gym Hero** can stay near the top for high-energy pop-ish queries even when a listener wanted lyrical sadness, because the CSV cannot represent emotions the model never sees. The catalog is small, so **any single row** (for example the only metal track) can dominate a niche profile regardless of diversity. These effects are classic **filter bubble** risks: the system can only recommend what exists, and weights decide which corners of the catalog get exaggerated.

---

## 7. Evaluation  

Profiles tested in the CLI bundle include **High-Energy Pop**, **Chill Lofi**, **Deep Intense Rock**, and two **adversarial** mixes (very high energy with a mood that barely exists in the data, and metal with relaxed mood plus acoustic taste). I compared rankings to my own intuition and watched how ties broke through energy and acoustic gaps. I also ran a **weight experiment**: with `RECOMMENDER_EXPERIMENT=1`, genre weight halves and energy similarity doubles; top pop picks stayed similar but ordering tightened around energy, showing the system is **sensitive** to those knobs. For stretch, I compared **`--mode genre_first`** vs **`--mode mood_first`** on the same profiles (tables in the terminal): mood-first bumps *Rooftop Lights* above *Gym Hero* for the high-energy pop profile because it rewards the happy mood match more strongly than the pure-pop genre gate. Pairwise commentary lives in `reflection.md`.

---

## 8. Future Work  

Add **collaborative** signals (synthetic play counts) or a second mode that balances **diversity** (penalize repeated artists in the top k). Incorporate **tempo bands** or **valence** with the same “distance to target” rule. Build a tiny **evaluation harness** that asserts expected top-1 rows for frozen CSV snapshots.

---

## 9. Personal Reflection  

The biggest learning moment was seeing how a handful of weighted rules already produces convincing “because” explanations—**ranking** is really just repeated **scoring** plus sorting. AI tools sped up boilerplate (CSV typing, sorting patterns), but I still had to sanity-check weights against edge profiles so the story stayed honest. What surprised me is how quickly **missing labels** (like no `sad` mood) turn into silent bias: the math keeps working, but the user’s intent is not in the file. If I extended the project, I would log per-feature contributions across the whole top k to catch when one feature silently steers everything.

---

## 10. Stretch features (bonus rubric)

**Multiple ranking modes.** The CLI supports `--mode genre_first` (default: genre and mood weights match the main recipe) and `--mode mood_first`, which lowers the genre-match weight slightly and doubles the mood-match weight before the same energy and acoustic terms run. That is a small **strategy-style** switch: `score_weights(ranking_mode)` in `src/recommender.py` centralizes the numbers so `score_song` and `recommend_songs` stay in sync. You pick the mode in `main.py` via the flag; the `Recommender` class also accepts `ranking_mode` for tests. **Mood-first** can reorder near-ties when a listener cares more about vibe labels than strict genre boxes.

**Tabulate summary table.** `src/main.py` prints each profile’s top picks as a **GitHub-flavored Markdown table** using the `tabulate` library, with columns for title, artist, genre, mood, score, and wrapped **Reasons** so the scoring logic is visible at a glance. That improves transparency compared to a loose bullet list, especially when reasons are long.
