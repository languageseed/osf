# OSF Network Simulation - Technical Specification

> **Status:** Active Development  
> **Last Updated:** 2026-01-20  
> **Target:** Gemini 3 Hackathon (Deadline: Feb 9, 2026)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Implemented Features](#implemented-features)
4. [Core Systems](#core-systems)
5. [API Reference](#api-reference)
6. [Data Models](#data-models)
7. [Implementation Plan](#implementation-plan)
8. [Future Features](#future-features)
9. [Technical Decisions](#technical-decisions)

---

## Executive Summary

### What is OSF?

The **Open Source Fund (OSF)** is a property tokenization simulation that demonstrates how AI can manage transparent, community-governed investment networks. Users can:

- **Invest** in tokenized property shares
- **Rent** properties within the network
- **Provide services** as custodians/contractors
- **Govern** the network through proposals and voting
- **Learn** about property investment through AI guidance

### Hackathon Strategy

This project targets the **Marathon Agent** track by:

1. **Long-running autonomous simulation** - 10-year (120 month) autonomous simulation
2. **Massive context utilization** - Monthly batch processing uses 1M+ tokens
3. **Multi-agent coordination** - 11 NPCs with unique personalities, Governor, Advisor agents
4. **Real-time + batch hybrid** - Interactive chat between batch ticks
5. **Self-healing network** - Autonomous detection and recovery from market stress
6. **Visible AI reasoning** - AI Thinking Log shows all NPC decisions with "thought signatures"
7. **Self-correction** - NPCs adjust strategy based on performance tracking

### Key Innovation

**Two-Phase Processing Model:**
- **Phase 1 (Interactive):** Real-time chat with Governor/Advisor AI (small context)
- **Phase 2 (Batch):** Monthly tick processes ALL events in single Gemini call (large context)

This optimizes token usage while maintaining responsiveness.

---

## Architecture Overview

### System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACES                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Investor   │  │    Renter    │  │   Service    │  │  Foundation  │     │
│  │   Dashboard  │  │   Portal     │  │   Provider   │  │   Partner    │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │                 │              │
│         └─────────────────┴────────┬────────┴─────────────────┘              │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         FRONTEND (SvelteKit)                         │    │
│  │  • NetworkClock component (SSE sync)                                │    │
│  │  • GovernorChat component (streaming)                               │    │
│  │  • Role-based UI panels                                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                              REST + SSE                                      │
│                                    │                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                              BACKEND (FastAPI)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                          API LAYER                                   │    │
│  │  • /api/v1/network/clock/* - Clock control & SSE                    │    │
│  │  • /api/v1/network/* - State, Governor, Advisor                     │    │
│  │  • /api/v1/sim/* - Simulation actions                               │    │
│  │  • /api/v1/chat/* - General AI chat                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        SERVICE LAYER                                 │    │
│  │                                                                      │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │    │
│  │  │  NetworkClock   │  │ BatchProcessor  │  │   AI Core       │      │    │
│  │  │                 │  │                 │  │                 │      │    │
│  │  │ • Timer loop    │  │ • State collect │  │ • Chat          │      │    │
│  │  │ • SSE broadcast │──│ • Gemini call   │  │ • Triage        │      │    │
│  │  │ • Action queue  │  │ • Parse result  │  │ • Screening     │      │    │
│  │  │ • Presets       │  │ • Update state  │  │                 │      │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘      │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        STATE LAYER                                   │    │
│  │                                                                      │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │    │
│  │  │  NetworkState   │  │  Participants   │  │   Properties    │      │    │
│  │  │  (in-memory)    │  │  (humans+NPCs)  │  │   (tokenized)   │      │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘      │    │
│  │                                                                      │    │
│  │  [ ] TODO: Persist to database (PostgreSQL/SQLite)                  │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                              GEMINI API                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ gemini-2.0-flash│  │  imagen-3       │  │   Future        │             │
│  │                 │  │                 │  │                 │             │
│  │ Batch + Chat    │  │ Property images │  │ gemini-3 when   │             │
│  │ Streaming SSE   │  │ Character avatar│  │ available       │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Agent Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AGENT LAYERS                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  LAYER 0: ORCHESTRATION                                                      │
│  ───────────────────────                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      BATCH PROCESSOR                                 │    │
│  │  • Runs on clock tick                                               │    │
│  │  • Processes entire month in one Gemini Pro call                    │    │
│  │  • Coordinates all agent decisions                                   │    │
│  │  • Resolves conflicts                                                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  LAYER 1: PROTOCOL AGENTS (Interactive)                                      │
│  ──────────────────────────────────────                                      │
│  ┌──────────────────────────┐  ┌──────────────────────────┐                 │
│  │     NETWORK GOVERNOR     │  │    PORTFOLIO ADVISOR     │                 │
│  │                          │  │                          │                 │
│  │  • Answers questions     │  │  • Analyzes portfolios   │                 │
│  │  • Explains network      │  │  • Suggests investments  │                 │
│  │  • Educational guidance  │  │  • Risk assessment       │                 │
│  │  • Uses: gemini-flash    │  │  • Uses: gemini-flash    │                 │
│  └──────────────────────────┘  └──────────────────────────┘                 │
│                                                                              │
│  LAYER 2: SIMULATION ACTORS (NPCs - Batch processed)                         │
│  ───────────────────────────────────────────────────                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │  Investor  │  │   Renter   │  │  Service   │  │   Market   │             │
│  │   NPCs     │  │   NPCs     │  │  Provider  │  │   Maker    │             │
│  │            │  │            │  │   NPCs     │  │            │             │
│  │ Buy/sell   │  │ Pay rent   │  │ Complete   │  │ Provide    │             │
│  │ decisions  │  │ Requests   │  │ jobs       │  │ liquidity  │             │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘             │
│                                                                              │
│  LAYER 3: FUTURE - SPECIALIZED WORKERS                                       │
│  ────────────────────────────────────                                        │
│  [ ] Property Valuation Agent                                                │
│  [ ] Market Analysis Agent                                                   │
│  [ ] Compliance Agent                                                        │
│  [ ] Dispute Resolution Agent                                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implemented Features

### Core Infrastructure

| Feature | Status | Location |
|---------|--------|----------|
| FastAPI Backend | ✅ Done | `/backend/src/main.py` |
| SvelteKit Frontend | ✅ Done | `/frontend/` |
| Gemini Integration | ✅ Done | `/backend/src/ai/core.py` |
| Authentication (JWT) | ✅ Done | `/backend/src/auth.py` |
| Configuration | ✅ Done | `/backend/src/config.py` |

### Network Clock System

| Feature | Status | Location |
|---------|--------|----------|
| Timer loop with presets | ✅ Done | `/backend/src/services/network_clock.py` |
| SSE broadcasting | ✅ Done | `/backend/src/api/clock.py` |
| Action queue | ✅ Done | `NetworkClock.queue_action()` |
| Frontend sync component | ✅ Done | `/frontend/.../NetworkClock.svelte` |
| Manual/Sync mode toggle | ✅ Done | `/frontend/.../simulate/+page.svelte` |

### Batch Processing

| Feature | Status | Location |
|---------|--------|----------|
| State collection | ✅ Done | `NetworkState` dataclass |
| Pre-computed financials | ✅ Done | `PreComputedResults` dataclass |
| Gemini batch call | ✅ Done | `BatchProcessor.process_month()` |
| Response parsing | ✅ Done | `_parse_response()` |
| Mock mode | ✅ Done | `_mock_process()` |

### Interactive Agents

| Feature | Status | Location |
|---------|--------|----------|
| Governor Chat | ✅ Done | `/backend/src/api/network.py` |
| Governor Streaming | ✅ Done | `/governor/chat/stream` |
| Portfolio Advisor | ✅ Done | `/advisor/portfolio` |
| Frontend Chat UI | ✅ Done | `/frontend/.../GovernorChat.svelte` |

### Simulation Features

| Feature | Status | Notes |
|---------|--------|-------|
| Role switching | ✅ Done | Investor, Renter, Service, Foundation |
| Property browsing | ✅ Done | With yields and valuations |
| Token trading (UI) | ✅ Done | Frontend only |
| Rent payment (UI) | ✅ Done | Frontend only |
| Governance voting (UI) | ✅ Done | Frontend only |
| NPC participants | ✅ Done | Demo data with personalities |

---

## Core Systems

### 1. Network Clock

**Purpose:** Synchronize simulation time across all connected users.

**Configuration:**
```python
class ClockPreset(Enum):
    TEST = "test"           # 30 seconds
    DEMO = "demo"           # 5 minutes
    CASUAL = "casual"       # 15 minutes
    STANDARD = "standard"   # 30 minutes
    REALTIME = "realtime"   # 1 hour
    PAUSED = "paused"       # Manual only
```

**Flow:**
```
Timer Loop (async)
      │
      ▼
Check elapsed time > interval
      │
      ├─ NO ──► Sleep, continue
      │
      └─ YES ─► Broadcast "tick_warning" (30s before)
                      │
                      ▼
                Wait 30 seconds
                      │
                      ▼
                Set is_processing = True
                      │
                      ▼
                Call on_tick handler with pending actions
                      │
                      ▼
                Broadcast "month_completed" with results
                      │
                      ▼
                Clear pending actions
                      │
                      ▼
                Increment month, reset timer
```

### 2. Batch Processor

**Purpose:** Process an entire simulation month in a single Gemini API call.

**Input:**
- `NetworkState`: All properties, participants, market conditions
- `PendingActions`: User actions queued since last tick
- `PreComputedResults`: Rent collected, dividends, market changes

**Prompt Structure:**
```
SYSTEM: You are the OSF Network Simulation Engine...

USER:
# OSF Network Simulation - Month {N}

## Current Network State
[Properties JSON]
[Participants JSON]
[Market Conditions JSON]

## Pre-Computed Results
[Rent, dividends, valuations]

## Pending User Actions
[Prioritized action list]

## Your Tasks
1. Process User Actions
2. NPC Decisions
3. Conflict Resolution
4. Generate Events
5. Governor Summary
6. User Responses
7. Alerts
```

**Output (JSON):**
```json
{
  "events": [...],
  "state_changes": {...},
  "npc_decisions": [...],
  "governor_summary": "...",
  "alerts": [...],
  "chat_responses": {...},
  "processing_log": [...]
}
```

### 3. Interactive Agents

**Governor Agent:**
- Answers general questions about the network
- Educational focus
- Uses `gemini-flash` for low latency
- Streaming responses for UX

**Portfolio Advisor:**
- Personalized investment advice
- Portfolio analysis
- Risk assessment
- Uses `gemini-flash`

---

## API Reference

### Clock Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/network/clock/status` | Current clock state |
| GET | `/network/clock/presets` | Available timing presets |
| GET | `/network/clock/pending-actions` | Queued actions |
| POST | `/network/clock/preset` | Change preset |
| POST | `/network/clock/interval` | Set custom interval |
| POST | `/network/clock/mode` | Set auto/manual |
| POST | `/network/clock/start` | Start the clock |
| POST | `/network/clock/stop` | Stop the clock |
| POST | `/network/clock/pause` | Pause (keep state) |
| POST | `/network/clock/resume` | Resume from pause |
| POST | `/network/clock/force-tick` | Trigger immediate tick |
| POST | `/network/clock/queue-action` | Add action to queue |
| GET | `/network/clock/stream` | SSE event stream |

### Network Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/network/state` | Network summary |
| GET | `/network/properties` | Property list |
| GET | `/network/participants` | Participant list |
| POST | `/network/governor/chat` | Chat with Governor |
| GET | `/network/governor/chat/stream` | Streaming Governor chat |
| POST | `/network/advisor/portfolio` | Portfolio advice |

---

## Data Models

### Property
```python
@dataclass
class Property:
    id: str
    address: str
    suburb: str
    state: str
    property_type: str  # 'house', 'apartment', 'townhouse'
    bedrooms: int
    bathrooms: int
    valuation: float
    network_ownership: float  # 0.0 - 1.0
    token_price: float
    gross_yield: float
    status: str  # 'available', 'tenanted', 'owner_occupied'
    tenant_id: Optional[str]
    weekly_rent: Optional[float]
```

### Participant
```python
@dataclass
class Participant:
    id: str
    name: str
    type: str  # 'human', 'npc'
    role: str  # 'investor', 'renter', 'tenant', 'homeowner', 'custodian', 'foundation'
    balance: float
    holdings: List[Dict]  # [{property_id, tokens, percent}]
    
    # NPC-specific
    personality: Optional[Dict[str, float]]  # risk_tolerance, patience, etc.
    goal: Optional[str]
```

### PendingAction
```python
@dataclass
class PendingAction:
    id: str
    user_id: str
    action_type: str  # 'buy', 'sell', 'rent', 'vote', 'service', etc.
    data: Dict[str, Any]
    priority: int  # Higher = processed first
    timestamp: datetime
```

---

## Implementation Plan

### Phase 1: Core Loop (COMPLETED)
- [x] Network clock with configurable timing
- [x] Batch processor with Gemini integration
- [x] Interactive Governor and Advisor agents
- [x] Frontend clock sync component
- [x] Demo state generation

### Phase 2: State Persistence (COMPLETED)
- [x] Database schema design (SQLAlchemy models)
- [x] SQLite integration (aiosqlite for async)
- [x] State save/load on tick
- [x] User accounts linked to participants
- [x] Historical data tracking (network_events table)

### Phase 3: Action Processing (COMPLETED)
- [x] Action validation (balance checks, availability)
- [x] Order matching for token trades
- [x] Rent payment processing
- [x] Service job completion
- [x] Governance vote tallying

### Phase 4: NPC Enhancement (COMPLETED)
- [x] More diverse NPC personalities (11 unique NPCs)
- [x] Goal-driven behavior (accumulate, income, divest, stabilize)
- [x] Inter-NPC transactions
- [x] Market maker NPC (liquidity provider)
- [x] Property developer NPC (new listings)

### Phase 5: Events & Narrative (COMPLETED)
- [x] Random market events (RBA rates, housing trends)
- [x] Property listings and sales
- [x] Maintenance emergencies (scheduled and urgent)
- [x] Economic cycles (5 phases with transitions)
- [x] News feed generation (Gemini-powered summaries)

### Phase 6: Polish & Demo (COMPLETED)
- [ ] Demo video recording (user task)
- [x] Architecture diagrams (ARCHITECTURE.md)
- [x] Submission write-up (SUBMISSION.md)
- [x] Performance optimization
- [x] Error handling (middleware/error_handler.py)
- [x] Demo script (DEMO_SCRIPT.md)

### Phase 7: UI Enhancements (COMPLETED)
- [x] Property images in rental/tenant/homeowner sections
- [x] Property selection workflows for all roles
- [x] Homeowner property listing feature
- [x] Service provider transactions linked to properties
- [x] Property detail dialog with Services tab
- [x] **Network Ledger tab (blockchain-style tx log)**
- [x] Investment distribution charts
- [x] Participant role name formatting
- [x] Market data calibration integration

### Phase 8: Marathon Agent & Advanced Features (COMPLETED)
- [x] **Marathon Agent Mode** - 10-year autonomous simulation
  - [x] Auto-run with configurable tick intervals
  - [x] AI Thinking Log with thought signatures
  - [x] NPC self-correction based on performance
  - [x] Session continuity tracking
- [x] **WA Market Dynamics**
  - [x] Iron ore price events affecting economy
  - [x] Population growth/decline cycles
  - [x] Phase-aware property appreciation
  - [x] Mining boom/bust event templates
- [x] **Self-Healing System (Demand Side)**
  - [x] Liquidity pool activation
  - [x] Buyer-seller matching
  - [x] Partial exit programs
  - [x] Rent-to-own acceleration
- [x] **Self-Healing System (Supply Side)**
  - [x] Property sourcing during high demand
  - [x] Homeowner outreach campaigns
  - [x] Buyer/renter waitlist management
  - [x] Vacancy incentives
- [x] **Realistic Financial Model**
  - [x] Yield compression during booms
  - [x] Dynamic token pricing from network valuation
  - [x] Proportional dividend distribution
  - [x] 49% homeowner control threshold
- [x] **Post-Marathon Synopsis**
  - [x] Stakeholder outcomes summary
  - [x] Market journey visualization
  - [x] Self-healing activity report
  - [x] Network scale metrics
- [x] **Community Feedback System**
  - [x] NPC-generated feedback (bugs, features, questions)
  - [x] Market-condition-aware templates
  - [x] Governor AI auto-responses
  - [x] Community sentiment tracking
  - [x] Feedback-triggered diagnostics
- [x] **Interactive Diagrams (Svelte Flow)**
  - [x] Money Flow diagram with animated edges
  - [x] Self-Healing Cycle diagram with active step

### Phase 9: Cooperative Gamification & UX Polish (COMPLETED)
- [x] **Cooperative Gamification System**
  - [x] Network Health Report (A-F grade)
  - [x] Collective Outcomes (families housed, dividends, etc.)
  - [x] User Contribution tracking
  - [x] Contribution titles (Founding Investor, Network Anchor)
- [x] **Exploration Achievements**
  - [x] 10 achievements for learning milestones
  - [x] Toast notifications on unlock
  - [x] Achievement grid in synopsis
- [x] **Insight Moments**
  - [x] Educational popups during marathon
  - [x] Market condition explanations
  - [x] Self-healing alerts
  - [x] Year milestone summaries
- [x] **Floating AI Chat**
  - [x] Persistent bottom-right button
  - [x] Expandable/minimizable panel
  - [x] Streaming SSE responses
  - [x] Always-accessible Network Governor
- [x] **Onboarding Modal**
  - [x] First-time user detection
  - [x] Quick Demo option (24 months fast)
  - [x] Full Marathon option
  - [x] localStorage persistence
- [x] **Connected Role State**
  - [x] Homeowner equity → Investor holdings
  - [x] "Your Home Equity" badge
  - [x] Cross-role navigation links
- [x] **Live Performance Charts**
  - [x] Real-time SVG charts during marathon
  - [x] Network value tracking
  - [x] Token price history
  - [x] User net worth visualization
- [x] **Dynamic Property Portfolio**
  - [x] Properties enter based on network reputation
  - [x] Properties exit on poor performance
  - [x] Diverse Perth suburbs with real pricing
- [x] **Homepage Rewrite**
  - [x] Problem-solution narrative
  - [x] Clear value proposition
  - [x] Gemini 3 hackathon section

---

## Future Features

> **Add your feature ideas below. Use the template for each feature.**

### Feature Template

```markdown
### Feature Name
**Priority:** High / Medium / Low
**Complexity:** Simple / Medium / Complex
**Dependencies:** [List any features this depends on]

**Description:**
[What does this feature do?]

**User Story:**
As a [role], I want to [action] so that [benefit].

**Implementation Notes:**
- [Technical considerations]
- [API changes needed]
- [Frontend changes needed]

**Acceptance Criteria:**
- [ ] Criteria 1
- [ ] Criteria 2
```

---

### Feature 1: Property Generation Pipeline

**Priority:** High  
**Complexity:** Medium  
**Dependencies:** Gemini API with Imagen 3 access

**Description:**
A complete pipeline that generates property data, descriptions, and images. The flow ensures that descriptions inform image generation for consistency.

**Pipeline Flow:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROPERTY GENERATION PIPELINE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  STEP 1: Generate Property Data                                              │
│  ───────────────────────────────                                             │
│  Input: Seed parameters (suburb, type, price range)                          │
│  Output: Complete property attributes                                        │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ {                                                                    │    │
│  │   "address": "32 Norbury Crescent",                                 │    │
│  │   "suburb": "City Beach",                                           │    │
│  │   "bedrooms": 4, "bathrooms": 3, "parking": 3,                      │    │
│  │   "land_size": 1123, "build_area": 430,                             │    │
│  │   "architectural_style": "Contemporary Australian",                  │    │
│  │   "features": ["pool", "solar", "boat_parking", "alfresco"],        │    │
│  │   "interior": ["marble_floors", "granite_kitchen", "study"],        │    │
│  │   "landscaping": ["established_gardens", "lawn", "native_plants"],  │    │
│  │   "valuation": 3050000,                                             │    │
│  │   "gross_yield": 4.2                                                │    │
│  │ }                                                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  STEP 2: Generate Marketing Description                                      │
│  ───────────────────────────────────────                                     │
│  Input: Property data from Step 1                                            │
│  Output: Rich marketing copy + structured highlights                         │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ {                                                                    │    │
│  │   "headline": "MODERN, SINGLE LEVEL LIVING...",                     │    │
│  │   "highlights": [...],                                              │    │
│  │   "features_description": "This contemporary residence...",         │    │
│  │   "lifestyle_description": "The Empire Games Village...",           │    │
│  │   "image_brief": "Detailed description for image generation..."     │    │
│  │ }                                                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                    ┌───────────────┴───────────────┐                        │
│                    ▼                               ▼                        │
│  STEP 3A: Generate Isometric Image    STEP 3B: Generate Floor Plan         │
│  ─────────────────────────────────    ─────────────────────────────         │
│  Input: image_brief + property data   Input: property data + rooms          │
│  Output: 45° isometric render         Output: Architectural floor plan      │
│                                                                              │
│  ┌─────────────────────────┐         ┌─────────────────────────┐           │
│  │                         │         │  ┌───┐ ┌───────────┐    │           │
│  │   [Isometric 3D View]   │         │  │BR1│ │  LIVING   │    │           │
│  │                         │         │  └───┘ │           │    │           │
│  │   Pool, landscaping,    │         │  ┌───┐ └───────────┘    │           │
│  │   solar panels visible  │         │  │BR2│ ┌───┐ ┌───┐     │           │
│  │                         │         │  └───┘ │KIT│ │DIN│     │           │
│  └─────────────────────────┘         └────────┴───┴─┴───┴─────┘           │
│                                                                              │
│                    └───────────────┬───────────────┘                        │
│                                    ▼                                         │
│  STEP 4: Update Property Record                                              │
│  ──────────────────────────────                                              │
│  Save all generated content to database                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**API Endpoint:**
```python
# Full pipeline - generates everything
POST /api/v1/network/properties/generate
{
  "suburb": "City Beach",
  "property_type": "house",
  "price_range": [2500000, 3500000],
  "features": ["pool", "solar"]  # optional hints
}

# Returns complete property with images
{
  "property": { ... },
  "listing": { ... },
  "images": {
    "isometric": "data:image/png;base64,...",
    "floorplan": "data:image/png;base64,..."
  }
}
```

---

### Feature 1A: Isometric Property Image Generation (Imagen 3)

**Description:**
Generate realistic 45-degree isometric property renders using Imagen 3. Uses the description's `image_brief` field for detailed, consistent prompting.

**User Story:**
As an investor, I want to see realistic property images so that I can visualize what I'm investing in without needing actual photos.

**Image Brief Generation (Step 2 output):**
```json
{
  "image_brief": {
    "style": "Photorealistic 3D architectural render, 45-degree isometric aerial view",
    "building": "Single-level contemporary Australian home with dark grey hip roof, white rendered walls, large glass windows and sliding doors, marble-tiled alfresco area",
    "features": "Rooftop solar panel array (12 panels), triple garage on right side with boat/caravan hardstand, saltwater swimming pool with timber deck surround",
    "landscaping": "Established gardens with Norfolk Island pines, native Australian plants, large grassed lawn area, high white boundary walls",
    "materials": "White marble floor tiles, dark timber decking, glass pool fencing, granite kitchen visible through windows",
    "atmosphere": "Bright daylight, clean shadows, premium luxury feel",
    "background": "Clean cream/white gradient background"
  }
}
```

**Imagen 3 Prompt (constructed from brief):**
```
45-degree isometric aerial view of a luxury single-level contemporary Australian home.

BUILDING: Dark grey hip roof with solar panels, white rendered walls, floor-to-ceiling glass windows, marble-tiled alfresco entertaining area with outdoor kitchen.

OUTDOOR: North-facing saltwater swimming pool with timber sundeck, glass pool fencing. Triple garage with boat parking. High white boundary walls.

LANDSCAPING: Established gardens with Norfolk Island pines and mature trees on left. Native Australian plants. Large grassed play area.

MATERIALS: White marble floor tiles throughout, dark timber decking, granite surfaces visible in kitchen.

STYLE: Photorealistic 3D architectural render. Clean cream background. Bright natural lighting with soft shadows. Premium luxury residential feel.

DO NOT include: People, cars, text, watermarks.
```

**Technical Implementation:**
```python
async def generate_isometric_image(property_data: dict, image_brief: dict) -> bytes:
    """Generate isometric property image using Imagen 3 Fast."""
    
    prompt = construct_imagen_prompt(image_brief)
    
    # Use FAST model for quick generation (demo quality)
    response = await client.models.generate_images(
        model="imagen-3.0-fast-generate-001",  # Fast variant - lower latency
        prompt=prompt,
        config=ImageGenerationConfig(
            number_of_images=1,
            aspect_ratio="16:9",  # Good for isometric views
            output_mime_type="image/jpeg",  # JPEG smaller/faster than PNG
        )
    )
    
    return response.generated_images[0].image_bytes
```

**Model Options:**
| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| `imagen-3.0-fast-generate-001` | ~2-3s | Good | Demo, bulk generation |
| `imagen-3.0-generate-002` | ~8-10s | Best | Final presentation |

**Alternative: Gemini Native Image Generation**
```python
# Even faster - use Gemini's built-in image generation
response = await client.models.generate_content(
    model="gemini-3-flash",
    contents="Generate an isometric view of...",
    config=GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
    )
)
# Extract image from response.candidates[0].content.parts
```

**Acceptance Criteria:**
- [ ] Isometric images generated from property descriptions
- [ ] Images reflect specific features (pool, solar, garage count)
- [ ] Consistent architectural style across properties
- [ ] High quality suitable for demo presentation
- [ ] Cached to avoid regeneration costs

---

### Feature 1B: Floor Plan Image Generation (Imagen 3)

**Description:**
Generate architectural floor plan images showing room layout, dimensions, and flow. Uses property data to create accurate, professional-looking floor plans.

**User Story:**
As an investor, I want to see the floor plan so that I can understand the property layout and room sizes.

**Floor Plan Brief (generated in Step 2):**
```json
{
  "floorplan_brief": {
    "layout_type": "Single level, separated wings",
    "total_area": "430m²",
    "rooms": [
      {"name": "Master Suite", "size": "45m²", "position": "left wing", "features": ["ensuite", "WIR", "garden views"]},
      {"name": "Bedroom 2", "size": "16m²", "position": "right wing"},
      {"name": "Bedroom 3", "size": "14m²", "position": "right wing"},
      {"name": "Bedroom 4", "size": "14m²", "position": "right wing"},
      {"name": "Living", "size": "65m²", "position": "central", "features": ["open plan", "pool views"]},
      {"name": "Kitchen", "size": "25m²", "position": "central", "features": ["granite", "island bench"]},
      {"name": "Dining", "size": "20m²", "position": "central"},
      {"name": "Alfresco", "size": "40m²", "position": "rear"},
      {"name": "Garage", "size": "60m²", "position": "right", "features": ["triple"]}
    ],
    "flow": "Entry leads to central living, master wing left, family wing right, outdoor entertaining rear"
  }
}
```

**Imagen 3 Prompt for Floor Plan:**
```
Professional architectural floor plan, top-down view, clean technical drawing style.

LAYOUT: Single-level luxury home, 430m² total area. Separated wing design.

LEFT WING: Master bedroom suite with ensuite bathroom and walk-in robe.

CENTRAL: Open-plan living (65m²), kitchen with island bench (25m²), dining area (20m²). High ceilings indicated.

RIGHT WING: Three secondary bedrooms, family bathroom, study.

REAR: Large alfresco entertaining area (40m²) connecting to pool area.

GARAGE: Triple garage (60m²) on right side with internal access.

STYLE: Clean architectural line drawing. Black lines on white background. Room labels in elegant font. Dimensions shown. North arrow indicator. Scale bar.

DO NOT include: Furniture, colors, 3D elements, photographs.
```

**Technical Implementation:**
```python
async def generate_floorplan_image(property_data: dict, floorplan_brief: dict) -> bytes:
    """Generate floor plan image using Imagen 3 Fast."""
    
    prompt = construct_floorplan_prompt(floorplan_brief)
    
    # Use FAST model for quick generation
    response = await client.models.generate_images(
        model="imagen-3.0-fast-generate-001",  # Fast variant
        prompt=prompt,
        config=ImageGenerationConfig(
            number_of_images=1,
            aspect_ratio="1:1",  # Square for floor plans
            output_mime_type="image/jpeg",
        )
    )
    
    return response.generated_images[0].image_bytes
```

**Generation Speed Target:**
- Isometric image: ~2-3 seconds
- Floor plan: ~2-3 seconds
- Total per property: ~5-6 seconds (parallel generation)

**Acceptance Criteria:**
- [ ] Floor plans generated for each property
- [ ] Room count matches property data
- [ ] Layout reflects description (separated wings, open plan, etc.)
- [ ] Professional architectural drawing style
- [ ] Readable room labels and dimensions

---

### Feature 2: AI Property Description Generation

**Priority:** High  
**Complexity:** Medium  
**Dependencies:** Gemini API

**Description:**
Auto-generate comprehensive property listings including marketing descriptions, highlights, structured attributes, AND image generation briefs. This is the central step that creates the detailed description used by Imagen 3 to generate consistent visuals.

**User Story:**
As an investor, I want detailed property descriptions so that I can understand the property's value proposition and lifestyle benefits.

**Generated Content Structure (Full Output):**

```json
{
  "headline": "MODERN, SINGLE LEVEL LIVING IN THE HEART OF THE VILLAGE",
  "subheadline": "32 Norbury Crescent, City Beach",
  
  "quick_stats": {
    "bedrooms": 4,
    "bathrooms": 3,
    "parking": 3,
    "land_size": "1,123m²",
    "property_type": "House",
    "status": "Available"
  },
  
  "highlights": [
    {
      "icon": "pool",
      "title": "North-facing saltwater pool",
      "description": "Saltwater pool, timber sundeck, powder room, outdoor shower & play area"
    },
    {
      "icon": "location",
      "title": "Sought-after Village precinct",
      "description": "Walk to cafes, shops, beach, golf course & Kapinara Primary School"
    },
    {
      "icon": "layout",
      "title": "Single level, separated layout",
      "description": "Marble floors, coved ceilings, granite kitchen & zoned bedroom wings"
    }
  ],
  
  "features_description": {
    "title": "THE FEATURES YOU WILL LOVE",
    "content": "This contemporary, single level residence displays classical styling and timeless elegance, taking full advantage of an enormous landholding (1,123m²) in the hugely sought after Empire Games Village precinct. Marble floors and coved ceilings define a superb sequence of living, dining and entertaining spaces with an exceptional sense of openness and flow..."
  },
  
  "lifestyle_description": {
    "title": "THE LIFESTYLE YOU WILL LIVE",
    "content": "The historic Empire Games Village precinct is one of the most sought after locations in City Beach with privileged access to the bustling cafes, restaurants and shopping options forming the social hub of the suburb..."
  },
  
  "property_features": {
    "building_size": "430m²",
    "land_size": "1,123m²",
    "ensuites": 2,
    "toilets": 4,
    "garage_spaces": 3,
    "indoor": ["Study", "Ducted AC", "Ducted vacuum", "Security system", "Marble floors", "Coved ceilings"],
    "outdoor": ["Swimming pool - saltwater", "Solar panels", "Boat/caravan parking", "Alfresco area", "Timber sundeck"]
  },
  
  "rates": {
    "council": 3908.70,
    "water": 2642.10
  },
  
  "nearby": {
    "schools": [
      {"name": "Kapinara Primary School", "distance": "0.51km", "type": "Government"},
      {"name": "Holy Spirit School", "distance": "0.96km", "type": "Catholic"}
    ],
    "amenities": ["Beach (0.3km)", "Empire Village Cafe Strip", "Bold Park Golf Course", "Wembley Aquatic Centre"]
  },

  "image_brief": {
    "style": "Photorealistic 3D architectural render, 45-degree isometric aerial view",
    "building": "Single-level contemporary Australian home, dark grey hip roof tiles, white rendered exterior walls, large floor-to-ceiling glass windows and sliding doors, marble-tiled wrap-around alfresco area with outdoor kitchen",
    "roof_features": "12-panel solar array on north-facing roof section",
    "outdoor_structures": "Triple garage attached on right side with internal access, concrete hardstand for boat/caravan",
    "pool_area": "North-facing rectangular saltwater swimming pool (8m x 4m), timber deck surround, glass pool fencing, poolside powder room structure, outdoor shower",
    "landscaping": "High white rendered boundary walls, established gardens with 3 Norfolk Island pines on left boundary, native Australian garden beds, large grassed lawn play area",
    "visible_interiors": "Through windows: marble floor tiles, granite kitchen island, open-plan living space",
    "materials": "White marble exterior tiles, dark timber decking, brushed concrete driveway, glass balustrades",
    "atmosphere": "Bright Australian daylight, clean architectural shadows, premium luxury residential",
    "background": "Clean cream/off-white gradient, no surrounding context"
  },

  "floorplan_brief": {
    "layout_type": "Single level, dual-wing design",
    "orientation": "North to rear (pool side)",
    "total_area": "430m²",
    "entry": "Grand entry foyer from front, leads to central living hub",
    "rooms": [
      {"name": "Master Suite", "area": "45m²", "wing": "west", "features": ["ensuite with dual vanity", "walk-in robe", "garden outlook"]},
      {"name": "Living", "area": "65m²", "wing": "central", "features": ["open plan", "pool views", "marble floors"]},
      {"name": "Kitchen", "area": "25m²", "wing": "central", "features": ["granite island bench", "butler's pantry"]},
      {"name": "Dining", "area": "22m²", "wing": "central", "features": ["adjacent to alfresco"]},
      {"name": "Bedroom 2", "area": "16m²", "wing": "east", "features": ["built-in robe"]},
      {"name": "Bedroom 3", "area": "14m²", "wing": "east", "features": ["built-in robe"]},
      {"name": "Bedroom 4", "area": "14m²", "wing": "east", "features": ["built-in robe"]},
      {"name": "Study", "area": "12m²", "wing": "west", "features": ["quiet location"]},
      {"name": "Family Bathroom", "area": "10m²", "wing": "east", "features": ["separate bath and shower"]},
      {"name": "Alfresco", "area": "45m²", "wing": "rear", "features": ["outdoor kitchen", "pool access"]},
      {"name": "Triple Garage", "area": "65m²", "wing": "east", "features": ["internal access", "storage"]}
    ],
    "flow_description": "Entry opens to central living spine. Master retreat isolated in west wing for privacy. Family bedrooms clustered in east wing near bathroom. Living areas flow seamlessly to rear alfresco and pool. Garage access through laundry.",
    "special_features": ["Ducted AC zones marked", "Powder rooms x2", "Laundry with external access"]
  }
}
```

**Prompt Template:**
```
You are generating a comprehensive property listing for the OSF Network simulation.

INPUT - Property Data:
- Address: {address}, {suburb}, {state} {postcode}
- Type: {property_type}
- Bedrooms: {bedrooms}, Bathrooms: {bathrooms}, Parking: {parking}
- Land: {land_size}m², Build: {build_area}m²
- Architectural Style: {style}
- Key Features: {feature_list}
- Estimated Value: ${valuation:,}
- Gross Yield: {yield}%

OUTPUT - Generate valid JSON with these sections:

1. "headline": Aspirational CAPS headline (8-12 words)
2. "subheadline": Address formatted nicely
3. "quick_stats": Structured property stats
4. "highlights": Array of 3 key selling points with icon, title, description
5. "features_description": Premium marketing copy (2-3 paragraphs)
6. "lifestyle_description": Location/lifestyle benefits (1-2 paragraphs)
7. "property_features": Structured indoor/outdoor feature lists
8. "rates": Estimated council and water rates
9. "nearby": Schools and amenities with distances

CRITICAL - Also generate these for image generation:

10. "image_brief": Detailed visual description for isometric 3D render
    - style, building, roof_features, outdoor_structures
    - pool_area, landscaping, visible_interiors, materials
    - atmosphere, background

11. "floorplan_brief": Detailed layout for floor plan generation
    - layout_type, orientation, total_area
    - rooms array with name, area, wing, features
    - flow_description, special_features

Style: Premium Australian real estate marketing
Tone: Aspirational, sophisticated, lifestyle-focused
Accuracy: Ensure all numbers and features match input data
```

**Implementation Notes:**
- Generate on property creation (Step 2 of pipeline)
- Output includes image_brief and floorplan_brief for Step 3
- Cache in database (descriptions don't change often)
- Use structured output (JSON mode) for reliable parsing
- Regenerate if property attributes change significantly
- image_brief must be detailed enough for Imagen 3 consistency

**API Endpoints:**
```python
# Generate description (Step 2 of pipeline)
POST /api/v1/network/properties/{property_id}/generate-description

# Get cached listing
GET /api/v1/network/properties/{property_id}/listing

# Regenerate everything (full pipeline)
POST /api/v1/network/properties/{property_id}/regenerate
```

**Data Model:**
```python
@dataclass
class PropertyListing:
    property_id: str
    headline: str
    subheadline: str
    highlights: List[Dict[str, str]]
    features_description: Dict[str, str]
    lifestyle_description: Dict[str, str]
    property_features: Dict[str, Any]
    rates: Dict[str, float]
    nearby: Dict[str, List[Any]]
    
    # Image generation briefs
    image_brief: Dict[str, str]
    floorplan_brief: Dict[str, Any]
    
    # Generated image URLs/data
    isometric_image_url: Optional[str] = None
    floorplan_image_url: Optional[str] = None
    
    # Metadata
    generated_at: datetime
    images_generated_at: Optional[datetime] = None
```

**Acceptance Criteria:**
- [ ] Properties have rich, AI-generated descriptions
- [ ] Descriptions reflect actual property attributes
- [ ] Highlights are specific and compelling
- [ ] image_brief is detailed enough for consistent renders
- [ ] floorplan_brief accurately describes room layout
- [ ] Descriptions cached/persisted
- [ ] Regeneration updates both text and images

---

### Feature 3: Property Detail Modal/Page

**Priority:** Medium  
**Complexity:** Medium  
**Dependencies:** Features 1 & 2

**Description:**
Rich property detail view that showcases the generated image and description, similar to realestate.com.au listings.

**UI Components:**
1. Hero image (isometric render)
2. Quick stats bar (beds/baths/parking/size)
3. AI highlights cards
4. Tabbed content (Features, Lifestyle, Investment)
5. Investment calculator (yield, token price, ownership %)
6. Action buttons (Buy Tokens, Request Info, Save)

**Mockup Structure:**
```
┌─────────────────────────────────────────────────────────────────┐
│  [Isometric Property Image - Full Width]                        │
│                                                                 │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────────┐                           │
│  │ 4🛏 │ │ 3🚿 │ │ 3🚗 │ │ 1,123m² │  House • Available        │
│  └─────┘ └─────┘ └─────┘ └─────────┘                           │
├─────────────────────────────────────────────────────────────────┤
│  MODERN, SINGLE LEVEL LIVING IN THE HEART OF THE VILLAGE       │
│  32 Norbury Crescent, City Beach                                │
├─────────────────────────────────────────────────────────────────┤
│  Property Highlights (AI-generated)                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ 🏊 Pool      │ │ 📍 Location  │ │ 🏠 Layout    │            │
│  │ North-facing │ │ Walk to...   │ │ Single level │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
├─────────────────────────────────────────────────────────────────┤
│  [Features] [Lifestyle] [Investment]                            │
│  ─────────────────────────────────────────────────────────────  │
│  THE FEATURES YOU WILL LOVE                                     │
│                                                                 │
│  This contemporary, single level residence displays classical   │
│  styling and timeless elegance...                               │
├─────────────────────────────────────────────────────────────────┤
│  Investment Summary                                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Token Price: $1.02  │ Network Ownership: 40%            │   │
│  │ Gross Yield: 5.2%   │ Available Tokens: 60,000          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [Buy Tokens] [Add to Watchlist] [Ask Advisor]                  │
└─────────────────────────────────────────────────────────────────┘
```

**Acceptance Criteria:**
- [ ] Property detail view with rich visuals
- [ ] AI-generated image prominently displayed
- [ ] Highlights easily scannable
- [ ] Full description available
- [ ] Investment metrics clearly shown
- [ ] Actions to buy/watch/inquire

---

### Feature 4: Batch Property Pre-Generation

**Priority:** High  
**Complexity:** Simple  
**Dependencies:** Features 1 & 2

**Description:**
Pre-generate a large pool of properties with all images and descriptions ahead of time. Properties are stored in "draft" status and enabled when needed in the simulation. This eliminates wait times during demos.

**Strategy:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     BATCH PRE-GENERATION STRATEGY                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  OFFLINE (Run overnight / before demo)                                       │
│  ─────────────────────────────────────                                       │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  python scripts/generate_properties.py --count 50                   │    │
│  │                                                                      │    │
│  │  Generating property 1/50... [City Beach, House, 4br] ✓ 3.2s        │    │
│  │  Generating property 2/50... [Subiaco, Apartment, 2br] ✓ 2.8s       │    │
│  │  ...                                                                 │    │
│  │  Complete! 50 properties generated in 4m 23s                        │    │
│  │  Saved to: data/property_pool.json                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Output: property_pool.json                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  {                                                                   │    │
│  │    "generated_at": "2026-01-19T10:00:00Z",                          │    │
│  │    "count": 50,                                                      │    │
│  │    "properties": [                                                   │    │
│  │      {                                                               │    │
│  │        "id": "prop_001",                                            │    │
│  │        "status": "draft",  // Not yet in simulation                 │    │
│  │        "data": { ... },                                             │    │
│  │        "listing": { ... },                                          │    │
│  │        "images": {                                                  │    │
│  │          "isometric": "data:image/jpeg;base64,...",                 │    │
│  │          "floorplan": "data:image/jpeg;base64,..."                  │    │
│  │        }                                                             │    │
│  │      },                                                              │    │
│  │      ...                                                             │    │
│  │    ]                                                                 │    │
│  │  }                                                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  RUNTIME (During demo)                                                       │
│  ─────────────────────                                                       │
│                                                                              │
│  Admin clicks "Add New Property" or simulation triggers new listing          │
│                         │                                                    │
│                         ▼                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  // Instant - no generation needed!                                 │    │
│  │  property = pool.get_next_available()                               │    │
│  │  property.status = "available"                                      │    │
│  │  property.listed_at = now()                                         │    │
│  │  network.add_property(property)                                     │    │
│  │                                                                      │    │
│  │  // User sees property immediately with images                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Property Pool Variety:**
| Category | Options | Distribution |
|----------|---------|--------------|
| Suburbs | City Beach, Subiaco, Nedlands, Cottesloe, Claremont, Fremantle | Even |
| Types | House (50%), Apartment (30%), Townhouse (20%) | Weighted |
| Bedrooms | 1-5 | Bell curve around 3 |
| Price Range | $400k - $5M | Log distribution |
| Features | Pool, Solar, Views, Garden, etc. | Random combinations |

**Generation Script:**
```python
# scripts/generate_properties.py

import asyncio
import json
from pathlib import Path

async def generate_property_pool(count: int = 50):
    """Pre-generate property pool for simulation."""
    
    pool = {
        "generated_at": datetime.utcnow().isoformat(),
        "count": count,
        "properties": []
    }
    
    suburbs = ["City Beach", "Subiaco", "Nedlands", "Cottesloe", "Claremont", "Fremantle"]
    
    for i in range(count):
        print(f"Generating property {i+1}/{count}...", end=" ")
        start = time.time()
        
        # Step 1: Generate property data
        property_data = generate_random_property_data(
            suburb=suburbs[i % len(suburbs)],
            index=i
        )
        
        # Step 2: Generate description + image briefs
        listing = await generate_property_listing(property_data)
        
        # Step 3: Generate images (parallel)
        isometric, floorplan = await asyncio.gather(
            generate_isometric_image(listing["image_brief"]),
            generate_floorplan_image(listing["floorplan_brief"])
        )
        
        # Package everything
        pool["properties"].append({
            "id": f"prop_{i+1:03d}",
            "status": "draft",
            "data": property_data,
            "listing": listing,
            "images": {
                "isometric": base64_encode(isometric),
                "floorplan": base64_encode(floorplan)
            }
        })
        
        elapsed = time.time() - start
        print(f"✓ {elapsed:.1f}s")
    
    # Save to file
    output_path = Path("data/property_pool.json")
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(json.dumps(pool, indent=2))
    
    print(f"\nComplete! {count} properties saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(generate_property_pool(50))
```

**Property Status Flow:**
```
draft → available → tenanted/sold → archived
  │         │            │
  │         │            └─ Tenant moves in or tokens fully sold
  │         └─ Enabled in simulation, visible to users
  └─ Pre-generated, waiting in pool
```

**API Endpoints:**
```python
# Admin: Enable next property from pool
POST /api/v1/admin/properties/enable-next
Response: { "property": {...}, "remaining_in_pool": 47 }

# Admin: Enable specific property
POST /api/v1/admin/properties/{pool_id}/enable

# Admin: Check pool status
GET /api/v1/admin/properties/pool-status
Response: { "total": 50, "draft": 47, "enabled": 3 }

# Trigger: Auto-enable property (e.g., on network growth)
# Called by batch processor when conditions met
```

**CLI Commands:**
```bash
# Generate 50 properties (run overnight)
python scripts/generate_properties.py --count 50

# Generate with specific mix
python scripts/generate_properties.py --count 30 --suburbs "City Beach,Subiaco" --types "house,apartment"

# Check pool status
python scripts/pool_status.py

# Enable properties for demo
python scripts/enable_properties.py --count 5
```

**Acceptance Criteria:**
- [ ] Script generates 50+ properties offline
- [ ] Each property has complete data, listing, and images
- [ ] Properties stored as JSON (or SQLite for larger pools)
- [ ] Pool loaded on app startup
- [ ] Properties can be enabled instantly (no wait)
- [ ] Admin can check pool status
- [ ] Simulation can auto-enable properties based on rules

---

### Feature 5: Character Avatar Generation

**Priority:** High  
**Complexity:** Simple  
**Dependencies:** Imagen 3 API

**Description:**
Generate 3D isometric character avatars for each role in the simulation. Characters stand on game board tiles, styled like board game pieces. Used for user avatars, NPC display, and role selection UI.

**Example Style (from user):**
- 45-degree isometric view
- Realistic 3D render, figurine/miniature aesthetic
- Character stands on geometric tile (hexagon, square, or octagon)
- Tile material: concrete, stone, or wood
- Clean studio lighting, soft shadows
- Light gradient background

**Role Types & Visual Descriptions:**

| Role | Character Description | Tile Style |
|------|----------------------|------------|
| **Investor** | Professional in navy suit, briefcase, confident stance | Polished concrete cube |
| **Renter** | Casual young adult, backpack or keys, friendly pose | Wooden hexagon |
| **Homeowner** | Family-oriented, holding house keys or plant, relaxed | Garden stone tile |
| **Trades Person** | Hi-vis vest, tool belt, cap, holding wrench/tools | Cracked concrete octagon |
| **Property Manager** | Smart casual, clipboard or tablet, organized look | Grey slate square |
| **Foundation Partner** | Business formal, handshake pose, trustworthy | Marble hexagon |
| **Governor (AI)** | Abstract/futuristic, holographic elements, AI aesthetic | Glowing platform |

**Prompt Template:**
```
Create a 45 degree isometric view of a [ROLE] character with realistic surfaces and materials, standing on a single tile for a game board.

CHARACTER: [Detailed description - clothing, pose, accessories, expression]

STYLE:
- 3D rendered figurine/miniature aesthetic
- Realistic materials and textures
- Soft studio lighting with gentle shadows
- Character is the focal point

TILE: [Shape] tile made of [material], approximately 1.5x character width
- Subtle texture detail on tile surface
- Tile slightly elevated like a game piece base

BACKGROUND: Clean light grey/white gradient, no distractions

DO NOT include: Text, logos, watermarks, multiple characters
```

**Character Briefs:**

```python
CHARACTER_BRIEFS = {
    "investor": {
        "description": "Professional male in tailored navy blue suit, white shirt, red tie. Holding brown leather briefcase. Confident standing pose, looking slightly to the side. Clean-shaven, neat brown hair.",
        "tile": "Polished concrete cube with subtle aggregate texture",
        "vibe": "Success, professionalism, wealth"
    },
    "investor_female": {
        "description": "Professional female in charcoal blazer and skirt, white blouse. Holding tablet or portfolio. Confident stance, slight smile. Professional hairstyle.",
        "tile": "Polished concrete cube with subtle aggregate texture",
        "vibe": "Success, professionalism, competence"
    },
    "renter": {
        "description": "Young adult in casual clothes - jeans, hoodie or t-shirt. Holding apartment keys or small box. Friendly, approachable expression. Diverse representation.",
        "tile": "Warm wooden hexagonal platform",
        "vibe": "Youth, mobility, aspiration"
    },
    "homeowner": {
        "description": "Middle-aged person in smart casual - chinos, button shirt. Holding house keys or small potted plant. Proud, content expression. Wedding ring visible.",
        "tile": "Natural stone garden tile with grass edge detail",
        "vibe": "Stability, family, achievement"
    },
    "tradesperson": {
        "description": "Rugged male tradie in grey t-shirt, hi-vis yellow safety vest, worn jeans, work boots. Leather tool belt with wrenches, screwdrivers. Holding pipe wrench. Baseball cap, beard, weathered hands.",
        "tile": "Cracked concrete octagonal platform with debris texture",
        "vibe": "Hard work, reliability, skill"
    },
    "tradesperson_female": {
        "description": "Female tradie in work clothes, hi-vis vest, steel-cap boots. Tool belt, holding drill or level. Confident stance, practical ponytail under cap.",
        "tile": "Cracked concrete octagonal platform",
        "vibe": "Skill, capability, breaking barriers"
    },
    "property_manager": {
        "description": "Professional in smart casual - blazer over polo shirt. Holding clipboard with checklist or tablet. Organized, efficient appearance. Lanyard with ID badge.",
        "tile": "Grey slate square tile, clean edges",
        "vibe": "Organization, service, reliability"
    },
    "foundation_partner": {
        "description": "Distinguished professional in premium business attire. Open, welcoming gesture or handshake pose. Grey hair, glasses optional. Trustworthy demeanor.",
        "tile": "White marble hexagonal platform with subtle veining",
        "vibe": "Trust, stability, partnership"
    },
    "governor_ai": {
        "description": "Abstract humanoid figure with smooth, metallic blue-silver surface. Subtle glowing circuit patterns. Zen-like pose, hands together or gesturing wisdom. No face details - smooth helmet-like head.",
        "tile": "Floating circular platform with soft blue glow underneath",
        "vibe": "Intelligence, fairness, technology"
    },
    "market_maker": {
        "description": "Sharp-dressed trader type, rolled sleeves, multiple screens implied. Energetic pose, pointing or gesturing. Modern smartwatch, earpiece.",
        "tile": "Digital-looking hexagon with subtle LED edge glow",
        "vibe": "Speed, markets, liquidity"
    }
}
```

**Generation Script (Fast Mode):**
```python
async def generate_character_avatars():
    """Pre-generate all character avatars using fast renders."""
    
    avatars = {}
    
    for role, brief in CHARACTER_BRIEFS.items():
        print(f"Generating {role}...", end=" ")
        
        prompt = f"""Create a 45 degree isometric view of a character standing on a game board tile.

CHARACTER: {brief['description']}
TILE: {brief['tile']}
STYLE: 3D figurine, soft lighting, light grey background

DO NOT include: Text, watermarks"""

        # FAST generation - ~2 seconds per image
        image = await client.models.generate_images(
            model="imagen-3.0-fast-generate-001",  # Fast model
            prompt=prompt,
            config=ImageGenerationConfig(
                number_of_images=1,
                aspect_ratio="1:1",  # Square for avatars
                output_mime_type="image/jpeg",  # Smaller files
            )
        )
        
        avatars[role] = base64_encode(image.generated_images[0].image_bytes)
        print("✓")
    
    save_json("data/avatars.json", avatars)
    print(f"Saved {len(avatars)} avatars")

# Generation time: ~45 avatars × 2s = ~90 seconds total
```

**Pre-Generation Strategy (Same as Properties):**
```
┌─────────────────────────────────────────────────────────────────┐
│  OFFLINE: Run once before demo                                  │
│  ─────────────────────────────                                  │
│                                                                 │
│  $ python scripts/generate_avatars.py                           │
│                                                                 │
│  Generating investor (1/3)... ✓ 2.1s                           │
│  Generating investor (2/3)... ✓ 2.3s                           │
│  Generating investor (3/3)... ✓ 2.0s                           │
│  Generating renter (1/3)... ✓ 2.2s                             │
│  ...                                                            │
│  Complete! 30 avatars saved to data/avatars/                    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  OUTPUT: data/avatars/                                          │
│  ─────────────────────                                          │
│                                                                 │
│  avatars/                                                       │
│  ├── investor_1.jpg                                             │
│  ├── investor_2.jpg                                             │
│  ├── investor_3.jpg                                             │
│  ├── renter_1.jpg                                               │
│  ├── renter_2.jpg                                               │
│  ├── ...                                                        │
│  ├── governor_ai_1.jpg                                          │
│  └── manifest.json    ← Index of all avatars                   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  RUNTIME: Just load from disk                                   │
│  ────────────────────────────                                   │
│                                                                 │
│  avatars = load_avatars("data/avatars/")                       │
│  # Instant - no generation needed                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Fixed Avatar Set:**
```python
# PARTICIPANT ROLES (~20 avatars)
PARTICIPANT_AVATARS = {
    "investor": 3,           # Suit, briefcase
    "renter": 3,             # Casual, keys
    "homeowner": 3,          # Smart casual, house keys
    "foundation_partner": 3, # Business formal
    "governor_ai": 2,        # AI/robot aesthetic
    "market_maker": 2,       # Trader type
    "npc_generic": 4,        # Variety for background NPCs
}

# SERVICE PROVIDERS (~25 avatars)
SERVICE_PROVIDER_AVATARS = {
    "plumber": 2,            # Pipe wrench, blue overalls
    "electrician": 2,        # Wire cutters, safety gear
    "gardener": 2,           # Gloves, pruning shears, sun hat
    "cleaner": 2,            # Cleaning supplies, apron
    "pest_control": 1,       # Spray equipment, coveralls
    "locksmith": 1,          # Key ring, tools
    "painter": 2,            # Paint roller, white overalls, paint splatter
    "roofer": 1,             # Hard hat, harness, hammer
    "hvac_tech": 1,          # HVAC gauges, uniform
    "pool_tech": 1,          # Pool net, test kit, shorts
    "security_tech": 1,      # Alarm panel, tools, uniform
    "building_inspector": 2, # Clipboard, hard hat, measuring tape
    "real_estate_agent": 2,  # Smart dress, tablet, "SOLD" sign
    "conveyancer": 1,        # Legal documents, glasses
    "accountant": 1,         # Calculator, glasses, neat attire
    "handyman": 2,           # General tools, versatile look
}

# Total: ~45 avatars, ~3-4 minutes to generate
```

**Service Provider Character Briefs:**
```python
SERVICE_PROVIDER_BRIEFS = {
    "plumber": {
        "description": "Plumber in blue work overalls, holding large pipe wrench. Tool bag at feet. Friendly, capable expression. Slightly wet/worn look to clothes.",
        "tile": "Grey concrete hexagon with subtle water puddle detail",
        "vibe": "Reliable, essential, skilled"
    },
    "electrician": {
        "description": "Electrician in dark work pants and company polo. Safety glasses on head, voltage tester in hand, wire cutters on belt. Alert, focused expression.",
        "tile": "Industrial metal grate platform",
        "vibe": "Precision, safety, expertise"
    },
    "gardener": {
        "description": "Gardener/landscaper in practical outdoor clothes - cargo shorts, sun-faded shirt, wide-brim hat. Leather gloves, holding pruning shears. Tanned, friendly.",
        "tile": "Natural grass and soil circular mound",
        "vibe": "Nature, care, outdoors"
    },
    "cleaner": {
        "description": "Professional cleaner in neat uniform or apron. Carrying cleaning caddy with supplies. Rubber gloves, efficient and proud demeanor.",
        "tile": "Sparkling clean white tile platform",
        "vibe": "Thoroughness, pride, detail"
    },
    "pest_control": {
        "description": "Pest control technician in protective coveralls, carrying spray wand equipment. Professional mask around neck. Determined expression.",
        "tile": "Concrete slab with subtle crack detail",
        "vibe": "Protection, thoroughness, expertise"
    },
    "locksmith": {
        "description": "Locksmith in work jacket, large key ring on belt, lock pick set visible. Holding door lock mechanism. Trustworthy, skilled appearance.",
        "tile": "Metallic brushed steel hexagon",
        "vibe": "Security, trust, precision"
    },
    "painter": {
        "description": "House painter in white overalls with colorful paint splatter. Holding paint roller, paint tray nearby. Cap worn backwards, cheerful expression.",
        "tile": "Paint-splattered drop cloth platform",
        "vibe": "Creativity, transformation, skill"
    },
    "roofer": {
        "description": "Roofer in work clothes, safety harness, hard hat. Holding roofing hammer, nail bag on belt. Weathered, tough, reliable appearance.",
        "tile": "Terracotta roof tile platform",
        "vibe": "Toughness, reliability, heights"
    },
    "hvac_tech": {
        "description": "HVAC technician in company uniform polo and work pants. Carrying refrigerant gauges, toolbox. Clean-cut, professional service tech look.",
        "tile": "Metal vent grate platform",
        "vibe": "Comfort, technical, essential"
    },
    "pool_tech": {
        "description": "Pool technician in shorts and company polo. Holding pool skimmer net, water test kit on belt. Tanned, relaxed but professional.",
        "tile": "Blue mosaic tile hexagon (pool tile style)",
        "vibe": "Summer, maintenance, clarity"
    },
    "security_tech": {
        "description": "Security system technician in uniform with company logo. Holding alarm panel, drill, and wiring. Professional, trustworthy appearance.",
        "tile": "Dark grey platform with subtle LED indicator lights",
        "vibe": "Safety, technology, protection"
    },
    "building_inspector": {
        "description": "Building inspector in smart casual with hi-vis vest. Hard hat, clipboard with checklist, measuring tape, flashlight. Authoritative, thorough.",
        "tile": "Blueprint-patterned platform",
        "vibe": "Standards, compliance, expertise"
    },
    "real_estate_agent": {
        "description": "Real estate agent in sharp business attire. Holding tablet showing property, small 'SOLD' sticker visible. Confident smile, polished appearance.",
        "tile": "Polished marble hexagon",
        "vibe": "Sales, success, connection"
    },
    "conveyancer": {
        "description": "Legal professional in business attire, glasses. Holding property documents/contracts, pen ready. Studious, meticulous appearance.",
        "tile": "Dark wood platform with legal book texture",
        "vibe": "Legal, detail, trust"
    },
    "accountant": {
        "description": "Accountant in professional attire, glasses optional. Calculator or laptop, neat stack of papers. Organized, intelligent appearance.",
        "tile": "Clean white platform with subtle grid pattern",
        "vibe": "Numbers, precision, advice"
    },
    "handyman": {
        "description": "Versatile handyman in jeans and work shirt, variety of tools on belt - hammer, screwdriver, pliers. Jack-of-all-trades confident look.",
        "tile": "Weathered wooden platform",
        "vibe": "Versatility, reliability, can-do"
    },
}
```

**UI Integration:**
```svelte
<!-- Role selection with avatars -->
<div class="grid grid-cols-4 gap-4">
  {#each roles as role}
    <button 
      class="p-4 rounded-xl border-2 transition hover:border-blue-500"
      onclick={() => selectRole(role.id)}
    >
      <img 
        src={role.avatar} 
        alt={role.name}
        class="w-24 h-24 mx-auto"
      />
      <div class="text-center mt-2 font-medium">{role.name}</div>
    </button>
  {/each}
</div>
```

**NPC Display:**
```svelte
<!-- NPC participant card -->
<div class="flex items-center gap-3 p-3 bg-slate-800 rounded-lg">
  <img src={npc.avatar} alt={npc.name} class="w-12 h-12" />
  <div>
    <div class="font-medium text-white">{npc.name}</div>
    <div class="text-xs text-slate-400">{npc.role}</div>
  </div>
  <div class="ml-auto text-sm text-green-400">${npc.balance.toLocaleString()}</div>
</div>
```

**Acceptance Criteria:**
- [ ] Avatars generated for all role types
- [ ] Consistent isometric style across all characters
- [ ] Characters stand on appropriate themed tiles
- [ ] Multiple variants available for user selection
- [ ] Avatars used in role selection, NPC cards, and profiles
- [ ] Pre-generated and cached (no runtime generation)

---

## Implementation Sequence

Given hackathon deadline (Feb 9), recommended order:

```
Week 1 (Jan 19-25):
├── Day 1-2: Property Description Generation API
├── Day 3-4: Imagen 3 Integration for Property Images  
├── Day 5-6: Property Detail UI Component
└── Day 7: Integration Testing

Week 2 (Jan 26 - Feb 1):
├── Day 1-2: Bulk Property Generation Script
├── Day 3-4: State Persistence (Database)
├── Day 5-6: Action Processing Logic
└── Day 7: NPC Enhancement

Week 3 (Feb 2-9):
├── Day 1-2: Polish & Bug Fixes
├── Day 3-4: Demo Video Recording
├── Day 5-6: Submission Materials
└── Day 7-8: Buffer / Final Polish
```

---

## Technical Decisions

### Why Batch Processing?

**Problem:** Continuous agent simulation burns tokens rapidly.

**Solution:** Process all events in monthly batches.

**Benefits:**
1. **Token efficiency** - One large call vs. thousands of small calls
2. **Consistency** - All decisions made with full context
3. **Conflict resolution** - Batch can resolve competing orders
4. **Narrative coherence** - Governor sees full picture

**Trade-off:** Less real-time feel, but interactive agents compensate.

### Why SSE for Clock Sync?

**Problem:** Multiple users need synchronized simulation time.

**Solution:** Server-Sent Events from backend clock.

**Benefits:**
1. **One-way stream** - Simpler than WebSockets
2. **Auto-reconnect** - Built into EventSource
3. **HTTP compatible** - Works through proxies
4. **Low overhead** - No polling

### Why Svelte 5 Runes?

**Problem:** Need reactive UI with good performance.

**Solution:** Svelte 5 with runes mode.

**Benefits:**
1. **Fine-grained reactivity** - Only re-render what changes
2. **Simpler mental model** - $state, $derived, $effect
3. **Smaller bundle** - Important for demo
4. **Modern DX** - TypeScript support, HMR

---

## File Structure

```
projects/osf-demo/
├── SPECIFICATION.md          ← This file
├── ARCHITECTURE.md           ← High-level architecture
├── BUSINESS_STRATEGY.md      ← Business/educational positioning
├── DEMO_SCRIPT.md            ← 3-minute demo walkthrough
├── MARKET_CONTEXT.md         ← Australian housing market data
├── SIMULATION_MODE.md        ← Simulation features documentation
├── SUBMISSION.md             ← Hackathon submission content
│
├── backend/
│   ├── requirements.txt
│   ├── data/
│   │   ├── property_pool.json   ← Pre-generated properties
│   │   ├── avatar_pool.json     ← Pre-generated avatars
│   │   └── viewer.html          ← Asset viewer
│   │
│   └── src/
│       ├── main.py              ← FastAPI app, lifespan
│       ├── config.py            ← Settings
│       ├── auth.py              ← JWT auth
│       │
│       ├── ai/
│       │   └── core.py          ← Shared AI capabilities
│       │
│       ├── models/
│       │   ├── network.py       ← SQLAlchemy models
│       │   └── simulation.py    ← Simulation models
│       │
│       ├── repositories/
│       │   ├── participant.py   ← Participant CRUD
│       │   ├── network.py       ← Network state CRUD
│       │   └── property.py      ← Property state CRUD
│       │
│       ├── services/
│       │   ├── network_clock.py     ← Clock service
│       │   ├── batch_processor.py   ← Batch processing
│       │   ├── action_processor.py  ← Action validation/execution
│       │   ├── npc_system.py        ← NPC manager and brain
│       │   ├── event_generator.py   ← Economic events/news
│       │   ├── market_data.py       ← AU housing market data
│       │   └── property_generator.py ← Property generation
│       │
│       ├── middleware/
│       │   └── error_handler.py ← Global error handling
│       │
│       └── api/
│           ├── clock.py         ← Clock endpoints
│           ├── network.py       ← Network/agent endpoints
│           ├── simulation.py    ← Simulation endpoints
│           ├── pool.py          ← Property/avatar pool endpoints
│           ├── participant.py   ← Participant endpoints
│           └── chat.py          ← General chat
│
└── frontend/
    └── src/
        ├── routes/
        │   └── simulate/
        │       └── +page.svelte  ← Main simulation page (all tabs)
        │
        └── lib/
            ├── pool.svelte.ts    ← Pool data store
            └── components/
                ├── NetworkClock.svelte   ← Clock display
                ├── GovernorChat.svelte   ← AI chat
                └── PropertyCard.svelte   ← Property card
```

---

## Contributing

### Adding a New Agent

1. Define the agent's system prompt in `/backend/src/api/network.py`
2. Create an endpoint for the agent
3. Add frontend component if needed
4. Document in this specification

### Adding a New Action Type

1. Add to `action_type` enum in batch processor
2. Update prompt to explain how to process it
3. Add UI for submitting the action
4. Test with clock queue

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-19 | 0.1.0 | Initial specification |
| 2026-01-19 | 0.2.0 | Phase 2-7 completed, Ledger tab, market data integration |
| 2026-01-20 | 0.3.0 | Phase 8 completed: Marathon Agent, Self-Healing (demand + supply), WA dynamics, Community Feedback, Svelte Flow diagrams |
| 2026-01-20 | 0.4.0 | Phase 9 completed: Cooperative Gamification, Achievements, Insight Moments, Floating AI Chat, Onboarding Modal, Connected Roles, Live Charts, Homepage Rewrite |

