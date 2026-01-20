"""
OSF Batch Processor - Monthly Network Simulation

Processes an entire month of network activity in a single Gemini API call.
This is the core of the "one giant prompt" architecture that leverages
Gemini 3's massive context window (1-2M tokens).

Flow:
1. Collect current network state (properties, participants, holdings)
2. Gather all pending user actions
3. Pre-compute deterministic financials (rent, dividends, valuations)
4. Send everything to Gemini for processing
5. Parse response and update state
6. Broadcast results to all clients
"""

import json
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import structlog

from google import genai
from google.genai import types

from src.config import get_settings
from src.services.network_clock import PendingAction

logger = structlog.get_logger()
settings = get_settings()


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class Property:
    """A property in the network."""
    id: str
    address: str
    suburb: str
    state: str
    property_type: str
    bedrooms: int
    bathrooms: int
    valuation: float
    network_ownership: float  # 0.0 - 1.0
    token_price: float
    gross_yield: float
    status: str  # 'available', 'tenanted', 'owner_occupied'
    tenant_id: Optional[str] = None
    weekly_rent: Optional[float] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "address": self.address,
            "suburb": self.suburb,
            "state": self.state,
            "property_type": self.property_type,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "valuation": self.valuation,
            "network_ownership": self.network_ownership,
            "token_price": self.token_price,
            "gross_yield": self.gross_yield,
            "status": self.status,
            "tenant_id": self.tenant_id,
            "weekly_rent": self.weekly_rent,
        }


@dataclass
class Participant:
    """A participant in the network (human or NPC)."""
    id: str
    name: str
    type: str  # 'human', 'npc'
    role: str  # 'investor', 'renter', 'tenant', 'homeowner', 'custodian', 'foundation'
    balance: float
    holdings: List[Dict[str, Any]] = field(default_factory=list)
    
    # NPC-specific
    personality: Optional[Dict[str, float]] = None  # risk_tolerance, patience, etc.
    goal: Optional[str] = None
    
    def to_dict(self) -> dict:
        result = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "role": self.role,
            "balance": self.balance,
            "holdings": self.holdings,
        }
        if self.type == "npc":
            result["personality"] = self.personality
            result["goal"] = self.goal
        return result


@dataclass
class NetworkState:
    """Complete network state for batch processing."""
    month: int
    properties: List[Property]
    participants: List[Participant]
    market_conditions: Dict[str, Any]
    governance_proposals: List[Dict[str, Any]]
    recent_history: List[Dict[str, Any]]  # Last 3 months summary
    
    def to_dict(self) -> dict:
        return {
            "month": self.month,
            "properties": [p.to_dict() for p in self.properties],
            "participants": [p.to_dict() for p in self.participants],
            "market_conditions": self.market_conditions,
            "governance_proposals": self.governance_proposals,
            "recent_history": self.recent_history,
        }


@dataclass
class PreComputedResults:
    """Pre-computed deterministic values."""
    rent_collected: Dict[str, float]  # property_id -> amount
    dividends_per_token: float
    market_change_percent: float
    new_valuations: Dict[str, float]  # property_id -> new value
    
    def to_dict(self) -> dict:
        return {
            "rent_collected": self.rent_collected,
            "dividends_per_token": self.dividends_per_token,
            "market_change_percent": self.market_change_percent,
            "new_valuations": self.new_valuations,
        }


@dataclass
class MonthResult:
    """Result from processing a month."""
    month: int
    events: List[Dict[str, Any]]
    state_changes: Dict[str, Any]
    npc_decisions: List[Dict[str, Any]]
    governor_summary: str
    alerts: List[Dict[str, Any]]
    chat_responses: Dict[str, str]  # user_id -> response
    processing_log: List[str]
    
    def to_dict(self) -> dict:
        return {
            "month": self.month,
            "events": self.events,
            "state_changes": self.state_changes,
            "npc_decisions": self.npc_decisions,
            "governor_summary": self.governor_summary,
            "alerts": self.alerts,
            "chat_responses": self.chat_responses,
            "processing_log": self.processing_log,
        }


# =============================================================================
# Prompt Templates
# =============================================================================

SYSTEM_PROMPT = """You are the OSF Network Simulation Engine, an AI that processes monthly network activity for a property tokenization simulation.

IMPORTANT: This is a SIMULATION for educational purposes. No real money or assets are involved.

Your role is to:
1. Process all user actions fairly and in order
2. Make decisions for NPC participants based on their personalities
3. Resolve conflicts (e.g., multiple buyers for same property tokens)
4. Generate natural language summaries and responses
5. Create realistic but educational simulation outcomes

RULES:
- Process actions in priority order (higher priority first)
- NPCs should make decisions consistent with their personality traits
- First-come-first-served for competing orders at same priority
- No participant can go negative in balance
- Property ownership percentages must sum to 1.0 or less
- Generate engaging narrative that educates users about property investment

OUTPUT FORMAT:
You MUST respond with valid JSON matching this exact structure:
{
  "events": [
    {"type": "string", "actor": "string", "target": "string", "data": {}}
  ],
  "state_changes": {
    "properties": {"property_id": {"field": "new_value"}},
    "participants": {"participant_id": {"field": "new_value"}}
  },
  "npc_decisions": [
    {"npc_id": "string", "decision": "string", "reasoning": "string"}
  ],
  "governor_summary": "A 2-3 sentence summary of the month's activity for all users",
  "alerts": [
    {"to": "user_id", "type": "string", "message": "string"}
  ],
  "chat_responses": {
    "user_id": "Response to their question if they asked one"
  },
  "processing_log": ["Step by step log of what was processed"]
}"""


MONTH_PROMPT_TEMPLATE = """# OSF Network Simulation - Month {next_month}

## Current Network State

### Properties ({property_count} total)
{properties_json}

### Participants ({participant_count} total, {npc_count} NPCs)
{participants_json}

### Market Conditions
{market_json}

### Active Governance Proposals
{governance_json}

## Pre-Computed Results (Already Applied)
These calculations are deterministic and have been pre-computed:
{precomputed_json}

## Pending User Actions ({action_count} actions to process)
Process these in priority order (highest first):
{actions_json}

## Recent History
{history_json}

## Your Tasks for Month {next_month}

1. **Process User Actions**: Execute each pending action, checking balances and availability
2. **NPC Decisions**: For each NPC, decide what they do this month based on their personality:
   - Investors: Should they buy, sell, or hold?
   - Renters: Any issues or requests?
   - Service Providers: Complete any pending tasks
3. **Conflict Resolution**: If multiple participants want the same thing, resolve fairly
4. **Generate Events**: Create event log entries for all activities
5. **Governor Summary**: Write a brief, engaging summary of the month
6. **User Responses**: If any user asked a question, generate a helpful response
7. **Alerts**: Create notifications for important events

Remember: Be educational and engaging. This is a learning simulation."""


# =============================================================================
# Batch Processor
# =============================================================================

class BatchProcessor:
    """
    Processes monthly network updates using Gemini.
    
    This is the core of the agent system - it takes the full network state,
    all pending actions, and processes everything in a single API call.
    """
    
    def __init__(self):
        if settings.google_api_key:
            self.client = genai.Client(api_key=settings.google_api_key)
            self.model = settings.gemini_pro_model  # Use Pro for complex reasoning
        else:
            self.client = None
            self.model = None
            logger.warning("batch_processor_not_configured",
                          message="GOOGLE_API_KEY not set, batch processing disabled")
    
    async def process_month(
        self,
        state: NetworkState,
        pending_actions: List[PendingAction],
        precomputed: PreComputedResults,
    ) -> MonthResult:
        """
        Process a full month of network activity.
        
        Args:
            state: Current network state
            pending_actions: User actions queued for this tick
            precomputed: Pre-calculated financial results
            
        Returns:
            MonthResult with all events, state changes, and narratives
        """
        next_month = state.month + 1
        
        logger.info("batch_processing_started",
                   month=next_month,
                   properties=len(state.properties),
                   participants=len(state.participants),
                   actions=len(pending_actions))
        
        # If Gemini is not configured, return mock result
        if not self.client:
            return self._mock_process(next_month, pending_actions)
        
        try:
            # Build the prompt
            prompt = self._build_prompt(state, pending_actions, precomputed)
            
            # Estimate tokens (rough: 4 chars = 1 token)
            estimated_tokens = len(prompt) // 4
            logger.info("batch_prompt_built", 
                       estimated_tokens=estimated_tokens,
                       prompt_length=len(prompt))
            
            # Call Gemini
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=[types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7,
                    max_output_tokens=50000,
                    response_mime_type="application/json",
                ),
            )
            
            # Parse response
            result = self._parse_response(response.text, next_month)
            
            logger.info("batch_processing_completed",
                       month=next_month,
                       events=len(result.events),
                       npc_decisions=len(result.npc_decisions))
            
            return result
            
        except Exception as e:
            logger.error("batch_processing_failed", error=str(e), month=next_month)
            return self._error_result(next_month, str(e))
    
    def _build_prompt(
        self,
        state: NetworkState,
        pending_actions: List[PendingAction],
        precomputed: PreComputedResults,
    ) -> str:
        """Build the monthly processing prompt."""
        
        # Count NPCs
        npc_count = sum(1 for p in state.participants if p.type == "npc")
        
        # Format actions with priority
        actions_list = [
            {
                "id": a.id,
                "user_id": a.user_id,
                "type": a.action_type,
                "priority": a.priority,
                "data": a.data,
            }
            for a in sorted(pending_actions, key=lambda x: -x.priority)
        ]
        
        return MONTH_PROMPT_TEMPLATE.format(
            next_month=state.month + 1,
            property_count=len(state.properties),
            properties_json=json.dumps([p.to_dict() for p in state.properties], indent=2),
            participant_count=len(state.participants),
            npc_count=npc_count,
            participants_json=json.dumps([p.to_dict() for p in state.participants], indent=2),
            market_json=json.dumps(state.market_conditions, indent=2),
            governance_json=json.dumps(state.governance_proposals, indent=2),
            precomputed_json=json.dumps(precomputed.to_dict(), indent=2),
            action_count=len(pending_actions),
            actions_json=json.dumps(actions_list, indent=2),
            history_json=json.dumps(state.recent_history, indent=2),
        )
    
    def _parse_response(self, response_text: str, month: int) -> MonthResult:
        """Parse Gemini's JSON response into a MonthResult."""
        try:
            # Clean up response if needed
            text = response_text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            data = json.loads(text)
            
            return MonthResult(
                month=month,
                events=data.get("events", []),
                state_changes=data.get("state_changes", {}),
                npc_decisions=data.get("npc_decisions", []),
                governor_summary=data.get("governor_summary", f"Month {month} completed."),
                alerts=data.get("alerts", []),
                chat_responses=data.get("chat_responses", {}),
                processing_log=data.get("processing_log", []),
            )
            
        except json.JSONDecodeError as e:
            logger.error("batch_response_parse_error", error=str(e))
            return self._error_result(month, f"Failed to parse response: {e}")
    
    def _mock_process(self, month: int, actions: List[PendingAction]) -> MonthResult:
        """Generate mock result when Gemini is not available."""
        events = []
        
        # Process each action with a simple mock result
        for action in actions:
            events.append({
                "type": action.action_type,
                "actor": action.user_id,
                "target": action.data.get("target", "network"),
                "data": {"status": "completed_mock", "note": "Gemini not configured"},
            })
        
        return MonthResult(
            month=month,
            events=events,
            state_changes={},
            npc_decisions=[],
            governor_summary=f"Month {month} processed in demo mode. Configure GOOGLE_API_KEY for full AI processing.",
            alerts=[],
            chat_responses={},
            processing_log=[
                "Demo mode: Gemini API not configured",
                f"Processed {len(actions)} actions with mock results",
            ],
        )
    
    def _error_result(self, month: int, error: str) -> MonthResult:
        """Generate error result."""
        return MonthResult(
            month=month,
            events=[],
            state_changes={},
            npc_decisions=[],
            governor_summary=f"Month {month} processing encountered an error. Please try again.",
            alerts=[{
                "to": "all",
                "type": "error",
                "message": f"Processing error: {error}",
            }],
            chat_responses={},
            processing_log=[f"ERROR: {error}"],
        )


# =============================================================================
# Demo State Generator
# =============================================================================

def generate_demo_state(month: int = 0) -> NetworkState:
    """Generate demo network state for testing."""
    
    # Demo properties
    properties = [
        Property(
            id="prop_1",
            address="123 Main Street",
            suburb="Wembley",
            state="WA",
            property_type="house",
            bedrooms=3,
            bathrooms=2,
            valuation=850000,
            network_ownership=0.4,
            token_price=1.02,
            gross_yield=5.2,
            status="tenanted",
            tenant_id="npc_renter_1",
            weekly_rent=650,
        ),
        Property(
            id="prop_2",
            address="456 Oak Avenue",
            suburb="Subiaco",
            state="WA",
            property_type="apartment",
            bedrooms=2,
            bathrooms=1,
            valuation=520000,
            network_ownership=0.6,
            token_price=1.05,
            gross_yield=5.8,
            status="tenanted",
            tenant_id="npc_renter_2",
            weekly_rent=450,
        ),
        Property(
            id="prop_3",
            address="789 Pine Road",
            suburb="Nedlands",
            state="WA",
            property_type="house",
            bedrooms=4,
            bathrooms=2,
            valuation=1200000,
            network_ownership=0.3,
            token_price=0.98,
            gross_yield=4.5,
            status="available",
        ),
    ]
    
    # Demo participants
    participants = [
        # Human investor (the user)
        Participant(
            id="user_1",
            name="Demo User",
            type="human",
            role="investor",
            balance=100000,
            holdings=[
                {"property_id": "prop_1", "tokens": 5000, "percent": 0.05},
                {"property_id": "prop_2", "tokens": 3000, "percent": 0.03},
            ],
        ),
        # NPC Investors
        Participant(
            id="npc_investor_alice",
            name="Alice (NPC)",
            type="npc",
            role="investor",
            balance=150000,
            holdings=[
                {"property_id": "prop_1", "tokens": 10000, "percent": 0.10},
            ],
            personality={"risk_tolerance": 0.7, "patience": 0.3, "diversification": 0.8},
            goal="Achieve 6% yield with moderate risk",
        ),
        Participant(
            id="npc_investor_bob",
            name="Bob (NPC)",
            type="npc",
            role="investor",
            balance=80000,
            holdings=[
                {"property_id": "prop_2", "tokens": 8000, "percent": 0.08},
            ],
            personality={"risk_tolerance": 0.4, "patience": 0.8, "diversification": 0.5},
            goal="Stable long-term growth, low risk",
        ),
        # NPC Renters
        Participant(
            id="npc_renter_1",
            name="Charlie (Renter)",
            type="npc",
            role="renter",
            balance=5000,
            personality={"reliability": 0.9, "maintenance_requests": 0.2},
            goal="Find stable housing near work",
        ),
        Participant(
            id="npc_renter_2",
            name="Diana (Renter)",
            type="npc",
            role="renter",
            balance=3000,
            personality={"reliability": 0.7, "maintenance_requests": 0.5},
            goal="Affordable apartment in good location",
        ),
        # NPC Service Provider
        Participant(
            id="npc_service_1",
            name="Fix-It Frank (Service)",
            type="npc",
            role="custodian",
            balance=10000,
            personality={"quality": 0.8, "speed": 0.6, "price_flexibility": 0.4},
            goal="Build reputation, get repeat business",
        ),
    ]
    
    # Market conditions
    market_conditions = {
        "wa_market_trend": "stable",
        "interest_rate": 4.35,
        "median_house_price_perth": 620000,
        "rental_vacancy_rate": 1.2,
        "annual_appreciation_forecast": 3.5,
        "economic_outlook": "positive",
    }
    
    # Governance
    governance_proposals = [
        {
            "id": "prop_fee_reduction",
            "title": "Reduce management fee from 0.5% to 0.4%",
            "status": "voting",
            "votes_for": 45,
            "votes_against": 20,
            "ends_month": month + 2,
        },
    ]
    
    # Recent history
    recent_history = []
    if month > 0:
        recent_history = [
            {"month": month - 1, "summary": "Stable month, all rents collected, +0.3% market"},
        ]
    if month > 1:
        recent_history.append(
            {"month": month - 2, "summary": "New property added, 2 new investors joined"}
        )
    
    return NetworkState(
        month=month,
        properties=properties,
        participants=participants,
        market_conditions=market_conditions,
        governance_proposals=governance_proposals,
        recent_history=recent_history,
    )


def generate_demo_precomputed(state: NetworkState) -> PreComputedResults:
    """Generate pre-computed results for demo."""
    import random
    
    # Collect rent from tenanted properties
    rent_collected = {}
    for prop in state.properties:
        if prop.weekly_rent:
            monthly_rent = prop.weekly_rent * 4.33  # Average weeks per month
            rent_collected[prop.id] = round(monthly_rent, 2)
    
    # Calculate dividends (simplified)
    total_rent = sum(rent_collected.values())
    total_tokens = sum(
        sum(h.get("tokens", 0) for h in p.holdings)
        for p in state.participants
    )
    dividends_per_token = (total_rent * 0.9) / max(total_tokens, 1)  # 90% to holders
    
    # Market change
    market_change = random.uniform(-0.5, 1.5)  # -0.5% to +1.5%
    
    # New valuations
    new_valuations = {
        prop.id: round(prop.valuation * (1 + market_change / 100), 2)
        for prop in state.properties
    }
    
    return PreComputedResults(
        rent_collected=rent_collected,
        dividends_per_token=round(dividends_per_token, 6),
        market_change_percent=round(market_change, 2),
        new_valuations=new_valuations,
    )


# =============================================================================
# Singleton Instance
# =============================================================================

_batch_processor: Optional[BatchProcessor] = None


def get_batch_processor() -> BatchProcessor:
    """Get the singleton batch processor instance."""
    global _batch_processor
    if _batch_processor is None:
        _batch_processor = BatchProcessor()
    return _batch_processor
