# Runbook: Awards

This board uses the shared STEMEd+ pipeline. For how every board works and the common fixes, see the [stemedplus-theme runbook](https://github.com/stemedplus/stemedplus-theme/blob/main/RUNBOOK.md).

| | |
|---|---|
| **Site** | stemedplus.github.io/stemed-awards |
| **Repository** | stemedplus/stemed-awards |
| **Updates** | Daily at 11:17 UTC, on push, and by hand (`update.yml`) |
| **Listings** | One YAML file per award in `awards/` (CC BY 4.0), checked against `schema/award.schema.json` |
| **Check / build** | `python -m stemed_awards --validate`, then `python -m stemed_awards --out output` |
| **Feeds** | `feeds/deadlines.ics` (nomination deadlines, also pulled into Deadlines) and `feeds/new.xml` (new awards) |
| **Add or fix** | **Suggest an award** and **Correct a listing** issue forms (labeled `add award` or `update award`), or email libarkin@msu.edu |

**Between cycles:** most awards run yearly and stay listed between cycles with `status: between-cycles` and a `deadline_note`. When a sponsor announces dates, add `deadline: YYYY-MM-DD` and set `status: open` or `upcoming`.

**Routine check:** passed deadlines switch to "Deadline passed" by themselves, and the footer lists them for a maintainer, along with any listing not checked in 180 days. Check the sponsor's page and update `checked:` each time.

**Write summaries in your own words;** don't copy the sponsor's text.

**First-seen dates** carry over from the published `awards.json`, so the repository never needs data commits.

_Written November 2026. Review with the yearly December review._
