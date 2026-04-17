from .core.config import Settings
settings = Settings.get_instance()
from flask import Flask
from flask_migrate import Migrate


migrate = Migrate()


def create_app() -> Flask:
    app = Flask(__name__)

    migrate.init_app(app=app, db=None, directory="./migrations")

    from .api.project import projects_bp
    app.register_blueprint(projects_bp)
    from .api.boards import boards_bp
    app.register_blueprint(boards_bp)
    
    return app
