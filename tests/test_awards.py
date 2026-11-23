import datetime as dt
import json
import re
import tempfile
import unittest
from pathlib import Path

import yaml

from stemed_awards import awards, build, feeds
from stemed_awards.disciplines import DISCIPLINES

ROOT = Path(__file__).resolve().parent.parent
TODAY = dt.date(2026, 11, 23)


def entry(**changes):
    e = {"name": "Test Award", "sponsor": "Test Society", "sponsor_type": "Society or association",
         "url": "https://example.org/award", "status": "between-cycles", "nomination": "others",
         "recognizes": ["Teaching"], "summary": "Recognizes something worth recognizing.", "checked": "2026-11-20"}
    e.update(changes)
    return e


class ListingTests(unittest.TestCase):
    def test_every_listing_is_valid(self):
        entries, problems = awards.load()
        self.assertEqual(problems, [])
        self.assertGreater(len(entries), 30)

    def test_listings_use_shared_disciplines_only(self):
        for path in (ROOT / "awards").glob("*.yml"):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            for d in data.get("disciplines", []):
                self.assertIn(d, DISCIPLINES, path.name)

    def test_unknown_discipline_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "bad.yml").write_text(yaml.safe_dump(entry(disciplines=["Physics", "Astrology"])))
            entries, problems = awards.load(Path(tmp))
            self.assertEqual(entries, [])
            self.assertTrue(any("Astrology" in p for p in problems))

    def test_national_awards_need_a_country(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "bad.yml").write_text(yaml.safe_dump(entry(open_to="National")))
            _, problems = awards.load(Path(tmp))
            self.assertTrue(any("country" in p for p in problems))

    def test_opens_after_deadline_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "bad.yml").write_text(yaml.safe_dump(entry(status="upcoming", opens="2027-03-01", deadline="2027-02-01")))
            _, problems = awards.load(Path(tmp))
            self.assertTrue(any("opens is after deadline" in p for p in problems))


class RecordTests(unittest.TestCase):
    def test_passed_deadline_is_dropped_and_flagged(self):
        r = awards.to_record("x", entry(status="open", deadline="2026-11-01"), TODAY)
        self.assertEqual((r["status"], r["deadline"]), ("passed", ""))
        self.assertIn("deadline passed", r["review"])

    def test_upcoming_becomes_open_once_window_opens(self):
        r = awards.to_record("x", entry(status="upcoming", opens="2026-11-01", deadline="2027-01-15"), TODAY)
        self.assertEqual(r["status"], "open")

    def test_open_without_deadline_is_flagged(self):
        r = awards.to_record("x", entry(status="open"), TODAY)
        self.assertIn("open or upcoming without a deadline", r["review"])

    def test_stale_check_is_flagged(self):
        r = awards.to_record("x", entry(checked="2025-01-01"), TODAY)
        self.assertTrue(any(w.startswith("last checked") for w in r["review"]))

    def test_no_disciplines_means_all_fields(self):
        self.assertTrue(awards.to_record("x", entry(), TODAY)["all_fields"])
        self.assertFalse(awards.to_record("x", entry(disciplines=["Physics"]), TODAY)["all_fields"])


class BuildTests(unittest.TestCase):
    def test_build_writes_site_feed_and_calendar(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            payload = build.run(out, None, TODAY)
            for name in ("index.html", "awards.json", "feeds/new.xml", "feeds/deadlines.ics", "stemedplus-theme.css"):
                self.assertTrue((out / name).exists(), name)
            dated = [i for i in payload["items"] if i["deadline"]]
            self.assertEqual([i["deadline"] for i in dated], sorted(i["deadline"] for i in dated))
            self.assertEqual(payload["items"][: len(dated)], dated)   # dated deadlines first
            ics = (out / "feeds" / "deadlines.ics").read_bytes().decode("utf-8")
            self.assertEqual(ics.count("BEGIN:VEVENT"), len(dated))
            self.assertTrue(all(len(line.encode()) <= 75 for line in ics.split("\r\n")))

    def test_first_seen_carries_over(self):
        with tempfile.TemporaryDirectory() as tmp:
            prev = Path(tmp) / "prev.json"
            prev.write_text(json.dumps({"items": [{"id": "award:paemst", "first_seen": "2026-01-01"}]}))
            payload = build.run(Path(tmp) / "out", str(prev), TODAY)
            seen = {i["id"]: i["first_seen"] for i in payload["items"]}
            self.assertEqual(seen["award:paemst"], "2026-01-01")
            self.assertEqual(seen["award:nsta-teacher-awards"], TODAY.isoformat())

    def test_every_status_and_nomination_has_a_label(self):
        props = json.loads((ROOT / "schema" / "award.schema.json").read_text())["properties"]
        for s in props["status"]["enum"] + ["passed"]:
            self.assertIn(s, build.STATUS_LABELS)
        for n in props["nomination"]["enum"]:
            self.assertIn(n, build.NOMINATION_LABELS)

    def test_rss_lists_newest(self):
        item = awards.to_record("x", entry(), TODAY)
        item["first_seen"] = TODAY.isoformat()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "new.xml"
            feeds.write_rss(path, [item], build.load_site(), dt.datetime(2026, 11, 23, tzinfo=dt.timezone.utc))
            self.assertIn("<title>Test Award</title>", path.read_text(encoding="utf-8"))


class FormTests(unittest.TestCase):
    def test_suggest_form_offers_every_discipline(self):
        form = (ROOT / ".github" / "ISSUE_TEMPLATE" / "suggest_award.yml").read_text(encoding="utf-8")
        for d in DISCIPLINES:
            self.assertIn(d, form)

    def test_page_uses_the_issue_templates_that_exist(self):
        page = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        for name in set(re.findall(r"(\w+\.yml)", page)):
            self.assertTrue((ROOT / ".github" / "ISSUE_TEMPLATE" / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
