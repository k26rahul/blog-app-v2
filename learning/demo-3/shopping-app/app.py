import uuid
from flask import Flask, request, g
from models import db, Visitor, Visit
from populate_db import populate_db
from routes import register_blueprints

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shop.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    populate_db(db)

register_blueprints(app)


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
        entity_info = request.path.split("/")[2]  # slug

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


if __name__ == "__main__":
    app.run(debug=True, port=5000)
