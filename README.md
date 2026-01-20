# OSF - Open Shared Futures

> 🏠 **Cooperative Property Ownership** — A simulation of how property tokenization could make ownership accessible to everyone.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/language-seed/osf)
[![Railway](https://railway.app/button.svg)](https://railway.app/template/osf)

**Built by [Language Seed](https://github.com/language-seed)** | **Hackathon Track:** 🧠 Marathon Agent

---

## What if everyone could own property?

Right now in Australia:
- **10.5 years** to save a deposit
- **$196 billion** locked in home equity
- **$13 billion/year** paid to banks in interest

OSF simulates how property tokenization could change this.

---

## Quick Start

```bash
cd projects/osf-demo

# 1. Set your Google API key
export GOOGLE_API_KEY="your-key-here"
# Get one from: https://aistudio.google.com/apikey

# 2. Start backend
cd backend
pip install -r requirements.txt
USE_SQLITE=true uvicorn src.main:app --host 0.0.0.0 --port 8000

# 3. Start frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 to start the simulation.

---

## The Experience

### 6 Roles to Explore

| Role | What You Do |
|------|-------------|
| **Investor** | Buy tokens, track portfolio, earn dividends |
| **Renter** | Select property, pay rent, request maintenance |
| **Tenant** | Rent-to-own pathway, build equity over time |
| **Homeowner** | Access equity without selling, stay in your home |
| **Service Provider** | Complete maintenance tasks, earn fees |
| **Foundation** | Stake tokens, participate in governance |

### Cooperative Focus

Unlike competitive games, OSF rewards:
- **Network Health** — Collective stability over individual gains
- **Families Housed** — Real impact metrics
- **Zero Evictions** — The goal is cooperative, not extractive

### Always-On AI

The Network Governor is always accessible:
- Floating chat button (bottom-right)
- Real-time streaming responses
- Full context of simulation state

---

## Key Features

### Marathon Agent Mode
- 10-year autonomous simulation (120+ months)
- 11 AI NPCs with unique personalities
- Self-correcting behavior based on performance
- Visible reasoning in AI Thinking Log

### Self-Healing Network
- Detects liquidity crises automatically
- Activates recovery mechanisms
- Matches buyers with sellers during stress
- Zero foreclosures, zero evictions

### Cooperative Gamification
- Network Health Report (A-F grade)
- Collective Outcomes tracking
- Exploration Achievements
- Educational Insight Moments

### Connected Roles
- Homeowner equity → Investor tokens
- Cross-role state persistence
- Unified portfolio tracking

---

## Technology

| Layer | Stack |
|-------|-------|
| Frontend | SvelteKit 2.0, Svelte 5, TypeScript, Tailwind |
| Backend | FastAPI, Python 3.11+, SQLAlchemy |
| AI | Gemini 2.0 Flash (streaming), Imagen 3 |
| Real-time | Server-Sent Events (SSE) |
| Data | RBA, ABS, REIWA, PropTrack (Australian markets) |

---

## Deployment

### One-Click Deploy

**Frontend (Vercel):**
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/language-seed/osf&root-directory=projects/osf-demo/frontend)

**Backend (Railway):**
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/osf)

### Manual Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

**Requirements:**
- Gemini API key from [AI Studio](https://aistudio.google.com/apikey)
- Vercel account (frontend)
- Railway account (backend + PostgreSQL)

---

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System design and diagrams |
| [SIMULATION_MODE.md](./SIMULATION_MODE.md) | Simulation features and roles |
| [SPECIFICATION.md](./SPECIFICATION.md) | Technical specification |
| [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) | 3-minute demo walkthrough |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Vercel & Railway deployment guide |
| [VIDEO_EXPLAINER.md](./VIDEO_EXPLAINER.md) | Concept explainer for video |
| [SUBMISSION.md](./SUBMISSION.md) | Hackathon submission content |
| [MARKET_CONTEXT.md](./MARKET_CONTEXT.md) | Australian housing data sources |

---

## Disclaimer

**This is a simulation sandbox — NOT a financial product.**

- No real money, no real assets, no financial advice
- Educational tool for exploring property tokenization concepts
- All data is simulated
- AI triages and recommends; production would require human oversight

---

## License

MIT License - [Language Seed](https://github.com/language-seed)

---

## Credits

- **Built for:** [Gemini 3 Hackathon](https://gemini3.devpost.com/)
- **Organization:** [Language Seed](https://github.com/language-seed)
- **AI Platform:** Google Gemini 2.0 Flash
- **Data Sources:** ABS, RBA, REIWA, PropTrack (Australian markets)
