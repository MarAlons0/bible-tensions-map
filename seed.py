"""
Seed the database from seed_data.json.
Run once after creating the schema: python seed.py
"""
import json
import os
from app import create_app
from models import db, Tension, ConductCategory, Book, BookTension, BookConduct

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

# All 38 OT books covered in seed data, in canonical order.
# Used to derive sort_order since the JSON dict preserves insertion order.
CANONICAL_ORDER = [
    'GEN', 'EXO', 'LEV', 'NUM', 'DEU',           # Pentateuch
    'JOS', 'JDG', 'RUT', '1SA', '2SA',            # Historical
    '1KI', '2KI', '1CH', '2CH', 'EZR', 'NEH', 'EST',
    'JOB', 'PSA', 'PRO', 'ECC', 'SNG',            # Wisdom / Poetry
    'ISA', 'JER', 'LAM', 'EZK', 'DAN',            # Major Prophets
    'HOS', 'JOL', 'AMO', 'OBA', 'JON',            # Minor Prophets
    'MIC', 'NAM', 'HAB', 'ZEP', 'HAG', 'ZEC',
]


def seed():
    data_path = os.path.join(os.path.dirname(__file__), 'seed_data.json')
    with open(data_path) as f:
        data = json.load(f)

    # --- Tensions ---
    for i, t in enumerate(data['tensions']):
        if not db.session.get(Tension, t['id']):
            db.session.add(Tension(
                id=t['id'],
                name=t['name'],
                pole_a=t['pole_a'],
                pole_b=t['pole_b'],
                sort_order=i,
            ))

    # --- Conduct categories ---
    for i, cat_id in enumerate(data['conduct_categories']):
        if not db.session.get(ConductCategory, cat_id):
            db.session.add(ConductCategory(
                id=cat_id,
                label=CONDUCT_LABELS.get(cat_id, cat_id.replace('_', ' ').title()),
                sort_order=i,
            ))

    db.session.flush()

    # --- Books ---
    for book_id, book in data['books'].items():
        sort_order = CANONICAL_ORDER.index(book_id) if book_id in CANONICAL_ORDER else 99

        if not db.session.get(Book, book_id):
            db.session.add(Book(
                id=book_id,
                name=book['name'],
                testament='Old Testament',   # all seed data is OT
                section=book.get('section'),
                chapters=book.get('chapters'),
                sort_order=sort_order,
                dating=book.get('dating'),
                sources=book.get('sources'),
                summary=book.get('summary'),
            ))

        db.session.flush()

        # Tension scores
        for tension_id, t_data in book.get('tensions', {}).items():
            existing = db.session.get(BookTension, (book_id, tension_id))
            if not existing:
                # t_data may be None (not applicable) or a dict with score/note
                score = t_data.get('score') if isinstance(t_data, dict) else None
                note  = t_data.get('note')  if isinstance(t_data, dict) else None
                db.session.add(BookTension(
                    book_id=book_id,
                    tension_id=tension_id,
                    score=score,
                    note=note,
                ))

        # Conduct entries
        for cat_id, description in book.get('conduct', {}).items():
            existing = db.session.get(BookConduct, (book_id, cat_id))
            if not existing and description:
                db.session.add(BookConduct(
                    book_id=book_id,
                    category_id=cat_id,
                    description=description,
                ))

    db.session.commit()
    print(f"Seeded {len(data['tensions'])} tensions, "
          f"{len(data['conduct_categories'])} conduct categories, "
          f"{len(data['books'])} books.")


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        seed()
