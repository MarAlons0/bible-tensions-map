# Bible Tensions Map — agent guide

Maps biblical books across theological tensions with heatmap, biplot, timeline, and word-cloud
views. Flask + PostgreSQL (Neon) + Claude API, deployed on Render.

## Project standards (read these before related work)
This repo follows shared standards documented at its root:
- **VERSIONING.md** — when shipping a feature, bump `VERSION`, add a `CHANGELOG.md` entry (Keep a Changelog), and tag per SemVer.
- **BACKLOG_FORMAT.md** — keep `BACKLOG.md` in the standard format (priority sections, checkbox status, type tags, ✅ Shipped). Long design specs go in `docs/`.
- **FAVICON.md** — favicon kit + root serving + Safari rules.

These three docs are synced from the `project-dashboard` repo (the source of truth) — don't edit
them here; change the master there and run its `sync-standards.sh`.

## Current open priorities (see BACKLOG.md for full detail)
No 🔴 High items at present.

**🟡 Medium**
- Export heatmap / biplot as PNG + CSV
- Book search / jump (quick nav from any page)
- Mobile layout pass (heatmap, biplot, timeline)

**🟢 Low**
- Dark-mode toggle

## Reading journal
`docs/my-points-by-book.md` (my own `[me]` points + `[claude]` replies) and `docs/reading-notes.md`
(Claude's summary: conclusions, themes, takeaways) are the sources for `/journal` and the imported
book notes. After editing either,
run `python import_reading_notes.py` and commit the regenerated `seed_data_reading_notes.json`;
`seed.py` (run on every Render deploy) replaces the previous import.
`meta_analysis.py` builds the meta-analysis prompt from those notes + tension scores and runs it
in a background thread (longer than gunicorn's 120s timeout); results are stored in `meta_analyses`.

When a task ships: move its BACKLOG.md entry to ✅ Shipped with its version, add a CHANGELOG.md entry, bump VERSION, commit + tag.

## Seed data
`seed.py` reseeds whenever `seed_data*.json` change (hash stored in `seed_state`) and warns if
the `POLARITY_ANCHORS` point the wrong way. Score polarity follows each tension's definition
(-5 = pole A). Apocrypha + Malachi scores come from `rescored_tensions.py`.
