import os
from flask import Flask

def create_app(test_config=None):
    """Create and configure the Flask application."""
    # Create upload directory if it doesn't exist
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    app.config.from_object('app.config.Config')
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        os.makedirs(os.path.join(app.instance_path, 'uploads'), exist_ok=True)
    except OSError:
        pass
    
    # Initialize extensions
    from app.extensions import mongo, es
    mongo.init_app(app)
    es.init_app(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.documents import documents_bp
    from app.routes.compliance import compliance_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(compliance_bp)
    
    # Simple route to test the app
    @app.route('/ping')
    def ping():
        return 'pong'
    
    return app