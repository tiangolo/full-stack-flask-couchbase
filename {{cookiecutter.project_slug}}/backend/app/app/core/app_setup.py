# Import standard library packages

# Import installed packages
from raven.contrib.flask import Sentry

from app.core import config
# Import app code
from app.main import app

# Set up CORS
from . import cors  # noqa
from . import errors  # noqa
from ..api.api_v1 import api as api_v1  # noqa
from .jwt import jwt  # noqa

app.config["SECRET_KEY"] = config.SECRET_KEY
# app.config["JWT_ALGORITHM"] = "RS256"

sentry = Sentry(app, dsn=config.SENTRY_DSN)
