"""
OSPF Demo - Property Valuation Engine
AI-powered property valuation with reasoning
"""

import json
from dataclasses import dataclass
from typing import Optional

from google import genai
from google.genai import types
import structlog

from src.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


@dataclass
class PropertyValuation:
    """Property valuation result."""
    estimated_value: float
    confidence_low: float
    confidence_high: float
    confidence_level: str  # low, medium, high
    reasoning: str
    key_factors: list[str]
    comparables_used: int
    valuation_method: str


class ValuationEngine:
    """
    AI-powered property valuation.
    
    Analyzes property details and market context to estimate value.
    """
    
    VALUATION_PROMPT = """You are a property valuation AI for OSPF operating in Australia.

Analyze this property and provide a valuation estimate.

PROPERTY DETAILS:
{property_data}

MARKET CONTEXT:
- Current Australian property market conditions
- Interest rates at ~{interest_rate}%
- Consider suburb, property type, condition

Provide a valuation in JSON format:
{{
    "estimated_value": number (AUD),
    "confidence_low": number (10th percentile estimate),
    "confidence_high": number (90th percentile estimate),
    "confidence_level": "low|medium|high",
    "reasoning": "Detailed explanation of valuation",
    "key_factors": ["list", "of", "key", "value", "drivers"],
    "comparables_used": number (how many similar properties considered),
    "valuation_method": "comparable_sales|income_approach|cost_approach"
}}

Be conservative and explain your reasoning."""

    def __init__(self):
        """Initialize valuation engine."""
        if settings.google_api_key:
            self.client = genai.Client(api_key=settings.google_api_key)
            self.model_name = settings.gemini_pro_model
        else:
            self.client = None
            self.model_name = None
            logger.warning("valuation_engine_not_configured")

    async def value_property(
        self,
        property_data: dict,
        interest_rate: float = 4.35,
    ) -> PropertyValuation:
        """
        Value a property using AI analysis.
        
        Args:
            property_data: Dict containing:
                - address: str
                - suburb: str
                - state: str
                - property_type: str (house, apartment, townhouse)
                - bedrooms: int
                - bathrooms: int
                - parking: int
                - land_size_sqm: float (optional)
                - floor_area_sqm: float (optional)
                - year_built: int (optional)
                - condition: str (optional)
                - features: list[str] (optional)
            interest_rate: Current RBA rate
            
        Returns:
            PropertyValuation with estimate and reasoning
        """
        if not self.client:
            return PropertyValuation(
                estimated_value=0,
                confidence_low=0,
                confidence_high=0,
                confidence_level="low",
                reasoning="AI valuation unavailable",
                key_factors=[],
                comparables_used=0,
                valuation_method="unavailable",
            )
        
        prompt = self.VALUATION_PROMPT.format(
            property_data=json.dumps(property_data, indent=2),
            interest_rate=interest_rate,
        )
        
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            data = json.loads(text.strip())
            
            result = PropertyValuation(
                estimated_value=float(data.get("estimated_value", 0)),
                confidence_low=float(data.get("confidence_low", 0)),
                confidence_high=float(data.get("confidence_high", 0)),
                confidence_level=data.get("confidence_level", "low"),
                reasoning=data.get("reasoning", "No reasoning provided"),
                key_factors=data.get("key_factors", []),
                comparables_used=int(data.get("comparables_used", 0)),
                valuation_method=data.get("valuation_method", "unknown"),
            )
            
            logger.info("property_valued",
                       estimated_value=result.estimated_value,
                       confidence=result.confidence_level)
            
            return result
            
        except Exception as e:
            logger.error("valuation_error", error=str(e))
            return PropertyValuation(
                estimated_value=0,
                confidence_low=0,
                confidence_high=0,
                confidence_level="low",
                reasoning=f"Valuation error: {str(e)}",
                key_factors=[],
                comparables_used=0,
                valuation_method="error",
            )

    async def analyze_property_photos(
        self,
        photos: list[bytes],
        property_data: dict = None,
    ) -> dict:
        """
        Analyze property photos to assess condition and features.
        
        Args:
            photos: List of property images
            property_data: Optional known property details
            
        Returns:
            Analysis including condition, features, concerns
        """
        if not self.client or not photos:
            return {"error": "Analysis unavailable", "analyzed": False}
        
        prompt = """Analyze these property photos. Assess:
1. Overall condition (excellent, good, fair, poor)
2. Visible features (pool, renovated kitchen, etc.)
3. Any concerns (damage, maintenance issues)
4. Quality of finishes
5. Estimated age/era of construction

Respond in JSON:
{
    "overall_condition": "excellent|good|fair|poor",
    "condition_notes": "description",
    "features_identified": ["list of features"],
    "concerns": ["any issues spotted"],
    "finish_quality": "high|medium|low",
    "estimated_era": "description",
    "would_affect_valuation": "positive|neutral|negative"
}"""
        
        try:
            parts = [types.Part.from_text(text=prompt)]
            for photo in photos[:5]:  # Limit to 5 photos
                parts.append(types.Part.from_bytes(data=photo, mime_type="image/jpeg"))
            
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=parts,
            )
            
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            data = json.loads(text.strip())
            data["analyzed"] = True
            
            logger.info("property_photos_analyzed",
                       condition=data.get("overall_condition"))
            
            return data
            
        except Exception as e:
            logger.error("photo_analysis_error", error=str(e))
            return {"error": str(e), "analyzed": False}
