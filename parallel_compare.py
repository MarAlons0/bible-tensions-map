"""
Claude comparison of one curated parallel passage set (parallels.py).

Runs in a background thread like meta_analysis.py; the parallel's page polls
until the result is stored on its ParallelComparison row.
"""
import json
import threading

import anthropic

from models import db, ParallelComparison
from parallels import PARALLELS_BY_ID

MODEL = 'claude-opus-5-5'

SYSTEM_PROMPT = """You are a scholar of the Bible as literature and history, writing for a \
secular reader who has just read the whole Bible (NRSV) and is interested in how its parallel \
accounts differ, why, and how believers and scholars deal with that. Not devotional.

You receive one set of parallel passages (in the World English Bible), the question that frames \
the discrepancy, and a curated note. Compare the passages closely: what each version adds, omits \
or changes, what that suggests about each author's or editor's purpose and date, how traditional \
readers have harmonized the difference and whether the harmonization holds up, and the mainstream \
critical explanation. Cite verses. Be concise and concrete; say so when a difference is trivial or \
a likely copying error rather than inflating it.

Write in plain prose. You may use **bold** and *italics*; no other markdown, no headings."""

OUTPUT_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'required': ['summary', 'differences', 'agendas', 'harmonizations', 'critical_view'],
    'properties': {
        'summary': {'type': 'string', 'description': 'Two or three sentences: the heart of the discrepancy.'},
        'differences': {
            'type': 'array',
            'description': '3-6 concrete differences between the versions, most significant first.',
            'items': {
                'type': 'object', 'additionalProperties': False,
                'required': ['title', 'detail'],
                'properties': {'title': {'type': 'string'}, 'detail': {'type': 'string'}},
            },
        },
        'agendas': {
            'type': 'array',
            'description': 'One entry per passage: what its version suggests about its author or editor.',
            'items': {
                'type': 'object', 'additionalProperties': False,
                'required': ['passage', 'agenda'],
                'properties': {'passage': {'type': 'string'}, 'agenda': {'type': 'string'}},
            },
        },
        'harmonizations': {'type': 'string', 'description': 'How traditional readers reconcile the versions, and whether that works.'},
        'critical_view': {'type': 'string', 'description': 'The mainstream historical-critical explanation.'},
    },
}


def build_input(parallel, texts):
    lines = [f"QUESTION: {parallel['question']}", f"CURATED NOTE: {parallel['note']}", '']
    for ref, says in parallel['passages']:
        lines += [f'## {ref}', f'(Curated summary: {says})']
        for part in ref.split(';'):
            for ch, v, text in texts[part.strip()]['verses']:
                lines.append(f'{ch}:{v} {text}')
        lines.append('')
    return '\n'.join(lines)


def run(app, comparison_id, texts):
    with app.app_context():
        pc = db.session.get(ParallelComparison, comparison_id)
        try:
            client = anthropic.Anthropic()
            with client.beta.messages.stream(
                model=MODEL,
                max_tokens=32000,
                thinking={'type': 'adaptive'},
                output_config={
                    'effort': 'medium',
                    'format': {'type': 'json_schema', 'schema': OUTPUT_SCHEMA},
                },
                betas=['server-side-fallback-2026-07-01'],
                fallbacks='default',
                system=SYSTEM_PROMPT,
                messages=[{'role': 'user', 'content': build_input(PARALLELS_BY_ID[pc.parallel_id], texts)}],
            ) as stream:
                message = stream.get_final_message()

            if message.stop_reason == 'refusal':
                raise RuntimeError('Claude declined to produce the comparison.')
            if message.stop_reason == 'max_tokens':
                raise RuntimeError('The comparison was cut off (output limit reached).')
            text = next(b.text for b in message.content if b.type == 'text')
            json.loads(text)  # validate before storing
            pc.result_json, pc.model, pc.status = text, message.model, 'done'
        except anthropic.AuthenticationError:
            pc.status, pc.error = 'error', 'API key is invalid (check ANTHROPIC_API_KEY).'
        except anthropic.RateLimitError:
            pc.status, pc.error = 'error', 'Rate limited by the Anthropic API — try again in a minute.'
        except anthropic.APIStatusError as e:
            pc.status, pc.error = 'error', f'API error {e.status_code}: {e.message}'
        except anthropic.APIConnectionError:
            pc.status, pc.error = 'error', 'Could not reach the Anthropic API.'
        except Exception as e:
            pc.status, pc.error = 'error', str(e)
        db.session.commit()


def start(app, parallel_id, texts):
    pc = ParallelComparison(parallel_id=parallel_id, status='running', model=MODEL)
    db.session.add(pc)
    db.session.commit()
    threading.Thread(target=run, args=(app, pc.id, texts), daemon=True).start()
    return pc
