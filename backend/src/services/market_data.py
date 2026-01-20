"""
Market Data Service
Real Australian housing market data for simulation calibration

Sources:
- RBA Statistical Table E2 (Household Finances)
- APRA ADI Property Exposure Statistics
- ABS Lending Indicators
- ABS Total Value of Dwellings
- REIWA (WA specific)
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import datetime
import structlog

logger = structlog.get_logger()


@dataclass
class NationalMarketData:
    """Australian national housing market metrics."""
    
    # Household Debt (RBA E2, Q2 2025)
    debt_to_income_ratio: Decimal = Decimal("1.82")  # 182%
    housing_debt_to_income: Decimal = Decimal("1.34")  # 134%
    
    # Mortgage Credit Growth (APRA, Sep 2024)
    mortgage_credit_growth_yoy: Decimal = Decimal("0.047")  # 4.7%
    owner_occupier_credit_growth: Decimal = Decimal("0.052")  # 5.2%
    investor_credit_growth: Decimal = Decimal("0.047")  # 4.7%
    
    # New Lending (ABS, Sep Q 2025)
    total_lending_growth_yoy: Decimal = Decimal("0.058")  # 5.8%
    investor_lending_growth_value: Decimal = Decimal("0.187")  # 18.7%
    investor_lending_growth_number: Decimal = Decimal("0.123")  # 12.3%
    
    # Dwelling Values (ABS, Jun Q 2025)
    total_dwelling_value_billion: Decimal = Decimal("11564.0")
    total_dwellings_count: int = 11373900
    mean_dwelling_price: Decimal = Decimal("1016700")
    
    # RBA Cash Rate
    cash_rate: Decimal = Decimal("4.35")
    
    # Inflation
    cpi_annual: Decimal = Decimal("3.2")
    
    # Source metadata
    data_date: str = "2025-Q2"
    sources: Dict[str, str] = field(default_factory=lambda: {
        "debt_ratios": "RBA Statistical Table E2",
        "credit_growth": "APRA ADI Property Exposure Statistics",
        "lending": "ABS Lending Indicators",
        "dwelling_values": "ABS Total Value of Dwellings",
    })


@dataclass
class WAMarketData:
    """Western Australia specific market metrics."""
    
    # Perth Dwelling Prices (REIWA, Dec 2025 est.)
    median_house_price: Decimal = Decimal("750000")
    median_unit_price: Decimal = Decimal("480000")
    
    # Price relative to national
    price_ratio_to_national: Decimal = Decimal("0.74")  # Perth ~74% of national
    
    # Rental Market (REIWA)
    rental_vacancy_rate: Decimal = Decimal("0.008")  # 0.8% - very tight
    median_weekly_rent_house: Decimal = Decimal("650")
    median_weekly_rent_unit: Decimal = Decimal("550")
    rental_growth_yoy: Decimal = Decimal("0.08")  # 8% annual growth
    
    # Gross Rental Yield
    gross_yield_house: Decimal = Decimal("0.045")  # 4.5%
    gross_yield_unit: Decimal = Decimal("0.060")  # 6.0%
    
    # Market Conditions
    days_on_market_median: int = 12  # Fast selling market
    auction_clearance_rate: Decimal = Decimal("0.72")  # 72%
    
    # Regional Economic Factors
    mining_employment_growth: Decimal = Decimal("0.03")  # 3%
    population_growth: Decimal = Decimal("0.023")  # 2.3%
    
    # Source metadata
    data_date: str = "2025-Q4"
    sources: Dict[str, str] = field(default_factory=lambda: {
        "prices": "REIWA Market Update",
        "rentals": "REIWA Rental Statistics",
        "economic": "WA Government Statistics",
    })


@dataclass
class MarketConditions:
    """Derived market conditions for simulation."""
    
    # Market Health Indicators (0-100)
    buyer_demand: int = 70  # High demand
    seller_confidence: int = 65
    investor_activity: int = 75  # Strong investor presence
    rental_pressure: int = 85  # Very tight rental market
    
    # Trend Indicators
    price_trend: str = "growing"  # growing, stable, declining
    rent_trend: str = "growing"
    interest_rate_outlook: str = "stable"  # rising, stable, falling
    
    # Risk Factors
    affordability_stress: str = "high"
    debt_serviceability: str = "moderate"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "buyer_demand": self.buyer_demand,
            "seller_confidence": self.seller_confidence,
            "investor_activity": self.investor_activity,
            "rental_pressure": self.rental_pressure,
            "price_trend": self.price_trend,
            "rent_trend": self.rent_trend,
            "interest_rate_outlook": self.interest_rate_outlook,
            "affordability_stress": self.affordability_stress,
            "debt_serviceability": self.debt_serviceability,
        }


class MarketDataService:
    """
    Provides real market data for simulation calibration.
    
    This service makes the simulation grounded in actual Australian
    housing market conditions, particularly for Western Australia.
    """
    
    def __init__(self):
        self.national = NationalMarketData()
        self.wa = WAMarketData()
        self._conditions: Optional[MarketConditions] = None
        logger.info("market_data_service_initialized",
                   national_mean_price=str(self.national.mean_dwelling_price),
                   wa_median_price=str(self.wa.median_house_price))
    
    @property
    def conditions(self) -> MarketConditions:
        """Get derived market conditions."""
        if self._conditions is None:
            self._conditions = self._derive_conditions()
        return self._conditions
    
    def _derive_conditions(self) -> MarketConditions:
        """Derive market conditions from raw data."""
        conditions = MarketConditions()
        
        # Investor activity based on lending growth
        if self.national.investor_lending_growth_value > Decimal("0.15"):
            conditions.investor_activity = 80
        elif self.national.investor_lending_growth_value > Decimal("0.10"):
            conditions.investor_activity = 70
        else:
            conditions.investor_activity = 60
        
        # Rental pressure based on vacancy
        if self.wa.rental_vacancy_rate < Decimal("0.01"):
            conditions.rental_pressure = 90
        elif self.wa.rental_vacancy_rate < Decimal("0.02"):
            conditions.rental_pressure = 75
        else:
            conditions.rental_pressure = 50
        
        # Price trend based on credit growth
        if self.national.mortgage_credit_growth_yoy > Decimal("0.05"):
            conditions.price_trend = "growing"
        elif self.national.mortgage_credit_growth_yoy < Decimal("0.02"):
            conditions.price_trend = "declining"
        else:
            conditions.price_trend = "stable"
        
        # Affordability based on debt-to-income
        if self.national.debt_to_income_ratio > Decimal("1.8"):
            conditions.affordability_stress = "high"
        elif self.national.debt_to_income_ratio > Decimal("1.5"):
            conditions.affordability_stress = "moderate"
        else:
            conditions.affordability_stress = "low"
        
        return conditions
    
    def get_property_valuation_range(self, property_type: str = "house") -> Dict[str, Decimal]:
        """Get realistic property valuation range for WA."""
        if property_type == "house":
            median = self.wa.median_house_price
        else:
            median = self.wa.median_unit_price
        
        return {
            "min": median * Decimal("0.4"),   # Entry level
            "median": median,
            "max": median * Decimal("3.0"),   # Premium
            "mean": median * Decimal("1.1"),  # Slightly above median
        }
    
    def get_rental_yield_expectation(self, property_type: str = "house") -> Decimal:
        """Get expected gross rental yield for property type."""
        if property_type == "house":
            return self.wa.gross_yield_house
        return self.wa.gross_yield_unit
    
    def get_weekly_rent_range(self, property_type: str = "house") -> Dict[str, Decimal]:
        """Get realistic weekly rent range for WA."""
        if property_type == "house":
            median = self.wa.median_weekly_rent_house
        else:
            median = self.wa.median_weekly_rent_unit
        
        return {
            "min": median * Decimal("0.5"),
            "median": median,
            "max": median * Decimal("2.5"),
        }
    
    def get_event_probability_modifiers(self) -> Dict[str, float]:
        """
        Get probability modifiers for events based on market conditions.
        
        Returns multipliers to apply to base event probabilities.
        """
        modifiers = {}
        
        # Tight rental market = more rent increase events
        if self.wa.rental_vacancy_rate < Decimal("0.01"):
            modifiers["rent_increase"] = 1.8
            modifiers["tenant_competition"] = 2.0
        elif self.wa.rental_vacancy_rate < Decimal("0.02"):
            modifiers["rent_increase"] = 1.3
            modifiers["tenant_competition"] = 1.5
        else:
            modifiers["rent_increase"] = 1.0
            modifiers["tenant_competition"] = 1.0
        
        # High investor activity = more competition, faster sales
        investor_growth = float(self.national.investor_lending_growth_value)
        modifiers["investor_competition"] = 1.0 + investor_growth
        modifiers["quick_sale"] = 1.0 + (investor_growth * 0.5)
        
        # Interest rate sensitivity
        if self.national.cash_rate > Decimal("4.0"):
            modifiers["rate_hold"] = 1.5
            modifiers["rate_cut"] = 0.5
            modifiers["rate_hike"] = 0.8
        else:
            modifiers["rate_hold"] = 1.0
            modifiers["rate_cut"] = 1.0
            modifiers["rate_hike"] = 1.0
        
        # Mining boom effects (WA specific)
        if self.wa.mining_employment_growth > Decimal("0.02"):
            modifiers["economic_positive"] = 1.5
            modifiers["wa_outperformance"] = 2.0
        
        return modifiers
    
    def get_npc_behavior_calibration(self) -> Dict[str, Any]:
        """
        Get calibration values for NPC behavior based on real market data.
        
        Returns parameters that should influence NPC decision-making.
        """
        return {
            # Leverage behavior (Australians are highly leveraged)
            "typical_leverage_ratio": float(self.national.debt_to_income_ratio),
            "max_safe_leverage": 2.0,  # Conservative limit
            
            # Investment appetite
            "investor_activity_score": self.conditions.investor_activity,
            "investor_lending_momentum": float(self.national.investor_lending_growth_value),
            
            # Yield expectations
            "minimum_acceptable_yield": 0.035,  # 3.5%
            "target_yield_house": float(self.wa.gross_yield_house),
            "target_yield_unit": float(self.wa.gross_yield_unit),
            
            # Price sensitivity
            "wa_discount_to_national": float(self.wa.price_ratio_to_national),
            "price_growth_expectation": float(self.national.mortgage_credit_growth_yoy),
            
            # Rental market
            "vacancy_rate": float(self.wa.rental_vacancy_rate),
            "rent_growth_expectation": float(self.wa.rental_growth_yoy),
            
            # Time preferences
            "expected_days_on_market": self.wa.days_on_market_median,
        }
    
    def get_simulation_context(self) -> Dict[str, Any]:
        """Get full market context for Gemini prompts."""
        return {
            "national": {
                "debt_to_income": f"{float(self.national.debt_to_income_ratio) * 100:.0f}%",
                "mortgage_growth": f"{float(self.national.mortgage_credit_growth_yoy) * 100:.1f}%",
                "investor_lending_growth": f"{float(self.national.investor_lending_growth_value) * 100:.1f}%",
                "mean_dwelling_price": f"${int(self.national.mean_dwelling_price):,}",
                "cash_rate": f"{float(self.national.cash_rate):.2f}%",
            },
            "wa": {
                "median_house_price": f"${int(self.wa.median_house_price):,}",
                "median_rent": f"${int(self.wa.median_weekly_rent_house)}/week",
                "vacancy_rate": f"{float(self.wa.rental_vacancy_rate) * 100:.1f}%",
                "gross_yield": f"{float(self.wa.gross_yield_house) * 100:.1f}%",
            },
            "conditions": self.conditions.to_dict(),
            "sources": {
                **self.national.sources,
                **self.wa.sources,
            },
        }
    
    def format_for_prompt(self) -> str:
        """Format market data for inclusion in Gemini prompts."""
        return f"""
Australian Housing Market Context (Educational Simulation):

National Metrics:
- Household debt-to-income: {float(self.national.debt_to_income_ratio) * 100:.0f}%
- Mortgage credit growth: {float(self.national.mortgage_credit_growth_yoy) * 100:.1f}% year-on-year
- Investor lending growth: {float(self.national.investor_lending_growth_value) * 100:.1f}% (value)
- Mean dwelling price: ${int(self.national.mean_dwelling_price):,}
- RBA cash rate: {float(self.national.cash_rate):.2f}%

Western Australia (Simulation Focus):
- Perth median house price: ${int(self.wa.median_house_price):,}
- Median weekly rent: ${int(self.wa.median_weekly_rent_house)}/week
- Rental vacancy rate: {float(self.wa.rental_vacancy_rate) * 100:.1f}% (very tight)
- Gross rental yield: {float(self.wa.gross_yield_house) * 100:.1f}%
- Days on market: {self.wa.days_on_market_median} (fast market)

Market Conditions:
- Price trend: {self.conditions.price_trend}
- Rental pressure: {self.conditions.rental_pressure}/100 (very high)
- Investor activity: {self.conditions.investor_activity}/100
- Affordability stress: {self.conditions.affordability_stress}

Note: This data is for educational simulation purposes only.
"""


# Singleton instance
_market_data_service: Optional[MarketDataService] = None


def get_market_data() -> MarketDataService:
    """Get the market data service singleton."""
    global _market_data_service
    if _market_data_service is None:
        _market_data_service = MarketDataService()
    return _market_data_service
