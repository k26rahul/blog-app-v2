import uuid
from datetime import datetime
from flask import (
    Flask,
    request,
    g,
    render_template,
    redirect,
    url_for,
    jsonify,
    send_from_directory,
)
from sqlalchemy import func
from models import db, Product, Visitor, Visit, CartItem
from populate_db import populate_db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shop.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    populate_db(db)


def time_ago(dt):
    if not dt:
        return ""
    seconds = (datetime.utcnow() - dt).total_seconds()
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        return f"{int(seconds/60)} mins ago"
    elif seconds < 86400:
        return f"{int(seconds/3600)} hours ago"
    else:
        return f"{int(seconds/86400)} days ago"


app.jinja_env.filters["timeago"] = time_ago


@app.before_request
def track_visitor():
    if (
        request.path.startswith("/static")
        or request.path.startswith("/api/")
        or request.path == "/analytics"
        or request.path == "/favicon.ico"
        or request.path.startswith("/.well-known")
    ):
        return

    tracking_id = request.cookies.get("tracking_uuid")
    g.is_new_visitor = False

    if not tracking_id:
        tracking_id = str(uuid.uuid4())
        g.is_new_visitor = True
        visitor = Visitor(
            tracking_uuid=tracking_id,
            user_agent=request.user_agent.string,
            ip_address=request.remote_addr,
        )
        db.session.add(visitor)
        db.session.commit()
    else:
        visitor = Visitor.query.filter_by(tracking_uuid=tracking_id).first()
        if not visitor:  # Failsafe if cookie exists but DB was wiped
            visitor = Visitor(
                tracking_uuid=tracking_id,
                user_agent=request.user_agent.string,
                ip_address=request.remote_addr,
            )
            db.session.add(visitor)
            db.session.commit()

    g.tracking_uuid = tracking_id
    g.visitor_id = visitor.id

    page_type, entity_info = "other", ""
    if request.path == "/":
        page_type = "home"
    elif request.path.startswith("/store/"):
        page_type = "store"
        entity_info = request.path.split("/")[-1]
    elif request.path.startswith("/product/"):
        page_type = "product"
        entity_info = request.path.split("/")[2]

    visit = Visit(
        visitor_id=visitor.id,
        url=request.url,
        page_type=page_type,
        entity_info=entity_info,
    )
    db.session.add(visit)
    db.session.commit()


@app.after_request
def set_tracking_cookie(response):
    if getattr(g, "is_new_visitor", False):
        response.set_cookie(
            "tracking_uuid",
            g.tracking_uuid,
            max_age=31536000,
            samesite="None",
            secure=True,
        )
    return response


# --- HTML ROUTES ---
@app.route("/")
def index():
    stores = db.session.query(Product.category).distinct().all()
    recent_products, frequent_products = [], []

    if hasattr(g, "visitor_id"):
        recent_visits = (
            db.session.query(
                Visit.entity_info, func.max(Visit.timestamp).label("last_visit")
            )
            .filter_by(visitor_id=g.visitor_id, page_type="product")
            .group_by(Visit.entity_info)
            .order_by(db.desc("last_visit"))
            .limit(3)
            .all()
        )
        for pid, ts in recent_visits:
            if pid and pid.isdigit():
                p = Product.query.get(int(pid))
                if p:
                    recent_products.append({"product": p, "time": ts})

        freq_visits = (
            db.session.query(
                Visit.entity_info, func.count(Visit.id).label("visit_count")
            )
            .filter_by(visitor_id=g.visitor_id, page_type="product")
            .group_by(Visit.entity_info)
            .order_by(db.desc("visit_count"))
            .limit(3)
            .all()
        )
        for pid, count in freq_visits:
            if pid and pid.isdigit():
                p = Product.query.get(int(pid))
                if p:
                    frequent_products.append({"product": p, "count": count})

    return render_template(
        "index.html",
        stores=[s[0] for s in stores],
        recent=recent_products,
        frequent=frequent_products,
    )


@app.route("/store/<category>")
def store(category):
    all_products = Product.query.filter_by(category=category).limit(20).all()
    recent_products, frequent_products = [], []

    if hasattr(g, "visitor_id"):
        all_recent = (
            db.session.query(
                Visit.entity_info, func.max(Visit.timestamp).label("last_visit")
            )
            .filter_by(visitor_id=g.visitor_id, page_type="product")
            .group_by(Visit.entity_info)
            .order_by(db.desc("last_visit"))
            .all()
        )
        for pid, ts in all_recent:
            if pid and pid.isdigit() and len(recent_products) < 3:
                p = Product.query.get(int(pid))
                if p and p.category == category:
                    recent_products.append({"product": p, "time": ts})

        all_freq = (
            db.session.query(
                Visit.entity_info, func.count(Visit.id).label("visit_count")
            )
            .filter_by(visitor_id=g.visitor_id, page_type="product")
            .group_by(Visit.entity_info)
            .order_by(db.desc("visit_count"))
            .all()
        )
        for pid, count in all_freq:
            if pid and pid.isdigit() and len(frequent_products) < 3:
                p = Product.query.get(int(pid))
                if p and p.category == category:
                    frequent_products.append({"product": p, "count": count})

    return render_template(
        "store.html",
        category=category,
        products=all_products,
        recent=recent_products,
        frequent=frequent_products,
    )


@app.route("/product/<int:id>/<slug>")
def product(id, slug):
    prod = Product.query.get_or_404(id)
    return render_template("product.html", product=prod)


@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    item = CartItem(tracking_uuid=g.tracking_uuid, product_id=product_id)
    db.session.add(item)
    db.session.commit()
    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    items = CartItem.query.filter_by(tracking_uuid=g.tracking_uuid).all()
    products = [item.product for item in items]
    total = sum(p.price for p in products if p)
    return render_template("cart.html", products=products, total=total)


@app.route("/analytics")
def analytics():
    # Serve completely static file
    return send_from_directory("templates", "analytics.html")


# --- API ROUTES ---
@app.route("/api/analytics")
def api_analytics():
    total_visitors = Visitor.query.count()
    total_visits = Visit.query.count()

    # Store Logic: Direct store hits + product hits in that category
    store_totals = {}
    direct_store_hits = (
        db.session.query(Visit.entity_info, func.count(Visit.id))
        .filter_by(page_type="store")
        .group_by(Visit.entity_info)
        .all()
    )
    for store, count in direct_store_hits:
        if store:
            store_totals[store] = count

    product_hits = (
        db.session.query(Visit.entity_info, func.count(Visit.id))
        .filter_by(page_type="product")
        .group_by(Visit.entity_info)
        .all()
    )
    for pid, count in product_hits:
        if pid and pid.isdigit():
            p = Product.query.get(int(pid))
            if p:
                store_totals[p.category] = store_totals.get(p.category, 0) + count

    top_products_data = (
        db.session.query(Visit.entity_info, func.count(Visit.id))
        .filter_by(page_type="product")
        .group_by(Visit.entity_info)
        .order_by(func.count(Visit.id).desc())
        .limit(10)
        .all()
    )
    top_products = []
    for pid, count in top_products_data:
        if pid and pid.isdigit():
            p = Product.query.get(int(pid))
            if p:
                top_products.append({"title": p.title, "visits": count})

    last_visitors = Visitor.query.order_by(Visitor.first_seen.desc()).limit(10).all()
    last_visits = Visit.query.order_by(Visit.timestamp.desc()).limit(50).all()

    return jsonify(
        {
            "total_visitors": total_visitors,
            "total_visits": total_visits,
            "visits_by_store": [
                {"store": k, "visits": v} for k, v in store_totals.items()
            ],
            "top_products": top_products,
            "last_visitors": [
                {
                    "id": v.id,
                    "uuid": v.tracking_uuid,
                    "time": v.first_seen.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for v in last_visitors
            ],
            "last_visits": [
                {
                    "id": v.id,
                    "vid": v.visitor_id,
                    "url": v.url,
                    "type": v.page_type,
                    "time": v.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for v in last_visits
            ],
        }
    )


@app.route("/api/user_interests", methods=["GET", "OPTIONS"])
def user_interests():
    response = jsonify({}) if request.method == "OPTIONS" else None

    headers = {
        "Access-Control-Allow-Origin": "http://localhost:5001",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
    }

    if request.method == "OPTIONS":
        for k, v in headers.items():
            response.headers[k] = v
        return response

    tracking_id = request.cookies.get("tracking_uuid")
    interests = {"categories": [], "brands": []}

    if tracking_id:
        visitor = Visitor.query.filter_by(tracking_uuid=tracking_id).first()
        if visitor:
            # SQLAlchemy relationships make this cleaner
            visits = [v for v in visitor.visits if v.page_type == "product"]
            cat_counts, brand_counts = {}, {}

            for v in visits:
                if v.entity_info and v.entity_info.isdigit():
                    p = Product.query.get(int(v.entity_info))
                    if p:
                        cat_counts[p.category] = cat_counts.get(p.category, 0) + 1
                        brand_counts[p.brand] = brand_counts.get(p.brand, 0) + 1

            interests["categories"] = sorted(
                cat_counts, key=cat_counts.get, reverse=True
            )[:3]
            interests["brands"] = sorted(
                brand_counts, key=brand_counts.get, reverse=True
            )[:3]

    response = jsonify(interests)
    for k, v in headers.items():
        response.headers[k] = v
    return response


if __name__ == "__main__":
    app.run(debug=True, port=5000)
