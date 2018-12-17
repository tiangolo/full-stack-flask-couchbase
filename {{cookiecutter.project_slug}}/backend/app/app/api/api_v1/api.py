# Import installed packages

from app.core import config
# Import app code
from app.main import app

from .api_docs import docs
from .endpoints import role, token, user, utils
