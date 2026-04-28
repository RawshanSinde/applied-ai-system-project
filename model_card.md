# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**

---

## 2. Intended Use

VibeMatch 1.0 generates a ranked list of up to five song recommendations from a small 20-song catalog, based on how closely each song's audio features match a user's stated taste profile. It is built for classroom exploration — not for real users or production use.

The system assumes the user can describe their preferences numerically: they need to know roughly how energetic, danceable, or acoustically warm they want a song to feel, and they need to pick a target genre and mood from a fixed set of labels. It does not learn from listening history or adapt over time. Every recommendation is based entirely on the single profile the user provides at run time, so it works best when that profile is specific and the catalog contains songs close to those preferences.

---

## 3. How the Model Works

Every song in the catalog is described by eight pieces of information: its genre (like pop or rock), its mood (like chill or intense), and six numbers between 0 and 1 that describe how it sounds — energy, danceability, valence (how happy or dark it feels), acousticness (how organic vs. electronic it sounds), and a normalized tempo derived from its BPM.

The user provides a matching set of preferences: a target genre, a target mood, and their own ideal value for each of the six numbers. They also assign a weight to each feature — a way of saying "energy matters more to me than acousticness." Higher weight means that feature has more influence on the final score.

To score a song, the model goes through each feature and asks: how close is this song to what the user wants? For numbers like energy or danceability, closeness is measured as a simple gap — a song that is 0.05 away from the target scores nearly perfect, while one that is 0.50 away scores much lower. For genre and mood, it is all or nothing: exact match gets full credit, anything else gets zero, regardless of how similar the labels might sound. Each feature's closeness score is then multiplied by its weight, and all the weighted scores are added together to produce a final number between 0 and 1. Songs are ranked from highest to lowest and the top five are returned.

The main change from the starter logic was replacing a single generic profile with seven distinct user profiles — three realistic taste profiles and four adversarial ones designed to expose edge cases — and adding a per-feature explanation to the output so each recommendation shows exactly which features helped or hurt its score.

---

## 4. Data

The catalog contains 20 songs stored in `data/songs.csv`. No songs were added or removed from the original dataset.

Twelve distinct genres are represented, but coverage is uneven. Pop, lofi, and r&b each have three songs. Dance pop and indie pop have two each. Rock, jazz, ambient, synthwave, electropop, classic rock, and afrobeats each have exactly one. On the mood side, the catalog covers dreamy, chill, and happy with two or three songs each, and has single entries for focused, relaxed, nostalgic, euphoric, and romantic.

Large portions of musical taste are missing entirely. There are no hip-hop, country, classical, metal, Latin, or K-pop songs. The energy range runs from 0.28 to 0.93 — nothing exists below 0.28, so very quiet or meditative music has no representation. Valence (the happiness-to-darkness scale) bottoms out at 0.48, meaning there are no genuinely dark or melancholic songs in the catalog despite those being common listener preferences. The dataset also skews toward music that is moderately to highly danceable; only a handful of songs fall below 0.55 on danceability.

---

## 5. Strengths

The system works best for users whose preferences align with the most-represented part of the catalog — upbeat, danceable, produced pop and r&b. The High-Energy Pop profile produced results that matched musical intuition closely: Can't Tame Her ranked first because it was a near-perfect match on every feature, and Espresso ranked second for the right reasons (identical energy and acousticness, same confident mood) even though it was docked for a genre label difference. A human would make the same call.

The weighted scoring approach correctly captures that different users care about different things. When the energy weight was doubled and the genre weight halved in the experimental profile, Espresso's score rose from 0.84 to 0.93 — reflecting that it genuinely is closer to the target on audio feel than the genre label alone suggested. The system responded to that weight change in a predictable and musically sensible direction, which shows the underlying logic is sound even when individual weights are imperfect.

The per-feature explanation is also a genuine strength. Because every recommendation shows exactly which features matched and which didn't — and by how much — it is easy to audit why a song ranked where it did. That transparency makes it straightforward to identify when the system is working correctly versus when a ranking is being driven by a quirk in the weights or catalog coverage.

---

## 6. Limitations and Bias

The system ignores tempo entirely: even though a user can set a preferred BPM in their profile and it appears in the "Why" output, the tempo weight is hardcoded to zero in the scoring logic, meaning it never actually affects which songs are recommended — a runner who needs 140 BPM gets the exact same results as someone who wants 70 BPM. Genres with only one song in the catalog — rock, jazz, ambient, synthwave, and afrobeats — create a filter bubble where those users always receive the same song at the top with no variety possible, while pop, lofi, and r&b users (three songs each) benefit from a small but real pool of options. The scoring also unintentionally favors users whose preferences land in the middle of the catalog's energy range (roughly 0.60–0.85), because songs in that band accumulate partial credit across many profiles and float into nearly every top-five list regardless of what the user actually asked for — a quiet ambient listener targeting energy 0.10 sees Spacewalk Thoughts scored at 82% match, which looks acceptable but is actually the best the system can do given that nothing in the catalog comes close. Finally, the binary exact-match rule for mood and genre means that stylistically adjacent labels — like "euphoric" and "confident," or "electropop" and "dance pop" — are penalized as heavily as completely unrelated ones, so a song that is 95% the right feel but carries a slightly different tag is treated the same as a song from an entirely different genre.

---

## 7. Evaluation

Seven profiles were run in total: three realistic taste profiles (High-Energy Pop, Chill Lofi, Deep Intense Rock) and four adversarial profiles designed to break the scoring logic (a mood that doesn't exist in the catalog, a phantom genre and mood, inflated weights that sum to 1.80, and an energy value of 1.5 that sits outside the valid 0–1 scale). For each run we looked at whether the top results matched the stated preferences, whether the scores were in the expected 0–1 range, and whether the "Why" explanation actually justified the ranking.

The most surprising result from the normal profiles was that Midnight Sun by Zara Larsson — a dance pop track nearly identical to Can't Tame Her — ranked third instead of second, losing 0.20 points solely because its mood tag is "euphoric" rather than "confident." To a human listener those two songs are interchangeable in feel, but the scorer treats the label difference as a total mismatch. A close second surprise was Secondhand (feat. Rema), an afrobeats track, appearing at #4 in the dance pop results purely because its energy and danceability numbers happened to land close to the target — the system had no way to penalize stylistic distance between afrobeats and dance pop beyond the genre label.

From the adversarial runs, the inflated-weights profile produced scores above 1.00 with no error, confirming that the scorer never validates its own output range. The out-of-range energy profile (1.5) produced negative score contributions for low-energy songs, also silently. The most instructive comparison was between the normal High-Energy Pop profile and its weight-shifted variant (energy doubled, genre halved): the ranking order stayed the same, but Espresso jumped from 0.84 to 0.93, closing the gap with Can't Tame Her — which confirmed that the original 0.15 genre penalty was the main reason Espresso scored lower despite being an almost perfect audio match. That single weight change made the results feel more musically accurate without changing the logic at all.

---

## 8. Future Work

The single most impactful fix would be activating tempo as a real scoring feature — right now the weight is hardcoded to zero, so it appears in the output but changes nothing. Giving users meaningful control over tempo would make the system genuinely useful for context-driven listening like workouts or studying.

The categorical scoring is the deepest structural problem. Replacing the binary exact-match check with a similarity lookup — so that "euphoric" and "confident" score closer to each other than "euphoric" and "focused" do — would immediately close the gap between songs that feel similar but carry different labels. This would also fix the Espresso / dance pop penalty without needing to manually tune weights.

For diversity, the system currently returns the five closest numerical matches, which means users with a popular taste profile always see the same two or three songs at the top with no variation. A re-ranking step that penalizes the second song for being too similar to the first — and the third for being too similar to either — would spread results across more of the catalog and surface songs the user might not have considered.

Longer term, the most meaningful improvement would be expanding the catalog. Many listener types — fans of hip-hop, classical, metal, Latin, or very quiet ambient music — have no good matches available regardless of how well the scoring logic works. A better catalog would also close the valence and energy gaps at the extremes, so users who want genuinely dark or extremely calm music get real options rather than the system's best approximation.

---

## 9. Personal Reflection

Building this made it clear that a recommender system is only as good as the assumptions baked into its design, and those assumptions are easy to miss until you stress-test them. The most surprising moment was running the adversarial "sad mood, high energy" profile and watching the system confidently recommend Gym Hero — a pump-up gym anthem — with a score of 0.67 out of 1.00 and no indication that anything had gone wrong. There was no warning, no low-confidence flag, nothing. The output looked exactly like a normal result. That experience made the concept of silent failure feel very real: a system can be technically functioning, printing clean scores and explanations, while recommending something completely at odds with what the user wanted.

It also changed how I think about Spotify or YouTube recommendations in everyday use. Those systems feel intuitive and personal, but underneath they are doing a version of the same thing — comparing your behavior and preferences against a catalog of features, using weights that someone decided on, with gaps in coverage that reflect whoever built the dataset. When Spotify keeps pushing a certain genre, or YouTube can't seem to surface anything outside a narrow band of content, it is probably not because the algorithm misunderstood you. It is more likely that the catalog skews a certain way, or the weights were tuned for the average user, or some feature that would matter to you specifically just isn't being measured. This project made that process visible in a way that was hard to unsee.

---

## 10. AI Collaboration

This project was built in collaboration with Claude (Anthropic) as an AI coding assistant throughout Modules 1–4 — writing and refactoring code, generating documentation, designing the test suite, and building the system diagram.

**One instance where the AI gave a genuinely helpful suggestion:**
When asked to prove the system's reliability, Claude proposed adding a `confidence_label()` function that translates the 0–1 match score into a human-readable tier (High / Medium / Low) surfaced directly in the CLI output. This was more useful than the raw score alone because it gives any reader — technical or not — an immediate signal about whether to trust a result. A Low confidence label on a Deep Rock recommendation correctly communicates that the catalog may not cover that taste well, which the score number alone doesn't convey as clearly. It also created a small, independently testable function with its own unit tests.

**One instance where the AI's suggestion was flawed:**
In the README's Sample Interactions section, Claude wrote "realistic" example outputs showing what GPT-3.5-turbo would say for each profile. Those outputs were invented — generated by Claude to illustrate what the system *might* produce, not from actually running the code with a live API key. They are plausible but fabricated, meaning someone who clones the repo will see different outputs from the real OpenAI API. Writing documentation about AI output without running the AI is itself a form of the silent-confidence problem the project documents elsewhere: the result looked authoritative but wasn't grounded in actual retrieval. The correct version of that section would be captured from a real terminal run.
