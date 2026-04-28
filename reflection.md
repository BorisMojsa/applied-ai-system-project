# Profile comparison notes

Plain-language comparisons between pairs of profiles (same recommender, different inputs).

- **A vs B (High-Energy Pop vs Chill Lofi):** Pop/happy/high energy pushes bright, uptempo tracks like *Sunrise City* to the top, while lofi/chill favors *Library Rain* and *Midnight Coding* because both genre and mood match first; energy similarity then separates similar lofi rows. The change makes sense because the first two weights only fire when the CSV row’s labels match the user’s.

- **A vs C (Pop vs Rock):** Both profiles demand high energy, but genre and mood gates send *Sunrise City* to #1 for A and *Storm Runner* for C. *Gym Hero* appears for both as a “near miss” (shared mood or energy) because intense pop still overlaps the energy target.

- **A vs D (Pop/Happy vs Pop/Sad adversarial):** With the same favorite genre, D loses the mood bonus, so the list is driven by genre plus raw energy fit. *Gym Hero* can beat *Sunrise City* for D when the user’s target energy is extremely high, which shows how a missing mood match stops “happy pop” from automatically winning even inside pop.

- **A vs E (Pop vs Metal/Relaxed):** Completely different top songs: A rewards pop/happy alignment; E rewards the only metal row first (*Furnace Heart*) even though its vibe is aggressive, then relaxed-but-not-metal tracks pick up mood points. That is a good sanity check that the catalog’s rarity (one metal song) can dominate a niche profile.

- **B vs C (Lofi vs Rock):** No shared winner: chill/acoustic-leaning targets surface lofi and ambient, while intense rock surfaces *Storm Runner*. If the same song appeared at the top for both, we would worry the weights were ignoring genre; here they do not.

- **B vs D (Lofi vs Adversarial Pop/Sad):** B’s list is almost all lofi or neighbor genres with chill moods; D’s list is dominated by high-energy pop despite “sad” mood never matching the CSV (there is no `sad` mood label), so the model cannot reward sadness explicitly—it mostly shows energy and genre carry the score.

- **C vs E (Rock/Intense vs Metal/Relaxed):** C gets a perfect rock/intense match first. E’s relaxed mood pulls *Coffee Shop Stories* and *Samba Sketch* upward even though the user asked for metal first—so when mood and acoustic taste align strongly, they can compete with a lone genre match that has weaker energy/acoustic fit.

- **D vs E (two adversarial profiles):** D is “missing mood in the data” (no sad songs), so results are energy-heavy within pop or nearby intensity. E combines a rare genre with a common mood, producing a metal-first list then relaxed non-metal tracks; the contrast shows how dataset coverage shapes what looks like “intelligence.”

- **B vs E:** B stays in low-energy acoustic space; E starts with aggressive metal then relaxes into jazz/reggae. The outputs differ mainly because genre and mood bonuses are disjoint, which is what we want from a simple linear score.

- **C vs D:** C rewards coherent rock/intense rows; D rewards whatever pop row best matches extreme energy—again illustrating that mood only matters when the CSV supports it.
