"""
OSF Demo - Energy API
Energy asset monitoring and management endpoints
"""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

from src.ai.energy import EnergyManager
from src.ai.core import OSFCore, AssetClass

router = APIRouter()
energy_manager = EnergyManager()
osf_core = OSFCore()


class SystemInfo(BaseModel):
    """Energy system information."""
    id: str = "demo-solar-001"
    asset_type: str = "solar"
    capacity_kw: float = 10.0
    location: str = "Sydney, NSW"
    panels: int = 25
    inverter: str = "Fronius Primo 10.0"
    installation_year: int = 2023


class Readings(BaseModel):
    """Current system readings."""
    output_kw: float
    voltage_v: float = 240.0
    frequency_hz: float = 50.0
    temperature_c: float = 25.0
    irradiance_w_m2: Optional[float] = None


class Weather(BaseModel):
    """Weather conditions."""
    cloud_cover_percent: float = 0.0
    temperature_c: float = 25.0
    humidity_percent: float = 50.0
    description: str = "Clear sky"


class ProductionRequest(BaseModel):
    """Request for production analysis."""
    system_info: SystemInfo
    readings: Readings
    weather: Optional[Weather] = None


class ProductionResponse(BaseModel):
    """Production analysis response."""
    current_output_kw: float
    expected_output_kw: float
    efficiency_percent: float
    status: str
    diagnosis: str
    recommendations: list[str]
    estimated_daily_production_kwh: float
    carbon_offset_kg: float


class AlertResponse(BaseModel):
    """Alert from monitoring."""
    severity: str
    alert_type: str
    message: str
    asset_id: str
    recommended_action: str
    estimated_revenue_impact: Optional[float] = None


class IssueRequest(BaseModel):
    """Issue report for triage."""
    description: str
    system_data: Optional[dict] = None


class TriageResponse(BaseModel):
    """Triage result."""
    urgency: str
    category: str
    diagnosis: str
    recommended_action: str
    requires_specialist: bool
    estimated_cost_low: Optional[float] = None
    estimated_cost_high: Optional[float] = None
    safety_concern: Optional[bool] = None
    estimated_production_loss_kwh: Optional[float] = None


@router.post("/analyze", response_model=ProductionResponse)
async def analyze_production(request: ProductionRequest):
    """
    Analyze current energy production.
    
    Compares actual output to expected output based on:
    - System specifications
    - Current readings
    - Weather conditions
    
    Returns efficiency analysis and recommendations.
    """
    result = await energy_manager.analyze_production(
        system_info=request.system_info.model_dump(),
        readings=request.readings.model_dump(),
        weather=request.weather.model_dump() if request.weather else None,
    )
    
    return ProductionResponse(
        current_output_kw=result.current_output_kw,
        expected_output_kw=result.expected_output_kw,
        efficiency_percent=result.efficiency_percent,
        status=result.status,
        diagnosis=result.diagnosis,
        recommendations=result.recommendations,
        estimated_daily_production_kwh=result.estimated_daily_production_kwh,
        carbon_offset_kg=result.carbon_offset_kg,
    )


@router.post("/alerts", response_model=list[AlertResponse])
async def generate_alerts(request: ProductionRequest):
    """
    Generate alerts based on current system state.
    
    Monitors for:
    - Production anomalies
    - Equipment issues
    - Grid problems
    - Safety concerns
    """
    current_state = {
        **request.readings.model_dump(),
        "weather": request.weather.model_dump() if request.weather else None,
    }
    
    alerts = await energy_manager.generate_alerts(
        system_info=request.system_info.model_dump(),
        current_state=current_state,
    )
    
    return [
        AlertResponse(
            severity=a.severity,
            alert_type=a.alert_type,
            message=a.message,
            asset_id=a.asset_id,
            recommended_action=a.recommended_action,
            estimated_revenue_impact=a.estimated_revenue_impact,
        )
        for a in alerts
    ]


@router.post("/triage", response_model=TriageResponse)
async def triage_issue(request: IssueRequest):
    """
    Triage an energy system issue.
    
    Classifies urgency and provides diagnosis:
    - emergency: Safety risk, fire hazard (immediate)
    - urgent: System offline, major production loss (24hr)
    - routine: Minor issues, optimization (7 day)
    - planned: Upgrades, scheduled maintenance
    """
    result = await osf_core.triage(
        description=request.description,
        asset_class=AssetClass.ENERGY,
        system_data=request.system_data,
    )
    
    return TriageResponse(
        urgency=result.urgency,
        category=result.category,
        diagnosis=result.diagnosis,
        recommended_action=result.recommended_action,
        requires_specialist=result.requires_specialist,
        estimated_cost_low=result.estimated_cost_low,
        estimated_cost_high=result.estimated_cost_high,
        safety_concern=result.metadata.get("safety_concern") if result.metadata else None,
        estimated_production_loss_kwh=result.metadata.get("estimated_production_loss_kwh") if result.metadata else None,
    )


# Demo endpoints with mock data
@router.get("/demo/systems")
async def get_demo_systems():
    """Get demo energy systems."""
    return {
        "systems": [
            {
                "id": "solar-sydney-001",
                "name": "Sydney Rooftop Solar",
                "type": "solar",
                "capacity_kw": 10.0,
                "location": "Sydney, NSW",
                "status": "online",
                "current_output_kw": 7.5,
                "today_production_kwh": 42.3,
                "efficiency_percent": 94.2,
            },
            {
                "id": "solar-melbourne-001",
                "name": "Melbourne Commercial Solar",
                "type": "solar",
                "capacity_kw": 50.0,
                "location": "Melbourne, VIC",
                "status": "online",
                "current_output_kw": 38.2,
                "today_production_kwh": 198.5,
                "efficiency_percent": 91.8,
            },
            {
                "id": "battery-brisbane-001",
                "name": "Brisbane Battery Storage",
                "type": "battery",
                "capacity_kw": 13.5,
                "capacity_kwh": 27.0,
                "location": "Brisbane, QLD",
                "status": "charging",
                "state_of_charge_percent": 65.0,
                "current_power_kw": 5.0,
            },
        ],
        "total": 3,
        "total_capacity_kw": 73.5,
        "current_output_kw": 45.7,
    }
