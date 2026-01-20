# OSF Demo - Architecture

> **Last Updated:** 2026-01-20

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              OSF SIMULATION                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   FRONTEND   │    │   BACKEND    │    │   GEMINI AI  │                   │
│  │  (SvelteKit) │◄──►│  (FastAPI)   │◄──►│   (Google)   │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│         │                   │                   │                            │
│         │              ┌────┴────┐              │                            │
│         │              │         │              │                            │
│         ▼              ▼         ▼              ▼                            │
│  ┌──────────────┐  ┌───────┐  ┌───────┐  ┌──────────────┐                   │
│  │   Browser    │  │SQLite │  │ Pool  │  │   Imagen 3   │                   │
│  │     SSE      │  │  DB   │  │ JSON  │  │   (Images)   │                   │
│  └──────────────┘  └───────┘  └───────┘  └──────────────┘                   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         MARKET DATA SERVICE                           │   │
│  │  • Real Australian housing metrics (RBA, ABS, APRA)                  │   │
│  │  • WA/Perth specific rental yields and vacancy rates                 │   │
│  │  • Calibrates valuations, events, and NPC behavior                   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Two-Phase Processing Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 1: REAL-TIME                                   │
│                      (Between Monthly Ticks)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  User Action ──► Action Processor ──► Validation ──► Database               │
│       │                                                                      │
│       ▼                                                                      │
│  Governor Chat ◄──────────────────────────────────────► Gemini Flash        │
│  Advisor Chat                                           (Low Latency)        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 2: BATCH TICK                                  │
│                    (Once per Simulation Month)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Network Clock Tick                                                          │
│       │                                                                      │
│       ├──► Process DB Actions                                                │
│       │                                                                      │
│       ├──► NPC Decisions ──► Action Processor                                │
│       │         │                                                            │
│       │         └──► Market Maker, Developer, Investors                      │
│       │                                                                      │
│       ├──► Event Generator ──► Economic Cycles, Market Events                │
│       │                                                                      │
│       └──► Batch Processor ─────────────────────────► Gemini Pro             │
│                   │                                   (1M+ Tokens)           │
│                   │                                        │                 │
│                   │◄───────────────────────────────────────┘                 │
│                   │                                                          │
│                   ▼                                                          │
│             Save Snapshot ──► Database                                       │
│                   │                                                          │
│                   ▼                                                          │
│             Broadcast SSE ──► All Clients                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Services

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND SERVICES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐            │
│  │  Network Clock  │   │ Batch Processor │   │ Action Processor│            │
│  ├─────────────────┤   ├─────────────────┤   ├─────────────────┤            │
│  │ • Timer loop    │   │ • State collect │   │ • Buy/Sell      │            │
│  │ • SSE broadcast │   │ • Gemini call   │   │ • Rent payment  │            │
│  │ • Tick trigger  │   │ • Parse results │   │ • Voting        │            │
│  │ • Configurable  │   │ • Governor msg  │   │ • Validation    │            │
│  └────────┬────────┘   └────────┬────────┘   └────────┬────────┘            │
│           │                     │                     │                      │
│           └─────────────────────┼─────────────────────┘                      │
│                                 │                                            │
│                                 ▼                                            │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐            │
│  │   NPC Manager   │   │ Event Generator │   │  Pool Manager   │            │
│  ├─────────────────┤   ├─────────────────┤   ├─────────────────┤            │
│  │ • 11 NPCs       │   │ • Market events │   │ • Properties    │            │
│  │ • Personalities │   │ • Property evts │   │ • Avatars       │            │
│  │ • Goal-driven   │   │ • Economic cycle│   │ • Pre-generated │            │
│  │ • Market maker  │   │ • News articles │   │ • Imagen 3      │            │
│  └─────────────────┘   └─────────────────┘   └─────────────────┘            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │     │  Frontend│     │  Backend │     │  Gemini  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │  Buy Tokens    │                │                │
     ├───────────────►│                │                │
     │                │  POST /action  │                │
     │                ├───────────────►│                │
     │                │                │  Validate      │
     │                │                ├────────┐       │
     │                │                │◄───────┘       │
     │                │                │                │
     │                │  { success }   │                │
     │                │◄───────────────┤                │
     │  Updated UI    │                │                │
     │◄───────────────┤                │                │
     │                │                │                │
     │                │    ─ ─ ─ ─ ─ ─ TICK ─ ─ ─ ─ ─ ─ │
     │                │                │                │
     │                │                │  Batch State   │
     │                │                ├───────────────►│
     │                │                │                │
     │                │                │  AI Response   │
     │                │                │◄───────────────┤
     │                │                │                │
     │                │  SSE: tick     │                │
     │                │◄───────────────┤                │
     │  New Month!    │                │                │
     │◄───────────────┤                │                │
     │                │                │                │
```

## Database Schema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATABASE TABLES                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐    │
│  │   participants  │       │ network_snapshots│       │  network_events │    │
│  ├─────────────────┤       ├─────────────────┤       ├─────────────────┤    │
│  │ id              │       │ id              │       │ id              │    │
│  │ name            │       │ network_month   │       │ network_month   │    │
│  │ role            │       │ total_properties│       │ event_type      │    │
│  │ participant_type│       │ total_valuation │       │ title           │    │
│  │ balance         │       │ avg_yield       │       │ description     │    │
│  │ is_active       │       │ governor_summary│       │ severity        │    │
│  └────────┬────────┘       │ processing_time │       │ property_id     │    │
│           │                └─────────────────┘       └─────────────────┘    │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐    │
│  │participant_hold.│       │ pending_actions │       │ property_state  │    │
│  ├─────────────────┤       ├─────────────────┤       ├─────────────────┤    │
│  │ id              │       │ id              │       │ id              │    │
│  │ participant_id  │       │ participant_id  │       │ pool_property_id│    │
│  │ property_id     │       │ action_type     │       │ status          │    │
│  │ token_amount    │       │ action_data     │       │ total_tokens    │    │
│  │ avg_purchase_   │       │ status          │       │ token_price     │    │
│  │   price         │       │ queued_for_month│       │ weekly_rent     │    │
│  └─────────────────┘       └─────────────────┘       └─────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Gemini Integration Points

| Feature | Model | Context | Purpose |
|---------|-------|---------|---------|
| Batch Processing | gemini-2.0-flash | ~50K tokens | Monthly simulation tick |
| Governor Chat | gemini-2.0-flash | ~10K tokens | Real-time Q&A (streaming) |
| Portfolio Advisor | gemini-2.0-flash | ~5K tokens | Investment guidance |
| Property Listings | gemini-2.0-flash | ~2K tokens | Generate descriptions |
| News Articles | gemini-2.0-flash | ~3K tokens | Monthly summaries |
| Property Images | imagen-3 | N/A | Isometric renders |
| Character Avatars | imagen-3 | N/A | NPC/user avatars |

## Marathon Agent Pattern

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MARATHON AGENT IMPLEMENTATION                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  "Autonomous systems for tasks spanning hours or days"                      │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    THOUGHT SIGNATURE CYCLE                           │    │
│  │                                                                      │    │
│  │   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐        │    │
│  │   │OBSERVATION│──▶│ ANALYSIS │──▶│ DECISION │──▶│  ACTION  │        │    │
│  │   │           │   │          │   │          │   │          │        │    │
│  │   │ Market    │   │ Risk     │   │ Buy/Sell │   │ Execute  │        │    │
│  │   │ Scan      │   │ Assess   │   │ Choice   │   │ Trade    │        │    │
│  │   └──────────┘   └──────────┘   └──────────┘   └────┬─────┘        │    │
│  │                                                      │              │    │
│  │                  ┌───────────────────────────────────┘              │    │
│  │                  ▼                                                  │    │
│  │            ┌──────────┐                                             │    │
│  │            │REFLECTION│ ◄─── Track outcome, adjust strategy         │    │
│  │            │          │                                             │    │
│  │            │ Self-    │ ◄─── Modify risk tolerance if failing       │    │
│  │            │ Correct  │                                             │    │
│  │            └──────────┘                                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    MARATHON MODE EXECUTION                           │    │
│  │                                                                      │    │
│  │   Start ──▶ Auto-tick (2s) ──▶ NPC Decisions ──▶ Log Thinking       │    │
│  │                  │                   │                │              │    │
│  │                  ▼                   ▼                ▼              │    │
│  │            120 months          11 NPCs act      AI Thinking Tab     │    │
│  │            (10 years)          each tick        streams live        │    │
│  │                  │                   │                               │    │
│  │                  └───────────────────┴──────────▶ ~4 hours runtime  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Key Features:                                                               │
│  • Runs autonomously without human supervision                              │
│  • Self-corrects: NPCs adjust strategy based on performance                 │
│  • Visible reasoning: All thoughts logged to AI Thinking tab                │
│  • Session continuity: Tracks elapsed time and total months                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Self-Healing Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OSF SELF-HEALING SYSTEM                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  "What Banks Can't Do — Coordinated Recovery from Network Stress"           │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     SELF-HEALING CYCLE                               │    │
│  │                                                                      │    │
│  │   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐        │    │
│  │   │  SENSE   │──▶│ DIAGNOSE │──▶│ RESPOND  │──▶│  VERIFY  │        │    │
│  │   │          │   │          │   │          │   │          │        │    │
│  │   │ Monitor  │   │ Root     │   │ Activate │   │ Did it   │        │    │
│  │   │ metrics  │   │ cause    │   │ counter- │   │ work?    │        │    │
│  │   │          │   │ analysis │   │ measures │   │          │        │    │
│  │   └──────────┘   └──────────┘   └──────────┘   └────┬─────┘        │    │
│  │        ▲                                             │              │    │
│  │        │              ┌──────────────────────────────┘              │    │
│  │        │              ▼                                             │    │
│  │        │        ┌──────────┐                                        │    │
│  │        └────────│  LEARN   │ ◄─── Improve strategies over time      │    │
│  │                 └──────────┘                                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    HEALTH INDICATORS                                 │    │
│  │                                                                      │    │
│  │   Liquidity    Exit Queue    Trade Failures    Occupancy    Rent    │    │
│  │   ────────     ──────────    ──────────────    ─────────    ────    │    │
│  │    >80%          <5           <15%              >95%        >98%    │    │
│  │   =healthy      =healthy      =healthy         =healthy    =healthy │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    HEALING STRATEGIES                                │    │
│  │                                                                      │    │
│  │   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐          │    │
│  │   │ Liquidity     │  │ Buyer-Seller  │  │ Partial Exit  │          │    │
│  │   │ Pool          │  │ Matching      │  │ Program       │          │    │
│  │   │               │  │               │  │               │          │    │
│  │   │ Deploy floor  │  │ Match sellers │  │ 30% now,      │          │    │
│  │   │ bids from     │  │ with          │  │ 70% over      │          │    │
│  │   │ treasury      │  │ opportunists  │  │ 6 months      │          │    │
│  │   └───────────────┘  └───────────────┘  └───────────────┘          │    │
│  │                                                                      │    │
│  │   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐          │    │
│  │   │ Rent-to-Own   │  │ Tenant        │  │ Cross-Prop    │          │    │
│  │   │ Acceleration  │  │ Support       │  │ Rebalancing   │          │    │
│  │   │               │  │               │  │               │          │    │
│  │   │ Alert tenants │  │ Payment plans │  │ Swap tokens   │          │    │
│  │   │ to buy in     │  │ for stressed  │  │ between       │          │    │
│  │   │ downturn      │  │ tenants       │  │ properties    │          │    │
│  │   └───────────────┘  └───────────────┘  └───────────────┘          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Key Differentiator:                                                        │
│  • Banks can only foreclose or hold                                         │
│  • OSF can coordinate participants to solve problems markets can't          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Supply-Side Self-Healing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SUPPLY SHORTAGE MITIGATION                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  When demand exceeds supply (boom conditions):                              │
│                                                                              │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                   │
│  │ Investor      │  │ Rental        │  │ Buyer         │                   │
│  │ Waitlist      │  │ Waitlist      │  │ Demand Ratio  │                   │
│  │               │  │               │  │               │                   │
│  │ Track buyers  │  │ Track renters │  │ Monitor       │                   │
│  │ wanting in    │  │ seeking homes │  │ pressure      │                   │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘                   │
│          │                  │                  │                            │
│          └──────────────────┼──────────────────┘                            │
│                             ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    SUPPLY STRATEGIES                                 │   │
│  │                                                                      │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐           │   │
│  │  │ Property      │  │ Homeowner     │  │ Vacancy       │           │   │
│  │  │ Sourcing      │  │ Outreach      │  │ Incentive     │           │   │
│  │  │               │  │               │  │               │           │   │
│  │  │ Fast-track    │  │ Contact owners│  │ Encourage     │           │   │
│  │  │ new listings  │  │ in high-demand│  │ rentals to    │           │   │
│  │  │ from pool     │  │ suburbs       │  │ market        │           │   │
│  │  └───────────────┘  └───────────────┘  └───────────────┘           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Community Feedback System

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMMUNITY FEEDBACK ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    NPC FEEDBACK GENERATION                           │   │
│  │                                                                      │   │
│  │  12 Unique Authors with Personalities:                              │   │
│  │  • Conservative (Sarah Chen, Lisa Chang)                            │   │
│  │  • Aggressive (Marcus Thompson)                                     │   │
│  │  • Speculator (Michael Foster)                                      │   │
│  │  • Newbie (NewInvestor42)                                          │   │
│  │  • FIFO Worker (PerthMiner_FIFO)                                   │   │
│  │  • Income-focused (RetiredTeacher)                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                             │                                               │
│                             ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    MARKET-AWARE TEMPLATES                            │   │
│  │                                                                      │   │
│  │  BOOM:     "Auto-invest feature", "More listings needed"           │   │
│  │  STABLE:   "Dividend reinvestment", "Tax report generation"        │   │
│  │  BUST:     "Exit request stuck", "Early warning alerts needed"     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                             │                                               │
│                             ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    GOVERNOR AI RESPONSES                             │   │
│  │                                                                      │   │
│  │  35% of feedback receives automatic Governor response               │   │
│  │  • Questions → Resolved                                              │   │
│  │  • Bugs → In Progress                                                │   │
│  │  • Features → Planned                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                             │                                               │
│                             ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    SENTIMENT TRACKING                                │   │
│  │                                                                      │   │
│  │  Score: -1.0 ──────────────●────────────────────── +1.0             │   │
│  │         Anxious        Neutral              Very Positive           │   │
│  │                                                                      │   │
│  │  Impacts:                                                           │   │
│  │  • Market condition affects baseline                                │   │
│  │  • Resolution rate boosts sentiment                                 │   │
│  │  • Low sentiment triggers self-healing diagnostics                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Cooperative Gamification System

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COOPERATIVE GAMIFICATION ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Philosophy: Reward cooperation and network stability, NOT competition      │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    NETWORK HEALTH REPORT                            │    │
│  │                                                                      │    │
│  │  Overall Grade: A/B/C/D/F based on:                                 │    │
│  │  • Reputation Score (network trust)                                 │    │
│  │  • Occupancy Rate (homes utilized)                                  │    │
│  │  • Sustainable Growth (controlled expansion)                        │    │
│  │  • Crisis Resilience (survived downturns)                           │    │
│  │  • Network Scale (properties in network)                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    COLLECTIVE OUTCOMES                              │    │
│  │                                                                      │    │
│  │  • Families Housed (network providing shelter)                      │    │
│  │  • Dividends Distributed (shared prosperity)                        │    │
│  │  • Equity Accessed (homeowners helped)                              │    │
│  │  • Crises Survived (network resilience)                             │    │
│  │  • Evictions: 0 / Foreclosures: 0 (zero harm)                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    EXPLORATION ACHIEVEMENTS                         │    │
│  │                                                                      │    │
│  │  Unlocked by learning and experiencing, NOT competing:              │    │
│  │  • First Investment, Dividend Received, Weathered Storm             │    │
│  │  • Witnessed Boom, Saw Self-Healing, Explored Roles                 │    │
│  │  • Full Cycle, Long Term Holder, Network Anchor                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    INSIGHT MOMENTS                                  │    │
│  │                                                                      │    │
│  │  Educational popups during marathon simulation:                     │    │
│  │  • Market Boom/Bust explanations                                    │    │
│  │  • Self-Healing activation alerts                                   │    │
│  │  • Property growth notifications                                    │    │
│  │  • Dividend distribution explanations                               │    │
│  │  • Year milestone summaries                                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Frontend Views

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            FRONTEND TABS                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐     │
│  │ Dashboard │ │  Network  │ │Governance │ │Leaderboard│ │ Community │     │
│  │           │ │           │ │           │ │           │ │           │     │
│  │ Portfolio │ │ Partic-   │ │ Proposals │ │ Rankings  │ │ NPC Feed- │     │
│  │ Holdings  │ │ ipants    │ │ Voting    │ │ Metrics   │ │ back +    │     │
│  │ Charts    │ │           │ │           │ │           │ │ Sentiment │     │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘     │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         LEDGER TAB (NEW)                             │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │  • Blockchain-style transaction log                                  │    │
│  │  • All network events with simulated tx hashes                      │    │
│  │  • Block numbers (months), from/to, amounts                         │    │
│  │  • Color-coded transaction types                                     │    │
│  │  • Total volume metrics                                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    AI THINKING TAB (Marathon Agent)                  │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │  • Real-time NPC decision reasoning ("Thought Signatures")          │    │
│  │  • 5 thinking levels: Observation → Analysis → Decision → Action    │    │
│  │  • NPC performance tracking with self-correction                    │    │
│  │  • Marathon Mode controls (start/pause/stop)                        │    │
│  │  • Session duration and total months counter                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    HEALTH TAB (Self-Healing)                         │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │  • Network health metrics (liquidity, exit queue, failures)         │    │
│  │  • Liquidity pool status and deployment history                     │    │
│  │  • Exit queue with seller/buyer matching                            │    │
│  │  • Active healing strategies with progress tracking                 │    │
│  │  • Automatic alerts when health degrades                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    POST-MARATHON SYNOPSIS                            │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │  • Stakeholder outcomes (Investors, Renters, Tenants, Homeowners)   │    │
│  │  • Market journey (boom/bust phases, iron ore range, worst/best)    │    │
│  │  • Self-healing activity (strategies used, exits handled)           │    │
│  │  • Collective outcomes (families housed, dividends, equity accessed)│    │
│  │  • User contribution (capital deployed, network anchor status)      │    │
│  │  • Exploration achievements unlocked during simulation              │    │
│  │  • Live performance charts (network value, token price, user worth) │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    FLOATING AI CHAT                                  │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │  • Persistent floating button (bottom-right)                        │    │
│  │  • Expandable chat panel with Network Governor                      │    │
│  │  • Streaming responses via SSE                                      │    │
│  │  • Always accessible during simulation                              │    │
│  │  • Minimizable/closable                                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    ONBOARDING MODAL                                  │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │  First-time user experience:                                        │    │
│  │  • Quick Demo (2-minute overview, 24 months at fast speed)          │    │
│  │  • Full Marathon (10-year simulation, configurable speed)           │    │
│  │  • Dismissable, remembers preference in localStorage                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      ROLE-SPECIFIC PANELS                            │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │  Investor  │  Renter   │  Tenant  │ Homeowner │ Service  │Foundation│    │
│  │  ─────────  ─────────   ────────   ─────────   Provider   ──────────│    │
│  │  • Buy/sell │ • Select  │ • Rent-  │ • Property│ • Tasks   │ • Stake │    │
│  │  • Portfolio│   property│   to-own │   listing │ • History │ • Yields│    │
│  │  • Auto-inv │ • Pay rent│ • Equity │ • Equity  │ • Per-prop│ • Govern│    │
│  │  • Charts   │ • Maint.  │ • Miles. │   access  │   tracking│ • Votes │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    CONNECTED STATE (Cross-Role)                      │    │
│  ├─────────────────────────────────────────────────────────────────────┤    │
│  │  Homeowner → Investor Connection:                                   │    │
│  │  • Equity accessed as Homeowner creates tokens                      │    │
│  │  • Tokens appear in Investor holdings (marked "Your Home Equity")   │    │
│  │  • Link from Homeowner view to Investor view                        │    │
│  │  • Unified portfolio tracks all token sources                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | SvelteKit 2.0, Svelte 5 Runes, TypeScript, Tailwind CSS |
| UI Components | shadcn-svelte, Lucide icons, Chart.js, Svelte Flow |
| Interactive Diagrams | @xyflow/svelte (Money Flow, Self-Healing Cycle) |
| Backend | FastAPI, Python 3.11+, SQLAlchemy 2.0, aiosqlite |
| Database | SQLite (demo) / PostgreSQL (production) |
| AI | Google Gemini 2.0 Flash (streaming), Imagen 3 |
| Real-time | Server-Sent Events (SSE) for clock sync and AI chat |
| Market Data | RBA, ABS, APRA, REIWA, PropTrack (Australian housing metrics) |
| Gamification | Cooperative achievements, insight moments, network health |
| Deployment | Docker, uvicorn |
