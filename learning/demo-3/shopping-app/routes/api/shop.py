from flask import Blueprint, request, jsonify
from sqlalchemy import func
from models import db, Product, Visitor, Visit, CartItem
from utils import time_ago

shop = Blueprint("api_shop", __name__, url_prefix="/api")


@shop.route("/index")
def index():
    stores = db.session.query(Product.category).distinct().all()
    recent_products = []

    tracking_id = request.cookies.get("tracking_uuid")
    visitor = Visitor.query.filter_by(tracking_uuid=tracking_id).first() if tracking_id else None

    if visitor:
        recent_visits = (
            db.session.query(
                Visit.entity_info, func.max(Visit.timestamp).label("last_visit")
            )
            .filter_by(visitor_id=visitor.id, page_type="product")
            .group_by(Visit.entity_info)
            .order_by(db.desc("last_visit"))
            .limit(5)
            .all()
        )
        for slug, ts in recent_visits:
            if slug:
                p = Product.query.filter_by(slug=slug).first()
                if p:
                    recent_products.append({"slug": p.slug, "title": p.title, "time": time_ago(ts)})

    tracking_uuid = request.cookies.get("tracking_uuid", "")
    is_new_visitor = not bool(tracking_uuid)

    return jsonify({
        "stores": [s[0] for s in stores],
        "recent": recent_products,
        "tracking_uuid": tracking_uuid,
        "is_new_visitor": is_new_visitor,
    })


@shop.route("/store/<category>")
def store(category):
    all_products = Product.query.filter_by(category=category).limit(20).all()
    recent_products = []

    tracking_id = request.cookies.get("tracking_uuid")
    visitor = Visitor.query.filter_by(tracking_uuid=tracking_id).first() if tracking_id else None

    if visitor:
        all_recent = (
            db.session.query(
                Visit.entity_info, func.max(Visit.timestamp).label("last_visit")
            )
            .filter_by(visitor_id=visitor.id, page_type="product")
            .group_by(Visit.entity_info)
            .order_by(db.desc("last_visit"))
            .all()
        )
        for slug, ts in all_recent:
            if slug and len(recent_products) < 5:
                p = Product.query.filter_by(slug=slug).first()
                if p and p.category == category:
                    recent_products.append({"slug": p.slug, "title": p.title, "time": time_ago(ts)})

    return jsonify({
        "category": category,
        "products": [{"slug": p.slug, "title": p.title, "price": p.price} for p in all_products],
        "recent": recent_products,
    })


@shop.route("/product/<slug>")
def product(slug):
    p = Product.query.filter_by(slug=slug).first_or_404()
    return jsonify({
        "id": p.id,
        "slug": p.slug,
        "title": p.title,
        "brand": p.brand,
        "price": p.price,
        "description": p.description,
    })


@shop.route("/cart")
def cart():
    tracking_id = request.cookies.get("tracking_uuid", "")
    visitor = Visitor.query.filter_by(tracking_uuid=tracking_id).first() if tracking_id else None
    items = CartItem.query.filter_by(visitor_id=visitor.id).all() if visitor else []
    products = [item.product for item in items if item.product]
    total = sum(p.price for p in products)
    return jsonify({
        "products": [{"title": p.title, "price": p.price} for p in products],
        "total": round(total, 2),
    })
