---
description: Analyze recent training data against the plan and flag adjustments.
argument-hint: "[days=42]"
allowed-tools: Bash(uv run python triclops.py:*), Bash(date:*), Read, Write, Glob
---

Analyze the athlete's recent training. Arguments (`$ARGUMENTS`) may give a lookback window in days — if none is given, use 42.

1. Fetch the data: run `uv run python triclops.py summary --days <N>` and read the JSON (use the **fetch-training-data** skill; see its `schema.md` for field meanings).
2. Find the current plan: use Glob to locate the most recent file in `training-plans/`. If none exists, fall back to `training_plan.md`. Read it if found.
3. Analyze, as the coach:
   - CTL/ATL/TSB trend — is fitness building, holding, or decaying? Is the athlete fresh or buried?
   - Volume & intensity distribution by sport (swim/bike/run) over the window.
   - Recovery markers: HRV, resting HR, sleep, and ramp rate — any red flags?
   - If a plan exists, compare prescribed vs. actual and call out adherence gaps.
4. Give **concrete, numbers-and-dates-specific** adjustments. Be honest about overtraining or insufficient volume.
5. Run `date "+%Y-%m-%d-%H%M"` (e.g. `2026-05-31-0925`) and write the file to `training-analyses/<that-timestamp>.md`.
