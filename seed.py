"""
Seed (and re-seed) the database from seed_data.json.
Safe to run multiple times — uses upserts throughout.
Run: python seed.py
"""
import hashlib
import json
import os
from sqlalchemy import inspect, text
from app import create_app
from models import (
    db, Tension, ConductCategory, Book, BookTension, BookConduct,
    ChapterAnalysis, ChapterTension, ChapterConduct, UserNote, JournalEntry, SeedState,
)

CONDUCT_LABELS = {
    'diet': 'Diet',
    'marriage_sexuality': 'Marriage & Sexuality',
    'homosexuality': 'Homosexuality',
    'slavery': 'Slavery',
    'clothing': 'Clothing',
    'agriculture': 'Agriculture',
    'economic_justice': 'Economic Justice',
    'violence_war': 'Violence & War',
    'ritual_calendar': 'Ritual Calendar',
}

CANONICAL_ORDER = [
    'GEN', 'EXO', 'LEV', 'NUM', 'DEU',
    'JOS', 'JDG', 'RUT', '1SA', '2SA',
    '1KI', '2KI', '1CH', '2CH', 'EZR', 'NEH', 'EST',
    'JOB', 'PSA', 'PRO', 'ECC', 'SNG',
    'ISA', 'JER', 'LAM', 'EZK', 'DAN',
    'HOS', 'JOL', 'AMO', 'OBA', 'JON',
    'MIC', 'NAM', 'HAB', 'ZEP', 'HAG', 'ZEC', 'MAL',
    # Apocrypha (NOAB NRSV order)
    'TOB', 'JDT', 'AES', '1MA', '2MA', 'WIS', 'SIR',
    'BAR', 'LJE', 'PAZ', 'SUS', 'BEL', '1ES', 'MAN', 'PS2', '3MA', '2ES',
    # NT
    'MAT', 'MRK', 'LUK', 'JHN', 'ACT',
    'ROM', '1CO', '2CO', 'GAL', 'EPH', 'PHP', 'COL',
    '1TH', '2TH', '1TI', '2TI', 'TIT', 'PHM',
    'HEB', 'JAS', '1PE', '2PE', '1JN', '2JN', '3JN', 'JUD',
    'REV',
]


def upsert_tension(i, t):
    existing = db.session.get(Tension, t['id'])
    if existing:
        existing.name = t['name']
        existing.pole_a = t['pole_a']
        existing.pole_b = t['pole_b']
        existing.sort_order = i
    else:
        db.session.add(Tension(
            id=t['id'], name=t['name'],
            pole_a=t['pole_a'], pole_b=t['pole_b'],
            sort_order=i,
        ))


def upsert_book(book_id, book, testament):
    sort_order = CANONICAL_ORDER.index(book_id) if book_id in CANONICAL_ORDER else 999
    existing = db.session.get(Book, book_id)
    if existing:
        existing.name = book['name']
        existing.testament = testament
        existing.section = book.get('section')
        existing.chapters = book.get('chapters')
        existing.sort_order = sort_order
        existing.dating = book.get('dating')
        existing.sources = book.get('sources')
        existing.summary = book.get('summary')
    else:
        db.session.add(Book(
            id=book_id, name=book['name'], testament=testament,
            section=book.get('section'), chapters=book.get('chapters'),
            sort_order=sort_order, dating=book.get('dating'),
            sources=book.get('sources'), summary=book.get('summary'),
        ))


def upsert_book_tension(book_id, tension_id, t_data):
    score = t_data.get('score') if isinstance(t_data, dict) else None
    note  = t_data.get('note')  if isinstance(t_data, dict) else None
    existing = db.session.get(BookTension, (book_id, tension_id))
    if existing:
        existing.score = score
        existing.note  = note
    else:
        db.session.add(BookTension(
            book_id=book_id, tension_id=tension_id,
            score=score, note=note,
        ))


def upsert_book_conduct(book_id, cat_id, description):
    if not description:
        return
    existing = db.session.get(BookConduct, (book_id, cat_id))
    if existing:
        existing.description = description
    else:
        db.session.add(BookConduct(
            book_id=book_id, category_id=cat_id,
            description=description,
        ))


def seed_file(data_path, testament):
    with open(data_path) as f:
        data = json.load(f)

    # Tensions (optional — already seeded from OT)
    for i, t in enumerate(data.get('tensions', [])):
        upsert_tension(i, t)

    # Conduct categories (optional — already seeded from OT)
    for i, cat_id in enumerate(data.get('conduct_categories', [])):
        existing = db.session.get(ConductCategory, cat_id)
        label = CONDUCT_LABELS.get(cat_id, cat_id.replace('_', ' ').title())
        if existing:
            existing.label = label
            existing.sort_order = i
        else:
            db.session.add(ConductCategory(id=cat_id, label=label, sort_order=i))

    db.session.flush()

    # Books + scores + conduct
    for book_id, book in data['books'].items():
        upsert_book(book_id, book, testament)
        db.session.flush()

        for tension_id, t_data in book.get('tensions', {}).items():
            upsert_book_tension(book_id, tension_id, t_data)

        for cat_id, description in book.get('conduct', {}).items():
            upsert_book_conduct(book_id, cat_id, description)

    db.session.commit()
    print(f"  {testament}: {len(data['books'])} books, "
          f"{len(data.get('tensions', []))} tensions, "
          f"{len(data.get('conduct_categories', []))} conduct categories")


SEED_FILES = ['seed_data.json', 'seed_data_apocrypha.json', 'seed_data_nt.json']


def seed_files_hash():
    base = os.path.dirname(os.path.abspath(__file__))
    h = hashlib.sha256()
    for name in SEED_FILES:
        path = os.path.join(base, name)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                h.update(f.read())
    return h.hexdigest()


def needs_seed():
    """True if the DB is missing books or the seed files changed since the last seed."""
    try:
        if Book.query.count() < 83:
            return True
        state = db.session.get(SeedState, 'seed_files_hash')
        return state is None or state.value != seed_files_hash()
    except Exception:
        return True


# Scores whose direction is beyond dispute: (book, tension, expected sign).
# A violation means a book or a whole axis was scored with the poles reversed.
POLARITY_ANCHORS = [
    ('JOS', 'T02', +1), ('JON', 'T02', -1), ('GAL', 'T02', -1),   # exclusivism +
    ('EXO', 'T01', -1), ('WIS', 'T01', +1),                       # monotheism +
    ('ECC', 'T07', -1), ('DAN', 'T07', +1), ('2MA', 'T07', +1),   # resurrection +
    ('LEV', 'T09', +1), ('GAL', 'T09', -1),                       # works +
    ('SIR', 'T08', -1), ('SNG', 'T08', +1),                       # women as agents +
    ('1MA', 'T16', -1), ('DAN', 'T16', +1),                       # mythological +
]


def check_polarity():
    bad = []
    for book_id, tension_id, sign in POLARITY_ANCHORS:
        bt = db.session.get(BookTension, (book_id, tension_id))
        if bt is None or bt.score is None or bt.score * sign <= 0:
            bad.append(f"{book_id} {tension_id}={bt.score if bt else None}")
    if bad:
        print("WARNING: scores pointing the wrong way (poles reversed?): " + ', '.join(bad))
    return not bad


def record_seed():
    state = db.session.get(SeedState, 'seed_files_hash')
    if state is None:
        db.session.add(SeedState(key='seed_files_hash', value=seed_files_hash()))
    else:
        state.value = seed_files_hash()
    db.session.commit()


def seed():
    base = os.path.dirname(__file__)

    print("Seeding OT...")
    seed_file(os.path.join(base, 'seed_data.json'), 'Old Testament')

    apocrypha_path = os.path.join(base, 'seed_data_apocrypha.json')
    if os.path.exists(apocrypha_path):
        print("Seeding Apocrypha...")
        seed_file(apocrypha_path, 'Apocrypha')

    nt_path = os.path.join(base, 'seed_data_nt.json')
    if os.path.exists(nt_path):
        print("Seeding NT...")
        seed_file(nt_path, 'New Testament')

    print("Done.")


def migrate():
    """Add columns that create_all() won't add to existing tables."""
    cols = {c['name'] for c in inspect(db.engine).get_columns('user_notes')}
    with db.engine.begin() as conn:
        for name in ('source', 'heading', 'speaker'):
            if name not in cols:
                conn.execute(text(f'ALTER TABLE user_notes ADD COLUMN {name} TEXT'))
                print(f"Added user_notes.{name}")


def seed_reading_notes():
    """Load seed_data_reading_notes.json, replacing any previous import of it."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seed_data_reading_notes.json')
    if not os.path.exists(path):
        return
    with open(path) as f:
        data = json.load(f)
    source, points_source = data['source'], data.get('points_source')
    UserNote.query.filter(UserNote.source.in_([source, points_source])).delete()
    JournalEntry.query.filter_by(source=source).delete()

    # My own points first, so they come before the summary takeaways (ordered by id)
    for p in data.get('points', []):
        for book_id in p['books'] or [None]:
            db.session.add(UserNote(book_id=book_id, chapter=p['chapter'], note=p['note'],
                                    source=points_source, heading=p['heading'],
                                    speaker=p['speaker']))

    entries = [('intro', None, data['intro'])]
    entries += [('conclusion', c['title'], c['body']) for c in data['conclusions']]
    entries += [('theme', t['theme'], t['trajectory']) for t in data['themes']]
    entries += [('question', None, q) for q in data['open_questions']]
    for i, (kind, title, body) in enumerate(entries):
        db.session.add(JournalEntry(kind=kind, title=title, body=body, sort_order=i, source=source))

    # A note spanning several books ("1-2 Kings") is stored once per book so it
    # shows on each book's page; the journal page de-duplicates by heading.
    for n in data['notes']:
        for book_id in n['books'] or [None]:
            db.session.add(UserNote(book_id=book_id, chapter=n['chapter'], note=n['note'],
                                    source=source, heading=n['heading']))
    db.session.commit()
    print(f"Loaded {len(data.get('points', []))} dialog points and {len(data['notes'])} summary notes.")


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        migrate()
        if needs_seed():
            seed()
            check_polarity()
            record_seed()
        else:
            print("DB already seeded, skipping.")
        seed_reading_notes()
