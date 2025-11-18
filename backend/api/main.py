from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.routers import recommend, users, recipes, ingredients, interactions, detect, auth, cuisines
from api.db import close_driver


# =====================================
# 🚀 App Initialization
# =====================================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="Food Recommendation API built with FastAPI and Neo4j"
)


# =====================================
# 🌐 CORS Configuration
# =====================================
# If CORS_ALLOW_ORIGINS = "*", allow all origins (no credentials)
# If it’s a string, split by commas to convert to a list
# If it’s a list, use it directly

if settings.CORS_ALLOW_ORIGINS == "*" or settings.CORS_ALLOW_ORIGINS == ["*"]:
    allow_origins = ["*"]
    allow_credentials = False  # must be False when using wildcard origin
else:
    if isinstance(settings.CORS_ALLOW_ORIGINS, str):
        allow_origins = [o.strip() for o in settings.CORS_ALLOW_ORIGINS.split(",")]
    else:
        allow_origins = settings.CORS_ALLOW_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True if "*" not in allow_origins else False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================
# 📦 Routers
# =====================================
app.include_router(auth.router)
app.include_router(recommend.router)
app.include_router(users.router)
app.include_router(recipes.router)
app.include_router(ingredients.router)
app.include_router(interactions.router)
app.include_router(detect.router)
app.include_router(cuisines.router)


# =====================================
# 🏠 Root Endpoint
# =====================================
@app.get("/", include_in_schema=False)
def root():
    return {
        "message": "Food Recommendation API",
        "version": settings.API_VERSION
    }


# =====================================
# 🧹 Shutdown Cleanup
# =====================================
@app.on_event("shutdown")
def _shutdown():
    close_driver()


# =====================================
# ▶️ Entry Point
# =====================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
