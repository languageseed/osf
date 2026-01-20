"""
Network API Endpoints

Provides access to network state and interactive agent chat.
These endpoints are for real-time interactions between clock ticks.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json

from google import genai
from google.genai import types
import structlog

from src.config import get_settings
from src.services.network_clock import get_network_clock

logger = structlog.get_logger()
settings = get_settings()

router = APIRouter(prefix="/network", tags=["Network"])


# =============================================================================
# Request/Response Models
# =============================================================================

class NetworkStateResponse(BaseModel):
    """Current network state summary."""
    month: int
    property_count: int
    participant_count: int
    total_value: float
    average_yield: float
    market_trend: str
    active_proposals: int


class GovernorChatRequest(BaseModel):
    """Request to chat with the Network Governor."""
    message: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class GovernorChatResponse(BaseModel):
    """Response from the Network Governor."""
    response: str
    month: int
    suggestions: Optional[List[str]] = None


class PropertySummary(BaseModel):
    """Summary of a property."""
    id: str
    address: str
    suburb: str
    valuation: float
    yield_percent: float
    network_ownership: float
    status: str


class ParticipantSummary(BaseModel):
    """Summary of a participant."""
    id: str
    name: str
    type: str
    role: str
    balance: float
    holdings_count: int


# =============================================================================
# Network State Endpoints
# =============================================================================

@router.get("/state", response_model=NetworkStateResponse)
async def get_network_state(request: Request):
    """
    Get current network state summary.
    
    Returns high-level metrics about the network.
    """
    # Get state from app
    if not hasattr(request.app.state, 'network_state'):
        raise HTTPException(500, "Network state not initialized")
    
    state = request.app.state.network_state
    
    # Calculate totals
    total_value = sum(p.valuation * p.network_ownership for p in state.properties)
    avg_yield = sum(p.gross_yield for p in state.properties) / max(len(state.properties), 1)
    
    return NetworkStateResponse(
        month=state.month,
        property_count=len(state.properties),
        participant_count=len(state.participants),
        total_value=total_value,
        average_yield=avg_yield,
        market_trend=state.market_conditions.get("wa_market_trend", "stable"),
        active_proposals=len([p for p in state.governance_proposals if p.get("status") == "voting"]),
    )


@router.get("/properties", response_model=List[PropertySummary])
async def get_properties(request: Request):
    """Get all properties in the network."""
    if not hasattr(request.app.state, 'network_state'):
        raise HTTPException(500, "Network state not initialized")
    
    state = request.app.state.network_state
    
    return [
        PropertySummary(
            id=p.id,
            address=p.address,
            suburb=p.suburb,
            valuation=p.valuation,
            yield_percent=p.gross_yield,
            network_ownership=p.network_ownership,
            status=p.status,
        )
        for p in state.properties
    ]


@router.get("/participants", response_model=List[ParticipantSummary])
async def get_participants(request: Request):
    """Get all participants in the network."""
    if not hasattr(request.app.state, 'network_state'):
        raise HTTPException(500, "Network state not initialized")
    
    state = request.app.state.network_state
    
    return [
        ParticipantSummary(
            id=p.id,
            name=p.name,
            type=p.type,
            role=p.role,
            balance=p.balance,
            holdings_count=len(p.holdings),
        )
        for p in state.participants
    ]


# =============================================================================
# Governor Chat (Interactive Agent)
# =============================================================================

GOVERNOR_SYSTEM_PROMPT = """You are the OSF Network Governor, an AI assistant that helps users understand and interact with the OSF property tokenization simulation.

Your role:
- Explain how the network works
- Answer questions about properties, investments, and governance
- Provide insights about the current network state
- Suggest actions users might want to take
- Be educational and encouraging

Context:
- This is a SIMULATION for learning about property tokenization
- No real money or assets are involved
- Users can invest virtual funds, vote on governance, and explore different roles

Current Network State:
{network_context}

Be helpful, friendly, and educational. Keep responses concise but informative."""


@router.post("/governor/chat", response_model=GovernorChatResponse)
async def chat_with_governor(request: Request, chat_request: GovernorChatRequest):
    """
    Chat with the Network Governor AI.
    
    This is for interactive queries between clock ticks.
    The Governor can answer questions about the network, explain concepts,
    and suggest actions.
    """
    if not hasattr(request.app.state, 'network_state'):
        raise HTTPException(500, "Network state not initialized")
    
    state = request.app.state.network_state
    
    # Build context
    network_context = {
        "month": state.month,
        "properties": len(state.properties),
        "total_value": sum(p.valuation * p.network_ownership for p in state.properties),
        "participants": len(state.participants),
        "npcs": sum(1 for p in state.participants if p.type == "npc"),
        "market_trend": state.market_conditions.get("wa_market_trend"),
        "interest_rate": state.market_conditions.get("interest_rate"),
        "active_proposals": len([p for p in state.governance_proposals if p.get("status") == "voting"]),
    }
    
    # Add user context if provided
    if chat_request.user_id:
        user = next((p for p in state.participants if p.id == chat_request.user_id), None)
        if user:
            network_context["user"] = {
                "name": user.name,
                "role": user.role,
                "balance": user.balance,
                "holdings": len(user.holdings),
            }
    
    # Check if Gemini is configured
    if not settings.google_api_key:
        return GovernorChatResponse(
            response=f"Hello! I'm the Network Governor. We're currently in Month {state.month} of the simulation. "
                     f"The network has {len(state.properties)} properties worth ${sum(p.valuation for p in state.properties):,.0f} total. "
                     f"For full AI responses, please configure the GOOGLE_API_KEY.",
            month=state.month,
            suggestions=["View properties", "Check your portfolio", "Explore governance"],
        )
    
    # Call Gemini
    try:
        client = genai.Client(api_key=settings.google_api_key)
        
        system_prompt = GOVERNOR_SYSTEM_PROMPT.format(
            network_context=json.dumps(network_context, indent=2)
        )
        
        response = await client.aio.models.generate_content(
            model=settings.gemini_model,
            contents=[types.Content(
                role="user",
                parts=[types.Part.from_text(text=chat_request.message)]
            )],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                max_output_tokens=1024,
            ),
        )
        
        # Generate suggestions based on context
        suggestions = []
        if not chat_request.user_id:
            suggestions.append("Sign up as an investor")
        if state.governance_proposals:
            suggestions.append("Vote on active proposals")
        if any(p.status == "available" for p in state.properties):
            suggestions.append("Explore available properties")
        
        logger.info("governor_chat_completed",
                   user_id=chat_request.user_id,
                   message_length=len(chat_request.message),
                   response_length=len(response.text))
        
        return GovernorChatResponse(
            response=response.text,
            month=state.month,
            suggestions=suggestions if suggestions else None,
        )
        
    except Exception as e:
        logger.error("governor_chat_error", error=str(e))
        return GovernorChatResponse(
            response=f"I apologize, but I'm having trouble processing your request right now. "
                     f"The network is currently in Month {state.month}. Please try again shortly.",
            month=state.month,
        )


@router.get("/governor/chat/stream")
async def stream_chat_with_governor(
    request: Request,
    message: str,
    user_id: Optional[str] = None,
):
    """
    Stream a response from the Network Governor.
    
    Returns Server-Sent Events for real-time streaming.
    """
    if not hasattr(request.app.state, 'network_state'):
        raise HTTPException(500, "Network state not initialized")
    
    state = request.app.state.network_state
    
    # Build context (same as above)
    network_context = {
        "month": state.month,
        "properties": len(state.properties),
        "total_value": sum(p.valuation * p.network_ownership for p in state.properties),
        "market_trend": state.market_conditions.get("wa_market_trend"),
    }
    
    async def generate():
        if not settings.google_api_key:
            yield f"data: {json.dumps({'type': 'token', 'content': 'Gemini not configured. '})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return
        
        try:
            client = genai.Client(api_key=settings.google_api_key)
            
            system_prompt = GOVERNOR_SYSTEM_PROMPT.format(
                network_context=json.dumps(network_context, indent=2)
            )
            
            stream = await client.aio.models.generate_content_stream(
                model=settings.gemini_model,
                contents=[types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=message)]
                )],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    max_output_tokens=1024,
                ),
            )
            async for chunk in stream:
                if chunk.text:
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk.text})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            logger.error("governor_stream_error", error=str(e))
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# =============================================================================
# Portfolio Advisor (Interactive Agent)
# =============================================================================

ADVISOR_SYSTEM_PROMPT = """You are the OSF Portfolio Advisor, an AI assistant that helps investors make informed decisions in the OSF property tokenization simulation.

Your role:
- Analyze the user's current portfolio
- Suggest investment opportunities based on their goals
- Explain risks and potential returns
- Provide educational insights about property investment
- Be balanced - highlight both opportunities and risks

IMPORTANT: This is a SIMULATION. No real money is involved. Your advice is for educational purposes.

User's Portfolio:
{portfolio_context}

Available Properties:
{properties_context}

Market Conditions:
{market_context}

Provide helpful, balanced advice. Be specific about numbers when relevant."""


class AdvisorRequest(BaseModel):
    """Request for portfolio advice."""
    user_id: str
    question: str


class AdvisorResponse(BaseModel):
    """Response from portfolio advisor."""
    advice: str
    portfolio_summary: Dict[str, Any]
    opportunities: Optional[List[Dict[str, Any]]] = None


@router.post("/advisor/portfolio", response_model=AdvisorResponse)
async def get_portfolio_advice(request: Request, advisor_request: AdvisorRequest):
    """
    Get personalized portfolio advice.
    
    The Portfolio Advisor analyzes your holdings and provides
    investment suggestions and insights.
    """
    if not hasattr(request.app.state, 'network_state'):
        raise HTTPException(500, "Network state not initialized")
    
    state = request.app.state.network_state
    
    # Find user
    user = next((p for p in state.participants if p.id == advisor_request.user_id), None)
    if not user:
        raise HTTPException(404, f"User {advisor_request.user_id} not found")
    
    # Build portfolio context
    portfolio_value = 0
    holdings_detail = []
    for h in user.holdings:
        prop = next((p for p in state.properties if p.id == h.get("property_id")), None)
        if prop:
            value = prop.valuation * h.get("percent", 0)
            portfolio_value += value
            holdings_detail.append({
                "property": prop.address,
                "suburb": prop.suburb,
                "percent_owned": h.get("percent", 0) * 100,
                "value": value,
                "yield": prop.gross_yield,
            })
    
    portfolio_context = {
        "name": user.name,
        "role": user.role,
        "cash_balance": user.balance,
        "portfolio_value": portfolio_value,
        "total_assets": user.balance + portfolio_value,
        "holdings": holdings_detail,
    }
    
    # Available properties
    available = [p for p in state.properties if p.network_ownership < 1.0]
    properties_context = [
        {
            "address": p.address,
            "suburb": p.suburb,
            "price_per_percent": p.valuation / 100,
            "yield": p.gross_yield,
            "available_percent": (1 - p.network_ownership) * 100,
        }
        for p in available
    ]
    
    # Market context
    market_context = state.market_conditions
    
    # Generate advice
    if not settings.google_api_key:
        return AdvisorResponse(
            advice=f"Your portfolio is worth ${portfolio_value:,.0f} plus ${user.balance:,.0f} cash. "
                   f"Consider diversifying across the {len(available)} available properties. "
                   f"Configure GOOGLE_API_KEY for personalized AI advice.",
            portfolio_summary=portfolio_context,
            opportunities=[{"property": p.address, "yield": p.gross_yield} for p in available[:3]],
        )
    
    try:
        client = genai.Client(api_key=settings.google_api_key)
        
        system_prompt = ADVISOR_SYSTEM_PROMPT.format(
            portfolio_context=json.dumps(portfolio_context, indent=2),
            properties_context=json.dumps(properties_context, indent=2),
            market_context=json.dumps(market_context, indent=2),
        )
        
        response = await client.aio.models.generate_content(
            model=settings.gemini_model,
            contents=[types.Content(
                role="user",
                parts=[types.Part.from_text(text=advisor_request.question)]
            )],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                max_output_tokens=1500,
            ),
        )
        
        # Generate opportunities
        opportunities = [
            {
                "property": p.address,
                "suburb": p.suburb,
                "yield": p.gross_yield,
                "min_investment": p.valuation / 100,  # 1%
            }
            for p in sorted(available, key=lambda x: -x.gross_yield)[:3]
        ]
        
        logger.info("advisor_completed",
                   user_id=advisor_request.user_id,
                   portfolio_value=portfolio_value)
        
        return AdvisorResponse(
            advice=response.text,
            portfolio_summary=portfolio_context,
            opportunities=opportunities,
        )
        
    except Exception as e:
        logger.error("advisor_error", error=str(e))
        return AdvisorResponse(
            advice=f"I apologize, but I'm having trouble generating advice right now. "
                   f"Your portfolio is worth ${portfolio_value:,.0f}. Please try again shortly.",
            portfolio_summary=portfolio_context,
        )


# =============================================================================
# Network History (Database Queries)
# =============================================================================

class SnapshotResponse(BaseModel):
    """Network snapshot data."""
    month: int
    total_properties: int
    total_participants: int
    total_valuation: float
    avg_token_price: float
    avg_yield: float
    actions_processed: int
    dividends_paid: float
    rent_collected: float
    governor_summary: Optional[str] = None
    created_at: str


class EventResponse(BaseModel):
    """Network event data."""
    id: str
    month: int
    event_type: str
    title: str
    description: str
    severity: str
    created_at: str


@router.get("/history/snapshots", response_model=List[SnapshotResponse])
async def get_snapshots(
    months: int = 12,
):
    """Get historical network snapshots."""
    from src.database import async_session
    from src.repositories import NetworkRepository
    
    try:
        async with async_session() as session:
            repo = NetworkRepository(session)
            snapshots = await repo.get_snapshots(limit=months)
            
            return [
                SnapshotResponse(
                    month=s.network_month,
                    total_properties=s.total_properties,
                    total_participants=s.total_participants,
                    total_valuation=float(s.total_valuation),
                    avg_token_price=float(s.avg_token_price),
                    avg_yield=float(s.avg_yield),
                    actions_processed=s.actions_processed,
                    dividends_paid=float(s.dividends_paid),
                    rent_collected=float(s.rent_collected),
                    governor_summary=s.governor_summary,
                    created_at=s.created_at.isoformat(),
                )
                for s in snapshots
            ]
    except Exception as e:
        logger.error("get_snapshots_error", error=str(e))
        return []


@router.get("/history/events", response_model=List[EventResponse])
async def get_events(
    month: Optional[int] = None,
    event_type: Optional[str] = None,
    limit: int = 50,
):
    """Get network events with optional filters."""
    from src.database import async_session
    from src.repositories import NetworkRepository
    
    try:
        async with async_session() as session:
            repo = NetworkRepository(session)
            events = await repo.get_events(
                network_month=month,
                event_type=event_type,
                limit=limit,
            )
            
            return [
                EventResponse(
                    id=e.id,
                    month=e.network_month,
                    event_type=e.event_type,
                    title=e.title,
                    description=e.description,
                    severity=e.severity,
                    created_at=e.created_at.isoformat(),
                )
                for e in events
            ]
    except Exception as e:
        logger.error("get_events_error", error=str(e))
        return []


@router.get("/history/metrics")
async def get_metrics_history(
    months: int = 12,
):
    """Get historical metrics for charts."""
    from src.database import async_session
    from src.repositories import NetworkRepository
    
    try:
        async with async_session() as session:
            repo = NetworkRepository(session)
            return await repo.get_metrics_history(months=months)
    except Exception as e:
        logger.error("get_metrics_error", error=str(e))
        return []


# =============================================================================
# NPC Endpoints
# =============================================================================

class NPCSummary(BaseModel):
    """Summary of an NPC participant."""
    id: str
    name: str
    personality: str
    role: str
    backstory: str
    risk_tolerance: float
    activity_level: float
    goals: List[Dict[str, Any]]


@router.get("/npcs", response_model=List[NPCSummary])
async def list_npcs():
    """Get all NPC participants with their personalities and goals."""
    from src.services.npc_system import get_npc_manager
    
    try:
        npc_manager = get_npc_manager()
        await npc_manager.initialize()
        return npc_manager.get_npc_summaries()
    except Exception as e:
        logger.error("list_npcs_error", error=str(e))
        return []


@router.get("/npcs/{npc_id}")
async def get_npc(npc_id: str):
    """Get detailed information about a specific NPC."""
    from src.services.npc_system import get_npc_manager
    from src.database import async_session
    from src.repositories import ParticipantRepository
    
    try:
        npc_manager = get_npc_manager()
        await npc_manager.initialize()
        
        if npc_id not in npc_manager.npcs:
            raise HTTPException(status_code=404, detail="NPC not found")
        
        npc = npc_manager.npcs[npc_id]
        
        # Get holdings from database
        async with async_session() as session:
            repo = ParticipantRepository(session)
            participant = await repo.get_by_id(npc_id)
            holdings = await repo.get_holdings(npc_id)
        
        return {
            "id": npc.id,
            "name": npc.name,
            "personality": npc.personality.value,
            "role": npc.role.value,
            "backstory": npc.backstory,
            "risk_tolerance": npc.risk_tolerance,
            "activity_level": npc.activity_level,
            "patience": npc.patience,
            "contrarian": npc.contrarian,
            "loyalty": npc.loyalty,
            "preferences": npc.preferences,
            "goals": [
                {
                    "type": g.goal_type,
                    "target": float(g.target_value),
                    "priority": g.priority,
                    "progress": float(g.progress),
                    "completed": g.completed,
                }
                for g in npc.goals
            ],
            "balance": float(participant.balance) if participant else 0,
            "holdings": [
                {
                    "property_id": h.property_id,
                    "tokens": float(h.token_amount),
                    "avg_price": float(h.avg_purchase_price),
                }
                for h in holdings
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_npc_error", npc_id=npc_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/npcs/initialize")
async def initialize_npcs():
    """Initialize NPC participants (creates database records)."""
    from src.services.npc_system import get_npc_manager
    
    try:
        npc_manager = get_npc_manager()
        count = await npc_manager.initialize()
        return {
            "message": f"Initialized {count} NPCs",
            "npc_count": count,
        }
    except Exception as e:
        logger.error("initialize_npcs_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Events & Economy Endpoints
# =============================================================================

class EconomicStateResponse(BaseModel):
    """Current economic conditions."""
    phase: str
    interest_rate: float
    inflation_rate: float
    unemployment_rate: float
    housing_index: float
    consumer_confidence: int
    months_in_phase: int


class GenerateEventsRequest(BaseModel):
    """Request to generate events for a month."""
    month: Optional[int] = None


@router.get("/economy", response_model=EconomicStateResponse)
async def get_economic_state():
    """Get current economic conditions affecting the simulation."""
    from src.services.event_generator import get_event_generator
    
    generator = get_event_generator()
    state = generator.get_economic_state()
    
    return EconomicStateResponse(**state)


@router.post("/events/generate")
async def generate_events(request: GenerateEventsRequest):
    """Generate events for the current or specified month."""
    from src.services.event_generator import get_event_generator
    from src.services.network_clock import get_network_clock
    
    generator = get_event_generator()
    clock = get_network_clock()
    
    month = request.month or clock.current_month
    
    # Get properties for event context
    network_state = getattr(clock, '_last_state', None)
    properties = []
    if network_state:
        properties = [
            {
                "id": p.id,
                "address": p.address,
                "suburb": p.suburb,
                "property_type": p.property_type,
                "weekly_rent": p.weekly_rent,
            }
            for p in getattr(network_state, 'properties', [])
        ]
    
    # Generate events
    events = generator.generate_events(
        network_month=month,
        properties=properties,
        participants=[],
    )
    
    # Save to database
    saved = await generator.save_events(events)
    
    # Generate news article
    news = await generator.generate_news_article(events, month)
    
    return {
        "month": month,
        "events_generated": len(events),
        "events_saved": saved,
        "events": [e.to_dict() for e in events],
        "news_summary": news,
        "economic_state": generator.get_economic_state(),
    }


@router.get("/news/{month}")
async def get_monthly_news(month: int):
    """Get news summary for a specific month."""
    from src.database import async_session
    from src.repositories import NetworkRepository
    from src.services.event_generator import get_event_generator, SimulationEvent, EventCategory, EventSeverity
    
    try:
        async with async_session() as session:
            repo = NetworkRepository(session)
            db_events = await repo.get_events(network_month=month, limit=10)
            
            if not db_events:
                return {
                    "month": month,
                    "news": "No events recorded for this month.",
                    "events": [],
                }
            
            # Convert to SimulationEvent objects for news generation
            events = []
            for e in db_events:
                events.append(SimulationEvent(
                    id=e.id,
                    category=EventCategory(e.event_type) if e.event_type in [c.value for c in EventCategory] else EventCategory.MARKET,
                    severity=EventSeverity(e.severity) if e.severity in [s.value for s in EventSeverity] else EventSeverity.INFO,
                    title=e.title,
                    description=e.description or "",
                    impact={},
                    narrative="",
                    month=e.network_month,
                ))
            
            # Generate news
            generator = get_event_generator()
            news = await generator.generate_news_article(events, month)
            
            return {
                "month": month,
                "news": news,
                "events": [
                    {
                        "id": e.id,
                        "title": e.title,
                        "description": e.description,
                        "type": e.event_type,
                        "severity": e.severity,
                    }
                    for e in db_events
                ],
            }
    except Exception as e:
        logger.error("get_news_error", month=month, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feed")
async def get_event_feed(
    limit: int = 20,
    category: Optional[str] = None,
):
    """Get recent events as a news feed."""
    from src.database import async_session
    from src.repositories import NetworkRepository
    
    try:
        async with async_session() as session:
            repo = NetworkRepository(session)
            events = await repo.get_events(
                event_type=category,
                limit=limit,
            )
            
            return {
                "events": [
                    {
                        "id": e.id,
                        "month": e.network_month,
                        "title": e.title,
                        "description": e.description,
                        "type": e.event_type,
                        "severity": e.severity,
                        "created_at": e.created_at.isoformat(),
                    }
                    for e in events
                ],
                "total": len(events),
            }
    except Exception as e:
        logger.error("get_feed_error", error=str(e))
        return {"events": [], "total": 0}
