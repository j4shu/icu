---
description: Build a periodized training plan from now until the next race, grounded in the athlete's current fitness and limiters.
argument-hint: "[days=42]"
allowed-tools: Bash(uv run python triclops.py:*), Bash(date:*), Read, Write, Glob
---

Build a periodized training plan the athlete follows from the closest upcoming Monday until their next race. `$ARGUMENTS` may give a history window in days: parse the first integer, clamp to `[14, 180]`, default `42` if absent/zero/negative; note any clamp in the chat summary. Ignore other text for windowing, but if it names a race, use it to disambiguate the target in step 2. Use only fields defined in the **fetch-training-data** skill `schema.md`; if a referenced field is missing for this athlete, fall back as described below — never assume a default or invent a value. Do **not** read any existing training plans under `training-plans/` as a template or reference.

**Workout shorthand**:

- `WU`/`CD` = warm-up/cool-down; `Z2` = easy aerobic; `SS` = sweet spot; `VO2` = VO2max. Intervals as `<reps>×<duration-or-distance> @ <target> w/ <recovery>` (e.g. `3×8min @ 175–185 W w/ 4min easy spin`, `5×800m @ 8:10–8:25/mi w/ 2min jog`).
- Targets from the athlete's own data: bike in **W** (and/or HR), run in **M:SS/mi** (and/or HR), swim in **M:SS/100yd** with rest. Degrade gracefully: power→HR→RPE 1–10 (bike), pace→HR→RPE (run). End each line with a rough **total** (`~60min`/`~4 mi`); mark estimates with `~`.

1. **Fetch data** via the **fetch-training-data** skill (values are already display-ready — do not convert): run `uv run python triclops.py summary --days <N>` and `uv run python triclops.py athlete`; read both. `summary` already includes the `events` array, so no separate `events` call is needed. If either errors or returns no `dates`, report the CLI's actual `Error: ...` (stderr) verbatim, stop, and do not fabricate data (common causes: missing `INTERVALS_API_KEY` in `.env`, or a missing `.athlete` file).

2. **Select the target race** from `events` (ignore `completed: true` events; absent `completed` = upcoming):
   - If `$ARGUMENTS` named a race, match it. Else pick the next uncompleted event by `date`, preferring `RACE_A` > `RACE_B` > `RACE_C`. Read distances and `type` from the event `description`/`type`.
   - **No upcoming race:** do not invent one — ask the athlete for race name, date, type, and distances, then continue.
   - **Single-sport race** (`type` Run/Swim/Bike): build KEY sessions and Race Day around that sport only; demote the other disciplines to optional cross-training/maintenance (no brick, no mandated swims).
   - If distances are unclear, infer from `type`/`name` and **state the assumption**; if you truly cannot tell, ask.

3. **Compute runway and phase shape.** Get today's date with `date "+%Y-%m-%d"` (never assume it). **Week 1 starts with the closest upcoming Monday on or after today's date**, number forward in 7-day blocks, final partial week is the taper/race week ending race day; let `W` = total weeks. If runway > 10 weeks and `N < 90`, re-run `summary --days 90` (up to 180) and re-read before periodizing — but an explicit user-supplied window always wins. Pick the shape and state it in one line:

   | Runway     | Shape                                                                                                           |
   | ---------- | --------------------------------------------------------------------------------------------------------------- |
   | ≤ 3 days   | Mini-taper + race day only (1–2 short openers, rest, pacing). No base/build.                                    |
   | 4–10 days  | Taper/sharpen only — short race-specific touches, cut volume, hold frequency, start no new load.                |
   | 11–28 days | Compressed Build → Peak → Taper.                                                                                |
   | 29–84 days | Full Base → Build → Peak → Taper.                                                                               |
   | > 84 days  | Detail the first ~10–12 weeks (Base + early Build); outline later phases; note to regenerate as the race nears. |

   The **taper** is always the final block, scaled to priority/distance (short-course → short, aggressive; long-course → longer, more Z2).

4. **Assess the starting point** (becomes the "Starting point" section), from real fields only:
   - **Fitness/fatigue:** latest `ctl`, `atl`, `tsb`, `ramp_rate`; note the CTL trend. **Rhythm:** weekly volume + session count by sport and the easy-vs-hard split. **Limiter:** the weakest discipline or shaping constraint, with the numbers behind it.
   - Adapt Week 1 — do not ask, just handle and note (these modify Week 1 regardless of which race step 2 selected):
     - **Just raced** (recent `race: true` activity or completed event) — recovery scales with that race's distance: sprint/super-sprint ≈ 2–3 easy/optional days then reintroduce quality as `tsb` recovers; Olympic ≈ 4–5 easy days first; half/full-distance ≈ 7–14+ days easy aerobic only, **no quality** even if `tsb` looks fine (soft-tissue/immune recovery lags CTL/TSB). Label the week "Reload."
     - **Deeply fatigued** (`tsb` strongly negative, high `ramp_rate`, rising `resting_hr` / falling `hrv`): cap the ramp, emphasize recovery, flag the red flag honestly.
     - **Detrained / sparse history** (very low `ctl` or large `activities` gaps): start conservative, ramp gradually, say early weeks are about consistency, suggest regenerating after 1–2 weeks of data.

5. **Set the periodization spine (data-driven, not a template).**
   - **CTL/TSB targeting:** build CTL through Base/Build, hold/peak it, let it dip in taper as TSB rises. Give each week a target CTL direction + end-of-week TSB. Scale KEY intensity/duration and long-Z2 volume up Base→Build→Peak, then cut hard in Taper. **Short-course:** raise intensity toward VO2/race-pace into Peak. **Long-course:** hold intensity at tempo/SS and raise sustained DURATION/race-pace specificity into Peak, not peak intensity.
   - **Race-morning TSB target** (anchored to actual current `ctl`/`tsb` so the dip is realistic): sprint/super-sprint A ≈ +5 to +12; Olympic ≈ +10 to +18; half/full-distance ≈ +15 to +25; smaller for B/C.
   - **Ramp safety:** cap week-to-week load growth ~5–8%; if already ramping fast or `tsb` is deeply negative / `hrv` suppressed, open with a recovery/reload week — never spike volume to catch up.
   - **Recovery weeks:** in blocks of ~4+ build weeks, drop volume ~30–40% every 3rd–4th week. In compressed (11–28 day) or taper-only runways, skip the down week — the taper provides the absorption.

6. **Establish reference paces & powers** (becomes the "Reference paces & powers" block), using only the athlete's own benchmarks. For each sport, anchor on the most recent hard/threshold or race effort in the window (state which activity/date); if none, use the best recent steady effort.
   - **Bike** (anchor `athlete_ftp` / recent `normalized_power`): Z2 ≈ 56–75%, Tempo ≈ 76–87%, SS ≈ 88–94%, Threshold ≈ 95–105%, VO2 ≈ 106–120% FTP.
   - **Run** (anchor a recent tempo/threshold workout `average_speed`/`grade_adjusted_speed` + `lthr`/`hr_zones`): give Easy/Z2, Tempo, Threshold/5K, VO2 paces with HR ranges. When only a race `average_speed` is available it is activity-level (races have no interval splits) and depends on distance — a standalone 5K ≈ threshold; longer races run progressively slower, so do not treat their average as threshold pace. State which effort you anchored on.
   - **Swim** (anchor recent swim `average_speed`, M:SS/100yd): threshold + easy pace.
   - **Missing benchmarks:** never invent a number. No FTP → prescribe bike by HR/RPE. No run threshold → derive from recent `average_speed` + `lthr`/`hr_zones`, else RPE. No HR zones → RPE + pace. No swim threshold → estimate from recent swim `average_speed`, else by feel. Mark estimates with `~`, state the assumption, and recommend an early benchmark test (e.g. 20-min FTP or run threshold effort).

7. **Set the weekly session framework for Base/Build/Peak**, then vary content by phase (keep counts stable; vary content):
   - **2 KEY sessions** — one bike-quality (SS/threshold/VO2) and one run-quality (tempo/hill/interval/race-pace). A **brick** workout also satisfies as one of the KEY sessions.
     - Can include an optional/additional quality session with a skip condition depending on the phase.
   - **2 swims** (technique/aerobic in base, race-pace nearer the race).
   - **1 strength** (full-body, ≥48h from any KEY/quality or long-Z2 day; in Build/Peak bias to lower load or place it after a quality day, not before; light/activation in taper).
   - **1 full rest day.**
   - Fill remaining time with **long Z2 bike/run.**
   - **By phase:** Base = sub-max keys, more Z2; Build = keys at threshold, hold Z2; Peak = optional 2nd bike-quality or race-pace brick, trim Z2; Taper = cut volume ~40–55%, keep frequency + short snappy intensity.
   - **Override:** Recovery/Reload and deep-taper weeks override this frame — at most one short quality touch (zero in true post-long-course recovery), easy frequency only. Never prescribe more sessions/sport than the athlete has recently sustained; scale down and note it.

8. **Write the file with these sections in this exact order** (the proven house format — by week, NOT by day):
   - **Title + header:** `# Training Plan: <Race Name> on <YYYY-MM-DD>` (no real race → `# Training Plan: Base/Build Block (no scheduled race)`), then athlete (name, age/sex, weight from `athlete`), race (type + distances), plan window (closest upcoming Monday → race, `W` weeks), priority.
   - **`## Starting point (as of <closest upcoming Monday>)`** — fitness/fatigue (CTL/ATL/TSB), context (incl. just-raced / fatigue notes), benchmarks (mark missing/estimated), and the primary limiter.
   - **`## Reference paces & powers`** — bike / run / swim blocks from step 6.
   - **One `## Week N: <Phase label> (<date range>)` per week:** a one-line **Goal**, a short **Rationale** (target CTL/TSB, intent), then a **numbered** workout list (not bound to weekdays), **KEY sessions first**, each labeled (`🔴 KEY — Bike: SS 3×8`, `🟠` for optional/additional quality with a skip condition, `Swim (technique)`, `Long Run — Z2`, `Rest day`) and prescribed with the shorthand above.
   - **`### 🏁 Race Day — <weekday, date>`** (when a real race exists) — warm-up, then per-discipline pacing in race order (swim → bike → run for a tri, or the single sport) using the reference paces — concrete targets, not platitudes.
   - **`### Weekly structure at a glance`** — table (`Week | Phase | Key bike | Key run | Strength | Swim | Long Z2 | Rest`) plus a one-paragraph **Periodization** note on how intensity rises and volume tapers.
   - **Runways < 1 week:** replace the per-week sections and the at-a-glance table with a single day-by-day countdown to race day; Starting point, Reference paces & powers, and Race Day still apply.

9. **Name and write.** Run `date "+%Y-%m-%d-%H%M"`; the path is `training-plans/<that-timestamp>-training-plan.md`. Never overwrite or modify an existing file.

10. **Summarize in chat** (plain text — no emojis): target race and runway, phase progression, CTL/TSB trajectory and race-morning TSB target, taper length, any edge cases handled or assumptions/estimates made, any argument clamp, and the absolute file path.
