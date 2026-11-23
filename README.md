# STEMEd+ Awards

National and international awards for STEM+ teaching, STEM+ education research, and
education-adjacent work such as science communication and public engagement, across every
STEMEd+ discipline, with who can be nominated and when nominations are due.

The list covers awards from professional societies (AAS, AGU, APS, ACS, RSC, IOP, AAAS, ACM
SIGCSE, ASEE, NARST, AERA, AMTE, NABT, NSTA, MAA, ASM, HSS, NAGT, GSA, NAAEE, EGU, RAS, and
others), academies (NAE), international bodies (ICMI, IUPAP, UNESCO), government programs (USDA,
EPA, PAEMST), and foundations. Each award is one short file in [`awards/`](awards/), checked
against the sponsor's own page. Campus and regional awards are not listed unless they lead to a
national one.

Disciplines use the STEMEd+ discipline list shared by every STEMEd+ board, so Astronomy & Space
Science, Environmental Science, Computing, History & Philosophy of Science, and Science & Health
Communication all have their own awards here.

🔎 **Website:** https://stemedplus.github.io/stemed-awards/ (once GitHub Pages is turned on)

## What you get

| | |
|---|---|
| **Website** | Search and filter by what an award recognizes (teaching, education research, communication and public engagement, mentoring, curriculum and innovation, broadening participation, service and leadership), discipline, where the work happens (K-12, undergraduate, graduate and professional, informal and public), career stage, who nominates (including "self-nominations welcome"), which countries' nominees are eligible, status, and how soon nominations are due. "Copy link to this view" shares any filtered view. |
| **Nomination calendar** | [`feeds/deadlines.ics`](https://stemedplus.github.io/stemed-awards/feeds/deadlines.ics) has every dated nomination deadline. Subscribe in Google Calendar, Outlook, or Apple Calendar ("add calendar from URL"). It is also part of [STEMEd+ Deadlines](https://stemedplus.github.io/stemed-deadlines/). |
| **RSS** | [`feeds/new.xml`](https://stemedplus.github.io/stemed-awards/feeds/new.xml) lists newly added awards. |

Most awards run once a year and are listed between cycles too, with how the cycle usually runs,
so you can plan a nomination and line up letters early. When a listed deadline passes, the
listing switches to "Deadline passed" by itself, and the site's footer lists it for a maintainer
to check, along with any listing not checked in 180 days. Always confirm on the sponsor's page
before nominating; every listing links there.

## A listing

```yaml
name: "Biggs Award for Excellence in Earth Science Teaching"
sponsor: "Geological Society of America, Geoscience Education Division"
sponsor_type: "Society or association"   # Society or association, Academy, Foundation, Government, International organization
url: "https://community.geosociety.org/gedivision/biggsaward"
status: "between-cycles"   # open, upcoming, between-cycles, periodic (every few years), paused
                           # add deadline: YYYY-MM-DD once the sponsor announces it
deadline_note: "Annual; recent deadlines have been in March. Self-nominations are accepted."
prize: "$750"
eligibility: "College and university Earth science instructors within 10 years of starting full-time teaching."
                           # open_to: "International" or "National" (with country:), if the sponsor says
nomination: "self-or-others"   # self, self-or-others, others, institution, see-sponsor
recognizes: ["Teaching"]
stages: ["Early career"]       # leave out if any career stage
levels: ["Undergraduate"]      # leave out if any level
summary: "Recognizes innovative and effective teaching of Earth science by early-career college and university faculty."
disciplines: ["Earth Science"] # leave empty for awards open to all STEM+ fields
checked: 2026-11-23            # when someone last checked the sponsor's page
```

The full rules are in [`schema/award.schema.json`](schema/award.schema.json), and every file is
checked automatically. Summaries are written in our own words rather than copied.

## Add or correct a listing

* **Suggest an award:** use the [Suggest an award](../../issues/new?template=suggest_award.yml) form.
* **Report a correction:** use the [Correct a listing](../../issues/new?template=update_award.yml) form,
  or the "Report a correction" link on any listing.
* **No GitHub account?** Email the maintainer at libarkin@msu.edu.
* **Edit directly:** add or change a file in [`awards/`](awards/) and open a pull request.
  The checks run on every pull request.

Suggestions arrive as issues labeled `add award` or `update award`.

## Running it

Python 3.10+ with PyYAML and jsonschema (`pip install -r requirements.txt`).

```bash
python -m unittest discover -s tests -t .   # tests (no network)
python -m stemed_awards --validate          # check the files in awards/
python -m stemed_awards --out output        # build the site in output/
```

`.github/workflows/update.yml` runs this every day and publishes to GitHub Pages, so passed
deadlines drop off on time. It carries over when each listing was first seen from the published
site's `awards.json`, so the repository never needs data commits. Turn it on once in
**Settings → Pages → Source: GitHub Actions**.

## Settings

| File | What it controls |
|---|---|
| `config/site.json` | Title, tagline, links to the other STEMEd+ sites, and the size of the RSS feed. |
| `awards/*.yml` | The listings. |

## License

Code: MIT. Listings in `awards/`: [CC BY 4.0](awards/LICENSE.md). The disciplines (labels,
definitions, and matching words) come from the STEMEd+ discipline list shared across STEMEd+
Commons, kept in [stemedplus-theme](https://github.com/stemedplus/stemedplus-theme)
(`stemedplus_disciplines.json`) and stored here as `stemed_awards/stemedplus_disciplines.json`;
each build refreshes the stored copy.
