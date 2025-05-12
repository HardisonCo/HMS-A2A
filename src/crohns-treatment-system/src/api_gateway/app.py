"""
Main application module for the Crohn's Treatment System API gateway.

This module initializes the Flask application and registers all API routes.
"""
import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config=None):
    """
    Create and configure the Flask application.
    
    Args:
        config: Configuration dictionary (optional)
        
    Returns:
        Configured Flask application
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app)
    
    # Load configuration
    app.config.update({
        'DEBUG': os.environ.get('DEBUG', 'false').lower() == 'true',
        'TESTING': False,
        'JSON_SORT_KEYS': False,
        'JSONIFY_PRETTYPRINT_REGULAR': True,
    })
    
    # Override with custom config if provided
    if config:
        app.config.update(config)
    
    # Register routes
    register_routes(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

def register_routes(app):
    """
    Register all API routes with the Flask app.

    Args:
        app: Flask application
    """
    # Import controllers
    from src.api_gateway.abstraction_analysis_controller import register_routes as register_abstraction_routes
    from src.api_gateway.publisher_integration_service import register_routes as register_publisher_routes
    from src.api_gateway.doc_integration_controller import register_routes as register_doc_integration_routes

    # Register routes
    register_abstraction_routes(app)
    register_publisher_routes(app)
    register_doc_integration_routes(app)
    
    # Health check routes
    @app.route('/health', methods=['GET'])
    def health_check():
        """Check the health of the API gateway."""
        return jsonify({
            "status": "healthy",
            "components": {
                "api_gateway": {"status": "healthy"},
                # In a real implementation, check other components too
            }
        })
    
    @app.route('/ready', methods=['GET'])
    def readiness_check():
        """Check if the API gateway is ready to serve requests."""
        return jsonify({"status": "ready"})
    
    # API status route
    @app.route('/api/v1/status', methods=['GET'])
    def api_status():
        """Get the status of the API."""
        return jsonify({
            "version": "1.0.0",
            "status": "operational",
            "features": [
                "abstraction_analysis",
                "enhanced_genetic_optimization",
                "adaptive_trial_design",
                "clinical_trial_publishing",
                "doc_integration"
            ]
        })

def register_error_handlers(app):
    """
    Register error handlers with the Flask app.
    
    Args:
        app: Flask application
    """
    @app.errorhandler(400)
    def bad_request(error):
        """Handle bad request errors."""
        return jsonify({
            "error": "Bad request",
            "message": str(error)
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle not found errors."""
        return jsonify({
            "error": "Not found",
            "message": str(error)
        }), 404
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle internal server errors."""
        logger.error(f"Internal server error: {str(error)}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }), 500

def run_app():
    """Run the Flask application."""
    app = create_app()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    run_app()