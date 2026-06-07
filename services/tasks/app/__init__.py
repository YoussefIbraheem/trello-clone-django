from .core.config import Settings
from flask import Flask
from flask_migrate import Migrate
import logging

migrate = Migrate()
settings = Settings.get_instance()
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)

    migrate.init_app(app=app, db=None, directory="./migrations")

    from .apis.project_api import project_bp

    app.register_blueprint(project_bp)
    from .apis.board_api import board_bp

    app.register_blueprint(board_bp)
    from .apis.task_api import task_bp

    app.register_blueprint(task_bp)

    return app
