"""
Live chapter analysis via the Anthropic API.
Called from the POST /api/analyze/<book_id>/<chapter> route.
"""
import json
import anthropic
from models import db, Tension, ConductCategory, ChapterAnalysis, ChapterTension, ChapterConduct

MODEL = 'claude-sonnet-4-6'

SYSTEM_PROMPT_TEMPLATE = """You are a biblical scholar performing thematic analysis from an academic, \
secular, sociological and anthropological perspective. You are NOT devotional. \
Treat the text as literature, historical document, and cultural artifact.

Analyze the given chapter. For each applicable tension, score from -5 to +5 where the \
negative pole (A) and positive pole (B) are defined below. Use null if the tension is \
not relevant to this chapter.

TENSIONS:
{tensions}

For each applicable conduct category, briefly describe what this chapter prescribes, \
permits, or prohibits. Omit categories with no relevant content.

CONDUCT CATEGORIES:
{categories}

Respond ONLY with valid JSON in this exact structure:
{{
  "tensions": {{"T01": {{"score": <integer or null>, "note": "<1-2 sentences>"}}, ...}},
  "conduct": {{"diet": "<description>", ...}},
  "summary": "<2-3 sentence academic summary of the chapter>"
}}"""


def build_system_prompt():
    tensions = Tension.query.order_by(Tension.sort_order).all()
    categories = ConductCategory.query.order_by(ConductCategory.sort_order).all()

    tension_lines = '\n'.join(
        f'  {t.id} — {t.name}: pole A (-5) = {t.pole_a}, pole B (+5) = {t.pole_b}'
        for t in tensions
    )
    category_lines = '\n'.join(
        f'  {c.id} — {c.label}'
        for c in categories
    )
    return SYSTEM_PROMPT_TEMPLATE.format(
        tensions=tension_lines,
        categories=category_lines,
    )


def analyze_chapter(book_id: str, chapter: int, book_name: str) -> dict:
    """
    Call the Anthropic API to analyze a chapter.
    Returns the parsed analysis dict.
    Stores results in chapter_analyses / chapter_tensions / chapter_conduct.
    """
    client = anthropic.Anthropic()
    system = build_system_prompt()
    user_message = f'Analyze {book_name} chapter {chapter} from the Hebrew Bible / Old Testament.'

    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system,
        messages=[{'role': 'user', 'content': user_message}],
    )

    raw = message.content[0].text.strip()
    # Strip markdown code fences if Claude wrapped the JSON anyway
    if raw.startswith('```'):
        raw = raw.split('\n', 1)[-1]
        raw = raw.rsplit('```', 1)[0].strip()
    analysis = json.loads(raw)

    # Persist
    ca = ChapterAnalysis(
        book_id=book_id,
        chapter=chapter,
        summary=analysis.get('summary'),
        raw_json=raw,
    )
    db.session.add(ca)
    db.session.flush()

    for tension_id, t_data in analysis.get('tensions', {}).items():
        db.session.add(ChapterTension(
            chapter_analysis_id=ca.id,
            tension_id=tension_id,
            score=t_data.get('score'),
            note=t_data.get('note'),
        ))

    for cat_id, description in analysis.get('conduct', {}).items():
        if description:
            db.session.add(ChapterConduct(
                chapter_analysis_id=ca.id,
                category_id=cat_id,
                description=description,
            ))

    db.session.commit()
    return {'id': ca.id, 'summary': ca.summary, **analysis}
