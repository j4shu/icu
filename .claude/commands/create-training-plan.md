---
description: Build a periodized training plan from now until the next race, based on recent data.
argument-hint: "[history-days=42]"
allowed-tools: Bash(uv run python triclops.py:*), Bash(date:*), Read, Write, Glob
---

Build a training plan to follow from today until the athlete's next race. Arguments (`$ARGUMENTS`) may give how many days of history to consider — if none is given, use 42 (long enough to judge periodization).

1. Fetch the data: run `uv run python triclops.py summary --days <N>` and `uv run python triclops.py athlete`, and read both (use the **fetch-training-data** skill; see `schema.md`).
2. Identify the target race: the next **non-completed** event, preferring `RACE_A` then `RACE_B`. Get the race distances from the event's `description`. If there's no upcoming race, ask the athlete for the race date and distances.
3. Assess the starting point: current CTL (fitness), recent TSB (freshness/fatigue), and weekly volume by sport. Note FTP, threshold pace, and HR zones from recent activities.
4. **Aim for every week to include the following fixed set of sessions:**
   - **2 key/hard sessions** for bike and run each week. For bikes, this could be sweet spot/threshold intervals, vo2 max intervals, etc. For runs, this could be tempo runs, hill repeats, intervals, etc. It can also be a brick session that combines bike and run.
   - **1 strength session.**
   - **2 swim sessions.**
   - **1 rest day.**
   - Fill the remaining time with **long bikes or runs at Z2**.
   - Depending on which training phase we're in, the number of each session are allowed to vary. For example, in a base phase, there may be fewer key sessions and more Z2 volume; in a peak phase, there may be more key sessions and less Z2 volume.
5. Periodize **across** weeks, not within them: scale the intensity/duration of the key sessions and the volume of the Z2 long sessions through base → build → peak → taper, and scale the taper to the race priority and distance. Keep the weekly session _counts_ above constant; vary the _content_. Respect the athlete's recent training rhythm and any constraints in `$ARGUMENTS`.
6. **Output format — by week, NOT by day.** For each week, list the target workouts as a bulleted/numbered set (do **not** assign them to specific weekdays), so the athlete can arrange the week around how they feel and their schedule while still hitting the key sessions. For each workout:
   - Label it clearly (e.g. `🔴 KEY — Bike: 3x8min Sweet Spot`, `Swim (technique)`, `Long Run — Z2`).
   - Have the key sessions at the top of the list, followed by the rest.
   - Give the prescription using the workout-prescription shorthand from `CLAUDE.md` (WU/CD, reps, paces/powers/HR, totals).
     Include a one-line **goal** for the week and a short **rationale** (target CTL/TSB, periodization intent).
7. Run `date "+%Y-%m-%d-%H%M"` (e.g. `2026-05-31-0925`) and write the plan to `training-plans/<that-timestamp>-<race-slug>-training-plan.md` (use dashes in the race slug). Do **not** overwrite or modify any existing files.

After writing, summarize the plan's structure (weeks, phase progression, taper) in chat and report the file path.
