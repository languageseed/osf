"""
OSF Simulation Mode - API Endpoints
Paper trading functionality for user engagement

⚠️ DEMO MODE WARNING ⚠️
This simulation mode is for demonstration purposes only.
- No authentication/authorization is enforced
- All data is ephemeral (in-memory storage)
- Not suitable for production use without security hardening
- user_id is passed as a parameter with no ownership verification
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from src.database import get_db

router = APIRouter(
    tags=["Simulation (Demo Mode)"],
    responses={
        200: {"description": "Success"},
        400: {"description": "Bad request - demo mode only, no real transactions"},
        404: {"description": "Resource not found"},
    }
)


# ============================================
# Pydantic Models
# ============================================

class SimSignupRequest(BaseModel):
    email: EmailStr
    display_name: Optional[str] = None


class SimSignupResponse(BaseModel):
    user_id: str
    email: str
    display_name: Optional[str]
    balance_aud: float
    message: str


class SimPortfolioResponse(BaseModel):
    user_id: str
    balance_aud: float
    portfolio_value: float
    total_value: float
    total_return: float
    total_return_percent: float
    holdings: list
    recent_transactions: list


class SimTradeRequest(BaseModel):
    property_id: str
    amount_aud: float


class SimTradeResponse(BaseModel):
    transaction_id: str
    tx_type: str
    property_id: str
    token_amount: float
    aud_amount: float
    token_price: float
    new_balance: float
    message: str


class SimLeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    display_name: Optional[str]
    portfolio_value: float
    total_return_percent: float
    total_trades: int


class SimProposalRequest(BaseModel):
    title: str
    description: str
    proposal_type: str = "feature"


class SimVoteRequest(BaseModel):
    vote: str  # for, against, abstain


# ============================================
# In-Memory Storage (Demo Mode)
# For hackathon - replace with DB in production
# ============================================

sim_users: dict = {}
sim_holdings: dict = {}  # user_id -> list of holdings
sim_transactions: dict = {}  # user_id -> list of transactions
sim_proposals: list = []

# Sample properties
SIM_PROPERTIES = [
    {
        "id": "prop-001",
        "address": "42 Harbour View Drive",
        "suburb": "Cottesloe",
        "state": "WA",
        "postcode": "6011",
        "property_type": "house",
        "bedrooms": 4,
        "bathrooms": 2,
        "valuation_aud": 1250000,
        "weekly_rent_aud": 850,
        "total_tokens": 1250000,
        "token_price": 1.00,
        "yield_percent": 3.5,
        "image": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400"
    },
    {
        "id": "prop-002",
        "address": "15 Beach Road",
        "suburb": "Scarborough",
        "state": "WA",
        "postcode": "6019",
        "property_type": "apartment",
        "bedrooms": 2,
        "bathrooms": 1,
        "valuation_aud": 550000,
        "weekly_rent_aud": 520,
        "total_tokens": 550000,
        "token_price": 1.00,
        "yield_percent": 4.9,
        "image": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400"
    },
    {
        "id": "prop-003",
        "address": "8 Park Lane",
        "suburb": "Subiaco",
        "state": "WA",
        "postcode": "6008",
        "property_type": "townhouse",
        "bedrooms": 3,
        "bathrooms": 2,
        "valuation_aud": 780000,
        "weekly_rent_aud": 650,
        "total_tokens": 780000,
        "token_price": 1.00,
        "yield_percent": 4.3,
        "image": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=400"
    },
    {
        "id": "prop-004",
        "address": "23 River Street",
        "suburb": "South Perth",
        "state": "WA",
        "postcode": "6151",
        "property_type": "apartment",
        "bedrooms": 3,
        "bathrooms": 2,
        "valuation_aud": 890000,
        "weekly_rent_aud": 720,
        "total_tokens": 890000,
        "token_price": 1.00,
        "yield_percent": 4.2,
        "image": "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=400"
    },
    {
        "id": "prop-005",
        "address": "156 Ocean Drive",
        "suburb": "City Beach",
        "state": "WA",
        "postcode": "6015",
        "property_type": "house",
        "bedrooms": 5,
        "bathrooms": 3,
        "valuation_aud": 2100000,
        "weekly_rent_aud": 1200,
        "total_tokens": 2100000,
        "token_price": 1.00,
        "yield_percent": 3.0,
        "image": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=400"
    },
]

# Initial proposals
sim_proposals = [
    {
        "id": "gov-001",
        "proposer_id": "system",
        "proposer_name": "OSF Team",
        "title": "Expand to Melbourne market",
        "description": "Allocate $500K from treasury to acquire 5 properties in Melbourne's eastern suburbs. Target suburbs: Hawthorn, Camberwell, and Kew.",
        "proposal_type": "expansion",
        "votes_for": 125000,
        "votes_against": 45000,
        "status": "active",
        "voting_ends_at": (datetime.utcnow() + timedelta(days=5)).isoformat(),
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "id": "gov-002",
        "proposer_id": "system",
        "proposer_name": "OSF Team",
        "title": "Reduce management fee to 0.4%",
        "description": "Lower the annual management fee from 0.5% to 0.4% to attract more investors and remain competitive with traditional REITs.",
        "proposal_type": "parameter",
        "votes_for": 89000,
        "votes_against": 76000,
        "status": "active",
        "voting_ends_at": (datetime.utcnow() + timedelta(days=3)).isoformat(),
        "created_at": datetime.utcnow().isoformat(),
    },
]


# ============================================
# Endpoints
# ============================================

@router.post("/signup", response_model=SimSignupResponse)
async def simulation_signup(request: SimSignupRequest):
    """Create a simulation account with $100K starting balance."""
    
    # Check if email already exists
    for user in sim_users.values():
        if user["email"] == request.email:
            return SimSignupResponse(
                user_id=user["id"],
                email=user["email"],
                display_name=user.get("display_name"),
                balance_aud=user["balance_aud"],
                message="Welcome back! Your simulation account is ready."
            )
    
    # Create new user
    user_id = str(uuid4())
    display_name = request.display_name or request.email.split("@")[0]
    
    sim_users[user_id] = {
        "id": user_id,
        "email": request.email,
        "display_name": display_name,
        "balance_aud": 100000.00,
        "total_trades": 0,
        "total_invested": 0,
        "created_at": datetime.utcnow().isoformat(),
        "last_active_at": datetime.utcnow().isoformat(),
    }
    
    sim_holdings[user_id] = []
    sim_transactions[user_id] = []
    
    return SimSignupResponse(
        user_id=user_id,
        email=request.email,
        display_name=display_name,
        balance_aud=100000.00,
        message="Welcome to OSF Simulation! You have $100,000 to invest."
    )


@router.get("/portfolio/{user_id}", response_model=SimPortfolioResponse)
async def get_portfolio(user_id: str):
    """Get user's simulation portfolio."""
    
    if user_id not in sim_users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = sim_users[user_id]
    holdings = sim_holdings.get(user_id, [])
    transactions = sim_transactions.get(user_id, [])
    
    # Calculate portfolio value
    portfolio_value = 0
    total_cost = 0
    holdings_with_details = []
    
    for holding in holdings:
        prop = next((p for p in SIM_PROPERTIES if p["id"] == holding["property_id"]), None)
        if prop:
            current_value = holding["token_amount"] * prop["token_price"]
            cost_basis = holding["token_amount"] * holding["avg_price"]
            portfolio_value += current_value
            total_cost += cost_basis
            
            holdings_with_details.append({
                "property_id": prop["id"],
                "address": prop["address"],
                "suburb": prop["suburb"],
                "token_amount": holding["token_amount"],
                "current_value": current_value,
                "cost_basis": cost_basis,
                "return_aud": current_value - cost_basis,
                "return_percent": ((current_value - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0,
                "yield_percent": prop["yield_percent"],
            })
    
    total_value = user["balance_aud"] + portfolio_value
    starting_balance = 100000
    total_return = total_value - starting_balance
    total_return_percent = (total_return / starting_balance) * 100
    
    # Recent transactions (last 10)
    recent_txs = sorted(transactions, key=lambda x: x["created_at"], reverse=True)[:10]
    
    return SimPortfolioResponse(
        user_id=user_id,
        balance_aud=user["balance_aud"],
        portfolio_value=portfolio_value,
        total_value=total_value,
        total_return=total_return,
        total_return_percent=total_return_percent,
        holdings=holdings_with_details,
        recent_transactions=recent_txs,
    )


@router.get("/properties")
async def list_properties():
    """List all available properties for investment."""
    return {
        "properties": SIM_PROPERTIES,
        "total": len(SIM_PROPERTIES),
    }


@router.post("/buy", response_model=SimTradeResponse)
async def buy_tokens(user_id: str, request: SimTradeRequest):
    """Buy tokens for a property."""
    
    if user_id not in sim_users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = sim_users[user_id]
    prop = next((p for p in SIM_PROPERTIES if p["id"] == request.property_id), None)
    
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    
    if request.amount_aud <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    if request.amount_aud > user["balance_aud"]:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Calculate tokens
    token_price = prop["token_price"]
    token_amount = request.amount_aud / token_price
    
    # Update balance
    user["balance_aud"] -= request.amount_aud
    user["total_trades"] += 1
    user["total_invested"] += request.amount_aud
    user["last_active_at"] = datetime.utcnow().isoformat()
    
    # Update or create holding
    holdings = sim_holdings[user_id]
    existing = next((h for h in holdings if h["property_id"] == request.property_id), None)
    
    if existing:
        # Update average price
        total_tokens = existing["token_amount"] + token_amount
        total_cost = (existing["token_amount"] * existing["avg_price"]) + request.amount_aud
        existing["avg_price"] = total_cost / total_tokens
        existing["token_amount"] = total_tokens
    else:
        holdings.append({
            "property_id": request.property_id,
            "token_amount": token_amount,
            "avg_price": token_price,
        })
    
    # Record transaction
    tx_id = str(uuid4())
    sim_transactions[user_id].append({
        "id": tx_id,
        "tx_type": "buy",
        "property_id": request.property_id,
        "property_address": prop["address"],
        "token_amount": token_amount,
        "aud_amount": request.amount_aud,
        "token_price": token_price,
        "created_at": datetime.utcnow().isoformat(),
    })
    
    return SimTradeResponse(
        transaction_id=tx_id,
        tx_type="buy",
        property_id=request.property_id,
        token_amount=token_amount,
        aud_amount=request.amount_aud,
        token_price=token_price,
        new_balance=user["balance_aud"],
        message=f"Successfully purchased {token_amount:,.2f} tokens of {prop['address']}"
    )


@router.post("/sell", response_model=SimTradeResponse)
async def sell_tokens(user_id: str, request: SimTradeRequest):
    """Sell tokens for a property."""
    
    if user_id not in sim_users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = sim_users[user_id]
    prop = next((p for p in SIM_PROPERTIES if p["id"] == request.property_id), None)
    
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Find holding
    holdings = sim_holdings[user_id]
    holding = next((h for h in holdings if h["property_id"] == request.property_id), None)
    
    if not holding:
        raise HTTPException(status_code=400, detail="You don't own any tokens for this property")
    
    # Calculate tokens to sell based on AUD amount
    token_price = prop["token_price"]
    tokens_to_sell = request.amount_aud / token_price
    
    if tokens_to_sell > holding["token_amount"]:
        raise HTTPException(status_code=400, detail="Insufficient tokens")
    
    # Update holding
    holding["token_amount"] -= tokens_to_sell
    if holding["token_amount"] <= 0:
        holdings.remove(holding)
    
    # Update balance
    user["balance_aud"] += request.amount_aud
    user["total_trades"] += 1
    user["last_active_at"] = datetime.utcnow().isoformat()
    
    # Record transaction
    tx_id = str(uuid4())
    sim_transactions[user_id].append({
        "id": tx_id,
        "tx_type": "sell",
        "property_id": request.property_id,
        "property_address": prop["address"],
        "token_amount": tokens_to_sell,
        "aud_amount": request.amount_aud,
        "token_price": token_price,
        "created_at": datetime.utcnow().isoformat(),
    })
    
    return SimTradeResponse(
        transaction_id=tx_id,
        tx_type="sell",
        property_id=request.property_id,
        token_amount=tokens_to_sell,
        aud_amount=request.amount_aud,
        token_price=token_price,
        new_balance=user["balance_aud"],
        message=f"Successfully sold {tokens_to_sell:,.2f} tokens of {prop['address']}"
    )


@router.post("/reset/{user_id}")
async def reset_account(user_id: str):
    """
    Reset simulation account to $100K.
    
    Rate limit: Once per 24 hours (enforced).
    
    ⚠️ Demo mode: No authentication - anyone with user_id can reset.
    """
    
    if user_id not in sim_users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = sim_users[user_id]
    
    # Enforce 24-hour cooldown
    last_reset = user.get("last_reset")
    if last_reset:
        last_reset_time = datetime.fromisoformat(last_reset) if isinstance(last_reset, str) else last_reset
        cooldown_remaining = (last_reset_time + timedelta(hours=24)) - datetime.utcnow()
        if cooldown_remaining.total_seconds() > 0:
            hours_remaining = int(cooldown_remaining.total_seconds() // 3600)
            minutes_remaining = int((cooldown_remaining.total_seconds() % 3600) // 60)
            raise HTTPException(
                status_code=429,
                detail=f"Reset cooldown active. Try again in {hours_remaining}h {minutes_remaining}m"
            )
    
    # Reset account
    user["balance_aud"] = 100000.00
    user["total_trades"] = 0
    user["total_invested"] = 0
    user["last_reset"] = datetime.utcnow().isoformat()
    sim_holdings[user_id] = []
    sim_transactions[user_id] = [{
        "id": str(uuid4()),
        "tx_type": "reset",
        "property_id": None,
        "property_address": None,
        "token_amount": 0,
        "aud_amount": 100000,
        "token_price": 0,
        "created_at": datetime.utcnow().isoformat(),
    }]
    
    return {
        "message": "Account reset to $100,000. Next reset available in 24 hours.",
        "balance_aud": 100000.00,
        "next_reset_available": (datetime.utcnow() + timedelta(hours=24)).isoformat()
    }


@router.get("/leaderboard")
async def get_leaderboard():
    """Get top performers leaderboard."""
    
    leaderboard = []
    
    for user_id, user in sim_users.items():
        # Calculate portfolio value
        portfolio_value = 0
        holdings = sim_holdings.get(user_id, [])
        
        for holding in holdings:
            prop = next((p for p in SIM_PROPERTIES if p["id"] == holding["property_id"]), None)
            if prop:
                portfolio_value += holding["token_amount"] * prop["token_price"]
        
        total_value = user["balance_aud"] + portfolio_value
        total_return = total_value - 100000
        total_return_percent = (total_return / 100000) * 100
        
        leaderboard.append({
            "user_id": user_id,
            "display_name": user.get("display_name", "Anonymous"),
            "portfolio_value": total_value,
            "total_return_percent": total_return_percent,
            "total_trades": user.get("total_trades", 0),
        })
    
    # Sort by return percent
    leaderboard.sort(key=lambda x: x["total_return_percent"], reverse=True)
    
    # Add ranks
    for i, entry in enumerate(leaderboard):
        entry["rank"] = i + 1
    
    return {
        "leaderboard": leaderboard[:50],  # Top 50
        "total_users": len(leaderboard),
        "updated_at": datetime.utcnow().isoformat(),
    }


@router.get("/proposals")
async def list_proposals():
    """List governance proposals."""
    return {
        "proposals": sim_proposals,
        "total": len(sim_proposals),
    }


@router.post("/proposals")
async def create_proposal(user_id: str, request: SimProposalRequest):
    """Create a new governance proposal."""
    
    if user_id not in sim_users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = sim_users[user_id]
    
    # Calculate voting power (total holdings)
    holdings = sim_holdings.get(user_id, [])
    total_tokens = sum(h["token_amount"] for h in holdings)
    
    if total_tokens < 10000:
        raise HTTPException(
            status_code=400, 
            detail="You need at least 10,000 tokens to create a proposal"
        )
    
    proposal_id = str(uuid4())
    proposal = {
        "id": proposal_id,
        "proposer_id": user_id,
        "proposer_name": user.get("display_name", "Anonymous"),
        "title": request.title,
        "description": request.description,
        "proposal_type": request.proposal_type,
        "votes_for": 0,
        "votes_against": 0,
        "status": "active",
        "voting_ends_at": (datetime.utcnow() + timedelta(days=5)).isoformat(),
        "created_at": datetime.utcnow().isoformat(),
    }
    
    sim_proposals.append(proposal)
    
    return {
        "proposal": proposal,
        "message": "Proposal created successfully",
    }


@router.post("/proposals/{proposal_id}/vote")
async def vote_on_proposal(proposal_id: str, user_id: str, request: SimVoteRequest):
    """Vote on a governance proposal."""
    
    if user_id not in sim_users:
        raise HTTPException(status_code=404, detail="User not found")
    
    proposal = next((p for p in sim_proposals if p["id"] == proposal_id), None)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    if proposal["status"] != "active":
        raise HTTPException(status_code=400, detail="Voting has ended")
    
    # Calculate voting power
    holdings = sim_holdings.get(user_id, [])
    voting_power = sum(h["token_amount"] for h in holdings)
    
    if voting_power <= 0:
        raise HTTPException(status_code=400, detail="You need tokens to vote")
    
    # Apply vote
    if request.vote == "for":
        proposal["votes_for"] += voting_power
    elif request.vote == "against":
        proposal["votes_against"] += voting_power
    
    return {
        "message": f"Vote recorded: {request.vote}",
        "voting_power": voting_power,
        "votes_for": proposal["votes_for"],
        "votes_against": proposal["votes_against"],
    }


# ============================================
# Community Feedback System
# ============================================

# In-memory storage for feedback
feedback_items: dict = {}  # feedback_id -> feedback
feedback_votes: dict = {}  # feedback_id -> {user_id: vote}
feedback_comments: dict = {}  # feedback_id -> list of comments

# Initialize with sample feedback
INITIAL_FEEDBACK = [
    {
        "id": "fb-001",
        "author_id": "system",
        "author_name": "OSF Team",
        "title": "Add dividend payout simulation",
        "description": "It would be great to see simulated quarterly dividends based on property yields. This would help users understand the passive income aspect of fractional property ownership.",
        "feedback_type": "enhancement",
        "ai_category": "trading",
        "ai_priority": "high",
        "ai_summary": "Request for quarterly dividend simulation to demonstrate passive income from property yields.",
        "status": "planned",
        "upvotes": 42,
        "downvotes": 3,
        "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
    },
    {
        "id": "fb-002",
        "author_id": "system",
        "author_name": "Demo User",
        "title": "Property detail page not loading images",
        "description": "When I click on a property to view details, the images don't load. I see broken image icons instead. Using Chrome on Windows 11.",
        "feedback_type": "bug",
        "ai_category": "ui",
        "ai_priority": "medium",
        "ai_summary": "Image loading issue on property detail pages in Chrome/Windows 11.",
        "status": "in_progress",
        "upvotes": 18,
        "downvotes": 0,
        "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
    },
    {
        "id": "fb-003",
        "author_id": "system",
        "author_name": "Investor123",
        "title": "Add price alerts for properties",
        "description": "Would love to set price alerts for specific properties so I know when to buy or sell based on my target prices.",
        "feedback_type": "enhancement",
        "ai_category": "trading",
        "ai_priority": "medium",
        "ai_summary": "Feature request for customizable price alerts on properties.",
        "status": "open",
        "upvotes": 31,
        "downvotes": 2,
        "created_at": (datetime.utcnow() - timedelta(days=3)).isoformat(),
    },
]

# Initialize feedback storage
for fb in INITIAL_FEEDBACK:
    feedback_items[fb["id"]] = fb
    feedback_votes[fb["id"]] = {}
    feedback_comments[fb["id"]] = []


class FeedbackCreateRequest(BaseModel):
    title: str
    description: str
    feedback_type: str  # bug, enhancement, question


class FeedbackCommentRequest(BaseModel):
    content: str
    parent_id: Optional[str] = None


class FeedbackVoteRequest(BaseModel):
    vote: int  # 1 for upvote, -1 for downvote


@router.get("/feedback")
async def list_feedback(
    feedback_type: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = "upvotes",  # upvotes, created_at, ai_priority
):
    """List all feedback items with optional filters."""
    
    items = list(feedback_items.values())
    
    # Filter by type
    if feedback_type:
        items = [f for f in items if f["feedback_type"] == feedback_type]
    
    # Filter by status
    if status:
        items = [f for f in items if f["status"] == status]
    
    # Sort
    if sort_by == "upvotes":
        items.sort(key=lambda x: x["upvotes"] - x["downvotes"], reverse=True)
    elif sort_by == "created_at":
        items.sort(key=lambda x: x["created_at"], reverse=True)
    elif sort_by == "ai_priority":
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, None: 4}
        items.sort(key=lambda x: priority_order.get(x.get("ai_priority"), 4))
    
    # Add comment counts
    for item in items:
        item["comment_count"] = len(feedback_comments.get(item["id"], []))
    
    return {
        "feedback": items,
        "total": len(items),
        "filters": {
            "types": ["bug", "enhancement", "question"],
            "statuses": ["open", "in_review", "planned", "in_progress", "resolved", "wont_fix"],
        }
    }


@router.get("/feedback/{feedback_id}")
async def get_feedback(feedback_id: str):
    """Get a single feedback item with comments."""
    
    if feedback_id not in feedback_items:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    item = feedback_items[feedback_id].copy()
    item["comments"] = feedback_comments.get(feedback_id, [])
    item["comment_count"] = len(item["comments"])
    
    return item


@router.post("/feedback")
async def create_feedback(user_id: str, request: FeedbackCreateRequest):
    """Submit new feedback (bug report or feature request)."""
    
    if user_id not in sim_users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = sim_users[user_id]
    
    feedback_id = f"fb-{str(uuid4())[:8]}"
    
    # AI Triage - simple categorization for demo
    # In production, this would call Gemini API
    ai_category = _triage_category(request.title, request.description)
    ai_priority = _triage_priority(request.feedback_type, request.description)
    ai_summary = _generate_summary(request.description)
    
    feedback = {
        "id": feedback_id,
        "author_id": user_id,
        "author_name": user.get("display_name", "Anonymous"),
        "title": request.title,
        "description": request.description,
        "feedback_type": request.feedback_type,
        "ai_category": ai_category,
        "ai_priority": ai_priority,
        "ai_summary": ai_summary,
        "ai_triaged_at": datetime.utcnow().isoformat(),
        "status": "open",
        "upvotes": 0,
        "downvotes": 0,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    
    feedback_items[feedback_id] = feedback
    feedback_votes[feedback_id] = {}
    feedback_comments[feedback_id] = []
    
    return {
        "feedback": feedback,
        "message": "Thank you for your feedback! Our AI has categorized it and the community can now vote and comment.",
    }


@router.post("/feedback/{feedback_id}/vote")
async def vote_feedback(feedback_id: str, user_id: str, request: FeedbackVoteRequest):
    """Vote on a feedback item (upvote/downvote)."""
    
    if user_id not in sim_users:
        raise HTTPException(status_code=404, detail="User not found")
    
    if feedback_id not in feedback_items:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    if request.vote not in [1, -1]:
        raise HTTPException(status_code=400, detail="Vote must be 1 (upvote) or -1 (downvote)")
    
    feedback = feedback_items[feedback_id]
    votes = feedback_votes[feedback_id]
    
    # Check if user already voted
    previous_vote = votes.get(user_id, 0)
    
    if previous_vote == request.vote:
        # Remove vote
        votes.pop(user_id, None)
        if request.vote == 1:
            feedback["upvotes"] -= 1
        else:
            feedback["downvotes"] -= 1
        new_vote = 0
    else:
        # Apply new vote
        if previous_vote == 1:
            feedback["upvotes"] -= 1
        elif previous_vote == -1:
            feedback["downvotes"] -= 1
        
        if request.vote == 1:
            feedback["upvotes"] += 1
        else:
            feedback["downvotes"] += 1
        
        votes[user_id] = request.vote
        new_vote = request.vote
    
    return {
        "feedback_id": feedback_id,
        "your_vote": new_vote,
        "upvotes": feedback["upvotes"],
        "downvotes": feedback["downvotes"],
        "score": feedback["upvotes"] - feedback["downvotes"],
    }


@router.post("/feedback/{feedback_id}/comment")
async def add_comment(feedback_id: str, user_id: str, request: FeedbackCommentRequest):
    """Add a comment to a feedback item."""
    
    if user_id not in sim_users:
        raise HTTPException(status_code=404, detail="User not found")
    
    if feedback_id not in feedback_items:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    user = sim_users[user_id]
    comments = feedback_comments[feedback_id]
    
    comment_id = f"cmt-{str(uuid4())[:8]}"
    
    comment = {
        "id": comment_id,
        "feedback_id": feedback_id,
        "author_id": user_id,
        "author_name": user.get("display_name", "Anonymous"),
        "content": request.content,
        "parent_id": request.parent_id,
        "is_official": False,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    comments.append(comment)
    
    return {
        "comment": comment,
        "message": "Comment added successfully",
    }


@router.get("/feedback/{feedback_id}/comments")
async def list_comments(feedback_id: str):
    """Get all comments for a feedback item."""
    
    if feedback_id not in feedback_items:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    comments = feedback_comments.get(feedback_id, [])
    
    return {
        "comments": comments,
        "total": len(comments),
    }


# ============================================
# AI Triage Helper Functions (Mock for Demo)
# ============================================

def _triage_category(title: str, description: str) -> str:
    """Simple keyword-based categorization for demo."""
    text = (title + " " + description).lower()
    
    if any(word in text for word in ["ui", "button", "page", "display", "screen", "image", "layout"]):
        return "ui"
    elif any(word in text for word in ["api", "endpoint", "request", "response", "server"]):
        return "api"
    elif any(word in text for word in ["trade", "buy", "sell", "token", "portfolio", "dividend"]):
        return "trading"
    elif any(word in text for word in ["vote", "proposal", "governance", "dao"]):
        return "governance"
    elif any(word in text for word in ["docs", "documentation", "help", "guide"]):
        return "docs"
    else:
        return "general"


def _triage_priority(feedback_type: str, description: str) -> str:
    """Simple priority assignment for demo."""
    text = description.lower()
    
    if feedback_type == "bug":
        if any(word in text for word in ["crash", "error", "broken", "not working", "urgent"]):
            return "critical"
        elif any(word in text for word in ["issue", "problem", "bug"]):
            return "high"
        else:
            return "medium"
    else:  # enhancement, question
        if any(word in text for word in ["important", "need", "must have", "critical"]):
            return "high"
        elif any(word in text for word in ["would be nice", "could", "maybe"]):
            return "low"
        else:
            return "medium"


def _generate_summary(description: str) -> str:
    """Generate a brief summary for demo."""
    # Just return first 150 chars for demo
    # In production, this would call Gemini API
    if len(description) <= 150:
        return description
    return description[:147] + "..."


# ============================================
# Database-Backed Actions (Persistent)
# ============================================
# These endpoints use the action processor and persist to database

class ActionRequest(BaseModel):
    """Generic action request."""
    participant_id: str
    action_type: str
    data: dict


class ActionResponse(BaseModel):
    """Action result response."""
    success: bool
    action_id: str
    action_type: str
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None


class BuyTokensRequest(BaseModel):
    """Buy tokens request."""
    participant_id: str
    property_id: str
    token_amount: float
    max_price: Optional[float] = 999999


class SellTokensRequest(BaseModel):
    """Sell tokens request."""
    participant_id: str
    property_id: str
    token_amount: float
    min_price: Optional[float] = 0


class PayRentRequest(BaseModel):
    """Pay rent request."""
    participant_id: str
    property_id: str
    weeks: int = 1


@router.post("/actions/execute", response_model=ActionResponse)
async def execute_action(request: ActionRequest):
    """Execute a simulation action with validation and persistence."""
    from src.services.action_processor import get_action_processor
    from src.services.network_clock import get_network_clock
    
    processor = get_action_processor()
    clock = get_network_clock()
    
    result = await processor.process_action(
        participant_id=request.participant_id,
        action_type=request.action_type,
        action_data=request.data,
        network_month=clock.current_month,
    )
    
    return ActionResponse(
        success=result.success,
        action_id=result.action_id,
        action_type=result.action_type,
        message=result.message,
        data=result.data,
        error=result.error,
    )


@router.post("/actions/buy-tokens", response_model=ActionResponse)
async def buy_tokens_action(request: BuyTokensRequest):
    """Buy tokens with balance validation and persistence."""
    from src.services.action_processor import get_action_processor
    from src.services.network_clock import get_network_clock
    
    processor = get_action_processor()
    clock = get_network_clock()
    
    result = await processor.process_action(
        participant_id=request.participant_id,
        action_type="buy_tokens",
        action_data={
            "property_id": request.property_id,
            "token_amount": request.token_amount,
            "max_price": request.max_price,
        },
        network_month=clock.current_month,
    )
    
    return ActionResponse(
        success=result.success,
        action_id=result.action_id,
        action_type=result.action_type,
        message=result.message,
        data=result.data,
        error=result.error,
    )


@router.post("/actions/sell-tokens", response_model=ActionResponse)
async def sell_tokens_action(request: SellTokensRequest):
    """Sell tokens with validation and persistence."""
    from src.services.action_processor import get_action_processor
    from src.services.network_clock import get_network_clock
    
    processor = get_action_processor()
    clock = get_network_clock()
    
    result = await processor.process_action(
        participant_id=request.participant_id,
        action_type="sell_tokens",
        action_data={
            "property_id": request.property_id,
            "token_amount": request.token_amount,
            "min_price": request.min_price,
        },
        network_month=clock.current_month,
    )
    
    return ActionResponse(
        success=result.success,
        action_id=result.action_id,
        action_type=result.action_type,
        message=result.message,
        data=result.data,
        error=result.error,
    )


@router.post("/actions/pay-rent", response_model=ActionResponse)
async def pay_rent_action(request: PayRentRequest):
    """Pay rent with validation and persistence."""
    from src.services.action_processor import get_action_processor
    from src.services.network_clock import get_network_clock
    
    processor = get_action_processor()
    clock = get_network_clock()
    
    result = await processor.process_action(
        participant_id=request.participant_id,
        action_type="pay_rent",
        action_data={
            "property_id": request.property_id,
            "weeks": request.weeks,
        },
        network_month=clock.current_month,
    )
    
    return ActionResponse(
        success=result.success,
        action_id=result.action_id,
        action_type=result.action_type,
        message=result.message,
        data=result.data,
        error=result.error,
    )
