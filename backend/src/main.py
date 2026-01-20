"""
OSF Demo - FastAPI Application
Open Source Fund Demo for Gemini 3 Hackathon

This demonstrates the OSF Framework across multiple asset classes:
- OSF-Property: Real estate (tenants, maintenance, valuations)
- OSF-Energy: Solar/wind/battery (monitoring, performance, grid)

Core Features:
- Unified AI Core that adapts to any asset class
- Document processing with Gemini Vision
- Asset-specific triage and management
- Mock blockchain for ownership tracking
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import structlog

from src.config import get_settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    logger.info("starting_ospf_demo", version=settings.app_version)
    
    # Initialize database
    from src.database import init_db, close_db
    await init_db()
    logger.info("database_ready")
    
    # Startup - Initialize network clock and batch processor
    from src.services.network_clock import get_network_clock, ClockPreset, PendingAction
    from src.services.batch_processor import (
        get_batch_processor, 
        generate_demo_state, 
        generate_demo_precomputed,
        NetworkState,
    )
    
    # Import models to ensure they're registered with SQLAlchemy
    from src.models import Participant, NetworkSnapshot, PropertyState  # noqa: F401
    
    clock = get_network_clock()
    processor = get_batch_processor()
    
    # Network state (in-memory for demo)
    # In production, this would be loaded from database
    network_state = generate_demo_state(month=0)
    
    # Store state in app for access by endpoints
    app.state.network_state = network_state
    
    # Define tick handler - this is called each time the clock advances
    async def on_tick(pending_actions: list[PendingAction]) -> dict:
        """Process monthly tick with batch processor."""
        nonlocal network_state
        import time
        from decimal import Decimal
        from src.database import async_session
        from src.repositories import NetworkRepository, ParticipantRepository
        from src.services.action_processor import get_action_processor
        
        start_time = time.time()
        
        logger.info("tick_handler_called", 
                   month=network_state.month,
                   pending_actions=len(pending_actions))
        
        # Process database-queued actions first
        action_processor = get_action_processor()
        db_actions_processed = 0
        try:
            async with async_session() as session:
                participant_repo = ParticipantRepository(session)
                db_pending = await participant_repo.get_pending_actions(network_state.month)
                
                if db_pending:
                    logger.info("processing_db_actions", count=len(db_pending))
                    for action in db_pending:
                        result_action = await action_processor.process_action(
                            participant_id=action.participant_id,
                            action_type=action.action_type,
                            action_data=action.action_data,
                            network_month=network_state.month,
                        )
                        await participant_repo.complete_action(
                            action_id=action.id,
                            result=result_action.data or {},
                            error=result_action.error,
                        )
                        db_actions_processed += 1
                    await session.commit()
        except Exception as e:
            logger.error("db_action_processing_failed", error=str(e))
        
        # Process NPC decisions
        npc_actions_processed = 0
        try:
            from src.services.npc_system import get_npc_manager
            npc_manager = get_npc_manager()
            
            # Convert properties to dict format for NPCs
            properties_for_npcs = [
                {
                    "id": p.id,
                    "property_id": p.id,
                    "address": p.address,
                    "yield": p.weekly_rent * 52 / p.valuation * 100 if p.valuation else 4.0,
                    "token_price": 1.0,  # Default token price
                    "valuation": p.valuation,
                }
                for p in network_state.properties
            ]
            
            npc_results = await npc_manager.process_tick(
                network_month=network_state.month,
                properties=properties_for_npcs,
                market_conditions=network_state.market_conditions,
            )
            npc_actions_processed = len(npc_results)
            logger.info("npc_tick_processed", actions=npc_actions_processed)
        except Exception as e:
            logger.error("npc_processing_failed", error=str(e))
        
        # Generate simulation events
        generated_events = []
        try:
            from src.services.event_generator import get_event_generator
            event_generator = get_event_generator()
            
            properties_for_events = [
                {
                    "id": p.id,
                    "address": p.address,
                    "suburb": p.suburb,
                    "property_type": p.property_type,
                    "weekly_rent": p.weekly_rent,
                }
                for p in network_state.properties
            ]
            
            generated_events = event_generator.generate_events(
                network_month=network_state.month,
                properties=properties_for_events,
                participants=[p.name for p in network_state.participants],
            )
            
            # Update market conditions based on economic state
            econ_state = event_generator.get_economic_state()
            network_state.market_conditions["economic_phase"] = econ_state["phase"]
            network_state.market_conditions["interest_rate"] = econ_state["interest_rate"]
            network_state.market_conditions["consumer_confidence"] = econ_state["consumer_confidence"]
            
            logger.info("events_generated", count=len(generated_events))
        except Exception as e:
            logger.error("event_generation_failed", error=str(e))
        
        # Generate pre-computed results
        precomputed = generate_demo_precomputed(network_state)
        
        # Process the month with Gemini
        result = await processor.process_month(
            state=network_state,
            pending_actions=pending_actions,
            precomputed=precomputed,
        )
        
        # Update network state for next month
        network_state.month = result.month
        network_state.recent_history = [
            {"month": result.month, "summary": result.governor_summary}
        ] + network_state.recent_history[:2]  # Keep last 3
        
        # Store updated state
        app.state.network_state = network_state
        
        # Persist to database
        processing_time_ms = int((time.time() - start_time) * 1000)
        try:
            async with async_session() as session:
                network_repo = NetworkRepository(session)
                
                # Create snapshot
                await network_repo.create_snapshot(
                    network_month=result.month,
                    total_properties=len(network_state.properties),
                    total_participants=len(network_state.participants),
                    total_valuation=Decimal(str(precomputed.total_valuation)),
                    avg_token_price=Decimal(str(precomputed.avg_token_price)),
                    avg_yield=Decimal(str(network_state.market_conditions.get("avg_yield", 4.2))),
                    actions_processed=len(pending_actions) + db_actions_processed + npc_actions_processed,
                    dividends_paid=Decimal(str(precomputed.dividends)),
                    rent_collected=Decimal(str(precomputed.rent)),
                    governor_summary=result.governor_summary,
                    batch_response=result.to_dict(),
                    processing_time_ms=processing_time_ms,
                )
                
                # Record Gemini-generated events
                for event in result.events:
                    await network_repo.create_event(
                        network_month=result.month,
                        event_type=event.get("type", "general"),
                        title=event.get("title", "Network Event"),
                        description=event.get("description", ""),
                        severity=event.get("severity", "info"),
                        data=event,
                    )
                
                # Record simulation-generated events
                for event in generated_events:
                    await network_repo.create_event(
                        network_month=result.month,
                        event_type=event.category.value,
                        title=event.title,
                        description=event.description,
                        severity=event.severity.value,
                        property_id=event.property_id,
                        participant_id=event.participant_id,
                        data=event.to_dict(),
                    )
                
                await session.commit()
                logger.info("tick_state_persisted", 
                           month=result.month,
                           gemini_events=len(result.events),
                           sim_events=len(generated_events))
        except Exception as e:
            logger.error("tick_persistence_failed", error=str(e))
        
        logger.info("tick_handler_completed",
                   new_month=result.month,
                   events=len(result.events),
                   processing_time_ms=processing_time_ms,
                   summary=result.governor_summary[:100] if result.governor_summary else "")
        
        return result.to_dict()
    
    # Register tick handler
    clock.on_tick(on_tick)
    
    # Default to DEMO preset (5 min), can be changed via API
    # For testing, use: POST /api/v1/network/clock/preset {"preset": "test"}
    await clock.start()
    logger.info("network_clock_started", 
               preset=clock.config.preset.value,
               interval=clock.config.interval_seconds)
    
    yield
    
    # Shutdown - Stop the clock and close database
    await clock.stop()
    await close_db()
    logger.info("shutting_down_ospf_demo")


app = FastAPI(
    title="OSF Demo API",
    description="""
## Open Source Fund (OSF) Demo

A demonstration of the OSF Framework - transparent, AI-managed investment across asset classes.

**Hackathon Track:** 🧠 Marathon Agent - Autonomous asset management at scale

### Supported Asset Classes

| Class | Token | Features |
|-------|-------|----------|
| **Property** | OSF | Tenant chat, maintenance triage, screening, valuations |
| **Energy** | OSEF | Production monitoring, performance analysis, alerts |

### Key Innovation

One AI Core (powered by Gemini) that adapts to any asset class while sharing:
- Communication engine
- Document processing
- Triage and classification
- Fraud detection

### Endpoints

- `/health` - Health check with capabilities
- `/api/v1/chat` - Unified chat (property or energy)
- `/api/v1/properties` - Property assets
- `/api/v1/energy` - Energy assets (solar, wind, battery)
- `/api/v1/screening` - Tenant screening
- `/api/v1/maintenance` - Maintenance triage
    """,
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS - Allow frontend access
# Note: FastAPI CORS middleware doesn't support wildcards in subdomains
# Using allow_origin_regex for Vercel preview deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local frontend
        "http://localhost:5174",  # Alternative local port
        "http://localhost:5175",  # Alternative local port
        "http://localhost:5176",  # Alternative local port
        "http://localhost:3000",  # Alternative local
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",  # Vercel preview deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handling middleware
from src.middleware import setup_error_handlers
setup_error_handlers(app)


# ============================================
# Security Middleware
# ============================================
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    """Check API key for protected endpoints."""
    # Public endpoints
    public_paths = ["/", "/health", "/docs", "/openapi.json", "/redoc"]
    if request.url.path in public_paths:
        return await call_next(request)
    
    # Check API key if required
    if settings.require_api_key:
        api_key = request.headers.get("X-API-Key")
        if api_key != settings.api_secret_key:
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid or missing API key"}
            )
    
    return await call_next(request)


# ============================================
# Health & Info Endpoints
# ============================================
@app.get("/", tags=["Info"])
async def root():
    """API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Open Source Property Fund Demo",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Info"])
async def health():
    """Health check with capability status."""
    gemini_configured = bool(settings.google_api_key)
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
        "capabilities": {
            "gemini": gemini_configured,
            "database": True,
            "redis": True,
        },
        "asset_classes": {
            "property": {
                "enabled": True,
                "features": ["chat", "maintenance", "screening", "valuation"],
            },
            "energy": {
                "enabled": True,
                "features": ["chat", "monitoring", "alerts", "triage"],
            },
        },
        "ai_core": {
            "communication": gemini_configured,
            "document_processing": gemini_configured,
            "triage": gemini_configured,
            "fraud_detection": gemini_configured,
        },
    }


# ============================================
# API Routes
# ============================================

from src.api.chat import router as chat_router
from src.api.screening import router as screening_router
from src.api.maintenance import router as maintenance_router
from src.api.energy import router as energy_router
from src.api.simulation import router as simulation_router
from src.api.clock import router as clock_router
from src.api.network import router as network_router
from src.api.pool import router as pool_router
from src.api.participant import router as participant_router
from src.auth import auth_router

# Auth routes (no prefix - /auth/*)
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])

app.include_router(chat_router, prefix="/api/v1/chat", tags=["OSF AI Chat"])
app.include_router(screening_router, prefix="/api/v1/screening", tags=["OSF-Property: Screening"])
app.include_router(maintenance_router, prefix="/api/v1/maintenance", tags=["OSF-Property: Maintenance"])
app.include_router(energy_router, prefix="/api/v1/energy", tags=["OSF-Energy: Monitoring"])
app.include_router(simulation_router, prefix="/api/v1/sim", tags=["Simulation Mode"])
app.include_router(clock_router, prefix="/api/v1", tags=["Network Clock"])
app.include_router(network_router, prefix="/api/v1", tags=["Network State & Agents"])
app.include_router(pool_router, prefix="/api/v1", tags=["Asset Pools"])
app.include_router(participant_router, prefix="/api/v1", tags=["Participants"])


# ============================================
# Asset Viewer (for development/demo)
# ============================================

@app.get("/viewer")
async def asset_viewer():
    """Serve the asset viewer HTML page."""
    viewer_path = Path("data/viewer.html")
    if viewer_path.exists():
        return FileResponse(viewer_path, media_type="text/html")
    return JSONResponse({"error": "Viewer not found"}, status_code=404)


# ============================================
# Placeholder endpoints (to be implemented)
# ============================================
@app.get("/api/v1/properties", tags=["Properties"])
async def properties_list():
    """List properties in the network."""
    # TODO: Implement with database
    return {
        "properties": [
            {
                "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "address": "123 Demo Street, Sydney NSW 2000",
                "type": "apartment",
                "bedrooms": 2,
                "bathrooms": 1,
                "valuation": 850000,
                "status": "active",
            }
        ],
        "total": 1,
    }


@app.get("/api/v1/transactions", tags=["Transactions"])
async def transactions_list():
    """List transactions in the ledger."""
    # TODO: Implement with database
    return {
        "transactions": [
            {
                "id": "tx-001",
                "type": "token_purchase",
                "amount": 10000,
                "token_amount": 10000,
                "timestamp": "2026-01-18T12:00:00Z",
                "status": "completed",
            }
        ],
        "total": 1,
    }


# ============================================
# Error Handlers
# ============================================
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
        }
    )
