from typing import Dict, List

from apispec import APISpec
from flask_apispec import FlaskApiSpec

from ...core import config
from ...main import app

security_definitions = {
    "bearer": {
        "type": "oauth2",
        "flow": "password",
        "tokenUrl": f"{config.API_V1_STR}/login/access-token",
    }
}

app.config.update(
    {
        "APISPEC_SPEC": APISpec(
            title=config.PROJECT_NAME,
            version="v1",
            openapi_version="2.0",
            plugins=("apispec.ext.marshmallow",),
            securityDefinitions=security_definitions,
        ),
        "APISPEC_SWAGGER_URL": f"{config.API_V1_STR}/swagger/",
    }
)
docs = FlaskApiSpec(app)

security_params: List[Dict[str, List]] = [{"bearer": []}]
