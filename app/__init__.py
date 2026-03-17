from flask import Flask
from .config import config


def create_app(config_name: str = "default") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Register blueprints
    from .routes.main import main_bp
    app.register_blueprint(main_bp)

    return app
