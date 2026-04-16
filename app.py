import os
import re
import json
from collections import Counter
from flask import Flask, render_template, request, jsonify, abort
from dotenv import load_dotenv
from models import (
    db, Tension, ConductCategory, Book, BookTension, BookConduct,
    ChapterAnalysis, ChapterTension, ChapterConduct, UserNote,
)

load_dotenv()


def create_app():
    app = Flask(__name__)

    # --- Database ---
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///bible_tensions.db')
    # Render provides postgres:// but SQLAlchemy requires postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret')
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,   # verify connection before use (handles Neon idle drops)
        'pool_recycle': 300,     # recycle connections every 5 min
    }

    db.init_app(app)
    return app


app = create_app()


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------

@app.route('/')
def dashboard():
    books = Book.query.order_by(Book.sort_order).all()
    tensions = Tension.query.order_by(Tension.sort_order).all()
    sections = sorted({b.section for b in books if b.section})
    return render_template('dashboard.html', books=books, tensions=tensions, sections=sections)


@app.route('/book/<book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    tensions = Tension.query.order_by(Tension.sort_order).all()
    categories = ConductCategory.query.order_by(ConductCategory.sort_order).all()

    # Pre-index scores and conduct for template use
    scores = {bt.tension_id: bt for bt in BookTension.query.filter_by(book_id=book_id)}
    conduct = {bc.category_id: bc.description for bc in BookConduct.query.filter_by(book_id=book_id)}

    # Which chapters have been analyzed?
    analyzed_chapters = {
        ca.chapter for ca in ChapterAnalysis.query.filter_by(book_id=book_id)
    }

    return render_template(
        'book_detail.html',
        book=book,
        tensions=tensions,
        categories=categories,
        scores=scores,
        conduct=conduct,
        analyzed_chapters=analyzed_chapters,
    )


@app.route('/book/<book_id>/chapter/<int:chapter>')
def chapter_view(book_id, chapter):
    book = Book.query.get_or_404(book_id)
    ca = ChapterAnalysis.query.filter_by(book_id=book_id, chapter=chapter).first()
    tensions = Tension.query.order_by(Tension.sort_order).all()
    categories = ConductCategory.query.order_by(ConductCategory.sort_order).all()

    chapter_tensions = {}
    chapter_conduct = {}
    if ca:
        chapter_tensions = {ct.tension_id: ct for ct in ChapterTension.query.filter_by(chapter_analysis_id=ca.id)}
        chapter_conduct = {cc.category_id: cc.description for cc in ChapterConduct.query.filter_by(chapter_analysis_id=ca.id)}

    return render_template(
        'chapter_view.html',
        book=book,
        chapter=chapter,
        ca=ca,
        tensions=tensions,
        categories=categories,
        chapter_tensions=chapter_tensions,
        chapter_conduct=chapter_conduct,
    )


@app.route('/biplot')
def biplot():
    tensions = Tension.query.order_by(Tension.sort_order).all()
    sections = [r[0] for r in db.session.query(Book.section).distinct().order_by(Book.section) if r[0]]
    return render_template('biplot.html', tensions=tensions, sections=sections)


@app.route('/conduct')
def conduct():
    categories = ConductCategory.query.order_by(ConductCategory.sort_order).all()
    return render_template('conduct.html', categories=categories)


@app.route('/timeline')
def timeline():
    books = Book.query.order_by(Book.sort_order).all()
    tensions = Tension.query.order_by(Tension.sort_order).all()
    return render_template('timeline.html', books=books, tensions=tensions,
                           date_estimates=DATE_ESTIMATES)


@app.route('/about')
def about():
    tensions = Tension.query.order_by(Tension.sort_order).all()
    return render_template('about.html', tensions=tensions)


@app.route('/wordcloud')
def wordcloud():
    books = Book.query.order_by(Book.sort_order).all()
    # Build section list grouped by testament for cascading dropdowns
    ot_sections  = sorted({b.section for b in books if b.testament == 'Old Testament' and b.section})
    ap_sections  = sorted({b.section for b in books if b.testament == 'Apocrypha'    and b.section})
    nt_sections  = sorted({b.section for b in books if b.testament == 'New Testament' and b.section})
    return render_template('wordcloud.html', books=books,
                           ot_sections=ot_sections, ap_sections=ap_sections,
                           nt_sections=nt_sections)


# ---------------------------------------------------------------------------
# API — reference data
# ---------------------------------------------------------------------------

@app.route('/api/books')
def api_books():
    books = Book.query.order_by(Book.sort_order).all()
    return jsonify([{
        'id': b.id, 'name': b.name, 'testament': b.testament,
        'section': b.section, 'chapters': b.chapters,
        'sort_order': b.sort_order, 'dating': b.dating,
        'sources': b.sources, 'summary': b.summary,
    } for b in books])


@app.route('/api/books/<book_id>')
def api_book(book_id):
    book = Book.query.get_or_404(book_id)
    tensions = {
        bt.tension_id: {'score': bt.score, 'note': bt.note}
        for bt in BookTension.query.filter_by(book_id=book_id)
    }
    conduct = {
        bc.category_id: bc.description
        for bc in BookConduct.query.filter_by(book_id=book_id)
    }
    return jsonify({
        'id': book.id, 'name': book.name, 'testament': book.testament,
        'section': book.section, 'chapters': book.chapters,
        'dating': book.dating, 'sources': book.sources, 'summary': book.summary,
        'tensions': tensions, 'conduct': conduct,
    })


@app.route('/api/tensions')
def api_tensions():
    tensions = Tension.query.order_by(Tension.sort_order).all()
    return jsonify([{
        'id': t.id, 'name': t.name, 'pole_a': t.pole_a, 'pole_b': t.pole_b,
    } for t in tensions])


@app.route('/api/tensions/<tension_id>/scores')
def api_tension_scores(tension_id):
    tension = Tension.query.get_or_404(tension_id)
    rows = (
        db.session.query(BookTension, Book)
        .join(Book, BookTension.book_id == Book.id)
        .filter(BookTension.tension_id == tension_id)
        .order_by(Book.sort_order)
        .all()
    )
    return jsonify({
        'tension': {'id': tension.id, 'name': tension.name, 'pole_a': tension.pole_a, 'pole_b': tension.pole_b},
        'scores': [{'book_id': bt.book_id, 'book_name': b.name, 'score': bt.score, 'note': bt.note} for bt, b in rows],
    })


# ---------------------------------------------------------------------------
# API — heatmap
# ---------------------------------------------------------------------------

@app.route('/api/heatmap')
def api_heatmap():
    book_filter = request.args.get('books')
    tension_filter = request.args.get('tensions')
    section_filter = request.args.get('section')

    book_query = Book.query.order_by(Book.sort_order)
    if book_filter:
        ids = book_filter.split(',')
        book_query = book_query.filter(Book.id.in_(ids))
    if section_filter and section_filter != 'All':
        book_query = book_query.filter(Book.section == section_filter)
    books = book_query.all()

    tension_query = Tension.query.order_by(Tension.sort_order)
    if tension_filter:
        ids = tension_filter.split(',')
        tension_query = tension_query.filter(Tension.id.in_(ids))
    tensions = tension_query.all()

    # Build score lookup: {(book_id, tension_id): (score, note)}
    all_scores = BookTension.query.all()
    score_map = {(bt.book_id, bt.tension_id): (bt.score, bt.note) for bt in all_scores}

    tension_ids = [t.id for t in tensions]
    z = []
    notes = []
    book_names = []

    for b in books:
        row_z = []
        row_notes = []
        for t in tensions:
            entry = score_map.get((b.id, t.id))
            if entry and entry[0] is not None:
                row_z.append(entry[0])
                row_notes.append(entry[1] or '')
            else:
                row_z.append(None)
                row_notes.append('')
        z.append(row_z)
        notes.append(row_notes)
        book_names.append(b.name)

    return jsonify({
        'books': [{'id': b.id, 'name': b.name, 'section': b.section} for b in books],
        'tensions': [{'id': t.id, 'name': t.name, 'pole_a': t.pole_a, 'pole_b': t.pole_b} for t in tensions],
        'z': z,
        'notes': notes,
    })


@app.route('/api/heatmap-full')
def api_heatmap_full():
    """Return all books with scores keyed by tension_id — used by the layered heatmap."""
    books = Book.query.order_by(Book.sort_order).all()
    tensions = Tension.query.order_by(Tension.sort_order).all()
    all_bt = BookTension.query.all()
    score_map = {(bt.book_id, bt.tension_id): (bt.score, bt.note) for bt in all_bt}

    books_data = []
    for b in books:
        scores = {}
        notes = {}
        for t in tensions:
            entry = score_map.get((b.id, t.id))
            scores[t.id] = entry[0] if entry and entry[0] is not None else None
            notes[t.id] = entry[1] if entry and entry[1] else ''
        books_data.append({
            'id': b.id, 'name': b.name,
            'testament': b.testament, 'section': b.section,
            'scores': scores, 'notes': notes,
        })

    return jsonify({
        'books': books_data,
        'tensions': [{'id': t.id, 'name': t.name, 'pole_a': t.pole_a, 'pole_b': t.pole_b} for t in tensions],
    })


# ---------------------------------------------------------------------------
# API — biplot
# ---------------------------------------------------------------------------

@app.route('/api/biplot')
def api_biplot():
    x_id = request.args.get('x', 'T01')
    y_id = request.args.get('y', 'T07')
    color_by = request.args.get('color', 'section')  # section | testament | dating

    tx = Tension.query.get_or_404(x_id)
    ty = Tension.query.get_or_404(y_id)

    books = Book.query.order_by(Book.sort_order).all()
    scores_x = {bt.book_id: (bt.score, bt.note) for bt in BookTension.query.filter_by(tension_id=x_id)}
    scores_y = {bt.book_id: (bt.score, bt.note) for bt in BookTension.query.filter_by(tension_id=y_id)}

    points = []
    for b in books:
        sx, nx = scores_x.get(b.id, (None, None))
        sy, ny = scores_y.get(b.id, (None, None))
        if sx is None or sy is None:
            continue
        points.append({
            'book_id': b.id,
            'book_name': b.name,
            'x': sx,
            'y': sy,
            'note_x': nx,
            'note_y': ny,
            'section': b.section,
            'testament': b.testament,
            'dating': b.dating,
            'color_val': getattr(b, color_by, b.section),
        })

    return jsonify({
        'x_tension': {'id': tx.id, 'name': tx.name, 'pole_a': tx.pole_a, 'pole_b': tx.pole_b},
        'y_tension': {'id': ty.id, 'name': ty.name, 'pole_a': ty.pole_a, 'pole_b': ty.pole_b},
        'color_by': color_by,
        'points': points,
    })


# ---------------------------------------------------------------------------
# API — conduct
# ---------------------------------------------------------------------------

@app.route('/api/conduct/<category_id>')
def api_conduct(category_id):
    cat = ConductCategory.query.get_or_404(category_id)
    rows = (
        db.session.query(BookConduct, Book)
        .join(Book, BookConduct.book_id == Book.id)
        .filter(BookConduct.category_id == category_id)
        .order_by(Book.sort_order)
        .all()
    )
    return jsonify({
        'category': {'id': cat.id, 'label': cat.label},
        'entries': [{'book_id': bc.book_id, 'book_name': b.name, 'section': b.section,
                     'dating': b.dating, 'description': bc.description} for bc, b in rows],
    })


# ---------------------------------------------------------------------------
# API — timeline chart
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Word cloud — text processing
# ---------------------------------------------------------------------------

_STOP_WORDS = {
    'the','a','an','and','or','but','in','on','at','to','for','of','with',
    'by','from','as','is','are','was','were','be','been','being','have',
    'has','had','do','does','did','will','would','could','should','may',
    'might','must','shall','can','not','no','nor','so','yet','than','then',
    'when','where','while','who','whom','whose','what','how','why','if',
    'although','though','since','because','whether','throughout','within',
    'between','among','through','during','before','after','above','below',
    'up','down','out','off','over','under','again','once','here','there',
    'all','each','every','other','another','such','same','first','second',
    'third','often','particularly','especially','rather','quite','very',
    'more','most','less','least','much','many','few','some','any','both',
    'either','neither','this','these','those','their','they','them','he',
    'she','it','we','you','his','her','its','our','your','i','me','my',
    'him','who','also','just','even','only','upon','into','about','which',
    'that','thus','hence','toward','towards','without','against','along',
    'around','across','behind','beyond','despite','except','inside','near',
    'outside','since','until','upon','within','become','becomes','became',
    'make','makes','made','take','takes','took','give','gives','given',
    'use','uses','used','see','seen','come','comes','came','go','goes',
    'went','include','includes','included','become','often','always',
    'never','still','already','now','then','here','there','away','back',
    'text','book','books','biblical','author','authors','one','two','three',
    'four','five','six','seven','eight','nine','ten','cf','eg','ie','vs',
    'reflect','reflects','reflected','represent','represents','suggest',
    'suggests','indicate','indicates','demonstrate','demonstrates','show',
    'shows','appear','appears','seem','seems','present','presents',
    'focus','focuses','establish','establishes','develop','develops',
    'provide','provides','emphasize','emphasizes','central','major','key',
    'primary','important','significant','strong','clear','explicit',
    'dominant','prominent','pervasive','later','early','however','overall',
}

# Map variants and near-synonyms to a single canonical form
_NORMALIZE = {
    # God / deity
    'lord':'god','lords':'god','yhwh':'god','divine':'god','deity':'god',
    'gods':'god','almighty':'god','heavenly':'god',
    # Prophet / prophecy
    'prophets':'prophet','prophecy':'prophet','prophetic':'prophet',
    'prophesied':'prophet','prophesy':'prophet','prophecies':'prophet',
    # Covenant
    'covenants':'covenant','treaty':'covenant',
    # Law / commandment
    'laws':'law','torah':'law','commandments':'commandment',
    'statutes':'law','ordinances':'law','precepts':'law','decrees':'law',
    # Sacrifice / offering
    'sacrifices':'sacrifice','offerings':'offering','sacrificial':'sacrifice',
    # King / ruler
    'kings':'king','ruler':'king','rulers':'king','kingship':'king',
    'royal':'king','monarch':'king','reign':'king','reigns':'king',
    'kingdom':'king','kingdoms':'king',
    # Temple / sanctuary
    'temples':'temple','sanctuary':'temple','tabernacle':'temple',
    'shrine':'temple','shrines':'temple','altar':'temple','altars':'temple',
    # Priest / Levite
    'priests':'priest','priestly':'priest','priesthood':'priest',
    'levite':'priest','levites':'priest','levitical':'priest',
    # Israel / people of God
    'israelites':'israel','israelite':'israel','hebrew':'israel',
    'hebrews':'israel','judah':'israel','judean':'israel','jewish':'israel',
    'zion':'israel','jerusalem':'israel',
    # Sin / evil
    'sins':'sin','sinful':'sin','sinner':'sin','sinners':'sin',
    'transgression':'sin','transgressions':'sin','wickedness':'sin',
    'iniquity':'sin','iniquities':'sin','evil':'sin','evils':'sin',
    'wicked':'sin','corruption':'sin','corrupt':'sin',
    # Righteousness / justice
    'justice':'righteousness','righteous':'righteousness',
    'just':'righteousness','judgment':'righteousness',
    'judgments':'righteousness',
    # Grace / mercy
    'mercy':'grace','compassion':'grace','lovingkindness':'grace',
    'kindness':'grace','steadfast':'grace','forgiveness':'grace',
    'forgive':'grace','forgives':'grace',
    # Redemption / salvation
    'salvation':'redemption','deliverance':'redemption','saved':'redemption',
    'redeem':'redemption','redeemed':'redemption','redeemer':'redemption',
    'rescue':'redemption','liberate':'redemption','liberation':'redemption',
    # Faith / trust
    'belief':'faith','trust':'faith','faithful':'faith',
    'faithfulness':'faith','obedience':'faith','obedient':'faith',
    # Wisdom / knowledge
    'wise':'wisdom','understanding':'wisdom','knowledge':'wisdom',
    'discernment':'wisdom','insight':'wisdom',
    # Resurrection / life after death
    'risen':'resurrection','raised':'resurrection','raise':'resurrection',
    # Apocalyptic
    'apocalypse':'apocalyptic','apocalypticism':'apocalyptic',
    # Nation / peoples
    'nations':'nation','peoples':'people','gentiles':'nation',
    'foreigners':'nation','outsiders':'nation',
    # War / violence
    'wars':'war','warfare':'war','military':'war','battle':'war',
    'battles':'war','warrior':'war','warriors':'war','violence':'war',
    'violent':'war','conquest':'war','conquer':'war',
    # Death
    'deaths':'death','dying':'death','dead':'death','die':'death',
    # Spirit / holy spirit
    'spirits':'spirit','spiritual':'spirit','holy':'spirit',
    # Blessing
    'blessings':'blessing','blessed':'blessing','bless':'blessing',
    # Curse / punishment
    'curses':'curse','cursed':'curse','punishment':'curse',
    'punish':'curse','punishes':'curse','wrath':'curse',
    # Suffering / affliction
    'suffer':'suffering','suffers':'suffering','affliction':'suffering',
    'afflictions':'suffering','pain':'suffering','anguish':'suffering',
    'lament':'suffering','lamentation':'suffering',
    # Worship / prayer
    'worships':'worship','worshipped':'worship','worshipping':'worship',
    'prayers':'prayer','pray':'prayer','prays':'prayer','praying':'prayer',
    # Community / church
    'communities':'community','church':'community','congregation':'community',
    'assembly':'community',
    # Love
    'loves':'love','loved':'love','loving':'love',
    # Mission / universalism
    'missionary':'mission','missions':'mission',
    # Eschatology
    'eschaton':'eschatology','eschatological':'eschatology',
    'endtimes':'eschatology','endtime':'eschatology',
    # Ethics / moral
    'ethical':'ethics','morality':'ethics','moral':'ethics',
}


def _process_text(text, max_words=80):
    words = re.findall(r"\b[a-z']{3,}\b", text.lower())
    normalized = []
    for w in words:
        w = _NORMALIZE.get(w, w)
        if w not in _STOP_WORDS and len(w) >= 3:
            normalized.append(w)
    counter = Counter(normalized)
    return [[word, count] for word, count in counter.most_common(max_words)]


@app.route('/api/wordcloud')
def api_wordcloud():
    testament = request.args.get('testament', '')
    section   = request.args.get('section', '')
    book_id   = request.args.get('book', '')

    query = Book.query
    if book_id:
        query = query.filter(Book.id == book_id)
    elif section:
        query = query.filter(Book.section == section)
    elif testament:
        query = query.filter(Book.testament == testament)
    books = query.all()

    chunks = []
    for b in books:
        if b.summary:
            chunks.append(b.summary)
        for bt in BookTension.query.filter_by(book_id=b.id).all():
            if bt.note:
                chunks.append(bt.note)
        for bc in BookConduct.query.filter_by(book_id=b.id).all():
            if bc.description:
                chunks.append(bc.description)

    words = _process_text(' '.join(chunks))
    return jsonify({'words': words, 'book_count': len(books)})


# ---------------------------------------------------------------------------
# Approximate scholarly date (year CE; BCE = negative) for chronological ordering.
# Composite midpoint estimates based on NOAB critical consensus.
DATE_ESTIMATES = {
    'AMO': -760, 'HOS': -750, 'MIC': -730, 'ISA': -720,
    'ZEP': -630, 'NAM': -625, 'HAB': -610, 'JER': -605,
    'DEU': -621, 'JOS': -610, 'JDG': -610, '1SA': -610, '2SA': -610,
    '1KI': -610, '2KI': -610,
    'GEN': -580, 'EXO': -570, 'NUM': -560,
    'LAM': -586, 'EZK': -590, 'OBA': -550, 'LEV': -540,
    'HAG': -520, 'ZEC': -518, 'MAL': -440,
    'JOB': -500, 'PRO': -480,
    'PSA': -450, 'RUT': -450, 'JOL': -450, 'JON': -430,
    '1CH': -400, '2CH': -400, 'EZR': -400, 'NEH': -445,
    'EST': -400, 'SNG': -400,
    'ECC': -250, 'DAN': -165,
    # Apocrypha (BCE/CE dates, NOAB NRSV scholarly consensus)
    'TOB': -200, 'JDT': -100, 'AES': -90,
    '1MA': -100, '2MA': -120,
    'WIS': -40,  'SIR': -180,
    'BAR': -150, 'LJE': -300,
    'PAZ': -100, 'SUS': -100, 'BEL': -100,
    '1ES': -150, 'MAN': -100, 'PS2': -150,
    '3MA': -75,  '2ES': 100,
    # New Testament (CE dates)
    'MRK': 70, 'MAT': 85, 'LUK': 85, 'JHN': 95,
    'ACT': 85,
    '1TH': 51, '2TH': 51, 'GAL': 55, '1CO': 55, '2CO': 56, 'ROM': 57,
    'PHP': 62, 'COL': 62, 'PHM': 62, 'EPH': 80,
    '1TI': 100, '2TI': 100, 'TIT': 100,
    'HEB': 80, 'JAS': 62, '1PE': 80, '2PE': 120,
    '1JN': 100, '2JN': 100, '3JN': 100, 'JUD': 90,
    'REV': 95,
}


@app.route('/api/timeline-chart')
def api_timeline_chart():
    tension_filter = request.args.get('tensions', '')
    order = request.args.get('order', 'scholarly')  # 'scholarly' | 'canonical'
    selected_ids = [t for t in tension_filter.split(',') if t] if tension_filter else None

    tension_query = Tension.query.order_by(Tension.sort_order)
    if selected_ids:
        tension_query = tension_query.filter(Tension.id.in_(selected_ids))
    tensions = tension_query.all()

    books = Book.query.order_by(Book.sort_order).all()
    if order == 'canonical':
        books_sorted = sorted(books, key=lambda b: b.sort_order)
    else:
        books_sorted = sorted(
            books,
            key=lambda b: (DATE_ESTIMATES.get(b.id, 9999), b.sort_order)
        )

    # Build score map
    all_scores = BookTension.query.all()
    score_map = {(bt.book_id, bt.tension_id): (bt.score, bt.note) for bt in all_scores}

    # One trace per tension — every book appears on x-axis; null where no score.
    # This ensures connectgaps:false draws a break rather than a cross-chart line.
    traces = []
    for t in tensions:
        xs, ys, notes = [], [], []
        for b in books_sorted:
            entry = score_map.get((b.id, t.id))
            xs.append(b.name)
            if entry and entry[0] is not None:
                ys.append(entry[0])
                notes.append(entry[1] or '')
            else:
                ys.append(None)
                notes.append('')
        traces.append({
            'tension_id': t.id,
            'tension_name': t.name,
            'pole_a': t.pole_a,
            'pole_b': t.pole_b,
            'x': xs,
            'y': ys,
            'notes': notes,
        })

    return jsonify({'traces': traces})


# ---------------------------------------------------------------------------
# API — chapter analysis
# ---------------------------------------------------------------------------

@app.route('/api/analyze/<book_id>/<int:chapter>', methods=['POST'])
def api_analyze(book_id, chapter):
    book = Book.query.get_or_404(book_id)

    # Return cached result if available
    ca = ChapterAnalysis.query.filter_by(book_id=book_id, chapter=chapter).first()
    if ca:
        tensions = {ct.tension_id: {'score': ct.score, 'note': ct.note}
                    for ct in ChapterTension.query.filter_by(chapter_analysis_id=ca.id)}
        conduct = {cc.category_id: cc.description
                   for cc in ChapterConduct.query.filter_by(chapter_analysis_id=ca.id)}
        return jsonify({'cached': True, 'id': ca.id, 'summary': ca.summary,
                        'tensions': tensions, 'conduct': conduct})

    # Live analysis
    try:
        from analyze import analyze_chapter
        result = analyze_chapter(book_id, chapter, book.name)
        return jsonify({'cached': False, **result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chapter/<book_id>/<int:chapter>')
def api_chapter(book_id, chapter):
    ca = ChapterAnalysis.query.filter_by(book_id=book_id, chapter=chapter).first()
    if not ca:
        return jsonify(None)
    tensions = {ct.tension_id: {'score': ct.score, 'note': ct.note}
                for ct in ChapterTension.query.filter_by(chapter_analysis_id=ca.id)}
    conduct = {cc.category_id: cc.description
               for cc in ChapterConduct.query.filter_by(chapter_analysis_id=ca.id)}
    return jsonify({'id': ca.id, 'summary': ca.summary,
                    'analyzed_at': ca.analyzed_at.isoformat(),
                    'tensions': tensions, 'conduct': conduct})


# ---------------------------------------------------------------------------
# API — user notes
# ---------------------------------------------------------------------------

@app.route('/api/notes', methods=['GET', 'POST'])
def api_notes():
    if request.method == 'POST':
        data = request.get_json()
        note = UserNote(
            book_id=data.get('book_id'),
            chapter=data.get('chapter'),
            tension_id=data.get('tension_id'),
            note=data.get('note', ''),
        )
        db.session.add(note)
        db.session.commit()
        return jsonify({'id': note.id}), 201

    book_id = request.args.get('book')
    chapter = request.args.get('chapter', type=int)
    query = UserNote.query.filter_by(book_id=book_id)
    if chapter is not None:
        query = query.filter_by(chapter=chapter)
    notes = query.order_by(UserNote.created_at.desc()).all()
    return jsonify([{
        'id': n.id, 'book_id': n.book_id, 'chapter': n.chapter,
        'tension_id': n.tension_id, 'note': n.note,
        'created_at': n.created_at.isoformat(),
    } for n in notes])


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
