from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    app = FastAPI(title="Microloans API", version="1.0.0")
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Import and include routers
    from .routes.health import router as health_router
    from .routes.loans import router as loans_router
    from .routes.stats import router as stats_router
    
    app.include_router(health_router)
    app.include_router(loans_router, prefix="/api", tags=["loans"])
    app.include_router(stats_router, prefix="/api", tags=["stats"])
    
    return app
