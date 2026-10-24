"""
Parse my reading dialog with Claude into seed_data_reading_notes.json, which
seed.py loads into the database. Two inputs:
  docs/reading-notes.md      — Claude's summary: conclusions, themes, per-book takeaways
  docs/my-points-by-book.md  — my own points per book ([me]), with Claude's short replies ([claude])

Run after editing either file:  python import_reading_notes.py
Then deploy (or run `python seed.py` locally) to load them.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'docs', 'reading-notes.md')
POINTS_SRC = os.path.join(BASE, 'docs', 'my-points-by-book.md')
OUT = os.path.join(BASE, 'seed_data_reading_notes.json')
SOURCE = 'reading-notes'
POINTS_SOURCE = 'my-points'
OWN_CONCLUSIONS = 'Overall final observations'

# Recap headings that don't map 1:1 to a single book name
HEADING_BOOKS = {
    'Joshua and Judges': ['JOS', 'JDG'],
    '1-2 Samuel': ['1SA', '2SA'],
    '1-2 Kings': ['1KI', '2KI'],
    '1-2 Chronicles': ['1CH', '2CH'],
    'Ezra-Nehemiah': ['EZR', 'NEH'],
    'Song of Songs': ['SNG'],
    'Zephaniah and the prophets on Moab': ['ZEP'],
    'Baruch and the Letter of Jeremiah': ['BAR', 'LJE'],
    '4 Maccabees': [],  # not in the book table; kept as a journal-only note
    'General (not tied to one book)': [],
    OWN_CONCLUSIONS: [],
    'Luke and John': ['LUK', 'JHN'],
    '1-2 Corinthians': ['1CO', '2CO'],
    'Colossians, Ephesians, 1 Timothy, Titus': ['COL', 'EPH', '1TI', 'TIT'],
    'James, 1-2 Peter, 1 John': ['JAS', '1PE', '2PE', '1JN'],
    'Other topics': [],
}

# Names/abbreviations used in references -> book id
ALIASES = {
    'Genesis': 'GEN', 'Gen': 'GEN', 'Exodus': 'EXO', 'Exod': 'EXO',
    'Leviticus': 'LEV', 'Lev': 'LEV', 'Numbers': 'NUM', 'Num': 'NUM',
    'Deuteronomy': 'DEU', 'Deut': 'DEU', 'Joshua': 'JOS', 'Judges': 'JDG',
    '1 Samuel': '1SA', '1 Sam': '1SA', '2 Samuel': '2SA', '2 Sam': '2SA',
    '1 Kings': '1KI', '2 Kings': '2KI',
    '1 Chronicles': '1CH', '1 Chron': '1CH', '2 Chronicles': '2CH', '2 Chron': '2CH',
    'Ezra': 'EZR', 'Nehemiah': 'NEH', 'Job': 'JOB',
    'Psalms': 'PSA', 'Psalm': 'PSA', 'Ps': 'PSA', 'Proverbs': 'PRO', 'Prov': 'PRO',
    'Ecclesiastes': 'ECC', 'Eccl': 'ECC', 'Isaiah': 'ISA', 'Isa': 'ISA',
    'Ezekiel': 'EZK', 'Ezek': 'EZK', 'Daniel': 'DAN', 'Dan': 'DAN',
    'Hosea': 'HOS', 'Zephaniah': 'ZEP', 'Malachi': 'MAL', 'Wisdom': 'WIS', 'Tobit': 'TOB', 'Sirach': 'SIR',
    'Baruch': 'BAR', 'Letter of Jeremiah': 'LJE', '1 Maccabees': '1MA', '2 Maccabees': '2MA',
    '2 Esdras': '2ES', 'Matthew': 'MAT', 'Matt': 'MAT', 'Mark': 'MRK',
    'Luke': 'LUK', 'John': 'JHN', 'Acts': 'ACT', 'Romans': 'ROM', 'Rom': 'ROM',
    '1 Corinthians': '1CO', '1 Cor': '1CO', '2 Corinthians': '2CO', '2 Cor': '2CO',
    'Galatians': 'GAL', 'Ephesians': 'EPH', 'Colossians': 'COL',
    '1 Timothy': '1TI', '1 Tim': '1TI', 'Titus': 'TIT', 'Hebrews': 'HEB', 'Heb': 'HEB',
    'James': 'JAS', '1 Peter': '1PE', '1 Pet': '1PE', '2 Peter': '2PE', '2 Pet': '2PE',
    '1 John': '1JN', 'Revelation': 'REV', 'Rev': 'REV',
}
# Longest first so "1 John" wins over "John"
_ALIAS_RE = '|'.join(re.escape(a) for a in sorted(ALIASES, key=len, reverse=True))
NAMED_REF = re.compile(rf'(?<![\w])({_ALIAS_RE})\b(?:\s+(\d+))?')
BARE_REF = re.compile(
    r'\((?:ch\.\s*)?(\d+)(?=[:,)\-])|\b(\d+):\d+|\b(?:ch\.|chapter)\s*(\d+)', re.I)


def book_and_chapter(text, candidates):
    """Pick which of the heading's books a bullet is about, and its chapter."""
    named = [(m.start(), ALIASES[m.group(1)], m.group(2)) for m in NAMED_REF.finditer(text)]
    in_group = [(pos, b, c) for pos, b, c in named if b in candidates]
    if len(candidates) > 1:
        books = list(dict.fromkeys(b for _, b, _ in in_group)) or candidates
    else:
        books = candidates
    if len(books) != 1:
        return books, None
    # Earliest reference to this book wins: a named one ("Mark 7"), or a bare
    # "(20:12)" / "7:28" / "ch. 17" that isn't the tail of another book's name.
    refs = [(pos, int(c)) for pos, b, c in in_group if b == books[0] and c]
    masked = NAMED_REF.sub(lambda m: ' ' * len(m.group(0)), text)
    refs += [(m.start(), int(next(g for g in m.groups() if g)))
             for m in BARE_REF.finditer(masked)]
    return books, min(refs)[1] if refs else None


def parse(md):
    data = {'source': SOURCE, 'intro': '', 'conclusions': [], 'themes': [],
            'notes': [], 'open_questions': []}
    part = section = heading = None
    concl = None
    for raw in md.splitlines():
        line = raw.rstrip()
        if line.startswith('## Part'):
            part = int(re.search(r'Part (\d)', line).group(1))
            continue
        if part is None:
            if line.startswith('*') and not data['intro']:
                data['intro'] = line.strip('*').strip()
            continue
        if part == 1:
            m = re.match(r'\*\*\d\. (.+?)\*\*$', line)
            if m:
                concl = {'title': m.group(1).strip('"“”'), 'body': ''}
                data['conclusions'].append(concl)
            elif line.startswith('###'):
                concl = None
            elif concl is not None and line:
                concl['body'] = (concl['body'] + ' ' + line).strip()
            elif line.startswith('| **'):
                cells = [c.strip() for c in line.strip('|').split('|')]
                data['themes'].append({'theme': cells[0].strip('*'), 'trajectory': cells[1]})
        elif part == 2:
            if line.startswith('### '):
                section = line[4:].strip()
                if section == 'Other topics':
                    heading = section
            elif line.startswith('**'):
                # e.g. "**Colossians, Ephesians, 1 Timothy, Titus** (disputed or later)"
                heading = re.match(r'\*\*(.+?)\*\*', line).group(1)
            elif line.startswith('- ') and heading:
                data['notes'].append(bullet(heading, line[2:].strip()))
        elif part == 4 and line.startswith('- '):
            data['open_questions'].append(line[2:].strip())
        # Part 3 (corrections) is already reflected in the Part 2 text.
    return data


def bullet(heading, text):
    candidates = HEADING_BOOKS.get(heading)
    if candidates is None:
        if heading not in ALIASES:
            raise SystemExit(f'Unknown heading "{heading}": add it to ALIASES or HEADING_BOOKS')
        candidates = [ALIASES[heading]]
    books, chapter = book_and_chapter(text, candidates) if candidates else ([], None)
    return {'heading': heading, 'books': books, 'chapter': chapter, 'note': text}


def parse_points(md):
    """My points file: **Book** headings, then `- [me] …` / `- [claude] …` bullets."""
    points, heading = [], None
    for line in md.splitlines():
        if line.startswith('**'):
            heading = re.match(r'\*\*(.+?)\*\*', line).group(1)
        elif heading and (m := re.match(r'- \[(me|claude)\]\s*(.+)', line)):
            p = bullet(heading, m.group(2).strip())
            p['speaker'] = m.group(1)
            if p['speaker'] == 'claude' and points and points[-1]['heading'] == heading:
                # A reply belongs with the point it answers
                p['books'], p['chapter'] = points[-1]['books'], points[-1]['chapter']
            points.append(p)
    return points


if __name__ == '__main__':
    with open(SRC) as f:
        data = parse(f.read())
    data['points_source'] = POINTS_SOURCE
    data['own_conclusions_heading'] = OWN_CONCLUSIONS
    with open(POINTS_SRC) as f:
        data['points'] = parse_points(f.read())
    with open(OUT, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    mine = sum(p['speaker'] == 'me' for p in data['points'])
    print(f"{mine} of my points (+{len(data['points']) - mine} Claude replies), "
          f"{len(data['notes'])} summary notes, {len(data['conclusions'])} conclusions, "
          f"{len(data['themes'])} themes, {len(data['open_questions'])} open questions -> {OUT}")
