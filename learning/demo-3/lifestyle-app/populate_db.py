import json
import os
from models import Article, Category, Brand


def populate_db(db):
    if Article.query.count() > 0:
        return

    # Load from articles.json
    json_path = os.path.join(os.path.dirname(__file__), "articles.json")
    with open(json_path, "r") as f:
        articles_data = json.load(f)

    cat_objs = {}
    brand_objs = {}

    for item in articles_data:
        c_name = item["category"]
        b_name = item["brand"]

        if c_name not in cat_objs:
            cat_objs[c_name] = Category(name=c_name)
            db.session.add(cat_objs[c_name])
        
        if b_name not in brand_objs:
            brand_objs[b_name] = Brand(name=b_name)
            db.session.add(brand_objs[b_name])

    db.session.flush()

    for item in articles_data:
        a = Article(
            slug=item["slug"],
            title=item["title"],
            content=item["content"]
        )

        a.category = cat_objs[item["category"]]
        a.brand = brand_objs[item["brand"]]
        db.session.add(a)

    db.session.commit()
    print("Lifestyle database seeded successfully from articles.json.")
