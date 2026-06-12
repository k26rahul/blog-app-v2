from flask import Blueprint, send_from_directory, redirect, url_for, g
from models import db, CartItem

views = Blueprint("views", __name__)


@views.route("/")
def index():
    return send_from_directory("templates", "index.html")


@views.route("/store/<category>")
def store(category):
    return send_from_directory("templates", "store.html")


@views.route("/product/<slug>")
def product(slug):
    return send_from_directory("templates", "product.html")


@views.route("/cart")
def cart():
    return send_from_directory("templates", "cart.html")


@views.route("/analytics")
def analytics():
    return send_from_directory("templates", "analytics.html")


@views.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    item = CartItem(tracking_uuid=g.tracking_uuid, product_id=product_id)
    db.session.add(item)
    db.session.commit()
    return redirect(url_for("views.cart"))
