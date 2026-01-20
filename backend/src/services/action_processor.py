"""
Action Processor Service
Validates and executes simulation actions with proper balance checks
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4
import structlog

from src.database import async_session
from src.repositories.participant import ParticipantRepository
from src.repositories.property import PropertyStateRepository
from src.repositories.network import NetworkRepository

logger = structlog.get_logger()


@dataclass
class ActionResult:
    """Result of an action execution."""
    success: bool
    action_id: str
    action_type: str
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ActionProcessor:
    """Processes and validates simulation actions."""
    
    def __init__(self):
        self.action_handlers = {
            "buy_tokens": self._handle_buy_tokens,
            "sell_tokens": self._handle_sell_tokens,
            "pay_rent": self._handle_pay_rent,
            "collect_rent": self._handle_collect_rent,
            "vote": self._handle_vote,
            "request_service": self._handle_request_service,
            "complete_service": self._handle_complete_service,
        }
    
    async def process_action(
        self,
        participant_id: str,
        action_type: str,
        action_data: Dict[str, Any],
        network_month: int,
    ) -> ActionResult:
        """Process a single action with validation."""
        action_id = str(uuid4())
        
        handler = self.action_handlers.get(action_type)
        if not handler:
            return ActionResult(
                success=False,
                action_id=action_id,
                action_type=action_type,
                message=f"Unknown action type: {action_type}",
                error="INVALID_ACTION_TYPE",
            )
        
        try:
            result = await handler(participant_id, action_data, network_month)
            result.action_id = action_id
            return result
        except Exception as e:
            logger.error("action_processing_error",
                        action_type=action_type,
                        participant_id=participant_id,
                        error=str(e))
            return ActionResult(
                success=False,
                action_id=action_id,
                action_type=action_type,
                message=f"Action failed: {str(e)}",
                error="PROCESSING_ERROR",
            )
    
    async def process_batch(
        self,
        actions: List[Dict[str, Any]],
        network_month: int,
    ) -> List[ActionResult]:
        """Process a batch of actions (for tick processing)."""
        results = []
        for action in actions:
            result = await self.process_action(
                participant_id=action["participant_id"],
                action_type=action["action_type"],
                action_data=action.get("data", {}),
                network_month=network_month,
            )
            results.append(result)
        return results
    
    # =========================================================================
    # Token Trading
    # =========================================================================
    
    async def _handle_buy_tokens(
        self,
        participant_id: str,
        data: Dict[str, Any],
        network_month: int,
    ) -> ActionResult:
        """Buy tokens in a property."""
        property_id = data.get("property_id")
        token_amount = Decimal(str(data.get("token_amount", 0)))
        max_price = Decimal(str(data.get("max_price", "999999")))
        
        if not property_id or token_amount <= 0:
            return ActionResult(
                success=False,
                action_id="",
                action_type="buy_tokens",
                message="Invalid property or token amount",
                error="INVALID_PARAMS",
            )
        
        async with async_session() as session:
            participant_repo = ParticipantRepository(session)
            property_repo = PropertyStateRepository(session)
            
            # Get participant
            participant = await participant_repo.get_by_id(participant_id)
            if not participant:
                return ActionResult(
                    success=False,
                    action_id="",
                    action_type="buy_tokens",
                    message="Participant not found",
                    error="NOT_FOUND",
                )
            
            # Get property state
            property_state = await property_repo.get_by_id(property_id)
            if not property_state:
                return ActionResult(
                    success=False,
                    action_id="",
                    action_type="buy_tokens",
                    message="Property not found",
                    error="NOT_FOUND",
                )
            
            # Check token availability
            if property_state.tokens_available < token_amount:
                return ActionResult(
                    success=False,
                    action_id="",
                    action_type="buy_tokens",
                    message=f"Only {property_state.tokens_available} tokens available",
                    error="INSUFFICIENT_TOKENS",
                )
            
            # Check price
            current_price = property_state.token_price
            if current_price > max_price:
                return ActionResult(
                    success=False,
                    action_id="",
                    action_type="buy_tokens",
                    message=f"Price ${current_price} exceeds max ${max_price}",
                    error="PRICE_TOO_HIGH",
                )
            
            # Calculate cost
            total_cost = token_amount * current_price
            
            # Check balance
            if participant.balance < total_cost:
                return ActionResult(
                    success=False,
                    action_id="",
                    action_type="buy_tokens",
                    message=f"Insufficient balance: ${participant.balance} < ${total_cost}",
                    error="INSUFFICIENT_BALANCE",
                )
            
            # Execute trade
            # 1. Deduct from participant balance
            participant.balance -= total_cost
            participant.total_invested += total_cost
            
            # 2. Add holding
            await participant_repo.add_holding(
                participant_id=participant_id,
                property_id=property_id,
                token_amount=token_amount,
                purchase_price=current_price,
            )
            
            # 3. Update property state
            await property_repo.update_tokens(
                property_id=property_id,
                tokens_sold=token_amount,
            )
            
            await session.commit()
            
            logger.info("tokens_bought",
                       participant_id=participant_id,
                       property_id=property_id,
                       tokens=str(token_amount),
                       cost=str(total_cost))
            
            return ActionResult(
                success=True,
                action_id="",
                action_type="buy_tokens",
                message=f"Bought {token_amount} tokens for ${total_cost}",
                data={
                    "property_id": property_id,
                    "tokens": float(token_amount),
                    "price_per_token": float(current_price),
                    "total_cost": float(total_cost),
                    "new_balance": float(participant.balance),
                },
            )
    
    async def _handle_sell_tokens(
        self,
        participant_id: str,
        data: Dict[str, Any],
        network_month: int,
    ) -> ActionResult:
        """Sell tokens in a property."""
        property_id = data.get("property_id")
        token_amount = Decimal(str(data.get("token_amount", 0)))
        min_price = Decimal(str(data.get("min_price", "0")))
        
        if not property_id or token_amount <= 0:
            return ActionResult(
                success=False,
                action_id="",
                action_type="sell_tokens",
                message="Invalid property or token amount",
                error="INVALID_PARAMS",
            )
        
        async with async_session() as session:
            participant_repo = ParticipantRepository(session)
            property_repo = PropertyStateRepository(session)
            
            # Get participant and holdings
            participant = await participant_repo.get_by_id(participant_id)
            if not participant:
                return ActionResult(
                    success=False,
                    action_id="",
                    action_type="sell_tokens",
                    message="Participant not found",
                    error="NOT_FOUND",
                )
            
            holdings = await participant_repo.get_holdings(participant_id)
            holding = next((h for h in holdings if h.property_id == property_id), None)
            
            if not holding or holding.token_amount < token_amount:
                available = holding.token_amount if holding else 0
                return ActionResult(
                    success=False,
                    action_id="",
                    action_type="sell_tokens",
                    message=f"Insufficient tokens: have {available}, need {token_amount}",
                    error="INSUFFICIENT_TOKENS",
                )
            
            # Get property state for current price
            property_state = await property_repo.get_by_id(property_id)
            current_price = property_state.token_price if property_state else Decimal("1.00")
            
            # Check minimum price
            if current_price < min_price:
                return ActionResult(
                    success=False,
                    action_id="",
                    action_type="sell_tokens",
                    message=f"Price ${current_price} below minimum ${min_price}",
                    error="PRICE_TOO_LOW",
                )
            
            # Calculate proceeds
            total_proceeds = token_amount * current_price
            
            # Execute trade
            # 1. Remove from holding
            await participant_repo.remove_holding(
                participant_id=participant_id,
                property_id=property_id,
                token_amount=token_amount,
            )
            
            # 2. Add to balance
            participant.balance += total_proceeds
            
            # 3. Update property (tokens return to available)
            if property_state:
                property_state.tokens_available += token_amount
                property_state.network_ownership = (
                    (property_state.total_tokens - property_state.tokens_available) 
                    / property_state.total_tokens * 100
                )
            
            await session.commit()
            
            logger.info("tokens_sold",
                       participant_id=participant_id,
                       property_id=property_id,
                       tokens=str(token_amount),
                       proceeds=str(total_proceeds))
            
            return ActionResult(
                success=True,
                action_id="",
                action_type="sell_tokens",
                message=f"Sold {token_amount} tokens for ${total_proceeds}",
                data={
                    "property_id": property_id,
                    "tokens": float(token_amount),
                    "price_per_token": float(current_price),
                    "total_proceeds": float(total_proceeds),
                    "new_balance": float(participant.balance),
                },
            )
    
    # =========================================================================
    # Rent Processing
    # =========================================================================
    
    async def _handle_pay_rent(
        self,
        participant_id: str,
        data: Dict[str, Any],
        network_month: int,
    ) -> ActionResult:
        """Process rent payment from a tenant."""
        property_id = data.get("property_id")
        weeks = int(data.get("weeks", 1))
        
        async with async_session() as session:
            participant_repo = ParticipantRepository(session)
            property_repo = PropertyStateRepository(session)
            
            # Get participant (tenant)
            participant = await participant_repo.get_by_id(participant_id)
            if not participant:
                return ActionResult(
                    success=False,
                    action_id="",
                    action_type="pay_rent",
                    message="Participant not found",
                    error="NOT_FOUND",
                )
            
            # Get property
            property_state = await property_repo.get_by_id(property_id)
            if not property_state:
                return ActionResult(
                    success=False,
                    action_id="",
                    action_type="pay_rent",
                    message="Property not found",
                    error="NOT_FOUND",
                )
            
            # Check tenant is correct
            if property_state.tenant_id != participant_id:
                return ActionResult(
                    success=False,
                    action_id="",
                    action_type="pay_rent",
                    message="You are not the tenant of this property",
                    error="NOT_TENANT",
                )
            
            # Calculate rent
            total_rent = property_state.weekly_rent * weeks
            
            # Check balance
            if participant.balance < total_rent:
                return ActionResult(
                    success=False,
                    action_id="",
                    action_type="pay_rent",
                    message=f"Insufficient balance for rent: ${participant.balance} < ${total_rent}",
                    error="INSUFFICIENT_BALANCE",
                )
            
            # Process payment
            participant.balance -= total_rent
            await property_repo.record_rent(property_id, total_rent)
            
            await session.commit()
            
            logger.info("rent_paid",
                       participant_id=participant_id,
                       property_id=property_id,
                       weeks=weeks,
                       amount=str(total_rent))
            
            return ActionResult(
                success=True,
                action_id="",
                action_type="pay_rent",
                message=f"Paid ${total_rent} rent for {weeks} week(s)",
                data={
                    "property_id": property_id,
                    "weeks": weeks,
                    "weekly_rent": float(property_state.weekly_rent),
                    "total_paid": float(total_rent),
                    "new_balance": float(participant.balance),
                },
            )
    
    async def _handle_collect_rent(
        self,
        participant_id: str,
        data: Dict[str, Any],
        network_month: int,
    ) -> ActionResult:
        """Collect rent and distribute dividends to token holders."""
        property_id = data.get("property_id")
        
        async with async_session() as session:
            property_repo = PropertyStateRepository(session)
            network_repo = NetworkRepository(session)
            
            property_state = await property_repo.get_by_id(property_id)
            if not property_state:
                return ActionResult(
                    success=False,
                    action_id="",
                    action_type="collect_rent",
                    message="Property not found",
                    error="NOT_FOUND",
                )
            
            if property_state.status != "tenanted":
                return ActionResult(
                    success=False,
                    action_id="",
                    action_type="collect_rent",
                    message="Property is not tenanted",
                    error="NOT_TENANTED",
                )
            
            # Calculate monthly rent (4.33 weeks)
            monthly_rent = property_state.weekly_rent * Decimal("4.33")
            
            # Calculate dividend (after expenses - simplified 80% to holders)
            dividend_pool = monthly_rent * Decimal("0.80")
            
            # Record dividend payment
            await property_repo.record_dividend(property_id, dividend_pool)
            
            # Create event
            await network_repo.create_event(
                network_month=network_month,
                event_type="dividend",
                title=f"Dividend Payment - Property {property_id[:8]}",
                description=f"Distributed ${dividend_pool:.2f} to token holders",
                property_id=property_id,
                data={"amount": float(dividend_pool)},
            )
            
            await session.commit()
            
            return ActionResult(
                success=True,
                action_id="",
                action_type="collect_rent",
                message=f"Collected ${monthly_rent:.2f} rent, distributed ${dividend_pool:.2f} dividends",
                data={
                    "property_id": property_id,
                    "rent_collected": float(monthly_rent),
                    "dividends_distributed": float(dividend_pool),
                },
            )
    
    # =========================================================================
    # Governance
    # =========================================================================
    
    async def _handle_vote(
        self,
        participant_id: str,
        data: Dict[str, Any],
        network_month: int,
    ) -> ActionResult:
        """Cast a vote on a proposal."""
        proposal_id = data.get("proposal_id")
        vote_choice = data.get("vote")  # "for", "against", "abstain"
        
        if vote_choice not in ["for", "against", "abstain"]:
            return ActionResult(
                success=False,
                action_id="",
                action_type="vote",
                message="Invalid vote choice",
                error="INVALID_VOTE",
            )
        
        async with async_session() as session:
            participant_repo = ParticipantRepository(session)
            
            # Get participant to calculate voting power
            participant = await participant_repo.get_by_id(participant_id)
            if not participant:
                return ActionResult(
                    success=False,
                    action_id="",
                    action_type="vote",
                    message="Participant not found",
                    error="NOT_FOUND",
                )
            
            # Calculate voting power from holdings
            holdings = await participant_repo.get_holdings(participant_id)
            voting_power = sum(h.token_amount for h in holdings)
            
            if voting_power <= 0:
                return ActionResult(
                    success=False,
                    action_id="",
                    action_type="vote",
                    message="No voting power - you need token holdings to vote",
                    error="NO_VOTING_POWER",
                )
            
            # Queue action for batch processing (votes tallied at tick)
            await participant_repo.queue_action(
                participant_id=participant_id,
                action_type="vote",
                action_data={
                    "proposal_id": proposal_id,
                    "vote": vote_choice,
                    "voting_power": float(voting_power),
                },
                network_month=network_month,
            )
            
            await session.commit()
            
            return ActionResult(
                success=True,
                action_id="",
                action_type="vote",
                message=f"Vote '{vote_choice}' queued with {voting_power} voting power",
                data={
                    "proposal_id": proposal_id,
                    "vote": vote_choice,
                    "voting_power": float(voting_power),
                },
            )
    
    # =========================================================================
    # Service Requests
    # =========================================================================
    
    async def _handle_request_service(
        self,
        participant_id: str,
        data: Dict[str, Any],
        network_month: int,
    ) -> ActionResult:
        """Request a service (maintenance, etc.)."""
        property_id = data.get("property_id")
        service_type = data.get("service_type")
        description = data.get("description", "")
        
        async with async_session() as session:
            participant_repo = ParticipantRepository(session)
            network_repo = NetworkRepository(session)
            
            # Create service request event
            await network_repo.create_event(
                network_month=network_month,
                event_type="service_request",
                title=f"Service Request: {service_type}",
                description=description,
                participant_id=participant_id,
                property_id=property_id,
                data={
                    "service_type": service_type,
                    "status": "pending",
                },
            )
            
            await session.commit()
            
            return ActionResult(
                success=True,
                action_id="",
                action_type="request_service",
                message=f"Service request submitted: {service_type}",
                data={
                    "property_id": property_id,
                    "service_type": service_type,
                },
            )
    
    async def _handle_complete_service(
        self,
        participant_id: str,
        data: Dict[str, Any],
        network_month: int,
    ) -> ActionResult:
        """Complete a service job (for service providers)."""
        request_id = data.get("request_id")
        completion_notes = data.get("notes", "")
        amount = Decimal(str(data.get("amount", 0)))
        
        async with async_session() as session:
            participant_repo = ParticipantRepository(session)
            network_repo = NetworkRepository(session)
            
            # Get service provider
            participant = await participant_repo.get_by_id(participant_id)
            if not participant or participant.role != "service":
                return ActionResult(
                    success=False,
                    action_id="",
                    action_type="complete_service",
                    message="Only service providers can complete jobs",
                    error="NOT_SERVICE_PROVIDER",
                )
            
            # Pay service provider
            participant.balance += amount
            
            # Create completion event
            await network_repo.create_event(
                network_month=network_month,
                event_type="service_completed",
                title=f"Service Completed",
                description=completion_notes,
                participant_id=participant_id,
                data={
                    "request_id": request_id,
                    "amount_paid": float(amount),
                },
            )
            
            await session.commit()
            
            return ActionResult(
                success=True,
                action_id="",
                action_type="complete_service",
                message=f"Service completed, earned ${amount}",
                data={
                    "request_id": request_id,
                    "amount_earned": float(amount),
                    "new_balance": float(participant.balance),
                },
            )


# Singleton instance
_action_processor: Optional[ActionProcessor] = None


def get_action_processor() -> ActionProcessor:
    """Get the action processor singleton."""
    global _action_processor
    if _action_processor is None:
        _action_processor = ActionProcessor()
    return _action_processor
