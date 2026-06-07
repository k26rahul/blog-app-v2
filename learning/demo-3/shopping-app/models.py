from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    slug = db.Column(db.String(100))
    description = db.Column(db.Text)
    brand = db.Column(db.String(50))
    category = db.Column(db.String(50))
    price = db.Column(db.Float)


class Visitor(db.Model):
    __tablename__ = "visitors"
    id = db.Column(db.Integer, primary_key=True)
    tracking_uuid = db.Column(db.String(36), unique=True)
    user_agent = db.Column(db.String(255))
    ip_address = db.Column(db.String(50))
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    visits = db.relationship("Visit", backref="visitor", lazy=True)


class Visit(db.Model):
    __tablename__ = "visits"
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey("visitors.id"), nullable=False)
    url = db.Column(db.String(255))
    page_type = db.Column(db.String(50))
    entity_info = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class CartItem(db.Model):
    __tablename__ = "cart_items"
    id = db.Column(db.Integer, primary_key=True)
    tracking_uuid = db.Column(db.String(36))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    # Relationship
    product = db.relationship("Product")
