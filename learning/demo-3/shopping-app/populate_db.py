import json, re
from models import Product


def slugify(text):
    return re.sub(r"[\W_]+", "-", text.lower())


def populate_db(db):
    if Product.query.count() > 0:
        return  # No-op if data is already seeded

    with open("products.json", "r") as f:
        data = json.load(f)
        for item in data:
            p = Product(
                title=item["title"],
                slug=slugify(item["title"]),
                description=item["description"],
                brand=item["brand"],
                category=item["category"],
                price=item["price"],
            )
            db.session.add(p)
        db.session.commit()
    print("Shopping database seeded successfully.")
