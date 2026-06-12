from flask import Flask, send_from_directory, jsonify
from models import db, Article
from populate_db import populate_db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lifestyle.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    populate_db(db)


@app.route("/")
def index():
    return send_from_directory("templates", "index.html")


@app.route("/post/<slug>")
def post(slug):
    return send_from_directory("templates", "post.html")


@app.route("/api/articles")
def api_articles():
    articles = Article.query.all()
    articles_data = []
    for a in articles:
        articles_data.append(
            {
                "slug": a.slug,
                "title": a.title,
                "category": a.category.name,
                "brand": a.brand.name,
            }
        )
    return jsonify(articles_data)


@app.route("/api/articles/<slug>")
def api_article(slug):
    a = Article.query.filter_by(slug=slug).first_or_404()
    return jsonify({
        "slug": a.slug,
        "title": a.title,
        "content": a.content,
        "category": a.category.name,
        "brand": a.brand.name,
    })


if __name__ == "__main__":
    # Running on 5001 to demonstrate cross-origin
    app.run(debug=True, port=5001)
