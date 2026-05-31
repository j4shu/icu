---
description: Build a race-week and race-day nutrition & hydration plan for the next race.
argument-hint: "[race-name]"
allowed-tools: Bash(uv run python triclops.py:*), Bash(date:*), Read, Write, Glob
---

Build a nutrition and hydration plan for a race. Arguments (`$ARGUMENTS`) may name a specific race; if none is given, use the next uncompleted race.

1. Fetch the data: run `uv run python triclops.py events` and `uv run python triclops.py athlete`, and read both (use the **fetch-training-data** skill).
2. Pick the race: match `$ARGUMENTS` against event names, or default to the next uncompleted event. Get the distances from its `description`. If unclear, ask.
3. Estimate the demand: use the race distances, the athlete's `weight` (for carb g/hr and fluid ml/hr targets), and an estimated finish time per discipline.
4. Produce a plan with three phases:
   - **Race week / morning** — carb loading, the pre-race meal, and timing.
   - **During the race** — per-discipline fueling and hydration across the swim → bike → run sequence, with concrete amounts and timing (e.g. g carbs/hr, ml fluid/hr, when to take gels).
   - **Recovery** — immediate post-race refueling.
5. Run `date "+%Y-%m-%d-%H%M"` (e.g. `2026-05-31-0925`) and write the plan to `nutrition/<that-timestamp>-nutrition.md`, then summarize the key targets in chat.
