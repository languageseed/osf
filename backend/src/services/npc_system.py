"""
NPC System - Goal-Driven AI Participants
Diverse personalities with autonomous decision making
"""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4
import random
import structlog

from src.database import async_session
from src.repositories.participant import ParticipantRepository
from src.repositories.property import PropertyStateRepository
from src.services.action_processor import get_action_processor, ActionResult

logger = structlog.get_logger()


class NPCPersonality(Enum):
    """NPC personality types affecting behavior."""
    CONSERVATIVE = "conservative"    # Low risk, steady income focus
    AGGRESSIVE = "aggressive"        # High risk, growth focus
    BALANCED = "balanced"            # Mixed strategy
    OPPORTUNIST = "opportunist"      # Market timing focus
    PASSIVE = "passive"              # Buy and hold, minimal activity
    SPECULATOR = "speculator"        # High frequency, momentum chasing


class NPCRole(Enum):
    """Special NPC roles with unique behaviors."""
    INVESTOR = "investor"            # Standard investor behavior
    RENTER = "renter"                # Tenant focused
    SERVICE = "service"              # Service provider
    MARKET_MAKER = "market_maker"    # Provides liquidity
    DEVELOPER = "developer"          # Creates new properties
    FOUNDATION = "foundation"        # OSF governance


@dataclass
class NPCGoal:
    """A goal that drives NPC behavior."""
    goal_type: str  # "accumulate", "income", "divest", "stabilize"
    target_value: Decimal
    priority: int  # 1-10, higher = more important
    deadline_month: Optional[int] = None
    progress: Decimal = Decimal("0")
    completed: bool = False


@dataclass
class NPCProfile:
    """Complete NPC profile with personality and goals."""
    id: str
    name: str
    personality: NPCPersonality
    role: NPCRole
    risk_tolerance: float  # 0.0 to 1.0
    activity_level: float  # 0.0 to 1.0 (how often they act)
    goals: List[NPCGoal] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    backstory: str = ""
    avatar_id: Optional[str] = None
    
    # Behavior modifiers
    patience: float = 0.5  # How long they wait for good deals
    contrarian: float = 0.0  # Tendency to go against market
    loyalty: float = 0.5  # Preference for holding existing positions


@dataclass
class NPCDecision:
    """A decision made by an NPC."""
    npc_id: str
    action_type: str
    action_data: Dict[str, Any]
    confidence: float  # 0.0 to 1.0
    reasoning: str


# ============================================================================
# Predefined NPC Templates
# ============================================================================

NPC_TEMPLATES: List[Dict[str, Any]] = [
    # Investors
    {
        "name": "Sarah Chen",
        "personality": NPCPersonality.CONSERVATIVE,
        "role": NPCRole.INVESTOR,
        "risk_tolerance": 0.2,
        "activity_level": 0.3,
        "backstory": "Retired teacher focused on steady dividend income for retirement.",
        "preferences": {"min_yield": 4.0, "max_price_ratio": 1.1},
        "goals": [
            {"goal_type": "income", "target_value": "5000", "priority": 9},
        ],
    },
    {
        "name": "Marcus Thompson",
        "personality": NPCPersonality.AGGRESSIVE,
        "role": NPCRole.INVESTOR,
        "risk_tolerance": 0.8,
        "activity_level": 0.7,
        "backstory": "Tech entrepreneur reinvesting startup profits into property.",
        "preferences": {"growth_focus": True, "min_tokens_per_trade": 10000},
        "goals": [
            {"goal_type": "accumulate", "target_value": "500000", "priority": 8},
        ],
    },
    {
        "name": "Emily Rodriguez",
        "personality": NPCPersonality.BALANCED,
        "role": NPCRole.INVESTOR,
        "risk_tolerance": 0.5,
        "activity_level": 0.5,
        "backstory": "Financial advisor building a demonstration portfolio.",
        "preferences": {"diversification": True, "max_single_property": 0.3},
        "goals": [
            {"goal_type": "accumulate", "target_value": "200000", "priority": 7},
            {"goal_type": "income", "target_value": "2000", "priority": 6},
        ],
    },
    {
        "name": "David Park",
        "personality": NPCPersonality.OPPORTUNIST,
        "role": NPCRole.INVESTOR,
        "risk_tolerance": 0.6,
        "activity_level": 0.8,
        "backstory": "Day trader exploring fractional property markets.",
        "preferences": {"momentum": True, "quick_trades": True},
        "goals": [
            {"goal_type": "accumulate", "target_value": "100000", "priority": 5},
        ],
        "contrarian": 0.3,
    },
    {
        "name": "Janet Williams",
        "personality": NPCPersonality.PASSIVE,
        "role": NPCRole.INVESTOR,
        "risk_tolerance": 0.3,
        "activity_level": 0.1,
        "backstory": "Long-term investor who rarely checks her portfolio.",
        "preferences": {"set_and_forget": True},
        "goals": [
            {"goal_type": "accumulate", "target_value": "150000", "priority": 4},
        ],
        "patience": 0.9,
        "loyalty": 0.9,
    },
    
    # Renters
    {
        "name": "Alex Kim",
        "personality": NPCPersonality.BALANCED,
        "role": NPCRole.RENTER,
        "risk_tolerance": 0.4,
        "activity_level": 0.3,
        "backstory": "Young professional renting while saving for a deposit.",
        "preferences": {"preferred_suburbs": ["Cottesloe", "Scarborough"]},
        "goals": [
            {"goal_type": "accumulate", "target_value": "50000", "priority": 8},
        ],
    },
    {
        "name": "The Morrison Family",
        "personality": NPCPersonality.CONSERVATIVE,
        "role": NPCRole.RENTER,
        "risk_tolerance": 0.2,
        "activity_level": 0.2,
        "backstory": "Family of four renting a house in the suburbs.",
        "preferences": {"stability": True, "min_bedrooms": 3},
        "goals": [],
    },
    
    # Service Providers
    {
        "name": "BuildRight Maintenance",
        "personality": NPCPersonality.BALANCED,
        "role": NPCRole.SERVICE,
        "risk_tolerance": 0.3,
        "activity_level": 0.6,
        "backstory": "Local maintenance company servicing OSF properties.",
        "preferences": {"service_types": ["maintenance", "repairs", "renovation"]},
        "goals": [
            {"goal_type": "income", "target_value": "10000", "priority": 9},
        ],
    },
    {
        "name": "CleanHome Services",
        "personality": NPCPersonality.CONSERVATIVE,
        "role": NPCRole.SERVICE,
        "risk_tolerance": 0.2,
        "activity_level": 0.7,
        "backstory": "Professional cleaning company for rental turnovers.",
        "preferences": {"service_types": ["cleaning", "inspection"]},
        "goals": [
            {"goal_type": "income", "target_value": "5000", "priority": 8},
        ],
    },
    
    # Special NPCs
    {
        "name": "OSF Market Maker",
        "personality": NPCPersonality.BALANCED,
        "role": NPCRole.MARKET_MAKER,
        "risk_tolerance": 0.5,
        "activity_level": 0.9,
        "backstory": "Automated market maker providing liquidity for all properties.",
        "preferences": {"spread": 0.02, "max_position": 0.1},
        "goals": [
            {"goal_type": "stabilize", "target_value": "0", "priority": 10},
        ],
    },
    {
        "name": "Sunset Developments",
        "personality": NPCPersonality.AGGRESSIVE,
        "role": NPCRole.DEVELOPER,
        "risk_tolerance": 0.7,
        "activity_level": 0.4,
        "backstory": "Property developer bringing new listings to the OSF network.",
        "preferences": {"target_suburbs": ["Subiaco", "South Perth", "Fremantle"]},
        "goals": [
            {"goal_type": "accumulate", "target_value": "1000000", "priority": 7},
        ],
    },
]


class NPCBrain:
    """Decision-making engine for NPCs."""
    
    def __init__(self, profile: NPCProfile):
        self.profile = profile
        # Load market calibration data
        from src.services.market_data import get_market_data
        self.market_data = get_market_data()
        self.calibration = self.market_data.get_npc_behavior_calibration()
    
    def should_act(self, network_month: int) -> bool:
        """Determine if NPC should take action this month."""
        # Base probability from activity level
        base_prob = self.profile.activity_level
        
        # Modify by urgency of goals
        urgency_bonus = 0
        for goal in self.profile.goals:
            if goal.deadline_month and not goal.completed:
                months_remaining = goal.deadline_month - network_month
                if months_remaining <= 3:
                    urgency_bonus += 0.2 * goal.priority / 10
        
        # Market-driven activity boost (high investor activity = more NPC trades)
        investor_momentum = self.calibration.get("investor_lending_momentum", 0)
        if investor_momentum > 0.15:  # Strong investor growth
            base_prob *= 1.2
        
        final_prob = min(1.0, base_prob + urgency_bonus)
        return random.random() < final_prob
    
    def evaluate_market(
        self,
        properties: List[Dict[str, Any]],
        market_conditions: Dict[str, Any],
    ) -> Dict[str, float]:
        """Evaluate market attractiveness using real market calibration."""
        scores = {}
        
        # Use real market data for baseline expectations
        target_yield = self.calibration.get("target_yield_house", 0.045)  # 4.5% WA average
        min_yield = self.calibration.get("minimum_acceptable_yield", 0.035)
        market_trend = market_conditions.get("trend", "stable")
        
        # Tight rental market boosts rental property attractiveness
        vacancy_rate = self.calibration.get("vacancy_rate", 0.01)
        rental_boost = 10 if vacancy_rate < 0.01 else 5 if vacancy_rate < 0.02 else 0
        
        for prop in properties:
            prop_id = prop.get("id", prop.get("property_id"))
            score = 50.0  # Base score
            
            # Yield attractiveness (calibrated to WA market)
            prop_yield = prop.get("yield", prop.get("yield_percent", 4.0)) / 100
            if prop_yield >= target_yield:
                score += 15  # Meets WA target yield
            elif prop_yield >= min_yield:
                score += 5   # Acceptable yield
            else:
                score -= 10  # Below minimum
            
            # Rental market tightness bonus
            score += rental_boost
            
            # Price attractiveness (lower = better for buying)
            token_price = prop.get("token_price", 1.0)
            if token_price < 1.0:
                score += (1.0 - token_price) * 20
            elif token_price > 1.2:
                score -= (token_price - 1.2) * 15
            
            # WA discount factor (Perth is ~25% below national average)
            wa_discount = self.calibration.get("wa_discount_to_national", 0.74)
            if wa_discount < 0.8:
                score += 5  # Value opportunity vs national market
            
            # Personality adjustments
            if self.profile.personality == NPCPersonality.CONSERVATIVE:
                if prop_yield >= target_yield:
                    score += 10
            elif self.profile.personality == NPCPersonality.AGGRESSIVE:
                if market_trend == "growing":
                    score += 15
                # Growth expectation from real data
                growth = self.calibration.get("price_growth_expectation", 0)
                if growth > 0.05:
                    score += 10
            elif self.profile.personality == NPCPersonality.CONTRARIAN:
                if market_trend == "declining":
                    score += 20  # Buy when others are selling
            
            scores[prop_id] = max(0, min(100, score))
        
        return scores
    
    def decide_action(
        self,
        balance: Decimal,
        holdings: List[Dict[str, Any]],
        properties: List[Dict[str, Any]],
        market_conditions: Dict[str, Any],
        network_month: int,
    ) -> Optional[NPCDecision]:
        """Make a decision based on goals and market conditions."""
        
        # Special role handling
        if self.profile.role == NPCRole.MARKET_MAKER:
            return self._market_maker_decision(properties, holdings)
        elif self.profile.role == NPCRole.DEVELOPER:
            return self._developer_decision(network_month)
        elif self.profile.role == NPCRole.SERVICE:
            return None  # Service providers react to requests
        elif self.profile.role == NPCRole.RENTER:
            return self._renter_decision(balance, network_month)
        
        # Standard investor logic
        return self._investor_decision(
            balance, holdings, properties, market_conditions, network_month
        )
    
    def _investor_decision(
        self,
        balance: Decimal,
        holdings: List[Dict[str, Any]],
        properties: List[Dict[str, Any]],
        market_conditions: Dict[str, Any],
        network_month: int,
    ) -> Optional[NPCDecision]:
        """Standard investor decision making."""
        
        # Evaluate market
        scores = self.evaluate_market(properties, market_conditions)
        
        # Check goals
        primary_goal = None
        for goal in self.profile.goals:
            if not goal.completed:
                primary_goal = goal
                break
        
        if not primary_goal:
            # No active goals - passive behavior
            return None
        
        if primary_goal.goal_type == "accumulate":
            # Look to buy
            if balance < Decimal("1000"):
                return None  # Not enough to trade
            
            # Find best property to buy
            best_prop = max(scores.items(), key=lambda x: x[1])
            if best_prop[1] < 40:  # Market not attractive
                return None
            
            # Calculate amount based on risk tolerance
            invest_pct = Decimal(str(self.profile.risk_tolerance * 0.3))
            invest_amount = balance * invest_pct
            invest_amount = max(Decimal("1000"), min(invest_amount, balance * Decimal("0.5")))
            
            return NPCDecision(
                npc_id=self.profile.id,
                action_type="buy_tokens",
                action_data={
                    "property_id": best_prop[0],
                    "token_amount": float(invest_amount),
                    "max_price": 1.5,
                },
                confidence=best_prop[1] / 100,
                reasoning=f"Accumulation goal: investing ${invest_amount:.0f} in property with score {best_prop[1]:.0f}",
            )
        
        elif primary_goal.goal_type == "income":
            # Already holding? Just wait for dividends
            if holdings:
                return None
            
            # Look for high-yield properties
            high_yield_props = [
                (pid, score) for pid, score in scores.items()
                if any(p.get("yield", 0) >= 4.5 for p in properties 
                      if p.get("id") == pid or p.get("property_id") == pid)
            ]
            
            if not high_yield_props:
                return None
            
            best_prop = max(high_yield_props, key=lambda x: x[1])
            invest_amount = min(balance * Decimal("0.25"), Decimal("20000"))
            
            return NPCDecision(
                npc_id=self.profile.id,
                action_type="buy_tokens",
                action_data={
                    "property_id": best_prop[0],
                    "token_amount": float(invest_amount),
                    "max_price": 1.2,
                },
                confidence=0.7,
                reasoning=f"Income goal: buying high-yield property for dividends",
            )
        
        elif primary_goal.goal_type == "divest":
            # Look to sell
            if not holdings:
                return None
            
            # Sell worst performing holding
            holding = random.choice(holdings)
            sell_amount = Decimal(str(holding.get("token_amount", 0))) * Decimal("0.5")
            
            return NPCDecision(
                npc_id=self.profile.id,
                action_type="sell_tokens",
                action_data={
                    "property_id": holding.get("property_id"),
                    "token_amount": float(sell_amount),
                    "min_price": 0.8,
                },
                confidence=0.6,
                reasoning=f"Divesting: selling {sell_amount:.0f} tokens",
            )
        
        return None
    
    def _market_maker_decision(
        self,
        properties: List[Dict[str, Any]],
        holdings: List[Dict[str, Any]],
    ) -> Optional[NPCDecision]:
        """Market maker provides liquidity."""
        if not properties:
            return None
        
        # Find property with least liquidity
        prop = random.choice(properties)
        prop_id = prop.get("id", prop.get("property_id"))
        
        # Randomly buy or sell to provide liquidity
        if random.random() < 0.5:
            return NPCDecision(
                npc_id=self.profile.id,
                action_type="buy_tokens",
                action_data={
                    "property_id": prop_id,
                    "token_amount": 5000,
                    "max_price": 1.1,
                },
                confidence=0.9,
                reasoning="Market making: providing buy-side liquidity",
            )
        else:
            return NPCDecision(
                npc_id=self.profile.id,
                action_type="sell_tokens",
                action_data={
                    "property_id": prop_id,
                    "token_amount": 5000,
                    "min_price": 0.9,
                },
                confidence=0.9,
                reasoning="Market making: providing sell-side liquidity",
            )
    
    def _developer_decision(self, network_month: int) -> Optional[NPCDecision]:
        """Developer creates new property listings."""
        # Only develop every few months
        if network_month % 3 != 0:
            return None
        
        return NPCDecision(
            npc_id=self.profile.id,
            action_type="request_service",
            action_data={
                "service_type": "new_listing",
                "description": "Sunset Developments is preparing a new property for the OSF network",
            },
            confidence=0.8,
            reasoning="Developer: proposing new property listing",
        )
    
    def _renter_decision(
        self,
        balance: Decimal,
        network_month: int,
    ) -> Optional[NPCDecision]:
        """Renter pays rent or saves for investment."""
        # Renters mainly pay rent (handled automatically)
        # Sometimes they invest their savings
        if balance > Decimal("10000") and random.random() < 0.2:
            return NPCDecision(
                npc_id=self.profile.id,
                action_type="buy_tokens",
                action_data={
                    "property_id": None,  # Will be selected by system
                    "token_amount": 1000,
                    "max_price": 1.0,
                },
                confidence=0.5,
                reasoning="Renter: investing savings into property tokens",
            )
        return None


class NPCManager:
    """Manages all NPCs in the simulation."""
    
    def __init__(self):
        self.npcs: Dict[str, NPCProfile] = {}
        self.brains: Dict[str, NPCBrain] = {}
        self._initialized = False
    
    async def initialize(self) -> int:
        """Initialize NPCs from templates and database."""
        if self._initialized:
            return len(self.npcs)
        
        async with async_session() as session:
            participant_repo = ParticipantRepository(session)
            
            for template in NPC_TEMPLATES:
                npc_id = str(uuid4())
                
                # Create participant record
                participant = await participant_repo.get_by_name(template["name"])
                if not participant:
                    participant = await participant_repo.create(
                        user_id=None,  # NPCs don't have users
                        display_name=template["name"],
                        role=template["role"].value if isinstance(template["role"], NPCRole) else template["role"],
                        is_npc=True,
                        balance=Decimal("100000"),  # Starting balance
                    )
                    await session.commit()
                    npc_id = participant.id
                else:
                    npc_id = participant.id
                
                # Create profile
                goals = []
                for g in template.get("goals", []):
                    goals.append(NPCGoal(
                        goal_type=g["goal_type"],
                        target_value=Decimal(g["target_value"]),
                        priority=g["priority"],
                    ))
                
                profile = NPCProfile(
                    id=npc_id,
                    name=template["name"],
                    personality=template["personality"],
                    role=template["role"],
                    risk_tolerance=template["risk_tolerance"],
                    activity_level=template["activity_level"],
                    goals=goals,
                    preferences=template.get("preferences", {}),
                    backstory=template.get("backstory", ""),
                    patience=template.get("patience", 0.5),
                    contrarian=template.get("contrarian", 0.0),
                    loyalty=template.get("loyalty", 0.5),
                )
                
                self.npcs[npc_id] = profile
                self.brains[npc_id] = NPCBrain(profile)
        
        self._initialized = True
        logger.info("npc_manager_initialized", npc_count=len(self.npcs))
        return len(self.npcs)
    
    async def process_tick(
        self,
        network_month: int,
        properties: List[Dict[str, Any]],
        market_conditions: Dict[str, Any],
    ) -> List[ActionResult]:
        """Process NPC decisions for a tick."""
        if not self._initialized:
            await self.initialize()
        
        results = []
        action_processor = get_action_processor()
        
        async with async_session() as session:
            participant_repo = ParticipantRepository(session)
            
            for npc_id, brain in self.brains.items():
                # Check if NPC wants to act
                if not brain.should_act(network_month):
                    continue
                
                # Get NPC state
                participant = await participant_repo.get_by_id(npc_id)
                if not participant:
                    continue
                
                holdings = await participant_repo.get_holdings(npc_id)
                holdings_dicts = [
                    {"property_id": h.property_id, "token_amount": float(h.token_amount)}
                    for h in holdings
                ]
                
                # Make decision
                decision = brain.decide_action(
                    balance=participant.balance,
                    holdings=holdings_dicts,
                    properties=properties,
                    market_conditions=market_conditions,
                    network_month=network_month,
                )
                
                if decision:
                    logger.info("npc_decision",
                              npc=brain.profile.name,
                              action=decision.action_type,
                              confidence=decision.confidence,
                              reasoning=decision.reasoning)
                    
                    # Execute action
                    result = await action_processor.process_action(
                        participant_id=npc_id,
                        action_type=decision.action_type,
                        action_data=decision.action_data,
                        network_month=network_month,
                    )
                    results.append(result)
            
            await session.commit()
        
        logger.info("npc_tick_processed",
                   month=network_month,
                   decisions=len(results))
        
        return results
    
    def get_npc_summaries(self) -> List[Dict[str, Any]]:
        """Get summaries of all NPCs for display."""
        return [
            {
                "id": npc.id,
                "name": npc.name,
                "personality": npc.personality.value,
                "role": npc.role.value,
                "backstory": npc.backstory,
                "risk_tolerance": npc.risk_tolerance,
                "activity_level": npc.activity_level,
                "goals": [
                    {"type": g.goal_type, "target": float(g.target_value), "priority": g.priority}
                    for g in npc.goals
                ],
            }
            for npc in self.npcs.values()
        ]


# Singleton instance
_npc_manager: Optional[NPCManager] = None


def get_npc_manager() -> NPCManager:
    """Get the NPC manager singleton."""
    global _npc_manager
    if _npc_manager is None:
        _npc_manager = NPCManager()
    return _npc_manager
