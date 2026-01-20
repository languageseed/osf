"""
Event Generator System
Creates dynamic simulation events and narrative content
"""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from uuid import uuid4
import random
import structlog

from google import genai
from google.genai import types

from src.config import get_settings
from src.database import async_session
from src.repositories import NetworkRepository

logger = structlog.get_logger()
settings = get_settings()


class EventCategory(Enum):
    """Categories of simulation events."""
    MARKET = "market"           # Interest rates, housing trends
    PROPERTY = "property"       # Listings, sales, maintenance
    ECONOMIC = "economic"       # GDP, employment, inflation
    GOVERNANCE = "governance"   # Proposals, votes, policy
    COMMUNITY = "community"     # User milestones, achievements
    EMERGENCY = "emergency"     # Urgent issues requiring action


class EventSeverity(Enum):
    """Event severity/importance levels."""
    INFO = "info"               # General information
    POSITIVE = "positive"       # Good news
    WARNING = "warning"         # Requires attention
    CRITICAL = "critical"       # Urgent action needed
    MILESTONE = "milestone"     # Achievement/celebration


class EconomicPhase(Enum):
    """Economic cycle phases."""
    EXPANSION = "expansion"     # Growth period
    PEAK = "peak"               # Market top
    CONTRACTION = "contraction" # Slowdown
    TROUGH = "trough"           # Market bottom
    RECOVERY = "recovery"       # Beginning of upturn


@dataclass
class SimulationEvent:
    """A generated simulation event."""
    id: str
    category: EventCategory
    severity: EventSeverity
    title: str
    description: str
    impact: Dict[str, Any]  # Numeric impacts on simulation
    narrative: str  # Story/news article format
    month: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Optional references
    property_id: Optional[str] = None
    participant_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "impact": self.impact,
            "narrative": self.narrative,
            "month": self.month,
            "property_id": self.property_id,
            "participant_id": self.participant_id,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class EconomicState:
    """Current economic conditions."""
    phase: EconomicPhase
    interest_rate: Decimal
    inflation_rate: Decimal
    unemployment_rate: Decimal
    housing_index: Decimal  # 100 = baseline
    consumer_confidence: int  # 0-100
    months_in_phase: int = 0
    
    # WA-specific indicators
    iron_ore_price: Decimal = Decimal("110")  # USD/tonne
    population_growth_rate: Decimal = Decimal("2.0")  # Annual %
    vacancy_rate: Decimal = Decimal("1.0")  # %
    
    # Derived market condition
    market_condition: str = "stable"  # boom, stable, stagnant, declining, bust
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase.value,
            "interest_rate": float(self.interest_rate),
            "inflation_rate": float(self.inflation_rate),
            "unemployment_rate": float(self.unemployment_rate),
            "housing_index": float(self.housing_index),
            "consumer_confidence": self.consumer_confidence,
            "months_in_phase": self.months_in_phase,
            "iron_ore_price": float(self.iron_ore_price),
            "population_growth_rate": float(self.population_growth_rate),
            "vacancy_rate": float(self.vacancy_rate),
            "market_condition": self.market_condition,
        }
    
    def update_market_condition(self):
        """Derive market condition from indicators."""
        iron_ore = float(self.iron_ore_price)
        pop_growth = float(self.population_growth_rate)
        confidence = self.consumer_confidence
        
        if iron_ore >= 150 and pop_growth >= 2.0 and confidence >= 60:
            self.market_condition = "boom"
        elif iron_ore >= 100 and pop_growth >= 1.5 and confidence >= 50:
            self.market_condition = "stable"
        elif iron_ore >= 80 and confidence >= 40:
            self.market_condition = "stagnant"
        elif iron_ore >= 60 or confidence >= 30:
            self.market_condition = "declining"
        else:
            self.market_condition = "bust"
    
    def get_appreciation_rate(self) -> float:
        """Get monthly appreciation rate based on market condition."""
        rates = {
            "boom": (0.008, 0.020),      # 0.8% to 2.0% monthly
            "stable": (0.002, 0.005),    # 0.2% to 0.5% monthly
            "stagnant": (-0.002, 0.002), # -0.2% to 0.2% monthly
            "declining": (-0.010, -0.003), # -1.0% to -0.3% monthly
            "bust": (-0.025, -0.010),    # -2.5% to -1.0% monthly
        }
        min_rate, max_rate = rates.get(self.market_condition, (0, 0.003))
        import random
        return random.uniform(min_rate, max_rate)


# ============================================================================
# Event Templates
# ============================================================================

# WA-specific market conditions
IRON_ORE_EVENT_TEMPLATES = [
    # BOOM conditions
    {
        "title": "Iron Ore Surges Past $150/tonne",
        "description": "Strong Chinese steel demand pushes iron ore to multi-year highs. WA mining sector booming.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.POSITIVE,
        "probability": 0.15,
        "impact": {"iron_ore_price": 155, "property_value_impact": 1.5, "confidence_impact": 10, "population_growth": 0.3},
        "phase_preference": [EconomicPhase.EXPANSION],
    },
    {
        "title": "Iron Ore Hits $180/tonne on Supply Constraints",
        "description": "Brazilian supply disruptions and Chinese stimulus drive WA's key export to record levels.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.POSITIVE,
        "probability": 0.08,
        "impact": {"iron_ore_price": 180, "property_value_impact": 2.0, "confidence_impact": 15, "population_growth": 0.5},
        "phase_preference": [EconomicPhase.EXPANSION, EconomicPhase.PEAK],
    },
    # STABLE conditions
    {
        "title": "Iron Ore Steady at $110/tonne",
        "description": "Iron ore prices remain stable as Chinese demand balances global supply increases.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.INFO,
        "probability": 0.25,
        "impact": {"iron_ore_price": 110, "property_value_impact": 0.3},
    },
    # DECLINE conditions
    {
        "title": "Iron Ore Falls Below $100/tonne",
        "description": "Weakening Chinese construction sector reduces steel demand. WA miners face margin pressure.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.WARNING,
        "probability": 0.12,
        "impact": {"iron_ore_price": 95, "property_value_impact": -0.5, "confidence_impact": -8},
        "phase_preference": [EconomicPhase.PEAK, EconomicPhase.CONTRACTION],
    },
    {
        "title": "Iron Ore Crashes to $80/tonne",
        "description": "Chinese property crisis and steel overcapacity send iron ore plunging. Mining job losses expected.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.CRITICAL,
        "probability": 0.06,
        "impact": {"iron_ore_price": 80, "property_value_impact": -1.5, "confidence_impact": -15, "population_growth": -0.3},
        "phase_preference": [EconomicPhase.CONTRACTION, EconomicPhase.TROUGH],
    },
    {
        "title": "Iron Ore Collapses to $60/tonne - Mining Layoffs Begin",
        "description": "Multi-year low in iron ore triggers cost-cutting across Pilbara operations. FIFO workers returning to eastern states.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.CRITICAL,
        "probability": 0.03,
        "impact": {"iron_ore_price": 60, "property_value_impact": -2.5, "confidence_impact": -25, "population_growth": -0.5, "vacancy_impact": 2},
        "phase_preference": [EconomicPhase.TROUGH],
    },
]

POPULATION_EVENT_TEMPLATES = [
    # GROWTH conditions
    {
        "title": "WA Population Growth Hits 2.5% - Highest in Nation",
        "description": "Strong mining employment and lifestyle appeal drive interstate and overseas migration to WA.",
        "category": EventCategory.ECONOMIC,
        "severity": EventSeverity.POSITIVE,
        "probability": 0.12,
        "impact": {"population_growth": 2.5, "property_value_impact": 1.0, "vacancy_impact": -1, "rent_impact": 5},
        "phase_preference": [EconomicPhase.EXPANSION],
    },
    {
        "title": "Perth Sees Record Net Migration",
        "description": "Eastern state residents relocating to Perth for affordability and mining sector opportunities.",
        "category": EventCategory.ECONOMIC,
        "severity": EventSeverity.POSITIVE,
        "probability": 0.1,
        "impact": {"population_growth": 0.5, "property_value_impact": 0.8, "vacancy_impact": -0.5},
        "phase_preference": [EconomicPhase.EXPANSION, EconomicPhase.RECOVERY],
    },
    # STABLE
    {
        "title": "WA Population Growth Moderates to 1.5%",
        "description": "Population growth returns to sustainable levels as mining boom cools.",
        "category": EventCategory.ECONOMIC,
        "severity": EventSeverity.INFO,
        "probability": 0.2,
        "impact": {"population_growth": 1.5, "property_value_impact": 0.2},
    },
    # DECLINE conditions
    {
        "title": "Interstate Migration Turns Negative",
        "description": "More Australians leaving WA than arriving as mining construction winds down.",
        "category": EventCategory.ECONOMIC,
        "severity": EventSeverity.WARNING,
        "probability": 0.08,
        "impact": {"population_growth": -0.3, "property_value_impact": -0.8, "vacancy_impact": 1, "rent_impact": -3},
        "phase_preference": [EconomicPhase.CONTRACTION],
    },
    {
        "title": "WA Population Growth Falls to 0.8% - Lowest Since 2016",
        "description": "Economic uncertainty and eastern state opportunities draw workers away from Perth.",
        "category": EventCategory.ECONOMIC,
        "severity": EventSeverity.WARNING,
        "probability": 0.06,
        "impact": {"population_growth": 0.8, "property_value_impact": -0.5, "vacancy_impact": 1.5, "confidence_impact": -5},
        "phase_preference": [EconomicPhase.CONTRACTION, EconomicPhase.TROUGH],
    },
    {
        "title": "Mining Workers Exodus from Pilbara",
        "description": "Project completions and automation reduce FIFO workforce. Regional towns see sharp population decline.",
        "category": EventCategory.ECONOMIC,
        "severity": EventSeverity.CRITICAL,
        "probability": 0.04,
        "impact": {"population_growth": -0.5, "property_value_impact": -2.0, "vacancy_impact": 3, "rent_impact": -8},
        "phase_preference": [EconomicPhase.TROUGH],
    },
]

MARKET_EVENT_TEMPLATES = [
    # Interest rate events
    {
        "title": "RBA Holds Interest Rate at {rate}%",
        "description": "The Reserve Bank of Australia maintained the cash rate, citing stable inflation.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.INFO,
        "probability": 0.4,
        "impact": {"interest_rate_change": 0},
    },
    {
        "title": "RBA Raises Interest Rate by 0.25%",
        "description": "The Reserve Bank increased rates to combat rising inflation pressures.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.WARNING,
        "probability": 0.15,
        "impact": {"interest_rate_change": 0.25, "yield_impact": 0.1, "property_value_impact": -0.3},
        "phase_preference": [EconomicPhase.EXPANSION, EconomicPhase.PEAK],
    },
    {
        "title": "RBA Cuts Interest Rate by 0.25%",
        "description": "The Reserve Bank lowered rates to stimulate economic growth.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.POSITIVE,
        "probability": 0.1,
        "impact": {"interest_rate_change": -0.25, "property_value_impact": 1.0},
        "phase_preference": [EconomicPhase.CONTRACTION, EconomicPhase.TROUGH],
    },
    # BOOM market events
    {
        "title": "Perth Housing Market Shows Strong Growth",
        "description": "Western Australian property values increased 1.5% this month, outperforming eastern states.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.POSITIVE,
        "probability": 0.15,
        "impact": {"property_value_impact": 1.5, "confidence_impact": 5},
        "phase_preference": [EconomicPhase.EXPANSION, EconomicPhase.RECOVERY],
    },
    {
        "title": "Perth Median House Price Hits New Record",
        "description": "Strong demand and limited supply push Perth's median house price above $1 million.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.MILESTONE,
        "probability": 0.05,
        "impact": {"property_value_impact": 2.0, "confidence_impact": 8},
        "phase_preference": [EconomicPhase.EXPANSION],
    },
    {
        "title": "Rental Vacancy Rates Hit Record Low",
        "description": "Perth rental market tightens with vacancy rates falling below 1%.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.POSITIVE,
        "probability": 0.12,
        "impact": {"rent_impact": 5, "yield_impact": 0.3, "vacancy_impact": -1},
        "phase_preference": [EconomicPhase.EXPANSION],
    },
    # STAGNANT/SIDEWAYS market events
    {
        "title": "Perth Property Market Flat for Third Month",
        "description": "Buyer hesitation amid rate uncertainty keeps Perth property values stable but stagnant.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.INFO,
        "probability": 0.15,
        "impact": {"property_value_impact": 0, "confidence_impact": -2},
        "phase_preference": [EconomicPhase.PEAK],
    },
    {
        "title": "Perth Housing Market Enters Consolidation Phase",
        "description": "After years of growth, Perth property values plateau as affordability constraints bite.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.INFO,
        "probability": 0.1,
        "impact": {"property_value_impact": -0.1, "confidence_impact": -3},
        "phase_preference": [EconomicPhase.PEAK],
    },
    # DOWNTURN market events
    {
        "title": "Perth Property Values Decline for First Time in 3 Years",
        "description": "Weakening demand and rising stock levels push Perth house prices down 0.5%.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.WARNING,
        "probability": 0.08,
        "impact": {"property_value_impact": -0.5, "confidence_impact": -8},
        "phase_preference": [EconomicPhase.CONTRACTION],
    },
    {
        "title": "Perth Housing Market Correction Deepens",
        "description": "Perth property values fall 1.2% as mining slowdown reduces buyer demand.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.WARNING,
        "probability": 0.06,
        "impact": {"property_value_impact": -1.2, "confidence_impact": -12},
        "phase_preference": [EconomicPhase.CONTRACTION, EconomicPhase.TROUGH],
    },
    {
        "title": "Vacancy Rates Rise to 4% - Landlords Compete for Tenants",
        "description": "Oversupply from construction boom meets falling demand. Rents under pressure.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.WARNING,
        "probability": 0.05,
        "impact": {"vacancy_impact": 2, "rent_impact": -5, "yield_impact": -0.3},
        "phase_preference": [EconomicPhase.CONTRACTION, EconomicPhase.TROUGH],
    },
    {
        "title": "Perth Outer Suburbs See 15% Price Falls",
        "description": "New housing estates face steep discounts as demand evaporates in fringe suburbs.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.CRITICAL,
        "probability": 0.03,
        "impact": {"property_value_impact": -2.0, "confidence_impact": -15},
        "phase_preference": [EconomicPhase.TROUGH],
    },
    # Affordability events
    {
        "title": "Housing Affordability Concerns Rise",
        "description": "First home buyers face increasing challenges as prices outpace wage growth.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.WARNING,
        "probability": 0.1,
        "impact": {"confidence_impact": -5},
        "phase_preference": [EconomicPhase.EXPANSION, EconomicPhase.PEAK],
    },
    {
        "title": "First Home Buyers Return as Prices Moderate",
        "description": "Price corrections create entry opportunities for new buyers.",
        "category": EventCategory.MARKET,
        "severity": EventSeverity.POSITIVE,
        "probability": 0.08,
        "impact": {"confidence_impact": 5, "property_value_impact": 0.3},
        "phase_preference": [EconomicPhase.TROUGH, EconomicPhase.RECOVERY],
    },
]

PROPERTY_EVENT_TEMPLATES = [
    {
        "title": "New Property Listed: {suburb}",
        "description": "A {type} in {suburb} has been added to the OSF network.",
        "category": EventCategory.PROPERTY,
        "severity": EventSeverity.INFO,
        "probability": 0.3,
        "impact": {"new_property": True},
    },
    {
        "title": "Property Fully Subscribed: {address}",
        "description": "All tokens for {address} have been purchased by network participants.",
        "category": EventCategory.PROPERTY,
        "severity": EventSeverity.MILESTONE,
        "probability": 0.1,
        "impact": {},
    },
    {
        "title": "Maintenance Required: {address}",
        "description": "Scheduled maintenance needed for {issue} at {address}.",
        "category": EventCategory.PROPERTY,
        "severity": EventSeverity.WARNING,
        "probability": 0.15,
        "impact": {"maintenance_cost": 2500},
        "issues": ["HVAC system", "roof repairs", "plumbing", "electrical work", "landscaping"],
    },
    {
        "title": "Emergency Repair: {address}",
        "description": "Urgent repairs required for {issue}. Tenant impact minimal.",
        "category": EventCategory.PROPERTY,
        "severity": EventSeverity.CRITICAL,
        "probability": 0.05,
        "impact": {"maintenance_cost": 8000, "rent_pause_weeks": 1},
        "issues": ["burst pipe", "electrical fault", "storm damage", "hot water system failure"],
    },
    {
        "title": "New Tenant Secured: {address}",
        "description": "Long-term lease signed at ${rent}/week, above market average.",
        "category": EventCategory.PROPERTY,
        "severity": EventSeverity.POSITIVE,
        "probability": 0.2,
        "impact": {"tenancy_secured": True},
    },
    {
        "title": "Property Valuation Updated: {address}",
        "description": "Independent valuation shows {change}% change in property value.",
        "category": EventCategory.PROPERTY,
        "severity": EventSeverity.INFO,
        "probability": 0.1,
        "impact": {"valuation_change": True},
    },
]

ECONOMIC_EVENT_TEMPLATES = [
    {
        "title": "Australian Economy Shows Strong Growth",
        "description": "GDP growth of {gdp}% signals robust economic conditions.",
        "category": EventCategory.ECONOMIC,
        "severity": EventSeverity.POSITIVE,
        "probability": 0.15,
        "impact": {"confidence_impact": 8, "phase_push": "expansion"},
        "phase_preference": [EconomicPhase.RECOVERY, EconomicPhase.EXPANSION],
    },
    {
        "title": "Employment Market Remains Tight",
        "description": "Unemployment holds at {unemployment}%, supporting housing demand.",
        "category": EventCategory.ECONOMIC,
        "severity": EventSeverity.INFO,
        "probability": 0.2,
        "impact": {"confidence_impact": 3},
    },
    {
        "title": "Mining Sector Boom Boosts WA Economy",
        "description": "Iron ore prices surge, benefiting Western Australian employment and property.",
        "category": EventCategory.ECONOMIC,
        "severity": EventSeverity.POSITIVE,
        "probability": 0.1,
        "impact": {"property_value_impact": 1.5, "rent_impact": 2},
    },
    {
        "title": "Consumer Confidence Drops",
        "description": "Economic uncertainty weighs on household spending intentions.",
        "category": EventCategory.ECONOMIC,
        "severity": EventSeverity.WARNING,
        "probability": 0.1,
        "impact": {"confidence_impact": -10},
        "phase_preference": [EconomicPhase.PEAK, EconomicPhase.CONTRACTION],
    },
    {
        "title": "Inflation Eases to {inflation}%",
        "description": "CPI data shows moderating price pressures, reducing rate hike pressure.",
        "category": EventCategory.ECONOMIC,
        "severity": EventSeverity.POSITIVE,
        "probability": 0.15,
        "impact": {"confidence_impact": 5},
        "phase_preference": [EconomicPhase.CONTRACTION, EconomicPhase.TROUGH],
    },
]

GOVERNANCE_EVENT_TEMPLATES = [
    {
        "title": "New Governance Proposal: {topic}",
        "description": "Token holders can now vote on {description}.",
        "category": EventCategory.GOVERNANCE,
        "severity": EventSeverity.INFO,
        "probability": 0.2,
        "impact": {"new_proposal": True},
        "topics": [
            ("Fee Reduction", "reducing management fees from 0.5% to 0.4%"),
            ("New Market Expansion", "expanding to Melbourne property market"),
            ("Dividend Policy", "increasing quarterly dividend payout ratio"),
            ("Emergency Fund", "building a larger maintenance reserve"),
        ],
    },
    {
        "title": "Proposal Passed: {topic}",
        "description": "Token holders voted to approve {topic} with {votes}% support.",
        "category": EventCategory.GOVERNANCE,
        "severity": EventSeverity.MILESTONE,
        "probability": 0.1,
        "impact": {"proposal_passed": True},
    },
    {
        "title": "Quarterly Dividends Distributed",
        "description": "OSF has distributed ${amount} in dividends to token holders.",
        "category": EventCategory.GOVERNANCE,
        "severity": EventSeverity.POSITIVE,
        "probability": 0.25,  # Once per quarter
        "impact": {"dividends_distributed": True},
    },
]


class EventGenerator:
    """Generates simulation events based on conditions."""
    
    def __init__(self):
        # Initialize with real Australian market data
        from src.services.market_data import get_market_data
        self.market_data = get_market_data()
        
        # Economic state calibrated from real data
        self.economic_state = EconomicState(
            phase=EconomicPhase.EXPANSION,  # Current market phase
            interest_rate=self.market_data.national.cash_rate,  # Real RBA rate
            inflation_rate=self.market_data.national.cpi_annual,  # Real CPI
            unemployment_rate=Decimal("3.8"),  # ABS data
            housing_index=Decimal("105"),  # Above baseline due to growth
            consumer_confidence=self.market_data.conditions.seller_confidence,
        )
        self._gemini_client = None
        self._probability_modifiers = self.market_data.get_event_probability_modifiers()
        
        logger.info("event_generator_initialized_with_market_data",
                   interest_rate=str(self.economic_state.interest_rate),
                   vacancy_rate=str(self.market_data.wa.rental_vacancy_rate))
    
    @property
    def gemini_client(self):
        if self._gemini_client is None:
            self._gemini_client = genai.Client(api_key=settings.gemini_api_key)
        return self._gemini_client
    
    def _should_trigger(self, template: Dict, phase: EconomicPhase) -> bool:
        """Determine if an event should trigger based on probability and phase."""
        base_prob = template.get("probability", 0.1)
        
        # Adjust probability based on phase preference
        phase_pref = template.get("phase_preference", [])
        if phase_pref and phase in phase_pref:
            base_prob *= 1.5
        elif phase_pref:
            base_prob *= 0.5
        
        # Apply market-data-driven modifiers
        event_type = template.get("title", "").lower()
        if "rent" in event_type and "rent_increase" in self._probability_modifiers:
            base_prob *= self._probability_modifiers["rent_increase"]
        if "investor" in event_type and "investor_competition" in self._probability_modifiers:
            base_prob *= self._probability_modifiers["investor_competition"]
        if "rate" in event_type:
            if "hold" in event_type:
                base_prob *= self._probability_modifiers.get("rate_hold", 1.0)
            elif "cut" in event_type:
                base_prob *= self._probability_modifiers.get("rate_cut", 1.0)
            elif "raise" in event_type or "hike" in event_type:
                base_prob *= self._probability_modifiers.get("rate_hike", 1.0)
        
        return random.random() < base_prob
    
    def _update_economic_cycle(self) -> Optional[SimulationEvent]:
        """Update economic cycle and potentially trigger phase transition."""
        self.economic_state.months_in_phase += 1
        
        # Phase transition logic
        transition_prob = min(0.3, self.economic_state.months_in_phase * 0.02)
        
        if random.random() < transition_prob:
            old_phase = self.economic_state.phase
            
            # Determine next phase
            phase_transitions = {
                EconomicPhase.EXPANSION: EconomicPhase.PEAK,
                EconomicPhase.PEAK: EconomicPhase.CONTRACTION,
                EconomicPhase.CONTRACTION: EconomicPhase.TROUGH,
                EconomicPhase.TROUGH: EconomicPhase.RECOVERY,
                EconomicPhase.RECOVERY: EconomicPhase.EXPANSION,
            }
            
            new_phase = phase_transitions[old_phase]
            self.economic_state.phase = new_phase
            self.economic_state.months_in_phase = 0
            
            # Adjust economic indicators
            if new_phase == EconomicPhase.CONTRACTION:
                self.economic_state.consumer_confidence -= 15
                self.economic_state.housing_index -= Decimal("3")
            elif new_phase == EconomicPhase.RECOVERY:
                self.economic_state.consumer_confidence += 10
            elif new_phase == EconomicPhase.EXPANSION:
                self.economic_state.housing_index += Decimal("2")
                self.economic_state.consumer_confidence += 5
            
            return SimulationEvent(
                id=str(uuid4()),
                category=EventCategory.ECONOMIC,
                severity=EventSeverity.INFO,
                title=f"Economic Cycle Shift: {new_phase.value.title()} Phase",
                description=f"The Australian economy has transitioned from {old_phase.value} to {new_phase.value} phase.",
                impact={
                    "phase_change": True,
                    "old_phase": old_phase.value,
                    "new_phase": new_phase.value,
                },
                narrative=self._generate_phase_narrative(old_phase, new_phase),
                month=0,  # Will be set by caller
            )
        
        return None
    
    def _generate_phase_narrative(self, old: EconomicPhase, new: EconomicPhase) -> str:
        """Generate narrative for economic phase transition."""
        narratives = {
            (EconomicPhase.EXPANSION, EconomicPhase.PEAK): 
                "After months of sustained growth, economists warn that the property market may be reaching its peak. Investors are advised to review their portfolios.",
            (EconomicPhase.PEAK, EconomicPhase.CONTRACTION):
                "The RBA's rate hiking cycle appears to be cooling the overheated market. Property prices have begun to stabilize as buyers become more cautious.",
            (EconomicPhase.CONTRACTION, EconomicPhase.TROUGH):
                "Market conditions have softened significantly. While challenging for sellers, this presents opportunities for long-term investors to enter at attractive prices.",
            (EconomicPhase.TROUGH, EconomicPhase.RECOVERY):
                "Early signs of recovery are emerging in the property market. First home buyers are returning, and investor confidence is slowly rebuilding.",
            (EconomicPhase.RECOVERY, EconomicPhase.EXPANSION):
                "The property market has entered a new growth phase. Strong fundamentals and improved affordability are driving renewed buyer interest.",
        }
        return narratives.get((old, new), "The economic cycle continues to evolve.")
    
    def generate_events(
        self,
        network_month: int,
        properties: List[Dict[str, Any]],
        participants: List[Dict[str, Any]],
    ) -> List[SimulationEvent]:
        """Generate events for the current month."""
        events = []
        
        # Check for economic phase transition
        phase_event = self._update_economic_cycle()
        if phase_event:
            phase_event.month = network_month
            events.append(phase_event)
        
        # Generate iron ore events (WA's primary economic driver)
        for template in IRON_ORE_EVENT_TEMPLATES:
            if self._should_trigger(template, self.economic_state.phase):
                event = self._create_commodity_event(template, network_month)
                if event:
                    events.append(event)
                    # Apply iron ore impact to economic state
                    if "iron_ore_price" in template.get("impact", {}):
                        self.economic_state.iron_ore_price = Decimal(str(template["impact"]["iron_ore_price"]))
                    break  # Only one iron ore event per month
        
        # Generate population events (critical for WA property demand)
        if random.random() < 0.3:  # 30% chance each month
            for template in POPULATION_EVENT_TEMPLATES:
                if self._should_trigger(template, self.economic_state.phase):
                    event = self._create_population_event(template, network_month)
                    if event:
                        events.append(event)
                        # Apply population impact
                        if "population_growth" in template.get("impact", {}):
                            self.economic_state.population_growth_rate = Decimal(str(template["impact"]["population_growth"]))
                        if "vacancy_impact" in template.get("impact", {}):
                            self.economic_state.vacancy_rate += Decimal(str(template["impact"]["vacancy_impact"]))
                            self.economic_state.vacancy_rate = max(Decimal("0.5"), min(Decimal("8.0"), self.economic_state.vacancy_rate))
                        break
        
        # Update market condition based on current state
        self.economic_state.update_market_condition()
        
        # Generate market events
        for template in MARKET_EVENT_TEMPLATES:
            if self._should_trigger(template, self.economic_state.phase):
                event = self._create_market_event(template, network_month)
                if event:
                    events.append(event)
                    break  # Only one market event per month
        
        # Generate property events
        if properties:
            for template in PROPERTY_EVENT_TEMPLATES:
                if self._should_trigger(template, self.economic_state.phase):
                    prop = random.choice(properties)
                    event = self._create_property_event(template, prop, network_month)
                    if event:
                        events.append(event)
                        if len([e for e in events if e.category == EventCategory.PROPERTY]) >= 2:
                            break
        
        # Generate economic events
        for template in ECONOMIC_EVENT_TEMPLATES:
            if self._should_trigger(template, self.economic_state.phase):
                event = self._create_economic_event(template, network_month)
                if event:
                    events.append(event)
                    break
        
        # Generate governance events (quarterly)
        if network_month % 3 == 0:
            for template in GOVERNANCE_EVENT_TEMPLATES:
                if self._should_trigger(template, self.economic_state.phase):
                    event = self._create_governance_event(template, network_month)
                    if event:
                        events.append(event)
                        break
        
        logger.info("events_generated", month=network_month, count=len(events))
        return events
    
    def _create_market_event(
        self, template: Dict, month: int
    ) -> Optional[SimulationEvent]:
        """Create a market event from template."""
        title = template["title"].format(rate=float(self.economic_state.interest_rate))
        
        return SimulationEvent(
            id=str(uuid4()),
            category=template["category"],
            severity=template["severity"],
            title=title,
            description=template["description"],
            impact=template["impact"].copy(),
            narrative=self._generate_market_narrative(template),
            month=month,
        )
    
    def _create_commodity_event(
        self, template: Dict, month: int
    ) -> Optional[SimulationEvent]:
        """Create an iron ore/commodity event from template."""
        return SimulationEvent(
            id=str(uuid4()),
            category=EventCategory.ECONOMIC,
            severity=template["severity"],
            title=template["title"],
            description=template["description"],
            impact=template["impact"].copy(),
            narrative=self._generate_commodity_narrative(template),
            month=month,
        )
    
    def _create_population_event(
        self, template: Dict, month: int
    ) -> Optional[SimulationEvent]:
        """Create a population/migration event from template."""
        return SimulationEvent(
            id=str(uuid4()),
            category=EventCategory.ECONOMIC,
            severity=template["severity"],
            title=template["title"],
            description=template["description"],
            impact=template["impact"].copy(),
            narrative=self._generate_population_narrative(template),
            month=month,
        )
    
    def _generate_commodity_narrative(self, template: Dict) -> str:
        """Generate narrative for iron ore events."""
        iron_price = template.get("impact", {}).get("iron_ore_price", 110)
        if iron_price >= 150:
            return f"The Pilbara is buzzing with activity as iron ore hits ${iron_price}/tonne. Mining companies report record profits, and Perth real estate agents are fielding calls from cashed-up FIFO workers looking to buy."
        elif iron_price >= 100:
            return f"Iron ore remains steady at ${iron_price}/tonne, supporting WA's economy. The mining sector continues to be a reliable employer, though the boom days have cooled."
        elif iron_price >= 80:
            return f"Iron ore has slipped to ${iron_price}/tonne, putting pressure on marginal mining operations. Some contractors are already being let go, and the ripple effects are starting to reach Perth's property market."
        else:
            return f"Iron ore has crashed to ${iron_price}/tonne, triggering layoffs across the Pilbara. Real estate agents in mining towns report properties sitting unsold for months. Perth's outer suburbs are also feeling the pinch."
    
    def _generate_population_narrative(self, template: Dict) -> str:
        """Generate narrative for population events."""
        pop_growth = template.get("impact", {}).get("population_growth", 1.5)
        if pop_growth >= 2.0:
            return f"Western Australia is experiencing a population surge, with annual growth hitting {pop_growth}%. New arrivals are competing for limited housing stock, driving up rents and property prices across Perth."
        elif pop_growth >= 1.0:
            return f"WA's population growth has moderated to {pop_growth}% annually. The housing market remains balanced, with steady demand meeting available supply."
        elif pop_growth >= 0:
            return f"Population growth has slowed significantly to just {pop_growth}%. Fewer people moving to WA means softer demand for housing, particularly in areas that boomed during the mining expansion."
        else:
            return f"Western Australia is experiencing net population outflow for the first time in years. Families are relocating to eastern states for better job opportunities, leaving behind vacant properties and falling rents."
    
    def _create_property_event(
        self, template: Dict, property: Dict, month: int
    ) -> Optional[SimulationEvent]:
        """Create a property event from template."""
        address = property.get("address", "Unknown Property")
        suburb = property.get("suburb", "Perth")
        prop_type = property.get("property_type", "property")
        rent = property.get("weekly_rent", 600)
        
        # Select random issue if applicable
        issue = ""
        if "issues" in template:
            issue = random.choice(template["issues"])
        
        # Handle valuation change
        change = random.choice([-2, -1, 1, 2, 3, 4, 5])
        
        title = template["title"].format(
            address=address[:30],
            suburb=suburb,
            type=prop_type,
            issue=issue,
            rent=rent,
            change=change,
        )
        description = template["description"].format(
            address=address,
            suburb=suburb,
            type=prop_type,
            issue=issue,
            rent=rent,
            change=change,
        )
        
        impact = template["impact"].copy()
        if "valuation_change" in impact:
            impact["valuation_percent"] = change
        
        return SimulationEvent(
            id=str(uuid4()),
            category=template["category"],
            severity=template["severity"],
            title=title,
            description=description,
            impact=impact,
            narrative=self._generate_property_narrative(template, property, issue),
            month=month,
            property_id=property.get("id"),
        )
    
    def _create_economic_event(
        self, template: Dict, month: int
    ) -> Optional[SimulationEvent]:
        """Create an economic event from template."""
        title = template["title"].format(
            gdp=round(random.uniform(0.3, 0.8), 1),
            unemployment=float(self.economic_state.unemployment_rate),
            inflation=float(self.economic_state.inflation_rate),
        )
        
        return SimulationEvent(
            id=str(uuid4()),
            category=template["category"],
            severity=template["severity"],
            title=title,
            description=template["description"],
            impact=template["impact"].copy(),
            narrative=self._generate_economic_narrative(template),
            month=month,
        )
    
    def _create_governance_event(
        self, template: Dict, month: int
    ) -> Optional[SimulationEvent]:
        """Create a governance event from template."""
        if "topics" in template:
            topic, desc = random.choice(template["topics"])
            title = template["title"].format(topic=topic)
            description = template["description"].format(topic=topic, description=desc)
        else:
            title = template["title"].format(
                topic="Network Policy",
                votes=random.randint(60, 85),
                amount=random.randint(50000, 150000),
            )
            description = template["description"].format(
                topic="the proposed changes",
                votes=random.randint(60, 85),
                amount=random.randint(50000, 150000),
            )
        
        return SimulationEvent(
            id=str(uuid4()),
            category=template["category"],
            severity=template["severity"],
            title=title,
            description=description,
            impact=template["impact"].copy(),
            narrative="",  # Governance events don't need extended narrative
            month=month,
        )
    
    def _generate_market_narrative(self, template: Dict) -> str:
        """Generate narrative for market events."""
        return template["description"]
    
    def _generate_property_narrative(
        self, template: Dict, property: Dict, issue: str
    ) -> str:
        """Generate narrative for property events."""
        return template["description"].format(
            address=property.get("address", "the property"),
            suburb=property.get("suburb", "Perth"),
            type=property.get("property_type", "property"),
            issue=issue,
            rent=property.get("weekly_rent", 600),
            change=random.randint(-2, 5),
        )
    
    def _generate_economic_narrative(self, template: Dict) -> str:
        """Generate narrative for economic events."""
        return template["description"]
    
    async def generate_news_article(
        self,
        events: List[SimulationEvent],
        network_month: int,
    ) -> str:
        """Generate a news article summarizing the month's events using Gemini."""
        if not events:
            return ""
        
        event_summaries = "\n".join([
            f"- {e.title}: {e.description}"
            for e in events[:5]  # Top 5 events
        ])
        
        # Include real market context
        market_context = self.market_data.format_for_prompt()
        
        prompt = f"""You are a financial news writer for the OSF Property Network newsletter.
Write a brief, engaging news summary (150-200 words) for Month {network_month} of the simulation.

Key events this month:
{event_summaries}

Simulation Economic State:
- Phase: {self.economic_state.phase.value}
- Interest rate: {self.economic_state.interest_rate}%
- Consumer confidence: {self.economic_state.consumer_confidence}/100

{market_context}

Write in a professional but accessible tone. Focus on what these events mean for 
property investors in the Perth/WA market. Reference real market conditions where 
relevant (e.g., tight rental vacancy, strong investor activity). End with a brief outlook.

Remember this is an educational simulation - frame insights as learning opportunities.
Do not use markdown formatting. Write as plain prose suitable for a newsletter."""

        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-3-flash",
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            logger.error("news_generation_failed", error=str(e))
            # Fallback to simple summary
            return f"Month {network_month} saw {len(events)} notable events in the OSF network."
    
    async def save_events(
        self,
        events: List[SimulationEvent],
    ) -> int:
        """Save events to database."""
        saved = 0
        async with async_session() as session:
            repo = NetworkRepository(session)
            for event in events:
                await repo.create_event(
                    network_month=event.month,
                    event_type=event.category.value,
                    title=event.title,
                    description=event.description,
                    severity=event.severity.value,
                    property_id=event.property_id,
                    participant_id=event.participant_id,
                    data=event.to_dict(),
                )
                saved += 1
            await session.commit()
        return saved
    
    def get_economic_state(self) -> Dict[str, Any]:
        """Get current economic state."""
        return self.economic_state.to_dict()


# Singleton instance
_event_generator: Optional[EventGenerator] = None


def get_event_generator() -> EventGenerator:
    """Get the event generator singleton."""
    global _event_generator
    if _event_generator is None:
        _event_generator = EventGenerator()
    return _event_generator
