---
name: fetch-training-data
description: Fetch the athlete's Intervals.icu training data (wellness, activities, races) as JSON. Use whenever you need recent training metrics, fitness/fatigue trends, completed workouts, or upcoming race info to answer a coaching question.
allowed-tools: Bash(uv run python triclops.py:*)
---

# Fetch training data

The athlete's data lives in Intervals.icu. Pull it with the `triclops.py` CLI and read the JSON it prints to stdout.

## Commands

```sh
uv run python triclops.py summary --days 42   # wellness + activities + events, newest date first
uv run python triclops.py summary --days 90 --force   # re-fetch, bypassing cache
uv run python triclops.py events               # races only (next/recent ~6 months)
uv run python triclops.py athlete              # athlete profile (name, sex, weight, age, height)
```

`summary` returns `{ "past_days": N, "dates": { "YYYY-MM-DD": { wellness, activities } }, "events": [...] }`. See [schema.md](schema.md) for every field and its (already-converted) units.

## Choosing a window

- **7 days** — acute check-in: "am I recovered?", "how was this week?"
- **42 days** — default. Enough to see CTL/ATL/TSB trend and weekly rhythm.
- **90–180 days** — periodization, plan building, long-term progression.

## Cache & errors

- Everything except today is cached in `.cache/training_summary.json`. Use `--force` only when you suspect stale data (e.g. an activity was just edited on Intervals.icu).
- On failure the CLI prints `Error: ...` to stderr and exits non-zero. The usual cause is a missing `INTERVALS_API_KEY` (set it in `.env`) or a missing `.athlete` file (copy `.athlete.example`).
