# OSF Demo - Gemini 3 Hackathon Submission

## Project Title
**OSF: AI-Powered Cooperative Property Network Simulation**

## Gemini Integration Description (~200 words)

OSF leverages Gemini's capabilities through a novel **Two-Phase Processing Architecture** that maximizes efficiency while enabling real-time interactivity.

**Phase 1 (Real-Time):** The "Network Governor" AI is always accessible via a floating chat interface, providing market insights and investment guidance using Gemini 2.0 Flash with streaming SSE responses. Users can ask questions anytime during the simulation.

**Phase 2 (Batch Processing):** Each simulation month, the entire network state—properties, participants, pending actions, economic conditions, and NPC decisions—is compiled into a comprehensive prompt. Gemini processes this to generate narrative events, update market dynamics, and produce the Governor's monthly summary.

**Visual Generation:** Imagen 3 pre-generates isometric property renders and character avatars, creating a cohesive visual identity.

**Cooperative Intelligence:** Unlike competitive simulations, OSF uses AI to track and reward network health, collective outcomes (families housed, dividends distributed), and individual contributions to stability. The AI Governor explains market conditions through "Insight Moments"—educational popups during marathon simulation.

**Marathon Agent:** Eleven AI-driven NPCs with distinct personalities make autonomous decisions each tick, running for 10+ simulated years without human supervision. NPCs self-correct based on performance tracking.

The architecture demonstrates that Gemini enables fundamentally different application designs—batching what would traditionally require hundreds of separate calls into single, coherent requests.

---

## Track
**Marathon Agent** - Autonomous simulation spanning hours with:
- **Thought Signatures**: NPCs follow Observation → Analysis → Decision → Action → Reflection cycle
- **Self-Correction**: NPCs adjust risk tolerance based on past performance without human supervision
- **Multi-Step Continuity**: 120+ months of autonomous simulation with persistent state
- **Cooperative Focus**: Network health and collective outcomes, not competition

## Key Features

### Marathon Agent Core
- **Marathon Mode**: Autonomous simulation running for hours (120+ months at 2s/tick = ~4 hours)
- **AI Thinking Log**: Real-time visibility into NPC decisions with Thought Signatures
- **Self-Correction**: NPCs adjust strategy based on performance without human intervention
- **Session Continuity**: Tracks elapsed time and total months simulated
- **Post-Marathon Synopsis**: Comprehensive summary with collective outcomes, network health grade, and user contribution

### Cooperative Gamification (NEW)
- **Network Health Report**: A-F grade based on reputation, occupancy, growth, resilience
- **Collective Outcomes**: Families housed, dividends distributed, equity accessed, crises survived
- **User Contribution**: Track how each user helped the network (capital deployed, stability during downturns)
- **Exploration Achievements**: 10 achievements for learning milestones (not competition)
- **Insight Moments**: Educational popups during simulation explaining market conditions
- **Zero Harm Goals**: Evictions = 0, Foreclosures = 0 (cooperative model)

### User Experience (NEW)
- **Floating AI Chat**: Always-accessible Network Governor via bottom-right button
- **Onboarding Modal**: Quick Demo (2 min) vs Full Marathon (4 hours) options for first-time users
- **Connected Roles**: Homeowner equity access creates investor holdings ("Your Home Equity" badge)
- **Live Performance Charts**: Real-time SVG charts showing network value, token price, user net worth

### Simulation Features
- **WA Boom-Bust Dynamics**: Iron ore prices and population drive 5 market conditions (boom → bust)
- **Self-Healing Network**: Autonomous detection and recovery from liquidity crises
  - Liquidity pool with floor bids
  - Buyer-seller matching during distress
  - Partial exit programs
  - Rent-to-own acceleration in downturns
- 11 goal-driven NPC participants with diverse personalities
- Economic cycle simulation (5 phases with transitions)
- **Property values can DECLINE** - not just grow (realistic WA volatility)
- **Dynamic property portfolio**: Properties enter/exit based on network conditions
- Real-time AI chat agents (Governor, Portfolio Advisor)
- Pre-generated visual assets (Imagen 3)
- Full state persistence with SQLite
- **Network Ledger with blockchain-style transaction log**
- Real Australian market data calibration (RBA, ABS, REIWA, PropTrack)
- 6 explorable roles with complete transaction histories

## Demo Video Highlights
1. **Homepage**: Problem statement (10.5 years to save, $196B locked)
2. **Onboarding Modal**: Quick Demo vs Full Marathon choice
3. **Role Switching**: Investor ↔ Homeowner connection
4. **Homeowner Equity Access**: Creates tokens visible in Investor view
5. **Floating AI Chat**: Ask the Governor about market conditions
6. **Marathon Mode with Live Charts**: Real-time performance tracking
7. **Cooperative Synopsis**: Network health, collective outcomes, achievements
8. **Insight Moments**: Educational popups explaining market events

## Technical Innovation

### Cooperative Gamification
- **Philosophy**: Reward network health and cooperation, not competition
- **Network Health**: Composite grade from reputation, occupancy, growth, resilience
- **Collective Outcomes**: Focus on what the NETWORK achieved together
- **Achievement System**: Unlock by exploring and learning, not by beating others

### Marathon Agent Implementation
- **Autonomous Multi-Hour Execution**: Marathon Mode runs 120+ simulation months without human supervision
- **Thought Signatures**: Every NPC decision follows Observation → Analysis → Decision → Action → Reflection
- **Self-Correction Without Supervision**: NPCs track success rates and adjust risk tolerance automatically
- **Visible Reasoning**: AI Thinking tab shows real-time thought stream from all agents

### Architecture
- Two-phase processing maximizes context window utilization
- Single batch call replaces hundreds of individual requests
- Emergent market dynamics from NPC goal systems
- Real-time SSE synchronization for clock and chat
- Market Data Service calibrates simulation to real AU housing metrics
- Connected role state (homeowner equity → investor holdings)

## Links
- **Repository:** [GitHub URL]
- **Live Demo:** [Demo URL]
- **Video:** [Video URL]

---

## Judging Criteria Alignment

### Technical Execution (40%)
- Clean Python/FastAPI backend with SQLAlchemy ORM
- TypeScript/SvelteKit frontend with Svelte 5 Runes
- Comprehensive API with 40+ endpoints
- Database persistence with repository pattern
- Streaming SSE for real-time AI chat
- Error handling and structured logging

### Innovation/Wow Factor (30%)
- Novel two-phase processing architecture
- Emergent NPC market dynamics with self-correction
- Cooperative gamification (not competitive)
- Connected cross-role state
- NOT a wrapper—deep simulation logic with self-healing

### Potential Impact (20%)
- Educational tool for understanding property investment
- Demonstrates fractional ownership concepts
- Models cooperative network behavior
- Applicable to financial literacy and simulation gaming

### Presentation/Demo (10%)
- Clear architecture diagrams
- Intuitive onboarding flow
- Problem-solution narrative on homepage
- Comprehensive documentation
