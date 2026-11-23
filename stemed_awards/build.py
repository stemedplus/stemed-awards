"""Check every award and write the website, feed, and calendar.

    python -m stemed_awards --out output --previous https://<owner>.github.io/<repo>
    python -m stemed_awards --validate      # only check awards/*.yml

Output (all static, served by GitHub Pages):
    index.html            searchable list
    awards.json           everything listed; also tells the next run when each was first seen
    feeds/new.xml         RSS of newly listed awards
    feeds/deadlines.ics   calendar of every dated nomination deadline
"""
import argparse
import datetime as dt
import json
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional
from urllib.request import Request, urlopen

from . import awards, feeds
from . import stemedplus_disciplines
from .disciplines import DISCIPLINES

ROOT = Path(__file__).resolve().parent.parent
USER_AGENT = "STEMEd+ Awards (https://github.com/stemedplus/stemed-awards)"
SCHEMA = json.loads((ROOT / "schema" / "award.schema.json").read_text(encoding="utf-8"))["properties"]
STATUS_LABELS = {
    "open": "Taking nominations", "upcoming": "Deadline announced", "between-cycles": "Between cycles",
    "periodic": "Every few years", "paused": "Paused", "passed": "Deadline passed",
}
NOMINATION_LABELS = {
    "self": "Apply yourself", "self-or-others": "Self-nominations welcome",
    "others": "Nominated by others", "institution": "Nominated by an institution",
    "see-sponsor": "Check the sponsor's nomination rules",
}
ASSETS = ("stemedplus-commons-logo.png", "stemedplus-commons-logo-white.png", "stemedplus-theme.css", "manrope.woff")


def load_site() -> dict:
    return json.loads((ROOT / "config" / "site.json").read_text(encoding="utf-8"))


def load_previous(previous: Optional[str]) -> List[dict]:
    """Items from the last published awards.json (a URL or a local path). A missing or
    unreadable file just means a fresh start, e.g. on the very first run."""
    if not previous:
        return []
    try:
        if previous.startswith(("http://", "https://")):
            url = previous.rstrip("/") + "/awards.json"
            with urlopen(Request(url, headers={"User-Agent": USER_AGENT}), timeout=60) as resp:
                data = json.load(resp)
        else:
            data = json.loads(Path(previous).read_text(encoding="utf-8"))
        return data.get("items", [])
    except Exception as exc:  # noqa: BLE001 - any failure means "start fresh"
        print(f"Note: no previous listings loaded from {previous} ({exc}).")
        return []


def sort_key(item: dict):
    """Dated deadlines first (soonest first), then everything else by name."""
    return (0 if item["deadline"] else 1, item["deadline"] or "9999", item["title"].lower())


def run(out: Path, previous: Optional[str], today: dt.date, now: Optional[dt.datetime] = None) -> dict:
    now = now or dt.datetime.combine(today, dt.time(12), tzinfo=dt.timezone.utc)
    site = load_site()
    first_seen: Dict[str, str] = {i["id"]: i.get("first_seen", today.isoformat()) for i in load_previous(previous)}

    entries, problems = awards.load()
    if problems:
        raise SystemExit("Problems in awards/:\n  " + "\n  ".join(problems))
    items = [awards.to_record(slug, e, today) for slug, e in entries]
    for item in items:
        item["first_seen"] = first_seen.get(item["id"], today.isoformat())
    items.sort(key=sort_key)

    payload = {
        "generated": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "today": today.isoformat(),
        "site": site,
        "disciplines": list(DISCIPLINES),
        "named_only": list(stemedplus_disciplines.named_only_labels()),  # never listed for "all STEM+ fields"
        "recognizes": SCHEMA["recognizes"]["items"]["enum"],
        "stages": SCHEMA["stages"]["items"]["enum"],
        "levels": SCHEMA["levels"]["items"]["enum"],
        "sponsor_types": SCHEMA["sponsor_type"]["enum"],
        "status_labels": STATUS_LABELS,
        "nomination_labels": NOMINATION_LABELS,
        "review": [{"title": i["title"], "file": i["file"], "why": i["review"]} for i in items if i["review"]],
        "items": items,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "awards.json").write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                                     encoding="utf-8")
    shutil.copyfile(ROOT / "site" / "index.html", out / "index.html")
    for name in ASSETS:
        shutil.copyfile(ROOT / "site" / name, out / name)
    feeds.write_rss(out / "feeds" / "new.xml", items, site, now)
    feeds.write_ics(out / "feeds" / "deadlines.ics", items, site, now)
    print(f"Wrote {len(items)} awards; {len(payload['review'])} listing(s) to re-check.")
    return payload


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=Path("output"))
    ap.add_argument("--previous", help="URL of the published site (or a local awards.json)")
    ap.add_argument("--validate", action="store_true", help="only check awards/*.yml")
    args = ap.parse_args(argv)
    if args.validate:
        entries, problems = awards.load()
        for p in problems:
            print(p)
        print(f"{len(entries)} valid file(s), {len(problems)} problem(s).")
        return 1 if problems else 0
    run(args.out, args.previous, dt.date.today())
    return 0


if __name__ == "__main__":
    sys.exit(main())
