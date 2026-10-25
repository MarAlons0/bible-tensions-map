"""
Fetch the World English Bible (public domain) text for every reference in
parallels.py and sayings.py from bible-api.com and save it to
seed_data_bible_texts.json.

Run after editing either file:  python fetch_bible_texts.py
Already-fetched references are reused; the API allows ~15 requests per 30 s.
"""
import json
import os
import time
import urllib.parse
import urllib.request

from parallels import PARALLELS
from sayings import SAYINGS

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'seed_data_bible_texts.json')
API = 'https://bible-api.com/{}?translation=web'


def fetch(ref):
    url = API.format(urllib.parse.quote(ref))
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.load(resp)
    if 'verses' not in data:
        raise RuntimeError(f'{ref}: {data.get("error", "no verses")}')
    return {
        'reference': data['reference'],
        'verses': [[v['chapter'], v['verse'], ' '.join(v['text'].split())] for v in data['verses']],
    }


def main():
    cache = {}
    if os.path.exists(OUT):
        with open(OUT) as f:
            cache = json.load(f)['texts']

    refs = {r.strip() for p in PARALLELS for ref, _ in p['passages'] for r in ref.split(';')}
    refs = sorted(refs | {s['ref'] for s in SAYINGS if s['ref']})
    todo = [r for r in refs if r not in cache]
    print(f'{len(refs)} references, {len(todo)} to fetch')
    for i, ref in enumerate(todo, 1):
        cache[ref] = fetch(ref)
        print(f'  [{i}/{len(todo)}] {ref}: {len(cache[ref]["verses"])} verses')
        time.sleep(2.2)

    texts = {r: cache[r] for r in refs}  # drop references no longer used
    with open(OUT, 'w') as f:
        json.dump({'translation': 'World English Bible (public domain)', 'texts': texts}, f, indent=1)
    print(f'Saved {OUT}')


if __name__ == '__main__':
    main()
