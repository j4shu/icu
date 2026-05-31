# Training data schema

All values are **pre-converted to display-ready strings** by the CLI — do not convert again. Empty/zero/null fields are stripped before output, so a missing field simply means "no data for that metric."

## `summary` shape

```json
{
  "past_days": 42,
  "dates": {
    "2026-05-30": { "wellness": { ... }, "activities": [ { ... } ] }
  },
  "events": [ { ... } ]
}
```

`dates` is ordered newest-first. A date may have only `wellness`, only `activities`, or both.

## Wellness (per date)

| Field | Meaning |
| --- | --- |
| `ctl` | Chronic Training Load — fitness (rolling ~42d load). |
| `atl` | Acute Training Load — fatigue (rolling ~7d load). |
| `tsb` | Training Stress Balance = `ctl − atl` — form. Negative = fatigued/loading; positive = fresh/tapered. |
| `ramp_rate` | Rate of CTL change. High positive = ramping fast (injury/overtraining risk). |
| `resting_hr` | Resting heart rate (bpm). |
| `hrv` | Heart rate variability. |
| `sleep_hours` | Formatted `HhMMmSSs`. |
| `sleep_score` | 0–100. |

## Activities (per date, a list)

| Field | Meaning / unit |
| --- | --- |
| `type` | `Swim`, `OpenWaterSwim`, `Run`, `VirtualRun`, `Ride`, `VirtualRide`, etc. |
| `name` | Activity title. |
| `race` | `true` if a race effort (no interval breakdown is fetched for races). |
| `duration` | Moving time, `HhMMmSSs`. |
| `distance` | Already in `mi` (run/bike) or `yd` (swim). |
| `elevation_gain` | `ft`. |
| `training_load` | Intervals.icu load score for the session. |
| `intensity` | % of threshold. |
| `average_heartrate` / `max_heartrate` | bpm. |
| `hr_zones` | 7 zone-boundary bpm values. |
| `lthr` | Lactate threshold HR (bpm). |
| `average_watts` / `normalized_power` / `athlete_ftp` | Cycling, watts. |
| `efficiency_factor` | Normalized power ÷ HR (aerobic efficiency). |
| `strain_score` | Session strain. |
| `average_speed` | Pre-formatted per sport: `mph` (bike), `M:SS/mi` (run), `M:SS/100yd` (swim). |
| `grade_adjusted_speed` | Running GAP pace (`M:SS/mi`). |
| `average_cadence` | Strokes/steps/revs per min. |
| `average_temp` | `F`. |
| `interval_details` | Per-lap breakdown (non-races): `distance`, `duration`, `zone`, `average_speed`, `average_heartrate`, `average_watts` (bike), `type` (e.g. `WORK`/`RECOVERY`). |

## Events (races)

| Field | Meaning |
| --- | --- |
| `name` | Race name. |
| `date` | `YYYY-MM-DD`. |
| `category` | `RACE_A` / `RACE_B` / `RACE_C` — priority (A = peak goal race). |
| `type` | `Triathlon`, `Run`, `Swim`, etc. |
| `description` | Free text — usually contains race distances. |
| `completed` | Present and `true` only if the race date is today or earlier. Absent = upcoming. |

Events are sorted by date, newest first.
