"""
OSPF Demo - Tenant Screening Engine
Fair, explainable AI-driven tenant screening

Key principle: Objective criteria only, fully auditable, no bias
"""

import json
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from google import genai
from google.genai import types
import structlog

from src.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class ScreeningDecision(str, Enum):
    """Possible screening outcomes."""
    APPROVE = "approve"
    REJECT = "reject"
    REVIEW = "human_review"  # AI uncertain, needs human


@dataclass
class RiskFactor:
    """A risk factor identified during screening."""
    factor: str
    severity: str  # low, medium, high
    explanation: str


@dataclass
class ScreeningResult:
    """Complete screening result with explanation."""
    decision: ScreeningDecision
    confidence: float  # 0-1
    score: float  # 0-100
    reasoning: str  # Human-readable explanation
    risk_factors: list[RiskFactor] = field(default_factory=list)
    positive_factors: list[str] = field(default_factory=list)
    income_to_rent_ratio: Optional[float] = None
    rental_history_years: Optional[float] = None


class ScreeningEngine:
    """
    AI-powered tenant screening.
    
    Analyzes:
    - Income documents (payslips, bank statements)
    - Identity documents (ID verification)
    - Rental history (references)
    - Employment verification
    
    Produces fair, explainable decisions.
    """
    
    SCREENING_PROMPT = """You are a fair, objective tenant screening AI for OSPF.

Your job is to assess rental applications based on OBJECTIVE CRITERIA ONLY.

ALLOWED FACTORS:
- Income to rent ratio (minimum 3:1 recommended)
- Verified employment status and stability
- Rental payment history from references
- Credit history (if provided)
- Identity verification status
- Completeness of application

PROHIBITED FACTORS (never consider):
- Name, ethnicity, nationality
- Age (except legal minimum)
- Family status or number of children
- Disability or health status
- Gender, religion, political views
- Suburb or address they're coming from
- Personal appearance

DECISION FRAMEWORK:
- APPROVE: Income ≥3x rent, positive rental history, verified identity
- REJECT: Income <2x rent, eviction history, fraud detected
- REVIEW: Borderline cases, incomplete info, complex situations

APPLICATION DATA:
{application_data}

Analyze this application and respond in JSON:
{{
    "decision": "approve|reject|human_review",
    "confidence": 0.0-1.0,
    "score": 0-100,
    "reasoning": "Clear explanation of the decision",
    "risk_factors": [
        {{"factor": "description", "severity": "low|medium|high", "explanation": "why this matters"}}
    ],
    "positive_factors": ["list of strengths"],
    "income_to_rent_ratio": number or null,
    "rental_history_years": number or null
}}

Be fair, be thorough, be explainable."""

    def __init__(self):
        """Initialize screening engine."""
        if settings.google_api_key:
            self.client = genai.Client(api_key=settings.google_api_key)
            # Use Pro model for important decisions
            self.model_name = settings.gemini_pro_model
        else:
            self.client = None
            self.model_name = None
            logger.warning("screening_engine_not_configured")

    async def screen_application(
        self,
        application_data: dict,
    ) -> ScreeningResult:
        """
        Screen a tenant application.
        
        Args:
            application_data: Dict containing:
                - monthly_income: float
                - rent_amount: float
                - employment_status: str
                - employment_duration_months: int
                - rental_history: list of {landlord, duration, payment_history}
                - identity_verified: bool
                - documents_complete: bool
                
        Returns:
            ScreeningResult with decision and explanation
        """
        if not self.client:
            return ScreeningResult(
                decision=ScreeningDecision.REVIEW,
                confidence=0.0,
                score=0,
                reasoning="AI screening unavailable. Manual review required.",
            )
        
        prompt = self.SCREENING_PROMPT.format(
            application_data=json.dumps(application_data, indent=2)
        )
        
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            
            # Parse JSON response
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            data = json.loads(text.strip())
            
            # Parse risk factors
            risk_factors = []
            for rf in data.get("risk_factors", []):
                risk_factors.append(RiskFactor(
                    factor=rf.get("factor", "Unknown"),
                    severity=rf.get("severity", "low"),
                    explanation=rf.get("explanation", ""),
                ))
            
            result = ScreeningResult(
                decision=ScreeningDecision(data.get("decision", "human_review")),
                confidence=float(data.get("confidence", 0.5)),
                score=float(data.get("score", 50)),
                reasoning=data.get("reasoning", "No reasoning provided"),
                risk_factors=risk_factors,
                positive_factors=data.get("positive_factors", []),
                income_to_rent_ratio=data.get("income_to_rent_ratio"),
                rental_history_years=data.get("rental_history_years"),
            )
            
            logger.info("application_screened",
                       decision=result.decision.value,
                       confidence=result.confidence,
                       score=result.score)
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error("screening_parse_error", error=str(e))
            return ScreeningResult(
                decision=ScreeningDecision.REVIEW,
                confidence=0.0,
                score=0,
                reasoning=f"AI screening failed to parse. Manual review required.",
            )
        except Exception as e:
            logger.error("screening_error", error=str(e))
            return ScreeningResult(
                decision=ScreeningDecision.REVIEW,
                confidence=0.0,
                score=0,
                reasoning=f"AI screening error. Manual review required.",
            )

    async def analyze_document(
        self,
        document_type: str,
        document_image: bytes,
    ) -> dict:
        """
        Analyze a document using Gemini Vision.
        
        Args:
            document_type: Type of document (id, payslip, bank_statement, lease)
            document_image: Image bytes
            
        Returns:
            Extracted data and verification status
        """
        if not self.client:
            return {"error": "AI not configured", "verified": False}
        
        prompts = {
            "id": """Analyze this ID document. Extract:
- Document type (license, passport, etc.)
- Full name
- Date of birth
- Document number
- Expiry date
- Is it valid/not expired?

Respond in JSON with these fields.""",
            
            "payslip": """Analyze this payslip. Extract:
- Employer name
- Employee name
- Pay period
- Gross pay
- Net pay
- Pay frequency (weekly, fortnightly, monthly)

Respond in JSON with these fields.""",
            
            "bank_statement": """Analyze this bank statement. Extract:
- Account holder name
- Bank name
- Statement period
- Closing balance
- Regular income deposits (list amounts and frequency)
- Any concerning patterns (overdrafts, bounced payments)

Respond in JSON with these fields.""",
        }
        
        prompt = prompts.get(document_type, "Analyze this document and extract key information. Respond in JSON.")
        
        try:
            parts = [
                types.Part.from_text(text=prompt),
                types.Part.from_bytes(data=document_image, mime_type="image/jpeg")
            ]
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
            data["verified"] = True
            data["document_type"] = document_type
            
            logger.info("document_analyzed", document_type=document_type)
            
            return data
            
        except Exception as e:
            logger.error("document_analysis_error", error=str(e))
            return {
                "error": str(e),
                "verified": False,
                "document_type": document_type,
            }
