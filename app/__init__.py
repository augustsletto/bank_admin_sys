from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap5
from flask_security import Security
from .config import ConfigDebug  # Byt till ConfigProduction för produktion
from .models import db
from .routes import main_bp

def create_app():
    app = Flask(__name__,
                template_folder="templates",static_folder="static")
    app.config.from_object(ConfigDebug)

    # Initiera tillägg
    db.init_app(app)
    migrate = Migrate(app, db)
    Bootstrap5(app)

    # Importera UserDatastore efter att db har initierats
    from .security import user_datastore, security

    # Initiera Flask-Security
    security.init_app(app, user_datastore)

    # Registrera Blueprints
    
    app.register_blueprint(main_bp)

    return app
