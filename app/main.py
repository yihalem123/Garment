"""
Garment Business Management System - Main FastAPI Application
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, products, raw_materials, inventory, purchases, production, transfers, sales, returns, websocket, analytics, hr, business_intelligence, finance, shops
from app.core.config import settings
from app.db.session import engine
from app.models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Disable SQLAlchemy engine logs
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Garment Business Management System...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down Garment Business Management System...")


# Create FastAPI app
app = FastAPI(
    title="Garment Business Management System",
    description="A comprehensive REST API for managing garment business operations including inventory, production, sales, and reporting",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(raw_materials.router, prefix="/raw-materials", tags=["Raw Materials"])
app.include_router(shops.router, prefix="/shops", tags=["Shops"])
app.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
app.include_router(purchases.router, prefix="/purchases", tags=["Purchases"])
app.include_router(production.router, prefix="/production", tags=["Production"])
app.include_router(transfers.router, prefix="/transfers", tags=["Transfers"])
app.include_router(sales.router, prefix="/sales", tags=["Sales"])
app.include_router(returns.router, prefix="/returns", tags=["Returns"])
app.include_router(websocket.router, tags=["WebSocket"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(hr.router, prefix="/hr", tags=["Human Resources"])
app.include_router(business_intelligence.router, prefix="/business-intelligence", tags=["Business Intelligence"])
app.include_router(finance.router, prefix="/finance", tags=["Finance"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Garment Business Management System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
