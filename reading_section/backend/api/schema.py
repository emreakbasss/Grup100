from fastapi.openapi.utils import get_openapi


def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Reading Section API",
        version="1.0.0",
        description="API with OAuth2 Password"
                    " Flow Authentication",
        routes=app.routes,
    )

    # components yoksa
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    # securitySchemes yoksa
    if "securitySchemes" not in openapi_schema["components"]:
        openapi_schema["components"]["securitySchemes"] = {}


    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/token",
                    "scopes": {
                        "me": "Read your profile"
                    }
                }
            }
        }
    }

    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"OAuth2PasswordBearer": ["me"]}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema





