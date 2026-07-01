import os
import uuid
import httpx
from contextvars import ContextVar
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from microsoft_teams.apps import App, ActivityContext
from microsoft_teams.api import MessageActivity, MessageActivityInput
from microsoft_teams.apps.http.fastapi_adapter import FastAPIAdapter
from azure.identity import ManagedIdentityCredential
from starlette.middleware.base import BaseHTTPMiddleware

from config import config
from api.tools import router as tools_router
from api.health import router as health_router
from services.copilot_service import CopilotService
from observability.logger import logger, log_error
from memory.memory_store import build_redis_client
import uvicorn


# Request Context for Tracing
request_id_var: ContextVar[str] = ContextVar("request_id", default="")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = str(uuid.uuid4())
        token = request_id_var.set(rid)
        
        # Log request start
        logger.info(f"Incoming Request: {request.method} {request.url.path} (request_id: {rid})")
        try:
            response = await call_next(request)
            return response
        finally:
            request_id_var.reset(token)

def create_token_factory():
    def get_token(scopes, tenant_id=None):
        credential = ManagedIdentityCredential(client_id=config.APP_ID)
        if isinstance(scopes, str):
            scopes_list = [scopes]
        else:
            scopes_list = scopes
        return credential.get_token(*scopes_list).token
    return get_token

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Resource Managers
    logger.info("Initializing HTTP client...")
    app.state.http_client = httpx.AsyncClient(timeout=30)
    
    logger.info("Initializing Redis connection...")
    app.state.redis = await build_redis_client()
    
    # Strictly initialize Teams SDK within lifespan
    logger.info("Initializing Teams SDK...")
    await teams.initialize()
    
    logger.info("Application starting up successfully.")
    
    yield
    
    # Graceful shutdown (dependents first)
    logger.info("Closing HTTP client...")
    await app.state.http_client.aclose()
    
    if app.state.redis:
        logger.info("Closing Redis connection...")
        try:
            await app.state.redis.aclose()
        except Exception as e:
            log_error(e, "Redis Shutdown")
            
    logger.info("Application shutdown complete.")


# Strict 5-Step Sequence for Teams SDK

# Step 2: FastAPI app with lifespan
app = FastAPI(
    title="Hybrid SQL Analytics Agent",
    description="SkySecure v3 Compliant Teams Bot + OpenAPI Backend",
    lifespan=lifespan
)

# Register Middleware & Routers
app.add_middleware(RequestLoggingMiddleware)
app.include_router(health_router, tags=["Health"])
app.include_router(tools_router, prefix="/api/tools", tags=["Database Tools"])

# Step 3: Adapter wraps the FastAPI app
adapter = FastAPIAdapter(app=app)

# Step 4: Teams App receives the adapter
teams = App(
    http_server_adapter=adapter,
    client_id=config.APP_ID,
    client_secret=config.APP_PASSWORD,
    token=create_token_factory() if config.APP_TYPE == "UserAssignedMsi" else None
)

# Step 5: Register event handlers
@teams.on_message
async def handle_message(ctx: ActivityContext[MessageActivity]):
    """
    Intercepts the user's message in Teams, forwards it to Copilot Studio,
    and returns the result.
    """
    user_text = ctx.activity.text
    logger.info("Received message from user")
    
    # Dependency Injection: Service classes RECEIVE their infrastructure
    # Access module-level app.state safely
    copilot_service = CopilotService(http_client=app.state.http_client)
    
    # Forward to Copilot Studio with the unique Conversation ID for stateful memory!
    conversation_id = ctx.activity.conversation.id
    ai_response = await copilot_service.send_message(user_text, conversation_id)
    
    # Send back to Teams
    await ctx.send(MessageActivityInput(text=ai_response))

if __name__ == "__main__":
    uvicorn.run(adapter.app, host="0.0.0.0", port=config.PORT)
