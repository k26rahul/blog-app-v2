from flask import Flask, render_template, jsonify
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
    articles = Article.query.all()
    # Serialize for frontend filtering
    articles_data = []
    for a in articles:
        articles_data.append(
            {
                "slug": a.slug,
                "title": a.title,
                "categories": [c.name for c in a.target_categories],
                "brands": [b.name for b in a.target_brands],
            }
        )
    return render_template("index.html", articles=articles, articles_json=articles_data)


@app.route("/post/<slug>")
def post(slug):
    article = Article.query.filter_by(slug=slug).first_or_404()
    return render_template("post.html", article=article)


if __name__ == "__main__":
    # Running on 5001 to demonstrate cross-origin
    app.run(debug=True, port=5001)
