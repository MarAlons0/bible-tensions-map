# Bible Tensions Map

An interactive web application for secular, academic analysis of the Bible as literature and historical document. It visualizes how theological and ethical tensions evolve across 65 biblical books — spanning the full Old and New Testaments — through four complementary views.

**Live app:** https://bible-tensions-map.onrender.com

---

## What it does

The Bible is not a monolithic document. It was composed over more than a millennium by dozens of authors, editors, and communities with divergent agendas, theologies, and social contexts. *Bible Tensions Map* treats it as a corpus and maps it along 20 analytical axes, asking: where does each book sit on each tension, and how do those positions shift across time and tradition?

The tool is designed for readers interested in historical-critical scholarship — not devotional use. Scores reflect the position of the text as scholars read it, not normative claims about which pole is correct.

---

## Views

### Heatmap
The main view. Each row is a book (or aggregate), each column is one of the 20 tensions, and each cell is colored from blue (Pole A, −5) to coral (Pole B, +5). Gray indicates a neutral or balanced position; white/empty means the tension is not applicable to that book.

The heatmap is **layered**:
- Starts with two aggregate rows — *Old Testament* and *New Testament* — each showing **median scores** across all their books.
- Click a testament row (▶/▼) to expand it into its canonical sections (e.g. Pentateuch, Historical Books, Pauline Epistles).
- Click a section row to expand it into individual books.
- Click any cell in a book row to open a **tension detail bar chart** below, showing how that tension scores across all currently-visible rows.

### Biplot
A two-dimensional scatter plot. Select any two tensions as the X and Y axes, then see where each book falls. Useful for identifying clusters (books that share a theological disposition) and outliers. Preset pairs highlight classic scholarly comparisons.

### Conduct Codes
Tracks how nine categories of practical conduct are addressed across the canon: diet, marriage and sexuality, homosexuality, slavery, clothing, agriculture, economic justice, violence and war, and ritual calendar. Select a category to see a chronologically ordered list of how each book handles it.

### Timeline
A line chart showing how tension scores shift across books ordered chronologically by **scholarly dating** (when scholars believe the text was composed) or **canonical order** (the traditional sequence). Toggle between the two orderings to compare the literary sequence with the historical one. Select which tensions to display; multiple tensions can be overlaid, with gaps where scores are not applicable.

### Book pages
Each book has its own page showing:
- Metadata: canonical section, dating, source traditions, summary
- All 20 tension scores as visual bar markers on a −5 to +5 track
- Conduct code entries for all applicable categories
- Chapter-level analysis via the Anthropic API (see below)

---

## The 20 tensions

| ID | Tension | Pole A | Pole B |
|----|---------|--------|--------|
| T01 | Divine transcendence vs. immanence | Transcendent/distant | Immanent/relational |
| T02 | Universalism vs. particularism | Universal/inclusive | Particularist/exclusive |
| T03 | Free will vs. divine determinism | Human agency | Divine sovereignty |
| T04 | Retributive vs. restorative justice | Retributive | Restorative/merciful |
| T05 | Ethical imperative vs. ritual/institutional observance | Ethical/prophetic priority | Ritual/institutional observance |
| T06 | Individual vs. collective identity | Individual | Collective/communal |
| T07 | Literal vs. allegorical/symbolic interpretation | Literal/historical | Allegorical/symbolic |
| T08 | Exclusivist vs. inclusivist soteriology | Exclusivist | Inclusivist |
| T09 | Faith vs. works | Faith/grace | Works/deeds |
| T10 | Theocracy vs. secular governance | Theocratic | Secular/civil |
| T11 | Patriarchal vs. egalitarian gender roles | Patriarchal | Egalitarian |
| T12 | Pacifism vs. just war | Pacifist | Just war/violence sanctioned |
| T13 | Prosperity gospel vs. suffering theology | Prosperity/blessing | Suffering/cross |
| T14 | Oral tradition vs. textual authority | Oral/living tradition | Written/textual authority |
| T15 | Creation care vs. dominion mandate | Stewardship/care | Human dominion |
| T16 | Syncretism vs. strict monotheism | Syncretic/pluralist | Strict monotheism |
| T17 | Wisdom/reason vs. revelation/faith | Wisdom/reason | Revelation/faith |
| T18 | Social justice vs. cultic piety | Social justice/prophetic | Cultic piety/ritual |
| T19 | Realized vs. apocalyptic eschatology | Realized/present | Apocalyptic/future |
| T20 | Suffering as redemptive vs. as punishment | Redemptive/meaningful | Divine punishment/retribution |

Scores run from −5 (strongly Pole A) to +5 (strongly Pole B). A score of 0 means both poles are actively present. `null` means the tension is not meaningfully applicable to that book.

---

## Chapter analysis (Anthropic API)

On any book page, individual chapters can be analyzed on demand. The app sends the chapter text to Claude and receives:
- A one-paragraph summary of the chapter's theological and ethical content
- Scores for each of the 20 tensions, with a brief rationale
- Conduct code entries for any of the 9 categories that appear

Results are stored in the database and displayed on subsequent visits without re-querying the API. The model used is `claude-sonnet-4-6`.

---

## Data

**65 books**: 38 Old Testament + 27 New Testament.

**Scoring methodology**: Scores are pre-computed scholarly assessments based on historical-critical consensus (drawing on resources like the New Oxford Annotated Bible and standard academic commentaries). They represent the dominant theological position of the text as reconstructed by scholars — not a reading from any single confessional tradition.

**Dating**: Scholarly dates follow critical consensus (e.g. Deuteronomy ~621 BCE reflecting Josianic reform; Second Isaiah ~550–540 BCE; Mark ~70 CE; Revelation ~95 CE). These are used for chronological ordering in the Timeline view.

---

## Technical design

| Layer | Technology |
|-------|-----------|
| Backend | Python / Flask |
| ORM | SQLAlchemy |
| Database | PostgreSQL (Render managed) |
| Charts | Plotly.js |
| AI analysis | Anthropic API (`claude-sonnet-4-6`) |
| Deployment | Render (web service + free-tier PostgreSQL) |

### Data model

- **Book** — id (3-letter code), name, testament, section, chapters, sort_order, dating, sources, summary
- **Tension** — id (T01–T20), name, pole_a, pole_b, sort_order
- **BookTension** — book_id × tension_id → score (integer −5..+5 or null), note
- **ConductCategory** — id, label, sort_order
- **BookConduct** — book_id × category_id → description text
- **ChapterAnalysis** — book_id, chapter, summary, analyzed_at
- **ChapterTension** — chapter analysis × tension → score, note
- **ChapterConduct** — chapter analysis × category → description
- **UserNote** — book_id, chapter (nullable), content, created_at

### Seed process

The database is seeded at startup via `python seed.py && gunicorn app:app`. The seed script is fully idempotent (upsert throughout), so it runs safely on every deployment restart. OT data comes from `seed_data.json`; NT data from `seed_data_nt.json`.

### Heatmap layering

All 65 books and their tension scores are loaded into the browser in a single API call (`/api/heatmap-full`). Expand/collapse state is managed entirely in JavaScript. Aggregate rows (testament and section) compute the **median** of non-null scores across their member books. No additional API calls are made when expanding or collapsing rows.

---

## Local development

```bash
# Clone and install
git clone https://github.com/MarAlons0/bible-tensions-map.git
cd bible-tensions-map
pip install -r requirements.txt

# Environment
export DATABASE_URL=sqlite:///bible.db
export ANTHROPIC_API_KEY=sk-...   # optional, only needed for chapter analysis

# Seed and run
python seed.py
flask run
```

The app will be available at `http://localhost:5000`.

To regenerate the NT seed data from the source script:
```bash
python generate_nt_seed.py   # writes seed_data_nt.json
python seed.py               # loads it into the database
```

---

## Repository

https://github.com/MarAlons0/bible-tensions-map
