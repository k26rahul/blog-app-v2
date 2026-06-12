from flask import Blueprint, request, jsonify
from models import Product, Visitor

tracking = Blueprint("api_tracking", __name__, url_prefix="/api")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "http://localhost:5001",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
}


@tracking.route("/user_interests", methods=["GET", "OPTIONS"])
def user_interests():
    if request.method == "OPTIONS":
        response = jsonify({})
        for k, v in CORS_HEADERS.items():
            response.headers[k] = v
        return response

    tracking_id = request.cookies.get("tracking_uuid")
    interests = {"categories": []}

    if tracking_id:
        visitor = Visitor.query.filter_by(tracking_uuid=tracking_id).first()
        if visitor:
            # SQLAlchemy relationships make this cleaner
            visits = [v for v in visitor.visits if v.page_type == "product"]

            # Track the most recent visit timestamp per category
            cat_latest = {}
            for v in visits:
                if v.entity_info:
                    p = Product.query.filter_by(slug=v.entity_info).first()
                    if p:
                        ts = v.timestamp
                        if p.category not in cat_latest or ts > cat_latest[p.category]:
                            cat_latest[p.category] = ts

            # Most recently visited category comes first
            interests["categories"] = sorted(
                cat_latest, key=cat_latest.get, reverse=True
            )

    response = jsonify(interests)
    for k, v in CORS_HEADERS.items():
        response.headers[k] = v
    return response
