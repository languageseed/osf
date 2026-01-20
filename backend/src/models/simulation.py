"""
OSF Simulation Mode - Database Models
Paper trading functionality for user engagement
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from sqlalchemy import String, Numeric, DateTime, ForeignKey, Integer, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class SimUser(Base):
    """Simulation user account - email-only signup."""
    __tablename__ = "sim_users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Simulation balance
    balance_aud: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("100000.00"))
    
    # Stats
    total_trades: Mapped[int] = mapped_column(Integer, default=0)
    total_invested: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_active_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    holdings: Mapped[list["SimHolding"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    transactions: Mapped[list["SimTransaction"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    votes: Mapped[list["SimVote"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class SimProperty(Base):
    """Simulated property in the network."""
    __tablename__ = "sim_properties"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Address
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    suburb: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(20), nullable=False)
    postcode: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # Property details
    property_type: Mapped[str] = mapped_column(String(50), default="house")
    bedrooms: Mapped[int] = mapped_column(Integer, default=3)
    bathrooms: Mapped[int] = mapped_column(Integer, default=2)
    
    # Valuation
    valuation_aud: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    weekly_rent_aud: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Token economics
    total_tokens: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    token_price: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=Decimal("1.0000"))
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    holdings: Mapped[list["SimHolding"]] = relationship(back_populates="property")


class SimHolding(Base):
    """User's token holdings for a property."""
    __tablename__ = "sim_holdings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("sim_users.id"), nullable=False)
    property_id: Mapped[str] = mapped_column(ForeignKey("sim_properties.id"), nullable=False)
    
    token_amount: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    avg_purchase_price: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["SimUser"] = relationship(back_populates="holdings")
    property: Mapped["SimProperty"] = relationship(back_populates="holdings")


class SimTransaction(Base):
    """Simulation transaction record."""
    __tablename__ = "sim_transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("sim_users.id"), nullable=False)
    property_id: Mapped[Optional[str]] = mapped_column(ForeignKey("sim_properties.id"))
    
    tx_type: Mapped[str] = mapped_column(String(20), nullable=False)  # buy, sell, dividend, reset
    token_amount: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    aud_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    token_price: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["SimUser"] = relationship(back_populates="transactions")


class SimProposal(Base):
    """Simulation governance proposal."""
    __tablename__ = "sim_proposals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    proposer_id: Mapped[str] = mapped_column(ForeignKey("sim_users.id"), nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    proposal_type: Mapped[str] = mapped_column(String(50), default="feature")  # feature, parameter, other
    
    votes_for: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=Decimal("0"))
    votes_against: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=Decimal("0"))
    
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, passed, rejected, executed
    voting_ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    votes: Mapped[list["SimVote"]] = relationship(back_populates="proposal", cascade="all, delete-orphan")


class SimVote(Base):
    """User vote on a proposal."""
    __tablename__ = "sim_votes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("sim_users.id"), nullable=False)
    proposal_id: Mapped[str] = mapped_column(ForeignKey("sim_proposals.id"), nullable=False)
    
    vote: Mapped[str] = mapped_column(String(10), nullable=False)  # for, against, abstain
    voting_power: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["SimUser"] = relationship(back_populates="votes")
    proposal: Mapped["SimProposal"] = relationship(back_populates="votes")


class SimAchievement(Base):
    """User achievements."""
    __tablename__ = "sim_achievements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("sim_users.id"), nullable=False)
    
    achievement_type: Mapped[str] = mapped_column(String(50), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ============================================
# Community Feedback System
# ============================================

class FeedbackItem(Base):
    """Community feedback - bugs and feature requests."""
    __tablename__ = "feedback_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    author_id: Mapped[str] = mapped_column(ForeignKey("sim_users.id"), nullable=False)
    
    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    feedback_type: Mapped[str] = mapped_column(String(20), nullable=False)  # bug, enhancement, question
    
    # AI Triage (populated by AI, preserves user content)
    ai_category: Mapped[Optional[str]] = mapped_column(String(50))  # ui, api, trading, governance, docs, etc.
    ai_priority: Mapped[Optional[str]] = mapped_column(String(20))  # critical, high, medium, low
    ai_summary: Mapped[Optional[str]] = mapped_column(Text)  # AI-generated summary
    ai_similar_items: Mapped[Optional[str]] = mapped_column(Text)  # JSON array of similar item IDs
    ai_triaged_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Status (managed by maintainers/AI)
    status: Mapped[str] = mapped_column(String(20), default="open")  # open, in_review, planned, in_progress, resolved, wont_fix
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Voting
    upvotes: Mapped[int] = mapped_column(Integer, default=0)
    downvotes: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    votes: Mapped[list["FeedbackVote"]] = relationship(back_populates="feedback_item", cascade="all, delete-orphan")
    comments: Mapped[list["FeedbackComment"]] = relationship(back_populates="feedback_item", cascade="all, delete-orphan")


class FeedbackVote(Base):
    """User vote on a feedback item."""
    __tablename__ = "feedback_votes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("sim_users.id"), nullable=False)
    feedback_id: Mapped[str] = mapped_column(ForeignKey("feedback_items.id"), nullable=False)
    
    vote: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 for upvote, -1 for downvote
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    feedback_item: Mapped["FeedbackItem"] = relationship(back_populates="votes")


class FeedbackComment(Base):
    """Comment on a feedback item."""
    __tablename__ = "feedback_comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    feedback_id: Mapped[str] = mapped_column(ForeignKey("feedback_items.id"), nullable=False)
    author_id: Mapped[str] = mapped_column(ForeignKey("sim_users.id"), nullable=False)
    parent_id: Mapped[Optional[str]] = mapped_column(ForeignKey("feedback_comments.id"))  # For threaded replies
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_official: Mapped[bool] = mapped_column(Boolean, default=False)  # Official team response
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    feedback_item: Mapped["FeedbackItem"] = relationship(back_populates="comments")
    replies: Mapped[list["FeedbackComment"]] = relationship(back_populates="parent", remote_side=[id])
    parent: Mapped[Optional["FeedbackComment"]] = relationship(back_populates="replies", remote_side=[parent_id])
