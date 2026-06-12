from routes.views import views
from routes.api import shop, analytics, tracking


def register_blueprints(app):
    app.register_blueprint(views)
    app.register_blueprint(shop)
    app.register_blueprint(analytics)
    app.register_blueprint(tracking)
