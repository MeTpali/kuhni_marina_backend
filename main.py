from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api.v1.routers import api_router
from core.config import settings, setup_logging
from fastapi.security.api_key import APIKeyHeader
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from admin import setup_admin

# Настраиваем логирование
setup_logging()

app = FastAPI(
    title="Kuhni Marina API",
    description="API ответственное за работу сайта кухни Вязники",
    version="1.0.1",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    contact={
        "name": "Tereshchuk Artemy",
        "email": "metpa.li@top.g",
    },
    license_info={
        "name": "MIT",
    },
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Настройка статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем роутеры API v1
app.include_router(api_router, prefix="/api/v1")

# Настраиваем SQLAdmin
admin = setup_admin(app)

# --- Настройка авторизации для OpenAPI ---
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags
    )
    openapi_schema["components"]["securitySchemes"] = {
        "tokenAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Token-based authentication. Just paste your access token."
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"tokenAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
