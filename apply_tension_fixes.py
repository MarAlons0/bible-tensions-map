"""
One-off data fixes to the seed files (safe to re-run):

1. Replace the tension scores of the 17 Apocrypha books and Malachi, which were
   scored against an earlier tension list, with rescored_tensions.RESCORED.
2. Flip T02 for the Hebrew Bible books: they were scored with -5 = exclusivism,
   the reverse of the app's definition (-5 = universal compassion) that the
   New Testament follows. Their rationales already describe the right pole.

Run: python apply_tension_fixes.py   (then seed.py picks the changes up)
"""
import json
import os

from rescored_tensions import RESCORED

BASE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    with open(os.path.join(BASE, name)) as f:
        return json.load(f)


def save(name, data):
    with open(os.path.join(BASE, name), 'w') as f:
        json.dump(data, f, indent=2)  # same format as the generators, so diffs stay minimal


def rescore(books):
    n = 0
    for book_id, scores in RESCORED.items():
        if book_id in books:
            books[book_id]['tensions'] = {
                tid: {'score': score, 'note': note} for tid, (score, note) in sorted(scores.items())
            }
            n += 1
    return n


def main():
    apoc = load('seed_data_apocrypha.json')
    print(f"Apocrypha: rescored {rescore(apoc['books'])} books")
    save('seed_data_apocrypha.json', apoc)

    ot = load('seed_data.json')
    print(f"Hebrew Bible: rescored {rescore(ot['books'])} book(s)")
    # Joshua's herem is the anchor: exclusivism must be positive once fixed
    if ot['books']['JOS']['tensions']['T02']['score'] < 0:
        flipped = 0
        for book_id, book in ot['books'].items():
            t02 = book['tensions'].get('T02')
            if book_id not in RESCORED and isinstance(t02, dict) and t02.get('score') is not None:
                t02['score'] = -t02['score']
                flipped += 1
        print(f"Hebrew Bible: flipped T02 on {flipped} books")
    else:
        print('Hebrew Bible: T02 already in the app\'s direction')
    save('seed_data.json', ot)


if __name__ == '__main__':
    main()
