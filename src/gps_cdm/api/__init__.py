"""
GPS CDM - REST API
==================

FastAPI-based REST API for GPS CDM operations including:
- Exception management
- Data quality validation
- Reconciliation
- Re-processing
- Lineage visualization

Usage:
    uvicorn gps_cdm.api:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from gps_cdm.api.routes import exceptions, data_quality, reconciliation, reprocess, lineage, pipeline, auth, schema, graph, errors, websocket, mappings

# Create FastAPI app
app = FastAPI(
    title="GPS CDM API",
    description="API for GPS Common Domain Model operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(exceptions.router, prefix="/api/v1/exceptions", tags=["Exceptions"])
app.include_router(data_quality.router, prefix="/api/v1/dq", tags=["Data Quality"])
app.include_router(reconciliation.router, prefix="/api/v1/recon", tags=["Reconciliation"])
app.include_router(reprocess.router, prefix="/api/v1/reprocess", tags=["Re-processing"])
app.include_router(lineage.router, prefix="/api/v1/lineage", tags=["Lineage"])
app.include_router(pipeline.router, prefix="/api/v1/pipeline", tags=["Pipeline"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(schema.router, prefix="/api/v1/schema", tags=["Schema"])
app.include_router(graph.router, prefix="/api/v1/graph", tags=["Graph"])
app.include_router(errors.router, prefix="/api/v1/errors", tags=["Processing Errors"])
app.include_router(websocket.router, prefix="/api/v1/ws", tags=["WebSocket"])
app.include_router(mappings.router, prefix="/api/v1/mappings", tags=["Mappings Documentation"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "gps-cdm-api"}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "GPS CDM API",
        "version": "1.0.0",
        "endpoints": {
            "errors": "/api/v1/errors",
            "exceptions": "/api/v1/exceptions",
            "data_quality": "/api/v1/dq",
            "reconciliation": "/api/v1/recon",
            "reprocess": "/api/v1/reprocess",
            "lineage": "/api/v1/lineage",
            "pipeline": "/api/v1/pipeline",
            "schema": "/api/v1/schema",
            "graph": "/api/v1/graph",
            "auth": "/api/v1/auth",
            "websocket": "/api/v1/ws/stream",
            "mappings": "/api/v1/mappings",
            "docs": "/docs",
        }
    }
