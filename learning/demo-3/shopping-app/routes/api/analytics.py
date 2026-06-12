from flask import Blueprint, jsonify
from sqlalchemy import func
from models import db, Product, Visitor, Visit

analytics = Blueprint("api_analytics", __name__, url_prefix="/api")


@analytics.route("/analytics")
def analytics_dashboard():
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
    for slug, count in product_hits:
        if slug:
            p = Product.query.filter_by(slug=slug).first()
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
    for slug, count in top_products_data:
        if slug:
            p = Product.query.filter_by(slug=slug).first()
            if p:
                top_products.append({"title": p.title, "visits": count})

    last_visitors = Visitor.query.order_by(Visitor.first_seen.desc()).limit(10).all()
    last_visits = Visit.query.order_by(Visit.timestamp.desc()).limit(50).all()

    return jsonify({
        "total_visitors": total_visitors,
        "total_visits": total_visits,
        "visits_by_store": [{"store": k, "visits": v} for k, v in store_totals.items()],
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
    })
