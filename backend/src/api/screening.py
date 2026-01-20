"""
OSPF Demo - Screening API
Fair, explainable tenant screening
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from src.ai.screening import ScreeningEngine, ScreeningDecision

router = APIRouter()
screening_engine = ScreeningEngine()


class ApplicationData(BaseModel):
    """Tenant application data."""
    monthly_income: float
    rent_amount: float
    employment_status: str  # employed, self-employed, unemployed, retired
    employment_duration_months: int
    rental_history: Optional[list[dict]] = None  # [{landlord, duration_months, payment_history}]
    identity_verified: bool = False
    documents_complete: bool = False


class RiskFactorResponse(BaseModel):
    """Risk factor in screening result."""
    factor: str
    severity: str
    explanation: str


class ScreeningResponse(BaseModel):
    """Screening result."""
    decision: str  # approve, reject, human_review
    confidence: float
    score: float
    reasoning: str
    risk_factors: list[RiskFactorResponse]
    positive_factors: list[str]
    income_to_rent_ratio: Optional[float] = None
    rental_history_years: Optional[float] = None


@router.post("/analyze", response_model=ScreeningResponse)
async def screen_application(application: ApplicationData):
    """
    Screen a tenant application.
    
    Uses objective criteria only:
    - Income to rent ratio
    - Employment stability
    - Rental history
    - Document completeness
    
    Returns explainable decision with reasoning.
    """
    result = await screening_engine.screen_application(application.model_dump())
    
    return ScreeningResponse(
        decision=result.decision.value,
        confidence=result.confidence,
        score=result.score,
        reasoning=result.reasoning,
        risk_factors=[
            RiskFactorResponse(
                factor=rf.factor,
                severity=rf.severity,
                explanation=rf.explanation,
            )
            for rf in result.risk_factors
        ],
        positive_factors=result.positive_factors,
        income_to_rent_ratio=result.income_to_rent_ratio,
        rental_history_years=result.rental_history_years,
    )


class DocumentAnalysisResponse(BaseModel):
    """Document analysis result."""
    document_type: str
    verified: bool
    extracted_data: dict
    error: Optional[str] = None


@router.post("/document", response_model=DocumentAnalysisResponse)
async def analyze_document(
    document_type: str,  # id, payslip, bank_statement
    file: UploadFile = File(...),
):
    """
    Analyze a document using AI vision.
    
    Supports:
    - ID documents (license, passport)
    - Payslips
    - Bank statements
    
    Extracts key information and verifies authenticity.
    """
    content = await file.read()
    
    result = await screening_engine.analyze_document(
        document_type=document_type,
        document_image=content,
    )
    
    return DocumentAnalysisResponse(
        document_type=document_type,
        verified=result.get("verified", False),
        extracted_data=result,
        error=result.get("error"),
    )
