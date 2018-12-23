from flask_cors import CORS

from app.core import config
from app.main import app

origins = []

# Set all CORS enabled origins
if config.BACKEND_CORS_ORIGINS:
    origins_raw = config.BACKEND_CORS_ORIGINS.split(",")
    for origin in origins_raw:
        use_origin = origin.strip()
        origins.append(use_origin)

    CORS(app, origins=origins, supports_credentials=True)
