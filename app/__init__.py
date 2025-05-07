import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

def create_app(test_config=None):
    """Create and configure the Flask application."""
    # Create upload directory if it doesn't exist
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    app.config.from_object('app.config.Config')
    
    # Override config with test config if provided
    if test_config is not None:
        app.config.update(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        os.makedirs(os.path.join(app.instance_path, 'uploads'), exist_ok=True)
        os.makedirs(os.path.join(app.instance_path, 'temp'), exist_ok=True)
    except OSError:
        pass
    
    # Initialize extensions
    from app.extensions import mongo, es
    mongo.init_app(app)
    es.init_app(app)
    
    # Initialize security features
    from app.utils.security import init_security, csrf
    init_security(app)
    
    # Configure CSRF protection
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
    app.config['WTF_CSRF_SSL_STRICT'] = False  # Allow CSRF tokens on http connections
    
    # Make csrf available globally
    app.extensions['csrf'] = csrf
    
    # Initialize rate limiting
    from app.utils.rate_limiter import init_limiter
    limiter = init_limiter(app)
    
    # Initialize caching
    from flask_caching import Cache
    cache = Cache(app)
    app.config['CACHE'] = cache
    
    # Enable CORS for API routes
    CORS(app, resources={"/api/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.documents import documents_bp
    from app.routes.compliance import compliance_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(compliance_bp)
    app.register_blueprint(api_bp)
    
    # Register error handlers
    from app.utils.error_handler import handle_error, AppError, NotFoundError
    
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found', 'message': str(error), 'status_code': 404}), 404
        return handle_error(NotFoundError('The requested resource was not found'))
    
    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error', 'message': str(error), 'status_code': 500}), 500
        return handle_error(AppError('An internal server error occurred', status_code=500))
    
    # Seed database with sample data
    with app.app_context():
        from app.services.seed_service import seed_compliance_rules
        seed_compliance_rules()
    
    # Register health check endpoints
    @app.route('/ping')
    def ping():
        return 'pong'
    
    @app.route('/health')
    def health_check():
        health_status = {
            'status': 'ok',
            'version': app.config.get('VERSION', '1.0.0'),
            'timestamp': str(datetime.now()),
            'services': {
                'database': 'ok',
                'elasticsearch': 'ok'
            }
        }
        
        # Check MongoDB connection
        try:
            mongo.db.command('ping')
        except Exception as e:
            health_status['services']['database'] = f'error: {str(e)}'
            health_status['status'] = 'degraded'
        
        # Check Elasticsearch connection
        try:
            es.ping()
        except Exception as e:
            health_status['services']['elasticsearch'] = f'error: {str(e)}'
            health_status['status'] = 'degraded'
        
        return jsonify(health_status)
    
    return app