# Import standard library modules

# Import installed modules
from flask_jwt_extended import JWTManager

from app.crud.user import get_user
from app.db.database import get_default_bucket

# Import app code
from ..main import app

# Setup the Flask-JWT-Extended extension
jwt = JWTManager(app)


@jwt.user_loader_callback_loader
def get_current_user(identity):
    bucket = get_default_bucket()
    return get_user(bucket, username=identity)
