# OSF Simulation - Market Context (Australia)

> Simulation-only context. No real money, no financial advice.

This page provides a neutral, source-based snapshot of Australia's housing
debt and housing market. It is intended for educational context within the
OSF Simulation sandbox.

## Key Metrics (Latest Available)

### Household Debt Burden (RBA)
- Household debt-to-income: ~182% (Q2 2025)
- Housing debt-to-income: ~134% (Q2 2025)
Source: RBA Statistical Table E2 (Household Finances - Selected Ratios),
via DBnomics mirror.
https://db.nomics.world/RBA/E2

### Mortgage Credit Growth (APRA, stock of credit)
- Residential mortgage credit: +4.7% y/y (Sep 2024)
- Owner-occupier credit: +5.2% y/y (Sep 2024)
- Investor credit: +4.7% y/y (Sep 2024)
Source: APRA ADI Property Exposure Statistics (Sep 2024 highlights).
https://www.apra.gov.au/quarterly-authorised-deposit-taking-institution-property-exposure-statistics-highlights-2

### New Lending Commitments (ABS, flow of new loans)
- Total loan commitments for dwellings: +5.8% y/y (Sep Q 2025)
- Owner-occupier: +1.7% y/y (number), +9.8% y/y (value)
- Investor: +12.3% y/y (number), +18.7% y/y (value)
Source: ABS Lending Indicators (latest release).
https://www.abs.gov.au/statistics/economy/finance/lending-indicators/latest-release

### Dwelling Values (ABS, stock of dwellings)
- Total value of residential dwellings: AUD $11,564.0 billion (Jun Q 2025)
- Number of dwellings: ~11,373,900 (Jun Q 2025)
- Mean dwelling price: AUD $1,016,700 (Jun Q 2025)
Source: ABS Total Value of Dwellings (Jun Quarter 2025).
https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/total-value-dwellings/jun-quarter-2025

## How to Read These Numbers

- Stock vs flow: APRA reports outstanding credit (stock). ABS lending
  indicators report new loan commitments (flow).
- Ratios: Debt-to-income ratios are broad indicators and can move with
  income changes as well as debt changes.
- Updates: These tables are revised and updated on different schedules.

## Western Australia Focus (Simulation Setting)

The OSF simulation is set in Perth and Western Australia. Here are WA-specific metrics:

### Perth Dwelling Prices (REIWA, Q4 2025 est.)
- Median house price: ~$750,000
- Median unit price: ~$480,000
- Price ratio to national average: ~74% (more affordable than eastern states)

Source: REIWA Perth Market Snapshot (December 2025)
https://reiwa.com.au/the-wa-market/perth-metro/

### Perth Rental Market (REIWA)
- Rental vacancy rate: <1% (extremely tight)
- Median weekly rent (house): ~$650/week
- Median weekly rent (unit): ~$550/week
- Rental growth: ~8% year-on-year

Source: REIWA Rental Market Statistics
https://reiwa.com.au/the-wa-market/rental-market/

### Gross Rental Yields
- Houses: ~4.5%
- Units: ~6.0%

Source: CoreLogic Hedonic Home Value Index (Dec 2025)
https://www.corelogic.com.au/our-data/corelogic-indices

### Market Speed
- Median days on market: ~12 days (fast-selling market)
- Auction clearance rate: ~72%

Source: Domain Property Market Report (Dec 2025)
https://www.domain.com.au/research/house-price-report/

### Regional Factors
- Mining sector employment growth: ~3%
- Population growth: ~2.3%

Source: WA Government - WA Economy Overview
https://www.wa.gov.au/organisation/department-of-treasury/wa-economy

## WA Boom-Bust Cycle History (1995-2025)

Western Australia's property market is uniquely volatile due to its dependence on mining:

| Period | Iron Ore | Pop Growth | Perth Median | Market |
|--------|----------|------------|--------------|--------|
| 1995-2003 | $12-28/t | 1.5% | $143K→$250K | Slow growth |
| 2004-2008 | $28→$65/t | 2.5%+ | $250K→$460K | **BOOM** |
| 2008-2009 | Crash to $35/t | Slowed | -8% | GFC correction |
| 2010-2012 | $145-170/t | 3.6% (peak) | $435K→$585K | **SUPER BOOM** |
| 2012-2014 | $170→$60/t | Slowing | Peak then decline | Peak→Decline |
| 2015-2019 | $55-80/t | 1.1% | $585K→$470K | **BUST** (-20%) |
| 2020-2025 | $100-200/t | 2.4%+ | $470K→$1M+ | **BOOM** |

### Key Drivers

1. **Iron Ore Prices** - WA's primary economic driver. When prices rise, mining jobs increase, migration surges, housing demand spikes.

2. **Population Migration** - Follows jobs. During booms, interstate migration is strong. During busts, people leave WA.

3. **Mining Project Cycles** - Construction phase brings FIFO workers. When projects complete, workforce shrinks.

### Mining Town Extremes

| Town | 2012 Peak | 2016-17 Trough | Decline |
|------|-----------|----------------|---------|
| Newman | $850,000 | $153,000 | **-82%** |
| Port Hedland | $1,200,000 | $361,000 | **-70%** |
| Perth (metro) | $585,000 | $470,000 | **-20%** |

## How This Data Drives the Simulation

The OSF simulation uses this real market data to:

### Property & Pricing
1. **Calibrate property valuations** - Perth suburbs priced relative to real medians (~$750K)
2. **Set realistic yields** - 4.5-6% based on actual WA rental returns
3. **Apply yield compression** - Booms compress yields, busts expand them

### Market Dynamics
4. **Drive event probabilities** - Tight vacancy rates (<1%) increase rental pressure events
5. **Influence NPC behavior** - High investor activity affects trading patterns
6. **Generate contextual news** - AI references real market conditions (iron ore, population)
7. **Simulate boom-bust cycles** - Iron ore and population drive appreciation/decline
8. **Model market conditions** - 5 states: boom, stable, stagnant, declining, bust

### Self-Healing Triggers
9. **Monitor demand overflow** - Buyer/renter waitlists trigger property sourcing
10. **Detect exit pressure** - Exit queue length triggers liquidity pool activation
11. **Track health metrics** - Vacancy rate, trade failures, rent collection
12. **Activate mitigations** - Automatic healing strategies based on network state

### Realistic Constraints
13. **Enforce 49% threshold** - Homeowner control limits
14. **Apply rate impacts** - Interest rates affect borrowing capacity
15. **Model FIFO dynamics** - Mining sector employment drives demand cycles

## Interest Rate Environment (RBA)

| Metric | Value | Source |
|--------|-------|--------|
| Cash rate | 4.35% (Dec 2025) | RBA |
| Average owner-occupier variable rate | ~6.3% | RBA F5 |
| Average investor variable rate | ~6.6% | RBA F5 |

Source: RBA Statistical Table F5 (Indicator Lending Rates)
https://www.rba.gov.au/statistics/tables/

### Impact on Simulation
- Higher rates reduce borrowing capacity
- Rate rises trigger mortgage stress events
- Rate cuts stimulate buyer demand

## Housing Affordability Stress (WA)

| Metric | Value | Context |
|--------|-------|---------|
| Median house to income ratio (Perth) | ~6.5x | More affordable than Sydney (~13x) |
| Mortgage stress threshold | >30% of income | Standard definition |
| % of WA mortgagees in stress | ~12% (est.) | Below national average |
| First home buyer deposit gap | ~$75K | 20% of $750K median |

### FIFO Worker Impact
- ~70,000 FIFO workers in WA
- Average FIFO salary: $150K-$200K
- Dual-income effect: Perth home + family in another state
- Boom periods see FIFO workers driving Perth property demand

Source: WA Chamber of Minerals and Energy (CME)
https://www.cmewa.com.au/

## Simulation Market Conditions

| Condition | Monthly Appreciation | Annual Equivalent | Triggers |
|-----------|---------------------|-------------------|----------|
| **Boom** | +0.6% to +1.2% | 7-15% | Iron ore >$150, pop growth >2%, confidence >60 |
| **Stable** | +0.2% to +0.4% | 2.4-5% | Iron ore >$100, pop growth >1.5% |
| **Stagnant** | -0.1% to +0.1% | -1 to +1% | Extended peak phase, buyer hesitation |
| **Declining** | -0.5% to -0.2% | -6% to -2.4% | Iron ore <$100, confidence dropping |
| **Bust** | -1.0% to -0.5% | -11% to -6% | Iron ore <$80, population outflow |

Note: Perth metro rates. Mining towns can experience 5-10x these swings.

## Homeowner Control Threshold (49% Rule)

In the OSF model, homeowners can tokenize equity while retaining control:

| Equity Tokenized | Status | Occupancy Rights |
|------------------|--------|------------------|
| 0-49% | **Owner-occupier** | Full control, remains owner |
| 50%+ | **Living arrangement change** | Becomes tenant or exits |

### Why 49%?
- Maintains majority ownership and decision-making control
- Aligns with typical lender LVR requirements (60-80% LVR = 20-40% equity)
- Provides buffer for market volatility

### Exceeding 49%
If a homeowner tokenizes more than 49%, they are:
1. **Tenant with intent to buy back** - Renting from the network, building equity to repurchase
2. **Renter** - Full exit from ownership, token holders own the property

This typically occurs during **financial distress** when immediate liquidity is needed.

## Distressed Exit Pathways

When homeowners face financial stress, OSF provides alternatives to forced sale:

| Pathway | Equity Access | Occupancy | Use Case |
|---------|---------------|-----------|----------|
| **Equity access (≤49%)** | Partial | Retained | Temporary cashflow needs |
| **Rent-back (50-80%)** | Substantial | Tenant | Mortgage distress, divorce |
| **Full exit (100%)** | Complete | Renter | Bankruptcy, relocation |
| **Gradual buyback** | Decreasing | Tenant→Owner | Recovery from distress |

### Traditional vs OSF

| Scenario | Traditional | OSF Network |
|----------|-------------|-------------|
| Mortgage distress | Forced sale, lose home | Tokenize equity, stay as tenant |
| Divorce settlement | Sell or refinance | One party exits via tokens |
| Retirement income | Reverse mortgage | Controlled equity release |
| Market downturn | Negative equity trap | Network absorbs partial losses |

## Network Self-Healing Mechanisms

OSF responds to market stress differently than traditional markets:

### Demand Pressure (Boom Conditions)
| Issue | Traditional Market | OSF Response |
|-------|-------------------|--------------|
| Investor FOMO | Price spiral, no supply | Buyer waitlist, property sourcing |
| Rental shortage | Bidding wars, homelessness | Renter waitlist, homeowner outreach |
| Token scarcity | N/A | Incentivize new property listings |

### Exit Pressure (Bust Conditions)
| Issue | Traditional Market | OSF Response |
|-------|-------------------|--------------|
| Panic selling | Price crash, foreclosures | Liquidity pool floor bids |
| No buyers | Fire sales | Buyer-seller matching |
| Distressed owners | Foreclosure | Partial exit programs |

### Why This Matters
Banks can only **foreclose or hold**. OSF can **coordinate participants** to solve problems that markets alone cannot address.

## Professional Services Map (WA)

Specialist services typically required to operate property transactions and
financing in Western Australia. These map to roles in the simulation.

### Mortgage & Finance

- **Mortgage broker / credit assistance**: Must hold an Australian Credit
  Licence (ACL) or act as a credit representative under a licensee.
  - National Consumer Credit Protection Act 2009 (Cth):
    https://www.legislation.gov.au/C2009A00134
  - ASIC responsible lending guidance:
    https://asic.gov.au/regulatory-resources/credit/responsible-lending/

- **Credit provider / lender**: Must be licensed and comply with responsible
  lending and disclosure obligations under the Credit Act.
  - ASIC credit licensing overview:
    https://asic.gov.au/for-finance-professionals/credit-licensees/

### Insurance (Property & Strata)

- **Strata company insurance** (if property is in a strata scheme): must insure
  insurable assets and hold legal liability insurance (minimum $10M).
  - Strata Titles Act 1985 (WA) Section 97:
    https://www.legislation.wa.gov.au/legislation/statutes.nsf/RedirectURL?OpenAgent=&query=mrdoc_44209.htm

- **Building / landlord insurance**: commonly required by lenders and owners
  and affects risk and cashflow in the simulation.

### Valuation & Professional Standards

- **Licensed property valuer**: required for formal market valuations and
  risk assessment (equity access, lending, insurance).
- **Insurance valuations**: common industry practice is to obtain replacement
  cost valuations periodically (often every 3–5 years) to reduce underinsurance.
  - Strata insurance valuation guidance (WA):
    https://www.wa.strata.community/post/the-critical-role-of-building-valuations-for-strata-insurance-coverage-in-wa

### Settlement & Title

- **Settlement agent / conveyancer**: licensed in WA to handle title transfer.
  https://www.consumerprotection.wa.gov.au/settlement-agents
- **Landgate**: title registration and verification of identity (VOI).
  https://www.landgate.wa.gov.au/land-and-property/land-transactions-hub/land-transaction-policy-and-procedure-guides/land-titles/proprietor/voi-01-western-australian-registrar-and-commissioner-of-titles-joint-practice-verification-of-identity-and-authority.-paper-based-transactions

## How This Informs Simulation Events

These services and metrics drive event generation and constraints:

### Property Events
- **Valuation updates** affect token price and equity access limits
- **Insurance renewal** events depend on replacement valuations
- **Maintenance requests** trigger service provider tasks

### Financial Events
- **Mortgage approval** events depend on credit rules and valuations
- **Settlement events** change ownership and trigger token mint/burn
- **Equity access requests** limited by 49% threshold and valuations

### Market Events
- **Iron ore price changes** trigger boom/bust market condition shifts
- **Population migration** affects rental demand and vacancy rates
- **Interest rate changes** impact borrowing capacity and stress levels

### Network Health Events
- **Exit pressure** triggers liquidity pool activation
- **Demand overflow** triggers property sourcing campaigns
- **Rental shortage** triggers homeowner outreach programs
- **Trade failures** trigger buyer-seller matching

### Distress Events
- **Mortgage stress** can trigger equity access or rent-back pathways
- **Market downturns** activate self-healing mechanisms
- **Forced sales** are prevented via network coordination

## Notes for OSF Simulation

- This data is used for educational context only.
- Simulation outputs do not represent real investment outcomes.
- Data is updated periodically and may lag current market conditions.
- The simulation demonstrates both UPSIDE and DOWNSIDE scenarios.

