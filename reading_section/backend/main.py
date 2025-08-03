import os
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

# Routers
from backend.api.auth_routes    import router as auth_router
from backend.api.routes         import router as main_router
from backend.api.reading_routes import router as reading_router
from backend.api.default_routes import router as default_router
from backend.api.schema         import custom_openapi
import google.generativeai as genai
from fastapi.staticfiles import StaticFiles

app = FastAPI()

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def create_app():
    app = FastAPI()

    # Statik dosya servisi için frontend klasörünün tam yolu
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    try:
        app.openapi = lambda: custom_openapi(app)
    except:
        pass


    # Router’lar
    app.include_router(auth_router,    prefix="/auth",    tags=["auth"])
    app.include_router(main_router,    prefix="/api",     tags=["main"])
    app.include_router(reading_router, prefix="/reading", tags=["reading"])
    app.include_router(default_router, prefix="",         tags=["default"])

    # CORS
    origins = ["http://localhost:63342", "http://127.0.0.1:63342"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app  # ✅ Burası eksikti!


app = create_app()

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
