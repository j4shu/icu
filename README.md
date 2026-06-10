# triclops

An AI triathlon coach you talk to through
[Claude Code](https://claude.com/claude-code), backed by your
[Intervals.icu](https://intervals.icu) data.

_One eye on your swim. One on your bike. One on your run._

There's no web server and no separate LLM API call — triclops is just a coach
persona plus a few slash commands that live in this repo. Claude Code _is_ the
coach: it pulls your live training data from Intervals.icu and responds as an
expert triathlon coach.

## How it works

- **`CLAUDE.md`** — the always-on coach persona, data conventions, and workout
  notation. Loaded into every Claude Code session in this repo.
- **`triclops.py`** — a small CLI that fetches your Intervals.icu data
  (wellness, activities, races) and prints it as JSON.
- **`.claude/skills/fetch-training-data/`** — a skill that teaches Claude how to
  call the CLI and read the data, so any coaching question is grounded in real
  numbers.
- **`.claude/commands/`** — the slash commands you run for specific tasks.

The Python data layer (`intervals_client.py`, `helpers.py`) only ever _reads_
from Intervals.icu — nothing is written back to your account.

## Setup

Requires Python 3.14+, [uv](https://docs.astral.sh/uv/), and
[Claude Code](https://claude.com/claude-code).

```sh
uv sync
```

### Environment variable

Copy the example and fill in your INTERVALS_API_KEY key:

```sh
cp .env.example .env
```

| Variable            | Description                                  |
| ------------------- | -------------------------------------------- |
| `INTERVALS_API_KEY` | Intervals.icu API key (Settings > Developer) |

### Athlete profile

Copy the example and fill in your details (weight, age, etc. — used for training
reasoning):

```sh
cp .athlete.example .athlete
```

## Use

Open this folder in Claude Code and run a command:

| Command                 | What it does                                                        |
| ----------------------- | ------------------------------------------------------------------- |
| `/analyze-training`     | Analyze recent data against your current plan and flag adjustments. |
| `/create-training-plan` | Build a periodized plan from now until your next race.              |
| `/race-nutrition`       | Build a race-week and race-day nutrition & hydration plan.          |

You can also just **talk to Claude** — ask any coaching question (e.g. "am I
recovered enough to race this weekend?") and it pulls your data automatically
via the `fetch-training-data` skill.

### Output

Each command saves its result as a dated markdown file (named with the date and
time, e.g. `2026-05-31-0925`):

| Artifact          | Location             |
| ----------------- | -------------------- |
| Training plans    | `training-plans/`    |
| Training analyses | `training-analyses/` |
| Nutrition guides  | `nutrition/`         |

## Inspecting the data

To see the raw data Claude works with:

```sh
uv run python triclops.py summary --days 42    # wellness + activities + events
uv run python triclops.py events               # upcoming/recent races only
uv run python triclops.py athlete              # athlete profile
```

Pass `--force` to `summary` to bypass the cache and re-fetch. Data is cached in
`.cache/` (everything except today), and commands default to a 42-day window of
activity and wellness data plus races within ~6 months.

## Repo layout

```
CLAUDE.md                 # coach persona + conventions (always loaded)
triclops.py               # data CLI (summary / events / athlete)
intervals_client.py       # Intervals.icu data fetching + caching
helpers.py                # API client + unit conversions
.claude/
  settings.json           # pre-approves the data CLI so sessions run without prompts
  skills/
    fetch-training-data/  # how to fetch + the data schema reference
  commands/               # /analyze-training, /create-training-plan, /race-nutrition
```
