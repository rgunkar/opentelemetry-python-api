#!/usr/bin/env python3
"""
Example FastAPI application with OpenTelemetry tracing using otel-tracer.

This example demonstrates:
- Basic FastAPI app setup with tracing
- Async endpoints with tracing
- Custom spans and attributes
- Database tracing
- HTTP client instrumentation
- Background tasks with tracing
- Dependency injection with tracing

Run with:
    python examples/fastapi_app.py

Or with custom configuration:
    OTEL_SERVICE_NAME="my-fastapi-app" \
    OTEL_EXPORTER_TYPE="jaeger" \
    uvicorn examples.fastapi_app:app --host 0.0.0.0 --port 8000
"""

import asyncio
import logging
import os
import time
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from otel_tracer import setup_fastapi_tracing

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class User(BaseModel):
    id: int
    name: str
    email: str
    active: bool = True

class UserCreate(BaseModel):
    name: str
    email: str

class BatchRequest(BaseModel):
    items: list[str]
    process_async: bool = False

# Application lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    logger.info("🚀 Starting FastAPI application")
    yield
    logger.info("🛑 Shutting down FastAPI application")

# Create FastAPI app
app = FastAPI(
    title="FastAPI OpenTelemetry Example",
    description="Example FastAPI application with OpenTelemetry tracing",
    version="1.0.0",
    lifespan=lifespan
)

# Setup OpenTelemetry tracing
tracer = setup_fastapi_tracing(
    app,
    service_name="fastapi-example-app",
    excluded_urls=["/health", "/metrics", "/docs", "/redoc"]
)

# In-memory data store for example
users_db: Dict[int, User] = {
    1: User(id=1, name="Alice", email="alice@example.com"),
    2: User(id=2, name="Bob", email="bob@example.com"),
    3: User(id=3, name="Charlie", email="charlie@example.com"),
}

# Dependency functions
async def get_current_user_id() -> int:
    """Example dependency that could be traced."""
    with tracer.start_as_current_span("get_current_user_id") as span:
        # Simulate some work to get user ID
        await asyncio.sleep(0.01)
        user_id = 1  # Hardcoded for example
        span.set_attribute("user.id", user_id)
        return user_id

# Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Hello from FastAPI with OpenTelemetry!",
        "service": "fastapi-example-app",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint (excluded from tracing)."""
    return {"status": "healthy"}

@app.get("/api/users", response_model=list[User])
async def get_users():
    """Get all users."""
    with tracer.start_as_current_span("get_all_users") as span:
        span.set_attribute("users.count", len(users_db))
        
        # Simulate some async work
        await asyncio.sleep(0.1)
        
        return list(users_db.values())

@app.get("/api/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get user by ID."""
    with tracer.start_as_current_span("get_user_by_id") as span:
        span.set_attribute("user.id", user_id)
        
        # Simulate database lookup
        await asyncio.sleep(0.05)
        
        if user_id not in users_db:
            span.set_attribute("error", True)
            raise HTTPException(status_code=404, detail="User not found")
        
        user = users_db[user_id]
        span.set_attribute("user.name", user.name)
        return user

@app.post("/api/users", response_model=User)
async def create_user(user_data: UserCreate):
    """Create a new user."""
    with tracer.start_as_current_span("create_user") as span:
        span.set_attribute("user.email", user_data.email)
        
        # Generate new user ID
        new_id = max(users_db.keys()) + 1 if users_db else 1
        
        # Simulate database insertion
        await asyncio.sleep(0.1)
        
        new_user = User(
            id=new_id,
            name=user_data.name,
            email=user_data.email
        )
        
        users_db[new_id] = new_user
        
        span.set_attribute("user.id", new_id)
        span.set_attribute("user.created", True)
        
        return new_user

@app.get("/api/slow")
async def slow_endpoint():
    """Example of a slow async endpoint."""
    with tracer.start_as_current_span("slow_async_operation") as span:
        span.set_attribute("operation.type", "slow_async_computation")
        
        # Simulate slow async work
        await asyncio.sleep(2)
        
        return {
            "message": "This async endpoint is intentionally slow",
            "duration_seconds": 2
        }

@app.get("/api/external")
async def call_external_api():
    """Example of calling external APIs with async HTTP client."""
    import httpx
    
    with tracer.start_as_current_span("external_async_api_call") as span:
        try:
            async with httpx.AsyncClient() as client:
                # This HTTP call will be automatically traced
                response = await client.get("https://httpbin.org/json", timeout=5)
                
                span.set_attribute("external.api", "httpbin.org")
                span.set_attribute("external.status_code", response.status_code)
                
                return {
                    "message": "External API call successful",
                    "status_code": response.status_code,
                    "data": response.json()
                }
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("error", True)
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/batch")
async def batch_process(batch_data: BatchRequest, background_tasks: BackgroundTasks):
    """Example of batch processing with background tasks."""
    with tracer.start_as_current_span("batch_process_request") as span:
        span.set_attribute("batch.size", len(batch_data.items))
        span.set_attribute("batch.async", batch_data.process_async)
        
        if batch_data.process_async:
            # Process in background
            background_tasks.add_task(
                process_batch_async,
                batch_data.items,
                tracer
            )
            
            return {
                "message": "Batch processing started in background",
                "item_count": len(batch_data.items),
                "async": True
            }
        else:
            # Process synchronously
            results = []
            for i, item in enumerate(batch_data.items):
                with tracer.start_as_current_span(f"process_item_{i}") as item_span:
                    item_span.set_attribute("item.index", i)
                    item_span.set_attribute("item.value", item)
                    
                    # Simulate processing
                    await asyncio.sleep(0.1)
                    
                    results.append({
                        "item": item,
                        "processed": True,
                        "timestamp": time.time()
                    })
            
            span.set_attribute("batch.processed_count", len(results))
            
            return {
                "message": "Batch processing completed",
                "results": results
            }

@app.get("/api/user-profile")
async def get_user_profile(current_user_id: int = Depends(get_current_user_id)):
    """Example endpoint using dependency injection."""
    with tracer.start_as_current_span("get_user_profile") as span:
        span.set_attribute("user.id", current_user_id)
        
        # Get user from database
        if current_user_id not in users_db:
            span.set_attribute("error", True)
            raise HTTPException(status_code=404, detail="User not found")
        
        user = users_db[current_user_id]
        
        # Simulate additional profile data loading
        await asyncio.sleep(0.1)
        
        profile = {
            "user": user.dict(),
            "profile": {
                "last_login": "2023-12-01T10:30:00Z",
                "preferences": {"theme": "dark", "notifications": True},
                "stats": {"logins": 42, "posts": 15}
            }
        }
        
        span.set_attribute("profile.loaded", True)
        return profile

# Background task function
async def process_batch_async(items: list[str], tracer):
    """Process batch items asynchronously in background."""
    with tracer.start_as_current_span("background_batch_processing") as span:
        span.set_attribute("batch.size", len(items))
        span.set_attribute("batch.background", True)
        
        logger.info(f"Starting background processing of {len(items)} items")
        
        for i, item in enumerate(items):
            with tracer.start_as_current_span(f"background_process_item_{i}") as item_span:
                item_span.set_attribute("item.index", i)
                item_span.set_attribute("item.value", item)
                
                # Simulate processing time
                await asyncio.sleep(0.5)
                
                logger.info(f"Processed item {i}: {item}")
        
        span.set_attribute("batch.completed", True)
        logger.info("Background batch processing completed")

# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler."""
    logger.exception("Unhandled exception occurred")
    
    # Add error information to current span if available
    from opentelemetry import trace
    current_span = trace.get_current_span()
    if current_span:
        current_span.record_exception(exc)
        current_span.set_attribute("error", True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Print some helpful information
    print("\n🚀 Starting FastAPI application with OpenTelemetry tracing")
    print("="*60)
    print(f"Service Name: {os.getenv('OTEL_SERVICE_NAME', 'fastapi-example-app')}")
    print(f"Exporter Type: {os.getenv('OTEL_EXPORTER_TYPE', 'console')}")
    print(f"Environment: {os.getenv('OTEL_DEPLOYMENT_ENVIRONMENT', 'development')}")
    print("\n📍 Available endpoints:")
    print("  GET  /                      - Hello world")
    print("  GET  /health                - Health check (not traced)")
    print("  GET  /api/users             - Get all users")
    print("  GET  /api/users/<id>        - Get user by ID")
    print("  POST /api/users             - Create new user")
    print("  GET  /api/slow              - Slow endpoint (2s)")
    print("  GET  /api/external          - External API call")
    print("  POST /api/batch             - Batch processing")
    print("  GET  /api/user-profile      - User profile with dependency")
    print("  GET  /docs                  - API documentation")
    print("\n🔍 Try these examples:")
    print("  curl http://localhost:8000/")
    print("  curl http://localhost:8000/api/users")
    print("  curl http://localhost:8000/api/users/1")
    print("  curl http://localhost:8000/api/users/999  # Error case")
    print("  curl http://localhost:8000/api/slow")
    print("  curl http://localhost:8000/api/external")
    print('  curl -X POST http://localhost:8000/api/users -H "Content-Type: application/json" -d \'{"name":"David","email":"david@example.com"}\'')
    print('  curl -X POST http://localhost:8000/api/batch -H "Content-Type: application/json" -d \'{"items":["a","b","c"],"process_async":false}\'')
    print("\n" + "="*60)
    
    # Run the app
    uvicorn.run(
        "examples.fastapi_app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to avoid double instrumentation
        access_log=True
    ) 