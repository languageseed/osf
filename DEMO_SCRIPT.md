# OSF Demo Script (~3 minutes)

## Setup (Before Recording)
```bash
# Terminal 1: Start backend
cd projects/osf-demo/backend
USE_SQLITE=true uvicorn src.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd projects/osf-demo/frontend
npm run dev
```

---

## Demo Flow

### 0:00-0:20 - Introduction & Problem Statement
**Script:**
> "What if everyone could own property? Right now, it takes 10.5 years to save a deposit in Australia. $196 billion sits locked in home equity. OSF is an AI-powered simulation that demonstrates how property tokenization could change this."

**Show:** Homepage with problem statement (10.5 years, $196B locked, $13B/year to banks)

---

### 0:20-0:40 - Onboarding Experience
**Script:**
> "New users see this onboarding modal. They can choose a Quick Demo for a 2-minute overview, or dive into a full 10-year marathon simulation."

**Actions:**
1. Click "Try the Simulation"
2. Show the onboarding modal with Quick Demo / Full Marathon options
3. Explain: "The Quick Demo runs 24 months at high speed—perfect for judges."

---

### 0:40-1:10 - Role Exploration
**Script:**
> "Users can experience property from 6 different perspectives—not just as investors, but as renters, tenants building equity, homeowners accessing their wealth, service providers, and foundation partners."

**Actions:**
1. Show the role selector tabs
2. Click through Investor → Homeowner briefly
3. Highlight: "Each role has its own dashboard, transactions, and experience."

---

### 1:10-1:40 - Homeowner-Investor Connection
**Script:**
> "Here's something unique: when a homeowner accesses equity, they receive OSF tokens. Watch—I'll access $50,000 of equity..."

**Actions:**
1. Switch to Homeowner role
2. Select a property and list on network
3. Access equity (click the equity access button)
4. Show the purple notice: "View as Investor"
5. Switch to Investor role
6. Point out the holding marked "Your Home Equity"
7. Explain: "The roles are connected. Your home equity is now working for you."

---

### 1:40-2:00 - Floating AI Chat
**Script:**
> "The AI Network Governor is always accessible. Users can ask questions about properties, market conditions, or investment strategies at any time."

**Actions:**
1. Click the floating chat button (bottom-right)
2. Type: "How is the network performing?"
3. Wait for streaming response
4. Highlight: "Powered by Gemini, with full context of the simulation state."

---

### 2:00-2:20 - Marathon Mode & Live Charts
**Script:**
> "The Marathon Mode demonstrates our 'Marathon Agent' approach—autonomous simulation running for hours. Live charts track performance in real-time."

**Actions:**
1. Start Marathon Mode (or show it running)
2. Point to live performance charts (network value, token price, user net worth)
3. Show the market condition indicator
4. Explain: "This can run for 10 simulated years autonomously."

---

### 2:20-2:40 - Cooperative Gamification
**Script:**
> "Unlike competitive games, OSF rewards cooperation. The focus is on collective outcomes—families housed, dividends distributed, crises survived—not beating other players."

**Actions:**
1. Show an achievement toast popping up (if timing works)
2. Or show the marathon synopsis with:
   - Collective Outcomes section
   - Network Health grade
   - "Your Contribution" section
3. Highlight: "Zero evictions, zero foreclosures—that's the goal."

---

### 2:40-2:55 - Architecture Highlight
**Script:**
> "What makes this unique is the two-phase processing model—real-time chat with Gemini streaming, monthly batch processing for the full simulation. Real Australian market data calibrates everything."

**Show:** Brief flash of Network tab or mention Market Context

---

### 2:55-3:00 - Closing
**Script:**
> "OSF demonstrates that Gemini's context window enables fundamentally different application architectures. This isn't a chatbot wrapper—it's an autonomous, self-healing property network simulation. Thank you."

---

## Key Points to Emphasize

1. **Not a wrapper** - Deep simulation logic with emergent behavior and self-healing
2. **Cooperative focus** - Rewards network health, not individual competition
3. **Connected roles** - Homeowner equity flows to investor holdings
4. **Always-on AI** - Floating chat available throughout the experience
5. **Marathon Agent** - Hours of autonomous operation with visible reasoning
6. **Real data** - Calibrated to Australian housing market metrics

---

## Backup Demos (If Time)

### Trigger a Manual Tick
```bash
curl -X POST http://localhost:8000/api/v1/network/clock/tick
```

### Test AI Chat
```bash
curl "http://localhost:8000/api/v1/network/governor/chat/stream?message=How%20is%20the%20network%20performing?"
```

### View NPC List
```bash
curl http://localhost:8000/api/v1/network/npcs
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check `GOOGLE_API_KEY` is set |
| No properties showing | Run pool generator script |
| Clock not ticking | Check preset isn't "paused" |
| Images not loading | Verify pool JSON files exist |
| AI chat not responding | Check model is `gemini-2.0-flash` in config |
| Onboarding not showing | Clear localStorage or use incognito |
