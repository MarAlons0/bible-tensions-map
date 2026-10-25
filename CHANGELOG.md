# Changelog

All notable changes to Bible Tensions Map are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/);
this project adheres to [Semantic Versioning](https://semver.org/) per `VERSIONING.md`.

## [0.7.1] – 2026-10-25
### Fixed
- **Apocrypha scores were on the wrong axes.** The 17 Apocrypha books (and Malachi) had been scored against an earlier list of 20 tensions, so their scores appeared under unrelated tensions (e.g. 2 Maccabees' resurrection under eschatology, its monotheism under "Historical vs. Mythological"). All 18 books re-scored against the app's T01–T20 (`rescored_tensions.py`, applied by `apply_tension_fixes.py`).
- **T02 was inverted for the Hebrew Bible** (−5 meant exclusivism, the reverse of the definition the New Testament follows). Signs flipped for 31 books; rationales unchanged.
- Chapter analysis told Claude every chapter was from the Hebrew Bible; it now names the right corpus.
- Corrected seed data now reaches production: `seed.py` reseeds when the seed files change, not only when books are missing.
### Added
- `seed.py` checks a set of unambiguous anchor scores after seeding and warns if any point the wrong way.

## [0.7.0] – 2026-10-24
### Added
- **Meta-analysis** (`/journal/analysis`): Claude (Opus 5.5) reads every point in the Reading Journal alongside the app's tension scores and writes a structured synthesis — lines of questioning, how the reading changed, notes vs. scores, closing observations assessed, the dialog itself, threads to pull.
- Runs in the background and the page polls until done; each run is saved, with earlier runs listed.
### Changed
- `anthropic` SDK upgraded 0.40.0 → 0.125.0.

## [0.6.0] – 2026-10-24
### Added
- **Reading Journal** (`/journal`): my closing observations (in my words and summarised), themes traced across the canon, book-by-book points and open questions from my full reading of the Bible with Claude.
- Two imported sources: my own points per book with Claude's short replies (`docs/my-points-by-book.md`, 216 points + 28 replies), and Claude's summary takeaways (`docs/reading-notes.md`).
- `import_reading_notes.py` parses both into `seed_data_reading_notes.json`; `seed.py` loads it on deploy (re-runnable, replaces the previous import).
- Imported points appear in each book's **My Notes** panel, linked to the chapter they reference.
### Changed
- `user_notes` gains `source`, `heading` and `speaker` columns (added automatically by `seed.py`).
### Security
- Notes are now HTML-escaped when rendered on the book page.

## [0.5.0] – 2026-06-01
### Added
- `VERSIONING.md` and `FAVICON.md` project standards; this `CHANGELOG.md` and a `VERSION` file.
- Full Safari favicon and bookmark support (multi-size icons, root routes).

## [0.4.1] – 2026-04-16
### Fixed
- SSL connection drops with Neon PostgreSQL (pool pre-ping / recycle).
- JSON parse failure in chapter analysis; surface the real error message on failure.
- Missing chapter-analysis tables on a fresh database.
- Heatmap height not growing on expand.
### Changed
- Skip seeding on warm restarts to reduce cold-start time; raise gunicorn timeout to 120s for Anthropic calls.

## [0.4.0] – 2026-04-11
### Added
- Apocrypha: 17 NOAB/NRSV books across 5 sections, with word-cloud drill-down.

## [0.3.0] – 2026-04-09
### Added
- Word Cloud page with semantic term merging and nested drill-down.

## [0.2.0] – 2026-04-08
### Added
- Layered collapsible heatmap (Testament → Section → Book) with directly clickable axis labels.
- README and About page with nav link.
- Malachi (MAL) — complete entry across all 20 tensions and 9 conduct categories.
### Fixed
- Biplot: distinct colors for Testament and Section groups.

## [0.1.0] – 2026-04-07
### Added
- Initial build: Bible Tensions Map with the full New Testament seed (27 books), tension scores, and date estimates.
- Timeline view with a tension-evolution line chart and scholarly/canonical toggle.
### Changed
- Tension axes: renamed T05 and replaced T09/T19/T20 with Faith/Works, Eschatology, and Suffering axes.
