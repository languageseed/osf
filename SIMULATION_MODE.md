# OSF Simulation Mode

## Overview

OSF Simulation is an educational sandbox that allows users to explore property tokenization concepts without any financial risk. This is the core product for the Gemini 3 Hackathon submission.

> **⚠️ Important Disclaimer**
> 
> This is a **simulation sandbox** - not a financial product.
> - No real money
> - No real assets
> - No financial advice
> 
> OSF Simulation is an educational tool for exploring property tokenization, governance mechanics, and AI-assisted insights.

---

## Why Simulation First?

### Strategic Positioning

| Approach | Benefits |
|----------|----------|
| **Educational Sandbox** | Low regulatory burden |
| **Risk-Free Exploration** | Users engage without financial anxiety |
| **Community Building** | Feedback loop improves product |
| **Concept Validation** | Prove value before real implementation |

### What Users Learn

1. **Token Economics** - How property tokens are priced and traded
2. **Governance Mechanics** - How DAO voting and proposals work
3. **Multi-Stakeholder Systems** - How investors, homeowners, renters, and service providers interact
4. **AI-Assisted Operations** - How AI can triage, recommend, and automate

---

## Simulation Features

### 1. Simulated Portfolio

**Starting Balance:** $100,000 simulated AUD

| Feature | Implementation |
|---------|---------------|
| Token Purchase | Instant, client-side state |
| Token Sale | Instant, client-side state |
| Portfolio Value | Tracks based on holdings |
| Yields | Simulated on "Simulate Month" |
| Transaction History | Full history with role-specific transaction types |
| Auto-Invest | Recurring monthly investments |
| Projection Calculator | Interactive chart with adjustable parameters |

### Token Model (AUD-Denominated)

OSF tokens are **not a currency**. They represent **fractional equity exposure**
to AUD-valued property in the simulation.

**Key rules:**
- Tokens are **AUD-denominated** and track property valuation
- Valuations update based on simulated market demand and comparable sales
- Redemption means **selling tokens for AUD balance** inside the simulation
- **No fixed peg** (tokens move with property valuations)

**Pricing formula (simulation):**
```
token_price = property_valuation_aud / total_tokens_issued
```

**Risk allocation (simulation):**
- Borrowing against equity assumes higher future market value
- Investors take market risk when buying tokens
- OSF facilitates matching; liquidity is **not guaranteed**
- Owner control threshold: normally **<=49%** can be tokenized while the owner
  retains control and occupancy. Tokenizing more implies a change in living
  arrangement (tenant with intent to buy back, or renter).

### Valuation Method (Simulation)

- Updates at each monthly tick
- Driven by comparable sales, market demand, and macro state
- Includes uncertainty; values can move both up and down

### Liquidity & Matching

- OSF **matches buyers and sellers** in the simulation
- If no buyers exist, sales can be delayed or partial
- Market‑maker NPCs provide limited liquidity and spreads

### Token Supply & Redemption

- Tokens are **minted** when equity is tokenized
- Tokens are **burned** when equity is bought back or exited
- Redemption = **sell tokens for AUD balance** in the simulation

### Rights vs Obligations

- Token holders receive **price exposure** and **governance participation**
- Token holders **do not** receive tenancy or occupancy rights
- Homeowners remain responsible for maintenance and occupancy choices

### Fees & Friction (Simulated)

- Buy/sell fees
- Management fee on holdings
- Service and maintenance costs reduce net returns

### Financial Distress Pathways

- If a household needs to exceed 49% tokenization, living arrangements change
  (tenant with intent to buy back, or renter)
- The simulation reflects this as a trade‑off between liquidity and control

### 2. All Roles Explorable

Users can switch between all roles to understand the full ecosystem:

| Role | Simulation Experience |
|------|----------------------|
| **Investor** | Buy/sell tokens, track returns, vote, auto-invest |
| **Renter** | Select property, pay rent, request maintenance, swap properties |
| **Tenant** | Rent-to-own pathway, equity accumulation, milestones |
| **Homeowner** | Equity access, rental income toggle, buyback |
| **Service Provider** | Complete diverse tasks, earn fees |
| **Foundation** | Stake tokens, enhanced yields, governance |

### 3. Transaction Logs for All Roles

Each role maintains a dedicated activity log:

**Investor Transactions:**
- Buy/sell tokens
- Dividends received
- Auto-invest executions
- Fees paid

**Renter Transactions:**
- Lease signing/ending
- Bond deposit
- Weekly rent payments
- Inspections
- Maintenance requests

**Tenant Transactions:**
- Monthly payments
- Equity credits
- Ownership milestones
- Maintenance

**Homeowner Transactions:**
- Equity access
- Rental income
- Equity buyback
- Valuation updates

**Service Provider Transactions:**
- Task completions
- Inspections conducted
- Fees collected
- New properties added

**Foundation Transactions:**
- Stakes made
- Yields earned
- Governance participation
- Withdrawals

### 4. Service Provider Types

The Service Provider role (formerly "Custodian") now represents all service types:

| Service Type | Example Tasks |
|--------------|--------------|
| Property Manager | Routine inspections, tenant enquiries |
| Strata Manager | AGM preparation, strata meetings |
| Plumber | Plumbing repairs |
| Electrician | Electrical inspections |
| Legal Advisor | Lease renewal reviews |
| Accountant | Strata levy audits |
| Building Inspector | Building compliance checks |

### 5. Simulated Governance (Sandbox DAO)

| Feature | Implementation |
|---------|----------------|
| Proposal Creation | Anyone can propose |
| Voting | Weighted by simulated holdings |
| Discussion | View proposal details |
| Status Tracking | Active → Passed/Rejected |

### 6. Community Feedback System

| Feature | Implementation |
|---------|----------------|
| Bug Reports | Submit with title/description |
| Feature Requests | Submit with title/description |
| AI Triage | Automatic categorisation |
| Voting | Upvote/downvote |
| Comments | Community discussion |
| Status | open → triaged → planned → completed |

### 7. Portfolio Projection Calculator

**User Controls:**
- Expected yield rate (slider: 0-15%)
- Monthly contribution amount
- Time horizon (1-30 years)
- Auto-invest toggle

**Chart Output:**
- Interactive Chart.js visualisation
- Shows projected value over time
- Recalculates on parameter change

### 8. Leaderboard

| Feature | Implementation |
|---------|----------------|
| Ranking | By portfolio return % |
| Display | Username, return %, days active |
| Updates | Real-time based on trades |

### 9. Network Ledger (Blockchain Log)

| Feature | Implementation |
|---------|----------------|
| Transaction Log | All network events in table format |
| Block Numbers | Mapped to simulation months |
| Tx Hashes | Simulated hexadecimal transaction IDs |
| Types | Color-coded (rent, dividends, trades, etc.) |
| From/To | Source and destination roles |
| Amounts | Green for positive, red for negative |
| Volume Metrics | Total transactions, total volume |
| Live Status | Real-time updates as events occur |

### 10. Property-Linked Service Transactions

| Feature | Implementation |
|---------|----------------|
| Task Assignment | Each service task linked to specific property |
| Property Display | Thumbnails and addresses in task list |
| Service History | Per-property service history in detail view |
| Cost Tracking | Service costs tracked per property |
| Activity Log | Full transaction log with property context |

---

## Technical Implementation

### Frontend State Management

The simulation uses Svelte 5 runes for reactive state:

```typescript
// Core simulation state
let balance = $state(100000);
let holdings = $state<Holding[]>([]);
let activeRole = $state<SimRole>('investor');

// Role-specific transaction logs
let investorTransactions = $state<InvestorTx[]>([]);
let renterTransactions = $state<RenterTx[]>([]);
let tenantTransactions = $state<TenantTx[]>([]);
let homeownerTransactions = $state<HomeownerTx[]>([]);
let custodianTransactions = $state<CustodianTx[]>([]);
let foundationTransactions = $state<FoundationTx[]>([]);
```

### State Persistence

```typescript
// Save to localStorage
$effect(() => {
  localStorage.setItem('osf_sim_state', JSON.stringify({
    balance,
    holdings,
    // ... other state
  }));
});

// Load on mount
onMount(() => {
  const saved = localStorage.getItem('osf_sim_state');
  if (saved) {
    const state = JSON.parse(saved);
    balance = state.balance;
    // ... restore state
  }
});
```

### Backend API (Demo Mode)

```python
# In-memory storage for demo
sim_users: Dict[str, dict] = {}
sim_holdings: Dict[str, List[dict]] = {}
sim_transactions: Dict[str, List[dict]] = {}

# Reset with cooldown
@router.post("/reset/{user_id}")
async def reset_account(user_id: str):
    # 24-hour cooldown enforcement
    if cooldown_active:
        raise HTTPException(status_code=429, ...)
    # Reset to $100K
    user["balance_aud"] = 100000.00
```

---

## User Journey

### Onboarding Flow

```
1. Landing Page
   "Property tokenization, simulated"
   [Start Simulation] [How it Works]
   
2. Simulation Dashboard
   - Role selector (Investor, Renter, Tenant, Homeowner, Service Provider, Foundation)
   - Starting balance: $100,000
   - Tutorial prompts (optional)
   
3. Role-Specific Experience
   - Investor: Buy tokens, track portfolio
   - Renter: Select property, pay rent
   - Etc.
   
4. Governance & Feedback
   - Vote on proposals
   - Submit feature requests
   - Engage with community
```

### Key User Actions

| Action | How It Works |
|--------|-------------|
| Switch Roles | Click role tab in simulation dashboard |
| Buy Tokens | Select property → Enter amount → Confirm |
| Simulate Time | Click "Simulate Month/Week" → Events fire |
| Vote | Go to Governance tab → Select proposal → Vote |
| Submit Feedback | Go to Feedback tab → Submit bug/feature |

---

## Implementation Status

### ✅ Completed Features

| Feature | Status |
|---------|--------|
| Simulation dashboard | ✅ Complete |
| Investor role | ✅ Complete with transactions |
| Renter role | ✅ Complete with property images & swap |
| Tenant (rent-to-own) | ✅ Complete with equity tracking & property selection |
| Homeowner role | ✅ Complete with property listing & equity access |
| Service Provider role | ✅ Complete with property-linked transactions |
| Foundation role | ✅ Complete with staking |
| Governance tab | ✅ Complete with voting |
| Leaderboard tab | ✅ Complete |
| Feedback tab | ✅ Complete with AI triage |
| **Ledger tab** | ✅ **Complete with blockchain-style tx log** |
| Transaction logs (all roles) | ✅ Complete |
| Portfolio projection chart | ✅ Complete with adjustable parameters |
| Investment distribution chart | ✅ Complete |
| Auto-invest | ✅ Complete |
| Simulation time controls | ✅ Complete |
| Reset cooldown | ✅ Complete (24h) |
| Simulation branding | ✅ Complete |
| Disclaimer banners | ✅ Complete |
| Property images (isometric) | ✅ Complete with Imagen 3 |
| WA market dynamics (boom/bust) | ✅ Iron ore, population, 5 market conditions |
| Self-healing system | ✅ Liquidity pool, buyer matching, partial exits |
| Post-marathon synopsis | ✅ Stakeholder outcomes, market journey, counterfactual |
| Character avatars | ✅ Complete with role-based display |
| Property detail dialog | ✅ Complete with Services tab |
| Market data calibration | ✅ Complete with real AU metrics |
| **Cooperative Gamification** | ✅ **Network health, collective outcomes, achievements** |
| **Exploration Achievements** | ✅ **10 achievements tracking learning progress** |
| **Insight Moments** | ✅ **Educational popups during simulation** |
| **Floating AI Chat** | ✅ **Persistent Network Governor access** |
| **Onboarding Modal** | ✅ **Quick Demo / Full Marathon options** |
| **Homeowner-Investor Link** | ✅ **Equity access creates investor holdings** |
| **Live Performance Charts** | ✅ **Real-time SVG charts during marathon** |
| **Dynamic Property Portfolio** | ✅ **Properties enter/exit based on conditions** |

### 🔄 Demo Implementation Notes

> **Important:** The simulation dashboard is **frontend-driven** by design. While backend API endpoints exist (`/api/v1/sim/*`), the main simulation uses client-side `$state` + `localStorage` for instant responsiveness. This is intentional for the hackathon demo.

| Area | Implementation |
|------|----------------|
| State Management | Frontend: `$state` runes + `localStorage` |
| User IDs | Client-generated (no server auth) |
| Persistence | `localStorage` (per-browser, clears on reset) |
| Backend APIs | Available but optional for demo |
| Real-time sync | Not implemented (single-browser session) |
| Multi-device | State not synced across devices |

---

## Cooperative Gamification (NEW)

OSF uses **cooperative gamification** that rewards network health and exploration rather than individual competition.

### Philosophy

| Traditional Games | OSF Approach |
|-------------------|--------------|
| Beat other players | Contribute to network health |
| Maximize personal wealth | Support collective outcomes |
| Individual rankings | Network health grade |
| Competitive leaderboards | Exploration achievements |

### Network Health Report

At the end of each marathon, users see a Network Health grade (A-F) based on:

| Metric | What It Measures |
|--------|------------------|
| Reputation Score | Network trust and stability |
| Occupancy Rate | Homes being utilized |
| Sustainable Growth | Controlled expansion |
| Crisis Resilience | Surviving downturns |
| Network Scale | Properties in network |

### Collective Outcomes

The marathon synopsis highlights what the NETWORK achieved:

| Outcome | Description |
|---------|-------------|
| Families Housed | Number of families with stable housing |
| Dividends Distributed | Total shared with token holders |
| Equity Accessed | Amount homeowners could access |
| Crises Survived | Market downturns weathered |
| Evictions | Always 0 (OSF prevents this) |
| Foreclosures | Always 0 (cooperative model) |

### User Contribution

Instead of "beating" others, users see how they helped:

| Contribution | Description |
|--------------|-------------|
| Capital Deployed | Amount invested in network |
| Stability Score | Held during downturns |
| Network Anchor | Contributed to resilience |
| Contribution Title | "Founding Investor", "Network Anchor", etc. |

### Exploration Achievements

Unlocked by learning and experiencing:

| Achievement | How to Unlock |
|-------------|---------------|
| First Investment | Make your first token purchase |
| Dividend Received | Earn a dividend payment |
| Weathered Storm | Hold during a market downturn |
| Witnessed Boom | Experience a boom market |
| Saw Self-Healing | Watch the network recover |
| Explored Roles | Try 3+ different roles |
| Full Cycle | Complete a full boom-bust cycle |
| Long Term Holder | Stay invested for 5+ years |
| Network Anchor | Maintain holdings during crisis |
| Community Builder | Contribute to network growth |

### Insight Moments

Educational popups appear during marathon simulation:

| Insight | When It Appears |
|---------|-----------------|
| Market Boom | When market enters boom phase |
| Market Bust | When market enters bust phase |
| Self-Healing Active | When network recovery triggers |
| Property Growth | When new property joins network |
| Dividend Paid | When dividends are distributed |
| Year Milestone | Every 12 simulated months |

---

## Onboarding Experience (NEW)

### First-Time Users

New users see an onboarding modal with two options:

| Option | Duration | Speed | Best For |
|--------|----------|-------|----------|
| Quick Demo | ~2 minutes | Fast (100ms/tick) | Judges, first impressions |
| Full Marathon | ~4 hours | Normal (2s/tick) | Deep exploration |

### Onboarding Flow

```
1. User arrives at /simulate
2. Check localStorage for previous visit
3. If first visit → Show onboarding modal
4. User chooses Quick Demo or Full Marathon
5. Simulation starts with chosen settings
6. User can always restart or change speed
```

---

## Connected Roles (NEW)

### Homeowner → Investor Connection

When a homeowner accesses equity, their holdings now appear in the investor view:

| Action | Result |
|--------|--------|
| Homeowner accesses $50K equity | Receives OSF tokens |
| Tokens added to holdings | Marked "Your Home Equity" |
| Switch to Investor view | See combined portfolio |
| Tokens earn dividends | Just like regular investments |

### Cross-Role Benefits

| From Role | To Role | What Transfers |
|-----------|---------|----------------|
| Homeowner | Investor | Equity → Tokens |
| Tenant | Investor | Accumulated equity → Tokens |
| Foundation | All | Governance influence |

---

## Floating AI Chat (NEW)

### Always-On Governor

The Network Governor is now accessible via a floating chat button:

| Feature | Description |
|---------|-------------|
| Location | Bottom-right corner |
| State | Minimized button or expanded panel |
| Streaming | Real-time response via SSE |
| Context | Full simulation state awareness |

### Suggested Prompts

- "How is the network performing?"
- "What properties are available?"
- "Explain how dividends work"
- "What should I invest in?"

---

## Engagement Mechanics

### Exploration Focus

Rather than competitive rankings, OSF tracks:

| What We Track | Why |
|---------------|-----|
| Roles explored | Learning breadth |
| Achievements unlocked | Understanding depth |
| Time in simulation | Engagement |
| Insights seen | Educational value |

### No Competitive Leaderboard

OSF intentionally avoids:
- Player-vs-player rankings
- "Beat the market" messaging
- Wealth accumulation as primary goal
- FOMO-inducing mechanics

---

## Feedback Collection

### In-App Feedback

| Feature | Implementation |
|---------|----------------|
| Bug reports | Title + description form |
| Feature requests | Title + description form |
| Voting | Upvote/downvote buttons |
| Comments | Threaded discussion |
| AI Triage | Automatic categorisation |

### DAO-Driven Development

| Mechanism | How It Works |
|-----------|--------------|
| Feature Proposals | Users propose, community votes |
| Bug Bounties | Report bugs, earn recognition |
| Governance Testing | Test proposal mechanics safely |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Users think sim is real | Clear "SIMULATION" banners everywhere |
| Regulatory concerns | Explicit disclaimers, no financial advice |
| Misleading claims | Educational framing throughout |
| Data collection concerns | Minimal data, transparency |

---

## Success Metrics

### Engagement

| Metric | Target |
|--------|--------|
| Roles explored per user | 3+ |
| Simulation trades | 5+ per user |
| Governance votes cast | 200+ total |
| Feedback items | 50+ |

### Learning

| Metric | Target |
|--------|--------|
| Multi-role exploration | 40%+ users |
| Time in simulation | 5+ minutes avg |
| Return visits | 30%+ |

---

## Marketing Messaging

### Primary Message

```
"Learn property tokenization by playing, not paying."
```

### Key Points

- $100K simulated portfolio
- All roles explorable
- AI-powered insights
- Governance sandbox
- No real money required

### Disclaimers (Always Visible)

- 🎮 **Simulation Mode** — No real money, no real assets, no financial advice.
- This is an educational sandbox for exploring property tokenization.
- Not a licensed financial product.

---

## Conclusion

OSF Simulation transforms complex property tokenization concepts into an accessible, interactive learning experience. By focusing on simulation rather than real transactions, we:

1. **Lower barriers** - Anyone can explore without risk
2. **Build community** - Users become invested in the concept
3. **Gather feedback** - Real usage informs development
4. **Demonstrate value** - Show what AI-assisted property investment could look like
5. **Avoid regulatory complexity** - Educational framing, clear disclaimers
6. **Provide transparency** - Network Ledger shows all transactions

**Key Insight:** Every simulation user is a potential advocate. Treat them accordingly.
