from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Tension(db.Model):
    __tablename__ = 'tensions'
    id = db.Column(db.String(3), primary_key=True)   # T01–T20
    name = db.Column(db.Text, nullable=False)
    pole_a = db.Column(db.Text, nullable=False)
    pole_b = db.Column(db.Text, nullable=False)
    sort_order = db.Column(db.Integer)


class ConductCategory(db.Model):
    __tablename__ = 'conduct_categories'
    id = db.Column(db.String(50), primary_key=True)
    label = db.Column(db.Text, nullable=False)
    sort_order = db.Column(db.Integer)


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.String(10), primary_key=True)  # GEN, EXO, …
    name = db.Column(db.Text, nullable=False)
    testament = db.Column(db.Text)                   # 'Old Testament' / 'New Testament'
    section = db.Column(db.Text)                     # Pentateuch, Historical Books, …
    chapters = db.Column(db.Integer)
    sort_order = db.Column(db.Integer)
    dating = db.Column(db.Text)
    sources = db.Column(db.Text)
    summary = db.Column(db.Text)


class BookTension(db.Model):
    __tablename__ = 'book_tensions'
    book_id = db.Column(db.String(10), db.ForeignKey('books.id'), primary_key=True)
    tension_id = db.Column(db.String(3), db.ForeignKey('tensions.id'), primary_key=True)
    score = db.Column(db.Integer)   # -5 to +5, nullable if not applicable
    note = db.Column(db.Text)


class BookConduct(db.Model):
    __tablename__ = 'book_conduct'
    book_id = db.Column(db.String(10), db.ForeignKey('books.id'), primary_key=True)
    category_id = db.Column(db.String(50), db.ForeignKey('conduct_categories.id'), primary_key=True)
    description = db.Column(db.Text)


class ChapterAnalysis(db.Model):
    __tablename__ = 'chapter_analyses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.String(10), db.ForeignKey('books.id'))
    chapter = db.Column(db.Integer)
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)
    summary = db.Column(db.Text)
    raw_json = db.Column(db.Text)


class ChapterTension(db.Model):
    __tablename__ = 'chapter_tensions'
    chapter_analysis_id = db.Column(db.Integer, db.ForeignKey('chapter_analyses.id'), primary_key=True)
    tension_id = db.Column(db.String(3), db.ForeignKey('tensions.id'), primary_key=True)
    score = db.Column(db.Integer)
    note = db.Column(db.Text)


class ChapterConduct(db.Model):
    __tablename__ = 'chapter_conduct'
    chapter_analysis_id = db.Column(db.Integer, db.ForeignKey('chapter_analyses.id'), primary_key=True)
    category_id = db.Column(db.String(50), db.ForeignKey('conduct_categories.id'), primary_key=True)
    description = db.Column(db.Text)


class UserNote(db.Model):
    __tablename__ = 'user_notes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.String(10), db.ForeignKey('books.id'))
    chapter = db.Column(db.Integer)          # null = book-level note
    tension_id = db.Column(db.String(3), db.ForeignKey('tensions.id'))  # null = general note
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
