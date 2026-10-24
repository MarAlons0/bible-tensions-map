"""
Meta-analysis of my reading journal via the Anthropic API.

Sends every point I raised while reading (with Claude's short replies), my closing
observations, the traced themes, and the app's tension scores for the books I
commented on, and asks Claude for a structured synthesis of my thinking.

Runs in a background thread (a single call can take several minutes, longer than
gunicorn's request timeout); the /journal page polls until it's done.
"""
import json
import threading
from collections import defaultdict

import anthropic

from models import (
    db, Book, Tension, BookTension, UserNote, JournalEntry, MetaAnalysis,
)

MODEL = 'claude-opus-5-5'

SYSTEM_PROMPT = """You are a scholar of the Bible as literature and history, writing a candid \
meta-analysis of one reader's journal. The reader has just finished the whole Bible \
(Hebrew Bible, Apocrypha, New Testament) in the New Oxford Annotated Bible, reading it from a \
secular, literary-historical stance, not a devotional one. While reading they kept a dialog \
with an AI assistant; you receive the points they raised in their own words, the assistant's \
short replies, their closing observations, a table of themes traced across the canon, and the \
reading app's own tension scores for the books they commented on.

Your subject is the reader's thinking, not the Bible. Address the reader as "you". \
Be specific: cite their actual points and the books or verses they were reading. Be honest \
rather than flattering: say where their reading is sharp and well supported, and also where \
it is contestable, where scholars would push back, or where a stronger form of their argument \
exists. Don't invent points they didn't make.

Comparing with the tension scores: each tension runs from pole A (-5) to pole B (+5). Look for \
books where the reader's observations agree with, sharpen, or cut against where the app places \
that book, and say what each comparison shows. Only use tensions and scores that appear in \
the data.

Write in plain prose. You may use **bold** and *italics*; no other markdown, no headings."""

OUTPUT_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'required': ['overview', 'lines_of_questioning', 'evolution', 'against_the_scores',
                 'conclusions_assessed', 'dialog_dynamics', 'open_threads', 'closing'],
    'properties': {
        'overview': {
            'type': 'string',
            'description': 'Two or three paragraphs: what kind of reader this journal shows and what they kept looking for.',
        },
        'lines_of_questioning': {
            'type': 'array',
            'description': 'The 5-8 recurring moves or preoccupations in the reader\'s questions.',
            'items': {
                'type': 'object', 'additionalProperties': False,
                'required': ['title', 'analysis', 'books'],
                'properties': {
                    'title': {'type': 'string'},
                    'analysis': {'type': 'string'},
                    'books': {'type': 'array', 'items': {'type': 'string'},
                              'description': 'Book names where this shows up.'},
                },
            },
        },
        'evolution': {
            'type': 'string',
            'description': 'How the reader\'s questions and stance changed from the Pentateuch through the Apocrypha to the New Testament.',
        },
        'against_the_scores': {
            'type': 'array',
            'description': '5-10 comparisons between the reader\'s observations and the app\'s tension scores.',
            'items': {
                'type': 'object', 'additionalProperties': False,
                'required': ['book', 'tension', 'score', 'verdict', 'comment'],
                'properties': {
                    'book': {'type': 'string'},
                    'tension': {'type': 'string', 'description': 'Tension name as given in the data.'},
                    'score': {'type': ['integer', 'null']},
                    'verdict': {'type': 'string', 'enum': ['agrees', 'sharpens', 'challenges']},
                    'comment': {'type': 'string'},
                },
            },
        },
        'conclusions_assessed': {
            'type': 'array',
            'description': 'One entry per closing observation of the reader, in order.',
            'items': {
                'type': 'object', 'additionalProperties': False,
                'required': ['observation', 'assessment'],
                'properties': {
                    'observation': {'type': 'string'},
                    'assessment': {'type': 'string'},
                },
            },
        },
        'dialog_dynamics': {
            'type': 'string',
            'description': 'How the exchange with the assistant went: where the reader pushed back and was right, where the assistant corrected them, what that suggests.',
        },
        'open_threads': {
            'type': 'array',
            'description': '4-6 specific next readings or questions worth pursuing, each one or two sentences.',
            'items': {'type': 'string'},
        },
        'closing': {'type': 'string', 'description': 'One short closing paragraph.'},
    },
}


def build_input():
    """Everything the model sees, as one plain-text document (stable order for caching)."""
    books = {b.id: b for b in Book.query.all()}
    entries = JournalEntry.query.order_by(JournalEntry.sort_order).all()
    lines = ['# MY CLOSING OBSERVATIONS (my words)']

    notes = UserNote.query.filter(UserNote.source != 'reading-notes').order_by(UserNote.id).all()
    seen, by_heading = set(), defaultdict(list)
    for n in notes:
        if (n.heading, n.note) in seen:   # multi-book notes are stored once per book
            continue
        seen.add((n.heading, n.note))
        by_heading[n.heading or 'Notes typed in the app'].append(n)
    for n in by_heading.pop('Overall final observations', []):
        lines.append(f"- [{n.speaker or 'me'}] {n.note}")

    lines += ['', '# THEMES TRACED ACROSS THE CANON (summary of our dialog)']
    lines += [f'- {e.title}: {e.body}' for e in entries if e.kind == 'theme']

    lines += ['', '# MY POINTS, BOOK BY BOOK ([me] = my words, [claude] = the assistant\'s reply)']
    for heading, items in by_heading.items():
        lines += ['', f'## {heading}']
        lines += [f"- [{n.speaker or 'me'}] {n.note}" for n in items]

    commented = [books[b] for b in {n.book_id for n in notes if n.book_id in books}]
    commented.sort(key=lambda b: b.sort_order)
    tensions = Tension.query.order_by(Tension.sort_order).all()
    scores = defaultdict(dict)
    for bt in BookTension.query.filter(BookTension.book_id.in_([b.id for b in commented])):
        scores[bt.book_id][bt.tension_id] = bt

    lines += ['', '# THE APP\'S TENSIONS (score -5 = pole A, +5 = pole B)']
    lines += [f'- {t.id} {t.name}: A = {t.pole_a}; B = {t.pole_b}' for t in tensions]
    lines += ['', '# THE APP\'S SCORES FOR THE BOOKS I COMMENTED ON']
    for b in commented:
        lines += ['', f'## {b.name} ({b.section}; {b.dating or "date n/a"})']
        for t in tensions:
            bt = scores[b.id].get(t.id)
            if bt and bt.score is not None:
                lines.append(f'- {t.id} {t.name}: {bt.score:+d}' + (f' — {bt.note}' if bt.note else ''))
    return '\n'.join(lines)


def run(app, analysis_id):
    """Background job: call Claude and store the result on the MetaAnalysis row."""
    with app.app_context():
        ma = db.session.get(MetaAnalysis, analysis_id)
        try:
            client = anthropic.Anthropic()
            with client.beta.messages.stream(
                model=MODEL,
                max_tokens=64000,
                thinking={'type': 'adaptive'},
                output_config={
                    'effort': 'high',
                    'format': {'type': 'json_schema', 'schema': OUTPUT_SCHEMA},
                },
                # If a safety classifier declines, retry server-side on a fallback model
                betas=['server-side-fallback-2026-07-01'],
                fallbacks='default',
                system=SYSTEM_PROMPT,
                messages=[{'role': 'user', 'content': build_input()}],
            ) as stream:
                message = stream.get_final_message()

            if message.stop_reason == 'refusal':
                raise RuntimeError('Claude declined to produce the analysis.')
            if message.stop_reason == 'max_tokens':
                raise RuntimeError('The analysis was cut off (output limit reached).')
            text = next(b.text for b in message.content if b.type == 'text')
            json.loads(text)  # validate before storing
            ma.result_json = text
            ma.model = message.model
            ma.input_tokens = message.usage.input_tokens
            ma.output_tokens = message.usage.output_tokens
            ma.status = 'done'
        except anthropic.AuthenticationError:
            ma.status, ma.error = 'error', 'API key is invalid (check ANTHROPIC_API_KEY).'
        except anthropic.RateLimitError:
            ma.status, ma.error = 'error', 'Rate limited by the Anthropic API — try again in a minute.'
        except anthropic.APIStatusError as e:
            ma.status, ma.error = 'error', f'API error {e.status_code}: {e.message}'
        except anthropic.APIConnectionError:
            ma.status, ma.error = 'error', 'Could not reach the Anthropic API.'
        except Exception as e:
            ma.status, ma.error = 'error', str(e)
        db.session.commit()


def start(app):
    """Create a 'running' row and launch the job; returns the row."""
    ma = MetaAnalysis(status='running', model=MODEL)
    db.session.add(ma)
    db.session.commit()
    threading.Thread(target=run, args=(app, ma.id), daemon=True).start()
    return ma
