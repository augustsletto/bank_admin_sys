from flask_security import Security, SQLAlchemyUserDatastore
from app.models import db, User, Role

# Skapa UserDatastore
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

# Skapa en instans av Flask-Security
security = Security()
