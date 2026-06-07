from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association tables for Many-to-Many relationships
article_category_link = db.Table(
    "article_category_link",
    db.Column("article_id", db.Integer, db.ForeignKey("articles.id"), primary_key=True),
    db.Column(
        "category_id", db.Integer, db.ForeignKey("categories.id"), primary_key=True
    ),
)

article_brand_link = db.Table(
    "article_brand_link",
    db.Column("article_id", db.Integer, db.ForeignKey("articles.id"), primary_key=True),
    db.Column("brand_id", db.Integer, db.ForeignKey("brands.id"), primary_key=True),
)


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
    affiliate_link = db.Column(db.String(255))

    # Relationships
    target_categories = db.relationship(
        "Category",
        secondary=article_category_link,
        lazy="subquery",
        backref=db.backref("articles", lazy=True),
    )
    target_brands = db.relationship(
        "Brand",
        secondary=article_brand_link,
        lazy="subquery",
        backref=db.backref("articles", lazy=True),
    )
