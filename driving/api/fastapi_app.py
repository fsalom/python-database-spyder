"""FastAPI application configuration."""

import time
from typing import Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config.settings import settings
from config.database import init_db, close_db

# Import API adapters
from driving.api.users.adapter import UsersAPIAdapter


class RequestCaptureMiddleware(BaseHTTPMiddleware):
    """Custom middleware to capture all HTTP requests with headers and body."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timing
        start_time = time.time()

        # Capture request data if DEBUG is enabled
        if settings.debug:
            await self._capture_request(request, start_time)

        # Process the request
        response = await call_next(request)

        # Log completion
        process_time = time.time() - start_time
        print(
            f"[REQUEST COMPLETED] {request.method} {request.url.path} - {response.status_code} ({process_time:.4f}s)\n"
        )

        return response

    async def _capture_request(self, request: Request, start_time: float):
        """Capture and log request details."""

        # Separate headers into categories
        standard_headers = {}
        custom_headers = {}
        security_headers = {}

        for key, value in request.headers.items():
            key_lower = key.lower()
            if key_lower.startswith('x-'):
                custom_headers[key] = value
            elif key_lower in ['authorization', 'cookie', 'x-api-key', 'x-auth-token']:
                security_headers[key] = (
                    f"[HIDDEN - {len(value)} chars]" if value else None
                )
            else:
                standard_headers[key] = value

        # Capture request body for POST/PUT/PATCH
        body_data = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Read the body
                body = await request.body()
                if body:
                    try:
                        import json
                        body_data = json.loads(body.decode())
                    except json.JSONDecodeError:
                        body_data = {"raw_body": body.decode()[:1000]}  # Limit size
            except Exception as e:
                body_data = {"error": f"Could not read body: {str(e)}"}

        # Format and print the captured data
        print(f"\n[MIDDLEWARE REQUEST CAPTURED]")
        print("=" * 70)
        print(
            f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}"
        )
        print(f"Method: {request.method}")
        print(f"URL: {request.url}")
        print(f"Path: {request.url.path}")
        print(
            f"Client: {request.client.host}:{request.client.port}"
            if request.client
            else "Client: Unknown"
        )
        print(f"User Agent: {request.headers.get('user-agent', 'Not provided')}")

        # Query parameters
        if request.query_params:
            print(f"Query Params: {dict(request.query_params)}")

        # Path parameters
        if hasattr(request, 'path_params') and request.path_params:
            print(f"Path Params: {request.path_params}")

        # Headers
        print(f"\nHEADERS:")
        print("─" * 40)

        if standard_headers:
            print("Standard Headers:")
            for key, value in standard_headers.items():
                print(f"   {key}: {value}")

        if custom_headers:
            print("\nCustom Headers (X-*):")
            for key, value in custom_headers.items():
                print(f"   {key}: {value}")

        if security_headers:
            print("\nSecurity Headers:")
            for key, value in security_headers.items():
                print(f"   {key}: {value}")

        # Request body
        if body_data:
            print(f"\nRequest Body:")
            if isinstance(body_data, dict) and "raw_body" in body_data:
                print(f"   Raw: {body_data['raw_body']}")
            elif isinstance(body_data, dict) and "error" in body_data:
                print(f"   Error: {body_data['error']}")
            else:
                import json
                print(json.dumps(body_data, indent=4))

        print("=" * 70)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting up application...")
    print(f"📝 Environment: {'DEBUG' if settings.debug else 'PRODUCTION'}")
    print(f"🗄️  Database: {settings.database.driver}")

    # Initialize database
    await init_db()
    print("✅ Database initialized")

    yield

    # Shutdown
    print("🛑 Shutting down application...")
    await close_db()
    print("✅ Database connections closed")


def create_fastapi_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        description="FastAPI microservice for dynamic API generation using hexagonal architecture",
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request capture middleware (only in debug mode)
    if settings.debug:
        app.add_middleware(RequestCaptureMiddleware)

    # Initialize adapters
    users_adapter = UsersAPIAdapter()

    # Include routers
    app.include_router(users_adapter.router, prefix=f"{settings.api_v1_prefix}/users", tags=["Users"])

    # Add new routers here as we create them:
    # connections_adapter = ConnectionsAPIAdapter()
    # app.include_router(connections_adapter.router, prefix=settings.api_v1_prefix, tags=["Connections"])

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.version,
        }

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Welcome to Spyder - Dynamic API Generator",
            "docs": "/docs",
            "health": "/health",
        }

    return app


# Create the FastAPI app instance
fastapi_app = create_fastapi_app()
