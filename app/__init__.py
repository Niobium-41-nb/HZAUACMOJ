import os
from flask import Flask, render_template
from dotenv import load_dotenv
from .extensions import init_extensions
from .utils.decorators import admin_required


# Load environment variables
load_dotenv()


def create_app(config_name=None, init_admin=True):
    """Create and configure the Flask application.
    
    Args:
        config_name: Name of the configuration to use
        init_admin: Whether to initialize the admin panel (default: True)
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    from config import config
    app.config.from_object(config[config_name])
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    init_extensions(app)
    
    # Flask-Login user loader
    from app.extensions import login_manager
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from .api.v1 import api_bp as api_v1_bp
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
    
    # Register admin views if requested
    if init_admin:
        from .admin import init_admin
        init_admin(app)
    
    # Register error handlers
    from .utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # Frontend routes
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/resources')
    def resources():
        return render_template('resources.html')
    
    @app.route('/blogs')
    def blogs():
        return render_template('blogs.html')
    
    @app.route('/contests')
    def contests():
        return render_template('contests.html')
    
    @app.route('/problems')
    def problems():
        return render_template('problems.html')
    
    @app.route('/submissions')
    def submissions():
        return render_template('submissions.html')
    
    @app.route('/login')
    def login():
        return render_template('login.html')
    
    @app.route('/register')
    def register():
        return render_template('register.html')
    
    return app
