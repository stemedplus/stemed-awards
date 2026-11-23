"""Awards kept by hand, one YAML file each in awards/."""
import datetime as dt
import json
from pathlib import Path
from typing import List, Tuple

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from .disciplines import DISCIPLINES

ROOT = Path(__file__).resolve().parent.parent
FOLDER = ROOT / "awards"
SCHEMA = json.loads((ROOT / "schema" / "award.schema.json").read_text(encoding="utf-8"))
# The allowed disciplines are the shared STEMEd+ list, not a copy in the schema file.
SCHEMA["properties"]["disciplines"]["items"] = {"enum": list(DISCIPLINES)}
REVIEW_AFTER_DAYS = 180


def _plain(value):
    """YAML reads dates as date objects; the schema and the site want strings."""
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, list):
        return [_plain(v) for v in value]
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    return value


def load(folder: Path = FOLDER) -> Tuple[List[Tuple[str, dict]], List[str]]:
    """(slug, entry) for every valid file, and a list of problems."""
    validator = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
    entries, problems = [], []
    for path in sorted(folder.glob("*.yml")):
        try:
            data = _plain(yaml.safe_load(path.read_text(encoding="utf-8")))
        except yaml.YAMLError as exc:
            problems.append(f"{path.name}: not valid YAML ({exc})")
            continue
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        for e in errors:
            where = ".".join(str(p) for p in e.path) or "(file)"
            problems.append(f"{path.name}: {where}: {e.message}")
        if not errors and data.get("opens") and data.get("deadline") and data["opens"] > data["deadline"]:
            problems.append(f"{path.name}: opens is after deadline")
            continue
        if not errors:
            entries.append((path.stem, data))
    return entries, problems


def to_record(slug: str, e: dict, today: dt.date) -> dict:
    today_s = today.isoformat()
    status, deadline = e["status"], e.get("deadline", "")
    if deadline and deadline < today_s:
        status, deadline = "passed", ""
    elif status == "upcoming" and e.get("opens") and e["opens"] <= today_s:
        status = "open"   # the window has opened since the file was last edited
    checked = e["checked"]
    review = []
    if status == "passed":
        review.append("deadline passed")
    if e["status"] in ("open", "upcoming") and not e.get("deadline"):
        review.append("open or upcoming without a deadline")
    if checked < (today - dt.timedelta(days=REVIEW_AFTER_DAYS)).isoformat():
        review.append(f"last checked {checked}")
    return {
        "id": f"award:{slug}",
        "sponsor_type": e["sponsor_type"],
        "sponsor": e["sponsor"],
        "title": e["name"],
        "url": e["url"],
        "status": status,
        "opens": e.get("opens", ""),
        "deadline": deadline,
        "deadline_note": e.get("deadline_note", ""),
        "prize": e.get("prize", ""),
        "eligibility": e.get("eligibility", ""),
        "open_to": e.get("open_to", ""),
        "country": e.get("country", ""),
        "nomination": e["nomination"],
        "recognizes": e["recognizes"],
        "stages": e.get("stages", []),
        "levels": e.get("levels", []),
        "summary": e["summary"],
        "disciplines": e.get("disciplines", []),
        "all_fields": not e.get("disciplines"),
        "checked": checked,
        "review": review,
        "file": f"awards/{slug}.yml",
    }
