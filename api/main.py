"""
JCode v3.0 - FastAPI Main Application
Oh-my-opencode governance extension layer API.

This module provides the main FastAPI application with all routes,
middleware, exception handlers, and configuration.
"""

from datetime import datetime, UTC
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import agents_router, config_router

# Create FastAPI application
app = FastAPI(
    title="JCode API",
    description="JCode v3.0 Agent System API - Oh-my-opencode governance extension layer",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS middleware (allow all origins for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development: allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent error response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_type": "HTTPException",
            "message": exc.detail,
            "action": "Check request parameters and try again",
            "timestamp": datetime.now(UTC).isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic exceptions with consistent error response format."""
    return JSONResponse(
        status_code=500,
        content={
            "error_type": type(exc).__name__,
            "message": str(exc) if str(exc) else "An unexpected error occurred",
            "action": "Contact system administrator or check logs",
            "timestamp": datetime.now(UTC).isoformat()
        }
    )


# Health Check Endpoint

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns system status and version information.
    """
    return {
        "status": "healthy",
        "version": "3.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
        "integration": "opencode-superpowers",
        "agents": ["analyst", "planner", "implementer", "reviewer", "tester", "conductor"]
    }


# Include Routers

app.include_router(
    agents_router,
    tags=["Agents"]
)

app.include_router(
    config_router,
    tags=["Configuration"]
)


# Development Server Entry Point

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
