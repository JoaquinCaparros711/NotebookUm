"""Flask application factory"""

import os
from flask import Flask
from openai import OpenAI
from .config import config
from .database import db


def create_app(config_name: str = None) -> Flask:
    """
    Flask application factory.

    Args:
        config_name: Configuration name ('development', 'production', 'testing')
                    If None, uses FLASK_ENV environment variable or 'default'

    Returns:
        Configured Flask application instance
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "default")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize SQLAlchemy database
    db.init_app(app)

    # Initialize OpenAI client and attach to app
    app.openai_client = OpenAI(api_key=app.config["OPENAI"].api_key)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    return app


def register_blueprints(app: Flask) -> None:
    """Register Flask blueprints"""
    from .routes.main import main_bp
    from .routes.intelligence import intelligence_bp
    from .routes.users import users_bp
    from .routes.summaries import summaries_bp
    from .routes.documents import documents_bp, documents_list_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(intelligence_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(summaries_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(documents_list_bp)



def register_error_handlers(app: Flask) -> None:
    """Register global error handlers"""
    from .utils.errors import problem_details

    @app.errorhandler(404)
    def handle_404(error):
        return problem_details(status=404, title="Not Found", detail=str(error))

    @app.errorhandler(500)
    def handle_500(error):
        return problem_details(
            status=500, title="Internal Server Error", detail="An unexpected error occurred"
        )
