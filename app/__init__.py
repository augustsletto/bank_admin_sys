from flask import Flask
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap5
from .config import ConfigDebug  # toggla mellan ConfigProduction/ConfigDebug för produktion/debug
from .models import db
from .routes import main_bp
from .security import user_datastore, security

def create_app():
    app = Flask(__name__,
template_folder="templates",static_folder="static")
    app.config.from_object(ConfigDebug)

    db.init_app(app)
    migrate = Migrate(app, db)
    Bootstrap5(app)

    
    security.init_app(app, user_datastore)

    
    app.register_blueprint(main_bp)

    return app
