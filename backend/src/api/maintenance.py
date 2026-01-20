"""
OSPF Demo - Maintenance API
AI-powered maintenance triage
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel

from src.ai.property_manager import PropertyManager

router = APIRouter()
property_manager = PropertyManager()


class MaintenanceRequest(BaseModel):
    """Maintenance request payload."""
    description: str
    property_id: Optional[str] = None
    tenant_id: Optional[str] = None


class MaintenanceResponse(BaseModel):
    """Maintenance triage response."""
    urgency: str
    category: str
    diagnosis: str
    recommended_action: str
    requires_vendor: bool
    estimated_cost_low: Optional[float] = None
    estimated_cost_high: Optional[float] = None


@router.post("", response_model=MaintenanceResponse)
async def create_maintenance_request(request: MaintenanceRequest):
    """
    Submit a maintenance request for AI triage.
    
    The AI will:
    1. Classify urgency (emergency, urgent, routine, planned)
    2. Categorize the issue (plumbing, electrical, etc.)
    3. Provide diagnosis and recommended action
    4. Estimate cost range
    """
    result = await property_manager.triage_maintenance(
        description=request.description,
    )
    
    return MaintenanceResponse(
        urgency=result.urgency,
        category=result.category,
        diagnosis=result.diagnosis,
        recommended_action=result.recommended_action,
        requires_vendor=result.requires_vendor,
        estimated_cost_low=result.estimated_cost_range[0] if result.estimated_cost_range else None,
        estimated_cost_high=result.estimated_cost_range[1] if result.estimated_cost_range else None,
    )


@router.post("/with-images", response_model=MaintenanceResponse)
async def create_maintenance_with_images(
    description: str = Form(...),
    images: list[UploadFile] = File(default=[]),
):
    """
    Submit a maintenance request with photos.
    
    Photos help the AI diagnose the issue more accurately.
    """
    # Read image bytes
    image_bytes = []
    for image in images[:5]:  # Limit to 5 images
        content = await image.read()
        image_bytes.append(content)
    
    result = await property_manager.triage_maintenance(
        description=description,
        images=image_bytes if image_bytes else None,
    )
    
    return MaintenanceResponse(
        urgency=result.urgency,
        category=result.category,
        diagnosis=result.diagnosis,
        recommended_action=result.recommended_action,
        requires_vendor=result.requires_vendor,
        estimated_cost_low=result.estimated_cost_range[0] if result.estimated_cost_range else None,
        estimated_cost_high=result.estimated_cost_range[1] if result.estimated_cost_range else None,
    )
