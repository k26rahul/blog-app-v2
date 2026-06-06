from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from models import db, User
from routes import auth_bp, blogs_bp

app = Flask(__name__)
app.config.update(SQLALCHEMY_DATABASE_URI="sqlite:///blog.db")

app.register_blueprint(auth_bp)
app.register_blueprint(blogs_bp)

db.init_app(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    app.run(debug=True)
