---
title: Playlist Vibe Guide
source: internal
---

# Playlist Vibe Guide (toy knowledge base)

This file is intentionally small and human-written. The recommender uses it as a **retrieval source**
to map a free-text “vibe” request into the app’s **canonical** fields:

- `genre`: one of the genres present in `data/songs.csv`
- `mood`: one of the moods present in `data/songs.csv`
- `energy`: a number in `[0, 1]` (higher means more intense / workout-friendly)

## Mood cheat sheet (canonical moods + synonyms)

Use these synonyms as hints. If a user asks for something close, pick the canonical mood shown.

- happy: upbeat, cheerful, sunny, bright, joyful
- chill: relaxed, calm, mellow, laid-back, cozy
- intense: aggressive, hard, hype, adrenaline, heavy
- sad: melancholy, blue, heartbreak, somber
- relaxed: easygoing, slow, unwind, soft

## Genre cheat sheet (canonical genres + synonyms)

- pop: catchy, chart, radio, dance-pop, synth-pop
- rock: guitars, band, anthemic, alt-rock
- lofi: study beats, lo-fi, background beats, chillhop
- metal: heavy, screaming, distorted guitars, thrash
- edm: electronic, club, festival, rave

## Energy guidance

- energy ~0.2–0.4: calm / background / study
- energy ~0.5–0.7: mid-tempo / groove
- energy ~0.8–1.0: workout / hype / intense

