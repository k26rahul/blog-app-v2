from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)


class Brand(db.Model):
    __tablename__ = "brands"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)


class Article(db.Model):
    __tablename__ = "articles"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'))

    category = db.relationship("Category", backref=db.backref("articles", lazy=True))
    brand = db.relationship("Brand", backref=db.backref("articles", lazy=True))
