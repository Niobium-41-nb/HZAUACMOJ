from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail
from celery import Celery
import redis


# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
admin = Admin(name='HZAUACMOJ Admin', template_mode='bootstrap4')
bcrypt = Bcrypt()
cors = CORS()
mail = Mail()
celery = Celery(__name__)
redis_client = None


def init_extensions(app):
    """Initialize all extensions"""
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize Flask-Migrate
    migrate.init_app(app, db)
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    
    # Initialize Flask-Admin
    admin.init_app(app)
    
    # Initialize Flask-Bcrypt
    bcrypt.init_app(app)
    
    # Initialize Flask-CORS
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize Flask-Mail
    mail.init_app(app)
    
    # Initialize Celery
    celery.conf.update(app.config)
    
    # Initialize Redis
    global redis_client
    redis_client = redis.from_url(app.config['REDIS_URL'])
