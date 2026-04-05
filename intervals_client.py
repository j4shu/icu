from os import environ
import time
import requests
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth


BASE_URL = "https://intervals.icu/api/v1"


def _strip_empty(o):
    if isinstance(o, dict):
        return {
            k: _strip_empty(v)
            for k, v in o.items()
            # filter out null, boolean, and zero values
            if v is not None and not isinstance(v, bool) and not v == 0.0
        }
    if isinstance(o, list):
        return [_strip_empty(i) for i in o]
    return o


def seconds_to_hhmmss(s):
    h, rem = divmod(int(s), 3600)
    m, sec = divmod(rem, 60)
    return f"{h}h{m:02d}m{sec:02d}s"


def _meters_to_miles(m):
    return f"{round(m * 0.000621371, 2)}mi"


def _meters_to_yards(m):
    yards = m * 1.09361
    rounded = round(yards / 25) * 25
    return f"{rounded}yd"


def _mps_to_mph(mps):
    return f"{round(mps * 2.23694, 2)}mph"


def _mps_to_min_per_mile(mps):
    total_secs = 1609.34 / mps
    m, s = divmod(int(total_secs), 60)
    return f"{m}:{s:02d}/mi"


def _mps_to_min_per_100yds(mps):
    total_secs = (100 * 0.9144) / mps
    m, s = divmod(int(total_secs), 60)
    return f"{m}:{s:02d}/100yd"


def get_age(dob):
    birth_date = datetime.strptime(dob, "%Y-%m-%d").date()
    today = datetime.now().date()
    age = (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )
    return age


# "interval_summary": [
#     "2x 388m 138bpm",
#     "2x 45m 131bpm",
#     "6x 68m 140bpm",
#     "1x 274m 144bpm",
#     "1x 182m 143bpm",
#     "1x 91m 142bpm",
#     "1x 91m 143bpm"
# ],
def parse_interval_summary(summary):
    intervals = []
    for s in summary:
        parts = s.split()
        new_parts = []
        for p in parts:
            if p.endswith("m") and not p.endswith("bpm"):
                new_parts.append(_meters_to_yards(float(p[:-1])))
            else:
                new_parts.append(p)
        intervals.append(" ".join(new_parts))
    return intervals


# Simple TTL cache: { window: (timestamp, data) }
_cache = {}
CACHE_TTL = 3600  # 1 hour


def _auth():
    return HTTPBasicAuth("API_KEY", environ["INTERVALS_API_KEY"])


def _athlete_id():
    return environ["INTERVALS_ATHLETE_ID"]


def _date_range(window):
    today = datetime.now().date()
    windows = {
        "1d": 1,
        "4d": 4,
        "7d": 7,
        "1mo": 30,
        "42d": 42,
        "3mo": 90,
        "6mo": 180,
        "1y": 365,
    }
    days = windows.get(window, 42)
    oldest = today - timedelta(days=days)
    return oldest.isoformat(), today.isoformat()


def get_activities(window="42d", raw=False):
    oldest, newest = _date_range(window)
    url = f"{BASE_URL}/athlete/{_athlete_id()}/activities"
    resp = requests.get(
        url,
        params={"oldest": oldest, "newest": newest},
        auth=_auth(),
        timeout=30,
    )
    resp.raise_for_status()
    ret = resp.json()
    if raw:
        return ret
    ret = [
        {
            # Identity
            "date": a.get("start_date_local", "")[:10],
            "type": a.get("type"),
            "name": a.get("name"),
            # Duration & distance
            "duration": seconds_to_hhmmss(a.get("moving_time", a.get("elapsed_time"))),
            "distance": (
                _meters_to_yards(a.get("distance"))
                if a.get("type") == "Swim"
                else _meters_to_miles(a.get("distance", 0))
            ),
            # Training load & fitness
            "training_load": a.get("icu_training_load"),
            "intensity": a.get("icu_intensity"),
            "atl": a.get("icu_atl"),
            "ctl": a.get("icu_ctl"),
            "trimp": a.get("trimp"),
            "joules": a.get("joules"),
            # Heart rate
            "average_heartrate": a.get("average_heartrate"),
            "max_heartrate": a.get("max_heartrate"),
            "hr_zones": a.get("icu_hr_zones"),
            "lthr": a.get("lthr"),
            # Cycling-specific
            "average_watts": a.get("icu_average_watts"),
            "normalized_power": a.get("icu_weighted_avg_watts"),
            "athlete_ftp": a.get("icu_ftp"),
            "time_in_zones": a.get("icu_zone_times"),
            "decoupling": a.get("decoupling"),
            "efficiency_factor": a.get("icu_efficiency_factor"),
            "variability_index": a.get("icu_variability_index"),
            "polarization_index": a.get("polarization_index"),
            "strain_score": a.get("strain_score"),
            "power_hr_ratio": a.get("icu_power_hr"),
            # Pace & form
            "average_speed": (
                _mps_to_min_per_100yds(a.get("average_speed"))
                if a.get("type") == "Swim"
                else (
                    _mps_to_min_per_mile(a.get("average_speed"))
                    if a.get("type") == "Run"
                    else _mps_to_mph(a.get("average_speed", 0))
                )
            ),
            "average_cadence": a.get("average_cadence"),
            # Workout structure
            "interval_summary": (
                a.get("interval_summary")
                if a.get("type") != "Swim"
                else parse_interval_summary(a.get("interval_summary"))
            ),
            # Body & fuel
            "calories": a.get("calories"),
        }
        for a in _strip_empty(ret)
    ]
    return _strip_empty(ret)


def get_wellness(window="42d", raw=False):
    oldest, newest = _date_range(window)
    url = f"{BASE_URL}/athlete/{_athlete_id()}/wellness"
    resp = requests.get(
        url,
        params={"oldest": oldest, "newest": newest},
        auth=_auth(),
        timeout=30,
    )
    resp.raise_for_status()
    ret = resp.json()
    if raw:
        return ret
    ret = [
        {
            "date": w.get("id"),
            "ctl": w.get("ctl"),
            "atl": w.get("atl"),
            "ramp_rate": w.get("rampRate"),
            "resting_hr": w.get("restingHR"),
            "hrv": w.get("hrv"),
            "sleep_hours": seconds_to_hhmmss(w.get("sleepSecs")),
            "sleep_score": w.get("sleepScore"),
        }
        for w in _strip_empty(ret)
    ]
    return _strip_empty(ret)


def get_athlete(raw=False):
    # url = f"{BASE_URL}/athlete/{_athlete_id()}"
    # resp = requests.get(url, auth=_auth(), timeout=30)
    # resp.raise_for_status()
    # ret = resp.json()
    # if raw:
    # return ret
    return {
        "name": "Jason",
        "sex": "M",
        "weight": "150lbs",
        "age": get_age("1999-08-06"),
        "height": "5ft7in",
    }


def get_events(raw=False):
    """Fetch planned events / races."""
    oldest = (datetime.now().date() - timedelta(days=365)).isoformat()
    newest = (datetime.now().date() + timedelta(days=365)).isoformat()
    url = f"{BASE_URL}/athlete/{_athlete_id()}/events"
    resp = requests.get(
        url,
        params={"oldest": oldest, "newest": newest},
        auth=_auth(),
        timeout=30,
    )
    resp.raise_for_status()
    ret = resp.json()
    if raw:
        return ret
    # filter for races only
    ret = [
        {
            "name": e.get("name"),
            "date": e.get("start_date_local")[:10],
            "category": e.get("category"),
            "type": (e.get("type") if e.get("type") != "Other" else "Triathlon"),
            "description": e.get("description"),
        }
        for e in _strip_empty(ret)
        if e.get("category").startswith("RACE")
    ]
    return _strip_empty(ret)


def build_training_summary(window="42d"):
    now = time.time()
    if window in _cache:
        cached_at, data = _cache[window]
        if now - cached_at < CACHE_TTL:
            return data

    result = {
        "window": window,
        "athlete": get_athlete(),
        "wellness": get_wellness(window),
        "activities": get_activities(window),
        "events": get_events(),
    }

    _cache[window] = (now, result)
    return result
