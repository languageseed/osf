"""
OSPF Demo - AI Property Manager
Gemini-powered autonomous property management

This is the CORE hackathon demo - an AI that:
- Communicates with tenants 24/7
- Triages maintenance requests
- Answers lease questions
- Handles routine property management

Track: Marathon Agent - Autonomous tasks at scale
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


class ConversationContext(str, Enum):
    """Types of conversations the AI can handle."""
    GENERAL = "general"
    MAINTENANCE = "maintenance"
    LEASE = "lease"
    PAYMENT = "payment"
    APPLICATION = "application"
    EMERGENCY = "emergency"


@dataclass
class MaintenanceClassification:
    """AI classification of maintenance request."""
    urgency: str  # emergency, urgent, routine, planned
    category: str  # plumbing, electrical, hvac, structural, etc.
    diagnosis: str
    recommended_action: str
    requires_vendor: bool
    estimated_cost_range: Optional[tuple[float, float]] = None


@dataclass
class Message:
    """A message in a conversation."""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class PropertyManager:
    """
    AI Property Manager - Gemini-powered autonomous agent
    
    Handles:
    - Tenant communication (chat, queries, complaints)
    - Maintenance triage (classify, diagnose, route)
    - Lease questions (explain terms, renewals)
    - Payment inquiries (statements, disputes)
    - Emergency escalation
    """
    
    SYSTEM_PROMPT = """You are OSPF Property Manager, an AI assistant for the Open Source Property Fund.

Your role is to help tenants, homeowners, and property stakeholders with:
- Answering questions about their lease, property, or account
- Triaging maintenance requests (classify urgency, diagnose issues)
- Processing routine inquiries
- Escalating emergencies appropriately

PERSONALITY:
- Professional but warm
- Clear and concise
- Patient with frustrated tenants
- Proactive in offering solutions

GUIDELINES:
1. For maintenance: Always ask for photos/details to diagnose properly
2. For emergencies (gas leak, flood, fire, security): Immediately provide emergency contacts
3. For lease questions: Explain terms clearly, don't give legal advice
4. For payments: Be understanding, offer payment plan options if struggling
5. For complaints: Acknowledge, document, escalate if needed

ESCALATION TRIGGERS (flag for human review):
- Threats or abuse
- Legal disputes
- Claims exceeding $1000
- Discrimination allegations
- Health/safety emergencies

CONTEXT:
Property: {property_address}
Tenant: {tenant_name}
Lease Status: {lease_status}
Account Balance: {account_balance}

Respond helpfully and professionally. If you need to escalate, say so clearly."""

    def __init__(self):
        """Initialize the AI Property Manager."""
        if settings.google_api_key:
            self.client = genai.Client(api_key=settings.google_api_key)
            self.model_name = settings.gemini_model
            self.pro_model_name = settings.gemini_pro_model
        else:
            self.client = None
            self.model_name = None
            self.pro_model_name = None
            logger.warning("gemini_not_configured", 
                          message="GOOGLE_API_KEY not set, AI features disabled")

    async def chat(
        self,
        message: str,
        conversation_history: list[Message] = None,
        context: dict = None,
    ) -> str:
        """
        Chat with tenant/user about property matters.
        
        Args:
            message: User's message
            conversation_history: Previous messages in conversation
            context: Property/tenant context for personalization
            
        Returns:
            AI response
        """
        if not self.client:
            return "AI Property Manager is not configured. Please contact support."
        
        # Build context
        context = context or {}
        system_prompt = self.SYSTEM_PROMPT.format(
            property_address=context.get("property_address", "Not specified"),
            tenant_name=context.get("tenant_name", "Valued Tenant"),
            lease_status=context.get("lease_status", "Active"),
            account_balance=context.get("account_balance", "$0.00"),
        )
        
        # Build conversation contents
        contents = []
        if conversation_history:
            for msg in conversation_history:
                contents.append(types.Content(
                    role="user" if msg.role == "user" else "model",
                    parts=[types.Part.from_text(text=msg.content)]
                ))
        
        # Add current message with system prompt
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=f"{system_prompt}\n\nUser message: {message}")]
        ))
        
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
            )
            
            result_text = response.text
            
            logger.info("property_manager_chat",
                       message_length=len(message),
                       response_length=len(result_text))
            
            return result_text
            
        except Exception as e:
            logger.error("property_manager_chat_error", error=str(e))
            return "I apologize, but I'm having trouble processing your request. Please try again or contact support."

    async def chat_stream(
        self,
        message: str,
        conversation_history: list[Message] = None,
        context: dict = None,
    ) -> AsyncIterator[str]:
        """
        Stream chat response for better UX.
        
        Yields:
            Chunks of the AI response
        """
        if not self.client:
            yield "AI Property Manager is not configured. Please contact support."
            return
        
        context = context or {}
        system_prompt = self.SYSTEM_PROMPT.format(
            property_address=context.get("property_address", "Not specified"),
            tenant_name=context.get("tenant_name", "Valued Tenant"),
            lease_status=context.get("lease_status", "Active"),
            account_balance=context.get("account_balance", "$0.00"),
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
            parts=[types.Part.from_text(text=f"{system_prompt}\n\nUser message: {message}")]
        ))
        
        try:
            async for chunk in self.client.aio.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
            ):
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error("property_manager_stream_error", error=str(e))
            yield "I apologize, but I'm having trouble processing your request."

    async def triage_maintenance(
        self,
        description: str,
        images: list[bytes] = None,
    ) -> MaintenanceClassification:
        """
        Triage a maintenance request using AI.
        
        Classifies urgency, diagnoses issue, recommends action.
        
        Args:
            description: Text description of the issue
            images: Optional photos of the issue
            
        Returns:
            MaintenanceClassification with AI analysis
        """
        if not self.client:
            return MaintenanceClassification(
                urgency="routine",
                category="general",
                diagnosis="AI analysis unavailable",
                recommended_action="Please contact property management",
                requires_vendor=True,
            )
        
        prompt = f"""Analyze this maintenance request and classify it.

MAINTENANCE REQUEST:
{description}

Respond in JSON format:
{{
    "urgency": "emergency|urgent|routine|planned",
    "category": "plumbing|electrical|hvac|structural|appliance|pest|cosmetic|security|other",
    "diagnosis": "Brief diagnosis of the likely issue",
    "recommended_action": "What should be done",
    "requires_vendor": true/false,
    "estimated_cost_low": number or null,
    "estimated_cost_high": number or null
}}

URGENCY GUIDE:
- emergency: Safety risk, no water/power, flooding, gas leak, security breach (4hr response)
- urgent: Major inconvenience, no hot water, broken AC in extreme weather (24hr response)
- routine: Normal repairs, minor issues (7 day response)
- planned: Preventive, upgrades, non-urgent (scheduled)
"""
        
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
            # Extract JSON from markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            data = json.loads(text.strip())
            
            logger.info("maintenance_triaged",
                       urgency=data.get("urgency"),
                       category=data.get("category"))
            
            return MaintenanceClassification(
                urgency=data.get("urgency", "routine"),
                category=data.get("category", "other"),
                diagnosis=data.get("diagnosis", "Unable to diagnose"),
                recommended_action=data.get("recommended_action", "Contact property management"),
                requires_vendor=data.get("requires_vendor", True),
                estimated_cost_range=(
                    data.get("estimated_cost_low"),
                    data.get("estimated_cost_high")
                ) if data.get("estimated_cost_low") else None,
            )
            
        except json.JSONDecodeError as e:
            logger.error("maintenance_triage_parse_error", error=str(e))
            return MaintenanceClassification(
                urgency="routine",
                category="other",
                diagnosis="AI analysis failed to parse",
                recommended_action="Manual review required",
                requires_vendor=True,
            )
        except Exception as e:
            logger.error("maintenance_triage_error", error=str(e))
            return MaintenanceClassification(
                urgency="routine",
                category="other",
                diagnosis=f"AI analysis error: {str(e)}",
                recommended_action="Contact property management",
                requires_vendor=True,
            )

    async def detect_context(self, message: str) -> ConversationContext:
        """
        Detect the context/intent of a message.
        
        Used to route to appropriate handler and set conversation context.
        """
        if not self.client:
            return ConversationContext.GENERAL
        
        prompt = f"""Classify this tenant message into one of these categories:
- general: General inquiry, greetings, other
- maintenance: Repair request, something broken, issue with property
- lease: Questions about lease, renewal, terms, moving out
- payment: Rent payment, balance, statement, financial
- application: New application, screening, references
- emergency: Gas leak, flood, fire, security, immediate danger

Message: {message}

Respond with just the category name, nothing else."""
        
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            category = response.text.strip().lower()
            
            if category in [c.value for c in ConversationContext]:
                return ConversationContext(category)
            return ConversationContext.GENERAL
            
        except Exception as e:
            logger.error("context_detection_error", error=str(e))
            return ConversationContext.GENERAL
