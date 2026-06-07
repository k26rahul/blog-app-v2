import random
from models import Article, Category, Brand

categories = ["grocery", "clothing", "electronics", "home-decor", "toys"]
brands = [
    "Nature Farm",
    "FreshCo",
    "BasicWear",
    "UrbanStyle",
    "TechPro",
    "ElectroMax",
    "HomeEssentials",
    "CozyLiving",
    "PlayTime",
    "KidJoy",
]
topics = [
    "Fashion",
    "Tech Trends",
    "Healthy Living",
    "Parenting",
    "Home Decor",
    "Sports",
    "Yoga",
    "Politics",
    "Finance",
    "Travel",
]


def populate_db(db):
    if Article.query.count() > 0:
        return

    # Pre-populate Categories and Brands
    cat_objs = {c: Category(name=c) for c in categories}
    brand_objs = {b: Brand(name=b) for b in brands}

    for c in cat_objs.values():
        db.session.add(c)
    for b in brand_objs.values():
        db.session.add(b)

    for i in range(1, 51):
        target_cat = random.choice(categories)
        target_brand = random.choice(brands)

        a = Article(
            slug=f"post-{i}",
            title=f"The Ultimate Guide to {random.choice(topics)} ({i})",
            content="This is a great lifestyle article. We highly recommend checking out this amazing product that aligns perfectly with your lifestyle.",
            affiliate_link=f"http://127.0.0.1:5000/store/{target_cat}?affiliation_id=lifestyle_blog",
        )

        a.target_categories.append(cat_objs[target_cat])
        a.target_brands.append(brand_objs[target_brand])
        db.session.add(a)

    db.session.commit()
    print("Lifestyle database seeded successfully.")
