import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create declarative base for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize database
db = SQLAlchemy(model_class=Base)

# Custom template functions
def get_category_color(category):
    """Get bootstrap color for news category"""
    colors = {
        'market': 'warning',
        'war': 'danger',
        'diplomacy': 'success',
        'technology': 'info',
        'espionage': 'secondary',
        'ranking': 'dark',
        'event': 'primary'
    }
    return colors.get(category, 'primary')

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "ecoworld-default-secret")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Add template context processors
app.jinja_env.globals.update(get_category_color=get_category_color)

# Configure the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///ecoworld.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database with the app
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# Import models to ensure they're registered with SQLAlchemy
with app.app_context():
    from models import User, Nation, Resource, Technology, Military, MarketItem, Trade, War, Alliance, NewsArticle
    db.create_all()

# Import and register blueprints
from routes.auth import auth as auth_blueprint
from routes.game import game as game_blueprint
from routes.market import market as market_blueprint
from routes.military import military as military_blueprint
from routes.technology import technology as technology_blueprint
from routes.landing import landing as landing_blueprint
from routes.diplomacy import diplomacy as diplomacy_blueprint
from routes.espionage import espionage as espionage_blueprint
from routes.news import news_bp as news_blueprint

app.register_blueprint(landing_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(game_blueprint)
app.register_blueprint(market_blueprint)
app.register_blueprint(military_blueprint)
app.register_blueprint(technology_blueprint)
app.register_blueprint(diplomacy_blueprint)
app.register_blueprint(espionage_blueprint)
app.register_blueprint(news_blueprint)

# Context processor rimosso

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    print(f"LOAD USER CALLED - user_id: {user_id}")
    user = User.query.get(int(user_id))
    if user:
        print(f"USER FOUND - username: {user.username}")
    else:
        print(f"USER NOT FOUND - user_id: {user_id}")
    return user

# Import and initialize scheduler
from utils.scheduler import init_scheduler
init_scheduler(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
