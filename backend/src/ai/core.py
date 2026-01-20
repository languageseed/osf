"""
OSF - AI Core
Shared AI capabilities across all asset classes

This is the CORE innovation: One AI engine that adapts to any asset class
while sharing common capabilities like communication, document processing,
fraud detection, and reporting.
"""

import json
from datetime import datetime
from typing import Optional, AsyncIterator
from dataclasses import dataclass
from enum import Enum

from google import genai
from google.genai import types
import structlog

from src.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class AssetClass(str, Enum):
    """Supported asset classes in OSF."""
    PROPERTY = "property"
    ENERGY = "energy"
    # Future: ROYALTY, ART, VEHICLE, AGRI, BUSINESS


class ContextType(str, Enum):
    """Types of conversations/contexts."""
    GENERAL = "general"
    MAINTENANCE = "maintenance"
    MONITORING = "monitoring"
    FINANCIAL = "financial"
    EMERGENCY = "emergency"
    SUPPORT = "support"


@dataclass
class Message:
    """A message in a conversation."""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class TriageResult:
    """Result of AI triage for any asset class."""
    urgency: str  # emergency, urgent, routine, planned
    category: str  # asset-specific category
    diagnosis: str
    recommended_action: str
    requires_specialist: bool
    estimated_cost_low: Optional[float] = None
    estimated_cost_high: Optional[float] = None
    metadata: Optional[dict] = None


class OSFCore:
    """
    OSF AI Core - The shared intelligence layer.
    
    This core provides:
    - Communication (chat with users about any asset)
    - Document processing (analyze docs across asset types)
    - Triage (classify and route issues)
    - Fraud detection (identify suspicious patterns)
    - Reporting (generate insights)
    
    Asset-specific behavior is controlled by the asset_class parameter.
    """
    
    # Role-specific prompts that extend base prompts
    ROLE_PROMPTS = {
        "tenant": """You are speaking with a TENANT. They rent a network property.
Focus on:
- Answering rent and lease questions
- Helping with maintenance requests
- Explaining their rights and responsibilities
- Encouraging their path to investment/ownership

Be warm, supportive, and helpful. They may be stressed about housing issues.""",

        "homeowner": """You are speaking with a HOMEOWNER who has sold equity to the network.
Focus on:
- Explaining their equity position and valuation
- Discussing buyback options
- Helping with any property maintenance
- Reassuring them about their partnership with OSF

Be respectful of their emotional connection to their home.""",

        "investor": """You are speaking with an INVESTOR/TOKEN HOLDER.
Focus on:
- Portfolio performance and returns
- Governance and voting
- Market insights and strategy
- Fee structures and transparency

Be data-driven and transparent. They care about returns and governance.""",

        "custodian": """You are speaking with a CUSTODIAN (regional property manager).
Focus on:
- Helping resolve escalated issues
- Providing AI analysis and recommendations
- Discussing tenant/property situations
- Performance metrics and earnings

Be concise and professional. They're busy handling real issues.""",

        "energy_owner": """You are speaking with an ENERGY ASSET OWNER (solar/wind/battery).
Focus on:
- Production monitoring and performance
- Maintenance alerts and scheduling
- Revenue and carbon credit tracking
- System optimization recommendations

Be technical but accessible. Provide data and actionable insights.""",
    }
    
    # System prompts per asset class
    SYSTEM_PROMPTS = {
        AssetClass.PROPERTY: """You are OSF Property Manager, an AI assistant for the Open Source Fund - Property division.

You help tenants, homeowners, and investors with:
- Property maintenance and repairs
- Lease questions and renewals
- Rent payments and statements
- Property valuations and market insights
- Investment performance

PERSONALITY: Professional, warm, patient, solution-oriented

{role_context}

PROPERTY CONTEXT:
{context}

Respond helpfully and professionally. Escalate emergencies immediately.""",

        AssetClass.ENERGY: """You are OSF Energy Manager, an AI assistant for the Open Source Fund - Energy division.

You help asset owners, investors, and grid operators with:
- Solar/wind/battery performance monitoring
- Maintenance alerts and scheduling
- Energy production and revenue tracking
- Grid connection issues
- Carbon credit management
- System optimization

PERSONALITY: Technical but accessible, proactive, data-driven

{role_context}

ENERGY CONTEXT:
{context}

Respond helpfully with relevant metrics. Escalate safety issues immediately.""",
    }
    
    # Triage prompts per asset class
    TRIAGE_PROMPTS = {
        AssetClass.PROPERTY: """Analyze this property maintenance/issue report and classify it.

REPORT:
{description}

Respond in JSON format:
{{
    "urgency": "emergency|urgent|routine|planned",
    "category": "plumbing|electrical|hvac|structural|appliance|pest|cosmetic|security|other",
    "diagnosis": "Brief diagnosis of the likely issue",
    "recommended_action": "What should be done",
    "requires_specialist": true/false,
    "estimated_cost_low": number or null,
    "estimated_cost_high": number or null
}}

URGENCY GUIDE:
- emergency: Safety risk, no water/power, flooding, gas leak, security breach (4hr response)
- urgent: Major inconvenience, no hot water, broken AC in extreme weather (24hr response)
- routine: Normal repairs, minor issues (7 day response)
- planned: Preventive, upgrades, non-urgent (scheduled)""",

        AssetClass.ENERGY: """Analyze this energy asset issue report and classify it.

REPORT:
{description}

SYSTEM DATA (if available):
{system_data}

Respond in JSON format:
{{
    "urgency": "emergency|urgent|routine|planned",
    "category": "inverter|panel|battery|wiring|grid|meter|weather|performance|other",
    "diagnosis": "Brief diagnosis of the likely issue",
    "recommended_action": "What should be done",
    "requires_specialist": true/false,
    "estimated_cost_low": number or null,
    "estimated_cost_high": number or null,
    "estimated_production_loss_kwh": number or null,
    "safety_concern": true/false
}}

URGENCY GUIDE:
- emergency: Fire risk, DC arc fault, grid fault, physical damage (immediate)
- urgent: Inverter offline, significant production loss >50% (24hr response)
- routine: Minor performance degradation, cleaning needed (7 day response)
- planned: Panel replacement, upgrade, optimization (scheduled)""",
    }

    def __init__(self):
        """Initialize the OSF AI Core."""
        if settings.google_api_key:
            self.client = genai.Client(api_key=settings.google_api_key)
            self.model_name = settings.gemini_model
            self.pro_model_name = settings.gemini_pro_model
        else:
            self.client = None
            self.model_name = None
            self.pro_model_name = None
            logger.warning("osf_core_not_configured", 
                          message="GOOGLE_API_KEY not set, AI features disabled")

    async def chat(
        self,
        message: str,
        asset_class: AssetClass,
        conversation_history: list[Message] = None,
        context: dict = None,
        role: str = None,
    ) -> str:
        """
        Chat with user about their asset.
        
        Args:
            message: User's message
            asset_class: Which asset class context
            conversation_history: Previous messages
            context: Asset-specific context (property details, energy system data, etc.)
            role: User role (tenant, homeowner, investor, custodian, energy_owner)
            
        Returns:
            AI response
        """
        if not self.client:
            return "OSF AI is not configured. Please contact support."
        
        # Get role-specific context
        role_context = ""
        if role and role in self.ROLE_PROMPTS:
            role_context = self.ROLE_PROMPTS[role]
        
        # Get asset-specific system prompt
        context = context or {}
        system_prompt = self.SYSTEM_PROMPTS.get(
            asset_class, 
            self.SYSTEM_PROMPTS[AssetClass.PROPERTY]
        ).format(
            context=json.dumps(context, indent=2) if context else "No specific context",
            role_context=role_context
        )
        
        # Build conversation contents
        contents = []
        if conversation_history:
            for msg in conversation_history:
                contents.append(types.Content(
                    role="user" if msg.role == "user" else "model",
                    parts=[types.Part.from_text(text=msg.content)]
                ))
        
        # Add current user message (system prompt passed separately)
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=message)]
        ))
        
        try:
            # Use system_instruction parameter to properly isolate system prompt
            # This prevents prompt injection attacks where user messages could
            # override the system prompt behavior
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    max_output_tokens=2048,
                ),
            )
            
            result_text = response.text
            
            logger.info("osf_chat",
                       asset_class=asset_class.value,
                       message_length=len(message),
                       response_length=len(result_text))
            
            return result_text
            
        except Exception as e:
            logger.error("osf_chat_error", error=str(e), asset_class=asset_class.value)
            return "I apologize, but I'm having trouble processing your request. Please try again or contact support."

    async def chat_stream(
        self,
        message: str,
        asset_class: AssetClass,
        conversation_history: list[Message] = None,
        context: dict = None,
        role: str = None,
    ) -> AsyncIterator[str]:
        """Stream chat response for real-time display."""
        if not self.client:
            yield "OSF AI is not configured. Please contact support."
            return
        
        # Get role-specific context
        role_context = ""
        if role and role in self.ROLE_PROMPTS:
            role_context = self.ROLE_PROMPTS[role]
        
        context = context or {}
        system_prompt = self.SYSTEM_PROMPTS.get(
            asset_class,
            self.SYSTEM_PROMPTS[AssetClass.PROPERTY]
        ).format(
            context=json.dumps(context, indent=2) if context else "No specific context",
            role_context=role_context
        )
        
        contents = []
        if conversation_history:
            for msg in conversation_history:
                contents.append(types.Content(
                    role="user" if msg.role == "user" else "model",
                    parts=[types.Part.from_text(text=msg.content)]
                ))
        
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=message)]
        ))
        
        try:
            # Use system_instruction parameter to properly isolate system prompt
            # This prevents prompt injection attacks where user messages could
            # override the system prompt behavior
            async for chunk in self.client.aio.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    max_output_tokens=2048,
                ),
            ):
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error("osf_stream_error", error=str(e))
            yield "I apologize, but I'm having trouble processing your request."

    async def triage(
        self,
        description: str,
        asset_class: AssetClass,
        images: list[bytes] = None,
        system_data: dict = None,
    ) -> TriageResult:
        """
        Triage an issue/report for any asset class.
        
        Args:
            description: Text description of the issue
            asset_class: Which asset class
            images: Optional photos/screenshots
            system_data: Optional telemetry/monitoring data (for energy)
            
        Returns:
            TriageResult with classification and recommendations
        """
        if not self.client:
            return TriageResult(
                urgency="routine",
                category="other",
                diagnosis="AI triage unavailable",
                recommended_action="Please contact support",
                requires_specialist=True,
            )
        
        # Get asset-specific triage prompt
        prompt_template = self.TRIAGE_PROMPTS.get(
            asset_class,
            self.TRIAGE_PROMPTS[AssetClass.PROPERTY]
        )
        
        prompt = prompt_template.format(
            description=description,
            system_data=json.dumps(system_data, indent=2) if system_data else "No system data available"
        )
        
        try:
            # Build parts
            parts = [types.Part.from_text(text=prompt)]
            if images:
                for img in images:
                    parts.append(types.Part.from_bytes(data=img, mime_type="image/jpeg"))
            
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=parts,
            )
            
            # Parse JSON response
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            data = json.loads(text.strip())
            
            logger.info("osf_triage",
                       asset_class=asset_class.value,
                       urgency=data.get("urgency"),
                       category=data.get("category"))
            
            # Extract metadata (asset-specific fields)
            metadata = {}
            for key in ["estimated_production_loss_kwh", "safety_concern"]:
                if key in data:
                    metadata[key] = data[key]
            
            return TriageResult(
                urgency=data.get("urgency", "routine"),
                category=data.get("category", "other"),
                diagnosis=data.get("diagnosis", "Unable to diagnose"),
                recommended_action=data.get("recommended_action", "Contact support"),
                requires_specialist=data.get("requires_specialist", True),
                estimated_cost_low=data.get("estimated_cost_low"),
                estimated_cost_high=data.get("estimated_cost_high"),
                metadata=metadata if metadata else None,
            )
            
        except json.JSONDecodeError as e:
            logger.error("osf_triage_parse_error", error=str(e))
            return TriageResult(
                urgency="routine",
                category="other",
                diagnosis="AI triage failed to parse",
                recommended_action="Manual review required",
                requires_specialist=True,
            )
        except Exception as e:
            logger.error("osf_triage_error", error=str(e))
            return TriageResult(
                urgency="routine",
                category="other",
                diagnosis=f"AI triage error: {str(e)}",
                recommended_action="Contact support",
                requires_specialist=True,
            )

    async def detect_context(self, message: str, asset_class: AssetClass) -> ContextType:
        """Detect the context/intent of a message."""
        if not self.client:
            return ContextType.GENERAL
        
        context_options = {
            AssetClass.PROPERTY: "general, maintenance, financial, emergency, support",
            AssetClass.ENERGY: "general, monitoring, maintenance, financial, emergency, support",
        }
        
        prompt = f"""Classify this {asset_class.value} message into one of these categories:
{context_options.get(asset_class, context_options[AssetClass.PROPERTY])}

Message: {message}

Respond with just the category name, nothing else."""
        
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            category = response.text.strip().lower()
            
            if category in [c.value for c in ContextType]:
                return ContextType(category)
            return ContextType.GENERAL
            
        except Exception as e:
            logger.error("osf_context_detection_error", error=str(e))
            return ContextType.GENERAL

    async def analyze_document(
        self,
        document_type: str,
        document_image: bytes,
        asset_class: AssetClass,
    ) -> dict:
        """
        Analyze a document using Gemini Vision.
        Works across asset classes with asset-specific extraction.
        """
        if not self.client:
            return {"error": "AI not configured", "verified": False}
        
        # Asset-specific document prompts
        prompts = {
            # Property documents
            ("property", "lease"): "Analyze this lease document. Extract key terms, dates, rent amount, and conditions.",
            ("property", "id"): "Analyze this ID document. Extract name, DOB, document number, expiry.",
            ("property", "inspection"): "Analyze this property inspection report. Extract condition notes and issues.",
            
            # Energy documents
            ("energy", "installation"): "Analyze this solar/energy installation certificate. Extract system specs, installer, date, warranty.",
            ("energy", "performance"): "Analyze this energy performance report. Extract production data, efficiency metrics.",
            ("energy", "grid"): "Analyze this grid connection agreement. Extract capacity, tariffs, terms.",
        }
        
        key = (asset_class.value, document_type)
        prompt = prompts.get(key, f"Analyze this {document_type} document and extract key information. Respond in JSON.")
        prompt += "\n\nRespond in JSON format."
        
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
            data["asset_class"] = asset_class.value
            
            logger.info("osf_document_analyzed", 
                       document_type=document_type,
                       asset_class=asset_class.value)
            
            return data
            
        except Exception as e:
            logger.error("osf_document_analysis_error", error=str(e))
            return {
                "error": str(e),
                "verified": False,
                "document_type": document_type,
                "asset_class": asset_class.value,
            }
