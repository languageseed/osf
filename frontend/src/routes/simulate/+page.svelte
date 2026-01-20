<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';
	import { Chart, registerables } from 'chart.js';
	import { TrendingUp, TrendingDown, Wallet, Building, Trophy, Vote, RefreshCw, ArrowUpRight, ArrowDownRight, ArrowRight, Mail, Play, ChevronRight, ChevronUp, Bug, Lightbulb, MessageSquare, ThumbsUp, ThumbsDown, Send, Plus, Filter, Sparkles, MapPin, Calendar, Clock, Repeat, Home, Users, Shield, Landmark, Key, Wrench, DollarSign, PiggyBank, FileText, CheckCircle, AlertCircle, Percent, CreditCard, Hammer, Award, Info, Target, Zap, AlertTriangle, Gift, LogOut, UserCircle, Settings, Edit, Trash2, Check, Car, Ruler, Eye, Image, Bath, BedDouble, Wifi, WifiOff, Pause, Search, Activity, Heart, ShieldCheck, Handshake, ArrowRightLeft, Star, Minus, X, Bot } from 'lucide-svelte';
	import * as Card from "$lib/components/ui/card";
	import { Button } from "$lib/components/ui/button";
	import { Badge } from "$lib/components/ui/badge";
	import MoneyFlowDiagram from "$lib/components/MoneyFlowDiagram.svelte";
	import SelfHealingDiagram from "$lib/components/SelfHealingDiagram.svelte";
	import { Input } from "$lib/components/ui/input";
	import * as Dialog from "$lib/components/ui/dialog";
	import { auth, devLogin, logout, fetchAuthConfig, type AuthConfig } from '$lib/auth.svelte';
	import NetworkClock from '$lib/components/NetworkClock.svelte';
	import GovernorChat from '$lib/components/GovernorChat.svelte';
	import PropertyCard from '$lib/components/PropertyCard.svelte';
	import PropertyDetail from '$lib/components/PropertyDetail.svelte';
	import AvatarSelect from '$lib/components/AvatarSelect.svelte';
	import { 
		initPool, 
		fetchProperties, 
		fetchProperty, 
		fetchAvatars,
		getProperties as getPoolProperties,
		getAvatars as getPoolAvatars,
		type PoolProperty,
		type PoolAvatar
	} from '$lib/pool.svelte';
	import { API_V1 } from '$lib/config';
	
	// =====================================================
	// Network Clock Configuration
	// =====================================================
	// Clock modes:
	// - 'manual': User controls time (current behavior) - good for testing
	// - 'sync': Backend clock controls time (multiplayer sync)
	type ClockMode = 'manual' | 'sync';
	let clockMode = $state<ClockMode>('manual');
	
	// Backend API base URL (from config)
	const API_BASE = API_V1;
	
	// Clock presets for quick switching
	const clockPresets = [
		{ id: 'test', label: 'Test (30s)', desc: 'Fast for testing' },
		{ id: 'demo_fast', label: 'Demo Fast (2m)', desc: 'Quick demos' },
		{ id: 'demo', label: 'Demo (5m)', desc: 'Standard demo' },
		{ id: 'casual', label: 'Casual (15m)', desc: 'Relaxed play' },
	];

	// Register Chart.js components
	Chart.register(...registerables);

	// Chart references
	let projectionChartCanvas = $state<HTMLCanvasElement | null>(null);
	let locationChartCanvas = $state<HTMLCanvasElement | null>(null);
	let projectionChart: Chart | null = null;
	let locationChart: Chart | null = null;

	// Role selection
	type SimRole = 'investor' | 'renter' | 'tenant' | 'homeowner' | 'custodian' | 'foundation';
	let activeRole = $state<SimRole>('investor');
	
	const roles = [
		{ id: 'investor' as SimRole, label: 'Investor', icon: TrendingUp, desc: 'Explore token economics' },
		{ id: 'renter' as SimRole, label: 'Renter', icon: Building, desc: 'Simulate finding a rental' },
		{ id: 'tenant' as SimRole, label: 'Tenant', icon: Key, desc: 'Learn rent-to-own mechanics' },
		{ id: 'homeowner' as SimRole, label: 'Homeowner', icon: Home, desc: 'Explore equity access flows' },
		{ id: 'custodian' as SimRole, label: 'Service Provider', icon: Wrench, desc: 'Learn service fee mechanics' },
		{ id: 'foundation' as SimRole, label: 'Foundation', icon: Landmark, desc: 'Explore governance staking' },
	];
	
	// Role info dialog
	let showRoleInfoDialog = $state(false);
	
	// Simulation info dialog
	let showSimulationInfoDialog = $state(false);
	
	// Detailed role information
	const roleDetails: Record<SimRole, {
		purpose: string;
		motivation: string;
		rewards: string[];
		risks: string[];
		threats: string[];
		opportunities: string[];
	}> = {
		investor: {
			purpose: 'Investors provide capital to the network by purchasing property tokens. This capital enables homeowners to access equity and funds property acquisitions.',
			motivation: 'Build wealth through diversified property exposure without the hassles of direct ownership. Start small and grow over time.',
			rewards: [
				'Earn rental yields distributed monthly',
				'Benefit from property appreciation',
				'Governance voting rights on network decisions',
				'Liquidity to buy/sell anytime (in production)',
				'Portfolio diversification across multiple properties',
			],
			risks: [
				'Property values can decline',
				'Rental yields may vary based on occupancy',
				'Token price volatility',
				'Smart contract risks (in production)',
			],
			threats: [
				'Economic downturns affecting property markets',
				'Interest rate rises reducing property demand',
				'Regulatory changes affecting tokenised assets',
			],
			opportunities: [
				'Early adoption of property tokenisation',
				'Access to premium properties normally out of reach',
				'Compound growth through auto-reinvestment',
				'Progression to Foundation Partner for enhanced yields',
			],
		},
		renter: {
			purpose: 'Renters occupy network properties under standard rental agreements. They enjoy quality housing with transparent, AI-assisted property management.',
			motivation: 'Find quality rental housing with responsive maintenance, fair treatment, and transparent communication through the OSF network.',
			rewards: [
				'Responsive AI-triaged maintenance requests',
				'Transparent rental terms and communication',
				'Quality properties in the network',
				'Option to upgrade to rent-to-own (Tenant)',
				'Digital lease management',
			],
			risks: [
				'Rent payments are required on time',
				'Standard tenancy obligations apply',
				'Property may be sold (with tenant rights protected)',
			],
			threats: [
				'Rental market price increases',
				'Property maintenance issues',
				'Lease non-renewal at end of term',
			],
			opportunities: [
				'Build rental history for future applications',
				'Transition to Tenant role for equity accumulation',
				'Access to well-maintained network properties',
				'Participate in governance as token holder',
			],
		},
		tenant: {
			purpose: 'Tenants are on a rent-to-own pathway, accumulating equity with each payment while living in the property they will eventually own.',
			motivation: 'Build towards homeownership without needing a large deposit upfront. Every payment brings you closer to owning your home.',
			rewards: [
				'Equity accumulation with each payment',
				'Path to full homeownership',
				'No need for traditional mortgage approval',
				'Live in your future home while building equity',
				'Transparent progress tracking',
			],
			risks: [
				'Commitment to long-term payment schedule',
				'Property value changes affect equity position',
				'Must maintain property to standard',
			],
			threats: [
				'Income disruption affecting payments',
				'Property market decline during accumulation period',
				'Life circumstances requiring relocation',
			],
			opportunities: [
				'Homeownership without traditional barriers',
				'Forced savings through equity contributions',
				'Property appreciation during tenure',
				'Transition to Homeowner with full ownership',
			],
		},
		homeowner: {
			purpose: 'Homeowners sell partial equity to the network in exchange for capital, while continuing to live in their property. They can also rent out their property.',
			motivation: 'Access your home equity without taking on debt or selling your entire property. Unlock value while staying in your home.',
			rewards: [
				'Access capital without interest-bearing debt',
				'Continue living in your property',
				'Benefit from remaining equity appreciation',
				'Optional rental income if renting out',
				'Buyback equity at any time',
			],
			risks: [
				'Reduced ownership stake in property',
				'Property value decline affects equity',
				'Must maintain property to network standards',
			],
			threats: [
				'Property market downturn',
				'Maintenance costs and responsibilities',
				'Regulatory changes affecting equity arrangements',
			],
			opportunities: [
				'Debt consolidation without interest',
				'Fund renovations to increase property value',
				'Transition to Foundation Partner with freed capital',
				'Generate rental income while away',
			],
		},
		custodian: {
			purpose: 'Service Providers perform essential work for the network: property management, trades, legal advice, accounting, inspections, and more.',
			motivation: 'Earn consistent fees by providing professional services to network properties. Work is routed by AI based on skills and availability.',
			rewards: [
				'Regular service fees for completed work',
				'AI-assisted task routing and prioritisation',
				'Diverse work across multiple properties',
				'Build reputation in the network',
				'Potential for governance participation',
			],
			risks: [
				'Work volume depends on network size',
				'Must meet quality standards',
				'Competition from other service providers',
			],
			threats: [
				'Economic downturn reducing property activity',
				'AI automation of some tasks',
				'Reputation damage from poor service',
			],
			opportunities: [
				'First-mover advantage in new service categories',
				'Specialisation in high-value services',
				'Scale across multiple property networks',
				'Invest earnings into network tokens',
			],
		},
		foundation: {
			purpose: 'Foundation Partners provide long-term capital stability by staking significant holdings. They receive enhanced yields and governance power in return.',
			motivation: 'Earn premium returns and shape network direction through enhanced governance rights. Ideal for long-term believers in the protocol.',
			rewards: [
				'Enhanced yield rates (+0.5% or more)',
				'2x voting power on governance',
				'Priority access to new properties',
				'Network stability rewards',
				'Proposal creation rights',
			],
			risks: [
				'Capital locked for chosen period',
				'Early withdrawal penalties',
				'Higher minimum commitment',
			],
			threats: [
				'Network growth slower than expected',
				'Liquidity needs during lock period',
				'Protocol governance disputes',
			],
			opportunities: [
				'Shape network direction through governance',
				'Compound enhanced yields over time',
				'Build significant stake in network success',
				'Mentorship/advisory roles in ecosystem',
			],
		},
	};

	// =====================================================
	// UNIFIED NETWORK FINANCIAL MODEL
	// All roles interact with this shared state
	// =====================================================
	
	// Network-level state (shared across all roles)
	let networkMonth = $state(0);  // Current simulation month
	// Treasury should be ~1% of property value for operating expenses
	// With ~$10M in properties, treasury is ~$100K
	let networkTreasury = $state(100000);  // Network operating funds
	
	// Live performance tracking (updates every tick)
	let simulationHistory = $state<Array<{
		month: number;
		networkValue: number;
		tokenPrice: number;
		userNetWorth: number;
		propertyCount: number;
		marketCondition: string;
		reputationScore: number;
	}>>([]);
	let networkTotalRentalIncome = $state(0);  // Accumulates each month
	let networkTotalExpenses = $state(0);  // Service provider payments, maintenance
	let networkOccupancyRate = $state(0.92);  // 92% occupied
	
	// Token economics (base values - derived values computed after properties are defined)
	let totalTokenSupply = $state(1000000);  // Total OSF tokens in circulation
	let lastTokenPrice = $state(1.0);  // For tracking price changes
	
	// =====================================================
	// WA MARKET STATE - Boom/Bust Cycle Tracking
	// =====================================================
	// These drive property appreciation, vacancy, and NPC behavior
	
	type MarketCondition = 'boom' | 'stable' | 'stagnant' | 'declining' | 'bust';
	type EconomicPhase = 'expansion' | 'peak' | 'contraction' | 'trough' | 'recovery';
	
	let ironOrePrice = $state(115);  // USD/tonne (current: ~$110)
	let populationGrowthRate = $state(2.0);  // Annual % (current: ~2.4%)
	let marketCondition = $state<MarketCondition>('stable');
	let economicPhase = $state<EconomicPhase>('expansion');
	let monthsInPhase = $state(0);
	let consumerConfidence = $state(65);  // 0-100
	
	// Derived appreciation rate based on WA market conditions
	// REALISTIC rates based on Perth metro historical data (not mining towns)
	function getAppreciationRate(): number {
		// Perth metro realistic appreciation (Perth saw ~15% annual at peak 2006-2007)
		// Converting to monthly: 15% annual ≈ 1.2% monthly peak
		const rates: Record<MarketCondition, [number, number]> = {
			boom: [0.006, 0.012],       // 0.6% to 1.2% monthly (7-15% annual - realistic boom)
			stable: [0.002, 0.004],     // 0.2% to 0.4% monthly (2.4-5% annual - normal market)
			stagnant: [-0.001, 0.001],  // -0.1% to 0.1% monthly (flat market)
			declining: [-0.005, -0.002], // -0.5% to -0.2% monthly (-6% to -2.4% annual)
			bust: [-0.010, -0.005],     // -1.0% to -0.5% monthly (-11% to -6% annual for Perth metro)
		};
		const [min, max] = rates[marketCondition];
		return min + Math.random() * (max - min);
	}
	
	// Update market condition based on indicators
	function updateMarketCondition() {
		if (ironOrePrice >= 150 && populationGrowthRate >= 2.0 && consumerConfidence >= 60) {
			marketCondition = 'boom';
		} else if (ironOrePrice >= 100 && populationGrowthRate >= 1.5 && consumerConfidence >= 50) {
			marketCondition = 'stable';
		} else if (ironOrePrice >= 80 && consumerConfidence >= 40) {
			marketCondition = 'stagnant';
		} else if (ironOrePrice >= 60 || consumerConfidence >= 30) {
			marketCondition = 'declining';
		} else {
			marketCondition = 'bust';
		}
	}
	
	// Simulate WA economic events (iron ore, population)
	function simulateWAEconomicEvents() {
		// Iron ore price fluctuation (WA's primary economic driver)
		const ironOreChange = (Math.random() - 0.5) * 10;  // -5 to +5 per month
		
		// Add occasional bigger swings based on phase
		if (economicPhase === 'expansion' && Math.random() < 0.1) {
			ironOrePrice += 15 + Math.random() * 20;  // Boom spike
			addThinking('Market', 'observation', `Iron ore surges to $${ironOrePrice.toFixed(0)}/t on Chinese demand`, 90);
		} else if (economicPhase === 'contraction' && Math.random() < 0.15) {
			ironOrePrice -= 15 + Math.random() * 15;  // Bust drop
			addThinking('Market', 'observation', `Iron ore falls to $${ironOrePrice.toFixed(0)}/t as demand weakens`, 85);
		} else {
			ironOrePrice += ironOreChange;
		}
		
		// Keep iron ore in realistic range ($40-$220)
		ironOrePrice = Math.max(40, Math.min(220, ironOrePrice));
		
		// Population growth follows iron ore with lag
		if (ironOrePrice > 140) {
			populationGrowthRate = Math.min(3.5, populationGrowthRate + 0.05);
		} else if (ironOrePrice < 80) {
			populationGrowthRate = Math.max(-0.5, populationGrowthRate - 0.08);
		} else {
			populationGrowthRate += (Math.random() - 0.5) * 0.1;
		}
		populationGrowthRate = Math.max(-1, Math.min(4, populationGrowthRate));
		
		// Consumer confidence follows market
		if (marketCondition === 'boom') consumerConfidence = Math.min(90, consumerConfidence + 2);
		else if (marketCondition === 'declining') consumerConfidence = Math.max(20, consumerConfidence - 3);
		else if (marketCondition === 'bust') consumerConfidence = Math.max(10, consumerConfidence - 5);
		else consumerConfidence += (Math.random() - 0.5) * 4;
		consumerConfidence = Math.max(10, Math.min(95, consumerConfidence));
		
		// Vacancy rate follows population and market
		if (marketCondition === 'boom') {
			networkOccupancyRate = Math.min(0.99, networkOccupancyRate + 0.005);
		} else if (marketCondition === 'declining' || marketCondition === 'bust') {
			networkOccupancyRate = Math.max(0.80, networkOccupancyRate - 0.01);
		}
		
		// Economic phase transitions
		monthsInPhase++;
		const transitionProb = Math.min(0.25, monthsInPhase * 0.015);
		if (Math.random() < transitionProb) {
			const transitions: Record<EconomicPhase, EconomicPhase> = {
				expansion: 'peak',
				peak: 'contraction',
				contraction: 'trough',
				trough: 'recovery',
				recovery: 'expansion',
			};
			const oldPhase = economicPhase;
			economicPhase = transitions[economicPhase];
			monthsInPhase = 0;
			
			addThinking('Governor', 'observation', 
				`Economic cycle shift: ${oldPhase} → ${economicPhase}. Iron ore: $${ironOrePrice.toFixed(0)}/t, Pop growth: ${populationGrowthRate.toFixed(1)}%`, 
				95);
			
			addNetworkEvent('governance_vote', 'Governor', 'Network', 
				`Economy enters ${economicPhase} phase`, 0, { oldPhase, newPhase: economicPhase });
		}
		
		// Update market condition
		updateMarketCondition();
	}
	
	// =====================================================
	// SELF-HEALING SYSTEM - Autonomous Network Recovery
	// =====================================================
	
	type HealthStatus = 'healthy' | 'warning' | 'critical';
	type HealingStrategyType = 'liquidity_pool' | 'buyer_matching' | 'rent_to_own_accel' | 
		'partial_exit' | 'expense_reduction' | 'tenant_support' | 'rebalancing' |
		'property_sourcing' | 'homeowner_outreach' | 'waitlist_management' | 'vacancy_incentive';
	
	// Network health metrics
	let networkHealth = $state({
		liquidityRatio: 0.85,
		exitQueueLength: 0,
		tradeFailureRate: 0.10,
		tokenPriceVsNAV: 0.02,
		rentCollectionRate: 0.98,
		maintenanceBacklog: 2,
		// SUPPLY-SIDE METRICS
		buyerDemandRatio: 1.0,   // Buyers wanting in vs available tokens (>1.5 = shortage)
		rentalVacancyRate: 0.08, // % of properties vacant (< 0.02 = rental shortage)
		investorWaitlistSize: 0, // Investors waiting to buy tokens
	});
	
	// Exit queue for sellers wanting out
	let exitQueue = $state<Array<{
		id: number;
		seller: string;
		propertyId: string;
		propertyAddress: string;
		tokensForSale: number;
		askPrice: number;
		listedMonth: number;
		status: 'pending' | 'matched' | 'partial' | 'filled';
		matchedBuyer?: string;
	}>>([]);
	
	// BUYER WAITLIST - investors/renters wanting to join but no supply
	let buyerWaitlist = $state<Array<{
		id: number;
		buyer: string;
		type: 'investor' | 'renter';
		desiredAmount: number;  // $ for investors, monthly rent for renters
		waitingSince: number;   // Month added
		status: 'waiting' | 'matched' | 'partial' | 'cancelled';
		priority: 'standard' | 'premium';  // Premium = higher fees accepted
	}>>([]);
	
	// Rental waitlist - renters waiting for properties
	let rentalWaitlist = $state<Array<{
		id: number;
		renter: string;
		preferredSuburb?: string;
		maxRent: number;
		waitingSince: number;
		status: 'waiting' | 'matched' | 'cancelled';
	}>>([]);
	
	// Liquidity pool (stability fund)
	// Should be ~0.5-1% of total property value for realistic reserves
	// With ~$10M in properties, pool is ~$75K
	let liquidityPool = $state({
		balance: 75000,
		floorBidPrice: 0.80,  // 20% below NAV
		deploymentsThisMonth: 0,
		totalDeployed: 0,
		tokensHeld: 0,
	});
	
	// Active healing strategies
	let activeStrategies = $state<Array<{
		id: string;
		type: HealingStrategyType;
		name: string;
		activatedMonth: number;
		status: 'active' | 'completed' | 'failed';
		progress: number;  // 0-100%
		actions: string[];
		effectiveness?: number;
	}>>([]);
	
	// Healing history for learning
	let healingHistory = $state<Array<{
		crisisId: string;
		startMonth: number;
		endMonth?: number;
		trigger: string;
		strategiesUsed: string[];
		outcome: 'resolved' | 'ongoing' | 'failed';
		lessonsLearned: string[];
	}>>([]);
	
	// Derive overall health status
	let overallHealthStatus = $derived.by((): HealthStatus => {
		// CRITICAL: Major exit pressure OR major supply shortage
		if (networkHealth.tradeFailureRate > 0.30 || 
			exitQueue.length > 10 || 
			networkHealth.rentCollectionRate < 0.90 ||
			marketCondition === 'bust' ||
			// Supply shortage criticals
			networkHealth.rentalVacancyRate < 0.01 ||  // Almost zero vacancy
			buyerWaitlist.length > 20) {               // Massive investor demand unmet
			return 'critical';
		}
		// WARNING: Elevated stress in either direction
		if (networkHealth.tradeFailureRate > 0.15 || 
			exitQueue.length > 5 || 
			networkHealth.rentCollectionRate < 0.95 ||
			marketCondition === 'declining' ||
			// Supply shortage warnings
			networkHealth.rentalVacancyRate < 0.03 ||  // Very low vacancy
			buyerWaitlist.length > 10 ||               // Significant investor demand
			rentalWaitlist.length > 5) {               // Renters can't find homes
			return 'warning';
		}
		return 'healthy';
	});
	
	// Check if self-healing needed and execute
	function checkAndHeal() {
		const health = overallHealthStatus;
		
		if (health === 'critical' || health === 'warning') {
			const diagnosis = diagnoseNetworkIssues();
			
			if (diagnosis.length > 0) {
				addThinking('Governor', 'analysis', 
					`Network health: ${health.toUpperCase()}. Diagnosing ${diagnosis.length} issue(s).`,
					95);
				
				for (const issue of diagnosis) {
					const strategy = selectHealingStrategy(issue);
					if (strategy && !activeStrategies.find(s => s.type === strategy.type && s.status === 'active')) {
						executeHealingStrategy(strategy, issue);
					}
				}
			}
		}
		
		// Update active strategies progress
		updateStrategyProgress();
	}
	
	// Diagnose network issues
	function diagnoseNetworkIssues(): Array<{
		type: string;
		severity: 'warning' | 'critical';
		description: string;
		rootCause: string;
	}> {
		const issues: Array<{type: string; severity: 'warning' | 'critical'; description: string; rootCause: string}> = [];
		
		// Liquidity crisis
		if (networkHealth.tradeFailureRate > 0.30) {
			issues.push({
				type: 'liquidity_crisis',
				severity: 'critical',
				description: `Trade failure rate at ${(networkHealth.tradeFailureRate * 100).toFixed(0)}%`,
				rootCause: ironOrePrice < 80 ? 'Market downturn reducing buyer confidence' : 'Seller pressure exceeding buyer demand',
			});
		} else if (networkHealth.tradeFailureRate > 0.15) {
			issues.push({
				type: 'liquidity_stress',
				severity: 'warning',
				description: `Trade failure rate elevated at ${(networkHealth.tradeFailureRate * 100).toFixed(0)}%`,
				rootCause: 'Reduced trading activity',
			});
		}
		
		// Exit queue pressure
		if (exitQueue.filter(e => e.status === 'pending').length > 5) {
			const pendingCount = exitQueue.filter(e => e.status === 'pending').length;
			issues.push({
				type: 'exit_pressure',
				severity: pendingCount > 10 ? 'critical' : 'warning',
				description: `${pendingCount} sellers waiting to exit`,
				rootCause: marketCondition === 'bust' ? 'Panic selling during market bust' : 'Normal exit demand exceeding buyer interest',
			});
		}
		
		// Occupancy issues
		if (networkOccupancyRate < 0.85) {
			issues.push({
				type: 'vacancy_crisis',
				severity: 'critical',
				description: `Vacancy rate at ${((1 - networkOccupancyRate) * 100).toFixed(1)}%`,
				rootCause: populationGrowthRate < 0 ? 'Population outflow reducing tenant demand' : 'Rental pricing above market',
			});
		}
		
		// Rent collection issues
		if (networkHealth.rentCollectionRate < 0.95) {
			issues.push({
				type: 'collection_issues',
				severity: networkHealth.rentCollectionRate < 0.90 ? 'critical' : 'warning',
				description: `Rent collection at ${(networkHealth.rentCollectionRate * 100).toFixed(0)}%`,
				rootCause: 'Tenant financial stress',
			});
		}
		
		// ========== SUPPLY SHORTAGE DETECTION ==========
		
		// Investor demand exceeds available tokens
		if (buyerWaitlist.length > 10) {
			issues.push({
				type: 'investor_demand_overflow',
				severity: buyerWaitlist.length > 20 ? 'critical' : 'warning',
				description: `${buyerWaitlist.length} investors waiting to buy tokens`,
				rootCause: marketCondition === 'boom' ? 'Strong market driving investor FOMO' : 'Limited property supply for growing demand',
			});
		}
		
		// Rental shortage (very low vacancy)
		if (networkHealth.rentalVacancyRate < 0.03) {
			issues.push({
				type: 'rental_shortage',
				severity: networkHealth.rentalVacancyRate < 0.01 ? 'critical' : 'warning',
				description: `Vacancy rate only ${(networkHealth.rentalVacancyRate * 100).toFixed(1)}% - renters struggling to find homes`,
				rootCause: populationGrowthRate > 2.0 ? 'Population surge outpacing housing supply' : 'Insufficient rental properties in network',
			});
		}
		
		// Renter waitlist growing
		if (rentalWaitlist.length > 5) {
			issues.push({
				type: 'renter_waitlist',
				severity: rentalWaitlist.length > 15 ? 'critical' : 'warning',
				description: `${rentalWaitlist.length} renters waiting for properties`,
				rootCause: 'Rental demand exceeds available inventory',
			});
		}
		
		// Community feedback issues - bug clusters indicate systemic problems
		const openBugs = feedbackItems.filter(f => f.feedback_type === 'bug' && f.status === 'open').length;
		if (openBugs >= 5) {
			issues.push({
				type: 'community_concern',
				severity: openBugs >= 10 ? 'critical' : 'warning',
				description: `${openBugs} unresolved bug reports from community`,
				rootCause: 'User experience issues affecting community confidence',
			});
		}
		
		// Low community sentiment
		if (communitySentiment.score < -0.3) {
			issues.push({
				type: 'sentiment_crisis',
				severity: communitySentiment.score < -0.5 ? 'critical' : 'warning',
				description: `Community sentiment at ${(communitySentiment.score * 100).toFixed(0)}% - members expressing concern`,
				rootCause: marketCondition === 'bust' ? 'Market downturn affecting community mood' : 'Unaddressed feedback and concerns',
			});
		}
		
		return issues;
	}
	
	// Select appropriate healing strategy
	function selectHealingStrategy(issue: {type: string; severity: string}): {
		type: HealingStrategyType;
		name: string;
		actions: string[];
	} | null {
		const strategies: Record<string, {type: HealingStrategyType; name: string; actions: string[]}> = {
			liquidity_crisis: {
				type: 'liquidity_pool',
				name: 'Liquidity Pool Activation',
				actions: [
					'Deploy treasury floor bids',
					'Alert opportunist investors',
					'Enable partial exits',
				],
			},
			liquidity_stress: {
				type: 'buyer_matching',
				name: 'Buyer-Seller Matching',
				actions: [
					'Notify matching investor profiles',
					'Alert rent-to-own tenants',
					'Offer discounted tokens to renters',
				],
			},
			exit_pressure: {
				type: 'partial_exit',
				name: 'Partial Exit Program',
				actions: [
					'Enable 30% immediate exit',
					'Stagger remaining over 6 months',
					'Match with patient buyers',
				],
			},
			vacancy_crisis: {
				type: 'tenant_support',
				name: 'Tenant Attraction Program',
				actions: [
					'Offer rent incentives (1 month free)',
					'Reduce security deposits',
					'Fast-track applications',
				],
			},
			collection_issues: {
				type: 'tenant_support',
				name: 'Tenant Payment Support',
				actions: [
					'Offer payment plans',
					'Defer arrears to lease end',
					'Connect with support services',
				],
			},
			// ========== SUPPLY SHORTAGE STRATEGIES ==========
			investor_demand_overflow: {
				type: 'property_sourcing',
				name: 'Property Sourcing Campaign',
				actions: [
					'Alert homeowner network about listing incentives',
					'Contact real estate agents for new listings',
					'Offer premium listing fees to attract supply',
					'Create waitlist priority for early depositors',
				],
			},
			rental_shortage: {
				type: 'vacancy_incentive',
				name: 'Vacancy Incentive Program',
				actions: [
					'Incentivize rent-to-own tenants to convert to buyers',
					'Offer premium to homeowners adding rental units',
					'Fast-track new property onboarding',
					'Partner with developers for upcoming supply',
				],
			},
			renter_waitlist: {
				type: 'homeowner_outreach',
				name: 'Homeowner Outreach Campaign',
				actions: [
					'Contact homeowners in high-demand suburbs',
					'Offer guaranteed rent to hesitant landlords',
					'Reduce onboarding fees for new listings',
					'Match renters with upcoming vacancies',
				],
			},
			community_concern: {
				type: 'rebalancing',
				name: 'Community Engagement Response',
				actions: [
					'Governor AI triages and responds to open issues',
					'Escalate critical bugs to priority queue',
					'Publish community update addressing concerns',
					'Schedule feedback town hall session',
				],
			},
			sentiment_crisis: {
				type: 'rebalancing',
				name: 'Community Confidence Restoration',
				actions: [
					'Publish transparent market outlook report',
					'Governor holds AMA session with members',
					'Highlight successful self-healing actions',
					'Communicate network resilience measures',
				],
			},
		};
		
		return strategies[issue.type] || null;
	}
	
	// Execute a healing strategy
	function executeHealingStrategy(
		strategy: {type: HealingStrategyType; name: string; actions: string[]},
		issue: {type: string; description: string; rootCause: string}
	) {
		const strategyRecord = {
			id: `heal-${Date.now()}`,
			type: strategy.type,
			name: strategy.name,
			activatedMonth: networkMonth,
			status: 'active' as const,
			progress: 0,
			actions: strategy.actions,
		};
		
		activeStrategies = [...activeStrategies, strategyRecord];
		
		addThinking('Governor', 'decision',
			`Self-heal activated: ${strategy.name}. Root cause: ${issue.rootCause}`,
			90);
		
		// Execute immediate actions based on strategy type
		switch (strategy.type) {
			case 'liquidity_pool':
				executeLiquidityPoolStrategy();
				break;
			case 'buyer_matching':
				executeBuyerMatchingStrategy();
				break;
			case 'partial_exit':
				executePartialExitStrategy();
				break;
			case 'tenant_support':
				executeTenantSupportStrategy();
				break;
		}
		
		addNetworkEvent('governance_vote', 'Governor', 'Network',
			`Self-healing: ${strategy.name} activated`, 0, { strategy: strategy.type, issue: issue.type });
	}
	
	// Liquidity pool strategy execution
	function executeLiquidityPoolStrategy() {
		const pendingExits = exitQueue.filter(e => e.status === 'pending');
		
		if (pendingExits.length > 0 && liquidityPool.balance > 5000) {
			const deployment = Math.min(liquidityPool.balance * 0.2, 25000);
			liquidityPool.balance -= deployment;
			liquidityPool.totalDeployed += deployment;
			liquidityPool.deploymentsThisMonth++;
			
			// Partially fill some exits
			const tokensCanBuy = deployment / liquidityPool.floorBidPrice;
			let tokensBought = 0;
			
			for (const exit of pendingExits) {
				if (tokensBought >= tokensCanBuy) break;
				
				const buyAmount = Math.min(exit.tokensForSale * 0.5, tokensCanBuy - tokensBought);
				tokensBought += buyAmount;
				exit.tokensForSale -= buyAmount;
				
				if (exit.tokensForSale <= 0) {
					exit.status = 'filled';
					addThinking('Governor', 'action',
						`Exit filled: ${exit.seller} sold all tokens via Liquidity Pool at $${liquidityPool.floorBidPrice.toFixed(2)}`,
						85);
				} else {
					exit.status = 'partial';
					addThinking('Governor', 'action',
						`Partial exit: ${exit.seller} sold ${buyAmount.toFixed(0)} tokens, ${exit.tokensForSale.toFixed(0)} remaining`,
						80);
				}
			}
			
			liquidityPool.tokensHeld += tokensBought;
			
			addNetworkEvent('token_trade', 'Liquidity Pool', 'Sellers',
				`Pool deployed $${deployment.toLocaleString()} to absorb exits`, deployment);
		}
		
		// Alert opportunist investors
		const opportunists = npcRoster.filter(n => n.personality === 'Opportunist');
		for (const opp of opportunists) {
			addThinking(opp.name, 'observation',
				`🔔 ALERT: Distressed tokens available at ${((1 - liquidityPool.floorBidPrice) * 100).toFixed(0)}% discount. Matches my contrarian strategy.`,
				undefined);
		}
	}
	
	// Buyer matching strategy execution
	function executeBuyerMatchingStrategy() {
		const pendingExits = exitQueue.filter(e => e.status === 'pending');
		
		// Match with opportunist and conservative investors who buy dips
		const potentialBuyers = npcRoster.filter(n => 
			n.personality === 'Opportunist' || 
			(n.personality === 'Conservative' && marketCondition === 'bust')
		);
		
		for (const exit of pendingExits.slice(0, 3)) {
			if (potentialBuyers.length > 0) {
				const buyer = potentialBuyers[Math.floor(Math.random() * potentialBuyers.length)];
				
				addThinking('Governor', 'action',
					`Buyer match: Connecting ${exit.seller} with ${buyer.name} for ${exit.propertyAddress.split(',')[0]} tokens`,
					85);
				
				// Simulate match success (higher in bust when opportunists are active)
				if (Math.random() < (marketCondition === 'bust' ? 0.7 : 0.5)) {
					exit.status = 'matched';
					exit.matchedBuyer = buyer.name;
					
					addThinking(buyer.name, 'decision',
						`Accepting match: Buying ${exit.tokensForSale.toFixed(0)} tokens at $${exit.askPrice.toFixed(2)} (${((1 - exit.askPrice) * 100).toFixed(0)}% below NAV)`,
						75);
					
					addNetworkEvent('token_trade', exit.seller, buyer.name,
						`Matched sale: ${exit.propertyAddress.split(',')[0]}`, exit.tokensForSale * exit.askPrice);
				}
			}
		}
		
		// Alert rent-to-own tenants in affected properties
		addThinking('Governor', 'action',
			`Notifying rent-to-own tenants: Opportunity to accelerate ownership at discounted prices`,
			80);
	}
	
	// Partial exit strategy execution
	function executePartialExitStrategy() {
		const pendingExits = exitQueue.filter(e => e.status === 'pending');
		
		for (const exit of pendingExits) {
			// Offer 30% immediate exit
			const immediateExit = exit.tokensForSale * 0.3;
			const remaining = exit.tokensForSale * 0.7;
			
			addThinking('Governor', 'action',
				`Partial exit offer to ${exit.seller}: 30% immediate ($${(immediateExit * exit.askPrice).toFixed(0)}), 70% over 6 months`,
				80);
			
			// Simulate acceptance
			if (Math.random() < 0.6) {
				exit.tokensForSale = remaining;
				exit.status = 'partial';
				
				addNetworkEvent('token_trade', exit.seller, 'Market',
					`Partial exit: ${immediateExit.toFixed(0)} tokens sold`, immediateExit * exit.askPrice);
			}
		}
	}
	
	// Tenant support strategy execution
	function executeTenantSupportStrategy() {
		addThinking('Governor', 'action',
			`Tenant support activated: Payment plans offered, 1-month rent deferral available`,
			85);
		
		// Improve rent collection rate over time
		networkHealth.rentCollectionRate = Math.min(0.98, networkHealth.rentCollectionRate + 0.02);
		
		// Improve occupancy through incentives
		if (networkOccupancyRate < 0.90) {
			addThinking('Governor', 'action',
				`Tenant attraction: Offering 1-month free rent for new leases`,
				80);
		}
	}
	
	// Update strategy progress each month
	function updateStrategyProgress() {
		for (const strategy of activeStrategies.filter(s => s.status === 'active')) {
			strategy.progress += 15 + Math.random() * 10;
			
			if (strategy.progress >= 100) {
				strategy.status = 'completed';
				strategy.effectiveness = calculateStrategyEffectiveness(strategy);
				
				addThinking('Governor', 'reflection',
					`Strategy complete: ${strategy.name}. Effectiveness: ${strategy.effectiveness}%`,
					90);
				
				// Learn from this strategy
				learnFromStrategy(strategy);
			}
		}
		
		activeStrategies = [...activeStrategies];  // Trigger reactivity
	}
	
	// Calculate how effective a strategy was
	function calculateStrategyEffectiveness(strategy: typeof activeStrategies[0]): number {
		switch (strategy.type) {
			case 'liquidity_pool':
				return networkHealth.tradeFailureRate < 0.20 ? 80 : 50;
			case 'buyer_matching':
				return exitQueue.filter(e => e.status === 'matched' || e.status === 'filled').length > 0 ? 85 : 40;
			case 'partial_exit':
				return exitQueue.filter(e => e.status === 'partial').length > 0 ? 70 : 30;
			default:
				return 60;
		}
	}
	
	// Learn from strategy outcomes
	function learnFromStrategy(strategy: typeof activeStrategies[0]) {
		if (strategy.effectiveness && strategy.effectiveness > 70) {
			healingHistory.push({
				crisisId: `crisis-${strategy.activatedMonth}`,
				startMonth: strategy.activatedMonth,
				endMonth: networkMonth,
				trigger: strategy.type,
				strategiesUsed: [strategy.name],
				outcome: 'resolved',
				lessonsLearned: [`${strategy.name} effective in ${marketCondition} market conditions`],
			});
		}
	}
	
	// Simulate exit requests (sellers wanting out) - BUST CONDITIONS
	function simulateExitRequests() {
		// More exit requests during bust
		const exitProbability = marketCondition === 'bust' ? 0.15 : 
			marketCondition === 'declining' ? 0.08 : 0.03;
		
		if (Math.random() < exitProbability && properties.length > 0) {
			const sellerNPC = npcRoster.find(n => n.personality === 'Aggressive' || n.personality === 'Speculator');
			if (sellerNPC) {
				const property = properties[Math.floor(Math.random() * properties.length)];
				const discount = marketCondition === 'bust' ? 0.20 : marketCondition === 'declining' ? 0.10 : 0.05;
				
				const exitRequest = {
					id: Date.now(),
					seller: sellerNPC.name,
					propertyId: property.address,
					propertyAddress: property.address,
					tokensForSale: 1000 + Math.random() * 4000,
					askPrice: 1.0 - discount,
					listedMonth: networkMonth,
					status: 'pending' as const,
				};
				
				exitQueue = [...exitQueue, exitRequest];
				
				addThinking(sellerNPC.name, 'decision',
					`Requesting exit: Listing ${exitRequest.tokensForSale.toFixed(0)} tokens at $${exitRequest.askPrice.toFixed(2)} (${(discount * 100).toFixed(0)}% discount)`,
					60);
				
				// Update trade failure rate based on queue length
				networkHealth.tradeFailureRate = Math.min(0.5, 0.10 + (exitQueue.length * 0.03));
			}
		}
	}
	
	// Simulate buyer/renter demand (wanting in) - BOOM CONDITIONS
	function simulateDemandPressure() {
		// More demand during boom
		const investorDemandProb = marketCondition === 'boom' ? 0.20 : 
			marketCondition === 'stable' ? 0.08 : 0.02;
		const renterDemandProb = populationGrowthRate > 2.0 ? 0.15 :
			populationGrowthRate > 1.0 ? 0.06 : 0.02;
		
		// Investors wanting to buy tokens
		if (Math.random() < investorDemandProb) {
			const investorNames = ['New Investor', 'SMSF Fund', 'Family Trust', 'Interstate Buyer', 'First Timer'];
			const buyer = investorNames[Math.floor(Math.random() * investorNames.length)];
			const amount = 10000 + Math.random() * 40000;
			
			buyerWaitlist = [...buyerWaitlist, {
				id: Date.now() + Math.random(),
				buyer: `${buyer} #${Math.floor(Math.random() * 1000)}`,
				type: 'investor',
				desiredAmount: amount,
				waitingSince: networkMonth,
				status: 'waiting',
				priority: Math.random() > 0.7 ? 'premium' : 'standard',
			}];
			
			addThinking('Governor', 'observation',
				`New investor interest: $${amount.toLocaleString()} waiting to invest. ${buyerWaitlist.length} total on waitlist.`,
				75);
		}
		
		// Renters looking for properties
		if (Math.random() < renterDemandProb && networkHealth.rentalVacancyRate < 0.10) {
			const renterNames = ['Young Professional', 'Small Family', 'Relocating Worker', 'Student', 'Downsizer'];
			const renter = renterNames[Math.floor(Math.random() * renterNames.length)];
			const maxRent = 400 + Math.random() * 600;
			
			rentalWaitlist = [...rentalWaitlist, {
				id: Date.now() + Math.random(),
				renter: `${renter} #${Math.floor(Math.random() * 1000)}`,
				preferredSuburb: properties.length > 0 ? properties[Math.floor(Math.random() * properties.length)].suburb : undefined,
				maxRent: maxRent,
				waitingSince: networkMonth,
				status: 'waiting',
			}];
			
			addThinking('Governor', 'observation',
				`New renter inquiry: Looking for property up to $${maxRent.toFixed(0)}/week. ${rentalWaitlist.length} renters on waitlist.`,
				70);
		}
		
		// Update demand metrics
		networkHealth.buyerDemandRatio = 1.0 + (buyerWaitlist.length * 0.1);
		networkHealth.rentalVacancyRate = Math.max(0.005, 1 - networkOccupancyRate - (rentalWaitlist.length * 0.005));
		
		// Naturally clear some waitlist entries (they find alternatives)
		if (buyerWaitlist.length > 5 && Math.random() < 0.1) {
			const cancelled = buyerWaitlist[0];
			buyerWaitlist = buyerWaitlist.slice(1);
			addThinking('Governor', 'observation',
				`${cancelled.buyer} left waitlist (found alternative investment)`,
				60);
		}
		if (rentalWaitlist.length > 3 && Math.random() < 0.15) {
			const cancelled = rentalWaitlist[0];
			rentalWaitlist = rentalWaitlist.slice(1);
			addThinking('Governor', 'observation',
				`${cancelled.renter} left rental waitlist (found housing elsewhere)`,
				55);
		}
	}
	
	// Network event log (unified across all roles)
	type NetworkEventType = 'rent_collected' | 'dividend_paid' | 'token_trade' | 'equity_access' | 
		'service_payment' | 'stake_deposit' | 'stake_yield' | 'property_appreciation' | 
		'maintenance_expense' | 'lease_signed' | 'inspection' | 'governance_vote' |
		'property_added' | 'property_updated' | 'property_removed';
	
	let networkEvents = $state<Array<{
		id: number,
		month: number,
		type: NetworkEventType,
		fromRole: string,
		toRole: string,
		description: string,
		amount: number,
		metadata?: any
	}>>([]);
	
	// Add network event helper
	function addNetworkEvent(type: NetworkEventType, fromRole: string, toRole: string, description: string, amount: number, metadata?: any) {
		networkEvents = [{
			id: Date.now() + Math.random(),
			month: networkMonth,
			type,
			fromRole,
			toRole,
			description,
			amount,
			metadata
		}, ...networkEvents].slice(0, 100);  // Keep last 100 events
	}
	
	// =====================================================
	// MARATHON MODE - Autonomous Multi-Hour Simulation
	// =====================================================
	// Marathon Agent: "Autonomous systems for tasks spanning hours or days"
	
	let marathonMode = $state(false);  // Is marathon mode active?
	let marathonStartTime = $state<Date | null>(null);  // When marathon started
	let marathonTargetMonths = $state(120);  // Target: 10 years (120 months)
	let marathonInterval = $state(2000);  // 2 seconds between ticks (demo speed)
	let marathonTimer = $state<ReturnType<typeof setInterval> | null>(null);
	let marathonPaused = $state(false);
	
	// Session tracking for "spanning hours" claim
	let sessionStartTime = $state(new Date());
	let totalSessionMonths = $state(0);  // Months simulated this session
	
	// AI Thinking Log - "Thought Signatures and Thinking Levels"
	type ThinkingLevel = 'observation' | 'analysis' | 'decision' | 'action' | 'reflection';
	
	let aiThinkingLog = $state<Array<{
		id: number,
		timestamp: Date,
		month: number,
		agent: string,  // NPC name or "Governor" or "Market"
		level: ThinkingLevel,
		thought: string,
		confidence?: number,  // 0-100%
		outcome?: 'success' | 'failure' | 'pending'
	}>>([]);
	
	// Add AI thinking entry
	function addThinking(agent: string, level: ThinkingLevel, thought: string, confidence?: number) {
		const entry: typeof aiThinkingLog[0] = {
			id: Date.now() + Math.random(),
			timestamp: new Date(),
			month: networkMonth,
			agent,
			level,
			thought,
			confidence,
			outcome: 'pending' as const
		};
		aiThinkingLog = [entry, ...aiThinkingLog].slice(0, 200);  // Keep last 200 thoughts
	}
	
	// NPC Self-Correction tracking
	let npcPerformance = $state<Record<string, {
		decisions: number,
		successes: number,
		failures: number,
		strategyAdjustments: number,
		lastAdjustment?: string
	}>>({});
	
	// NPC Portfolio Performance tracking (returns, not just decisions)
	let npcPortfolios = $state<Record<string, {
		startingValue: number,
		currentValue: number,
		totalInvested: number,
		totalDividends: number,
		holdings: number,  // Token count
		returnPercent: number,
		strategy: string,
		personality: string,
	}>>({});
	
	// Marathon mode functions
	function startMarathon() {
		if (marathonMode) return;
		
		marathonMode = true;
		marathonStartTime = new Date();
		marathonPaused = false;
		
		// Reset marathon metrics for new run
		marathonMetrics = {
			startingPortfolioValue: portfolioValue,
			startingNetworkValue: networkTotalPropertyValue,  // Track starting network value
			peakPortfolioValue: portfolioValue,
			troughPortfolioValue: portfolioValue,
			totalDividends: 0,
			ironOreMin: ironOrePrice,
			ironOreMax: ironOrePrice,
			populationMin: populationGrowthRate,
			populationMax: populationGrowthRate,
			monthsInBoom: 0,
			monthsInBust: 0,
			monthsInDecline: 0,
			monthsInStable: 0,
			monthsInStagnant: 0,
			worstAppreciation: 0,
			worstAppreciationMonth: 0,
			bestAppreciation: 0,
			bestAppreciationMonth: 0,
			majorEvents: [],
			history: [],
		};
		
		// Initialize NPC portfolios with varying starting amounts based on personality
		const npcStartingAmounts: Record<string, number> = {
			'Sarah Chen': 50000,      // Conservative - moderate capital
			'Marcus Thompson': 80000, // Aggressive - more capital, higher risk
			'Emily Rodriguez': 60000, // Balanced
			'David Park': 70000,      // Opportunist
			'Janet Williams': 40000,  // Passive - smaller, steady
			'Michael Foster': 90000,  // Speculator - high capital, high risk
			'Lisa Chang': 45000,      // Conservative
			'Robert Kim': 65000,      // Balanced
			'Market Maker': 100000,   // System - high liquidity
			'OSF Developer': 30000,   // System - smaller stake
			'Foundation': 200000,     // System - largest stake for governance
		};
		
		npcPortfolios = {};
		for (const [name, startingValue] of Object.entries(npcStartingAmounts)) {
			const npc = npcRoster.find(n => n.name === name);
			npcPortfolios[name] = {
				startingValue,
				currentValue: startingValue,
				totalInvested: 0,
				totalDividends: 0,
				holdings: 0,
				returnPercent: 0,
				strategy: npc?.strategy || 'Unknown',
				personality: npc?.personality || 'Unknown',
			};
		}
		
		addThinking('Governor', 'decision', `Starting Marathon Mode: Target ${marathonTargetMonths} months (${(marathonTargetMonths / 12).toFixed(1)} years) of autonomous simulation`, 95);
		
		marathonTimer = setInterval(() => {
			if (!marathonPaused && networkMonth < marathonTargetMonths) {
				simulateNetworkMonth();
				totalSessionMonths++;
				
				// Add periodic governor observations
				if (networkMonth % 12 === 0) {
					addThinking('Governor', 'reflection', `Year ${Math.floor(networkMonth / 12)} complete. Network health: ${networkOccupancyRate > 0.9 ? 'Strong' : 'Moderate'}. Portfolio growth: ${((portfolioValue / 10000 - 1) * 100).toFixed(1)}%`, 85);
				}
			}
			
			if (networkMonth >= marathonTargetMonths) {
				stopMarathon();
				addThinking('Governor', 'reflection', `Marathon complete! Simulated ${marathonTargetMonths} months autonomously.`, 100);
			}
		}, marathonInterval);
	}
	
	function pauseMarathon() {
		marathonPaused = !marathonPaused;
		addThinking('Governor', 'observation', marathonPaused ? 'Marathon paused by user' : 'Marathon resumed', 100);
	}
	
	function stopMarathon() {
		if (marathonTimer) {
			clearInterval(marathonTimer);
			marathonTimer = null;
		}
		marathonMode = false;
		addThinking('Governor', 'observation', `Marathon stopped. Total months simulated: ${networkMonth}`, 100);
		
		// Generate marathon synopsis
		generateMarathonSynopsis();
	}
	
	// =====================================================
	// MARATHON SYNOPSIS - Post-Simulation Summary
	// =====================================================
	
	let showMarathonSynopsis = $state(false);
	let marathonSynopsis = $state<{
		// Overview
		totalMonths: number;
		totalYears: number;
		sessionDuration: string;
		
		// Network Scale
		networkScale: {
			propertiesUnderManagement: number;
			startingPropertyValue: number;
			totalPropertyValue: number;
			propertyValueGrowth: number;  // Percentage growth
			activeRentalContracts: number;
			rentToOwnContracts: number;
			totalParticipants: number;
			serviceProvidersActive: number;
		};
		
		// Market Journey
		marketPhases: Array<{phase: string; months: number; appreciation: number}>;
		ironOreRange: {min: number; max: number; final: number};
		populationRange: {min: number; max: number; final: number};
		worstMonth: {month: number; condition: string; appreciation: number};
		bestMonth: {month: number; condition: string; appreciation: number};
		
		// Portfolio Performance
		startingValue: number;
		endingValue: number;
		totalReturn: number;
		totalReturnPercent: number;
		dividendsCollected: number;
		
		// Mitigations & Positive Actions
		mitigations: Array<{
			action: string;
			trigger: string;
			outcome: string;
			beneficiaries: string;
		}>;
		
		// Stakeholder Outcomes
		stakeholders: {
			investors: {verdict: string; details: string};
			renters: {verdict: string; details: string};
			tenants: {verdict: string; details: string};
			homeowners: {verdict: string; details: string};
			serviceProviders: {verdict: string; details: string};
			foundation: {verdict: string; details: string};
		};
		
		// Self-Healing Activity
		healingStrategiesUsed: number;
		exitRequestsHandled: number;
		liquidityDeployed: number;
		successfulMatches: number;
		
		// NPC Performance
		topPerformers: Array<{name: string; successRate: number; decisions: number}>;
		mostAdaptive: Array<{name: string; adjustments: number}>;
		
		// Investor Portfolio Distribution
		investorDistribution: {
			all: Array<{name: string; returnPercent: number; strategy: string; personality: string; startingValue: number; endingValue: number}>;
			best: {name: string; returnPercent: number};
			worst: {name: string; returnPercent: number};
			median: number;
			averageReturn: number;
			positiveCount: number;
			negativeCount: number;
		};
		
		// Key Events
		majorEvents: Array<{month: number; event: string; impact: string}>;
		
		// Network Reputation & Growth
		reputation: {
			finalScore: number;
			trend: 'rising' | 'stable' | 'falling';
			investorSatisfaction: number;
			homeownerSatisfaction: number;
			renterSatisfaction: number;
			tenantSatisfaction: number;
			wordOfMouthMultiplier: number;
			propertiesAdded: number;
			propertiesExited: number;
			netGrowth: number;
		};
		
		// Historical data for charts
		history: Array<{
			month: number;
			networkValue: number;
			tokenPrice: number;
			userNetWorth: number;
			marketCondition: string;
			ironOrePrice: number;
			reputationScore: number;
			propertyCount: number;
		}>;
		
		// Counterfactual
		withoutOSF: string;
		
		// Cooperative Outcomes (NEW)
		collectiveOutcomes: {
			familiesHoused: number;
			rentToOwnParticipants: number;
			rentToOwnCompletions: number;
			equityAccessedByHomeowners: number;
			totalNetworkDividends: number;
			crisesSurvived: number;
			selfHealingActivations: number;
			evictions: number;
			foreclosures: number;
		};
		
		// User Contribution (NEW)
		userContribution: {
			capitalDeployed: number;
			homesEnabled: number;
			stabilityScore: number;
			title: string;
			description: string;
			heldDuringDownturns: boolean;
			monthsInNetwork: number;
		};
		
		// Network Health (NEW)
		networkHealth: {
			grade: string;
			score: number;
			resilience: string;
			stability: string;
		};
	} | null>(null);
	
	// Track metrics during marathon for synopsis
	let marathonMetrics = $state({
		startingPortfolioValue: 10000,
		startingNetworkValue: 10000000,  // ~$10M starting network value
		peakPortfolioValue: 10000,
		troughPortfolioValue: 10000,
		totalDividends: 0,
		ironOreMin: 115,
		ironOreMax: 115,
		populationMin: 2.0,
		populationMax: 2.0,
		monthsInBoom: 0,
		monthsInBust: 0,
		monthsInDecline: 0,
		monthsInStable: 0,
		monthsInStagnant: 0,
		worstAppreciation: 0,
		worstAppreciationMonth: 0,
		bestAppreciation: 0,
		bestAppreciationMonth: 0,
		majorEvents: [] as Array<{month: number; event: string; impact: string}>,
		// Historical data for charts
		history: [] as Array<{
			month: number;
			networkValue: number;
			tokenPrice: number;
			userNetWorth: number;
			marketCondition: string;
			ironOrePrice: number;
			reputationScore: number;
			propertyCount: number;
		}>,
	});
	
	// Update marathon metrics each month (called from simulation)
	function updateMarathonMetrics(appreciation: number) {
		// Track iron ore range
		marathonMetrics.ironOreMin = Math.min(marathonMetrics.ironOreMin, ironOrePrice);
		marathonMetrics.ironOreMax = Math.max(marathonMetrics.ironOreMax, ironOrePrice);
		
		// Track population range
		marathonMetrics.populationMin = Math.min(marathonMetrics.populationMin, populationGrowthRate);
		marathonMetrics.populationMax = Math.max(marathonMetrics.populationMax, populationGrowthRate);
		
		// Track market condition months
		if (marketCondition === 'boom') marathonMetrics.monthsInBoom++;
		else if (marketCondition === 'bust') marathonMetrics.monthsInBust++;
		else if (marketCondition === 'declining') marathonMetrics.monthsInDecline++;
		else if (marketCondition === 'stable') marathonMetrics.monthsInStable++;
		else if (marketCondition === 'stagnant') marathonMetrics.monthsInStagnant++;
		
		// Track best/worst months
		if (appreciation < marathonMetrics.worstAppreciation) {
			marathonMetrics.worstAppreciation = appreciation;
			marathonMetrics.worstAppreciationMonth = networkMonth;
		}
		if (appreciation > marathonMetrics.bestAppreciation) {
			marathonMetrics.bestAppreciation = appreciation;
			marathonMetrics.bestAppreciationMonth = networkMonth;
		}
		
		// Track portfolio
		marathonMetrics.peakPortfolioValue = Math.max(marathonMetrics.peakPortfolioValue, portfolioValue);
		marathonMetrics.troughPortfolioValue = Math.min(marathonMetrics.troughPortfolioValue, portfolioValue);
		
		// Record historical snapshot for charts
		marathonMetrics.history.push({
			month: networkMonth,
			networkValue: networkTotalPropertyValue,
			tokenPrice: tokenPrice,
			userNetWorth: balance + portfolioValue,
			marketCondition: marketCondition,
			ironOrePrice: ironOrePrice,
			reputationScore: networkReputation.score,
			propertyCount: properties.length,
		});
	}
	
	// SVG Chart helper functions for synopsis visualization
	function generateSparklinePath(data: number[], width: number, height: number, padding: number = 5): string {
		if (data.length === 0) return '';
		
		const min = Math.min(...data);
		const max = Math.max(...data);
		const range = max - min || 1;
		
		const xStep = (width - padding * 2) / (data.length - 1);
		
		const points = data.map((value, i) => {
			const x = padding + i * xStep;
			const y = height - padding - ((value - min) / range) * (height - padding * 2);
			return `${x},${y}`;
		});
		
		return `M ${points.join(' L ')}`;
	}
	
	function generateAreaPath(data: number[], width: number, height: number, padding: number = 5): string {
		if (data.length === 0) return '';
		
		const min = Math.min(...data);
		const max = Math.max(...data);
		const range = max - min || 1;
		
		const xStep = (width - padding * 2) / (data.length - 1);
		
		const points = data.map((value, i) => {
			const x = padding + i * xStep;
			const y = height - padding - ((value - min) / range) * (height - padding * 2);
			return `${x},${y}`;
		});
		
		// Close the path to create an area
		const firstX = padding;
		const lastX = padding + (data.length - 1) * xStep;
		return `M ${firstX},${height - padding} L ${points.join(' L ')} L ${lastX},${height - padding} Z`;
	}
	
	function getMarketConditionColor(condition: string): string {
		switch (condition) {
			case 'boom': return '#22c55e';
			case 'stable': return '#3b82f6';
			case 'stagnant': return '#eab308';
			case 'declining': return '#f97316';
			case 'bust': return '#ef4444';
			default: return '#6b7280';
		}
	}
	
	// Calculate the last dot position for sparkline charts
	function getSparklineLastDotY(data: number[], chartHeight: number, padding: number): number {
		if (data.length === 0) return chartHeight / 2;
		const min = Math.min(...data);
		const max = Math.max(...data);
		const range = max - min || 1;
		const lastValue = data[data.length - 1];
		return chartHeight - padding - ((lastValue - min) / range) * (chartHeight - 2 * padding);
	}
	
	// Calculate investor distribution for synopsis
	function calculateInvestorDistribution() {
		// Get all NPC portfolios plus the user
		const allInvestors: Array<{name: string; returnPercent: number; strategy: string; personality: string; startingValue: number; endingValue: number}> = [];
		
		// Add user's portfolio
		const userStarting = 100000;
		const userEnding = balance + portfolioValue;
		const userReturn = ((userEnding - userStarting) / userStarting) * 100;
		allInvestors.push({
			name: 'You',
			returnPercent: userReturn,
			strategy: 'Active participation',
			personality: 'User',
			startingValue: userStarting,
			endingValue: userEnding,
		});
		
		// Add NPC portfolios
		for (const [name, portfolio] of Object.entries(npcPortfolios)) {
			if (portfolio.totalInvested > 0 || portfolio.holdings > 0) {
				allInvestors.push({
					name,
					returnPercent: portfolio.returnPercent,
					strategy: portfolio.strategy,
					personality: portfolio.personality,
					startingValue: portfolio.startingValue,
					endingValue: portfolio.currentValue,
				});
			}
		}
		
		// Sort by return
		allInvestors.sort((a, b) => b.returnPercent - a.returnPercent);
		
		// Calculate statistics
		const returns = allInvestors.map(i => i.returnPercent);
		const positiveCount = returns.filter(r => r >= 0).length;
		const negativeCount = returns.filter(r => r < 0).length;
		const averageReturn = returns.length > 0 ? returns.reduce((a, b) => a + b, 0) / returns.length : 0;
		
		// Median calculation
		const sorted = [...returns].sort((a, b) => a - b);
		const median = sorted.length > 0 
			? sorted.length % 2 === 0 
				? (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2 
				: sorted[Math.floor(sorted.length / 2)]
			: 0;
		
		const best = allInvestors[0] || { name: 'N/A', returnPercent: 0 };
		const worst = allInvestors[allInvestors.length - 1] || { name: 'N/A', returnPercent: 0 };
		
		return {
			all: allInvestors,
			best: { name: best.name, returnPercent: best.returnPercent },
			worst: { name: worst.name, returnPercent: worst.returnPercent },
			median,
			averageReturn,
			positiveCount,
			negativeCount,
		};
	}
	
	// Generate the marathon synopsis
	function generateMarathonSynopsis() {
		const totalMonths = networkMonth;
		const totalYears = totalMonths / 12;
		const sessionDuration = formatElapsed(sessionElapsed);
		
		// Calculate market phases
		const marketPhases = [];
		if (marathonMetrics.monthsInBoom > 0) {
			marketPhases.push({phase: 'Boom', months: marathonMetrics.monthsInBoom, appreciation: 1.2});
		}
		if (marathonMetrics.monthsInStable > 0) {
			marketPhases.push({phase: 'Stable', months: marathonMetrics.monthsInStable, appreciation: 0.3});
		}
		if (marathonMetrics.monthsInStagnant > 0) {
			marketPhases.push({phase: 'Stagnant', months: marathonMetrics.monthsInStagnant, appreciation: 0});
		}
		if (marathonMetrics.monthsInDecline > 0) {
			marketPhases.push({phase: 'Declining', months: marathonMetrics.monthsInDecline, appreciation: -0.6});
		}
		if (marathonMetrics.monthsInBust > 0) {
			marketPhases.push({phase: 'Bust', months: marathonMetrics.monthsInBust, appreciation: -1.5});
		}
		
		// Calculate returns - use TOTAL net worth (balance + portfolioValue), not just token holdings
		// This matches the real-time calculation used throughout the simulation
		const startingNetWorth = 100000; // User always starts with $100k
		const endingNetWorth = balance + portfolioValue;
		const totalReturn = endingNetWorth - startingNetWorth;
		const totalReturnPercent = (totalReturn / startingNetWorth) * 100;
		
		// Get top NPC performers
		const npcEntries = Object.entries(npcPerformance);
		const topPerformers = npcEntries
			.filter(([_, perf]) => perf.decisions > 5)
			.map(([name, perf]) => ({
				name,
				successRate: perf.decisions > 0 ? (perf.successes / perf.decisions) * 100 : 0,
				decisions: perf.decisions
			}))
			.sort((a, b) => b.successRate - a.successRate)
			.slice(0, 3);
		
		const mostAdaptive = npcEntries
			.filter(([_, perf]) => perf.strategyAdjustments > 0)
			.map(([name, perf]) => ({
				name,
				adjustments: perf.strategyAdjustments
			}))
			.sort((a, b) => b.adjustments - a.adjustments)
			.slice(0, 3);
		
		// Generate stakeholder outcomes
		const hadBust = marathonMetrics.monthsInBust > 12;
		const hadSignificantDecline = marathonMetrics.monthsInDecline + marathonMetrics.monthsInBust > 24;
		const strongGrowth = totalReturnPercent > 100;
		
		// Calculate dividend yield over the period
		const totalDividends = marathonMetrics.totalDividends;
		const dividendYieldPercent = startingNetWorth > 0 
			? (totalDividends / startingNetWorth) * 100 
			: 0;
		const totalReturnWithDividends = totalReturnPercent + dividendYieldPercent;
		
		// Network grew even if individual portfolios didn't (due to new properties joining)
		// Calculate this directly since networkScale isn't declared yet
		const networkStartValue = marathonMetrics.startingNetworkValue;
		const networkEndValue = networkTotalPropertyValue;
		const networkGrowth = networkStartValue > 0 ? ((networkEndValue - networkStartValue) / networkStartValue) * 100 : 0;
		
		const stakeholders = {
			investors: {
				verdict: totalReturnWithDividends > 30 ? '✅ Strong' : 
					totalReturnWithDividends > 0 ? '✅ Positive' : 
					totalReturnWithDividends > -20 ? '⚠️ Challenged' : '⚠️ Stressed',
				details: totalReturnPercent >= 0 
					? `${totalReturnPercent.toFixed(0)}% token appreciation + ${dividendYieldPercent.toFixed(0)}% dividends = ${totalReturnWithDividends.toFixed(0)}% total return.`
					: networkGrowth > 0
						? `Token value: ${totalReturnPercent.toFixed(0)}%, but network grew ${networkGrowth.toFixed(0)}% and dividends of ${dividendYieldPercent.toFixed(0)}% provided income. Total economic return: ${totalReturnWithDividends.toFixed(0)}%.`
						: `Challenging market: ${totalReturnPercent.toFixed(0)}% token movement. Dividends of ${dividendYieldPercent.toFixed(0)}% provided ongoing income. OSF structure prevented forced selling.`
			},
			renters: {
				verdict: '✅ Protected',
				details: hadBust
					? 'Benefited from downturn — more housing options, potentially lower rents. OSF maintained property standards throughout.'
					: 'Stable tenancy with consistent property maintenance. Network structure provided reliability.'
			},
			tenants: {
				verdict: hadBust ? '✅ Opportunity' : '✅ Positive',
				details: hadBust
					? 'Rent-to-own participants could accelerate ownership during bust. Buying equity at discounted prices created long-term value.'
					: 'Steady equity building throughout. On track for ownership milestones.'
			},
			homeowners: {
				verdict: networkGrowth < -10 ? '⚠️ Paper Loss' : networkGrowth > 20 ? '✅ Strong' : '✅ Positive',
				details: networkGrowth < 0
					? `Property values declined ${Math.abs(networkGrowth).toFixed(0)}% but NO forced sales. OSF network absorbed stress without foreclosures. ${propertiesAdded} new homeowners still joined.`
					: `Property portfolio grew ${networkGrowth.toFixed(0)}% from $${(networkStartValue/1000000).toFixed(1)}M to $${(networkEndValue/1000000).toFixed(1)}M. ${propertiesAdded} homeowners joined the network.`
			},
			serviceProviders: {
				verdict: '✅ Stable',
				details: 'Consistent payment from network treasury regardless of market conditions. Essential work continued even during downturn.'
			},
			foundation: {
				verdict: overallHealthStatus === 'healthy' ? '✅ Healthy' : '⚠️ Tested',
				details: activeStrategies.length > 0
					? `Activated ${activeStrategies.length} self-healing strategies. Network maintained stability through coordination.`
					: 'Governance maintained network health. No major interventions required.'
			}
		};
		
		// Count healing activity
		const healingStrategiesUsed = activeStrategies.length;
		const exitRequestsHandled = exitQueue.filter(e => e.status !== 'pending').length;
		const successfulMatches = exitQueue.filter(e => e.status === 'matched' || e.status === 'filled').length;
		
		// Calculate network scale
		const startingValue = marathonMetrics.startingNetworkValue;
		const endingValue = networkTotalPropertyValue;
		const propertyValueGrowth = startingValue > 0 ? ((endingValue - startingValue) / startingValue) * 100 : 0;
		
		const networkScale = {
			propertiesUnderManagement: properties.length,
			startingPropertyValue: startingValue,
			totalPropertyValue: endingValue,
			propertyValueGrowth: propertyValueGrowth,
			activeRentalContracts: Math.round(properties.length * networkOccupancyRate),
			rentToOwnContracts: Math.round(properties.length * 0.15),  // ~15% are rent-to-own
			totalParticipants: npcRoster.length + 1,  // NPCs + user
			serviceProvidersActive: serviceProviderTypes.length,
		};
		
		// Generate mitigations based on what happened
		const mitigations: Array<{action: string; trigger: string; outcome: string; beneficiaries: string}> = [];
		
		// Diversification mitigation (always active)
		mitigations.push({
			action: 'Portfolio Diversification',
			trigger: `Spread across ${properties.length} properties in different Perth suburbs`,
			outcome: `No single property could cause catastrophic loss. Worst property decline offset by stable performers.`,
			beneficiaries: `${networkScale.totalParticipants} investors protected from concentration risk`,
		});
		
		// Liquidity during downturn
		if (liquidityPool.totalDeployed > 0) {
			mitigations.push({
				action: 'Liquidity Pool Activation',
				trigger: `${exitRequestsHandled} sellers needed to exit during market stress`,
				outcome: `$${liquidityPool.totalDeployed.toLocaleString()} deployed to absorb distressed sales at floor prices`,
				beneficiaries: `${exitRequestsHandled} sellers able to exit, preventing panic cascade`,
			});
		}
		
		// Buyer-seller matching
		if (successfulMatches > 0) {
			mitigations.push({
				action: 'Buyer-Seller Matching',
				trigger: `Sellers couldn't find buyers in thin market`,
				outcome: `Network matched ${successfulMatches} distressed sellers with opportunistic buyers`,
				beneficiaries: `Sellers got exit, buyers got discounted entry, network maintained liquidity`,
			});
		}
		
		// Rent-to-own acceleration during bust
		if (hadBust) {
			mitigations.push({
				action: 'Rent-to-Own Acceleration',
				trigger: `Property values declined during ${marathonMetrics.monthsInBust}-month bust`,
				outcome: `Tenants could buy equity at discounted prices, accelerating path to ownership`,
				beneficiaries: `${networkScale.rentToOwnContracts} rent-to-own tenants building equity faster`,
			});
		}
		
		// Continuous rental income
		mitigations.push({
			action: 'Rental Income Continuity',
			trigger: `${networkScale.activeRentalContracts} active rental contracts maintained`,
			outcome: `Rental yields continued flowing even during market downturn`,
			beneficiaries: `Investors received income regardless of property value fluctuations`,
		});
		
		// No forced sales
		if (hadSignificantDecline) {
			mitigations.push({
				action: 'No Forced Sales',
				trigger: `Property values declined ${Math.abs(marathonMetrics.worstAppreciation * 100).toFixed(1)}% in worst month`,
				outcome: `Zero foreclosures. Collective ownership absorbed individual stress.`,
				beneficiaries: `${properties.length} properties and their owners protected from forced liquidation`,
			});
		}
		
		// Service provider payments
		mitigations.push({
			action: 'Service Provider Stability',
			trigger: `${networkScale.serviceProvidersActive} service providers contracted for maintenance`,
			outcome: `Network treasury ensured consistent payment regardless of market conditions`,
			beneficiaries: `Service providers had reliable income, properties maintained to standard`,
		});
		
		// Generate counterfactual
		const withoutOSF = hadBust
			? `Without OSF: In traditional markets, the ${marathonMetrics.monthsInBust}-month bust would have caused foreclosures for overleveraged owners, stranded investors with illiquid assets, and disrupted tenancies as landlords went into distress. WA mining towns saw 70-82% price drops in 2015-2019 with mass foreclosures. With OSF: ${exitRequestsHandled} exits facilitated, ${properties.length} properties maintained, zero foreclosures.`
			: hadSignificantDecline
				? `Without OSF: The ${marathonMetrics.monthsInDecline + marathonMetrics.monthsInBust}-month downturn would have trapped individual investors. Banks don't match buyers with sellers — they foreclose. OSF's coordination prevented this. With OSF: $${liquidityPool.totalDeployed.toLocaleString()} liquidity deployed, ${successfulMatches} matches made.`
				: `Without OSF: Individual property investors would face concentration risk and illiquidity. OSF's diversification across ${properties.length} properties and token structure provided both safety and flexibility.`;
		
		// ========== COOPERATIVE OUTCOMES ==========
		// Calculate human impact metrics - what the network actually achieved for people
		
		// Families housed = properties * occupancy rate
		const familiesHoused = Math.round(properties.length * networkOccupancyRate);
		
		// Rent-to-own participants who progressed (simulated based on time)
		const rentToOwnParticipants = Math.round(properties.length * 0.15);
		const rentToOwnCompletions = Math.floor(rentToOwnParticipants * (totalYears / 8)); // ~8 years to complete
		
		// Equity accessed by homeowners (simulated based on property turnover)
		const equityAccessedByHomeowners = Math.round(propertiesAdded * 0.4 * 150000); // 40% of new properties are equity access
		
		// Total dividends distributed across all investors
		const totalNetworkDividends = totalDividends * (npcRoster.length + 1); // Rough estimate for all participants
		
		// Crises survived (busts + significant declines)
		const crisesSurvived = (marathonMetrics.monthsInBust > 6 ? 1 : 0) + 
			(marathonMetrics.monthsInDecline > 12 ? 1 : 0) +
			(marathonMetrics.monthsInStagnant > 18 ? 1 : 0);
		
		// Self-healing activations
		const selfHealingActivations = activeStrategies.length + healingStrategiesUsed;
		
		// Calculate user's contribution
		const userCapitalDeployed = startingNetWorth - balance; // How much they invested vs held as cash
		const homesEnabledByUser = userCapitalDeployed / (networkTotalPropertyValue / properties.length); // Fractional homes funded
		const userHeldDuringDownturns = marathonMetrics.monthsInBust + marathonMetrics.monthsInDecline > 0; // Did they stay?
		const userStabilityScore = Math.round(
			(userHeldDuringDownturns ? 40 : 0) +
			(totalReturnPercent >= 0 ? 20 : 10) +
			(portfolioValue > 0 ? 30 : 0) + // Still invested
			(totalYears >= 10 ? 10 : totalYears) // Long-term commitment
		);
		
		// Determine user's contribution title based on behavior
		let userContributionTitle = 'Participant';
		let userContributionDescription = 'You participated in the network.';
		
		if (userStabilityScore >= 80 && crisesSurvived >= 2) {
			userContributionTitle = 'Network Anchor';
			userContributionDescription = `Your steady capital helped the network weather ${crisesSurvived} market downturns without panic selling.`;
		} else if (userStabilityScore >= 70 && homesEnabledByUser >= 1) {
			userContributionTitle = 'Housing Enabler';
			userContributionDescription = `Your capital helped fund ${homesEnabledByUser.toFixed(1)} property shares, enabling families to find housing.`;
		} else if (userStabilityScore >= 60) {
			userContributionTitle = 'Steady Contributor';
			userContributionDescription = 'Your patient capital contributed to network stability throughout the simulation.';
		} else if (portfolioValue > 0) {
			userContributionTitle = 'Active Participant';
			userContributionDescription = 'You maintained investment in the network, contributing to collective ownership.';
		}
		
		// Calculate network health grade
		const networkHealthScore = Math.round(
			(networkReputation.score * 0.3) + // Reputation
			(networkOccupancyRate * 100 * 0.2) + // Occupancy
			(networkGrowth > 0 ? 20 : 10) + // Growth
			(crisesSurvived > 0 && properties.length >= 15 ? 20 : 10) + // Resilience
			(familiesHoused >= 20 ? 10 : familiesHoused / 2) // Scale
		);
		
		let networkHealthGrade = 'C';
		if (networkHealthScore >= 85) networkHealthGrade = 'A';
		else if (networkHealthScore >= 75) networkHealthGrade = 'A-';
		else if (networkHealthScore >= 65) networkHealthGrade = 'B+';
		else if (networkHealthScore >= 55) networkHealthGrade = 'B';
		else if (networkHealthScore >= 45) networkHealthGrade = 'B-';
		else if (networkHealthScore >= 35) networkHealthGrade = 'C+';
		
		// Collective outcomes object
		const collectiveOutcomes = {
			familiesHoused,
			rentToOwnParticipants,
			rentToOwnCompletions,
			equityAccessedByHomeowners,
			totalNetworkDividends,
			crisesSurvived,
			selfHealingActivations,
			evictions: 0, // OSF prevents evictions
			foreclosures: 0, // No foreclosures in cooperative model
		};
		
		// User contribution object
		const userContribution = {
			capitalDeployed: userCapitalDeployed,
			homesEnabled: homesEnabledByUser,
			stabilityScore: userStabilityScore,
			title: userContributionTitle,
			description: userContributionDescription,
			heldDuringDownturns: userHeldDuringDownturns,
			monthsInNetwork: totalMonths,
		};
		
		// Network health object
		const networkHealth = {
			grade: networkHealthGrade,
			score: networkHealthScore,
			resilience: crisesSurvived > 0 ? 'Tested & Proven' : 'Untested',
			stability: networkReputation.score >= 70 ? 'Strong' : networkReputation.score >= 50 ? 'Moderate' : 'Challenged',
		};
		
		marathonSynopsis = {
			totalMonths,
			totalYears,
			sessionDuration,
			networkScale,
			marketPhases,
			ironOreRange: {
				min: marathonMetrics.ironOreMin,
				max: marathonMetrics.ironOreMax,
				final: ironOrePrice
			},
			populationRange: {
				min: marathonMetrics.populationMin,
				max: marathonMetrics.populationMax,
				final: populationGrowthRate
			},
			worstMonth: {
				month: marathonMetrics.worstAppreciationMonth,
				condition: 'bust',
				appreciation: marathonMetrics.worstAppreciation * 100
			},
			bestMonth: {
				month: marathonMetrics.bestAppreciationMonth,
				condition: 'boom',
				appreciation: marathonMetrics.bestAppreciation * 100
			},
			startingValue: startingNetWorth,
			endingValue: endingNetWorth,
			totalReturn,
			totalReturnPercent,
			dividendsCollected: marathonMetrics.totalDividends,
			mitigations,
			stakeholders,
			healingStrategiesUsed,
			exitRequestsHandled,
			liquidityDeployed: liquidityPool.totalDeployed,
			successfulMatches,
			topPerformers,
			mostAdaptive,
			majorEvents: marathonMetrics.majorEvents.slice(-10),
			investorDistribution: calculateInvestorDistribution(),
			history: marathonMetrics.history,
			reputation: {
				finalScore: networkReputation.score,
				trend: networkReputation.trend,
				investorSatisfaction: networkReputation.investorSatisfaction,
				homeownerSatisfaction: networkReputation.homeownerSatisfaction,
				renterSatisfaction: networkReputation.renterSatisfaction,
				tenantSatisfaction: networkReputation.tenantSatisfaction,
				wordOfMouthMultiplier: networkReputation.wordOfMouthMultiplier,
				propertiesAdded,
				propertiesExited,
				netGrowth: propertiesAdded - propertiesExited,
			},
			withoutOSF,
			// NEW: Cooperative outcomes
			collectiveOutcomes,
			userContribution,
			networkHealth,
		};
		
		showMarathonSynopsis = true;
	}
	
	// Calculate marathon progress
	let marathonProgress = $derived(marathonMode ? Math.min(100, (networkMonth / marathonTargetMonths) * 100) : 0);
	let marathonElapsed = $derived(marathonStartTime ? Math.floor((Date.now() - marathonStartTime.getTime()) / 1000) : 0);
	let sessionElapsed = $derived(Math.floor((Date.now() - sessionStartTime.getTime()) / 1000));
	
	// Format elapsed time
	function formatElapsed(seconds: number): string {
		const hrs = Math.floor(seconds / 3600);
		const mins = Math.floor((seconds % 3600) / 60);
		const secs = seconds % 60;
		if (hrs > 0) return `${hrs}h ${mins}m ${secs}s`;
		if (mins > 0) return `${mins}m ${secs}s`;
		return `${secs}s`;
	}
	
	// Auth state (from auth store)
	let authConfig = $state<AuthConfig | null>(null);
	
	// Computed auth state
	let isSignedUp = $derived(auth.isAuthenticated);
	let currentUser = $derived(auth.user);
	let displayName = $derived(auth.user?.display_name || auth.user?.email?.split('@')[0] || 'User');
	let userId = $derived(auth.user?.id || '');
	
	// Local auth form state (for inline dev login)
	let loginEmail = $state('');
	let loginDisplayName = $state('');
	let loginError = $state<string | null>(null);
	
	// Simulation state
	let showSignup = $derived(!auth.isAuthenticated);
	let showBuyDialog = $state(false);
	let showFeedbackDialog = $state(false);
	let showFeedbackDetailDialog = $state(false);
	let selectedProperty = $state<any>(null);
	let selectedFeedback = $state<any>(null);
	let buyAmount = $state(1000);
	let isLoading = $state(false);
	
	// === PROPERTY MANAGEMENT STATE ===
	let showAddPropertyDialog = $state(false);
	let showEditPropertyDialog = $state(false);
	let showDeletePropertyDialog = $state(false);
	let showManagePropertiesDialog = $state(false);
	let editingProperty = $state<any>(null);
	
	// New property form state
	let newPropertyForm = $state({
		address: '',
		suburb: '',
		postcode: '',
		state: 'WA',
		property_type: 'house',
		bedrooms: 3,
		bathrooms: 2,
		car_spaces: 1,
		land_size_sqm: 400,
		floor_size_sqm: 150,
		valuation_aud: 500000,
		yield_percent: 4.0,
		year_built: 2020,
		features: [] as string[],
		highlights: [] as string[],
		council_rates: 2500,
		water_rates: 1000,
		strata_fees: 0,
		estimated_rent_pw: 500,
	});
	
	const propertyTypes = ['house', 'apartment', 'townhouse', 'unit', 'villa', 'duplex', 'land'];
	const australianStates = ['WA', 'NSW', 'VIC', 'QLD', 'SA', 'TAS', 'NT', 'ACT'];
	const availableFeatures = [
		'Air conditioning', 'Balcony', 'Courtyard', 'Garage', 'Garden', 'Gym', 
		'Home theatre', 'Intercom', 'Ocean views', 'Pool', 'River views', 
		'Secure parking', 'Smart home', 'Solar panels', 'Study', 'Alfresco', 
		'Built-in robes', 'Dishwasher', 'Ducted heating', 'Evaporative cooling',
		'Floorboards', 'NBN', 'Outdoor entertaining', 'Shed', 'Split system'
	];
	const availableHighlights = [
		'Stunning views', 'Premium location', 'North-facing', 'Architect-designed',
		'Resort-style pool', 'Walk to beach', 'Walk to shops', 'Walk to schools',
		'Quiet street', 'Corner block', 'Renovated', 'Low maintenance',
		'Family-friendly', 'Modern finishes', 'Abundant natural light'
	];
	
	function resetPropertyForm() {
		newPropertyForm = {
			address: '',
			suburb: '',
			postcode: '',
			state: 'WA',
			property_type: 'house',
			bedrooms: 3,
			bathrooms: 2,
			car_spaces: 1,
			land_size_sqm: 400,
			floor_size_sqm: 150,
			valuation_aud: 500000,
			yield_percent: 4.0,
			year_built: 2020,
			features: [],
			highlights: [],
			council_rates: 2500,
			water_rates: 1000,
			strata_fees: 0,
			estimated_rent_pw: 500,
		};
	}
	
	function openAddProperty() {
		resetPropertyForm();
		showAddPropertyDialog = true;
	}
	
	function handleAddProperty() {
		if (!newPropertyForm.address || !newPropertyForm.suburb) return;
		
		const newProperty = {
			id: `prop-${Date.now()}`,
			address: newPropertyForm.address,
			suburb: newPropertyForm.suburb,
			postcode: newPropertyForm.postcode || '6000',
			state: newPropertyForm.state,
			property_type: newPropertyForm.property_type,
			bedrooms: newPropertyForm.bedrooms,
			bathrooms: newPropertyForm.bathrooms,
			car_spaces: newPropertyForm.car_spaces,
			land_size_sqm: newPropertyForm.land_size_sqm,
			floor_size_sqm: newPropertyForm.floor_size_sqm,
			valuation_aud: newPropertyForm.valuation_aud,
			token_price: 1.00,
			yield_percent: newPropertyForm.yield_percent,
			year_built: newPropertyForm.year_built,
			features: [...newPropertyForm.features],
			highlights: [...newPropertyForm.highlights],
			photos_count: Math.floor(Math.random() * 15) + 5,
			listing_status: 'active',
			page_views: Math.floor(Math.random() * 2000) + 500,
			// WA-specific costs
			council_rates: newPropertyForm.council_rates,
			water_rates: newPropertyForm.water_rates,
			strata_fees: newPropertyForm.strata_fees,
			estimated_rent_pw: newPropertyForm.estimated_rent_pw,
			// Price history starts with current listing
			price_history: [
				{ date: new Date().toISOString().split('T')[0], event: 'Listed', price: newPropertyForm.valuation_aud, change_percent: null }
			],
		};
		
		properties = [...properties, newProperty];
		addNetworkEvent('property_added', 'User', 'Network', `Added property: ${newProperty.address}, ${newProperty.suburb}`, newProperty.valuation_aud);
		showAddPropertyDialog = false;
		resetPropertyForm();
	}
	
	function openEditProperty(property: any) {
		editingProperty = property;
		newPropertyForm = {
			address: property.address,
			suburb: property.suburb,
			postcode: property.postcode || '',
			state: property.state,
			property_type: property.property_type,
			bedrooms: property.bedrooms,
			bathrooms: property.bathrooms,
			car_spaces: property.car_spaces || 1,
			land_size_sqm: property.land_size_sqm || 0,
			floor_size_sqm: property.floor_size_sqm || 0,
			valuation_aud: property.valuation_aud,
			yield_percent: property.yield_percent,
			year_built: property.year_built || 2020,
			features: property.features || [],
			highlights: property.highlights || [],
			council_rates: property.council_rates || 2500,
			water_rates: property.water_rates || 1000,
			strata_fees: property.strata_fees || 0,
			estimated_rent_pw: property.estimated_rent_pw || 500,
		};
		showEditPropertyDialog = true;
	}
	
	function handleEditProperty() {
		if (!editingProperty || !newPropertyForm.address || !newPropertyForm.suburb) return;
		
		properties = properties.map(p => 
			p.id === editingProperty.id 
				? {
					...p,
					address: newPropertyForm.address,
					suburb: newPropertyForm.suburb,
					postcode: newPropertyForm.postcode,
					state: newPropertyForm.state,
					property_type: newPropertyForm.property_type,
					bedrooms: newPropertyForm.bedrooms,
					bathrooms: newPropertyForm.bathrooms,
					car_spaces: newPropertyForm.car_spaces,
					land_size_sqm: newPropertyForm.land_size_sqm,
					floor_size_sqm: newPropertyForm.floor_size_sqm,
					valuation_aud: newPropertyForm.valuation_aud,
					yield_percent: newPropertyForm.yield_percent,
					year_built: newPropertyForm.year_built,
					features: [...newPropertyForm.features],
					highlights: [...newPropertyForm.highlights],
					council_rates: newPropertyForm.council_rates,
					water_rates: newPropertyForm.water_rates,
					strata_fees: newPropertyForm.strata_fees,
					estimated_rent_pw: newPropertyForm.estimated_rent_pw,
				}
				: p
		);
		
		addNetworkEvent('property_updated', 'User', 'Network', `Updated property: ${newPropertyForm.address}`, 0);
		showEditPropertyDialog = false;
		editingProperty = null;
		resetPropertyForm();
	}
	
	function toggleHighlight(highlight: string) {
		if (newPropertyForm.highlights.includes(highlight)) {
			newPropertyForm.highlights = newPropertyForm.highlights.filter(h => h !== highlight);
		} else {
			newPropertyForm.highlights = [...newPropertyForm.highlights, highlight];
		}
	}
	
	function toggleFeature(feature: string) {
		if (newPropertyForm.features.includes(feature)) {
			newPropertyForm.features = newPropertyForm.features.filter(f => f !== feature);
		} else {
			newPropertyForm.features = [...newPropertyForm.features, feature];
		}
	}
	
	function openDeleteProperty(property: any) {
		editingProperty = property;
		showDeletePropertyDialog = true;
	}
	
	function handleDeleteProperty() {
		if (!editingProperty) return;
		
		// Check if property is used in holdings, rentals, etc.
		const isInHoldings = holdings.some(h => h.property_id === editingProperty.id);
		const isRented = renterProperty?.id === editingProperty.id;
		
		if (isInHoldings) {
			// Sell holdings first
			holdings = holdings.filter(h => h.property_id !== editingProperty.id);
		}
		
		if (isRented) {
			renterProperty = null;
			renterLeaseEnd = 12;
			renterLeaseStart = null;
		}
		
		const removedAddress = editingProperty.address;
		properties = properties.filter(p => p.id !== editingProperty.id);
		addNetworkEvent('property_removed', 'User', 'Network', `Removed property: ${removedAddress}`, 0);
		
		showDeletePropertyDialog = false;
		editingProperty = null;
	}
	
	// === RENTER SIMULATION STATE ===
	let renterProperty = $state<any>(null);
	let renterMonthlyRent = $state(2400);
	let renterWeeklyRent = $derived(Math.round(renterMonthlyRent / 4.33));
	let renterMonthsRented = $state(0);
	let renterWeeksRented = $state(0);
	let renterTotalPaid = $state(0);
	let renterLeaseEnd = $state(12);  // months until lease ends
	let renterLeaseStart = $state<string | null>(null);
	let renterBondAmount = $derived(renterWeeklyRent * 4);
	let renterNextInspection = $state(3);  // months until next inspection
	let renterMaintenanceRequests = $state<Array<{id: number, issue: string, status: string, submitted: string}>>([]);
	let renterShowUpgradePrompt = $state(false);
	let showRenterSwapDialog = $state(false);
	
	// Renter transaction/activity log
	let renterTransactions = $state<Array<{
		id: number,
		type: 'contract' | 'bond' | 'rent_advance' | 'rent_weekly' | 'inspection' | 'maintenance' | 'renewal',
		description: string,
		amount: number | null,
		date: string,
		status: 'completed' | 'pending' | 'upcoming'
	}>>([]);
	
	// === TENANT SIMULATION STATE ===
	let tenantRentAmount = $state(2200);  // Monthly rent
	let tenantEquityPercent = $state(0);  // Equity accumulated
	let tenantMonthsRented = $state(0);
	let tenantTargetProperty = $state<any>(null);
	let tenantSavingsVsRent = $state(0);
	
	// === HOMEOWNER SIMULATION STATE ===
	let homeownerProperty = $state<any>(null);  // Selected property with details
	let homeownerPropertyValue = $state(850000);
	let homeownerMortgageBalance = $state(520000);
	let homeownerEquityAccessAmount = $state(0);
	let homeownerEquityAvailable = $derived(homeownerPropertyValue * 0.8 - homeownerMortgageBalance);
	let homeownerMonthlyPayment = $state(2800);
	let homeownerRentalIncome = $state(0);
	let homeownerIsRenting = $state(false);
	let homeownerPropertyListed = $state(false);  // Whether property is listed on network
	
	// === CUSTODIAN SIMULATION STATE ===
	let custodianManagedProperties = $state(12);
	
	// Comprehensive service provider types with associated tasks
	const serviceProviderTypes = [
		// Property Management
		{ type: 'Property Manager', category: 'Management', tasks: ['Quarterly inspection', 'Tenant enquiry', 'Lease management', 'Rent collection follow-up'] },
		{ type: 'Strata Manager', category: 'Management', tasks: ['Strata meeting prep', 'AGM preparation', 'Levy collection', 'By-law compliance'] },
		{ type: 'Building Manager', category: 'Management', tasks: ['Common area maintenance', 'Security oversight', 'Contractor coordination'] },
		
		// Trades - Plumbing & Water
		{ type: 'Plumber', category: 'Trades', tasks: ['Blocked drain repair', 'Hot water system repair', 'Leaking tap fix', 'Toilet repair', 'Pipe replacement'] },
		{ type: 'Gas Fitter', category: 'Trades', tasks: ['Gas appliance service', 'Gas leak inspection', 'Heater installation'] },
		
		// Trades - Electrical
		{ type: 'Electrician', category: 'Trades', tasks: ['Smoke alarm check', 'Power point repair', 'Switchboard upgrade', 'Lighting installation', 'Safety switch test'] },
		{ type: 'HVAC Technician', category: 'Trades', tasks: ['Air conditioner service', 'Heating system repair', 'Duct cleaning', 'Thermostat replacement'] },
		
		// Trades - Building
		{ type: 'Carpenter', category: 'Trades', tasks: ['Door repair', 'Cabinet fix', 'Deck maintenance', 'Fence repair', 'Built-in wardrobe install'] },
		{ type: 'Tiler', category: 'Trades', tasks: ['Tile replacement', 'Grout repair', 'Bathroom retiling', 'Splashback installation'] },
		{ type: 'Painter', category: 'Trades', tasks: ['Interior repaint', 'Touch-up painting', 'Exterior painting', 'Feature wall'] },
		{ type: 'Plasterer', category: 'Trades', tasks: ['Crack repair', 'Ceiling patch', 'Wall repair', 'Cornicing'] },
		{ type: 'Roofer', category: 'Trades', tasks: ['Roof leak repair', 'Gutter cleaning', 'Tile replacement', 'Roof inspection'] },
		
		// Outdoor & Garden
		{ type: 'Gardener', category: 'Outdoor', tasks: ['Lawn mowing', 'Hedge trimming', 'Garden bed maintenance', 'Weeding', 'Mulching'] },
		{ type: 'Arborist', category: 'Outdoor', tasks: ['Tree trimming', 'Tree removal', 'Stump grinding', 'Tree health assessment'] },
		{ type: 'Landscaper', category: 'Outdoor', tasks: ['Garden design', 'Retaining wall', 'Paving', 'Irrigation install'] },
		{ type: 'Pool Technician', category: 'Outdoor', tasks: ['Pool cleaning', 'Chemical balance', 'Filter service', 'Pool equipment repair'] },
		
		// Cleaning & Maintenance
		{ type: 'Cleaner', category: 'Cleaning', tasks: ['End of lease clean', 'Regular clean', 'Carpet cleaning', 'Window cleaning'] },
		{ type: 'Pest Control', category: 'Cleaning', tasks: ['Termite inspection', 'Pest treatment', 'Rodent control', 'Cockroach treatment', 'Spider spray'] },
		{ type: 'Rubbish Removal', category: 'Cleaning', tasks: ['Hard rubbish collection', 'Green waste removal', 'Skip bin delivery', 'Junk removal'] },
		
		// Security & Safety
		{ type: 'Locksmith', category: 'Security', tasks: ['Lock change', 'Key cutting', 'Lock repair', 'Security upgrade'] },
		{ type: 'Security Installer', category: 'Security', tasks: ['Alarm installation', 'CCTV setup', 'Intercom repair', 'Access control'] },
		
		// Professional Services
		{ type: 'Building Inspector', category: 'Professional', tasks: ['Building compliance check', 'Pre-purchase inspection', 'Defect report'] },
		{ type: 'Legal Advisor', category: 'Professional', tasks: ['Lease renewal review', 'Dispute resolution', 'Contract review', 'Tribunal preparation'] },
		{ type: 'Accountant', category: 'Professional', tasks: ['Quarterly accounts', 'Tax preparation', 'Strata levy audit', 'Financial reporting'] },
		{ type: 'Valuer', category: 'Professional', tasks: ['Property valuation', 'Rental appraisal', 'Market assessment'] },
	];
	
	// Helper to format role name (removes gender suffixes like _female, _male)
	function formatRoleName(role: string): string {
		return role
			.replace(/_female$/, '')
			.replace(/_male$/, '')
			.replace(/_\d+$/, '')  // Remove trailing numbers like investor_2
			.replace(/_/g, ' ');
	}
	
	// Helper to get random task for a service type
	function getRandomTask(): { task: string; serviceType: string; category: string } {
		const provider = serviceProviderTypes[Math.floor(Math.random() * serviceProviderTypes.length)];
		const task = provider.tasks[Math.floor(Math.random() * provider.tasks.length)];
		return { task, serviceType: provider.type, category: provider.category };
	}
	
	// Service tasks with property linking
	type ServiceTask = {
		id: number;
		propertyId: string;
		propertyAddress: string;
		task: string;
		priority: 'low' | 'medium' | 'high';
		due: string;
		serviceType: string;
		category: string;
		cost: number;
	};
	
	let custodianPendingTasks = $state<ServiceTask[]>([]);
	let custodianMonthlyFees = $state(4800);
	let custodianOccupancyRate = $state(96);
	
	// === FOUNDATION SIMULATION STATE ===
	let foundationStakeAmount = $state(100000);
	let foundationLockPeriod = $state(12);  // months
	let foundationCurrentYield = $state(5.2);
	let foundationTotalStaked = $state(0);
	let foundationEarnings = $state(0);
	let foundationMonthsStaked = $state(0);
	
	// === TRANSACTION LOGS FOR ALL ROLES ===
	type InvestorTxType = 'buy' | 'sell' | 'dividend' | 'auto_invest' | 'fee';
	let investorTransactions = $state<Array<{
		id: number,
		type: InvestorTxType,
		description: string,
		amount: number | null,
		tokens?: number,
		date: string,
		status: 'completed' | 'pending' | 'processing'
	}>>([]);
	
	type TenantTxType = 'rent' | 'equity_accrued' | 'milestone' | 'inspection' | 'maintenance';
	let tenantTransactions = $state<Array<{
		id: number,
		type: TenantTxType,
		description: string,
		amount: number | null,
		date: string,
		status: 'completed' | 'pending' | 'upcoming'
	}>>([]);
	
	type HomeownerTxType = 'equity_access' | 'rental_income' | 'mortgage' | 'appreciation' | 'expense' | 'osf_deposit';
	let homeownerTransactions = $state<Array<{
		id: number,
		type: HomeownerTxType,
		description: string,
		amount: number | null,
		date: string,
		status: 'completed' | 'pending' | 'processing'
	}>>([]);
	
	type CustodianTxType = 'fee_collected' | 'task_completed' | 'property_added' | 'inspection' | 'expense' | 'payout' | 'maintenance';
	let custodianTransactions = $state<Array<{
		id: number,
		type: CustodianTxType,
		description: string,
		amount: number | null,
		date: string,
		status: 'completed' | 'pending' | 'processing',
		propertyId?: string,
		propertyAddress?: string,
		serviceType?: string,
	}>>([]);
	
	type FoundationTxType = 'stake' | 'unstake' | 'yield' | 'compound' | 'bonus' | 'governance';
	let foundationTransactions = $state<Array<{
		id: number,
		type: FoundationTxType,
		description: string,
		amount: number | null,
		date: string,
		status: 'completed' | 'pending' | 'locked'
	}>>([]);
	
	// Projection calculator state
	let projectedYield = $state(4.0);  // User-adjustable yield %
	let monthlyContribution = $state(0);  // Monthly additional investment
	let projectionYears = $state(10);  // Projection timeframe
	
	// Recurring investment state
	let recurringAmount = $state(500);  // Monthly auto-invest amount
	let recurringPropertyId = $state('');  // Property to auto-invest in
	let recurringEnabled = $state(false);  // Whether auto-invest is active
	let showRecurringDialog = $state(false);
	let simulatedMonths = $state(0);  // How many months have been simulated
	
	// Feedback state
	let activeTab = $state<'dashboard' | 'network' | 'governance' | 'leaderboard' | 'feedback' | 'ledger' | 'thinking' | 'health'>('dashboard');
	let feedbackFilter = $state('all');
	let feedbackSort = $state('upvotes');
	let newFeedbackTitle = $state('');
	let newFeedbackDescription = $state('');
	let newFeedbackType = $state<'bug' | 'enhancement' | 'question'>('enhancement');
	
	// =====================================================
	// EXPLORATION ACHIEVEMENTS SYSTEM
	// Rewards understanding and exploration, not "winning"
	// =====================================================
	
	type Achievement = {
		id: string;
		title: string;
		description: string;
		icon: string;
		unlocked: boolean;
		unlockedAt?: number; // month when unlocked
	};
	
	let achievements = $state<Achievement[]>([
		{ id: 'first_investment', title: 'First Steps', description: 'Made your first investment in the network', icon: '🌱', unlocked: false },
		{ id: 'dividend_received', title: 'Passive Income', description: 'Received your first dividend payment', icon: '💰', unlocked: false },
		{ id: 'weathered_storm', title: 'Weathered the Storm', description: 'Held steady through a market downturn', icon: '🌧️', unlocked: false },
		{ id: 'witnessed_boom', title: 'Rising Tide', description: 'Experienced a market boom', icon: '📈', unlocked: false },
		{ id: 'saw_self_healing', title: 'Network Resilience', description: 'Witnessed the network activate a self-healing strategy', icon: '🛡️', unlocked: false },
		{ id: 'explored_roles', title: 'Perspective Shift', description: 'Explored at least 3 different participant roles', icon: '👁️', unlocked: false },
		{ id: 'full_cycle', title: 'Full Economic Cycle', description: 'Experienced boom, stable, and bust market phases', icon: '🔄', unlocked: false },
		{ id: 'long_term', title: 'Long-Term Thinker', description: 'Completed a 10-year simulation', icon: '🎯', unlocked: false },
		{ id: 'network_anchor', title: 'Network Anchor', description: 'Maintained position through 3+ market downturns', icon: '⚓', unlocked: false },
		{ id: 'community_builder', title: 'Community Builder', description: 'Saw the network grow to 30+ properties', icon: '🏘️', unlocked: false },
	]);
	
	let recentAchievement = $state<Achievement | null>(null);
	let showAchievementToast = $state(false);
	let rolesExplored = $state<Set<SimRole>>(new Set(['investor'])); // Track which roles user has viewed
	let hasReceivedDividend = $state(false);
	let downturnsSurvived = $state(0);
	
	// Floating AI Chat
	let showFloatingChat = $state(false);
	let floatingChatMinimized = $state(false);
	
	// =====================================================
	// INSIGHT MOMENTS SYSTEM
	// Educational popups that explain what's happening
	// =====================================================
	
	type InsightMoment = {
		id: string;
		title: string;
		content: string;
		context: string;
		icon: string;
	};
	
	let currentInsight = $state<InsightMoment | null>(null);
	let showInsightModal = $state(false);
	let insightsShown = $state<Set<string>>(new Set()); // Track which insights have been shown
	
	const insightDefinitions: Record<string, InsightMoment> = {
		market_boom: {
			id: 'market_boom',
			title: 'Market Boom Detected',
			content: 'Iron ore prices are high and population is growing. This typically leads to increased property demand and rising values in WA.',
			context: 'In cooperative ownership, booms benefit everyone proportionally. No one is left out because they couldn\'t afford entry.',
			icon: '📈'
		},
		market_bust: {
			id: 'market_bust',
			title: 'Market Downturn Beginning',
			content: 'Economic conditions are weakening. Traditional property investors might face forced sales, but OSF\'s structure provides protection.',
			context: 'The network\'s liquidity pool and self-healing mechanisms activate during downturns to prevent cascading failures.',
			icon: '📉'
		},
		self_healing: {
			id: 'self_healing',
			title: 'Network Self-Healing Activated',
			content: 'The network detected stress and automatically activated a protection strategy to help affected participants.',
			context: 'Unlike traditional markets where individuals face problems alone, OSF coordinates responses collectively.',
			icon: '🛡️'
		},
		property_growth: {
			id: 'property_growth',
			title: 'Network Growing',
			content: 'A new property has joined the OSF network, increasing diversification for all token holders.',
			context: 'More properties = more diversification = lower risk for everyone. The network grows when reputation is strong.',
			icon: '🏠'
		},
		dividend_paid: {
			id: 'dividend_paid',
			title: 'Dividend Distribution',
			content: 'Rental income from occupied properties has been distributed to token holders based on their ownership share.',
			context: 'This passive income continues regardless of property value fluctuations — a key benefit of the OSF model.',
			icon: '💰'
		},
		year_milestone: {
			id: 'year_milestone',
			title: 'Year Complete',
			content: 'Another year of the simulation has passed. The network continues to operate autonomously.',
			context: 'Long-term stability is the goal. OSF is designed for decades, not days.',
			icon: '📅'
		},
	};
	
	// Show an insight if it hasn't been shown yet
	function showInsight(insightId: string) {
		if (insightsShown.has(insightId)) return;
		
		const insight = insightDefinitions[insightId];
		if (!insight) return;
		
		currentInsight = insight;
		showInsightModal = true;
		insightsShown.add(insightId);
		insightsShown = new Set(insightsShown); // Trigger reactivity
		
		// Auto-dismiss after 6 seconds during marathon
		if (marathonMode) {
			setTimeout(() => {
				if (showInsightModal && currentInsight?.id === insightId) {
					showInsightModal = false;
				}
			}, 6000);
		}
	}
	
	// Check for insight triggers (called during simulation)
	function checkInsights() {
		// Only show insights occasionally to avoid spam
		if (Math.random() > 0.3) return; // 30% chance to show
		
		// Market boom
		if (marketCondition === 'boom' && !insightsShown.has('market_boom')) {
			showInsight('market_boom');
			return;
		}
		
		// Market bust
		if (marketCondition === 'bust' && !insightsShown.has('market_bust')) {
			showInsight('market_bust');
			return;
		}
		
		// Self-healing
		if (activeStrategies.length > 0 && !insightsShown.has('self_healing')) {
			showInsight('self_healing');
			return;
		}
		
		// Year milestone (every 12 months)
		if (networkMonth > 0 && networkMonth % 12 === 0 && networkMonth <= 60) {
			// Only show for first 5 years
			showInsight('year_milestone');
			return;
		}
	}
	
	// =====================================================
	// ONBOARDING MODAL
	// Shown to first-time users to explain the simulation
	// =====================================================
	
	let showOnboardingModal = $state(false);
	let onboardingDismissed = $state(false);
	
	// Check if user has seen onboarding before
	function checkOnboarding() {
		if (typeof localStorage !== 'undefined') {
			const seen = localStorage.getItem('osf_onboarding_seen');
			if (!seen) {
				showOnboardingModal = true;
			} else {
				onboardingDismissed = true;
			}
		}
	}
	
	// Dismiss onboarding and remember choice
	function dismissOnboarding(remember: boolean = false) {
		showOnboardingModal = false;
		onboardingDismissed = true;
		if (remember && typeof localStorage !== 'undefined') {
			localStorage.setItem('osf_onboarding_seen', 'true');
		}
	}
	
	// Quick Demo mode (12 months fast)
	let quickDemoMode = $state(false);
	let savedMarathonTarget = $state(120); // Save original target
	let savedMarathonInterval = $state(1300); // Save original interval
	
	function startQuickDemo() {
		dismissOnboarding(false);
		quickDemoMode = true;
		
		// Save current settings
		savedMarathonTarget = marathonTargetMonths;
		savedMarathonInterval = marathonInterval;
		
		// Set quick demo settings (12 months, fast interval)
		marathonTargetMonths = 12;
		marathonInterval = 200; // Much faster
		
		// Start the marathon with modified settings
		startMarathon();
	}
	
	function startFullMarathon() {
		dismissOnboarding(false);
		quickDemoMode = false;
		
		// Ensure default settings
		marathonTargetMonths = 120;
		marathonInterval = 1300;
		
		startMarathon();
	}
	
	// Check and unlock achievements
	function checkAchievements() {
		const unlock = (id: string) => {
			const achievement = achievements.find(a => a.id === id);
			if (achievement && !achievement.unlocked) {
				achievement.unlocked = true;
				achievement.unlockedAt = networkMonth;
				recentAchievement = achievement;
				showAchievementToast = true;
				setTimeout(() => showAchievementToast = false, 4000);
				achievements = [...achievements]; // Trigger reactivity
			}
		};
		
		// First investment
		if (portfolioValue > 0) unlock('first_investment');
		
		// Dividend received
		if (hasReceivedDividend) unlock('dividend_received');
		
		// Weathered storm (held during bust/decline)
		if ((marketCondition === 'bust' || marketCondition === 'declining') && portfolioValue > 0) {
			unlock('weathered_storm');
		}
		
		// Witnessed boom
		if (marketCondition === 'boom') unlock('witnessed_boom');
		
		// Saw self-healing
		if (activeStrategies.length > 0) unlock('saw_self_healing');
		
		// Explored roles (3+)
		if (rolesExplored.size >= 3) unlock('explored_roles');
		
		// Full economic cycle
		if (marathonMetrics.monthsInBoom > 0 && 
			marathonMetrics.monthsInStable > 0 && 
			(marathonMetrics.monthsInBust > 0 || marathonMetrics.monthsInDecline > 0)) {
			unlock('full_cycle');
		}
		
		// Long-term thinker (10 years)
		if (networkMonth >= 120) unlock('long_term');
		
		// Network anchor (3+ downturns)
		if (downturnsSurvived >= 3 && portfolioValue > 0) unlock('network_anchor');
		
		// Community builder (30+ properties)
		if (properties.length >= 30) unlock('community_builder');
	}
	
	// Track role exploration
	function trackRoleExplored(role: SimRole) {
		rolesExplored.add(role);
		rolesExplored = new Set(rolesExplored); // Trigger reactivity
		checkAchievements();
	}
	
	// Derived: count unlocked achievements
	let unlockedAchievementsCount = $derived(achievements.filter(a => a.unlocked).length);
	let newComment = $state('');
	
	// Feedback items
	let feedbackItems = $state([
		{
			id: "fb-001",
			author_name: "OSF Team",
			title: "Add dividend payout simulation",
			description: "It would be great to see simulated quarterly dividends based on property yields. This would help users understand the passive income aspect of fractional property ownership.",
			feedback_type: "enhancement",
			ai_category: "trading",
			ai_priority: "high",
			ai_summary: "Request for quarterly dividend simulation to demonstrate passive income from property yields.",
			status: "planned",
			upvotes: 42,
			downvotes: 3,
			comment_count: 8,
			user_vote: 0,
			created_at: "2026-01-13",
		},
		{
			id: "fb-002",
			author_name: "Demo User",
			title: "Property detail page not loading images",
			description: "When I click on a property to view details, the images don't load. I see broken image icons instead. Using Chrome on Windows 11.",
			feedback_type: "bug",
			ai_category: "ui",
			ai_priority: "medium",
			ai_summary: "Image loading issue on property detail pages in Chrome/Windows 11.",
			status: "in_progress",
			upvotes: 18,
			downvotes: 0,
			comment_count: 4,
			user_vote: 0,
			created_at: "2026-01-16",
		},
		{
			id: "fb-003",
			author_name: "Investor123",
			title: "Add price alerts for properties",
			description: "Would love to set price alerts for specific properties so I know when to buy or sell based on my target prices.",
			feedback_type: "enhancement",
			ai_category: "trading",
			ai_priority: "medium",
			ai_summary: "Feature request for customizable price alerts on properties.",
			status: "open",
			upvotes: 31,
			downvotes: 2,
			comment_count: 12,
			user_vote: 0,
			created_at: "2026-01-15",
		},
		{
			id: "fb-004",
			author_name: "PropExpert",
			title: "Show historical property valuations",
			description: "It would be helpful to see how property values have changed over time. A chart showing historical valuations would help make investment decisions.",
			feedback_type: "enhancement",
			ai_category: "ui",
			ai_priority: "low",
			ai_summary: "Request for historical valuation charts on property pages.",
			status: "open",
			upvotes: 24,
			downvotes: 1,
			comment_count: 6,
			user_vote: 0,
			created_at: "2026-01-14",
		},
		{
			id: "fb-005",
			author_name: "NewUser42",
			title: "Mobile app version?",
			description: "Any plans for a mobile app? Would be great to track my portfolio on the go.",
			feedback_type: "question",
			ai_category: "general",
			ai_priority: "medium",
			ai_summary: "Inquiry about mobile application availability.",
			status: "open",
			upvotes: 56,
			downvotes: 0,
			comment_count: 3,
			user_vote: 0,
			created_at: "2026-01-12",
		},
	]);
	
	let feedbackComments = $state<Record<string, any[]>>({
		"fb-001": [
			{ id: "c1", author_name: "SmartMoney", content: "This would be amazing! I want to see how much passive income I could generate.", created_at: "2026-01-14", is_official: false },
			{ id: "c2", author_name: "OSF Team", content: "Great suggestion! We're planning to add this in the next release. Dividends will be calculated quarterly based on rental yields.", created_at: "2026-01-15", is_official: true },
		],
		"fb-002": [
			{ id: "c3", author_name: "TechSupport", content: "Thanks for reporting! Can you check if this happens in incognito mode?", created_at: "2026-01-16", is_official: true },
		],
	});
	
	// =====================================================
	// COMMUNITY FEEDBACK SYSTEM - NPC-Generated Feedback
	// =====================================================
	
	// Community sentiment tracking
	let communitySentiment = $state({
		score: 0.7,  // -1 to +1 (negative to positive)
		trend: 'stable' as 'rising' | 'stable' | 'falling',
		lastUpdated: 0,
		feedbackVolume: 0,
		resolutionRate: 0.75,
		governanceParticipation: 0.45,
	});
	
	// Feedback templates by category and market condition
	const feedbackTemplates = {
		bug: {
			boom: [
				{ title: "Portfolio loading slowly during peak hours", desc: "Dashboard takes 5+ seconds to load when market is active. Others experiencing this?" },
				{ title: "Token purchase confirmation delayed", desc: "Bought tokens 10 minutes ago but still showing as pending. High volume issue?" },
				{ title: "Price chart not updating in real-time", desc: "Chart shows stale data, need to refresh manually to see latest prices." },
			],
			stable: [
				{ title: "Statement PDF formatting issue", desc: "Monthly statement has overlapping text in the transaction section." },
				{ title: "Mobile view cuts off property images", desc: "On my phone, property photos are cropped on the right side." },
				{ title: "Filter doesn't save between sessions", desc: "I set suburb filter but it resets when I come back." },
			],
			bust: [
				{ title: "Exit request stuck in processing", desc: "Submitted exit request 3 days ago, still showing 'processing'. Support not responding." },
				{ title: "Valuation seems incorrect after update", desc: "Property value dropped 15% overnight but comparable sales don't show this?" },
				{ title: "Can't access my transaction history", desc: "Getting error when trying to view older transactions. Need this for tax." },
			],
		},
		enhancement: {
			boom: [
				{ title: "Auto-invest feature request", desc: "Would love to set up recurring investments. Market's hot and I don't want to miss opportunities." },
				{ title: "More property listings needed", desc: "There's high demand but limited inventory. Can we onboard more properties?" },
				{ title: "Portfolio rebalancing tools", desc: "Need tools to rebalance my holdings across different properties automatically." },
			],
			stable: [
				{ title: "Dividend reinvestment option", desc: "Instead of cash dividends, option to auto-reinvest into more tokens." },
				{ title: "Better suburb comparison tools", desc: "Would help to compare yield/growth across different suburbs." },
				{ title: "Tax report generation", desc: "End of financial year reporting would save a lot of time." },
			],
			bust: [
				{ title: "Early warning alerts for market changes", desc: "Would've helped to get alerts when market started declining." },
				{ title: "Partial exit options needed", desc: "Can't exit my full position, but would take partial exit at discount." },
				{ title: "Buyer matching for distressed sales", desc: "Connect those wanting to exit with new buyers willing to buy at current prices." },
			],
		},
		question: {
			boom: [
				{ title: "Is now a good time to invest more?", desc: "Market seems hot - should I be adding or waiting for correction?" },
				{ title: "How are property values calculated?", desc: "Values going up fast - is this based on sales or something else?" },
				{ title: "What happens if I invest at the peak?", desc: "Worried about buying high. How does OSF protect against this?" },
			],
			stable: [
				{ title: "When are dividends distributed?", desc: "New investor here - when do I receive my first dividend payment?" },
				{ title: "How does the 49% threshold work?", desc: "If I'm a homeowner, what happens when I hit 49% tokenized?" },
				{ title: "Can I transfer tokens to family?", desc: "Want to gift some tokens to my kids - is this possible?" },
			],
			bust: [
				{ title: "Should I be worried about my investment?", desc: "Values dropping - will OSF step in to stabilize things?" },
				{ title: "What if I need to exit urgently?", desc: "Life circumstances changed - what are my options for quick exit?" },
				{ title: "How does OSF handle market downturns?", desc: "First time through a bust - how does the self-healing work?" },
			],
		},
		governance: {
			boom: [
				{ title: "Proposal: Increase max property allocation", desc: "With demand high, should we allow more properties per investor?" },
				{ title: "Vote: Expedited onboarding for new properties", desc: "Can we fast-track new property listings to meet demand?" },
			],
			stable: [
				{ title: "Proposal: Reduce service fee from 8% to 6%", desc: "Network is stable - time to pass savings to token holders?" },
				{ title: "Vote: Add commercial property tier", desc: "Diversification into commercial real estate - thoughts?" },
			],
			bust: [
				{ title: "Emergency: Activate liquidity support", desc: "Many members need exits - should we deploy emergency liquidity?" },
				{ title: "Proposal: Temporary exit fee waiver", desc: "Help distressed sellers exit without penalty during downturn." },
			],
		},
	};
	
	// NPC feedback authors with personalities
	const feedbackAuthors = [
		{ name: 'Sarah Chen', personality: 'Conservative', feedbackStyle: 'Thoughtful, risk-aware' },
		{ name: 'Marcus Thompson', personality: 'Aggressive', feedbackStyle: 'Direct, action-oriented' },
		{ name: 'Emily Rodriguez', personality: 'Balanced', feedbackStyle: 'Constructive, solutions-focused' },
		{ name: 'David Park', personality: 'Opportunist', feedbackStyle: 'Strategic, timing-aware' },
		{ name: 'Janet Williams', personality: 'Passive', feedbackStyle: 'Supportive, patient' },
		{ name: 'Michael Foster', personality: 'Speculator', feedbackStyle: 'Urgent, opportunity-seeking' },
		{ name: 'Lisa Chang', personality: 'Conservative', feedbackStyle: 'Cautious, detailed' },
		{ name: 'NewInvestor42', personality: 'Newbie', feedbackStyle: 'Curious, learning' },
		{ name: 'PerthMiner_FIFO', personality: 'FIFO Worker', feedbackStyle: 'Practical, time-constrained' },
		{ name: 'FirstHomeDreamer', personality: 'Renter', feedbackStyle: 'Hopeful, pathway-focused' },
		{ name: 'RetiredTeacher', personality: 'Income-focused', feedbackStyle: 'Dividend-focused, stable' },
		{ name: 'TechStartupFounder', personality: 'Early Adopter', feedbackStyle: 'Feature-hungry, innovative' },
	];
	
	// Governor AI response templates
	const governorResponses = {
		bug: [
			"Thanks for reporting this. Our team is investigating and will update you within 24 hours.",
			"We've identified the issue and a fix is being deployed. Should be resolved shortly.",
			"Apologies for the inconvenience. This is a known issue during high-traffic periods - we're scaling infrastructure.",
		],
		enhancement: [
			"Great suggestion! This aligns with our roadmap. Adding to the backlog for prioritization.",
			"We've heard similar requests from the community. This is now under active development.",
			"Interesting idea. We'll include this in our next community survey to gauge broader interest.",
		],
		question: [
			"Great question! [Detailed answer would be provided based on the specific query]",
			"This is covered in our FAQ, but happy to clarify: [Answer]",
			"As a network, we [explanation]. Does that help answer your question?",
		],
		governance: [
			"This proposal has been formally submitted for community vote. Voting opens next week.",
			"The Foundation is reviewing this proposal. We'll share our recommendation before the vote.",
			"Important proposal. We're gathering data to help the community make an informed decision.",
		],
	};
	
	// Generate community feedback based on current conditions
	function generateCommunityFeedback() {
		// Base probability - 30% chance each month
		if (Math.random() > 0.30) return;
		
		// Determine feedback type based on conditions
		const typeWeights = {
			bug: marketCondition === 'bust' ? 0.35 : marketCondition === 'boom' ? 0.25 : 0.20,
			enhancement: marketCondition === 'boom' ? 0.35 : 0.30,
			question: marketCondition === 'bust' ? 0.30 : 0.25,
			governance: overallHealthStatus !== 'healthy' ? 0.20 : 0.10,
		};
		
		// Select type using string to avoid TS narrowing issues
		const rand = Math.random();
		let cumulative = 0;
		let selectedType = 'question' as string;
		for (const [type, weight] of Object.entries(typeWeights)) {
			cumulative += weight;
			if (rand < cumulative) {
				selectedType = type;
				break;
			}
		}
		
		// Map market condition to template key
		const conditionKey = (marketCondition === 'boom' ? 'boom' : 
			marketCondition === 'bust' || marketCondition === 'declining' ? 'bust' : 'stable') as 'boom' | 'stable' | 'bust';
		
		// Get templates based on type
		const templateCategory = selectedType === 'governance' ? 'governance' : selectedType as 'bug' | 'enhancement' | 'question';
		const categoryTemplates = feedbackTemplates[templateCategory as keyof typeof feedbackTemplates];
		const templates = categoryTemplates ? categoryTemplates[conditionKey] : null;
		if (!templates || templates.length === 0) return;
		
		// Select random template
		const template = templates[Math.floor(Math.random() * templates.length)];
		
		// Select random author
		const author = feedbackAuthors[Math.floor(Math.random() * feedbackAuthors.length)];
		
		// Determine feedback properties
		const isGovernance = selectedType === 'governance';
		const isBug = selectedType === 'bug';
		
		// Create feedback item
		const newFeedback = {
			id: 'fb-gen-' + Date.now() + Math.random().toString(36).substring(7),
			author_name: author.name,
			title: template.title,
			description: template.desc,
			feedback_type: isGovernance ? 'enhancement' : selectedType,
			ai_category: isGovernance ? 'governance' : 'general',
			ai_priority: (isBug && marketCondition === 'bust') ? 'high' : 
				isGovernance ? 'high' : 'medium',
			ai_summary: template.desc.slice(0, 80) + '...',
			status: 'open' as const,
			upvotes: Math.floor(Math.random() * 15) + 1,
			downvotes: Math.floor(Math.random() * 3),
			comment_count: 0,
			user_vote: 0,
			created_at: getFormattedDate(networkMonth),
			generated: true,  // Mark as NPC-generated
			author_personality: author.personality,
			market_context: marketCondition,
		};
		
		feedbackItems = [newFeedback, ...feedbackItems];
		communitySentiment.feedbackVolume++;
		
		// Log to AI thinking
		addThinking('Governor', 'observation',
			`New community ${selectedType}: "${template.title}" from ${author.name} (${author.personality})`,
			60);
		
		// Schedule Governor response (35% of actionable items)
		if (Math.random() < 0.35) {
			scheduleGovernorResponse(newFeedback.id, selectedType);
		}
		
		// Check if bug cluster should trigger self-healing
		const recentBugs = feedbackItems.filter(f => 
			f.feedback_type === 'bug' && 
			f.status === 'open' &&
			(f as any).generated
		).length;
		
		if (recentBugs >= 3 && isBug) {
			addThinking('Governor', 'analysis',
				`Bug cluster detected (${recentBugs} open issues). Triggering diagnostic review.`,
				75);
			// Could trigger self-healing here
		}
	}
	
	// Schedule a Governor AI response to feedback
	function scheduleGovernorResponse(feedbackId: string, feedbackType: string) {
		// Simulate async response (in real app would call AI)
		const responses = governorResponses[feedbackType as keyof typeof governorResponses] || governorResponses.question;
		const response = responses[Math.floor(Math.random() * responses.length)];
		
		// Add response as comment
		const comments = feedbackComments[feedbackId] || [];
		comments.push({
			id: 'c-gov-' + Date.now(),
			author_name: 'Governor AI',
			content: response,
			created_at: getFormattedDate(networkMonth),
			is_official: true,
		});
		feedbackComments[feedbackId] = [...comments];
		
		// Update feedback status
		const item = feedbackItems.find(f => f.id === feedbackId);
		if (item) {
			if (feedbackType === 'question') {
				item.status = 'resolved';
			} else if (feedbackType === 'bug') {
				item.status = 'in_progress';
			} else {
				item.status = 'planned';
			}
			item.comment_count++;
			feedbackItems = [...feedbackItems];
		}
		
		// Update resolution rate
		const resolved = feedbackItems.filter(f => f.status === 'resolved' || f.status === 'completed').length;
		communitySentiment.resolutionRate = feedbackItems.length > 0 ? resolved / feedbackItems.length : 0.75;
		
		addThinking('Governor', 'action',
			`Responded to community ${feedbackType}: "${item?.title?.slice(0, 30)}..."`,
			65);
	}
	
	// Update community sentiment based on conditions
	function updateCommunitySentiment() {
		// Base sentiment on market conditions and network health
		let baseScore = 0.5;
		
		// Market condition impact
		if (marketCondition === 'boom') baseScore += 0.2;
		else if (marketCondition === 'stable') baseScore += 0.1;
		else if (marketCondition === 'declining') baseScore -= 0.1;
		else if (marketCondition === 'bust') baseScore -= 0.25;
		
		// Network health impact
		if (overallHealthStatus === 'healthy') baseScore += 0.1;
		else if (overallHealthStatus === 'warning') baseScore -= 0.1;
		else if (overallHealthStatus === 'critical') baseScore -= 0.2;
		
		// Resolution rate impact
		baseScore += (communitySentiment.resolutionRate - 0.5) * 0.2;
		
		// Clamp to -1 to 1
		const newScore = Math.max(-1, Math.min(1, baseScore));
		
		// Determine trend
		const oldScore = communitySentiment.score;
		const trend = newScore > oldScore + 0.05 ? 'rising' : 
			newScore < oldScore - 0.05 ? 'falling' : 'stable';
		
		communitySentiment = {
			...communitySentiment,
			score: newScore,
			trend,
			lastUpdated: networkMonth,
		};
	}
	
	// Get sentiment label and color
	function getSentimentDisplay(score: number): { label: string; color: string; emoji: string } {
		if (score >= 0.6) return { label: 'Very Positive', color: 'text-green-600', emoji: '😊' };
		if (score >= 0.3) return { label: 'Positive', color: 'text-green-500', emoji: '🙂' };
		if (score >= -0.1) return { label: 'Neutral', color: 'text-gray-500', emoji: '😐' };
		if (score >= -0.4) return { label: 'Concerned', color: 'text-amber-500', emoji: '😟' };
		return { label: 'Anxious', color: 'text-red-500', emoji: '😰' };
	}

	// Portfolio state
	let balance = $state(100000);
	let portfolioValue = $state(0);
	let totalReturn = $state(0);
	let totalReturnPercent = $state(0);
	let holdings = $state<any[]>([]);
	let transactions = $state<any[]>([]);

	// Properties - Diverse mix representing Perth market
	// Distribution: Entry-level (30%), Mid-range (40%), Premium (30%)
	let properties = $state([
		// === ENTRY-LEVEL APARTMENTS ($350k-$480k) ===
		{
			id: "prop-001",
			address: "12/45 Railway Parade",
			suburb: "Midland",
			postcode: "6056",
			state: "WA",
			property_type: "unit",
			bedrooms: 1,
			bathrooms: 1,
			car_spaces: 1,
			land_size_sqm: 0,
			floor_size_sqm: 52,
			valuation_aud: 285000,
			token_price: 1.00,
			yield_percent: 5.8,
			year_built: 2008,
			features: ['Air conditioning', 'Carport', 'Built-in robes'],
			highlights: ['High rental yield', 'Near train station', 'Low strata fees', 'First home buyer friendly'],
			photos_count: 6,
			listing_status: 'active',
			page_views: 892,
			council_rates: 1200,
			water_rates: 650,
			strata_fees: 1800,
			estimated_rent_pw: 320,
			price_history: [
				{ date: '2024-03-15', event: 'Listed', price: 285000, change_percent: null },
				{ date: '2019-06-20', event: 'Sold', price: 235000, change_percent: null },
			],
		},
		{
			id: "prop-002",
			address: "3/18 Spencer Street",
			suburb: "Balga",
			postcode: "6061",
			state: "WA",
			property_type: "unit",
			bedrooms: 2,
			bathrooms: 1,
			car_spaces: 1,
			land_size_sqm: 0,
			floor_size_sqm: 68,
			valuation_aud: 340000,
			token_price: 1.00,
			yield_percent: 5.6,
			year_built: 1985,
			features: ['Air conditioning', 'Renovated kitchen', 'Private courtyard'],
			highlights: ['Affordable entry point', 'Recently renovated', 'Strong rental demand', 'Close to shops'],
			photos_count: 8,
			listing_status: 'active',
			page_views: 756,
			council_rates: 1300,
			water_rates: 700,
			strata_fees: 1500,
			estimated_rent_pw: 370,
			price_history: [
				{ date: '2024-05-01', event: 'Listed', price: 340000, change_percent: null },
				{ date: '2021-02-10', event: 'Sold', price: 285000, change_percent: null },
			],
		},
		{
			id: "prop-003",
			address: "7/92 Champion Drive",
			suburb: "Armadale",
			postcode: "6112",
			state: "WA",
			property_type: "apartment",
			bedrooms: 2,
			bathrooms: 1,
			car_spaces: 1,
			land_size_sqm: 0,
			floor_size_sqm: 72,
			valuation_aud: 320000,
			token_price: 1.00,
			yield_percent: 5.9,
			year_built: 2012,
			features: ['Air conditioning', 'Balcony', 'Secure complex'],
			highlights: ['Entry-level investment', 'Near Armadale Central', 'Modern build', 'Train station access'],
			photos_count: 7,
			listing_status: 'active',
			page_views: 634,
			council_rates: 1250,
			water_rates: 680,
			strata_fees: 2100,
			estimated_rent_pw: 365,
			price_history: [
				{ date: '2024-04-20', event: 'Listed', price: 320000, change_percent: null },
				{ date: '2020-08-15', event: 'Sold', price: 275000, change_percent: null },
			],
		},
		{
			id: "prop-004",
			address: "21/5 Stirling Highway",
			suburb: "Fremantle",
			postcode: "6160",
			state: "WA",
			property_type: "apartment",
			bedrooms: 1,
			bathrooms: 1,
			car_spaces: 1,
			land_size_sqm: 0,
			floor_size_sqm: 48,
			valuation_aud: 395000,
			token_price: 1.00,
			yield_percent: 5.2,
			year_built: 2016,
			features: ['Air conditioning', 'Balcony', 'Intercom', 'Lift access'],
			highlights: ['Freo lifestyle', 'Walk to markets', 'Modern amenities', 'Pet-friendly complex'],
			photos_count: 9,
			listing_status: 'active',
			page_views: 1245,
			council_rates: 1450,
			water_rates: 720,
			strata_fees: 2400,
			estimated_rent_pw: 400,
			price_history: [
				{ date: '2024-06-01', event: 'Listed', price: 395000, change_percent: null },
				{ date: '2020-11-20', event: 'Sold', price: 345000, change_percent: null },
			],
		},
		// === MID-RANGE UNITS & VILLAS ($450k-$650k) ===
		{
			id: "prop-005",
			address: "15 Beach Road",
			suburb: "Scarborough",
			postcode: "6019",
			state: "WA",
			property_type: "apartment",
			bedrooms: 2,
			bathrooms: 1,
			car_spaces: 1,
			land_size_sqm: 0,
			floor_size_sqm: 85,
			valuation_aud: 550000,
			token_price: 1.00,
			yield_percent: 4.9,
			year_built: 2020,
			features: ['Air conditioning', 'Balcony', 'Intercom', 'Pool'],
			highlights: ['Beach lifestyle', 'Modern finishes', 'Secure complex', 'Walk to cafes'],
			photos_count: 8,
			listing_status: 'active',
			page_views: 2156,
			council_rates: 1800,
			water_rates: 800,
			strata_fees: 3600,
			estimated_rent_pw: 580,
			price_history: [
				{ date: '2024-08-01', event: 'Listed', price: 550000, change_percent: null },
				{ date: '2020-02-15', event: 'Sold (off plan)', price: 495000, change_percent: null },
			],
		},
		{
			id: "prop-006",
			address: "4/28 Central Walk",
			suburb: "Joondalup",
			postcode: "6027",
			state: "WA",
			property_type: "apartment",
			bedrooms: 2,
			bathrooms: 2,
			car_spaces: 2,
			land_size_sqm: 0,
			floor_size_sqm: 95,
			valuation_aud: 485000,
			token_price: 1.00,
			yield_percent: 5.1,
			year_built: 2018,
			features: ['Air conditioning', 'Balcony', 'Secure parking', 'Storage'],
			highlights: ['Walk to Lakeside', 'Near ECU campus', 'Modern complex', 'Public transport access'],
			photos_count: 10,
			listing_status: 'active',
			page_views: 1567,
			council_rates: 1650,
			water_rates: 780,
			strata_fees: 2800,
			estimated_rent_pw: 480,
			price_history: [
				{ date: '2024-07-15', event: 'Listed', price: 485000, change_percent: null },
				{ date: '2021-09-01', event: 'Sold', price: 425000, change_percent: null },
			],
		},
		{
			id: "prop-007",
			address: "2/15 Marina Boulevard",
			suburb: "Rockingham",
			postcode: "6168",
			state: "WA",
			property_type: "villa",
			bedrooms: 3,
			bathrooms: 1,
			car_spaces: 2,
			land_size_sqm: 180,
			floor_size_sqm: 110,
			valuation_aud: 520000,
			token_price: 1.00,
			yield_percent: 5.0,
			year_built: 2005,
			features: ['Air conditioning', 'Courtyard', 'Double garage', 'Renovated'],
			highlights: ['Lock and leave', 'Near foreshore', 'Low maintenance', 'Renovated throughout'],
			photos_count: 11,
			listing_status: 'active',
			page_views: 1823,
			council_rates: 1900,
			water_rates: 850,
			strata_fees: 1200,
			estimated_rent_pw: 510,
			price_history: [
				{ date: '2024-05-20', event: 'Listed', price: 520000, change_percent: null },
				{ date: '2022-03-10', event: 'Sold', price: 455000, change_percent: null },
			],
		},
		{
			id: "prop-008",
			address: "1/42 Mandurah Terrace",
			suburb: "Mandurah",
			postcode: "6210",
			state: "WA",
			property_type: "duplex",
			bedrooms: 3,
			bathrooms: 2,
			car_spaces: 2,
			land_size_sqm: 220,
			floor_size_sqm: 125,
			valuation_aud: 495000,
			token_price: 1.00,
			yield_percent: 5.3,
			year_built: 2015,
			features: ['Air conditioning', 'Alfresco', 'Double garage', 'Modern kitchen'],
			highlights: ['Waterway lifestyle', 'Near shopping precinct', 'Quality finishes', 'Great for families'],
			photos_count: 12,
			listing_status: 'active',
			page_views: 1456,
			council_rates: 1750,
			water_rates: 820,
			strata_fees: 800,
			estimated_rent_pw: 510,
			price_history: [
				{ date: '2024-06-10', event: 'Listed', price: 495000, change_percent: null },
				{ date: '2021-11-25', event: 'Sold', price: 420000, change_percent: null },
			],
		},
		{
			id: "prop-009",
			address: "8/55 Wanneroo Road",
			suburb: "Wanneroo",
			postcode: "6065",
			state: "WA",
			property_type: "villa",
			bedrooms: 3,
			bathrooms: 2,
			car_spaces: 2,
			land_size_sqm: 200,
			floor_size_sqm: 115,
			valuation_aud: 545000,
			token_price: 1.00,
			yield_percent: 4.8,
			year_built: 2019,
			features: ['Air conditioning', 'Alfresco', 'Double garage', 'Theatre room'],
			highlights: ['Near Wanneroo Town Centre', 'Modern design', 'Low strata', 'Family friendly'],
			photos_count: 10,
			listing_status: 'active',
			page_views: 1234,
			council_rates: 1850,
			water_rates: 870,
			strata_fees: 1000,
			estimated_rent_pw: 520,
			price_history: [
				{ date: '2024-07-01', event: 'Listed', price: 545000, change_percent: null },
				{ date: '2022-01-15', event: 'Sold', price: 485000, change_percent: null },
			],
		},
		// === MID-RANGE TOWNHOUSES ($650k-$850k) ===
		{
			id: "prop-010",
			address: "8 Park Lane",
			suburb: "Subiaco",
			postcode: "6008",
			state: "WA",
			property_type: "townhouse",
			bedrooms: 3,
			bathrooms: 2,
			car_spaces: 2,
			land_size_sqm: 220,
			floor_size_sqm: 165,
			valuation_aud: 780000,
			token_price: 1.00,
			yield_percent: 4.3,
			year_built: 2018,
			features: ['Air conditioning', 'Courtyard', 'Garage', 'Study'],
			highlights: ['Leafy Subiaco street', 'Low-maintenance living', 'Walk to Subiaco Oval', 'Quality fixtures'],
			photos_count: 10,
			listing_status: 'active',
			page_views: 1523,
			council_rates: 2400,
			water_rates: 950,
			strata_fees: 2400,
			estimated_rent_pw: 720,
			price_history: [
				{ date: '2024-05-10', event: 'Listed', price: 780000, change_percent: null },
				{ date: '2022-08-20', event: 'Sold', price: 695000, change_percent: null },
				{ date: '2018-06-01', event: 'Sold (new)', price: 620000, change_percent: null },
			],
		},
		{
			id: "prop-011",
			address: "15/8 Bay View Terrace",
			suburb: "Claremont",
			postcode: "6010",
			state: "WA",
			property_type: "townhouse",
			bedrooms: 3,
			bathrooms: 2,
			car_spaces: 2,
			land_size_sqm: 180,
			floor_size_sqm: 145,
			valuation_aud: 850000,
			token_price: 1.00,
			yield_percent: 4.0,
			year_built: 2020,
			features: ['Air conditioning', 'Rooftop terrace', 'Designer kitchen', 'Home office'],
			highlights: ['Premium Claremont address', 'Walk to Quarter', 'Architect designed', 'North facing'],
			photos_count: 14,
			listing_status: 'active',
			page_views: 2345,
			council_rates: 2800,
			water_rates: 1000,
			strata_fees: 3200,
			estimated_rent_pw: 750,
			price_history: [
				{ date: '2024-08-15', event: 'Listed', price: 850000, change_percent: null },
				{ date: '2020-10-01', event: 'Sold (off plan)', price: 795000, change_percent: null },
			],
		},
		{
			id: "prop-012",
			address: "3/22 Douglas Avenue",
			suburb: "South Perth",
			postcode: "6151",
			state: "WA",
			property_type: "townhouse",
			bedrooms: 3,
			bathrooms: 2,
			car_spaces: 2,
			land_size_sqm: 195,
			floor_size_sqm: 155,
			valuation_aud: 820000,
			token_price: 1.00,
			yield_percent: 4.2,
			year_built: 2017,
			features: ['Air conditioning', 'Balcony', 'Double garage', 'Wine cellar'],
			highlights: ['River precinct', 'City views', 'Quality build', 'Walk to Zoo'],
			photos_count: 12,
			listing_status: 'active',
			page_views: 1987,
			council_rates: 2650,
			water_rates: 980,
			strata_fees: 2800,
			estimated_rent_pw: 740,
			price_history: [
				{ date: '2024-06-20', event: 'Listed', price: 820000, change_percent: null },
				{ date: '2021-04-15', event: 'Sold', price: 725000, change_percent: null },
			],
		},
		// === FAMILY HOUSES ($650k-$950k) ===
		{
			id: "prop-013",
			address: "27 Karri Way",
			suburb: "Baldivis",
			postcode: "6171",
			state: "WA",
			property_type: "house",
			bedrooms: 4,
			bathrooms: 2,
			car_spaces: 2,
			land_size_sqm: 450,
			floor_size_sqm: 185,
			valuation_aud: 650000,
			token_price: 1.00,
			yield_percent: 4.6,
			year_built: 2018,
			features: ['Air conditioning', 'Theatre room', 'Double garage', 'Alfresco', 'Solar panels'],
			highlights: ['Growing suburb', 'Family friendly', 'Near schools', 'Modern estate'],
			photos_count: 15,
			listing_status: 'active',
			page_views: 1876,
			council_rates: 2200,
			water_rates: 950,
			strata_fees: 0,
			estimated_rent_pw: 600,
			price_history: [
				{ date: '2024-05-01', event: 'Listed', price: 650000, change_percent: null },
				{ date: '2021-07-20', event: 'Sold', price: 545000, change_percent: null },
			],
		},
		{
			id: "prop-014",
			address: "15 Banksia Drive",
			suburb: "Ellenbrook",
			postcode: "6069",
			state: "WA",
			property_type: "house",
			bedrooms: 4,
			bathrooms: 2,
			car_spaces: 2,
			land_size_sqm: 500,
			floor_size_sqm: 195,
			valuation_aud: 620000,
			token_price: 1.00,
			yield_percent: 4.8,
			year_built: 2016,
			features: ['Air conditioning', 'Pool', 'Double garage', 'Shed', 'Solar'],
			highlights: ['Established neighbourhood', 'Near Woodlake Village', 'Great for families', 'Side access'],
			photos_count: 13,
			listing_status: 'active',
			page_views: 1654,
			council_rates: 2100,
			water_rates: 920,
			strata_fees: 0,
			estimated_rent_pw: 580,
			price_history: [
				{ date: '2024-06-15', event: 'Listed', price: 620000, change_percent: null },
				{ date: '2020-09-01', event: 'Sold', price: 495000, change_percent: null },
			],
		},
		{
			id: "prop-015",
			address: "8 Olive Street",
			suburb: "Morley",
			postcode: "6062",
			state: "WA",
			property_type: "house",
			bedrooms: 3,
			bathrooms: 2,
			car_spaces: 2,
			land_size_sqm: 650,
			floor_size_sqm: 165,
			valuation_aud: 750000,
			token_price: 1.00,
			yield_percent: 4.4,
			year_built: 2010,
			features: ['Air conditioning', 'Renovated', 'Double garage', 'Garden', 'Workshop'],
			highlights: ['Subdivision potential', 'Near Galleria', 'Character home', 'Large block'],
			photos_count: 11,
			listing_status: 'active',
			page_views: 2234,
			council_rates: 2450,
			water_rates: 980,
			strata_fees: 0,
			estimated_rent_pw: 660,
			price_history: [
				{ date: '2024-07-10', event: 'Listed', price: 750000, change_percent: null },
				{ date: '2018-11-20', event: 'Sold', price: 595000, change_percent: null },
			],
		},
		{
			id: "prop-016",
			address: "42 Safety Bay Road",
			suburb: "Safety Bay",
			postcode: "6169",
			state: "WA",
			property_type: "house",
			bedrooms: 4,
			bathrooms: 2,
			car_spaces: 2,
			land_size_sqm: 580,
			floor_size_sqm: 175,
			valuation_aud: 595000,
			token_price: 1.00,
			yield_percent: 5.0,
			year_built: 2008,
			features: ['Air conditioning', 'Pool', 'Double garage', 'Patio', 'Bore'],
			highlights: ['Beach lifestyle', 'Near marina', 'Tropical garden', 'Great for families'],
			photos_count: 12,
			listing_status: 'active',
			page_views: 1456,
			council_rates: 2050,
			water_rates: 890,
			strata_fees: 0,
			estimated_rent_pw: 575,
			price_history: [
				{ date: '2024-04-25', event: 'Listed', price: 595000, change_percent: null },
				{ date: '2019-12-10', event: 'Sold', price: 465000, change_percent: null },
			],
		},
		// === PREMIUM PROPERTIES ($950k-$1.5M) ===
		{
			id: "prop-017",
			address: "42 Harbour View Drive",
			suburb: "Cottesloe",
			postcode: "6011",
			state: "WA",
			property_type: "house",
			bedrooms: 4,
			bathrooms: 2,
			car_spaces: 2,
			land_size_sqm: 650,
			floor_size_sqm: 280,
			valuation_aud: 1250000,
			token_price: 1.00,
			yield_percent: 3.5,
			year_built: 2015,
			features: ['Air conditioning', 'Garage', 'Pool', 'Garden'],
			highlights: ['Stunning ocean glimpses', 'North-facing living', 'Resort-style pool', 'Premium Cottesloe location'],
			photos_count: 12,
			listing_status: 'active',
			page_views: 1847,
			council_rates: 3200,
			water_rates: 1100,
			strata_fees: 0,
			estimated_rent_pw: 950,
			price_history: [
				{ date: '2024-06-15', event: 'Listed', price: 1250000, change_percent: null },
				{ date: '2021-03-20', event: 'Sold', price: 980000, change_percent: null },
				{ date: '2018-11-05', event: 'Sold', price: 875000, change_percent: null },
			],
		},
		{
			id: "prop-018",
			address: "23 River Street",
			suburb: "South Perth",
			postcode: "6151",
			state: "WA",
			property_type: "apartment",
			bedrooms: 3,
			bathrooms: 2,
			car_spaces: 2,
			land_size_sqm: 0,
			floor_size_sqm: 120,
			valuation_aud: 890000,
			token_price: 1.00,
			yield_percent: 4.2,
			year_built: 2019,
			features: ['Air conditioning', 'Balcony', 'Gym', 'River views', 'Secure parking'],
			highlights: ['Panoramic Swan River views', 'Resort-style facilities', 'City skyline backdrop', 'Premium South Perth address'],
			photos_count: 15,
			listing_status: 'active',
			page_views: 3241,
			council_rates: 2600,
			water_rates: 900,
			strata_fees: 5200,
			estimated_rent_pw: 780,
			price_history: [
				{ date: '2024-07-01', event: 'Listed', price: 890000, change_percent: null },
				{ date: '2019-09-15', event: 'Sold (off plan)', price: 785000, change_percent: null },
			],
		},
		{
			id: "prop-019",
			address: "5/12 The Esplanade",
			suburb: "Applecross",
			postcode: "6153",
			state: "WA",
			property_type: "apartment",
			bedrooms: 3,
			bathrooms: 2,
			car_spaces: 2,
			land_size_sqm: 0,
			floor_size_sqm: 145,
			valuation_aud: 1150000,
			token_price: 1.00,
			yield_percent: 3.8,
			year_built: 2021,
			features: ['Air conditioning', 'River views', 'Wine room', 'Concierge', 'Private lift'],
			highlights: ['Prestigious Applecross address', 'River frontage', 'Luxury finishes', 'Secure building'],
			photos_count: 18,
			listing_status: 'active',
			page_views: 2876,
			council_rates: 3100,
			water_rates: 1050,
			strata_fees: 6500,
			estimated_rent_pw: 920,
			price_history: [
				{ date: '2024-08-01', event: 'Listed', price: 1150000, change_percent: null },
				{ date: '2021-06-15', event: 'Sold (new)', price: 1085000, change_percent: null },
			],
		},
		{
			id: "prop-020",
			address: "18 View Street",
			suburb: "Peppermint Grove",
			postcode: "6011",
			state: "WA",
			property_type: "house",
			bedrooms: 5,
			bathrooms: 3,
			car_spaces: 3,
			land_size_sqm: 800,
			floor_size_sqm: 350,
			valuation_aud: 1850000,
			token_price: 1.00,
			yield_percent: 3.2,
			year_built: 2019,
			features: ['Air conditioning', 'Pool', 'Home theatre', 'Wine cellar', 'Smart home', 'Solar'],
			highlights: ['Perth\'s most exclusive suburb', 'Federation character', 'Manicured gardens', 'Entertainer\'s dream'],
			photos_count: 22,
			listing_status: 'active',
			page_views: 4123,
			council_rates: 4200,
			water_rates: 1350,
			strata_fees: 0,
			estimated_rent_pw: 1250,
			price_history: [
				{ date: '2024-09-01', event: 'Listed', price: 1850000, change_percent: null },
				{ date: '2019-12-10', event: 'Sold', price: 1650000, change_percent: null },
			],
		},
	]);
	
	// Property detail dialog state
	let showPropertyDetailDialog = $state(false);
	let detailProperty = $state<any>(null);
	let propertyDetailTab = $state<'overview' | 'facts' | 'costs' | 'history' | 'services'>('overview');
	
	// Helper functions for property calculations
	function getPricePerSqm(property: any): number {
		const size = property.land_size_sqm > 0 ? property.land_size_sqm : property.floor_size_sqm;
		return size > 0 ? Math.round(property.valuation_aud / size) : 0;
	}
	
	function getAnnualCosts(property: any): number {
		return (property.council_rates || 0) + (property.water_rates || 0) + (property.strata_fees || 0);
	}
	
	function getNetYield(property: any): number {
		const grossRent = (property.estimated_rent_pw || 0) * 52;
		const costs = getAnnualCosts(property);
		const netRent = grossRent - costs;
		return property.valuation_aud > 0 ? (netRent / property.valuation_aud) * 100 : 0;
	}
	
	function openPropertyDetail(property: any) {
		detailProperty = property;
		propertyDetailTab = 'overview';
		showPropertyDetailDialog = true;
	}
	
	// Network derived values (depend on properties)
	let networkTotalPropertyValue = $derived(properties.reduce((sum, p) => sum + p.valuation_aud, 0));
	let networkAverageYield = $derived(4.2 + (networkOccupancyRate - 0.9) * 10);  // Yield adjusts with occupancy
	let tokenPrice = $derived(networkTotalPropertyValue > 0 ? (networkTotalPropertyValue * 0.4 / totalTokenSupply) : 1.0);

	// Leaderboard
	let leaderboard = $state([
		{ rank: 1, display_name: "PropertyPro", portfolio_value: 142500, total_return_percent: 42.5 },
		{ rank: 2, display_name: "InvestorX", portfolio_value: 128000, total_return_percent: 28.0 },
		{ rank: 3, display_name: "WealthBuilder", portfolio_value: 118500, total_return_percent: 18.5 },
		{ rank: 4, display_name: "SmartMoney", portfolio_value: 112000, total_return_percent: 12.0 },
		{ rank: 5, display_name: "DiversifyKing", portfolio_value: 108000, total_return_percent: 8.0 },
	]);

	// Proposals
	let proposals = $state([
		{
			id: "gov-001",
			title: "Expand to Melbourne market",
			votes_for: 125000,
			votes_against: 45000,
			status: "active",
			ends_in: "5 days",
		},
		{
			id: "gov-002",
			title: "Reduce management fee to 0.4%",
			votes_for: 89000,
			votes_against: 76000,
			status: "active",
			ends_in: "3 days",
		},
	]);

	async function handleSignup() {
		if (!loginEmail) {
			loginError = 'Please enter your email';
			return;
		}
		
		isLoading = true;
		loginError = null;
		
		try {
			// Check auth mode
			if (!authConfig) {
				authConfig = await fetchAuthConfig();
			}
			
			if (authConfig?.mode === 'google') {
				// Redirect to login page for Google OAuth
				goto('/auth/login');
				return;
			}
			
			// Dev mode: direct login
			await devLogin(loginEmail, loginDisplayName || undefined);
			// Auth store is now updated, isSignedUp will be true
			
		} catch (e) {
			loginError = e instanceof Error ? e.message : 'Login failed';
		} finally {
			isLoading = false;
		}
	}
	
	function handleLogout() {
		logout();
		// Reset simulation state
		balance = 100000;
		portfolioValue = 0;
		totalReturn = 0;
		totalReturnPercent = 0;
		holdings = [];
		transactions = [];
		networkMonth = 0;
		networkEvents = [];
	}

	function openBuyDialog(property: any) {
		selectedProperty = property;
		buyAmount = 1000;
		showBuyDialog = true;
	}

	function handleBuy() {
		if (!selectedProperty || buyAmount <= 0 || buyAmount > balance) return;
		
		// Use network-derived token price, not hardcoded property token_price
		// Token price = (Network Property Value * 0.4) / Total Token Supply
		const currentTokenPrice = tokenPrice > 0 ? tokenPrice : 1.0;
		const tokenAmount = buyAmount / currentTokenPrice;
		
		// Update balance
		balance -= buyAmount;
		
		// Update or add holding
		const existingIndex = holdings.findIndex(h => h.property_id === selectedProperty.id);
		if (existingIndex >= 0) {
			holdings[existingIndex].token_amount += tokenAmount;
			holdings[existingIndex].current_value += buyAmount;
		} else {
			holdings = [...holdings, {
				property_id: selectedProperty.id,
				address: selectedProperty.address,
				suburb: selectedProperty.suburb,
				token_amount: tokenAmount,
				current_value: buyAmount,
				cost_basis: buyAmount,
				yield_percent: selectedProperty.yield_percent,
			}];
		}
		
		// Add transaction
		transactions = [{
			id: 'tx-' + Math.random().toString(36).substring(7),
			tx_type: 'buy',
			property_address: selectedProperty.address,
			token_amount: tokenAmount,
			aud_amount: buyAmount,
			created_at: new Date().toISOString(),
		}, ...transactions];
		
		// Add to investor transaction log
		investorTransactions = [{
			id: Date.now(),
			type: 'buy',
			description: `Purchased ${tokenAmount.toFixed(2)} tokens of ${selectedProperty.address}`,
			amount: -buyAmount,
			tokens: tokenAmount,
			date: new Date().toLocaleDateString(),
			status: 'completed'
		}, ...investorTransactions];
		
		// Recalculate portfolio
		portfolioValue = holdings.reduce((sum, h) => sum + h.current_value, 0);
		totalReturn = (balance + portfolioValue) - 100000;
		totalReturnPercent = (totalReturn / 100000) * 100;
		
		showBuyDialog = false;
	}

	function handleSell(holding: any) {
		const saleAmount = holding.current_value;
		
		// Update balance
		balance += saleAmount;
		
		// Remove holding
		holdings = holdings.filter(h => h.property_id !== holding.property_id);
		
		// Add transaction
		transactions = [{
			id: 'tx-' + Math.random().toString(36).substring(7),
			tx_type: 'sell',
			property_address: holding.address,
			token_amount: holding.token_amount,
			aud_amount: saleAmount,
			created_at: new Date().toISOString(),
		}, ...transactions];
		
		// Add to investor transaction log
		investorTransactions = [{
			id: Date.now(),
			type: 'sell',
			description: `Sold ${holding.token_amount.toFixed(2)} tokens of ${holding.address}`,
			amount: saleAmount,
			tokens: holding.token_amount,
			date: new Date().toLocaleDateString(),
			status: 'completed'
		}, ...investorTransactions];
		
		// Recalculate portfolio
		portfolioValue = holdings.reduce((sum, h) => sum + h.current_value, 0);
		totalReturn = (balance + portfolioValue) - 100000;
		totalReturnPercent = (totalReturn / 100000) * 100;
	}

	function handleReset() {
		balance = 100000;
		portfolioValue = 0;
		totalReturn = 0;
		totalReturnPercent = 0;
		holdings = [];
		transactions = [{
			id: 'tx-reset',
			tx_type: 'reset',
			property_address: null,
			token_amount: 0,
			aud_amount: 100000,
			created_at: new Date().toISOString(),
		}];
		// Reset recurring investment
		recurringEnabled = false;
		recurringPropertyId = '';
		simulatedMonths = 0;
	}
	
	// Recurring investment handlers
	function setupRecurringInvestment() {
		if (!recurringPropertyId || recurringAmount <= 0) return;
		
		recurringEnabled = true;
		// Sync monthly contribution to projection calculator
		monthlyContribution = recurringAmount;
		showRecurringDialog = false;
	}
	
	function cancelRecurringInvestment() {
		recurringEnabled = false;
		recurringPropertyId = '';
		monthlyContribution = 0;
	}
	
	function simulateMonth() {
		if (!recurringEnabled || !recurringPropertyId) return;
		
		const property = properties.find(p => p.id === recurringPropertyId);
		if (!property) return;
		
		// Check if user has enough balance
		if (balance < recurringAmount) {
			// Not enough balance - pause auto-invest
			return;
		}
		
		// Use network-derived token price, not hardcoded property token_price
		const currentTokenPrice = tokenPrice > 0 ? tokenPrice : 1.0;
		const tokenAmount = recurringAmount / currentTokenPrice;
		
		// Update balance
		balance -= recurringAmount;
		
		// Update or add holding
		const existingIndex = holdings.findIndex(h => h.property_id === property.id);
		if (existingIndex >= 0) {
			holdings[existingIndex].token_amount += tokenAmount;
			holdings[existingIndex].current_value += recurringAmount;
			holdings = [...holdings]; // Trigger reactivity
		} else {
			holdings = [...holdings, {
				property_id: property.id,
				address: property.address,
				suburb: property.suburb,
				token_amount: tokenAmount,
				current_value: recurringAmount,
				cost_basis: recurringAmount,
				yield_percent: property.yield_percent,
			}];
		}
		
		// Add transaction
		transactions = [{
			id: 'tx-' + Math.random().toString(36).substring(7),
			tx_type: 'auto-invest',
			property_address: property.address,
			token_amount: tokenAmount,
			aud_amount: recurringAmount,
			created_at: new Date().toISOString(),
		}, ...transactions];
		
		// Add to investor transaction log
		investorTransactions = [{
			id: Date.now(),
			type: 'auto_invest',
			description: `Auto-invested in ${property.address}`,
			amount: -recurringAmount,
			tokens: tokenAmount,
			date: new Date().toLocaleDateString(),
			status: 'completed'
		}, ...investorTransactions];
		
		// Simulate monthly dividend (0.3-0.5% of portfolio value)
		if (portfolioValue > 0) {
			const dividendRate = 0.003 + Math.random() * 0.002;
			const dividend = portfolioValue * dividendRate;
			balance += dividend;
			
			investorTransactions = [{
				id: Date.now() + 1,
				type: 'dividend',
				description: `Monthly dividend from portfolio`,
				amount: dividend,
				date: new Date().toLocaleDateString(),
				status: 'completed'
			}, ...investorTransactions];
		}
		
		// Recalculate portfolio
		portfolioValue = holdings.reduce((sum, h) => sum + h.current_value, 0);
		totalReturn = (balance + portfolioValue) - 100000;
		totalReturnPercent = (totalReturn / 100000) * 100;
		
		// Increment simulated months
		simulatedMonths++;
	}
	
	function simulateMultipleMonths(months: number) {
		for (let i = 0; i < months; i++) {
			if (balance >= recurringAmount) {
				simulateMonth();
			} else {
				break;
			}
		}
	}
	
	function getRecurringProperty() {
		return properties.find(p => p.id === recurringPropertyId);
	}
	
	// =====================================================
	// UNIFIED NETWORK SIMULATION
	// Advances the entire network by one month, connecting all financial flows
	// =====================================================
	function simulateNetworkMonth() {
		networkMonth++;
		const monthLabel = `Month ${networkMonth}`;
		
		// Track last token price for appreciation calculation
		lastTokenPrice = tokenPrice;
		
		// ========== 0. SIMULATE WA ECONOMIC CONDITIONS ==========
		// Iron ore prices, population growth, and market conditions drive everything
		simulateWAEconomicEvents();
		
		// ========== 1. PROPERTY APPRECIATION (Market Condition Driven) ==========
		// WA property values can BOOM (+2%/month) or BUST (-2.5%/month) depending on iron ore and population
		const appreciationRate = getAppreciationRate();
		properties = properties.map(p => ({
			...p,
			valuation_aud: p.valuation_aud * (1 + appreciationRate)
		}));
		
		// Log significant market movements
		if (appreciationRate < -0.005) {
			addThinking('Governor', 'observation', 
				`Property values declining ${(appreciationRate * 100).toFixed(2)}% this month. Market condition: ${marketCondition}`, 
				80);
		} else if (appreciationRate > 0.01) {
			addThinking('Governor', 'observation', 
				`Strong property growth of ${(appreciationRate * 100).toFixed(2)}% this month. Boom conditions continue.`, 
				85);
		}
		
		// Track metrics for marathon synopsis
		if (marathonMode) {
			updateMarathonMetrics(appreciationRate);
		}
		
		// ========== 2. RENTAL INCOME COLLECTION ==========
		// Calculate total rent from occupied properties
		// REALISTIC: Rental yields COMPRESS during booms and EXPAND during busts
		// Perth gross yields: ~3.5% in boom, ~5% in bust (annual)
		const occupiedProperties = properties.filter(() => Math.random() < networkOccupancyRate);
		const yieldMultiplier = {
			boom: 0.7,      // Yields compress during booms (rents don't keep up with prices)
			stable: 0.9,
			stagnant: 1.0,
			declining: 1.1,  // Yields expand as prices fall faster than rents
			bust: 1.2,
		}[marketCondition] || 1.0;
		const baseMonthlyYield = 0.0035;  // 0.35% monthly = 4.2% annual base yield
		const effectiveMonthlyYield = baseMonthlyYield * yieldMultiplier;
		const monthlyRentTotal = occupiedProperties.reduce((sum, p) => sum + (p.valuation_aud * effectiveMonthlyYield), 0);
		networkTotalRentalIncome += monthlyRentTotal;
		
		// If renter is active, their rent contributes
		if (renterProperty) {
			addNetworkEvent('rent_collected', 'Renter', 'Network', 
				`Rent collected from ${renterProperty.address}`, renterMonthlyRent);
		}
		
		// ========== 3. SERVICE PROVIDER PAYMENTS (from rental income) ==========
		// Property management takes ~8% of rent
		const managementFee = monthlyRentTotal * 0.08;
		networkTotalExpenses += managementFee;
		networkTreasury -= managementFee;
		
		// If custodian is active, they receive portion
		if (custodianManagedProperties > 0) {
			const custodianShare = managementFee * (custodianManagedProperties / properties.length);
			custodianMonthlyFees = Math.round(custodianShare);
			
			addNetworkEvent('service_payment', 'Network', 'Service Provider',
				`Property management fees paid`, custodianShare);
			
			custodianTransactions = [{
				id: Date.now(),
				type: 'fee_collected',
				description: `Management fees - ${monthLabel}`,
				amount: custodianShare,
				date: getFormattedDate(networkMonth),
				status: 'completed'
			}, ...custodianTransactions];
		}
		
		// ========== 4. NET RENTAL INCOME TO TREASURY ==========
		const netRentalIncome = monthlyRentTotal - managementFee;
		networkTreasury += netRentalIncome;
		
		// ========== 5. DIVIDEND DISTRIBUTION TO TOKEN HOLDERS ==========
		// Distribute ~70% of net rental income to token holders (after management fees, reserves, etc.)
		const dividendPool = netRentalIncome * 0.70;  // Reduced from 80% - more realistic after all costs
		const dividendPerToken = dividendPool / totalTokenSupply;
		
		// Calculate investor dividend based on holdings
		// IMPORTANT: The user's dividend is proportional to their % of total tokens
		if (holdings.length > 0) {
			const investorTokens = holdings.reduce((sum, h) => sum + h.token_amount, 0);
			const investorOwnershipPercent = investorTokens / totalTokenSupply;
			
			// Investor's share of dividend pool (proportional to ownership)
			const investorDividend = dividendPool * investorOwnershipPercent;
			
			// Only add dividend if it's meaningful (avoid tiny fractions)
			if (investorDividend >= 1) {
				balance += investorDividend;
				hasReceivedDividend = true; // Track for achievements
				
				// Track dividends for marathon synopsis
				if (marathonMode) {
					marathonMetrics.totalDividends += investorDividend;
				}
				
				addNetworkEvent('dividend_paid', 'Network', 'Investor',
					`Monthly dividend payment`, investorDividend);
				
				investorTransactions = [{
					id: Date.now(),
					type: 'dividend',
					description: `Network dividend - ${monthLabel} (${(investorOwnershipPercent * 100).toFixed(2)}% of pool)`,
					amount: investorDividend,
					date: getFormattedDate(networkMonth),
					status: 'completed'
				}, ...investorTransactions];
			}
		}
		
		// ========== 6. FOUNDATION PARTNER YIELD ==========
		if (foundationTotalStaked > 0) {
			// Foundation gets enhanced yield (base + 0.5%)
			const foundationYieldRate = (networkAverageYield + 0.5) / 100 / 12;
			const foundationMonthlyYield = foundationTotalStaked * foundationYieldRate;
			foundationEarnings += foundationMonthlyYield;
			foundationMonthsStaked++;
			
			addNetworkEvent('stake_yield', 'Network', 'Foundation',
				`Staking yield payment`, foundationMonthlyYield);
			
			foundationTransactions = [{
				id: Date.now(),
				type: 'yield',
				description: `Staking yield - ${monthLabel}`,
				amount: foundationMonthlyYield,
				date: getFormattedDate(networkMonth),
				status: 'completed'
			}, ...foundationTransactions];
		}
		
		// ========== 7. TENANT EQUITY ACCUMULATION ==========
		if (tenantTargetProperty) {
			tenantMonthsRented++;
			// 15% of rent goes toward equity
			const equityContribution = tenantRentAmount * 0.15;
			const equityAsPercent = (equityContribution / tenantTargetProperty.valuation_aud) * 100;
			tenantEquityPercent += equityAsPercent;
			tenantSavingsVsRent += equityContribution;
			
			addNetworkEvent('rent_collected', 'Tenant', 'Network',
				`Rent-to-own payment (incl. ${equityContribution.toFixed(0)} equity)`, tenantRentAmount);
			
			tenantTransactions = [{
				id: Date.now(),
				type: 'rent',
				description: `Rent-to-own payment - ${monthLabel}`,
				amount: -tenantRentAmount,
				date: getFormattedDate(networkMonth),
				status: 'completed'
			}, {
				id: Date.now() + 1,
				type: 'equity_accrued',
				description: `Equity credited (${equityAsPercent.toFixed(3)}%)`,
				amount: equityContribution,
				date: getFormattedDate(networkMonth),
				status: 'completed'
			}, ...tenantTransactions];
			
			// Check for milestones
			if (tenantEquityPercent >= 5 && tenantEquityPercent - equityAsPercent < 5) {
				tenantTransactions = [{
					id: Date.now() + 2,
					type: 'milestone',
					description: '🎉 Reached 5% ownership milestone!',
					amount: null,
					date: getFormattedDate(networkMonth),
					status: 'completed'
				}, ...tenantTransactions];
			}
		}
		
		// ========== 8. HOMEOWNER MORTGAGE & APPRECIATION ==========
		if (homeownerPropertyValue > 0) {
			// Mortgage payment (if balance > 0)
			if (homeownerMortgageBalance > 0) {
				const interestPayment = homeownerMortgageBalance * (0.055 / 12);  // 5.5% annual rate
				const principalPayment = homeownerMonthlyPayment - interestPayment;
				homeownerMortgageBalance = Math.max(0, homeownerMortgageBalance - principalPayment);
				
				homeownerTransactions = [{
					id: Date.now(),
					type: 'mortgage',
					description: `Mortgage payment ($${Math.round(principalPayment)} principal)`,
					amount: -homeownerMonthlyPayment,
					date: getFormattedDate(networkMonth),
					status: 'completed'
				}, ...homeownerTransactions];
			}
			
			// Property appreciates
			const oldValue = homeownerPropertyValue;
			homeownerPropertyValue *= (1 + appreciationRate);
			
			// Quarterly appreciation record
			if (networkMonth % 3 === 0) {
				homeownerTransactions = [{
					id: Date.now() + 1,
					type: 'appreciation',
					description: `Property appreciation (Q${Math.ceil(networkMonth / 3)})`,
					amount: homeownerPropertyValue - oldValue,
					date: getFormattedDate(networkMonth),
					status: 'completed'
				}, ...homeownerTransactions];
			}
			
			// If renting out, collect income
			if (homeownerIsRenting) {
				const rentalIncome = homeownerPropertyValue * 0.004;
				homeownerRentalIncome += rentalIncome;
				
				addNetworkEvent('rent_collected', 'Renter', 'Homeowner',
					`Rental income received`, rentalIncome);
				
				homeownerTransactions = [{
					id: Date.now() + 2,
					type: 'rental_income',
					description: `Rental income - ${monthLabel}`,
					amount: rentalIncome,
					date: getFormattedDate(networkMonth),
					status: 'completed'
				}, ...homeownerTransactions];
			}
		}
		
		// ========== 9. RENTER WEEKLY CYCLES (4 weeks per month) ==========
		if (renterProperty) {
			for (let week = 0; week < 4; week++) {
				renterWeeksRented++;
				renterTotalPaid += renterWeeklyRent;
				
				renterTransactions = [{
					id: Date.now() + week,
					type: 'rent_weekly',
					description: `Week ${renterWeeksRented} rent payment`,
					amount: -renterWeeklyRent,
					date: getRenterDate(renterWeeksRented),
					status: 'completed'
				}, ...renterTransactions];
			}
			renterMonthsRented++;
			renterLeaseEnd = Math.max(0, 12 - renterMonthsRented);
			
			// Quarterly inspection
			if (renterMonthsRented % 3 === 0) {
				renterTransactions = [{
					id: Date.now() + 10,
					type: 'inspection',
					description: `Quarterly property inspection completed`,
					amount: null,
					date: getRenterDate(renterWeeksRented),
					status: 'completed'
				}, ...renterTransactions];
				
				addNetworkEvent('inspection', 'Service Provider', 'Renter',
					`Property inspection at ${renterProperty.address}`, 0);
			}
		}
		
		// ========== 10. CUSTODIAN NEW TASKS ==========
		// Generate new service tasks based on network activity (1-2 tasks per month)
		const numNewTasks = Math.random() > 0.5 ? 2 : 1;
		for (let t = 0; t < numNewTasks; t++) {
			if (custodianManagedProperties > 0 && Math.random() > 0.3 && properties.length > 0) {
				const randomProperty = properties[Math.floor(Math.random() * properties.length)];
				const newTask = generateServiceTask(randomProperty);
				
				custodianPendingTasks = [...custodianPendingTasks, newTask];
				
				addNetworkEvent('maintenance_expense', 'Network', newTask.serviceType,
					`New task: ${newTask.task} at ${newTask.propertyAddress}`, 0);
			}
		}
		
		custodianMonthsSimulated++;
		
		// ========== 11. UPDATE PORTFOLIO VALUES ==========
		holdings = holdings.map(h => {
			const property = properties.find(p => p.id === h.property_id);
			if (property) {
				return {
					...h,
					current_value: h.token_amount * property.token_price
				};
			}
			return h;
		});
		
		portfolioValue = holdings.reduce((sum, h) => sum + h.current_value, 0);
		totalReturn = (balance + portfolioValue) - 100000;
		totalReturnPercent = (totalReturn / 100000) * 100;
		
		// Increment the role-specific month counters
		simulatedMonths++;
		totalSessionMonths++;
		
		// ========== 12. NPC AUTONOMOUS DECISIONS (Marathon Agent Core) ==========
		// Simulate AI-driven NPC participants making autonomous decisions
		simulateNPCDecisions();
		
		// ========== 13. SELF-HEALING SYSTEM ==========
		// Simulate market pressure from both directions
		simulateExitRequests();      // Sellers wanting out (bust conditions)
		simulateDemandPressure();    // Buyers/renters wanting in (boom conditions)
		
		// Check network health and activate healing strategies
		checkAndHeal();
		
		// ========== 14. COMMUNITY FEEDBACK GENERATION ==========
		// NPCs generate feedback based on market conditions
		generateCommunityFeedback();
		updateCommunitySentiment();
		
		// ========== 15. PROPERTY PORTFOLIO DYNAMICS ==========
		// Properties enter and exit the network based on market conditions
		simulatePropertyPortfolioDynamics();
		
		// ========== 16. UPDATE NPC PORTFOLIO VALUES ==========
		// Recalculate each NPC's portfolio value based on current token price
		if (marathonMode) {
			updateNPCPortfolios();
		}
		
		// ========== 17. RECORD LIVE PERFORMANCE HISTORY ==========
		// Track every tick for real-time charting
		simulationHistory.push({
			month: networkMonth,
			networkValue: networkTotalPropertyValue,
			tokenPrice: tokenPrice,
			userNetWorth: balance + portfolioValue,
			propertyCount: properties.length,
			marketCondition: marketCondition,
			reputationScore: networkReputation.score,
		});
		// Keep last 240 months (20 years) max to prevent memory bloat
		if (simulationHistory.length > 240) {
			simulationHistory = simulationHistory.slice(-240);
		}
		
		// ========== 18. CHECK ACHIEVEMENTS ==========
		// Track downturns survived (market shifts from declining/bust to better)
		if ((marketCondition === 'stable' || marketCondition === 'boom') && 
			simulationHistory.length >= 2) {
			const prevCondition = simulationHistory[simulationHistory.length - 2]?.marketCondition;
			if (prevCondition === 'bust' || prevCondition === 'declining') {
				downturnsSurvived++;
			}
		}
		checkAchievements();
		
		// ========== 19. CHECK INSIGHT MOMENTS ==========
		// Show educational insights during marathon
		if (marathonMode) {
			checkInsights();
		}
	}
	
	// Update all NPC portfolio values and calculate returns
	function updateNPCPortfolios() {
		for (const [name, portfolio] of Object.entries(npcPortfolios)) {
			// Current value = holdings * token price + uninvested cash
			const tokenValue = portfolio.holdings * tokenPrice;
			const uninvestedCash = portfolio.startingValue - portfolio.totalInvested;
			portfolio.currentValue = tokenValue + uninvestedCash + portfolio.totalDividends;
			
			// Calculate dividends for this NPC (proportional to holdings)
			if (portfolio.holdings > 0) {
				const npcOwnershipPercent = portfolio.holdings / totalTokenSupply;
				const netRentalIncome = networkTotalRentalIncome * 0.003; // Approximate monthly
				const npcDividend = netRentalIncome * npcOwnershipPercent * 0.70;
				if (npcDividend >= 0.5) {
					portfolio.totalDividends += npcDividend;
				}
			}
			
			// Calculate return percentage
			portfolio.returnPercent = portfolio.startingValue > 0 
				? ((portfolio.currentValue - portfolio.startingValue) / portfolio.startingValue) * 100 
				: 0;
		}
		
		// Trigger reactivity
		npcPortfolios = { ...npcPortfolios };
	}
	
	// =====================================================
	// PROPERTY PORTFOLIO DYNAMICS
	// =====================================================
	// Growth is EARNED through performance, not random
	// Good service → satisfaction → referrals → organic growth
	// Poor performance → exits → network shrinks
	
	// Track properties that have exited (for stats)
	let propertiesExited = $state(0);
	let propertiesAdded = $state(0);
	
	// =====================================================
	// NETWORK REPUTATION & SATISFACTION SYSTEM
	// =====================================================
	// Reputation drives growth - a flywheel effect
	
	let networkReputation = $state({
		score: 70,              // 0-100, starts at 70 (new but promising)
		trend: 'stable' as 'rising' | 'stable' | 'falling',
		
		// Component scores (0-100)
		investorSatisfaction: 70,    // Based on returns vs expectations
		renterSatisfaction: 75,      // Based on occupancy, maintenance, stability
		homeownerSatisfaction: 70,   // Based on equity access, service quality
		tenantSatisfaction: 75,      // Based on equity progress, pathway clarity
		serviceProviderSatisfaction: 80, // Based on payment reliability
		
		// Reputation history
		monthlyScores: [] as number[],
		
		// Referral tracking
		referralsThisYear: 0,
		wordOfMouthMultiplier: 1.0,  // Grows with sustained high satisfaction
	});
	
	function updateNetworkReputation() {
		const prevScore = networkReputation.score;
		
		// === INVESTOR SATISFACTION ===
		// Based on actual returns vs market expectations
		const expectedReturn = marketCondition === 'boom' ? 8 : 
			marketCondition === 'stable' ? 5 : 
			marketCondition === 'bust' ? -5 : 2;
		const actualReturn = totalReturnPercent;
		const returnDelta = actualReturn - expectedReturn;
		
		// Returns beating expectations = happy investors
		let investorScore = 50 + (returnDelta * 3); // +/- 3 points per % difference
		investorScore = Math.max(20, Math.min(100, investorScore));
		
		// Yield consistency matters
		const yieldBonus = networkAverageYield > 4.0 ? 10 : networkAverageYield > 3.5 ? 5 : 0;
		investorScore = Math.min(100, investorScore + yieldBonus);
		
		networkReputation.investorSatisfaction = Math.round(
			networkReputation.investorSatisfaction * 0.8 + investorScore * 0.2
		);
		
		// === RENTER SATISFACTION ===
		// High occupancy = properties are desirable
		// Low vacancy = stability for renters
		let renterScore = 50 + (networkOccupancyRate - 0.85) * 200; // 85% baseline
		
		// Waitlist indicates demand (good for existing renters = community)
		const waitlistBonus = rentalWaitlist.length > 5 ? 10 : rentalWaitlist.length > 2 ? 5 : 0;
		renterScore += waitlistBonus;
		
		// Self-healing responsiveness
		const healingBonus = activeStrategies.length > 0 ? 5 : 0;
		renterScore += healingBonus;
		
		renterScore = Math.max(20, Math.min(100, renterScore));
		networkReputation.renterSatisfaction = Math.round(
			networkReputation.renterSatisfaction * 0.8 + renterScore * 0.2
		);
		
		// === HOMEOWNER SATISFACTION ===
		// Based on property value trends and equity access
		let homeownerScore = 60;
		
		// Property appreciation
		if (marketCondition === 'boom') homeownerScore += 20;
		else if (marketCondition === 'stable') homeownerScore += 10;
		else if (marketCondition === 'bust') homeownerScore -= 15;
		
		// Treasury health = security
		const treasuryRatio = networkTreasury / networkTotalPropertyValue;
		if (treasuryRatio > 0.20) homeownerScore += 15;
		else if (treasuryRatio > 0.10) homeownerScore += 5;
		else homeownerScore -= 10;
		
		homeownerScore = Math.max(20, Math.min(100, homeownerScore));
		networkReputation.homeownerSatisfaction = Math.round(
			networkReputation.homeownerSatisfaction * 0.8 + homeownerScore * 0.2
		);
		
		// === TENANT (RENT-TO-OWN) SATISFACTION ===
		// Based on equity accumulation progress
		let tenantScore = 65;
		
		// Tenant equity growth
		if (tenantEquityPercent > 0) {
			const monthlyEquityRate = tenantEquityPercent / Math.max(1, tenantMonthsRented);
			if (monthlyEquityRate > 0.5) tenantScore += 20; // Good progress
			else if (monthlyEquityRate > 0.25) tenantScore += 10;
		}
		
		// Market conditions affect pathway viability
		if (marketCondition === 'bust') tenantScore += 10; // Great time to accumulate
		else if (marketCondition === 'boom') tenantScore -= 5; // Harder to catch up
		
		tenantScore = Math.max(20, Math.min(100, tenantScore));
		networkReputation.tenantSatisfaction = Math.round(
			networkReputation.tenantSatisfaction * 0.8 + tenantScore * 0.2
		);
		
		// === SERVICE PROVIDER SATISFACTION ===
		// Based on payment reliability from treasury
		let serviceScore = 70;
		
		// Treasury can pay bills
		if (networkTreasury > 100000) serviceScore += 20;
		else if (networkTreasury > 50000) serviceScore += 10;
		else if (networkTreasury < 10000) serviceScore -= 20;
		
		// Network health = stable work
		if (overallHealthStatus === 'healthy') serviceScore += 10;
		else if (overallHealthStatus === 'critical') serviceScore -= 15;
		
		serviceScore = Math.max(20, Math.min(100, serviceScore));
		networkReputation.serviceProviderSatisfaction = Math.round(
			networkReputation.serviceProviderSatisfaction * 0.8 + serviceScore * 0.2
		);
		
		// === OVERALL REPUTATION SCORE ===
		// Weighted average - investors and homeowners matter most for growth
		const overallScore = (
			networkReputation.investorSatisfaction * 0.30 +
			networkReputation.renterSatisfaction * 0.15 +
			networkReputation.homeownerSatisfaction * 0.30 +
			networkReputation.tenantSatisfaction * 0.15 +
			networkReputation.serviceProviderSatisfaction * 0.10
		);
		
		// Community sentiment also affects reputation
		const sentimentBonus = communitySentiment.score * 10; // -10 to +10
		
		networkReputation.score = Math.round(Math.max(10, Math.min(100, overallScore + sentimentBonus)));
		
		// Track trend
		networkReputation.monthlyScores.push(networkReputation.score);
		if (networkReputation.monthlyScores.length > 12) {
			networkReputation.monthlyScores.shift();
		}
		
		if (networkReputation.monthlyScores.length >= 3) {
			const recent = networkReputation.monthlyScores.slice(-3);
			const avg = recent.reduce((a, b) => a + b, 0) / recent.length;
			if (networkReputation.score > avg + 2) {
				networkReputation.trend = 'rising';
			} else if (networkReputation.score < avg - 2) {
				networkReputation.trend = 'falling';
			} else {
				networkReputation.trend = 'stable';
			}
		}
		
		// Word of mouth multiplier grows with sustained high satisfaction
		if (networkReputation.score >= 80) {
			networkReputation.wordOfMouthMultiplier = Math.min(2.0, networkReputation.wordOfMouthMultiplier + 0.02);
		} else if (networkReputation.score >= 60) {
			// Stable
		} else {
			networkReputation.wordOfMouthMultiplier = Math.max(0.5, networkReputation.wordOfMouthMultiplier - 0.03);
		}
		
		// Log significant reputation changes
		if (Math.abs(networkReputation.score - prevScore) >= 5) {
			const direction = networkReputation.score > prevScore ? 'improved' : 'declined';
			addThinking('Governor', 'observation',
				`Network reputation ${direction}: ${prevScore} → ${networkReputation.score}. ` +
				`Investor: ${networkReputation.investorSatisfaction}, Homeowner: ${networkReputation.homeownerSatisfaction}`,
				75);
		}
	}
	
	// Property generation templates for when pool runs out
	// Real market benchmarks from ABS & PropTrack (2025)
	// Source: https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/total-value-dwellings/latest-release
	const realMarketBenchmarks = {
		waMeanPrice: 947900,       // ABS Sep 2025: $947,900
		waQuarterlyGrowth: 0.049,  // ABS: +4.9% (strongest in Australia)
		nationalMeanPrice: 1045400, // ABS: $1,045,400
		totalAusDwellings: 11410700, // ABS: 11.4 million
		totalAusValue: 11928200000000, // ABS: $11.9 trillion
		// Historical context: 2020-2025 saw ~60% national growth
		// WA outperforming due to mining boom and population growth
	};
	
	// Perth suburb price ranges based on real market data
	// Distribution: 20% entry-level, 50% mid-range, 30% premium
	const perthSuburbs = [
		// Entry-level suburbs (under $500K)
		{ suburb: 'Midland', postcode: '6056', priceRange: [320000, 480000], types: ['unit', 'apartment'] },
		{ suburb: 'Balga', postcode: '6061', priceRange: [350000, 520000], types: ['unit', 'villa'] },
		{ suburb: 'Armadale', postcode: '6112', priceRange: [340000, 550000], types: ['apartment', 'house'] },
		{ suburb: 'Kwinana', postcode: '6167', priceRange: [380000, 520000], types: ['house', 'villa'] },
		// Mid-range suburbs ($500K - $900K) - closest to WA mean of $948K
		{ suburb: 'Rockingham', postcode: '6168', priceRange: [500000, 700000], types: ['villa', 'house'] },
		{ suburb: 'Mandurah', postcode: '6210', priceRange: [480000, 680000], types: ['duplex', 'house'] },
		{ suburb: 'Wanneroo', postcode: '6065', priceRange: [550000, 750000], types: ['villa', 'house'] },
		{ suburb: 'Ellenbrook', postcode: '6069', priceRange: [580000, 780000], types: ['house'] },
		{ suburb: 'Baldivis', postcode: '6171', priceRange: [600000, 800000], types: ['house'] },
		{ suburb: 'Scarborough', postcode: '6019', priceRange: [550000, 850000], types: ['apartment', 'townhouse'] },
		{ suburb: 'Joondalup', postcode: '6027', priceRange: [520000, 750000], types: ['apartment', 'townhouse'] },
		{ suburb: 'Fremantle', postcode: '6160', priceRange: [580000, 920000], types: ['apartment', 'townhouse'] },
		{ suburb: 'Morley', postcode: '6062', priceRange: [650000, 900000], types: ['house', 'villa'] },
		// Premium suburbs ($900K+)
		{ suburb: 'South Perth', postcode: '6151', priceRange: [800000, 1350000], types: ['apartment', 'townhouse'] },
		{ suburb: 'Subiaco', postcode: '6008', priceRange: [850000, 1250000], types: ['townhouse', 'apartment'] },
		{ suburb: 'Claremont', postcode: '6010', priceRange: [950000, 1500000], types: ['townhouse', 'house'] },
		{ suburb: 'Cottesloe', postcode: '6011', priceRange: [1200000, 2200000], types: ['house'] },
		{ suburb: 'Peppermint Grove', postcode: '6011', priceRange: [2500000, 5000000], types: ['house'] },
	];
	const streetNames = ['Beach', 'Ocean', 'River', 'Park', 'Garden', 'Hill', 'Lake', 'Palm', 'Kings', 'Queens', 'Main', 'High', 'Station', 'Market', 'Church', 'School', 'Mill', 'Bridge', 'Spring', 'Sunset', 'Shore', 'Bay', 'Cove', 'Vista', 'View'];
	const streetTypes = ['Street', 'Road', 'Drive', 'Avenue', 'Place', 'Close', 'Crescent', 'Way', 'Lane', 'Terrace'];
	
	let generatedPropertyCounter = 0;
	
	function generateSyntheticProperty(): any {
		generatedPropertyCounter++;
		const suburbData = perthSuburbs[Math.floor(Math.random() * perthSuburbs.length)];
		const streetName = streetNames[Math.floor(Math.random() * streetNames.length)];
		const streetType = streetTypes[Math.floor(Math.random() * streetTypes.length)];
		const streetNumber = Math.floor(Math.random() * 150) + 1;
		const propertyType = suburbData.types[Math.floor(Math.random() * suburbData.types.length)];
		
		// Calculate valuation based on suburb price range with some randomness
		const [minPrice, maxPrice] = suburbData.priceRange;
		const valuation = Math.round(minPrice + Math.random() * (maxPrice - minPrice));
		
		// Bedrooms based on property type
		const bedrooms = propertyType === 'unit' ? 1 + Math.floor(Math.random() * 2) :
			propertyType === 'apartment' ? 1 + Math.floor(Math.random() * 3) :
			propertyType === 'villa' || propertyType === 'duplex' ? 2 + Math.floor(Math.random() * 2) :
			propertyType === 'townhouse' ? 2 + Math.floor(Math.random() * 2) :
			3 + Math.floor(Math.random() * 2); // house
		
		const bathrooms = Math.min(bedrooms, 1 + Math.floor(Math.random() * 2));
		const carSpaces = propertyType === 'unit' ? 1 : 1 + Math.floor(Math.random() * 2);
		
		// Yield inversely correlated with price
		const yieldPercent = valuation < 400000 ? 5.5 + Math.random() * 0.8 :
			valuation < 600000 ? 4.8 + Math.random() * 0.7 :
			valuation < 900000 ? 4.2 + Math.random() * 0.6 :
			3.2 + Math.random() * 0.8;
		
		return {
			id: `gen-prop-${generatedPropertyCounter}-${Date.now()}`,
			address: `${streetNumber} ${streetName} ${streetType}`,
			suburb: suburbData.suburb,
			postcode: suburbData.postcode,
			state: 'WA',
			property_type: propertyType,
			bedrooms,
			bathrooms,
			car_spaces: carSpaces,
			land_size_sqm: propertyType === 'house' ? 400 + Math.floor(Math.random() * 300) : 
				propertyType === 'villa' || propertyType === 'duplex' ? 150 + Math.floor(Math.random() * 100) : 0,
			floor_size_sqm: bedrooms * 35 + Math.floor(Math.random() * 40) + 40,
			valuation_aud: valuation,
			token_price: tokenPrice,
			yield_percent: Math.round(yieldPercent * 10) / 10,
			year_built: 2005 + Math.floor(Math.random() * 20),
			features: ['Air conditioning', carSpaces > 1 ? 'Double garage' : 'Garage'],
			highlights: [`${suburbData.suburb} location`, 'Well maintained'],
			photos_count: 6 + Math.floor(Math.random() * 8),
			listing_status: 'active',
			page_views: Math.floor(Math.random() * 500) + 100,
			council_rates: Math.round(valuation * 0.003),
			water_rates: 800 + Math.floor(Math.random() * 400),
			strata_fees: ['apartment', 'unit', 'townhouse'].includes(propertyType) ? 1500 + Math.floor(Math.random() * 3000) : 0,
			estimated_rent_pw: Math.round(valuation * (yieldPercent / 100) / 52),
			price_history: [],
			joined_month: networkMonth,
			tokenization_percent: 0.30 + Math.random() * 0.19,
		};
	}
	
	function simulatePropertyPortfolioDynamics() {
		// First, update reputation based on current performance
		updateNetworkReputation();
		
		// ========== PROPERTY GROWTH (New homeowners joining) ==========
		// Growth is EARNED through reputation and service quality
		// High reputation = referrals = organic growth
		
		// Base growth from market conditions
		const marketGrowthBase = {
			boom: 0.15,      // 15% base - market is hot
			stable: 0.10,    // 10% base - steady market
			stagnant: 0.05,  // 5% base - slow market
			declining: 0.02, // 2% - cautious market
			bust: 0.01,      // 1% - fearful market
		}[marketCondition] || 0.08;
		
		// REPUTATION MULTIPLIER - the key driver
		// Reputation 80+ = 2x growth, Reputation 50 = 1x, Reputation 30 = 0.5x
		const reputationMultiplier = networkReputation.score >= 85 ? 2.5 :
			networkReputation.score >= 75 ? 2.0 :
			networkReputation.score >= 65 ? 1.5 :
			networkReputation.score >= 55 ? 1.2 :
			networkReputation.score >= 45 ? 1.0 :
			networkReputation.score >= 35 ? 0.7 :
			0.4;
		
		// Word of mouth from sustained satisfaction
		const wordOfMouthBonus = (networkReputation.wordOfMouthMultiplier - 1.0) * 0.15;
		
		// Population growth bonus (WA has strong pop growth)
		const populationBonus = populationGrowthRate > 2.5 ? 0.08 : 
			populationGrowthRate > 1.5 ? 0.04 : 0;
		
		// Network size bonus - larger networks attract more homeowners (network effects)
		const networkSizeBonus = properties.length > 40 ? 0.08 : 
			properties.length > 25 ? 0.05 :
			properties.length > 15 ? 0.03 : 0;
		
		// Total growth chance = base * reputation + bonuses
		const totalGrowthChance = (marketGrowthBase * reputationMultiplier) + wordOfMouthBonus + populationBonus + networkSizeBonus;
		
		// Can add multiple properties per month based on reputation + market
		const maxNewProperties = networkReputation.score >= 80 && marketCondition === 'boom' ? 4 :
			networkReputation.score >= 70 && (marketCondition === 'boom' || marketCondition === 'stable') ? 3 :
			networkReputation.score >= 60 ? 2 : 1;
		
		// Track referrals for the year
		let referralsThisMonth = 0;
		
		for (let i = 0; i < maxNewProperties; i++) {
			if (Math.random() < totalGrowthChance) {
				// Try pool properties first, then generate synthetic
				const existingIds = new Set(properties.map(p => p.id));
				const availablePoolProps = poolProperties.filter(p => !existingIds.has(p.id));
				
				let newProperty: any;
				
				if (availablePoolProps.length > 0) {
					const newProp = availablePoolProps[Math.floor(Math.random() * availablePoolProps.length)];
					const propValuation = newProp.valuation || 750000;
					
					newProperty = {
						id: newProp.id,
						address: newProp.address,
						suburb: newProp.suburb,
						postcode: (newProp.data?.postcode) || '6000',
						state: 'WA',
						property_type: newProp.property_type,
						bedrooms: newProp.bedrooms,
						bathrooms: newProp.bathrooms,
						car_spaces: (newProp.data?.parking) || 2,
						land_size_sqm: (newProp.data?.land_size) || 0,
						floor_size_sqm: (newProp.data?.build_area) || 150,
						valuation_aud: propValuation,
						token_price: tokenPrice,
						yield_percent: (newProp.data?.gross_yield) || 4.5,
						year_built: 2015,
						features: ['Air conditioning', 'Garage'],
						highlights: [],
						photos_count: 8,
						listing_status: 'active',
						page_views: Math.floor(Math.random() * 500) + 100,
						council_rates: Math.round(propValuation * 0.003),
						water_rates: 1000,
						strata_fees: newProp.property_type === 'apartment' ? 2500 : 0,
						estimated_rent_pw: Math.round(propValuation * 0.0004),
						price_history: [],
						joined_month: networkMonth,
						tokenization_percent: 0.30 + Math.random() * 0.19,
					};
				} else {
					// Generate synthetic property when pool exhausted
					newProperty = generateSyntheticProperty();
				}
				
				properties = [...properties, newProperty];
				propertiesAdded++;
				referralsThisMonth++;
				
				const homeownerNames = ['The Smiths', 'The Nguyens', 'The Patels', 'The Johnsons', 'The Wongs', 'The O\'Briens', 'The Garcias', 'The Lees', 'The Martins', 'The Taylors'];
				const homeowner = homeownerNames[Math.floor(Math.random() * homeownerNames.length)];
				
				// Referral source based on reputation
				const referralSource = networkReputation.score >= 80 ? ' (referral from existing member)' :
					networkReputation.score >= 70 ? ' (heard positive reviews)' :
					networkReputation.score >= 60 ? '' : '';
				
				addNetworkEvent('property_added', homeowner, 'Network', 
					`New homeowner joined: ${newProperty.address}, ${newProperty.suburb}${referralSource}`, newProperty.valuation_aud);
				
				addThinking('Governor', 'observation',
					`New property added to network: ${newProperty.address}. Homeowner accessing ${((newProperty as any).tokenization_percent * 100).toFixed(0)}% equity. ` +
					`Reputation: ${networkReputation.score}/100. Market: ${marketCondition}`,
					70);
			}
		}
		
		// Update referrals count
		networkReputation.referralsThisYear += referralsThisMonth;
		if (networkMonth % 12 === 0) {
			networkReputation.referralsThisYear = 0; // Reset annually
		}
		
		// ========== PROPERTY SHRINKAGE (Homeowners exiting) ==========
		// Exits driven by DISSATISFACTION - unhappy homeowners leave
		// High reputation = low exits, Low reputation = high exits
		
		// Base exit rate from market (some exits are natural - life changes, etc.)
		const marketExitBase = {
			boom: 0.03,      // 3% - some cash out at high prices
			stable: 0.02,    // 2% - natural life changes
			stagnant: 0.015, // 1.5% - holding on
			declining: 0.01, // 1% - waiting for recovery
			bust: 0.01,      // 1% - can't afford buyback
		}[marketCondition] || 0.02;
		
		// DISSATISFACTION MULTIPLIER - unhappy homeowners leave faster
		// High satisfaction (80+) = 0.3x exits, Low satisfaction (40-) = 2x exits
		const homeownerSatScore = networkReputation.homeownerSatisfaction;
		const dissatisfactionMultiplier = homeownerSatScore >= 80 ? 0.3 :
			homeownerSatScore >= 70 ? 0.5 :
			homeownerSatScore >= 60 ? 0.8 :
			homeownerSatScore >= 50 ? 1.0 :
			homeownerSatScore >= 40 ? 1.5 :
			2.0;
		
		const shrinkProbability = marketExitBase * dissatisfactionMultiplier;
		
		// Only allow shrinkage if we have more than 12 properties (protect early growth)
		// Also reduce probability further when network is small
		const adjustedShrinkProb = properties.length < 20 ? shrinkProbability * 0.3 : shrinkProbability;
		if (Math.random() < adjustedShrinkProb && properties.length > 12) {
			// Select a random property to exit (prefer older properties)
			const eligibleProperties = properties.filter(p => {
				// Don't exit properties that user is actively using
				if (renterProperty?.id === p.id) return false;
				if (tenantTargetProperty?.id === p.id) return false;
				if (homeownerProperty?.id === p.id) return false;
				// Don't exit properties with active holdings from user
				if (holdings.some(h => h.property_id === p.id)) return false;
				return true;
			});
			
			if (eligibleProperties.length > 0) {
				const exitingProp = eligibleProperties[Math.floor(Math.random() * eligibleProperties.length)];
				
				// Remove from properties
				properties = properties.filter(p => p.id !== exitingProp.id);
				propertiesExited++;
				
				const exitReasons = [
					'Homeowner bought back full equity',
					'Property sold to external buyer',
					'Homeowner refinanced with bank',
					'Estate settlement - family buyout',
				];
				const reason = exitReasons[Math.floor(Math.random() * exitReasons.length)];
				
				addNetworkEvent('property_removed', 'Homeowner', 'Network',
					`Property exited: ${exitingProp.address} - ${reason}`, exitingProp.valuation_aud);
				
				addThinking('Governor', 'observation',
					`Property exited network: ${exitingProp.address}. Reason: ${reason}. Network now has ${properties.length} properties.`,
					65);
			}
		}
	}
	
	// NPC roster with personalities for Marathon Agent behavior
	const npcRoster = [
		{ name: 'Sarah Chen', personality: 'Conservative', riskTolerance: 0.2, strategy: 'Steady income focus' },
		{ name: 'Marcus Thompson', personality: 'Aggressive', riskTolerance: 0.8, strategy: 'Growth maximization' },
		{ name: 'Emily Rodriguez', personality: 'Balanced', riskTolerance: 0.5, strategy: 'Diversification' },
		{ name: 'David Park', personality: 'Opportunist', riskTolerance: 0.6, strategy: 'Market timing' },
		{ name: 'Janet Williams', personality: 'Passive', riskTolerance: 0.3, strategy: 'Buy and hold' },
		{ name: 'Michael Foster', personality: 'Speculator', riskTolerance: 0.9, strategy: 'Momentum trading' },
		{ name: 'Lisa Chang', personality: 'Conservative', riskTolerance: 0.25, strategy: 'Capital preservation' },
		{ name: 'Robert Kim', personality: 'Balanced', riskTolerance: 0.55, strategy: 'Risk-adjusted returns' },
		{ name: 'Market Maker', personality: 'System', riskTolerance: 0.5, strategy: 'Liquidity provision' },
		{ name: 'OSF Developer', personality: 'System', riskTolerance: 0.7, strategy: 'Network expansion' },
		{ name: 'Foundation', personality: 'System', riskTolerance: 0.4, strategy: 'Governance & stability' },
	];
	
	function simulateNPCDecisions() {
		// Each NPC considers an action each month (Marathon Agent: autonomous multi-step decisions)
		// Activity level varies by market condition - more NPCs act during volatility
		const activityModifier = marketCondition === 'boom' ? 0.5 : marketCondition === 'bust' ? 0.4 : 0.6;
		const activeNPCs = npcRoster.filter(() => Math.random() > activityModifier);
		
		for (const npc of activeNPCs) {
			// Initialize performance tracking
			if (!npcPerformance[npc.name]) {
				npcPerformance[npc.name] = { decisions: 0, successes: 0, failures: 0, strategyAdjustments: 0 };
			}
			
			const perf = npcPerformance[npc.name];
			const successRate = perf.decisions > 0 ? perf.successes / perf.decisions : 0.5;
			
			// SELF-CORRECTION: Adjust strategy based on past performance AND market conditions
			if (perf.decisions > 5 && successRate < 0.4 && Math.random() > 0.7) {
				perf.strategyAdjustments++;
				const oldRisk = npc.riskTolerance;
				// Reduce risk if failing, increase if too conservative
				npc.riskTolerance = Math.max(0.1, Math.min(0.9, npc.riskTolerance * (successRate < 0.3 ? 0.8 : 1.1)));
				
				addThinking(npc.name, 'reflection', 
					`Self-correction: Adjusting risk tolerance from ${(oldRisk * 100).toFixed(0)}% to ${(npc.riskTolerance * 100).toFixed(0)}% after ${perf.decisions} decisions (${(successRate * 100).toFixed(0)}% success rate)`, 
					75);
				perf.lastAdjustment = `Risk adjusted to ${(npc.riskTolerance * 100).toFixed(0)}%`;
			}
			
			// MARKET AWARENESS: NPCs react to WA-specific conditions
			const ironOreOutlook = ironOrePrice > 140 ? 'bullish' : ironOrePrice > 100 ? 'neutral' : ironOrePrice > 70 ? 'cautious' : 'bearish';
			const popTrend = populationGrowthRate > 2 ? 'growing' : populationGrowthRate > 1 ? 'stable' : 'shrinking';
			const yieldAttractiveness = networkAverageYield > 4.5 ? 'high' : networkAverageYield > 3.5 ? 'moderate' : 'low';
			
			// OBSERVATION phase - Now includes WA-specific market factors
			addThinking(npc.name, 'observation', 
				`WA Market: Iron ore $${ironOrePrice.toFixed(0)}/t (${ironOreOutlook}), Pop growth ${populationGrowthRate.toFixed(1)}% (${popTrend}), Market: ${marketCondition}`,
				undefined);
			
			// ANALYSIS phase - NPCs adjust behavior based on market conditions
			// Conservative investors sell during peaks, buy during troughs
			// Aggressive investors do the opposite
			let actionBias = 0;  // -1 = sell, 0 = hold, +1 = buy
			
			if (npc.personality === 'Conservative') {
				// Conservatives sell high, reduce exposure in uncertain markets
				if (marketCondition === 'boom') actionBias = -0.5;  // Consider selling
				else if (marketCondition === 'bust') actionBias = 0.3;  // Buy the dip cautiously
				else if (marketCondition === 'declining') actionBias = -0.3;  // Reduce exposure
			} else if (npc.personality === 'Aggressive') {
				// Aggressive investors buy into momentum, FOMO in booms
				if (marketCondition === 'boom') actionBias = 0.8;  // Buy aggressively
				else if (marketCondition === 'bust') actionBias = -0.4;  // Panic sell
				else if (marketCondition === 'declining') actionBias = 0;  // Hold and wait
			} else if (npc.personality === 'Opportunist') {
				// Contrarian - buy when others are fearful
				if (marketCondition === 'bust') actionBias = 0.9;  // Buy heavily
				else if (economicPhase === 'trough') actionBias = 0.7;  // Buy the bottom
				else if (marketCondition === 'boom') actionBias = -0.3;  // Take profits
			} else if (npc.personality === 'Passive') {
				actionBias = 0.1;  // Minimal activity regardless of market
			}
			
			const shouldAct = Math.random() < npc.riskTolerance * (marketCondition === 'boom' ? 1.3 : marketCondition === 'bust' ? 1.2 : 0.8);
			const confidence = Math.round(50 + (npc.riskTolerance * 30) + (successRate * 20) - (marketCondition === 'bust' ? 15 : 0));
			
			if (shouldAct && properties.length > 0) {
				const targetProperty = properties[Math.floor(Math.random() * properties.length)];
				
				// Determine action based on bias and personality
				let action: 'buy' | 'sell' | 'hold' = 'hold';
				const roll = Math.random() + actionBias;
				if (roll > 0.7) action = 'buy';
				else if (roll < 0.3 && actionBias < 0) action = 'sell';
				
				// DECISION phase
				const actionReason = action === 'buy' 
					? `Buying: ${ironOreOutlook} iron ore outlook, ${npc.strategy}` 
					: action === 'sell' 
						? `Selling: Reducing exposure in ${marketCondition} market`
						: `Holding: Waiting for better entry point`;
				
				addThinking(npc.name, 'decision', 
					`${actionReason}. Target: ${targetProperty.address.split(',')[0]}. Confidence: ${confidence}%`,
					confidence);
				
				// ACTION phase
				if (action === 'buy') {
					const amount = Math.round(1000 + Math.random() * 4000);
					addThinking(npc.name, 'action', 
						`Executing: Purchase $${amount.toLocaleString()} of tokens at $${targetProperty.token_price.toFixed(2)}/token`,
						confidence);
					
					// Simulate trade outcome - harder to buy in boom (competition), harder to sell in bust (no liquidity)
					const successChance = marketCondition === 'boom' ? 0.7 : marketCondition === 'bust' ? 0.6 : 0.85;
					const tradeSuccess = Math.random() < successChance;
					perf.decisions++;
					if (tradeSuccess) {
						perf.successes++;
						addNetworkEvent('token_trade', npc.name, 'Market', 
							`${npc.name} bought tokens in ${targetProperty.address.split(',')[0]}`, amount);
						
						// Track NPC portfolio investment
						if (marathonMode && npcPortfolios[npc.name]) {
							const tokensAcquired = amount / tokenPrice;
							npcPortfolios[npc.name].totalInvested += amount;
							npcPortfolios[npc.name].holdings += tokensAcquired;
						}
					} else {
						perf.failures++;
						addThinking(npc.name, 'reflection', 
							marketCondition === 'boom' ? `Trade failed: Outbid by other buyers. Competition fierce.` : `Trade failed: Insufficient liquidity.`,
							30);
					}
				} else if (action === 'sell') {
					const amount = Math.round(500 + Math.random() * 2000);
					addThinking(npc.name, 'action', 
						`Executing: Sell $${amount.toLocaleString()} of tokens to reduce exposure`,
						confidence);
					
					const sellSuccess = marketCondition === 'bust' ? 0.5 : 0.9;  // Hard to sell in bust
					perf.decisions++;
					if (Math.random() < sellSuccess) {
						perf.successes++;
						addNetworkEvent('token_trade', 'Market', npc.name, 
							`${npc.name} sold tokens (reducing exposure)`, amount);
					} else {
						perf.failures++;
						addThinking(npc.name, 'reflection', 
							`Sell order unfilled: No buyers at this price. May need to discount.`,
							25);
					}
				}
			} else if (npc.personality === 'System' && npc.name === 'Market Maker') {
				// Market maker provides liquidity - more active in volatile markets
				addThinking(npc.name, 'action', 
					`Providing liquidity: Placed ${Math.round(2 + Math.random() * 3)} bid/ask orders across ${Math.min(3, properties.length)} properties`,
					90);
			}
		}
		
		// Update npcPerformance to trigger reactivity
		npcPerformance = { ...npcPerformance };
	}
	
	function getFormattedDate(monthsFromNow: number): string {
		const date = new Date();
		date.setMonth(date.getMonth() + monthsFromNow);
		return date.toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric' });
	}
	
	// === RENTER SIMULATION FUNCTIONS ===
	function getRenterDate(weeksFromStart: number = 0): string {
		const start = new Date();
		start.setDate(start.getDate() + (weeksFromStart * 7));
		return start.toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric' });
	}
	
	function renterSelectProperty(property: any) {
		renterProperty = property;
		renterMonthlyRent = Math.round(property.valuation_aud * 0.004);  // ~0.4% monthly rent
		renterLeaseEnd = 12;
		renterMonthsRented = 0;
		renterWeeksRented = 0;
		renterTotalPaid = 0;
		renterNextInspection = 3;
		renterLeaseStart = getRenterDate();
		renterMaintenanceRequests = [];
		
		const weeklyRent = Math.round(renterMonthlyRent / 4.33);
		const bond = weeklyRent * 4;
		const advanceRent = weeklyRent * 2;  // 2 weeks in advance
		
		// Initialize transactions with contract setup
		renterTransactions = [
			{
				id: 1,
				type: 'contract',
				description: 'Lease agreement signed - 12 month fixed term',
				amount: null,
				date: getRenterDate(),
				status: 'completed'
			},
			{
				id: 2,
				type: 'bond',
				description: 'Bond deposit (4 weeks rent) - held by RTBA',
				amount: -bond,
				date: getRenterDate(),
				status: 'completed'
			},
			{
				id: 3,
				type: 'rent_advance',
				description: 'Initial rent payment (2 weeks in advance)',
				amount: -advanceRent,
				date: getRenterDate(),
				status: 'completed'
			},
			{
				id: 4,
				type: 'inspection',
				description: 'Initial property condition report completed',
				amount: null,
				date: getRenterDate(),
				status: 'completed'
			},
			{
				id: 5,
				type: 'inspection',
				description: 'Routine inspection scheduled',
				amount: null,
				date: getRenterDate(12),  // 3 months away
				status: 'upcoming'
			}
		];
		
		// Add initial payments to total
		renterTotalPaid = bond + advanceRent;
	}
	
	function renterSimulateWeek() {
		if (!renterProperty) return;
		
		renterWeeksRented++;
		const weeklyRent = Math.round(renterMonthlyRent / 4.33);
		renterTotalPaid += weeklyRent;
		
		// Add weekly rent transaction
		renterTransactions = [{
			id: Date.now(),
			type: 'rent_weekly',
			description: `Weekly rent payment (Week ${renterWeeksRented})`,
			amount: -weeklyRent,
			date: getRenterDate(renterWeeksRented),
			status: 'completed'
		}, ...renterTransactions];
		
		// Update months (every ~4 weeks)
		if (renterWeeksRented % 4 === 0) {
			renterMonthsRented++;
			renterLeaseEnd = Math.max(0, renterLeaseEnd - 1);
			renterNextInspection = Math.max(0, renterNextInspection - 1);
			
			// Inspection due
			if (renterNextInspection === 0) {
				renterTransactions = [{
					id: Date.now() + 1,
					type: 'inspection',
					description: 'Routine inspection completed - property in good condition',
					amount: null,
					date: getRenterDate(renterWeeksRented),
					status: 'completed'
				}, ...renterTransactions];
				renterNextInspection = 3;  // Next inspection in 3 months
				
				// Schedule next inspection
				renterTransactions = [{
					id: Date.now() + 2,
					type: 'inspection',
					description: 'Next routine inspection scheduled',
					amount: null,
					date: getRenterDate(renterWeeksRented + 12),
					status: 'upcoming'
				}, ...renterTransactions];
			}
			
			// Lease renewal prompt
			if (renterLeaseEnd === 1) {
				renterTransactions = [{
					id: Date.now() + 3,
					type: 'renewal',
					description: 'Lease renewal notice - decision required within 30 days',
					amount: null,
					date: getRenterDate(renterWeeksRented),
					status: 'pending'
				}, ...renterTransactions];
			}
			
			// Show upgrade prompt after 6 months
			if (renterMonthsRented >= 6 && !renterShowUpgradePrompt) {
				renterShowUpgradePrompt = true;
			}
		}
	}
	
	function renterSimulateMonth() {
		// Simulate 4 weeks
		for (let i = 0; i < 4; i++) {
			renterSimulateWeek();
		}
	}
	
	function renterSimulateYear() {
		for (let i = 0; i < 12; i++) {
			renterSimulateMonth();
		}
	}
	
	function renterSubmitMaintenance(issue: string) {
		if (!issue.trim()) return;
		
		const request = {
			id: Date.now(),
			issue: issue,
			status: 'pending',
			submitted: 'Just now',
		};
		renterMaintenanceRequests = [request, ...renterMaintenanceRequests];
		
		// Add to transaction log
		renterTransactions = [{
			id: Date.now(),
			type: 'maintenance',
			description: `Maintenance request: ${issue}`,
			amount: null,
			date: getRenterDate(renterWeeksRented),
			status: 'pending'
		}, ...renterTransactions];
	}
	
	function renterUpgradeToTenant() {
		// Transfer renter to tenant role
		tenantTargetProperty = renterProperty;
		tenantRentAmount = renterMonthlyRent;
		tenantMonthsRented = 0;
		tenantEquityPercent = 0;
		activeRole = 'tenant';
	}
	
	function renterEndLease() {
		// Add end lease transaction
		renterTransactions = [{
			id: Date.now(),
			type: 'contract',
			description: 'Lease ended - Bond refund processed',
			amount: renterBondAmount,
			date: getRenterDate(renterWeeksRented),
			status: 'completed'
		}, ...renterTransactions];
		
		// Reset renter state
		renterProperty = null;
		renterMonthsRented = 0;
		renterWeeksRented = 0;
		renterTotalPaid = 0;
		renterLeaseEnd = 12;
		renterLeaseStart = null;
		renterNextInspection = 3;
		renterMaintenanceRequests = [];
		renterShowUpgradePrompt = false;
		renterTransactions = [];
	}
	
	function renterSwapProperty(newProperty: any) {
		// End current lease first
		renterTransactions = [{
			id: Date.now(),
			type: 'contract',
			description: `Lease transfer: Moving to ${newProperty.address}`,
			amount: null,
			date: getRenterDate(renterWeeksRented),
			status: 'completed'
		}, ...renterTransactions];
		
		// Keep transaction history but reset stats
		const oldTransactions = renterTransactions;
		
		// Select new property
		renterSelectProperty(newProperty);
		
		// Merge transaction history
		renterTransactions = [...renterTransactions, ...oldTransactions];
	}
	
	function getRenterTransactionIcon(type: string) {
		switch(type) {
			case 'contract': return FileText;
			case 'bond': return Shield;
			case 'rent_advance': return CreditCard;
			case 'rent_weekly': return DollarSign;
			case 'inspection': return CheckCircle;
			case 'maintenance': return Wrench;
			case 'renewal': return RefreshCw;
			default: return FileText;
		}
	}
	
	function getRenterTransactionColor(type: string, status: string) {
		if (status === 'upcoming') return 'text-blue-500 bg-blue-50';
		if (status === 'pending') return 'text-amber-500 bg-amber-50';
		switch(type) {
			case 'contract': return 'text-purple-500 bg-purple-50';
			case 'bond': return 'text-orange-500 bg-orange-50';
			case 'rent_advance': 
			case 'rent_weekly': return 'text-red-500 bg-red-50';
			case 'inspection': return 'text-green-500 bg-green-50';
			case 'maintenance': return 'text-amber-500 bg-amber-50';
			case 'renewal': return 'text-blue-500 bg-blue-50';
			default: return 'text-gray-500 bg-gray-50';
		}
	}
	
	// === INVESTOR TRANSACTION HELPERS ===
	function getInvestorTransactionIcon(type: string) {
		switch(type) {
			case 'buy': return TrendingUp;
			case 'sell': return TrendingDown;
			case 'dividend': return PiggyBank;
			case 'auto_invest': return RefreshCw;
			case 'fee': return FileText;
			default: return DollarSign;
		}
	}
	
	function getInvestorTransactionColor(type: string, status: string) {
		if (status === 'pending') return 'text-amber-500 bg-amber-50';
		if (status === 'processing') return 'text-blue-500 bg-blue-50';
		switch(type) {
			case 'buy': return 'text-green-500 bg-green-50';
			case 'sell': return 'text-orange-500 bg-orange-50';
			case 'dividend': return 'text-emerald-500 bg-emerald-50';
			case 'auto_invest': return 'text-blue-500 bg-blue-50';
			case 'fee': return 'text-gray-500 bg-gray-50';
			default: return 'text-gray-500 bg-gray-50';
		}
	}
	
	// === TENANT TRANSACTION HELPERS ===
	function getTenantTransactionIcon(type: string) {
		switch(type) {
			case 'rent': return DollarSign;
			case 'equity_accrued': return TrendingUp;
			case 'milestone': return Award;
			case 'inspection': return CheckCircle;
			case 'maintenance': return Wrench;
			default: return FileText;
		}
	}
	
	function getTenantTransactionColor(type: string, status: string) {
		if (status === 'pending') return 'text-amber-500 bg-amber-50';
		if (status === 'upcoming') return 'text-blue-500 bg-blue-50';
		switch(type) {
			case 'rent': return 'text-red-500 bg-red-50';
			case 'equity_accrued': return 'text-green-500 bg-green-50';
			case 'milestone': return 'text-purple-500 bg-purple-50';
			case 'inspection': return 'text-blue-500 bg-blue-50';
			case 'maintenance': return 'text-amber-500 bg-amber-50';
			default: return 'text-gray-500 bg-gray-50';
		}
	}
	
	// === HOMEOWNER TRANSACTION HELPERS ===
	function getHomeownerTransactionIcon(type: string) {
		switch(type) {
			case 'equity_access': return Landmark;
			case 'rental_income': return DollarSign;
			case 'mortgage': return Home;
			case 'appreciation': return TrendingUp;
			case 'expense': return CreditCard;
			case 'osf_deposit': return PiggyBank;
			default: return FileText;
		}
	}
	
	function getHomeownerTransactionColor(type: string, status: string) {
		if (status === 'pending') return 'text-amber-500 bg-amber-50';
		if (status === 'processing') return 'text-blue-500 bg-blue-50';
		switch(type) {
			case 'equity_access': return 'text-purple-500 bg-purple-50';
			case 'rental_income': return 'text-green-500 bg-green-50';
			case 'mortgage': return 'text-red-500 bg-red-50';
			case 'appreciation': return 'text-emerald-500 bg-emerald-50';
			case 'expense': return 'text-orange-500 bg-orange-50';
			case 'osf_deposit': return 'text-blue-500 bg-blue-50';
			default: return 'text-gray-500 bg-gray-50';
		}
	}
	
	// === CUSTODIAN TRANSACTION HELPERS ===
	function getCustodianTransactionIcon(type: string) {
		switch(type) {
			case 'fee_collected': return DollarSign;
			case 'task_completed': return CheckCircle;
			case 'property_added': return Home;
			case 'inspection': return FileText;
			case 'expense': return CreditCard;
			case 'payout': return TrendingUp;
			default: return FileText;
		}
	}
	
	function getCustodianTransactionColor(type: string, status: string) {
		if (status === 'pending') return 'text-amber-500 bg-amber-50';
		if (status === 'processing') return 'text-blue-500 bg-blue-50';
		switch(type) {
			case 'fee_collected': return 'text-green-500 bg-green-50';
			case 'task_completed': return 'text-blue-500 bg-blue-50';
			case 'property_added': return 'text-purple-500 bg-purple-50';
			case 'inspection': return 'text-cyan-500 bg-cyan-50';
			case 'expense': return 'text-red-500 bg-red-50';
			case 'payout': return 'text-emerald-500 bg-emerald-50';
			default: return 'text-gray-500 bg-gray-50';
		}
	}
	
	// === FOUNDATION TRANSACTION HELPERS ===
	function getFoundationTransactionIcon(type: string) {
		switch(type) {
			case 'stake': return PiggyBank;
			case 'unstake': return TrendingDown;
			case 'yield': return TrendingUp;
			case 'compound': return RefreshCw;
			case 'bonus': return Award;
			case 'governance': return Vote;
			default: return Landmark;
		}
	}
	
	function getFoundationTransactionColor(type: string, status: string) {
		if (status === 'pending') return 'text-amber-500 bg-amber-50';
		if (status === 'locked') return 'text-purple-500 bg-purple-50';
		switch(type) {
			case 'stake': return 'text-blue-500 bg-blue-50';
			case 'unstake': return 'text-orange-500 bg-orange-50';
			case 'yield': return 'text-green-500 bg-green-50';
			case 'compound': return 'text-cyan-500 bg-cyan-50';
			case 'bonus': return 'text-amber-500 bg-amber-50';
			case 'governance': return 'text-purple-500 bg-purple-50';
			default: return 'text-gray-500 bg-gray-50';
		}
	}
	
	function getRenterEquityLost() {
		// Show how much equity they would have built with rent-to-own
		return renterTotalPaid * 0.20;  // 20% of rent would have gone to equity
	}
	
	// === TENANT SIMULATION FUNCTIONS ===
	function tenantSelectProperty(property: any) {
		tenantTargetProperty = property;
		tenantRentAmount = Math.round(property.valuation_aud * 0.004);  // ~0.4% monthly rent
	}
	
	function tenantSimulateMonth() {
		if (!tenantTargetProperty) return;
		
		tenantMonthsRented++;
		// 20% of rent goes towards equity accumulation
		const equityContribution = tenantRentAmount * 0.20;
		tenantEquityPercent += (equityContribution / tenantTargetProperty.valuation_aud) * 100;
		
		// Compare to traditional rent (no equity)
		tenantSavingsVsRent += equityContribution;
		
		// Add rent payment transaction
		tenantTransactions = [{
			id: Date.now(),
			type: 'rent',
			description: `Monthly rent payment`,
			amount: -tenantRentAmount,
			date: getTenantDate(tenantMonthsRented),
			status: 'completed'
		}, ...tenantTransactions];
		
		// Add equity accrued transaction
		tenantTransactions = [{
			id: Date.now() + 1,
			type: 'equity_accrued',
			description: `Equity contribution from rent`,
			amount: equityContribution,
			date: getTenantDate(tenantMonthsRented),
			status: 'completed'
		}, ...tenantTransactions];
		
		// Check for milestones
		if (tenantEquityPercent >= 10 && tenantEquityPercent - (equityContribution / tenantTargetProperty.valuation_aud * 100) < 10) {
			tenantTransactions = [{
				id: Date.now() + 2,
				type: 'milestone',
				description: '10% equity milestone reached!',
				amount: null,
				date: getTenantDate(tenantMonthsRented),
				status: 'completed'
			}, ...tenantTransactions];
		} else if (tenantEquityPercent >= 25 && tenantEquityPercent - (equityContribution / tenantTargetProperty.valuation_aud * 100) < 25) {
			tenantTransactions = [{
				id: Date.now() + 2,
				type: 'milestone',
				description: '25% equity milestone reached!',
				amount: null,
				date: getTenantDate(tenantMonthsRented),
				status: 'completed'
			}, ...tenantTransactions];
		} else if (tenantEquityPercent >= 50 && tenantEquityPercent - (equityContribution / tenantTargetProperty.valuation_aud * 100) < 50) {
			tenantTransactions = [{
				id: Date.now() + 2,
				type: 'milestone',
				description: '50% equity milestone - halfway to ownership!',
				amount: null,
				date: getTenantDate(tenantMonthsRented),
				status: 'completed'
			}, ...tenantTransactions];
		}
	}
	
	function getTenantDate(months: number): string {
		const date = new Date();
		date.setMonth(date.getMonth() + months);
		return date.toLocaleDateString('en-AU', { month: 'short', year: 'numeric' });
	}
	
	function tenantSimulateYear() {
		for (let i = 0; i < 12; i++) {
			tenantSimulateMonth();
		}
	}
	
	function getTenantEquityValue() {
		if (!tenantTargetProperty) return 0;
		return tenantTargetProperty.valuation_aud * (tenantEquityPercent / 100);
	}
	
	function getTenantTimeToOwnership() {
		if (!tenantTargetProperty || tenantEquityPercent === 0) return 'N/A';
		const remainingPercent = 100 - tenantEquityPercent;
		const monthlyEquityRate = tenantEquityPercent / Math.max(tenantMonthsRented, 1);
		const monthsRemaining = remainingPercent / monthlyEquityRate;
		const years = Math.floor(monthsRemaining / 12);
		const months = Math.round(monthsRemaining % 12);
		return `${years}y ${months}m`;
	}
	
	// === HOMEOWNER SIMULATION FUNCTIONS ===
let homeownerMonthsSimulated = $state(0);
	
	function getHomeownerDate(months: number): string {
		const date = new Date();
		date.setMonth(date.getMonth() + months);
		return date.toLocaleDateString('en-AU', { month: 'short', year: 'numeric' });
	}
	
	function homeownerSelectProperty(property: any) {
		homeownerProperty = property;
		homeownerPropertyValue = property.valuation_aud || 850000;
		// Set mortgage as ~60% of property value for simulation
		homeownerMortgageBalance = Math.round(homeownerPropertyValue * 0.6);
		homeownerMonthlyPayment = Math.round(homeownerMortgageBalance * 0.005);  // ~6% annual rate
		homeownerEquityAccessAmount = 0;
		homeownerIsRenting = false;
		homeownerRentalIncome = 0;
		homeownerPropertyListed = false;
	}
	
	function homeownerListOnNetwork() {
		homeownerPropertyListed = true;
		homeownerTransactions = [{
			id: Date.now(),
			type: 'osf_deposit' as HomeownerTxType,
			description: 'Property listed on OSF Network',
			amount: null,
			date: getHomeownerDate(0),
			status: 'completed'
		}, ...homeownerTransactions];
	}
	
	function homeownerAccessEquity(amount: number) {
		if (amount > homeownerEquityAvailable) return;
		homeownerEquityAccessAmount += amount;
		homeownerMortgageBalance += amount;
		
		homeownerTransactions = [{
			id: Date.now(),
			type: 'equity_access',
			description: `Accessed equity via OSF`,
			amount: amount,
			date: getHomeownerDate(homeownerMonthsSimulated),
			status: 'completed'
		}, ...homeownerTransactions];
		
		// === CONNECT TO INVESTOR VIEW ===
		// When homeowner accesses equity, they receive OSF tokens in return
		// These tokens represent their stake and should appear in the investor holdings
		const currentTokenPrice = networkTotalPropertyValue > 0 ? (networkTotalPropertyValue * 0.4 / totalTokenSupply) : 1.0;
		const tokenAmount = amount / currentTokenPrice;
		
		// Add to investor holdings - homeowner's property becomes their investment stake
		const holdingId = `homeowner-equity-${homeownerProperty?.id || 'home'}`;
		const existingIndex = holdings.findIndex(h => h.property_id === holdingId);
		
		if (existingIndex >= 0) {
			// Add to existing holding
			holdings[existingIndex].token_amount += tokenAmount;
			holdings[existingIndex].current_value += amount;
			holdings[existingIndex].cost_basis += amount;
			holdings = [...holdings]; // Trigger reactivity
		} else {
			// Create new holding for homeowner's equity stake
			holdings = [...holdings, {
				property_id: holdingId,
				address: homeownerProperty?.address || 'Your Home',
				suburb: homeownerProperty?.suburb || 'Perth',
				token_amount: tokenAmount,
				current_value: amount,
				cost_basis: amount,
				yield_percent: 4.5, // Network average yield
				isHomeownerEquity: true, // Mark as homeowner-sourced
			}];
		}
		
		// Update portfolio tracking
		portfolioValue += amount;
		balance += amount; // Homeowner receives cash
		
		// Add to investor transaction log
		transactions = [{
			id: 'tx-' + Math.random().toString(36).substring(7),
			tx_type: 'equity_access',
			property_address: homeownerProperty?.address || 'Your Home',
			token_amount: tokenAmount,
			aud_amount: amount,
			created_at: new Date().toISOString(),
		}, ...transactions];
	}
	
	function homeownerStartRenting() {
		homeownerIsRenting = true;
		homeownerRentalIncome = Math.round(homeownerPropertyValue * 0.004);
		
		homeownerTransactions = [{
			id: Date.now(),
			type: 'rental_income',
			description: `Started renting property - $${homeownerRentalIncome}/month`,
			amount: null,
			date: getHomeownerDate(homeownerMonthsSimulated),
			status: 'completed'
		}, ...homeownerTransactions];
	}
	
	function homeownerStopRenting() {
		homeownerIsRenting = false;
		homeownerRentalIncome = 0;
		
		homeownerTransactions = [{
			id: Date.now(),
			type: 'rental_income',
			description: `Stopped renting property`,
			amount: null,
			date: getHomeownerDate(homeownerMonthsSimulated),
			status: 'completed'
		}, ...homeownerTransactions];
	}

	function homeownerSimulateMonth() {
		homeownerMonthsSimulated++;
		
		// Pay down mortgage
		const interestPayment = homeownerMortgageBalance * (0.055 / 12);  // 5.5% annual rate
		const principalPayment = homeownerMonthlyPayment - interestPayment;
		homeownerMortgageBalance = Math.max(0, homeownerMortgageBalance - principalPayment);
		
		// Property appreciation (~3% annually)
		const appreciationAmount = homeownerPropertyValue * (0.03 / 12);
		homeownerPropertyValue *= (1 + 0.03 / 12);
		
		// Add mortgage payment transaction
		homeownerTransactions = [{
			id: Date.now(),
			type: 'mortgage',
			description: `Mortgage payment (${Math.round(principalPayment)} principal)`,
			amount: -homeownerMonthlyPayment,
			date: getHomeownerDate(homeownerMonthsSimulated),
			status: 'completed'
		}, ...homeownerTransactions];
		
		// Add appreciation transaction (quarterly)
		if (homeownerMonthsSimulated % 3 === 0) {
			homeownerTransactions = [{
				id: Date.now() + 1,
				type: 'appreciation',
				description: `Property value appreciation (Q${Math.ceil(homeownerMonthsSimulated / 3)})`,
				amount: Math.round(appreciationAmount * 3),
				date: getHomeownerDate(homeownerMonthsSimulated),
				status: 'completed'
			}, ...homeownerTransactions];
		}
		
		// If renting, add rental income
		if (homeownerIsRenting) {
			homeownerTransactions = [{
				id: Date.now() + 2,
				type: 'rental_income',
				description: `Rental income received`,
				amount: homeownerRentalIncome,
				date: getHomeownerDate(homeownerMonthsSimulated),
				status: 'completed'
			}, ...homeownerTransactions];
		}
	}
	
	function homeownerSimulateYear() {
		for (let i = 0; i < 12; i++) {
			homeownerSimulateMonth();
		}
	}
	
	// === CUSTODIAN SIMULATION FUNCTIONS ===
	let custodianMonthsSimulated = $state(0);
	
	function getCustodianDate(months: number): string {
		const date = new Date();
		date.setMonth(date.getMonth() + months);
		return date.toLocaleDateString('en-AU', { month: 'short', year: 'numeric' });
	}
	
	// Initialize service tasks from actual properties
	function initializeServiceTasks() {
		if (custodianPendingTasks.length === 0 && properties.length > 0) {
			const initialTasks: ServiceTask[] = [];
			// Create 2-3 random tasks from actual properties
			const numTasks = Math.min(properties.length, 3 + Math.floor(Math.random() * 2));
			const shuffled = [...properties].sort(() => Math.random() - 0.5);
			
			for (let i = 0; i < numTasks; i++) {
				const prop = shuffled[i];
				const { task, serviceType, category } = getRandomTask();
				initialTasks.push({
					id: Date.now() + i,
					propertyId: prop.id,
					propertyAddress: prop.address,
					task,
					priority: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)] as 'low' | 'medium' | 'high',
					due: `${Math.floor(Math.random() * 7) + 1} days`,
					serviceType,
					category,
					cost: Math.round(100 + Math.random() * 400),
				});
			}
			custodianPendingTasks = initialTasks;
		}
	}
	
	// Generate a random service task for a property
	function generateServiceTask(prop: any): ServiceTask {
		const { task, serviceType, category } = getRandomTask();
		return {
			id: Date.now() + Math.random() * 1000,
			propertyId: prop.id,
			propertyAddress: prop.address,
			task,
			priority: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)] as 'low' | 'medium' | 'high',
			due: `${Math.floor(Math.random() * 7) + 1} days`,
			serviceType,
			category,
			cost: Math.round(100 + Math.random() * 400),
		};
	}
	
	function custodianCompleteTask(taskId: number) {
		const task = custodianPendingTasks.find(t => t.id === taskId);
		custodianPendingTasks = custodianPendingTasks.filter(t => t.id !== taskId);
		
		if (task) {
			// Record completed service transaction
			custodianTransactions = [{
				id: Date.now(),
				type: 'task_completed',
				description: `${task.task}`,
				amount: task.cost,
				date: getCustodianDate(custodianMonthsSimulated),
				status: 'completed',
				propertyId: task.propertyId,
				propertyAddress: task.propertyAddress,
				serviceType: task.serviceType,
			}, ...custodianTransactions];
			
			// Add to network events
			addNetworkEvent('service_payment', 'Service Provider', task.propertyAddress,
				`${task.serviceType}: ${task.task}`, task.cost);
		}
	}
	
	// Get service history for a specific property
	function getPropertyServiceHistory(propertyId: string) {
		return custodianTransactions.filter(tx => tx.propertyId === propertyId);
	}
	
	function custodianAddProperty() {
		custodianManagedProperties++;
		custodianMonthlyFees += 400;  // Additional management fee
		
		custodianTransactions = [{
			id: Date.now(),
			type: 'property_added',
			description: `New property added to management portfolio`,
			amount: 400,
			date: getCustodianDate(custodianMonthsSimulated),
			status: 'completed'
		}, ...custodianTransactions];
	}
	
	function custodianSimulateMonth() {
		custodianMonthsSimulated++;
		
		// Initialize tasks if empty
		if (custodianPendingTasks.length === 0 && properties.length > 0) {
			initializeServiceTasks();
		}
		
		// Random new tasks with property linking
		if (Math.random() > 0.4 && properties.length > 0) {
			const randomProperty = properties[Math.floor(Math.random() * properties.length)];
			const newTask = generateServiceTask(randomProperty);
			custodianPendingTasks = [...custodianPendingTasks, newTask];
			
			custodianTransactions = [{
				id: Date.now() + 1,
				type: 'inspection',
				description: `New: ${newTask.task}`,
				amount: null,
				date: getCustodianDate(custodianMonthsSimulated),
				status: 'pending',
				propertyId: newTask.propertyId,
				propertyAddress: newTask.propertyAddress,
				serviceType: newTask.serviceType,
			}, ...custodianTransactions];
		}
		
		// Collect monthly management fees
		custodianTransactions = [{
			id: Date.now() + 2,
			type: 'fee_collected',
			description: `Monthly management fees collected`,
			amount: custodianMonthlyFees,
			date: getCustodianDate(custodianMonthsSimulated),
			status: 'completed'
		}, ...custodianTransactions];
		
		// Simulate occupancy fluctuation
		custodianOccupancyRate = Math.min(100, Math.max(85, custodianOccupancyRate + (Math.random() - 0.5) * 4));
	}
	
	// === FOUNDATION SIMULATION FUNCTIONS ===
	function getFoundationDate(months: number): string {
		const date = new Date();
		date.setMonth(date.getMonth() + months);
		return date.toLocaleDateString('en-AU', { month: 'short', year: 'numeric' });
	}
	
	function foundationStake() {
		if (foundationStakeAmount < 10000) return;
		foundationTotalStaked += foundationStakeAmount;
		
		foundationTransactions = [{
			id: Date.now(),
			type: 'stake',
			description: `Staked ${foundationLockPeriod}-month position`,
			amount: -foundationStakeAmount,
			date: getFoundationDate(foundationMonthsStaked),
			status: 'locked'
		}, ...foundationTransactions];
	}
	
	function foundationSimulateMonth() {
		if (foundationTotalStaked === 0) return;
		
		foundationMonthsStaked++;
		const monthlyYield = foundationCurrentYield / 100 / 12;
		const monthlyEarnings = foundationTotalStaked * monthlyYield;
		foundationEarnings += monthlyEarnings;
		
		// Add yield transaction
		foundationTransactions = [{
			id: Date.now(),
			type: 'yield',
			description: `Monthly yield (${foundationCurrentYield}% APY)`,
			amount: Math.round(monthlyEarnings * 100) / 100,
			date: getFoundationDate(foundationMonthsStaked),
			status: 'completed'
		}, ...foundationTransactions];
		
		// Compound if past lock period
		if (foundationMonthsStaked > foundationLockPeriod) {
			foundationTotalStaked += monthlyEarnings;
			
			foundationTransactions = [{
				id: Date.now() + 1,
				type: 'compound',
				description: `Yield compounded to stake`,
				amount: Math.round(monthlyEarnings * 100) / 100,
				date: getFoundationDate(foundationMonthsStaked),
				status: 'completed'
			}, ...foundationTransactions];
		}
		
		// Random governance participation bonus
		if (Math.random() > 0.8) {
			const bonus = Math.round(foundationTotalStaked * 0.001 * 100) / 100;
			foundationEarnings += bonus;
			
			foundationTransactions = [{
				id: Date.now() + 2,
				type: 'governance',
				description: `Governance participation bonus`,
				amount: bonus,
				date: getFoundationDate(foundationMonthsStaked),
				status: 'completed'
			}, ...foundationTransactions];
		}
	}
	
	function foundationSimulateYear() {
		for (let i = 0; i < 12; i++) {
			foundationSimulateMonth();
		}
	}
	
	function foundationWithdraw() {
		if (foundationMonthsStaked < foundationLockPeriod) return;
		const total = foundationTotalStaked + foundationEarnings;
		
		foundationTransactions = [{
			id: Date.now(),
			type: 'unstake',
			description: `Withdrew staked position + earnings`,
			amount: total,
			date: getFoundationDate(foundationMonthsStaked),
			status: 'completed'
		}, ...foundationTransactions];
		
		foundationTotalStaked = 0;
		foundationEarnings = 0;
		foundationMonthsStaked = 0;
		balance += total;
	}
	
	// Feedback handlers
	function handleVoteFeedback(feedbackId: string, vote: number) {
		const item = feedbackItems.find(f => f.id === feedbackId);
		if (!item) return;
		
		// Toggle vote
		if (item.user_vote === vote) {
			// Remove vote
			if (vote === 1) item.upvotes--;
			else item.downvotes--;
			item.user_vote = 0;
		} else {
			// Change vote
			if (item.user_vote === 1) item.upvotes--;
			else if (item.user_vote === -1) item.downvotes--;
			
			if (vote === 1) item.upvotes++;
			else item.downvotes++;
			item.user_vote = vote;
		}
		
		// Trigger reactivity
		feedbackItems = [...feedbackItems];
	}
	
	function handleSubmitFeedback() {
		if (!newFeedbackTitle || !newFeedbackDescription) return;
		
		// AI triage (simulated)
		const aiCategory = newFeedbackType === 'bug' ? 'ui' : 'general';
		const aiPriority = newFeedbackType === 'bug' ? 'high' : 'medium';
		
		const newItem = {
			id: 'fb-' + Math.random().toString(36).substring(7),
			author_name: displayName || currentUser?.email?.split('@')[0] || 'Anonymous',
			title: newFeedbackTitle,
			description: newFeedbackDescription,
			feedback_type: newFeedbackType,
			ai_category: aiCategory,
			ai_priority: aiPriority,
			ai_summary: newFeedbackDescription.slice(0, 100) + (newFeedbackDescription.length > 100 ? '...' : ''),
			status: 'open',
			upvotes: 0,
			downvotes: 0,
			comment_count: 0,
			user_vote: 0,
			created_at: new Date().toISOString().split('T')[0],
		};
		
		feedbackItems = [newItem, ...feedbackItems];
		feedbackComments[newItem.id] = [];
		
		// Reset form
		newFeedbackTitle = '';
		newFeedbackDescription = '';
		newFeedbackType = 'enhancement';
		showFeedbackDialog = false;
	}
	
	function handleAddComment(feedbackId: string) {
		if (!newComment.trim()) return;
		
		const comments = feedbackComments[feedbackId] || [];
		comments.push({
			id: 'c-' + Math.random().toString(36).substring(7),
			author_name: displayName || currentUser?.email?.split('@')[0] || 'Anonymous',
			content: newComment,
			created_at: new Date().toISOString().split('T')[0],
			is_official: false,
		});
		
		feedbackComments[feedbackId] = [...comments];
		
		// Update comment count
		const item = feedbackItems.find(f => f.id === feedbackId);
		if (item) {
			item.comment_count++;
			feedbackItems = [...feedbackItems];
		}
		
		newComment = '';
	}
	
	function openFeedbackDetail(feedback: any) {
		selectedFeedback = feedback;
		newComment = '';
		showFeedbackDetailDialog = true;
	}
	
	function getFilteredFeedback() {
		let items = [...feedbackItems];
		
		// Filter
		if (feedbackFilter !== 'all') {
			items = items.filter(f => f.feedback_type === feedbackFilter);
		}
		
		// Sort
		if (feedbackSort === 'upvotes') {
			items.sort((a, b) => (b.upvotes - b.downvotes) - (a.upvotes - a.downvotes));
		} else if (feedbackSort === 'newest') {
			items.sort((a, b) => b.created_at.localeCompare(a.created_at));
		} else if (feedbackSort === 'priority') {
			const priorityOrder: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 };
			items.sort((a, b) => (priorityOrder[a.ai_priority] ?? 4) - (priorityOrder[b.ai_priority] ?? 4));
		}
		
		return items;
	}
	
	function getPriorityColor(priority: string) {
		switch (priority) {
			case 'critical': return 'bg-red-100 text-red-700';
			case 'high': return 'bg-orange-100 text-orange-700';
			case 'medium': return 'bg-yellow-100 text-yellow-700';
			case 'low': return 'bg-green-100 text-green-700';
			default: return 'bg-gray-100 text-gray-700';
		}
	}
	
	function getStatusColor(status: string) {
		switch (status) {
			case 'open': return 'bg-blue-100 text-blue-700';
			case 'in_progress': return 'bg-purple-100 text-purple-700';
			case 'planned': return 'bg-teal-100 text-teal-700';
			case 'resolved': return 'bg-green-100 text-green-700';
			case 'wont_fix': return 'bg-gray-100 text-gray-700';
			default: return 'bg-gray-100 text-gray-700';
		}
	}
	
	function getTypeIcon(type: string) {
		switch (type) {
			case 'bug': return Bug;
			case 'enhancement': return Lightbulb;
			case 'question': return MessageSquare;
			default: return MessageSquare;
		}
	}
	
	// Chart functions
	function initProjectionChart() {
		if (!projectionChartCanvas) return;
		
		// Destroy existing chart
		if (projectionChart) {
			projectionChart.destroy();
		}
		
		const currentValue = balance + portfolioValue;
		
		// Use user-adjustable yield or calculate from holdings
		const baseYield = projectedYield;
		const monthlyRate = baseYield / 100 / 12;
		const monthlyAdd = monthlyContribution;
		
		// Generate projection with compound interest + monthly contributions
		const years = Array.from({ length: projectionYears + 1 }, (_, i) => `Year ${i}`);
		
		// Calculate future value with monthly contributions using FV formula
		const calculateProjection = (annualRate: number) => {
			return years.map((_, year) => {
				if (year === 0) return currentValue;
				const months = year * 12;
				const r = annualRate / 100 / 12;
				// FV = PV(1+r)^n + PMT * ((1+r)^n - 1) / r
				if (r === 0) return currentValue + (monthlyAdd * months);
				const compoundedPV = currentValue * Math.pow(1 + r, months);
				const futureContributions = monthlyAdd * ((Math.pow(1 + r, months) - 1) / r);
				return compoundedPV + futureContributions;
			});
		};
		
		const conservative = calculateProjection(baseYield * 0.7);
		const expected = calculateProjection(baseYield);
		const optimistic = calculateProjection(baseYield * 1.3);
		
		projectionChart = new Chart(projectionChartCanvas, {
			type: 'line',
			data: {
				labels: years,
				datasets: [
					{
						label: 'Optimistic',
						data: optimistic,
						borderColor: 'rgba(34, 197, 94, 0.5)',
						backgroundColor: 'rgba(34, 197, 94, 0.1)',
						fill: '+1',
						tension: 0.3,
						borderDash: [5, 5],
					},
					{
						label: 'Expected',
						data: expected,
						borderColor: 'rgb(59, 130, 246)',
						backgroundColor: 'rgba(59, 130, 246, 0.1)',
						fill: 'origin',
						tension: 0.3,
						borderWidth: 2,
					},
					{
						label: 'Conservative',
						data: conservative,
						borderColor: 'rgba(156, 163, 175, 0.5)',
						backgroundColor: 'transparent',
						fill: false,
						tension: 0.3,
						borderDash: [5, 5],
					},
				],
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: {
						position: 'bottom',
						labels: {
							usePointStyle: true,
							padding: 20,
						},
					},
					tooltip: {
						callbacks: {
							label: (context) => `${context.dataset.label}: $${(context.parsed.y ?? 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`,
						},
					},
				},
				scales: {
					y: {
						beginAtZero: false,
						ticks: {
							callback: (value) => `$${(Number(value) / 1000).toFixed(0)}k`,
						},
						grid: {
							color: 'rgba(0, 0, 0, 0.05)',
						},
					},
					x: {
						grid: {
							display: false,
						},
					},
				},
			},
		});
	}
	
	function initLocationChart() {
		if (!locationChartCanvas) return;
		
		// Destroy existing chart
		if (locationChart) {
			locationChart.destroy();
		}
		
		// Group holdings by suburb
		const locationData: Record<string, number> = {};
		holdings.forEach((h) => {
			const location = h.suburb || 'Unknown';
			locationData[location] = (locationData[location] || 0) + h.current_value;
		});
		
		// If no holdings, show placeholder data
		const hasData = Object.keys(locationData).length > 0;
		const labels = hasData ? Object.keys(locationData) : ['No investments yet'];
		const values = hasData ? Object.values(locationData) : [1];
		const colors = [
			'rgb(59, 130, 246)',
			'rgb(16, 185, 129)',
			'rgb(245, 158, 11)',
			'rgb(239, 68, 68)',
			'rgb(139, 92, 246)',
			'rgb(236, 72, 153)',
		];
		
		locationChart = new Chart(locationChartCanvas, {
			type: 'doughnut',
			data: {
				labels: labels,
				datasets: [{
					data: values,
					backgroundColor: hasData ? colors.slice(0, labels.length) : ['rgb(229, 231, 235)'],
					borderWidth: 0,
					hoverOffset: 4,
				}],
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				cutout: '65%',
				plugins: {
					legend: {
						position: 'bottom',
						labels: {
							usePointStyle: true,
							padding: 15,
						},
					},
					tooltip: {
						callbacks: {
							label: (context) => {
								if (!hasData) return 'Invest to see distribution';
								const value = context.parsed;
								const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
								const percentage = ((value / total) * 100).toFixed(1);
								return `${context.label}: $${value.toLocaleString()} (${percentage}%)`;
							},
						},
					},
				},
			},
		});
	}
	
	// Update charts when holdings change or canvas becomes available
	$effect(() => {
		// Track dependencies
		const _holdings = holdings.length;
		const _projCanvas = projectionChartCanvas;
		const _locCanvas = locationChartCanvas;
		
		if (isSignedUp && activeTab === 'dashboard') {
			// Small delay to ensure canvas is mounted
			setTimeout(() => {
				if (projectionChartCanvas) initProjectionChart();
				if (locationChartCanvas) initLocationChart();
			}, 100);
		}
	});
	
	// Update projection chart when user adjusts parameters
	$effect(() => {
		// Track these values to trigger updates
		const _yield = projectedYield;
		const _monthly = monthlyContribution;
		const _years = projectionYears;
		
		if (isSignedUp && activeTab === 'dashboard' && projectionChartCanvas) {
			initProjectionChart();
		}
	});
	
	// Calculate projected values for display
	function getProjectedValue(years: number, yield_: number, monthly: number): number {
		const currentValue = balance + portfolioValue;
		const months = years * 12;
		const r = yield_ / 100 / 12;
		if (r === 0) return currentValue + (monthly * months);
		const compoundedPV = currentValue * Math.pow(1 + r, months);
		const futureContributions = monthly * ((Math.pow(1 + r, months) - 1) / r);
		return compoundedPV + futureContributions;
	}
	
	// Update yield from holdings when holdings change
	$effect(() => {
		if (holdings.length > 0) {
			const avgYield = holdings.reduce((sum, h) => sum + h.yield_percent, 0) / holdings.length;
			projectedYield = Math.round(avgYield * 10) / 10;
		}
	});

	// Initialize auth config
	$effect(() => {
		if (browser && !authConfig) {
			fetchAuthConfig().then(config => {
				authConfig = config;
			});
		}
	});
	
	// =====================================================
	// Pool Assets Integration (AI-Generated Properties & Avatars)
	// =====================================================
	let poolProperties = $state<PoolProperty[]>([]);
	let poolAvatars = $state<Record<string, PoolAvatar>>({});
	let poolLoading = $state(false);
	let selectedPropertyDetail = $state<PoolProperty | null>(null);
	let showPropertyDetailModal = $state(false);
	let selectedAvatar = $state<string | null>(null);
	
	// Initialize pool and load assets
	$effect(() => {
		if (browser) {
			initPool(API_BASE);
			loadPoolAssets();
			checkOnboarding(); // Show onboarding for first-time users
		}
	});
	
	async function loadPoolAssets() {
		poolLoading = true;
		try {
			const [props, avs] = await Promise.all([
				fetchProperties(12),
				fetchAvatars()
			]);
			poolProperties = props;
			poolAvatars = avs;
			
			// Merge pool properties with existing mock properties
			// Pool properties take priority and have AI content
			if (props.length > 0) {
				const poolPropertyCards = props.map(p => ({
					id: p.id,
					address: p.data?.address || p.address,
					suburb: p.data?.suburb || p.suburb,
					postcode: p.data?.postcode || '',
					state: p.data?.state || 'WA',
					property_type: p.data?.property_type || p.property_type,
					bedrooms: p.data?.bedrooms || p.bedrooms,
					bathrooms: p.data?.bathrooms || p.bathrooms,
					car_spaces: p.data?.parking || 1,
					land_size_sqm: p.data?.land_size || 0,
					floor_size_sqm: p.data?.build_area || 0,
					valuation_aud: p.data?.valuation || p.valuation,
					token_price: 1.00,
					yield_percent: p.data?.gross_yield || 4.2,
					year_built: p.data?.year_built || 2020,
					features: p.data?.features || [],
					highlights: p.highlights?.map((h: any) => h.title) || p.listing?.highlights?.map((h: any) => h.title) || [],
					photos_count: 12,
					listing_status: 'active',
					page_views: Math.floor(Math.random() * 100) + 50,
					council_rates: p.listing?.rates?.council || 2500,
					water_rates: p.listing?.rates?.water || 1200,
					strata_fees: 0,
					estimated_rent_pw: Math.round((p.data?.valuation || p.valuation || 500000) * 0.004 / 4),
					price_history: [],
					// Keep pool data for detail view - include images from summary
					_poolData: {
						...p,
						images: p.images || {},
						listing: p.listing || { headline: p.headline, highlights: p.highlights },
						data: p.data || { 
							address: p.address, 
							suburb: p.suburb, 
							property_type: p.property_type,
							bedrooms: p.bedrooms,
							bathrooms: p.bathrooms,
							valuation: p.valuation
						}
					},
				})) as any;
				
				// Replace properties with pool properties
				properties = poolPropertyCards;
			}
		} catch (e) {
			console.error('Failed to load pool assets:', e);
		} finally {
			poolLoading = false;
		}
	}
	
	// Open property detail modal with full AI content
	async function openPoolPropertyDetail(property: any) {
		if (property._poolData) {
			// Already have full pool data
			selectedPropertyDetail = property._poolData;
			showPropertyDetailModal = true;
		} else if (property.id?.startsWith('prop_')) {
			// Fetch from pool API
			const full = await fetchProperty(property.id);
			if (full) {
				selectedPropertyDetail = full;
				showPropertyDetailModal = true;
			}
		} else {
			// Legacy property - show basic dialog
			openPropertyDetail(property);
		}
	}
	
	function closePoolPropertyDetail() {
		showPropertyDetailModal = false;
		selectedPropertyDetail = null;
	}
	
	// =====================================================
	// Network Clock Integration
	// =====================================================
	// Listen for synchronized clock events when in sync mode
	function handleNetworkClockTick(event: CustomEvent) {
		if (clockMode === 'sync') {
			console.log('[Simulation] Clock tick received, processing month...', event.detail);
			simulateNetworkMonth();
		}
	}
	
	// Set up event listener for clock ticks
	$effect(() => {
		if (browser && clockMode === 'sync') {
			window.addEventListener('osf:month_completed', handleNetworkClockTick as EventListener);
			return () => {
				window.removeEventListener('osf:month_completed', handleNetworkClockTick as EventListener);
			};
		}
	});
	
	// Toggle between manual and synchronized clock mode
	function toggleClockMode() {
		clockMode = clockMode === 'manual' ? 'sync' : 'manual';
		console.log(`[Simulation] Clock mode: ${clockMode}`);
	}
	
	// Change backend clock preset
	async function setClockPreset(presetId: string) {
		try {
			const res = await fetch(`${API_BASE}/network/clock/preset`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ preset: presetId })
			});
			if (res.ok) {
				console.log(`[Simulation] Clock preset changed to: ${presetId}`);
			}
		} catch (e) {
			console.error('Failed to set clock preset', e);
		}
	}
</script>

<div class="bg-gray-50 min-h-screen">
	<!-- Simulation Banner -->
	<div class="bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 px-4">
		<div class="max-w-7xl mx-auto flex items-center justify-between">
			<div class="flex items-center gap-3">
				<Badge variant="secondary" class="bg-white/20 text-white border-0">
					SIMULATION MODE
				</Badge>
				<span class="text-sm hidden sm:inline">
					Practice with $100,000 virtual funds. No real money involved.
				</span>
			</div>
			{#if isSignedUp}
				<div class="flex items-center gap-2">
					<!-- Tab Navigation -->
					<div class="flex bg-white/10 rounded-lg p-1">
						<button 
							class="px-3 py-1 text-sm rounded-md transition {activeTab === 'dashboard' ? 'bg-white text-blue-600 font-medium' : 'text-white hover:bg-white/10'}"
							onclick={() => activeTab = 'dashboard'}
						>
							Dashboard
						</button>
						<button 
							class="px-3 py-1 text-sm rounded-md transition flex items-center gap-1 {activeTab === 'network' ? 'bg-white text-blue-600 font-medium' : 'text-white hover:bg-white/10'}"
							onclick={() => activeTab = 'network'}
						>
							<TrendingUp class="w-3.5 h-3.5" />
							Network
						</button>
						<button 
							class="px-3 py-1 text-sm rounded-md transition flex items-center gap-1 {activeTab === 'governance' ? 'bg-white text-blue-600 font-medium' : 'text-white hover:bg-white/10'}"
							onclick={() => activeTab = 'governance'}
						>
							<Vote class="w-3.5 h-3.5" />
							Governance
						</button>
						<button 
							class="px-3 py-1 text-sm rounded-md transition flex items-center gap-1 {activeTab === 'leaderboard' ? 'bg-white text-blue-600 font-medium' : 'text-white hover:bg-white/10'}"
							onclick={() => activeTab = 'leaderboard'}
						>
							<Trophy class="w-3.5 h-3.5" />
							Leaderboard
						</button>
						<button 
							class="px-3 py-1 text-sm rounded-md transition flex items-center gap-1 {activeTab === 'feedback' ? 'bg-white text-blue-600 font-medium' : 'text-white hover:bg-white/10'}"
							onclick={() => activeTab = 'feedback'}
						>
							<Users class="w-3.5 h-3.5" />
							Community
							<span class="bg-white/20 text-white text-xs px-1.5 py-0.5 rounded-full">{feedbackItems.length}</span>
							{#if communitySentiment.score < -0.2}
								<span class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
							{/if}
						</button>
						<button 
							class="px-3 py-1 text-sm rounded-md transition flex items-center gap-1 {activeTab === 'ledger' ? 'bg-white text-blue-600 font-medium' : 'text-white hover:bg-white/10'}"
							onclick={() => activeTab = 'ledger'}
						>
							<FileText class="w-3.5 h-3.5" />
							Ledger
						</button>
						<button 
							class="px-3 py-1 text-sm rounded-md transition flex items-center gap-1 {activeTab === 'thinking' ? 'bg-white text-purple-600 font-medium' : 'text-white hover:bg-white/10'}"
							onclick={() => activeTab = 'thinking'}
						>
							<Sparkles class="w-3.5 h-3.5" />
							AI Thinking
							{#if aiThinkingLog.length > 0}
								<span class="ml-1 bg-purple-500 text-white text-xs px-1.5 rounded-full">{aiThinkingLog.length}</span>
							{/if}
						</button>
						<button 
							class="px-3 py-1 text-sm rounded-md transition flex items-center gap-1 {activeTab === 'health' ? 'bg-white text-green-600 font-medium' : 'text-white hover:bg-white/10'}"
							onclick={() => activeTab = 'health'}
						>
							<Activity class="w-3.5 h-3.5" />
							Health
							{#if overallHealthStatus !== 'healthy'}
								<span class="w-2 h-2 rounded-full {overallHealthStatus === 'critical' ? 'bg-red-500' : 'bg-yellow-500'} animate-pulse"></span>
							{/if}
						</button>
					</div>
					<Button variant="ghost" size="sm" class="text-white hover:bg-white/10" onclick={handleReset}>
						<RefreshCw class="w-4 h-4 mr-2" />
						Reset
					</Button>
				</div>
			{/if}
		</div>
	</div>

	{#if !isSignedUp}
		<!-- Signup Screen -->
		<div class="max-w-2xl mx-auto px-4 py-16">
			<div class="text-center mb-8">
				<div class="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
					<Play class="w-8 h-8 text-blue-600" />
				</div>
				<h1 class="text-3xl font-bold text-gray-900 mb-2">Try OSF Risk-Free</h1>
				<p class="text-gray-500 text-lg">
					Get $100,000 in virtual funds to explore property investment
				</p>
			</div>

			<Card.Root class="max-w-md mx-auto">
				<Card.Content class="pt-6">
					{#if loginError}
						<div class="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
							<AlertCircle class="w-4 h-4 shrink-0" />
							<span class="text-sm">{loginError}</span>
						</div>
					{/if}
					
					{#if authConfig?.mode === 'google'}
						<!-- Google OAuth mode - redirect to login -->
						<div class="text-center space-y-4">
							<p class="text-gray-600">Sign in with your Google account to continue</p>
							<Button onclick={() => goto('/auth/login')} class="w-full">
								<svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
									<path fill="#fff" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
									<path fill="#fff" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
								</svg>
								Continue with Google
							</Button>
						</div>
					{:else}
						<!-- Dev mode - email login -->
						<div class="space-y-4">
							{#if authConfig?.mode === 'dev'}
								<div class="flex items-center gap-2 mb-2">
									<Badge variant="outline" class="text-amber-600 border-amber-300 bg-amber-50">Dev Mode</Badge>
									<span class="text-xs text-gray-500">Any email works</span>
								</div>
							{/if}
							<div>
								<label for="sim-email" class="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
								<Input 
									id="sim-email"
									type="email" 
									placeholder="you@example.com" 
									bind:value={loginEmail}
									onkeydown={(e) => e.key === 'Enter' && handleSignup()}
								/>
							</div>
							<div>
								<label for="sim-name" class="block text-sm font-medium text-gray-700 mb-2">Display Name (optional)</label>
								<Input 
									id="sim-name"
									type="text" 
									placeholder="Your nickname for leaderboard" 
									bind:value={loginDisplayName}
									onkeydown={(e) => e.key === 'Enter' && handleSignup()}
								/>
							</div>
							
							<!-- Avatar Selection -->
							{#if Object.keys(poolAvatars).length > 0}
								<div>
									<label class="block text-sm font-medium text-gray-700 mb-2">
										Choose Your Avatar
										<span class="text-xs text-gray-500 ml-1">(optional)</span>
									</label>
									<div class="max-h-48 overflow-y-auto border border-gray-200 rounded-lg p-3">
										<div class="grid grid-cols-4 gap-2">
											{#each Object.entries(poolAvatars).filter(([_, a]) => a.category === 'participant').slice(0, 12) as [role, avatar]}
												<button
													type="button"
													class="relative rounded-lg overflow-hidden aspect-square transition-all {selectedAvatar === role ? 'ring-2 ring-blue-500 ring-offset-1' : 'hover:ring-2 hover:ring-gray-300'}"
													onclick={() => selectedAvatar = selectedAvatar === role ? null : role}
													title={formatRoleName(role)}
												>
													<img 
														src={avatar.image} 
														alt={formatRoleName(role)}
														class="w-full h-full object-cover"
													/>
													{#if selectedAvatar === role}
														<div class="absolute inset-0 bg-blue-500/20 flex items-center justify-center">
															<Check class="w-6 h-6 text-white drop-shadow-lg" />
														</div>
													{/if}
												</button>
											{/each}
										</div>
									</div>
								</div>
							{/if}
							
							<Button class="w-full" onclick={handleSignup} disabled={!loginEmail || isLoading}>
								{#if isLoading}
									Starting...
								{:else}
									Start Simulation
								{/if}
							</Button>
							<p class="text-xs text-gray-500 text-center">
								No credit card required. No real money. Just learning.
							</p>
						</div>
					{/if}
				</Card.Content>
			</Card.Root>

			<div class="mt-12 grid md:grid-cols-3 gap-6">
				<div class="text-center">
					<div class="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center mx-auto mb-3">
						<Wallet class="w-6 h-6 text-gray-600" />
					</div>
					<h3 class="font-medium text-gray-900">$100K Virtual Funds</h3>
					<p class="text-sm text-gray-500">Practice investing without risk</p>
				</div>
				<div class="text-center">
					<div class="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center mx-auto mb-3">
						<Building class="w-6 h-6 text-gray-600" />
					</div>
					<h3 class="font-medium text-gray-900">Real Property Data</h3>
					<p class="text-sm text-gray-500">Actual Australian properties</p>
				</div>
				<div class="text-center">
					<div class="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center mx-auto mb-3">
						<Trophy class="w-6 h-6 text-gray-600" />
					</div>
					<h3 class="font-medium text-gray-900">Compete & Learn</h3>
					<p class="text-sm text-gray-500">Leaderboard and achievements</p>
				</div>
			</div>
		</div>
	{:else}
		{#if activeTab === 'dashboard'}
		<!-- Simulation Dashboard -->
		<div class="max-w-7xl mx-auto px-4 py-8">
			<!-- Header -->
			<div class="flex items-center justify-between mb-6">
				<div>
					<h1 class="text-2xl font-bold text-gray-900">Simulation Dashboard</h1>
					<p class="text-gray-500">Welcome back, {displayName}</p>
				</div>
				<div class="flex items-center gap-4">
					<div class="flex items-center gap-2 text-sm text-gray-600">
						<UserCircle class="w-5 h-5" />
						<span>{currentUser?.email}</span>
					</div>
					<Button variant="ghost" size="sm" onclick={handleLogout}>
						<LogOut class="w-4 h-4 mr-1" />
						Sign out
					</Button>
					<a href="/" class="text-gray-500 hover:text-gray-900 text-sm">← Back home</a>
				</div>
			</div>

			<!-- Simulation Disclaimer -->
			<div class="mb-6 bg-amber-50 border border-amber-200 rounded-lg p-3 flex items-center gap-3">
				<div class="w-8 h-8 bg-amber-100 rounded-full flex items-center justify-center flex-shrink-0">
					<span class="text-amber-600 text-lg">🎮</span>
				</div>
				<div class="text-sm">
					<span class="font-medium text-amber-800">Simulation Mode</span>
					<span class="text-amber-700"> — This is an educational sandbox. No real money, no real assets, no financial advice. All data is simulated.</span>
				</div>
			</div>

			<!-- Role Selector -->
			<div class="mb-8">
				<div class="flex flex-wrap gap-2 p-2 bg-gray-100 rounded-xl">
					{#each roles as role}
						<button
							onclick={() => { activeRole = role.id; trackRoleExplored(role.id); }}
							class="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all {activeRole === role.id ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'}"
						>
							<svelte:component this={role.icon} class="w-4 h-4" />
							<span class="hidden sm:inline">{role.label}</span>
						</button>
					{/each}
				</div>
				<div class="flex items-center gap-2 mt-2">
					<p class="text-sm text-gray-500">
						{roles.find(r => r.id === activeRole)?.desc}
					</p>
					<button
						onclick={() => showRoleInfoDialog = true}
						class="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center gap-1"
					>
						<Info class="w-4 h-4" />
						Learn more
					</button>
				</div>
			</div>
			
		<!-- Network Status Bar (visible on all role tabs) -->
		<div class="bg-gradient-to-r from-slate-800 to-slate-700 rounded-xl p-4 mb-6">
			<div class="flex items-center justify-between flex-wrap gap-4">
				<!-- Left: Clock Mode Toggle + Month/Stats -->
				<div class="flex items-center gap-4">
					<!-- Clock Mode Toggle -->
					<button
						onclick={toggleClockMode}
						class="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all {clockMode === 'sync' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-slate-600/50 text-slate-400 border border-slate-600'}"
						title={clockMode === 'sync' ? 'Synchronized with network clock (click to switch to manual)' : 'Manual mode (click to sync with network clock)'}
					>
						{#if clockMode === 'sync'}
							<Wifi class="w-3.5 h-3.5" />
							<span>Synced</span>
						{:else}
							<WifiOff class="w-3.5 h-3.5" />
							<span>Manual</span>
						{/if}
					</button>
					
					<!-- Network Month -->
					<div class="flex items-center gap-2">
						<div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
						<span class="text-white text-sm font-medium">Month {networkMonth}</span>
					</div>
					
					<!-- Network Stats -->
					<div class="hidden md:flex items-center gap-4">
						<!-- WA Market Condition Badge -->
						<div class="flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium
							{marketCondition === 'boom' ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 
							 marketCondition === 'stable' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' :
							 marketCondition === 'stagnant' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' :
							 marketCondition === 'declining' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
							 'bg-red-500/20 text-red-400 border border-red-500/30'}">
							<span class="w-1.5 h-1.5 rounded-full 
								{marketCondition === 'boom' ? 'bg-green-400' : 
								 marketCondition === 'stable' ? 'bg-blue-400' :
								 marketCondition === 'stagnant' ? 'bg-yellow-400' :
								 marketCondition === 'declining' ? 'bg-orange-400' : 'bg-red-400'}"></span>
							{marketCondition.toUpperCase()}
						</div>
						<div class="text-slate-300 text-sm" title="Iron ore price - WA's primary economic driver">
							<span class="text-slate-400">Fe:</span> ${ironOrePrice.toFixed(0)}/t
						</div>
						<div class="text-slate-300 text-sm" title="WA population growth rate">
							<span class="text-slate-400">Pop:</span> {populationGrowthRate.toFixed(1)}%
						</div>
						<div class="text-slate-300 text-sm">
							<span class="text-slate-400">Properties:</span> ${(networkTotalPropertyValue / 1000000).toFixed(2)}M
						</div>
						<div class="text-slate-300 text-sm">
							<span class="text-slate-400">Yield:</span> {networkAverageYield.toFixed(1)}%
						</div>
					</div>
				</div>
				
				<!-- Right: Controls -->
				<div class="flex items-center gap-2">
					{#if clockMode === 'sync'}
						<!-- Synchronized Clock Display -->
						<NetworkClock apiBase={API_BASE} compact={true} />
					{:else}
						<!-- Manual Mode Controls -->
						<button 
							class="w-6 h-6 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white/70 hover:text-white transition"
							onclick={() => showSimulationInfoDialog = true}
							title="Learn about time simulation"
						>
							<Info class="w-3.5 h-3.5" />
						</button>
						<Button size="sm" variant="secondary" onclick={simulateNetworkMonth}>
							<Play class="w-3 h-3 mr-1" />
							+1 Month
						</Button>
						<Button size="sm" variant="ghost" class="text-white border border-white/30 bg-transparent hover:bg-white/10" onclick={() => { for(let i=0; i<12; i++) simulateNetworkMonth(); }}>
							+1 Year
						</Button>
						<!-- Marathon Mode Toggle -->
						{#if marathonMode}
							<Button size="sm" variant="ghost" class="text-amber-400 border border-amber-400/30 bg-amber-500/10 hover:bg-amber-500/20" onclick={pauseMarathon}>
								{#if marathonPaused}
									<Play class="w-3 h-3 mr-1" />
									Resume
								{:else}
									<Pause class="w-3 h-3 mr-1" />
									Pause
								{/if}
							</Button>
							<Button size="sm" variant="ghost" class="text-red-400 border border-red-400/30 bg-red-500/10 hover:bg-red-500/20" onclick={stopMarathon}>
								Stop
							</Button>
						{:else}
							<Button size="sm" variant="ghost" class="text-purple-400 border border-purple-400/30 bg-purple-500/10 hover:bg-purple-500/20" onclick={startMarathon}>
								<Zap class="w-3 h-3 mr-1" />
								Marathon
							</Button>
						{/if}
					{/if}
					<Button size="sm" variant="ghost" class="text-white hover:bg-white/10" onclick={() => activeTab = 'network'}>
						View Network →
					</Button>
				</div>
			</div>
			
			<!-- Activity Feed -->
			{#if networkEvents.length > 0}
				<div class="mt-3 pt-3 border-t border-slate-600">
					<div class="text-xs text-slate-400 mb-1">Latest activity:</div>
					<div class="flex gap-4 overflow-x-auto pb-1">
						{#each networkEvents.slice(0, 4) as event}
							<div class="flex items-center gap-2 text-xs text-slate-300 whitespace-nowrap">
								<span class="w-1.5 h-1.5 rounded-full {
									event.type === 'dividend_paid' ? 'bg-green-400' :
									event.type === 'rent_collected' ? 'bg-blue-400' :
									event.type === 'service_payment' ? 'bg-amber-400' :
									'bg-slate-400'
								}"></span>
								{event.description.slice(0, 30)}{event.description.length > 30 ? '...' : ''}
							</div>
						{/each}
					</div>
				</div>
			{/if}
			
			<!-- Sync Mode: Full Clock Controls (when expanded) -->
			{#if clockMode === 'sync'}
				<div class="mt-3 pt-3 border-t border-slate-600">
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2">
							<span class="text-xs text-slate-400">Clock Preset:</span>
							{#each clockPresets as preset}
								<button
									onclick={() => setClockPreset(preset.id)}
									class="px-2 py-1 text-xs rounded transition-colors hover:bg-white/10 text-slate-300"
									title={preset.desc}
								>
									{preset.label}
								</button>
							{/each}
						</div>
						<div class="text-xs text-slate-500">
							All users sync to the same network time
						</div>
					</div>
				</div>
			{/if}
		</div>

			{#if activeRole === 'investor'}
			<!-- INVESTOR SIMULATION -->
			
			<!-- Homeowner Equity Notice -->
			{#if holdings.some(h => h.isHomeownerEquity)}
			<div class="mb-6 p-4 bg-purple-50 border border-purple-200 rounded-lg flex items-start gap-3">
				<div class="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
					<Home class="w-5 h-5 text-purple-600" />
				</div>
				<div>
					<p class="font-medium text-purple-900">Your home equity is now working for you</p>
					<p class="text-sm text-purple-700">You accessed equity as a homeowner and received OSF tokens. These tokens earn dividends alongside your other investments.</p>
				</div>
			</div>
			{/if}
			
			<!-- Portfolio Summary -->
			<div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
				<Card.Root>
					<Card.Content class="pt-6">
						<div class="text-gray-500 text-sm mb-1">Cash Balance</div>
						<div class="text-2xl font-bold text-gray-900">${balance.toLocaleString()}</div>
					</Card.Content>
				</Card.Root>
				<Card.Root>
					<Card.Content class="pt-6">
						<div class="text-gray-500 text-sm mb-1">Portfolio Value</div>
						<div class="text-2xl font-bold text-gray-900">${portfolioValue.toLocaleString()}</div>
					</Card.Content>
				</Card.Root>
				<Card.Root>
					<Card.Content class="pt-6">
						<div class="text-gray-500 text-sm mb-1">Total Value</div>
						<div class="text-2xl font-bold text-gray-900">${(balance + portfolioValue).toLocaleString()}</div>
					</Card.Content>
				</Card.Root>
				<Card.Root>
					<Card.Content class="pt-6">
						<div class="text-gray-500 text-sm mb-1">Total Return</div>
						<div class="text-2xl font-bold {totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}">
							{totalReturn >= 0 ? '+' : ''}{totalReturnPercent.toFixed(1)}%
						</div>
						<div class="text-sm {totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}">
							{totalReturn >= 0 ? '+' : ''}${totalReturn.toLocaleString()}
						</div>
					</Card.Content>
				</Card.Root>
			</div>
			
			<!-- Charts Section -->
			<div class="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-8">
				<!-- Projected Investment Chart -->
				<Card.Root class="xl:col-span-2">
					<Card.Header>
						<Card.Title class="flex items-center gap-2">
							<TrendingUp class="w-5 h-5 text-blue-600" />
							Investment Projection
						</Card.Title>
						<p class="text-sm text-gray-500">Adjust the parameters to see how your investment could grow</p>
					</Card.Header>
					<Card.Content>
						<!-- Calculator Controls -->
						<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
							<div>
								<label for="yield-slider" class="block text-sm font-medium text-gray-700 mb-2">
									Expected Yield
									<span class="text-blue-600 font-bold ml-1">{projectedYield.toFixed(1)}%</span>
								</label>
								<input 
									id="yield-slider"
									type="range" 
									min="1" 
									max="10" 
									step="0.1" 
									bind:value={projectedYield}
									class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
								/>
								<div class="flex justify-between text-xs text-gray-400 mt-1">
									<span>1%</span>
									<span>10%</span>
								</div>
							</div>
							<div>
								<label for="monthly-slider" class="block text-sm font-medium text-gray-700 mb-2">
									Monthly Contribution
									<span class="text-blue-600 font-bold ml-1">${monthlyContribution.toLocaleString()}</span>
								</label>
								<input 
									id="monthly-slider"
									type="range" 
									min="0" 
									max="5000" 
									step="100" 
									bind:value={monthlyContribution}
									class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
								/>
								<div class="flex justify-between text-xs text-gray-400 mt-1">
									<span>$0</span>
									<span>$5,000</span>
								</div>
							</div>
							<div>
								<label for="years-slider" class="block text-sm font-medium text-gray-700 mb-2">
									Time Horizon
									<span class="text-blue-600 font-bold ml-1">{projectionYears} years</span>
								</label>
								<input 
									id="years-slider"
									type="range" 
									min="5" 
									max="30" 
									step="1" 
									bind:value={projectionYears}
									class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
								/>
								<div class="flex justify-between text-xs text-gray-400 mt-1">
									<span>5 yrs</span>
									<span>30 yrs</span>
								</div>
							</div>
						</div>
						
						<!-- Projection Summary -->
						<div class="grid grid-cols-3 gap-4 mb-6">
							<div class="text-center p-3 bg-gray-100 rounded-lg">
								<div class="text-xs text-gray-500 mb-1">Conservative ({(projectedYield * 0.7).toFixed(1)}%)</div>
								<div class="text-lg font-bold text-gray-600">
									${getProjectedValue(projectionYears, projectedYield * 0.7, monthlyContribution).toLocaleString(undefined, { maximumFractionDigits: 0 })}
								</div>
							</div>
							<div class="text-center p-3 bg-blue-50 rounded-lg border border-blue-200">
								<div class="text-xs text-blue-600 mb-1">Expected ({projectedYield.toFixed(1)}%)</div>
								<div class="text-lg font-bold text-blue-700">
									${getProjectedValue(projectionYears, projectedYield, monthlyContribution).toLocaleString(undefined, { maximumFractionDigits: 0 })}
								</div>
							</div>
							<div class="text-center p-3 bg-green-50 rounded-lg">
								<div class="text-xs text-green-600 mb-1">Optimistic ({(projectedYield * 1.3).toFixed(1)}%)</div>
								<div class="text-lg font-bold text-green-600">
									${getProjectedValue(projectionYears, projectedYield * 1.3, monthlyContribution).toLocaleString(undefined, { maximumFractionDigits: 0 })}
								</div>
							</div>
						</div>
						
						<!-- Chart -->
						<div class="h-64">
							<canvas bind:this={projectionChartCanvas}></canvas>
						</div>
						
						<!-- Calculation Breakdown -->
						<div class="mt-4 p-3 bg-gray-50 rounded-lg text-sm text-gray-600">
							<div class="flex justify-between">
								<span>Starting Value:</span>
								<span class="font-medium">${(balance + portfolioValue).toLocaleString()}</span>
							</div>
							<div class="flex justify-between mt-1">
								<span>Total Contributions ({projectionYears} yrs):</span>
								<span class="font-medium">${(monthlyContribution * 12 * projectionYears).toLocaleString()}</span>
							</div>
							<div class="flex justify-between mt-1">
								<span>Projected Growth (Expected):</span>
								<span class="font-medium text-green-600">
									+${(getProjectedValue(projectionYears, projectedYield, monthlyContribution) - (balance + portfolioValue) - (monthlyContribution * 12 * projectionYears)).toLocaleString(undefined, { maximumFractionDigits: 0 })}
								</span>
							</div>
						</div>
					</Card.Content>
				</Card.Root>
				
				<!-- Auto-Invest & Location -->
				<Card.Root>
					<Card.Header>
						<Card.Title class="flex items-center gap-2">
							<RefreshCw class="w-5 h-5 text-purple-600" />
							Auto-Invest
						</Card.Title>
						<p class="text-sm text-gray-500">Set up recurring monthly investments</p>
					</Card.Header>
					<Card.Content>
						{#if !recurringEnabled}
							<!-- Setup Auto-Invest -->
							<div class="space-y-4">
								<div>
									<label for="recurring-amount" class="block text-sm font-medium text-gray-700 mb-2">
										Monthly Amount
									</label>
									<div class="flex items-center gap-2">
										<span class="text-gray-500">$</span>
										<input 
											id="recurring-amount"
											type="number" 
											min="100" 
											max="10000" 
											step="100"
											bind:value={recurringAmount}
											class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
										/>
									</div>
								</div>
								
								<div>
									<label for="recurring-property" class="block text-sm font-medium text-gray-700 mb-2">
										Invest In
									</label>
									<select 
										id="recurring-property"
										bind:value={recurringPropertyId}
										class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
									>
										<option value="">Select a property...</option>
										{#each properties as property}
											<option value={property.id}>
												{property.address}, {property.suburb} ({property.yield_percent}% yield)
											</option>
										{/each}
									</select>
								</div>
								
								<Button 
									class="w-full bg-purple-600 hover:bg-purple-700" 
									onclick={setupRecurringInvestment}
									disabled={!recurringPropertyId || recurringAmount < 100}
								>
									<RefreshCw class="w-4 h-4 mr-2" />
									Start Auto-Invest
								</Button>
								
								<p class="text-xs text-gray-500 text-center">
									Simulates monthly purchases to show compound growth
								</p>
							</div>
						{:else}
							<!-- Active Auto-Invest -->
							<div class="space-y-4">
								<div class="p-4 bg-purple-50 rounded-lg border border-purple-200">
									<div class="flex items-center justify-between mb-2">
										<span class="text-sm font-medium text-purple-700">Auto-Invest Active</span>
										<Badge variant="outline" class="bg-purple-100 text-purple-700 border-purple-200">
											{simulatedMonths} months
										</Badge>
									</div>
									<div class="text-2xl font-bold text-purple-900 mb-1">
										${recurringAmount.toLocaleString()}/month
									</div>
									<div class="text-sm text-purple-600">
										→ {getRecurringProperty()?.address}, {getRecurringProperty()?.suburb}
									</div>
									<div class="text-xs text-purple-500 mt-2">
										Total invested: ${(recurringAmount * simulatedMonths).toLocaleString()}
									</div>
								</div>
								
								<!-- Simulate Time Buttons -->
								<div class="grid grid-cols-3 gap-2">
									<Button 
										variant="outline" 
										size="sm"
										onclick={() => simulateMultipleMonths(1)}
										disabled={balance < recurringAmount}
									>
										+1 Month
									</Button>
									<Button 
										variant="outline" 
										size="sm"
										onclick={() => simulateMultipleMonths(6)}
										disabled={balance < recurringAmount}
									>
										+6 Months
									</Button>
									<Button 
										variant="outline" 
										size="sm"
										onclick={() => simulateMultipleMonths(12)}
										disabled={balance < recurringAmount}
									>
										+1 Year
									</Button>
								</div>
								
								{#if balance < recurringAmount}
									<div class="p-2 bg-amber-50 rounded-lg border border-amber-200 text-xs text-amber-700">
										Insufficient balance for next auto-invest. Add more funds or reduce monthly amount.
									</div>
								{/if}
								
								<Button 
									variant="outline" 
									class="w-full text-red-600 border-red-200 hover:bg-red-50"
									onclick={cancelRecurringInvestment}
								>
									Cancel Auto-Invest
								</Button>
							</div>
						{/if}
						
						<!-- Location Breakdown -->
						{#if holdings.length > 0}
							<div class="mt-6 pt-4 border-t border-gray-200">
								<div class="flex items-center gap-2 mb-3">
									<MapPin class="w-4 h-4 text-gray-500" />
									<span class="text-sm font-medium text-gray-700">Portfolio by Location</span>
								</div>
								<div class="space-y-2">
									{#each holdings as holding}
										<div class="flex items-center justify-between text-sm">
											<span class="text-gray-600">{holding.suburb}</span>
											<div class="flex items-center gap-2">
												<div class="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
													<div 
														class="h-full bg-blue-500 rounded-full" 
														style="width: {(holding.current_value / portfolioValue * 100)}%"
													></div>
												</div>
												<span class="text-gray-900 font-medium w-16 text-right">
													{(holding.current_value / portfolioValue * 100).toFixed(0)}%
												</span>
											</div>
										</div>
									{/each}
								</div>
							</div>
						{/if}
					</Card.Content>
				</Card.Root>
			</div>
			
			<!-- Location Chart (Full Width when has holdings) -->
			{#if holdings.length > 0}
			<div class="mb-8">
				<Card.Root>
					<Card.Header>
						<Card.Title class="flex items-center gap-2">
							<MapPin class="w-5 h-5 text-green-600" />
							Investment Distribution
						</Card.Title>
						<p class="text-sm text-gray-500">Visual breakdown of your portfolio allocation</p>
					</Card.Header>
					<Card.Content>
						<div class="h-64 flex items-center justify-center">
							<canvas bind:this={locationChartCanvas}></canvas>
						</div>
					</Card.Content>
				</Card.Root>
			</div>
			{/if}

			<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
				<!-- Main Content -->
				<div class="lg:col-span-2 space-y-6">
					<!-- Holdings -->
					<Card.Root>
						<Card.Header>
							<Card.Title>Your Holdings</Card.Title>
						</Card.Header>
						<Card.Content>
							{#if holdings.length === 0}
								<div class="text-center py-8 text-gray-500">
									<Building class="w-12 h-12 mx-auto mb-3 text-gray-300" />
									<p>No holdings yet. Browse properties below to start investing.</p>
								</div>
							{:else}
								<div class="space-y-3">
								{#each holdings as holding}
									<div class="border {holding.isHomeownerEquity ? 'border-purple-300 bg-purple-50/50' : 'border-gray-200'} rounded-lg p-4">
										<div class="flex items-center justify-between">
											<div>
												<div class="font-medium text-gray-900 flex items-center gap-2">
													{holding.address}
													{#if holding.isHomeownerEquity}
														<span class="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">Your Home Equity</span>
													{/if}
												</div>
												<div class="text-sm text-gray-500">{holding.suburb}</div>
												<div class="text-sm text-gray-500">{holding.token_amount.toLocaleString()} tokens</div>
											</div>
											<div class="text-right">
												<div class="font-medium text-gray-900">${holding.current_value.toLocaleString()}</div>
												<div class="text-sm text-green-600">{holding.yield_percent}% yield</div>
												<Button variant="outline" size="sm" onclick={() => handleSell(holding)} class="mt-2">
													{holding.isHomeownerEquity ? 'Redeem' : 'Sell'}
												</Button>
											</div>
										</div>
									</div>
								{/each}
								</div>
							{/if}
						</Card.Content>
					</Card.Root>

					<!-- Properties to Buy -->
					<Card.Root>
						<Card.Header class="flex flex-row items-center justify-between">
							<div>
								<Card.Title>Available Properties</Card.Title>
								<Card.Description>{properties.length} properties in network</Card.Description>
							</div>
							<div class="flex gap-2">
								<Button size="sm" variant="outline" onclick={() => showManagePropertiesDialog = true}>
									<Settings class="w-4 h-4 mr-1" />
									Manage
								</Button>
								<Button size="sm" onclick={openAddProperty}>
									<Plus class="w-4 h-4 mr-1" />
									Add
								</Button>
							</div>
						</Card.Header>
						<Card.Content>
							{#if poolLoading}
								<div class="text-center py-8 text-gray-500">
									<RefreshCw class="w-6 h-6 mx-auto mb-2 animate-spin" />
									<p>Loading AI-generated properties...</p>
								</div>
							{:else}
								<div class="grid md:grid-cols-2 gap-4 items-start">
									{#each properties as property}
										{@const propData = property as any}
										{#if propData._poolData}
											<!-- AI-generated property with images -->
											<PropertyCard 
												property={propData._poolData}
												onDetails={() => openPoolPropertyDetail(property)}
												onInvest={() => openBuyDialog(property)}
											/>
										{:else}
											<!-- Legacy property card -->
											<button type="button" class="border border-gray-200 rounded-lg overflow-hidden hover:border-blue-400 hover:shadow-lg transition cursor-pointer text-left w-full bg-white" onclick={() => openBuyDialog(property)}>
												<div class="h-32 bg-gradient-to-br from-gray-100 to-gray-200 relative">
													<div class="absolute inset-0 flex items-center justify-center">
														<Building class="w-12 h-12 text-gray-300" />
													</div>
													<div class="absolute top-2 left-2">
														<Badge variant="secondary" class="bg-white/90 text-xs">{property.property_type}</Badge>
													</div>
													<div class="absolute bottom-2 right-2">
														<Badge class="bg-green-600 text-white text-xs">{property.yield_percent}% yield</Badge>
													</div>
												</div>
												<div class="p-4">
													<div class="flex items-baseline gap-2 mb-1">
														<span class="text-xl font-bold text-gray-900">${property.valuation_aud.toLocaleString()}</span>
													</div>
													<div class="font-medium text-gray-900">{property.address}</div>
													<div class="text-sm text-gray-500 mb-2">{property.suburb}, {property.state}</div>
													<div class="flex items-center gap-4 text-sm text-gray-600 mb-2">
														<span>{property.bedrooms} bed</span>
														<span>{property.bathrooms} bath</span>
													</div>
													<div class="flex gap-2 pt-2 border-t">
														<Button size="sm" variant="outline" onclick={(e: Event) => { e.stopPropagation(); openPropertyDetail(property); }}>Details</Button>
														<Button size="sm">Invest</Button>
													</div>
												</div>
											</button>
										{/if}
									{/each}
								</div>
							{/if}
						</Card.Content>
					</Card.Root>

					<!-- Recent Transactions -->
					{#if transactions.length > 0}
						<Card.Root>
							<Card.Header>
								<Card.Title>Recent Transactions</Card.Title>
							</Card.Header>
							<Card.Content class="p-0">
								<div class="divide-y divide-gray-100">
									{#each transactions.slice(0, 5) as tx}
										<div class="px-6 py-4 flex items-center justify-between">
											<div class="flex items-center gap-3">
												<div class="w-8 h-8 rounded-full flex items-center justify-center bg-gray-100">
													{#if tx.tx_type === 'buy'}
														<ArrowDownRight class="w-4 h-4 text-green-600" />
													{:else if tx.tx_type === 'sell'}
														<ArrowUpRight class="w-4 h-4 text-blue-600" />
													{:else}
														<RefreshCw class="w-4 h-4 text-gray-600" />
													{/if}
												</div>
												<div>
													<div class="font-medium text-gray-900 capitalize">
														{tx.tx_type === 'reset' ? 'Account Reset' : `${tx.tx_type} ${tx.property_address?.split(',')[0] || ''}`}
													</div>
													<div class="text-sm text-gray-500">
														{new Date(tx.created_at).toLocaleDateString()}
													</div>
												</div>
											</div>
											<div class="text-right">
												<div class="font-medium text-gray-900">
													{tx.tx_type === 'buy' ? '-' : tx.tx_type === 'sell' ? '+' : ''}${tx.aud_amount.toLocaleString()}
												</div>
												{#if tx.token_amount > 0}
													<div class="text-sm text-gray-500">{tx.token_amount.toLocaleString()} tokens</div>
												{/if}
											</div>
										</div>
									{/each}
								</div>
							</Card.Content>
						</Card.Root>
					{/if}
					
					<!-- Investor Activity Log -->
					{#if investorTransactions.length > 0}
					<Card.Root>
						<Card.Header>
							<div class="flex items-center justify-between">
								<Card.Title class="flex items-center gap-2">
									<TrendingUp class="w-5 h-5 text-blue-600" />
									Activity Log
								</Card.Title>
								<Badge variant="outline">{investorTransactions.length} items</Badge>
							</div>
						</Card.Header>
						<Card.Content class="p-0">
							<div class="max-h-80 overflow-y-auto divide-y divide-gray-100">
								{#each investorTransactions.slice(0, 12) as tx}
									<div class="px-4 py-3 flex items-start gap-3">
										<div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 {getInvestorTransactionColor(tx.type, tx.status)}">
											<svelte:component this={getInvestorTransactionIcon(tx.type)} class="w-4 h-4" />
										</div>
										<div class="flex-1 min-w-0">
											<div class="font-medium text-gray-900 text-sm">{tx.description}</div>
											<div class="flex items-center gap-2 mt-0.5">
												<span class="text-xs text-gray-500">{tx.date}</span>
												{#if tx.tokens}
													<Badge variant="outline" class="text-xs">{tx.tokens.toFixed(2)} tokens</Badge>
												{/if}
											</div>
										</div>
										{#if tx.amount}
											<div class="text-sm font-medium {tx.amount < 0 ? 'text-red-600' : 'text-green-600'}">
												{tx.amount < 0 ? '-' : '+'}${Math.abs(tx.amount).toLocaleString()}
											</div>
										{/if}
									</div>
								{/each}
							</div>
							{#if investorTransactions.length > 12}
								<div class="px-4 py-3 border-t border-gray-100 text-center">
									<span class="text-sm text-gray-500">+ {investorTransactions.length - 12} more transactions</span>
								</div>
							{/if}
						</Card.Content>
					</Card.Root>
					{/if}
				</div>

				<!-- Sidebar -->
				<div class="space-y-6">
					<!-- Quick Stats -->
					<Card.Root>
						<Card.Header>
							<Card.Title>Quick Links</Card.Title>
						</Card.Header>
						<Card.Content class="space-y-3">
							<button 
								onclick={() => activeTab = 'leaderboard'}
								class="w-full flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition text-left"
							>
								<div class="flex items-center gap-3">
									<Trophy class="w-5 h-5 text-amber-500" />
									<span class="font-medium text-gray-900">Leaderboard</span>
								</div>
								<ChevronRight class="w-4 h-4 text-gray-400" />
							</button>
							<button 
								onclick={() => activeTab = 'governance'}
								class="w-full flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition text-left"
							>
								<div class="flex items-center gap-3">
									<Vote class="w-5 h-5 text-blue-600" />
									<div>
										<span class="font-medium text-gray-900">Governance</span>
										<span class="text-xs text-blue-600 ml-2">{proposals.length} active</span>
									</div>
								</div>
								<ChevronRight class="w-4 h-4 text-gray-400" />
							</button>
							<button 
								onclick={() => activeTab = 'feedback'}
								class="w-full flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition text-left"
							>
								<div class="flex items-center gap-3">
									<MessageSquare class="w-5 h-5 text-purple-600" />
									<div>
										<span class="font-medium text-gray-900">Feedback</span>
										<span class="text-xs text-purple-600 ml-2">{feedbackItems.length} items</span>
									</div>
								</div>
								<ChevronRight class="w-4 h-4 text-gray-400" />
							</button>
						</Card.Content>
					</Card.Root>

					<!-- Convert CTA -->
					<Card.Root class="border-blue-200 bg-blue-50">
						<Card.Content class="pt-6">
							<h3 class="font-medium text-gray-900 mb-2">Ready for Real Investment?</h3>
							<p class="text-sm text-gray-600 mb-4">
								Convert to a live account and start building real wealth.
							</p>
							<Button class="w-full">
								Upgrade to Live Account
								<ChevronRight class="w-4 h-4 ml-2" />
							</Button>
						</Card.Content>
					</Card.Root>
				</div>
			</div>
			
			{:else if activeRole === 'renter'}
			<!-- RENTER SIMULATION -->
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
				<div class="lg:col-span-2 space-y-6">
					<!-- Current Rental -->
					<Card.Root>
						<Card.Header>
							<Card.Title class="flex items-center gap-2">
								<Building class="w-5 h-5 text-blue-600" />
								Your Rental
							</Card.Title>
						</Card.Header>
						<Card.Content>
							{#if !renterProperty}
								<div class="py-4">
									<div class="text-center mb-4">
										<Home class="w-10 h-10 mx-auto mb-2 text-gray-300" />
										<p class="text-gray-500">Select a property to rent</p>
									</div>
									<div class="grid gap-4">
										{#each properties.slice(0, 4) as property}
											{@const propAny = property as any}
											{@const imgSrc = propAny._poolData?.images?.isometric || propAny.image}
											<button 
												onclick={() => renterSelectProperty(property)}
												class="flex gap-4 p-3 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition text-left group"
											>
												<!-- Property Thumbnail -->
												{#if imgSrc}
													<div class="w-24 h-20 flex-shrink-0 rounded-md overflow-hidden bg-gray-100">
														<img 
															src={imgSrc.startsWith('data:') ? imgSrc : `data:image/png;base64,${imgSrc}`}
															alt={property.address}
															class="w-full h-full object-cover group-hover:scale-105 transition-transform"
														/>
													</div>
												{:else}
													<div class="w-24 h-20 flex-shrink-0 rounded-md bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
														<Home class="w-8 h-8 text-gray-300" />
													</div>
												{/if}
												
												<!-- Property Details -->
												<div class="flex-1 min-w-0">
													<div class="font-medium text-gray-900 truncate">{property.address}</div>
													<div class="text-sm text-gray-500">{property.suburb}</div>
													<div class="flex items-center gap-3 mt-1 text-xs text-gray-500">
														<span class="flex items-center gap-1">
															<BedDouble class="w-3 h-3" />
															{property.bedrooms}
														</span>
														<span class="flex items-center gap-1">
															<Bath class="w-3 h-3" />
															{property.bathrooms}
														</span>
												{#if property.car_spaces}
													<span class="flex items-center gap-1">
														<Car class="w-3 h-3" />
														{property.car_spaces}
													</span>
												{/if}
											</div>
											<div class="text-sm font-semibold text-blue-600 mt-1">
												${Math.round((property.valuation_aud || 800000) * 0.004).toLocaleString()}/month
													</div>
												</div>
											</button>
										{/each}
									</div>
								</div>
							{:else}
								{@const renterImgSrc = renterProperty._poolData?.images?.isometric || renterProperty.image}
								<div class="space-y-6">
									<!-- Current Property with Image -->
									<div class="bg-blue-50 rounded-lg border border-blue-200 overflow-hidden">
										<!-- Property Image -->
										{#if renterImgSrc}
											<div class="relative h-40 bg-gradient-to-br from-blue-100 to-blue-200">
												<img 
													src={renterImgSrc.startsWith?.('data:') ? renterImgSrc : `data:image/png;base64,${renterImgSrc}`}
													alt={renterProperty.address}
													class="w-full h-full object-cover"
												/>
												<div class="absolute top-2 right-2">
													<Badge variant="outline" class="bg-white/90 text-blue-700 border-blue-200">
														{renterLeaseEnd > 0 ? `${renterLeaseEnd} months left` : 'Lease Expired'}
													</Badge>
												</div>
											</div>
										{:else}
											<div class="h-32 bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
												<Home class="w-12 h-12 text-blue-300" />
											</div>
										{/if}
										
										<div class="p-4">
											<div class="flex items-center justify-between mb-1">
												<span class="text-sm font-medium text-blue-700">Your Rental Property</span>
											</div>
											<div class="text-lg font-bold text-gray-900">{renterProperty.address}</div>
											<div class="text-sm text-gray-600 mb-3">{renterProperty.suburb} • {renterProperty.postcode || ''}</div>
											
											<!-- Property Attributes -->
											<div class="flex flex-wrap gap-3 mb-3 text-sm text-gray-600">
												<span class="flex items-center gap-1">
													<BedDouble class="w-4 h-4" />
													{renterProperty.bedrooms} bed
												</span>
												<span class="flex items-center gap-1">
													<Bath class="w-4 h-4" />
													{renterProperty.bathrooms} bath
												</span>
												{#if renterProperty.car_spaces}
													<span class="flex items-center gap-1">
														<Car class="w-4 h-4" />
														{renterProperty.car_spaces} car
													</span>
												{/if}
												{#if renterProperty.land_size_sqm}
													<span class="flex items-center gap-1">
														<Ruler class="w-4 h-4" />
														{renterProperty.land_size_sqm}m²
													</span>
												{/if}
											</div>
											
											<!-- Property Actions -->
											<div class="flex gap-2 pt-3 border-t border-blue-200">
												<Button variant="outline" size="sm" class="text-xs" onclick={() => showRenterSwapDialog = true}>
													<RefreshCw class="w-3 h-3 mr-1" />
													Change Property
												</Button>
												<Button variant="outline" size="sm" class="text-xs text-red-600 border-red-200 hover:bg-red-50" onclick={renterEndLease}>
													End Lease
												</Button>
											</div>
										</div>
									</div>
									
									<!-- Rent Stats -->
									<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
										<div class="p-4 bg-gray-50 rounded-lg text-center">
											<div class="text-sm text-gray-500 mb-1">Weekly Rent</div>
											<div class="text-xl font-bold text-gray-900">${renterWeeklyRent.toLocaleString()}</div>
										</div>
										<div class="p-4 bg-gray-50 rounded-lg text-center">
											<div class="text-sm text-gray-500 mb-1">Weeks Rented</div>
											<div class="text-xl font-bold text-gray-900">{renterWeeksRented}</div>
										</div>
										<div class="p-4 bg-gray-50 rounded-lg text-center">
											<div class="text-sm text-gray-500 mb-1">Months</div>
											<div class="text-xl font-bold text-gray-900">{renterMonthsRented}</div>
										</div>
										<div class="p-4 bg-gray-50 rounded-lg text-center">
											<div class="text-sm text-gray-500 mb-1">Total Paid</div>
											<div class="text-xl font-bold text-red-600">${renterTotalPaid.toLocaleString()}</div>
										</div>
									</div>
									
									<!-- Time Simulation -->
									<div class="flex flex-wrap gap-2">
										<Button variant="outline" size="sm" onclick={renterSimulateWeek}>+1 Week</Button>
										<Button variant="outline" size="sm" onclick={simulateNetworkMonth}>+1 Month</Button>
										<Button variant="outline" size="sm" onclick={() => { for(let i=0; i<12; i++) simulateNetworkMonth(); }}>+1 Year</Button>
									</div>
									<p class="text-xs text-gray-500 mt-2">Simulates weekly rent payments, inspections, and lease milestones</p>
								</div>
							{/if}
						</Card.Content>
					</Card.Root>
					
					<!-- Maintenance Requests -->
					{#if renterProperty}
					<Card.Root>
						<Card.Header>
							<Card.Title class="flex items-center gap-2">
								<Wrench class="w-5 h-5 text-orange-600" />
								Maintenance Requests
							</Card.Title>
						</Card.Header>
						<Card.Content>
							<div class="space-y-3 mb-4">
								{#each renterMaintenanceRequests as request}
									<div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
										<div>
											<div class="font-medium text-gray-900">{request.issue}</div>
											<div class="text-sm text-gray-500">{request.submitted}</div>
										</div>
										<Badge variant="outline" class="{request.status === 'pending' ? 'bg-amber-100 text-amber-700 border-amber-200' : 'bg-green-100 text-green-700 border-green-200'}">
											{request.status}
										</Badge>
									</div>
								{/each}
							</div>
							<div class="flex gap-2">
								<Input placeholder="Describe the issue..." id="maintenance-issue" />
								<Button variant="outline" onclick={() => {
									const input = document.getElementById('maintenance-issue') as HTMLInputElement;
									if (input) {
										renterSubmitMaintenance(input.value);
										input.value = '';
									}
								}}>
									Submit
								</Button>
							</div>
						</Card.Content>
					</Card.Root>
					
					<!-- Transaction History -->
					<Card.Root>
						<Card.Header>
							<div class="flex items-center justify-between">
								<Card.Title class="flex items-center gap-2">
									<FileText class="w-5 h-5 text-purple-600" />
									Rental Activity
								</Card.Title>
								<Badge variant="outline">{renterTransactions.length} items</Badge>
							</div>
						</Card.Header>
						<Card.Content class="p-0">
							<div class="max-h-96 overflow-y-auto divide-y divide-gray-100">
								{#each renterTransactions.slice(0, 15) as tx}
									<div class="px-4 py-3 flex items-start gap-3">
										<div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 {getRenterTransactionColor(tx.type, tx.status)}">
											<svelte:component this={getRenterTransactionIcon(tx.type)} class="w-4 h-4" />
										</div>
										<div class="flex-1 min-w-0">
											<div class="font-medium text-gray-900 text-sm">{tx.description}</div>
											<div class="flex items-center gap-2 mt-0.5">
												<span class="text-xs text-gray-500">{tx.date}</span>
												{#if tx.status === 'pending'}
													<Badge variant="outline" class="text-xs bg-amber-50 text-amber-700 border-amber-200">Pending</Badge>
												{:else if tx.status === 'upcoming'}
													<Badge variant="outline" class="text-xs bg-blue-50 text-blue-700 border-blue-200">Upcoming</Badge>
												{/if}
											</div>
										</div>
										{#if tx.amount}
											<div class="text-sm font-medium {tx.amount < 0 ? 'text-red-600' : 'text-green-600'}">
												{tx.amount < 0 ? '-' : '+'}${Math.abs(tx.amount).toLocaleString()}
											</div>
										{/if}
									</div>
								{/each}
							</div>
							{#if renterTransactions.length > 15}
								<div class="px-4 py-3 border-t border-gray-100 text-center">
									<span class="text-sm text-gray-500">+ {renterTransactions.length - 15} more transactions</span>
								</div>
							{/if}
						</Card.Content>
					</Card.Root>
					{/if}
					
					<!-- Equity Comparison -->
					{#if renterMonthsRented >= 3}
					<Card.Root class="border-amber-200 bg-amber-50">
						<Card.Content class="pt-6">
							<div class="flex items-start gap-4">
								<div class="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
									<AlertCircle class="w-5 h-5 text-amber-600" />
								</div>
								<div class="flex-1">
									<h3 class="font-medium text-gray-900 mb-1">You're Missing Out on Equity</h3>
									<p class="text-sm text-gray-600 mb-3">
										If you were on OSF's Rent-to-Own program, you would have built 
										<span class="font-bold text-green-600">${getRenterEquityLost().toLocaleString()}</span> in equity from your rent payments.
									</p>
									<Button class="bg-green-600 hover:bg-green-700" onclick={renterUpgradeToTenant}>
										<Key class="w-4 h-4 mr-2" />
										Switch to Rent-to-Own
									</Button>
								</div>
							</div>
						</Card.Content>
					</Card.Root>
					{/if}
				</div>
				
				<!-- Sidebar -->
				<div class="space-y-6">
					<Card.Root>
						<Card.Header>
							<Card.Title>Rental Summary</Card.Title>
						</Card.Header>
						<Card.Content class="space-y-4">
							<div class="flex justify-between">
								<span class="text-gray-600">Monthly Rent</span>
								<span class="font-medium">${renterMonthlyRent.toLocaleString()}</span>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-600">Total Paid</span>
								<span class="font-medium text-red-600">-${renterTotalPaid.toLocaleString()}</span>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-600">Equity Built</span>
								<span class="font-medium text-gray-400">$0</span>
							</div>
							<hr />
							<div class="flex justify-between">
								<span class="text-gray-600 font-medium">Net Position</span>
								<span class="font-bold text-red-600">-${renterTotalPaid.toLocaleString()}</span>
							</div>
						</Card.Content>
					</Card.Root>
					
					<Card.Root>
						<Card.Header>
							<Card.Title>Lease Details</Card.Title>
						</Card.Header>
						<Card.Content class="space-y-3 text-sm">
							<div class="flex justify-between">
								<span class="text-gray-600">Lease Type</span>
								<span class="font-medium">12 Month Fixed</span>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-600">Weekly Rent</span>
								<span class="font-medium">${renterWeeklyRent.toLocaleString()}</span>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-600">Remaining</span>
								<span class="font-medium {renterLeaseEnd <= 2 ? 'text-amber-600' : ''}">{renterLeaseEnd} months</span>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-600">Bond Held</span>
								<span class="font-medium">${renterBondAmount.toLocaleString()}</span>
							</div>
							<hr class="my-2" />
							<div class="flex justify-between">
								<span class="text-gray-600">Weeks Rented</span>
								<span class="font-medium">{renterWeeksRented}</span>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-600">Next Inspection</span>
								<span class="font-medium {renterNextInspection <= 1 ? 'text-blue-600' : ''}">{renterNextInspection} months</span>
							</div>
							{#if renterLeaseStart}
							<div class="flex justify-between">
								<span class="text-gray-600">Lease Start</span>
								<span class="font-medium">{renterLeaseStart}</span>
							</div>
							{/if}
						</Card.Content>
					</Card.Root>
					
					<Card.Root class="border-green-200 bg-green-50">
						<Card.Content class="pt-6 text-center">
							<Key class="w-8 h-8 text-green-600 mx-auto mb-2" />
							<h3 class="font-medium text-gray-900 mb-1">Ready to Own?</h3>
							<p class="text-sm text-gray-600 mb-3">Turn your rent into ownership with Rent-to-Own</p>
							<Button variant="outline" class="w-full border-green-600 text-green-700 hover:bg-green-100" onclick={renterUpgradeToTenant}>
								Learn About Rent-to-Own
							</Button>
						</Card.Content>
					</Card.Root>
				</div>
			</div>
			
			{:else if activeRole === 'tenant'}
			<!-- TENANT SIMULATION -->
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
				<!-- Main Content -->
				<div class="lg:col-span-2 space-y-6">
					<!-- Rent-to-Own Progress -->
					<Card.Root>
						<Card.Header>
							<Card.Title class="flex items-center gap-2">
								<Key class="w-5 h-5 text-green-600" />
								Your Rent-to-Own Journey
							</Card.Title>
						</Card.Header>
						<Card.Content>
							{#if !tenantTargetProperty}
								<div class="py-4">
									<div class="text-center mb-4">
										<Home class="w-10 h-10 mx-auto mb-2 text-gray-300" />
										<p class="text-gray-500">Select a property to start your rent-to-own journey</p>
									</div>
									<div class="grid gap-4">
										{#each properties.slice(0, 4) as property}
											{@const tenantPropAny = property as any}
											{@const tenantImgSrc = tenantPropAny._poolData?.images?.isometric || tenantPropAny.image}
											<button 
												onclick={() => tenantSelectProperty(property)}
												class="flex gap-4 p-3 border border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition text-left group"
											>
												<!-- Property Thumbnail -->
												{#if tenantImgSrc}
													<div class="w-24 h-20 flex-shrink-0 rounded-md overflow-hidden bg-gray-100">
														<img 
															src={tenantImgSrc.startsWith?.('data:') ? tenantImgSrc : `data:image/png;base64,${tenantImgSrc}`}
															alt={property.address}
															class="w-full h-full object-cover group-hover:scale-105 transition-transform"
														/>
													</div>
												{:else}
													<div class="w-24 h-20 flex-shrink-0 rounded-md bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
														<Home class="w-8 h-8 text-gray-300" />
													</div>
												{/if}
												
												<!-- Property Details -->
												<div class="flex-1 min-w-0">
													<div class="font-medium text-gray-900 truncate">{property.address}</div>
													<div class="text-sm text-gray-500">{property.suburb}</div>
													<div class="flex items-center gap-3 mt-1 text-xs text-gray-500">
														<span class="flex items-center gap-1">
															<BedDouble class="w-3 h-3" />
															{property.bedrooms}
														</span>
														<span class="flex items-center gap-1">
															<Bath class="w-3 h-3" />
															{property.bathrooms}
														</span>
														{#if property.car_spaces}
															<span class="flex items-center gap-1">
																<Car class="w-3 h-3" />
																{property.car_spaces}
															</span>
														{/if}
													</div>
													<div class="flex items-center justify-between mt-1">
														<span class="text-xs text-gray-500">${property.valuation_aud.toLocaleString()}</span>
														<span class="text-sm font-semibold text-green-600">
															${Math.round(property.valuation_aud * 0.004).toLocaleString()}/month
														</span>
													</div>
												</div>
											</button>
										{/each}
									</div>
								</div>
							{:else}
								{@const targetImgSrc = tenantTargetProperty._poolData?.images?.isometric || tenantTargetProperty.image}
								<div class="space-y-6">
									<!-- Current Property with Image -->
									<div class="bg-green-50 rounded-lg border border-green-200 overflow-hidden">
										{#if targetImgSrc}
											<div class="relative h-40 bg-gradient-to-br from-green-100 to-green-200">
												<img 
													src={targetImgSrc.startsWith?.('data:') ? targetImgSrc : `data:image/png;base64,${targetImgSrc}`}
													alt={tenantTargetProperty.address}
													class="w-full h-full object-cover"
												/>
												<div class="absolute top-2 right-2">
													<Badge variant="outline" class="bg-white/90 text-green-700 border-green-200">
														Rent-to-Own
													</Badge>
												</div>
											</div>
										{/if}
										<div class="p-4">
											<div class="flex items-center justify-between mb-1">
												<span class="text-sm font-medium text-green-700">Your Target Property</span>
												<Badge variant="outline" class="bg-green-100 text-green-700 border-green-200">
													Active
												</Badge>
											</div>
											<div class="text-lg font-bold text-gray-900">{tenantTargetProperty.address}</div>
											<div class="text-sm text-gray-600 mb-2">{tenantTargetProperty.suburb} • {tenantTargetProperty.postcode || ''}</div>
											
											<!-- Property Attributes -->
											<div class="flex flex-wrap gap-3 text-sm text-gray-600">
												<span class="flex items-center gap-1">
													<BedDouble class="w-4 h-4" />
													{tenantTargetProperty.bedrooms} bed
												</span>
												<span class="flex items-center gap-1">
													<Bath class="w-4 h-4" />
													{tenantTargetProperty.bathrooms} bath
												</span>
												{#if tenantTargetProperty.car_spaces}
													<span class="flex items-center gap-1">
														<Car class="w-4 h-4" />
														{tenantTargetProperty.car_spaces} car
													</span>
												{/if}
												<span class="ml-auto font-semibold text-green-700">
													${tenantTargetProperty.valuation_aud.toLocaleString()}
												</span>
											</div>
										</div>
									</div>
									
									<!-- Progress Stats -->
									<div class="grid grid-cols-2 gap-4">
										<div class="p-4 bg-gray-50 rounded-lg">
											<div class="text-sm text-gray-500 mb-1">Monthly Rent</div>
											<div class="text-2xl font-bold text-gray-900">${tenantRentAmount.toLocaleString()}</div>
											<div class="text-xs text-green-600">20% goes to equity</div>
										</div>
										<div class="p-4 bg-gray-50 rounded-lg">
											<div class="text-sm text-gray-500 mb-1">Months Rented</div>
											<div class="text-2xl font-bold text-gray-900">{tenantMonthsRented}</div>
											<div class="text-xs text-gray-500">{Math.floor(tenantMonthsRented / 12)} years, {tenantMonthsRented % 12} months</div>
										</div>
									</div>
									
									<!-- Equity Progress Bar -->
									<div>
										<div class="flex justify-between text-sm mb-2">
											<span class="text-gray-600">Equity Accumulated</span>
											<span class="font-medium text-green-600">{tenantEquityPercent.toFixed(2)}%</span>
										</div>
										<div class="h-4 bg-gray-200 rounded-full overflow-hidden">
											<div 
												class="h-full bg-gradient-to-r from-green-400 to-green-600 rounded-full transition-all duration-500"
												style="width: {Math.min(tenantEquityPercent, 100)}%"
											></div>
										</div>
										<div class="flex justify-between text-xs text-gray-500 mt-1">
											<span>$0</span>
											<span class="text-green-600 font-medium">${getTenantEquityValue().toLocaleString()}</span>
											<span>${tenantTargetProperty.valuation_aud.toLocaleString()}</span>
										</div>
									</div>
									
									<!-- Time Simulation -->
									<div class="flex gap-2">
										<Button variant="outline" onclick={simulateNetworkMonth}>+1 Month</Button>
										<Button variant="outline" onclick={() => { for(let i=0; i<12; i++) simulateNetworkMonth(); }}>+1 Year</Button>
										<Button variant="outline" onclick={() => { for(let i=0; i<60; i++) simulateNetworkMonth(); }}>+5 Years</Button>
									</div>
								</div>
							{/if}
						</Card.Content>
					</Card.Root>
					
					<!-- Comparison Card -->
					{#if tenantMonthsRented > 0}
					<Card.Root>
						<Card.Header>
							<Card.Title>Rent-to-Own vs Traditional Renting</Card.Title>
						</Card.Header>
						<Card.Content>
							<div class="grid grid-cols-2 gap-6">
								<div class="p-4 bg-green-50 rounded-lg border border-green-200">
									<div class="text-sm text-green-700 mb-2">With OSF Rent-to-Own</div>
									<div class="text-2xl font-bold text-green-700">${getTenantEquityValue().toLocaleString()}</div>
									<div class="text-sm text-green-600">Equity built</div>
								</div>
								<div class="p-4 bg-gray-100 rounded-lg">
									<div class="text-sm text-gray-600 mb-2">Traditional Renting</div>
									<div class="text-2xl font-bold text-gray-400">$0</div>
									<div class="text-sm text-gray-500">No equity accumulated</div>
								</div>
							</div>
							<div class="mt-4 p-3 bg-blue-50 rounded-lg text-sm text-blue-700">
								<strong>Projected time to full ownership:</strong> {getTenantTimeToOwnership()}
							</div>
						</Card.Content>
					</Card.Root>
					{/if}
					
					<!-- Tenant Activity Log -->
					{#if tenantTransactions.length > 0}
					<Card.Root>
						<Card.Header>
							<div class="flex items-center justify-between">
								<Card.Title class="flex items-center gap-2">
									<FileText class="w-5 h-5 text-green-600" />
									Payment History
								</Card.Title>
								<Badge variant="outline">{tenantTransactions.length} items</Badge>
							</div>
						</Card.Header>
						<Card.Content class="p-0">
							<div class="max-h-80 overflow-y-auto divide-y divide-gray-100">
								{#each tenantTransactions.slice(0, 12) as tx}
									<div class="px-4 py-3 flex items-start gap-3">
										<div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 {getTenantTransactionColor(tx.type, tx.status)}">
											<svelte:component this={getTenantTransactionIcon(tx.type)} class="w-4 h-4" />
										</div>
										<div class="flex-1 min-w-0">
											<div class="font-medium text-gray-900 text-sm">{tx.description}</div>
											<div class="flex items-center gap-2 mt-0.5">
												<span class="text-xs text-gray-500">{tx.date}</span>
												{#if tx.status === 'pending'}
													<Badge variant="outline" class="text-xs bg-amber-50 text-amber-700 border-amber-200">Pending</Badge>
												{/if}
											</div>
										</div>
										{#if tx.amount}
											<div class="text-sm font-medium {tx.amount < 0 ? 'text-red-600' : 'text-green-600'}">
												{tx.amount < 0 ? '-' : '+'}${Math.abs(tx.amount).toLocaleString()}
											</div>
										{/if}
									</div>
								{/each}
							</div>
							{#if tenantTransactions.length > 12}
								<div class="px-4 py-3 border-t border-gray-100 text-center">
									<span class="text-sm text-gray-500">+ {tenantTransactions.length - 12} more transactions</span>
								</div>
							{/if}
						</Card.Content>
					</Card.Root>
					{/if}
				</div>
				
				<!-- Sidebar -->
				<div class="space-y-6">
					<Card.Root>
						<Card.Header>
							<Card.Title>Journey Summary</Card.Title>
						</Card.Header>
						<Card.Content class="space-y-4">
							<div class="flex justify-between">
								<span class="text-gray-600">Total Rent Paid</span>
								<span class="font-medium">${(tenantRentAmount * tenantMonthsRented).toLocaleString()}</span>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-600">Equity Value</span>
								<span class="font-medium text-green-600">${getTenantEquityValue().toLocaleString()}</span>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-600">Equity %</span>
								<span class="font-medium">{tenantEquityPercent.toFixed(2)}%</span>
							</div>
							<hr />
							<div class="flex justify-between">
								<span class="text-gray-600">Effective Cost</span>
								<span class="font-medium">${((tenantRentAmount * tenantMonthsRented) - getTenantEquityValue()).toLocaleString()}</span>
							</div>
						</Card.Content>
					</Card.Root>
					
					<Card.Root class="border-green-200 bg-green-50">
						<Card.Content class="pt-6 text-center">
							<CheckCircle class="w-8 h-8 text-green-600 mx-auto mb-2" />
							<p class="text-sm text-gray-700">Every rent payment builds your future</p>
						</Card.Content>
					</Card.Root>
				</div>
			</div>
			
			{:else if activeRole === 'homeowner'}
			<!-- HOMEOWNER SIMULATION -->
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
				<div class="lg:col-span-2 space-y-6">
					<!-- Property Overview -->
					<Card.Root>
						<Card.Header>
							<Card.Title class="flex items-center gap-2">
								<Home class="w-5 h-5 text-blue-600" />
								Your Property
							</Card.Title>
						</Card.Header>
						<Card.Content>
							{#if !homeownerProperty}
								<!-- Property Selection -->
								<div class="py-4">
									<div class="text-center mb-4">
										<Home class="w-10 h-10 mx-auto mb-2 text-gray-300" />
										<p class="text-gray-500">Select your property to manage</p>
									</div>
									<div class="grid gap-4">
										{#each properties.slice(0, 3) as property}
											{@const homePropAny = property as any}
											{@const homeImgSrc = homePropAny._poolData?.images?.isometric || homePropAny.image}
											<button 
												onclick={() => homeownerSelectProperty(property)}
												class="flex gap-4 p-3 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition text-left group"
											>
												{#if homeImgSrc}
													<div class="w-24 h-20 flex-shrink-0 rounded-md overflow-hidden bg-gray-100">
														<img 
															src={homeImgSrc.startsWith?.('data:') ? homeImgSrc : `data:image/png;base64,${homeImgSrc}`}
															alt={property.address}
															class="w-full h-full object-cover group-hover:scale-105 transition-transform"
														/>
													</div>
												{:else}
													<div class="w-24 h-20 flex-shrink-0 rounded-md bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
														<Home class="w-8 h-8 text-gray-300" />
													</div>
												{/if}
												<div class="flex-1 min-w-0">
													<div class="font-medium text-gray-900 truncate">{property.address}</div>
													<div class="text-sm text-gray-500">{property.suburb}</div>
													<div class="flex items-center gap-3 mt-1 text-xs text-gray-500">
														<span class="flex items-center gap-1"><BedDouble class="w-3 h-3" />{property.bedrooms}</span>
														<span class="flex items-center gap-1"><Bath class="w-3 h-3" />{property.bathrooms}</span>
														{#if property.car_spaces}<span class="flex items-center gap-1"><Car class="w-3 h-3" />{property.car_spaces}</span>{/if}
													</div>
													<div class="text-sm font-semibold text-blue-600 mt-1">${property.valuation_aud.toLocaleString()}</div>
												</div>
											</button>
										{/each}
									</div>
								</div>
							{:else}
								{@const ownerImgSrc = homeownerProperty._poolData?.images?.isometric || homeownerProperty.image}
								<!-- Property Display with Image -->
								<div class="bg-blue-50 rounded-lg border border-blue-200 overflow-hidden mb-6">
									{#if ownerImgSrc}
										<div class="relative h-36 bg-gradient-to-br from-blue-100 to-blue-200">
											<img 
												src={ownerImgSrc.startsWith?.('data:') ? ownerImgSrc : `data:image/png;base64,${ownerImgSrc}`}
												alt={homeownerProperty.address}
												class="w-full h-full object-cover"
											/>
											{#if homeownerPropertyListed}
												<div class="absolute top-2 right-2">
													<Badge variant="outline" class="bg-green-500 text-white border-green-500">
														Listed on OSF
													</Badge>
												</div>
											{/if}
										</div>
									{/if}
									<div class="p-3">
										<div class="font-bold text-gray-900">{homeownerProperty.address}</div>
										<div class="text-sm text-gray-600 mb-2">{homeownerProperty.suburb} • {homeownerProperty.postcode || ''}</div>
										<div class="flex flex-wrap gap-3 text-xs text-gray-600">
											<span class="flex items-center gap-1"><BedDouble class="w-3 h-3" />{homeownerProperty.bedrooms} bed</span>
											<span class="flex items-center gap-1"><Bath class="w-3 h-3" />{homeownerProperty.bathrooms} bath</span>
											{#if homeownerProperty.car_spaces}<span class="flex items-center gap-1"><Car class="w-3 h-3" />{homeownerProperty.car_spaces} car</span>{/if}
											{#if homeownerProperty.land_size_sqm}<span class="flex items-center gap-1"><Ruler class="w-3 h-3" />{homeownerProperty.land_size_sqm}m²</span>{/if}
										</div>
									</div>
								</div>
								
								<div class="grid grid-cols-2 gap-4 mb-6">
									<div class="p-4 bg-gray-50 rounded-lg">
										<div class="text-sm text-gray-500 mb-1">Property Value</div>
										<div class="text-2xl font-bold text-gray-900">${Math.round(homeownerPropertyValue).toLocaleString()}</div>
									</div>
									<div class="p-4 bg-gray-50 rounded-lg">
										<div class="text-sm text-gray-500 mb-1">Mortgage Balance</div>
										<div class="text-2xl font-bold text-gray-900">${Math.round(homeownerMortgageBalance).toLocaleString()}</div>
									</div>
								</div>
								
								<!-- Equity Bar -->
								<div class="mb-6">
									<div class="flex justify-between text-sm mb-2">
										<span class="text-gray-600">Your Equity</span>
										<span class="font-medium text-blue-600">
											${Math.round(homeownerPropertyValue - homeownerMortgageBalance).toLocaleString()} 
											({((homeownerPropertyValue - homeownerMortgageBalance) / homeownerPropertyValue * 100).toFixed(1)}%)
										</span>
									</div>
									<div class="h-4 bg-gray-200 rounded-full overflow-hidden">
										<div 
											class="h-full bg-gradient-to-r from-blue-400 to-blue-600 rounded-full"
											style="width: {((homeownerPropertyValue - homeownerMortgageBalance) / homeownerPropertyValue * 100)}%"
										></div>
									</div>
								</div>
								
								<!-- Time Simulation -->
								<div class="flex gap-2 mb-4">
									<Button variant="outline" onclick={simulateNetworkMonth}>+1 Month</Button>
									<Button variant="outline" onclick={() => { for(let i=0; i<12; i++) simulateNetworkMonth(); }}>+1 Year</Button>
									<Button variant="outline" onclick={() => { for(let i=0; i<60; i++) simulateNetworkMonth(); }}>+5 Years</Button>
								</div>
								<p class="text-xs text-gray-500">Advances network simulation (all roles progress together)</p>
							{/if}
						</Card.Content>
					</Card.Root>
					
					<!-- List on Network (NEW) -->
					{#if homeownerProperty && !homeownerPropertyListed}
					<Card.Root class="border-dashed border-2 border-blue-300 bg-blue-50/50">
						<Card.Header>
							<Card.Title class="flex items-center gap-2">
								<Building class="w-5 h-5 text-blue-600" />
								List on OSF Network
							</Card.Title>
						</Card.Header>
						<Card.Content>
							<p class="text-gray-600 mb-4">
								List your property on the OSF network to enable tokenized equity access, 
								rent collection, and connect with investors.
							</p>
							<div class="grid grid-cols-3 gap-3 mb-4 text-center text-sm">
								<div class="p-3 bg-white rounded-lg border">
									<div class="font-bold text-blue-600">Access Equity</div>
									<div class="text-xs text-gray-500">0% interest loans</div>
								</div>
								<div class="p-3 bg-white rounded-lg border">
									<div class="font-bold text-purple-600">Rent Income</div>
									<div class="text-xs text-gray-500">Managed tenants</div>
								</div>
								<div class="p-3 bg-white rounded-lg border">
									<div class="font-bold text-green-600">Token Sale</div>
									<div class="text-xs text-gray-500">Sell partial equity</div>
								</div>
							</div>
							<Button class="w-full bg-blue-600 hover:bg-blue-700" onclick={homeownerListOnNetwork}>
								<Building class="w-4 h-4 mr-2" />
								List Property on Network
							</Button>
						</Card.Content>
					</Card.Root>
					{/if}
					
					<!-- Access Equity (only when listed) -->
					{#if homeownerPropertyListed}
					<Card.Root>
						<Card.Header>
							<Card.Title class="flex items-center gap-2">
								<DollarSign class="w-5 h-5 text-green-600" />
								Access Your Equity
							</Card.Title>
						</Card.Header>
						<Card.Content>
							<div class="p-4 bg-green-50 rounded-lg border border-green-200 mb-4">
								<div class="text-sm text-green-700 mb-1">Available Equity (80% LVR)</div>
								<div class="text-2xl font-bold text-green-700">${Math.max(0, Math.round(homeownerEquityAvailable)).toLocaleString()}</div>
							</div>
							
							{#if homeownerEquityAvailable > 0}
								<div class="grid grid-cols-3 gap-2">
									<Button variant="outline" onclick={() => homeownerAccessEquity(10000)}>
										Access $10k
									</Button>
									<Button variant="outline" onclick={() => homeownerAccessEquity(25000)}>
										Access $25k
									</Button>
									<Button variant="outline" onclick={() => homeownerAccessEquity(50000)}>
										Access $50k
									</Button>
								</div>
								<p class="text-xs text-gray-500 mt-3">
									Simulate equity access. Explore how the 0% interest model could work.
								</p>
							{:else}
								<p class="text-sm text-gray-500">
									Build more equity or wait for property appreciation to access funds.
								</p>
							{/if}
							
							{#if homeownerEquityAccessAmount > 0}
								<div class="mt-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
									<div class="flex items-center justify-between">
										<div>
											<span class="text-purple-700 text-sm">Total equity accessed: </span>
											<span class="font-bold text-purple-900">${homeownerEquityAccessAmount.toLocaleString()}</span>
										</div>
										<button 
											onclick={() => activeRole = 'investor'}
											class="text-sm text-purple-600 hover:text-purple-800 underline flex items-center gap-1"
										>
											<TrendingUp class="w-4 h-4" />
											View as Investor
										</button>
									</div>
									<p class="text-xs text-purple-600 mt-1">You received OSF tokens for your equity. Switch to Investor view to see your holdings.</p>
								</div>
							{/if}
						</Card.Content>
					</Card.Root>
					{/if}
					
					<!-- Rental Income (only when listed) -->
					{#if homeownerPropertyListed}
					<Card.Root>
						<Card.Header>
							<Card.Title class="flex items-center gap-2">
								<PiggyBank class="w-5 h-5 text-purple-600" />
								Rental Income
							</Card.Title>
						</Card.Header>
						<Card.Content>
							{#if homeownerIsRenting}
								<div class="p-4 bg-purple-50 rounded-lg border border-purple-200 mb-4">
									<div class="flex justify-between items-center">
										<div>
											<div class="text-sm text-purple-700 mb-1">Monthly Rental Income</div>
											<div class="text-2xl font-bold text-purple-700">${homeownerRentalIncome.toLocaleString()}</div>
										</div>
										<Badge variant="outline" class="bg-purple-100 text-purple-700 border-purple-200">Active</Badge>
									</div>
								</div>
								<Button variant="outline" class="w-full" onclick={homeownerStopRenting}>
									Stop Renting Property
								</Button>
							{:else}
								<p class="text-gray-600 mb-4">Rent out your property and earn passive income while OSF manages tenants.</p>
								<Button class="w-full bg-purple-600 hover:bg-purple-700" onclick={homeownerStartRenting}>
									<Key class="w-4 h-4 mr-2" />
									List Property for Rent
								</Button>
							{/if}
						</Card.Content>
					</Card.Root>
					{/if}
					
					<!-- Homeowner Activity Log -->
					{#if homeownerTransactions.length > 0}
					<Card.Root>
						<Card.Header>
							<div class="flex items-center justify-between">
								<Card.Title class="flex items-center gap-2">
									<FileText class="w-5 h-5 text-blue-600" />
									Financial Activity
								</Card.Title>
								<Badge variant="outline">{homeownerTransactions.length} items</Badge>
							</div>
						</Card.Header>
						<Card.Content class="p-0">
							<div class="max-h-80 overflow-y-auto divide-y divide-gray-100">
								{#each homeownerTransactions.slice(0, 12) as tx}
									<div class="px-4 py-3 flex items-start gap-3">
										<div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 {getHomeownerTransactionColor(tx.type, tx.status)}">
											<svelte:component this={getHomeownerTransactionIcon(tx.type)} class="w-4 h-4" />
										</div>
										<div class="flex-1 min-w-0">
											<div class="font-medium text-gray-900 text-sm">{tx.description}</div>
											<div class="flex items-center gap-2 mt-0.5">
												<span class="text-xs text-gray-500">{tx.date}</span>
												{#if tx.status === 'pending'}
													<Badge variant="outline" class="text-xs bg-amber-50 text-amber-700 border-amber-200">Pending</Badge>
												{:else if tx.status === 'processing'}
													<Badge variant="outline" class="text-xs bg-blue-50 text-blue-700 border-blue-200">Processing</Badge>
												{/if}
											</div>
										</div>
										{#if tx.amount}
											<div class="text-sm font-medium {tx.amount < 0 ? 'text-red-600' : 'text-green-600'}">
												{tx.amount < 0 ? '-' : '+'}${Math.abs(tx.amount).toLocaleString()}
											</div>
										{/if}
									</div>
								{/each}
							</div>
							{#if homeownerTransactions.length > 12}
								<div class="px-4 py-3 border-t border-gray-100 text-center">
									<span class="text-sm text-gray-500">+ {homeownerTransactions.length - 12} more transactions</span>
								</div>
							{/if}
						</Card.Content>
					</Card.Root>
					{/if}
				</div>
				
				<!-- Sidebar -->
				<div class="space-y-6">
					<Card.Root>
						<Card.Header>
							<Card.Title>Financial Summary</Card.Title>
						</Card.Header>
						<Card.Content class="space-y-4">
							<div class="flex justify-between">
								<span class="text-gray-600">Property Value</span>
								<span class="font-medium">${Math.round(homeownerPropertyValue).toLocaleString()}</span>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-600">Mortgage</span>
								<span class="font-medium text-red-600">-${Math.round(homeownerMortgageBalance).toLocaleString()}</span>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-600">Equity Accessed</span>
								<span class="font-medium">-${homeownerEquityAccessAmount.toLocaleString()}</span>
							</div>
							<hr />
							<div class="flex justify-between">
								<span class="text-gray-600 font-medium">Net Equity</span>
								<span class="font-bold text-green-600">
									${Math.round(homeownerPropertyValue - homeownerMortgageBalance).toLocaleString()}
								</span>
							</div>
						</Card.Content>
					</Card.Root>
					
					<Card.Root>
						<Card.Header>
							<Card.Title>Monthly Costs</Card.Title>
						</Card.Header>
						<Card.Content class="space-y-3">
							<div class="flex justify-between text-sm">
								<span class="text-gray-600">Mortgage Payment</span>
								<span class="font-medium">-${homeownerMonthlyPayment.toLocaleString()}</span>
							</div>
							{#if homeownerIsRenting}
								<div class="flex justify-between text-sm">
									<span class="text-gray-600">Rental Income</span>
									<span class="font-medium text-green-600">+${homeownerRentalIncome.toLocaleString()}</span>
								</div>
								<hr />
								<div class="flex justify-between text-sm">
									<span class="text-gray-600 font-medium">Net Monthly</span>
									<span class="font-bold {homeownerRentalIncome - homeownerMonthlyPayment >= 0 ? 'text-green-600' : 'text-red-600'}">
										${(homeownerRentalIncome - homeownerMonthlyPayment).toLocaleString()}
									</span>
								</div>
							{/if}
						</Card.Content>
					</Card.Root>
				</div>
			</div>
			
			{:else if activeRole === 'custodian'}
			<!-- CUSTODIAN SIMULATION -->
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
				<div class="lg:col-span-2 space-y-6">
					<!-- Overview Stats -->
					<div class="grid grid-cols-3 gap-4">
						<Card.Root>
							<Card.Content class="pt-6 text-center">
								<Building class="w-8 h-8 text-blue-600 mx-auto mb-2" />
								<div class="text-2xl font-bold text-gray-900">{custodianManagedProperties}</div>
								<div class="text-sm text-gray-500">Properties Managed</div>
							</Card.Content>
						</Card.Root>
						<Card.Root>
							<Card.Content class="pt-6 text-center">
								<Percent class="w-8 h-8 text-green-600 mx-auto mb-2" />
								<div class="text-2xl font-bold text-gray-900">{custodianOccupancyRate.toFixed(1)}%</div>
								<div class="text-sm text-gray-500">Occupancy Rate</div>
							</Card.Content>
						</Card.Root>
						<Card.Root>
							<Card.Content class="pt-6 text-center">
								<DollarSign class="w-8 h-8 text-purple-600 mx-auto mb-2" />
								<div class="text-2xl font-bold text-gray-900">${custodianMonthlyFees.toLocaleString()}</div>
								<div class="text-sm text-gray-500">Monthly Fees</div>
							</Card.Content>
						</Card.Root>
					</div>
					
					<!-- Pending Tasks -->
					<Card.Root>
						<Card.Header>
							<div class="flex items-center justify-between">
								<Card.Title class="flex items-center gap-2">
									<FileText class="w-5 h-5 text-orange-600" />
									Pending Tasks
								</Card.Title>
								<Badge variant="outline">{custodianPendingTasks.length} tasks</Badge>
							</div>
						</Card.Header>
						<Card.Content class="p-0">
							{#if custodianPendingTasks.length === 0}
								<div class="text-center py-8 text-gray-500">
									<CheckCircle class="w-12 h-12 mx-auto mb-3 text-green-500" />
									<p>All tasks completed! Simulate a month to generate new tasks.</p>
								</div>
							{:else}
								<div class="divide-y divide-gray-100">
									{#each custodianPendingTasks as task}
										{@const taskProperty = properties.find(p => p.id === task.propertyId)}
										{@const taskPropAny = taskProperty as any}
										{@const taskImgSrc = taskPropAny?._poolData?.images?.isometric || taskPropAny?.image}
										<div class="px-4 py-3 flex items-center gap-3">
											<!-- Property Thumbnail -->
											{#if taskImgSrc}
												<div class="w-14 h-12 flex-shrink-0 rounded overflow-hidden bg-gray-100">
													<img 
														src={taskImgSrc.startsWith?.('data:') ? taskImgSrc : `data:image/png;base64,${taskImgSrc}`}
														alt={task.propertyAddress}
														class="w-full h-full object-cover"
													/>
												</div>
											{:else}
												<div class="w-14 h-12 flex-shrink-0 rounded bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
													<Home class="w-5 h-5 text-gray-300" />
												</div>
											{/if}
											
											<!-- Task Info -->
											<div class="flex-1 min-w-0">
												<div class="flex items-center gap-2">
													<div class="w-2 h-2 rounded-full flex-shrink-0 {task.priority === 'high' ? 'bg-red-500' : task.priority === 'medium' ? 'bg-amber-500' : 'bg-gray-400'}"></div>
													<div class="font-medium text-gray-900 truncate">{task.task}</div>
												</div>
												<div class="text-sm text-gray-500 truncate">{task.propertyAddress}</div>
												<div class="flex items-center gap-2 mt-1">
													<Badge variant="outline" class="text-xs">{task.serviceType}</Badge>
													<span class="text-xs text-gray-400">Due: {task.due}</span>
													{#if task.cost}
														<span class="text-xs font-medium text-green-600">${task.cost}</span>
													{/if}
												</div>
											</div>
											
											<!-- Complete Button -->
											<Button variant="outline" size="sm" onclick={() => custodianCompleteTask(task.id)}>
												Complete
											</Button>
										</div>
									{/each}
								</div>
							{/if}
						</Card.Content>
					</Card.Root>
					
					<!-- Simulate Time -->
					<Card.Root>
						<Card.Header>
							<Card.Title>Simulate Operations</Card.Title>
						</Card.Header>
						<Card.Content>
							<div class="flex gap-2 mb-4">
								<Button variant="outline" onclick={simulateNetworkMonth}>Simulate Month</Button>
								<Button variant="outline" onclick={custodianAddProperty}>Add New Property</Button>
							</div>
							<p class="text-xs text-gray-500">Simulating generates random maintenance tasks and occupancy changes</p>
						</Card.Content>
					</Card.Root>
					
					<!-- Custodian Activity Log -->
					{#if custodianTransactions.length > 0}
					<Card.Root>
						<Card.Header>
							<div class="flex items-center justify-between">
								<Card.Title class="flex items-center gap-2">
									<FileText class="w-5 h-5 text-orange-600" />
									Management Activity
								</Card.Title>
								<Badge variant="outline">{custodianTransactions.length} items</Badge>
							</div>
						</Card.Header>
						<Card.Content class="p-0">
							<div class="max-h-80 overflow-y-auto divide-y divide-gray-100">
								{#each custodianTransactions.slice(0, 12) as tx}
									<div class="px-4 py-3 flex items-start gap-3">
										<div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 {getCustodianTransactionColor(tx.type, tx.status)}">
											<svelte:component this={getCustodianTransactionIcon(tx.type)} class="w-4 h-4" />
										</div>
										<div class="flex-1 min-w-0">
											<div class="font-medium text-gray-900 text-sm">{tx.description}</div>
											<div class="flex flex-wrap items-center gap-2 mt-0.5">
												<span class="text-xs text-gray-500">{tx.date}</span>
												{#if tx.propertyAddress}
													<span class="text-xs text-blue-600">@ {tx.propertyAddress}</span>
												{/if}
												{#if tx.serviceType}
													<Badge variant="outline" class="text-xs">{tx.serviceType}</Badge>
												{/if}
												{#if tx.status === 'pending'}
													<Badge variant="outline" class="text-xs bg-amber-50 text-amber-700 border-amber-200">Pending</Badge>
												{/if}
											</div>
										</div>
										{#if tx.amount}
											<div class="text-sm font-medium text-green-600">
												+${Math.abs(tx.amount).toLocaleString()}
											</div>
										{/if}
									</div>
								{/each}
							</div>
							{#if custodianTransactions.length > 12}
								<div class="px-4 py-3 border-t border-gray-100 text-center">
									<span class="text-sm text-gray-500">+ {custodianTransactions.length - 12} more transactions</span>
								</div>
							{/if}
						</Card.Content>
					</Card.Root>
					{/if}
				</div>
				
				<!-- Sidebar -->
				<div class="space-y-6">
					<Card.Root>
						<Card.Header>
							<Card.Title class="flex items-center gap-2">
								<Users class="w-5 h-5 text-gray-600" />
								Service Provider Types
							</Card.Title>
							<Card.Description>{serviceProviderTypes.length} provider types across 6 categories</Card.Description>
						</Card.Header>
						<Card.Content class="space-y-3 text-sm">
							<!-- Management -->
							<div>
								<div class="text-xs font-semibold text-gray-500 mb-1.5">MANAGEMENT</div>
								<div class="flex flex-wrap gap-1">
									<Badge variant="outline" class="text-xs bg-blue-50 text-blue-700 border-blue-200">Property Manager</Badge>
									<Badge variant="outline" class="text-xs bg-blue-50 text-blue-700 border-blue-200">Strata Manager</Badge>
									<Badge variant="outline" class="text-xs bg-blue-50 text-blue-700 border-blue-200">Building Manager</Badge>
								</div>
							</div>
							
							<!-- Trades -->
							<div>
								<div class="text-xs font-semibold text-gray-500 mb-1.5">TRADES</div>
								<div class="flex flex-wrap gap-1">
									<Badge variant="outline" class="text-xs bg-amber-50 text-amber-700 border-amber-200">Plumber</Badge>
									<Badge variant="outline" class="text-xs bg-amber-50 text-amber-700 border-amber-200">Electrician</Badge>
									<Badge variant="outline" class="text-xs bg-amber-50 text-amber-700 border-amber-200">HVAC Tech</Badge>
									<Badge variant="outline" class="text-xs bg-amber-50 text-amber-700 border-amber-200">Carpenter</Badge>
									<Badge variant="outline" class="text-xs bg-amber-50 text-amber-700 border-amber-200">Tiler</Badge>
									<Badge variant="outline" class="text-xs bg-amber-50 text-amber-700 border-amber-200">Painter</Badge>
									<Badge variant="outline" class="text-xs bg-amber-50 text-amber-700 border-amber-200">Roofer</Badge>
									<Badge variant="outline" class="text-xs bg-amber-50 text-amber-700 border-amber-200">Gas Fitter</Badge>
								</div>
							</div>
							
							<!-- Outdoor -->
							<div>
								<div class="text-xs font-semibold text-gray-500 mb-1.5">OUTDOOR</div>
								<div class="flex flex-wrap gap-1">
									<Badge variant="outline" class="text-xs bg-green-50 text-green-700 border-green-200">Gardener</Badge>
									<Badge variant="outline" class="text-xs bg-green-50 text-green-700 border-green-200">Arborist</Badge>
									<Badge variant="outline" class="text-xs bg-green-50 text-green-700 border-green-200">Landscaper</Badge>
									<Badge variant="outline" class="text-xs bg-green-50 text-green-700 border-green-200">Pool Tech</Badge>
								</div>
							</div>
							
							<!-- Cleaning -->
							<div>
								<div class="text-xs font-semibold text-gray-500 mb-1.5">CLEANING & PEST</div>
								<div class="flex flex-wrap gap-1">
									<Badge variant="outline" class="text-xs bg-cyan-50 text-cyan-700 border-cyan-200">Cleaner</Badge>
									<Badge variant="outline" class="text-xs bg-cyan-50 text-cyan-700 border-cyan-200">Pest Control</Badge>
									<Badge variant="outline" class="text-xs bg-cyan-50 text-cyan-700 border-cyan-200">Rubbish Removal</Badge>
								</div>
							</div>
							
							<!-- Security -->
							<div>
								<div class="text-xs font-semibold text-gray-500 mb-1.5">SECURITY</div>
								<div class="flex flex-wrap gap-1">
									<Badge variant="outline" class="text-xs bg-red-50 text-red-700 border-red-200">Locksmith</Badge>
									<Badge variant="outline" class="text-xs bg-red-50 text-red-700 border-red-200">Security Installer</Badge>
								</div>
							</div>
							
							<!-- Professional -->
							<div>
								<div class="text-xs font-semibold text-gray-500 mb-1.5">PROFESSIONAL</div>
								<div class="flex flex-wrap gap-1">
									<Badge variant="outline" class="text-xs bg-purple-50 text-purple-700 border-purple-200">Legal Advisor</Badge>
									<Badge variant="outline" class="text-xs bg-purple-50 text-purple-700 border-purple-200">Accountant</Badge>
									<Badge variant="outline" class="text-xs bg-purple-50 text-purple-700 border-purple-200">Valuer</Badge>
									<Badge variant="outline" class="text-xs bg-purple-50 text-purple-700 border-purple-200">Building Inspector</Badge>
								</div>
							</div>
						</Card.Content>
					</Card.Root>
					
					<Card.Root>
						<Card.Header>
							<Card.Title>Earnings Summary</Card.Title>
						</Card.Header>
						<Card.Content class="space-y-3">
							<div class="flex justify-between text-sm">
								<span class="text-gray-600">Service Fees</span>
								<span class="font-medium text-green-600">+${custodianMonthlyFees.toLocaleString()}/mo</span>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-600">Properties Serviced</span>
								<span class="font-medium">{custodianManagedProperties}</span>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-600">Annual Projection</span>
								<span class="font-medium">${(custodianMonthlyFees * 12).toLocaleString()}</span>
							</div>
						</Card.Content>
					</Card.Root>
					
					<Card.Root class="bg-blue-50 border-blue-200">
						<Card.Content class="pt-6">
							<p class="text-sm text-blue-800">
								<strong>Service Providers</strong> earn fees for completing tasks 
								assigned by the network. AI triages and routes work to qualified providers.
							</p>
						</Card.Content>
					</Card.Root>
				</div>
			</div>
			
			{:else if activeRole === 'foundation'}
			<!-- FOUNDATION PARTNER SIMULATION -->
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
				<div class="lg:col-span-2 space-y-6">
					<!-- Staking Card -->
					<Card.Root>
						<Card.Header>
							<Card.Title class="flex items-center gap-2">
								<Landmark class="w-5 h-5 text-purple-600" />
								Foundation Staking
							</Card.Title>
						</Card.Header>
						<Card.Content>
							{#if foundationTotalStaked === 0}
								<div class="space-y-4">
									<div>
										<label for="stake-amount" class="block text-sm font-medium text-gray-700 mb-2">Stake Amount</label>
										<div class="flex items-center gap-2">
											<span class="text-gray-500">$</span>
											<input 
												id="stake-amount"
												type="number" 
												min="10000" 
												step="10000"
												bind:value={foundationStakeAmount}
												class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
											/>
										</div>
										<p class="text-xs text-gray-500 mt-1">Minimum stake: $10,000</p>
									</div>
									
									<div>
										<label class="block text-sm font-medium text-gray-700 mb-2">Lock Period</label>
										<div class="grid grid-cols-3 gap-2">
											<button 
												onclick={() => foundationLockPeriod = 6}
												class="p-3 border rounded-lg text-center transition {foundationLockPeriod === 6 ? 'border-purple-500 bg-purple-50 text-purple-700' : 'border-gray-200 hover:border-gray-300'}"
											>
												<div class="font-medium">6 Months</div>
												<div class="text-xs text-gray-500">4.5% APY</div>
											</button>
											<button 
												onclick={() => foundationLockPeriod = 12}
												class="p-3 border rounded-lg text-center transition {foundationLockPeriod === 12 ? 'border-purple-500 bg-purple-50 text-purple-700' : 'border-gray-200 hover:border-gray-300'}"
											>
												<div class="font-medium">12 Months</div>
												<div class="text-xs text-gray-500">5.2% APY</div>
											</button>
											<button 
												onclick={() => foundationLockPeriod = 24}
												class="p-3 border rounded-lg text-center transition {foundationLockPeriod === 24 ? 'border-purple-500 bg-purple-50 text-purple-700' : 'border-gray-200 hover:border-gray-300'}"
											>
												<div class="font-medium">24 Months</div>
												<div class="text-xs text-gray-500">6.0% APY</div>
											</button>
										</div>
									</div>
									
									<div class="p-4 bg-purple-50 rounded-lg">
										<div class="text-sm text-purple-700 mb-1">Projected Annual Earnings</div>
										<div class="text-2xl font-bold text-purple-700">
											${Math.round(foundationStakeAmount * (foundationLockPeriod === 6 ? 0.045 : foundationLockPeriod === 12 ? 0.052 : 0.06)).toLocaleString()}
										</div>
									</div>
									
									<Button class="w-full bg-purple-600 hover:bg-purple-700" onclick={foundationStake}>
										<Landmark class="w-4 h-4 mr-2" />
										Stake Funds
									</Button>
								</div>
							{:else}
								<!-- Active Stake -->
								<div class="space-y-6">
									<div class="p-4 bg-purple-50 rounded-lg border border-purple-200">
										<div class="flex items-center justify-between mb-2">
											<span class="text-sm font-medium text-purple-700">Active Stake</span>
											<Badge variant="outline" class="bg-purple-100 text-purple-700 border-purple-200">
												{foundationMonthsStaked} / {foundationLockPeriod} months
											</Badge>
										</div>
										<div class="text-3xl font-bold text-purple-900 mb-1">
											${foundationTotalStaked.toLocaleString()}
										</div>
										<div class="text-sm text-purple-600">
											+${foundationEarnings.toLocaleString(undefined, { maximumFractionDigits: 2 })} earned
										</div>
									</div>
									
									<!-- Lock Progress -->
									<div>
										<div class="flex justify-between text-sm mb-2">
											<span class="text-gray-600">Lock Progress</span>
											<span class="font-medium">{Math.min(100, (foundationMonthsStaked / foundationLockPeriod * 100)).toFixed(0)}%</span>
										</div>
										<div class="h-3 bg-gray-200 rounded-full overflow-hidden">
											<div 
												class="h-full bg-gradient-to-r from-purple-400 to-purple-600 rounded-full transition-all"
												style="width: {Math.min(100, foundationMonthsStaked / foundationLockPeriod * 100)}%"
											></div>
										</div>
										{#if foundationMonthsStaked < foundationLockPeriod}
											<p class="text-xs text-gray-500 mt-1">
												{foundationLockPeriod - foundationMonthsStaked} months until unlock
											</p>
										{:else}
											<p class="text-xs text-green-600 mt-1 font-medium">
												Unlocked! You can now withdraw or continue earning.
											</p>
										{/if}
									</div>
									
									<!-- Time Simulation -->
									<div class="flex gap-2">
										<Button variant="outline" onclick={simulateNetworkMonth}>+1 Month</Button>
										<Button variant="outline" onclick={() => { for(let i=0; i<12; i++) simulateNetworkMonth(); }}>+1 Year</Button>
									</div>
									
									{#if foundationMonthsStaked >= foundationLockPeriod}
										<Button 
											class="w-full bg-green-600 hover:bg-green-700"
											onclick={foundationWithdraw}
										>
											Withdraw ${(foundationTotalStaked + foundationEarnings).toLocaleString()}
										</Button>
									{/if}
								</div>
							{/if}
						</Card.Content>
					</Card.Root>
					
					<!-- Foundation Activity Log -->
					{#if foundationTransactions.length > 0}
					<Card.Root>
						<Card.Header>
							<div class="flex items-center justify-between">
								<Card.Title class="flex items-center gap-2">
									<FileText class="w-5 h-5 text-purple-600" />
									Staking Activity
								</Card.Title>
								<Badge variant="outline">{foundationTransactions.length} items</Badge>
							</div>
						</Card.Header>
						<Card.Content class="p-0">
							<div class="max-h-80 overflow-y-auto divide-y divide-gray-100">
								{#each foundationTransactions.slice(0, 12) as tx}
									<div class="px-4 py-3 flex items-start gap-3">
										<div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 {getFoundationTransactionColor(tx.type, tx.status)}">
											<svelte:component this={getFoundationTransactionIcon(tx.type)} class="w-4 h-4" />
										</div>
										<div class="flex-1 min-w-0">
											<div class="font-medium text-gray-900 text-sm">{tx.description}</div>
											<div class="flex items-center gap-2 mt-0.5">
												<span class="text-xs text-gray-500">{tx.date}</span>
												{#if tx.status === 'locked'}
													<Badge variant="outline" class="text-xs bg-purple-50 text-purple-700 border-purple-200">Locked</Badge>
												{:else if tx.status === 'pending'}
													<Badge variant="outline" class="text-xs bg-amber-50 text-amber-700 border-amber-200">Pending</Badge>
												{/if}
											</div>
										</div>
										{#if tx.amount}
											<div class="text-sm font-medium {tx.amount < 0 ? 'text-red-600' : 'text-green-600'}">
												{tx.amount < 0 ? '-' : '+'}${Math.abs(tx.amount).toLocaleString()}
											</div>
										{/if}
									</div>
								{/each}
							</div>
							{#if foundationTransactions.length > 12}
								<div class="px-4 py-3 border-t border-gray-100 text-center">
									<span class="text-sm text-gray-500">+ {foundationTransactions.length - 12} more transactions</span>
								</div>
							{/if}
						</Card.Content>
					</Card.Root>
					{/if}
				</div>
				
				<!-- Sidebar -->
				<div class="space-y-6">
					<Card.Root>
						<Card.Header>
							<Card.Title>Network Health</Card.Title>
						</Card.Header>
						<Card.Content class="space-y-3">
							<div class="flex justify-between text-sm">
								<span class="text-gray-600">Total Value Locked</span>
								<span class="font-medium">$24.5M</span>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-600">Foundation Partners</span>
								<span class="font-medium">847</span>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-600">Properties Funded</span>
								<span class="font-medium">156</span>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-600">Network Utilization</span>
								<span class="font-medium text-green-600">89%</span>
							</div>
						</Card.Content>
					</Card.Root>
					
					<Card.Root>
						<Card.Header>
							<Card.Title>Your Impact</Card.Title>
						</Card.Header>
						<Card.Content class="space-y-3">
							<div class="flex justify-between text-sm">
								<span class="text-gray-600">Homes Funded</span>
								<span class="font-medium">{Math.floor(foundationTotalStaked / 50000)}</span>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-600">Families Helped</span>
								<span class="font-medium">{Math.floor(foundationTotalStaked / 50000)}</span>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-600">Network Contribution</span>
								<span class="font-medium">{foundationTotalStaked > 0 ? ((foundationTotalStaked / 24500000) * 100).toFixed(3) : '0'}%</span>
							</div>
						</Card.Content>
					</Card.Root>
					
					<Card.Root class="border-purple-200 bg-purple-50">
						<Card.Content class="pt-6 text-center">
							<Landmark class="w-8 h-8 text-purple-600 mx-auto mb-2" />
							<p class="text-sm text-gray-700">Foundation Partners provide long-term stability to the OSF network</p>
						</Card.Content>
					</Card.Root>
				</div>
			</div>
			{/if}
		</div>
		
		{:else if activeTab === 'network'}
		<!-- Network Financial Dashboard -->
		<div class="max-w-6xl mx-auto px-4 py-8">
			<div class="flex items-center justify-between mb-6">
				<div>
					<h1 class="text-2xl font-bold text-gray-900">Network Financial Model</h1>
					<p class="text-gray-500 text-sm">Unified view of all financial flows in the OSF simulation</p>
				</div>
				<div class="flex items-center gap-2">
					<Badge variant="outline" class="text-blue-600 border-blue-200">
						Month {networkMonth}
					</Badge>
					<Button onclick={simulateNetworkMonth}>
						<Play class="w-4 h-4 mr-2" />
						Simulate Month
					</Button>
				</div>
			</div>
			
			<!-- Network Overview Cards -->
			<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
				<Card.Root>
					<Card.Content class="pt-6">
						<div class="text-gray-500 text-xs mb-1">Total Property Value</div>
						<div class="text-2xl font-bold text-gray-900">${(networkTotalPropertyValue / 1000000).toFixed(2)}M</div>
						<div class="text-xs text-green-600 mt-1">+{((tokenPrice / lastTokenPrice - 1) * 100).toFixed(2)}% this month</div>
					</Card.Content>
				</Card.Root>
				<Card.Root>
					<Card.Content class="pt-6">
						<div class="text-gray-500 text-xs mb-1">Token Price</div>
						<div class="text-2xl font-bold text-gray-900">${tokenPrice.toFixed(4)}</div>
						<div class="text-xs text-gray-500 mt-1">{totalTokenSupply.toLocaleString()} tokens</div>
					</Card.Content>
				</Card.Root>
				<Card.Root>
					<Card.Content class="pt-6">
						<div class="text-gray-500 text-xs mb-1">Network Treasury</div>
						<div class="text-2xl font-bold text-gray-900">${networkTreasury.toLocaleString()}</div>
						<div class="text-xs text-gray-500 mt-1">Operating funds</div>
					</Card.Content>
				</Card.Root>
				<Card.Root>
					<Card.Content class="pt-6">
						<div class="text-gray-500 text-xs mb-1">Network Yield</div>
						<div class="text-2xl font-bold text-gray-900">{networkAverageYield.toFixed(2)}%</div>
						<div class="text-xs text-gray-500 mt-1">{(networkOccupancyRate * 100).toFixed(0)}% occupancy</div>
					</Card.Content>
				</Card.Root>
			</div>
			
			<!-- Property Portfolio Breakdown -->
			{#if true}
			{@const totalProperties = properties.length}
			{@const tokenizedProperties = properties.filter(p => true).length}
			{@const rentedProperties = Math.floor(properties.length * networkOccupancyRate * 0.6)}
			{@const rentToOwnProperties = Math.floor(properties.length * 0.25)}
			{@const homeownerOccupied = Math.max(0, properties.length - rentedProperties - rentToOwnProperties)}
			{@const netGrowth = propertiesAdded - propertiesExited}
			<div class="grid grid-cols-2 md:grid-cols-6 gap-3 mb-6">
				<div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 border border-blue-200">
					<div class="flex items-center gap-2 mb-2">
						<Building class="w-5 h-5 text-blue-600" />
						<span class="text-xs font-medium text-blue-700">Total Properties</span>
					</div>
					<div class="text-2xl font-bold text-blue-900">{totalProperties}</div>
					<div class="text-xs text-blue-600 mt-1">
						{#if netGrowth > 0}
							<span class="text-green-600">+{netGrowth} net</span>
						{:else if netGrowth < 0}
							<span class="text-red-600">{netGrowth} net</span>
						{:else}
							In OSF network
						{/if}
					</div>
				</div>
				<div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 border border-purple-200">
					<div class="flex items-center gap-2 mb-2">
						<PiggyBank class="w-5 h-5 text-purple-600" />
						<span class="text-xs font-medium text-purple-700">Tokenized</span>
					</div>
					<div class="text-2xl font-bold text-purple-900">{tokenizedProperties}</div>
					<div class="text-xs text-purple-600 mt-1">Fractional shares</div>
				</div>
				<div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 border border-green-200">
					<div class="flex items-center gap-2 mb-2">
						<Key class="w-5 h-5 text-green-600" />
						<span class="text-xs font-medium text-green-700">Rented</span>
					</div>
					<div class="text-2xl font-bold text-green-900">{rentedProperties}</div>
					<div class="text-xs text-green-600 mt-1">Standard rental</div>
				</div>
				<div class="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-4 border border-amber-200">
					<div class="flex items-center gap-2 mb-2">
						<TrendingUp class="w-5 h-5 text-amber-600" />
						<span class="text-xs font-medium text-amber-700">Rent-to-Own</span>
					</div>
					<div class="text-2xl font-bold text-amber-900">{rentToOwnProperties}</div>
					<div class="text-xs text-amber-600 mt-1">Equity pathway</div>
				</div>
				<div class="bg-gradient-to-br from-rose-50 to-rose-100 rounded-xl p-4 border border-rose-200">
					<div class="flex items-center gap-2 mb-2">
						<Home class="w-5 h-5 text-rose-600" />
						<span class="text-xs font-medium text-rose-700">Homeowners</span>
					</div>
					<div class="text-2xl font-bold text-rose-900">{homeownerOccupied}</div>
					<div class="text-xs text-rose-600 mt-1">Owner-occupied</div>
				</div>
				<div class="bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl p-4 border border-slate-200">
					<div class="flex items-center gap-2 mb-2">
						<ArrowRightLeft class="w-5 h-5 text-slate-600" />
						<span class="text-xs font-medium text-slate-700">Turnover</span>
					</div>
					<div class="flex items-center gap-2">
						<span class="text-sm font-bold text-green-600">+{propertiesAdded}</span>
						<span class="text-slate-400">/</span>
						<span class="text-sm font-bold text-red-600">-{propertiesExited}</span>
					</div>
					<div class="text-xs text-slate-600 mt-1">Joined / Exited</div>
				</div>
			</div>
			{/if}
			
			<!-- Network Reputation & Satisfaction -->
			<div class="mb-6 p-4 rounded-xl border bg-gradient-to-r from-indigo-50 to-purple-50 border-indigo-200">
				<div class="flex items-center justify-between mb-3">
					<div class="flex items-center gap-2">
						<Star class="w-5 h-5 text-indigo-600" />
						<span class="font-semibold text-indigo-900">Network Reputation</span>
						<span class="text-xs px-2 py-0.5 rounded-full {networkReputation.trend === 'rising' ? 'bg-green-100 text-green-700' : networkReputation.trend === 'falling' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'}">
							{networkReputation.trend === 'rising' ? '↑ Rising' : networkReputation.trend === 'falling' ? '↓ Falling' : '→ Stable'}
						</span>
					</div>
					<div class="flex items-center gap-2">
						<span class="text-3xl font-bold {networkReputation.score >= 75 ? 'text-green-600' : networkReputation.score >= 50 ? 'text-amber-600' : 'text-red-600'}">
							{networkReputation.score}
						</span>
						<span class="text-sm text-indigo-600">/100</span>
					</div>
				</div>
				
				<!-- Reputation bar -->
				<div class="w-full h-2 bg-indigo-100 rounded-full mb-4">
					<div 
						class="h-full rounded-full transition-all duration-500 {networkReputation.score >= 75 ? 'bg-green-500' : networkReputation.score >= 50 ? 'bg-amber-500' : 'bg-red-500'}"
						style="width: {networkReputation.score}%"
					></div>
				</div>
				
				<!-- Stakeholder satisfaction breakdown -->
				<div class="grid grid-cols-5 gap-2 text-center">
					<div class="p-2 rounded-lg bg-white/60">
						<div class="text-lg font-bold {networkReputation.investorSatisfaction >= 70 ? 'text-green-600' : networkReputation.investorSatisfaction >= 50 ? 'text-amber-600' : 'text-red-600'}">
							{networkReputation.investorSatisfaction}%
						</div>
						<div class="text-xs text-gray-600">Investors</div>
					</div>
					<div class="p-2 rounded-lg bg-white/60">
						<div class="text-lg font-bold {networkReputation.homeownerSatisfaction >= 70 ? 'text-green-600' : networkReputation.homeownerSatisfaction >= 50 ? 'text-amber-600' : 'text-red-600'}">
							{networkReputation.homeownerSatisfaction}%
						</div>
						<div class="text-xs text-gray-600">Homeowners</div>
					</div>
					<div class="p-2 rounded-lg bg-white/60">
						<div class="text-lg font-bold {networkReputation.renterSatisfaction >= 70 ? 'text-green-600' : networkReputation.renterSatisfaction >= 50 ? 'text-amber-600' : 'text-red-600'}">
							{networkReputation.renterSatisfaction}%
						</div>
						<div class="text-xs text-gray-600">Renters</div>
					</div>
					<div class="p-2 rounded-lg bg-white/60">
						<div class="text-lg font-bold {networkReputation.tenantSatisfaction >= 70 ? 'text-green-600' : networkReputation.tenantSatisfaction >= 50 ? 'text-amber-600' : 'text-red-600'}">
							{networkReputation.tenantSatisfaction}%
						</div>
						<div class="text-xs text-gray-600">Rent-to-Own</div>
					</div>
					<div class="p-2 rounded-lg bg-white/60">
						<div class="text-lg font-bold {networkReputation.serviceProviderSatisfaction >= 70 ? 'text-green-600' : networkReputation.serviceProviderSatisfaction >= 50 ? 'text-amber-600' : 'text-red-600'}">
							{networkReputation.serviceProviderSatisfaction}%
						</div>
						<div class="text-xs text-gray-600">Services</div>
					</div>
				</div>
				
				<!-- Word of mouth multiplier -->
				{#if networkReputation.wordOfMouthMultiplier > 1.1}
				<div class="mt-3 text-xs text-center text-indigo-700">
					🗣️ Word of mouth bonus: {((networkReputation.wordOfMouthMultiplier - 1) * 100).toFixed(0)}% increased referrals from satisfied members
				</div>
				{/if}
			</div>
			
			<!-- Live Performance Charts -->
			{#if simulationHistory.length > 1}
			{@const chartWidth = 600}
			{@const chartHeight = 80}
			{@const padding = 5}
			{@const startingNetWorth = 100000}
			{@const currentNetWorth = balance + portfolioValue}
			{@const netWorthChange = currentNetWorth - startingNetWorth}
			{@const netWorthChangePercent = (netWorthChange / startingNetWorth) * 100}
			{@const startingNetworkValue = simulationHistory[0]?.networkValue || networkTotalPropertyValue}
			{@const networkChange = ((networkTotalPropertyValue - startingNetworkValue) / startingNetworkValue) * 100}
			<div class="mb-6 p-4 rounded-xl border bg-gradient-to-r from-slate-50 to-gray-50 border-slate-200">
				<div class="flex items-center justify-between mb-4">
					<div class="flex items-center gap-2">
						<Activity class="w-5 h-5 text-slate-600" />
						<span class="font-semibold text-slate-900">Live Performance</span>
						<span class="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
							{simulationHistory.length} months tracked
						</span>
					</div>
					<div class="flex items-center gap-4 text-sm">
						<div class="flex items-center gap-1">
							<div class="w-3 h-3 rounded-full bg-blue-500"></div>
							<span class="text-slate-600">Network</span>
						</div>
						<div class="flex items-center gap-1">
							<div class="w-3 h-3 rounded-full bg-green-500"></div>
							<span class="text-slate-600">Your Portfolio</span>
						</div>
						<div class="flex items-center gap-1">
							<div class="w-3 h-3 rounded-full bg-purple-500"></div>
							<span class="text-slate-600">Token Price</span>
						</div>
					</div>
				</div>
				
				<!-- Summary Stats Row -->
				<div class="grid grid-cols-4 gap-3 mb-4">
					<div class="bg-white rounded-lg p-3 border border-slate-100">
						<div class="text-xs text-slate-500 mb-1">Network Value</div>
						<div class="text-lg font-bold text-slate-800">${(networkTotalPropertyValue / 1000000).toFixed(2)}M</div>
						<div class="text-xs {networkChange >= 0 ? 'text-green-600' : 'text-red-600'}">
							{networkChange >= 0 ? '+' : ''}{networkChange.toFixed(1)}% total
						</div>
					</div>
					<div class="bg-white rounded-lg p-3 border border-slate-100">
						<div class="text-xs text-slate-500 mb-1">Your Net Worth</div>
						<div class="text-lg font-bold text-slate-800">${currentNetWorth.toLocaleString(undefined, {maximumFractionDigits: 0})}</div>
						<div class="text-xs {netWorthChangePercent >= 0 ? 'text-green-600' : 'text-red-600'}">
							{netWorthChangePercent >= 0 ? '+' : ''}{netWorthChangePercent.toFixed(1)}% return
						</div>
					</div>
					<div class="bg-white rounded-lg p-3 border border-slate-100">
						<div class="text-xs text-slate-500 mb-1">Token Price</div>
						<div class="text-lg font-bold text-slate-800">${tokenPrice.toFixed(4)}</div>
						<div class="text-xs {tokenPrice >= 1 ? 'text-green-600' : 'text-red-600'}">
							{tokenPrice >= 1 ? '+' : ''}{((tokenPrice - 1) * 100).toFixed(1)}% from $1.00
						</div>
					</div>
					<div class="bg-white rounded-lg p-3 border border-slate-100">
						<div class="text-xs text-slate-500 mb-1">Properties</div>
						<div class="text-lg font-bold text-slate-800">{properties.length}</div>
						<div class="text-xs text-slate-600">
							{properties.length - (simulationHistory[0]?.propertyCount || properties.length) >= 0 ? '+' : ''}{properties.length - (simulationHistory[0]?.propertyCount || properties.length)} net
						</div>
					</div>
				</div>
				
				<!-- Charts Grid -->
				<div class="grid md:grid-cols-2 gap-4">
					<!-- Network Value Chart -->
					<div class="bg-white rounded-lg p-3 border border-slate-100">
						<div class="text-xs font-medium text-slate-600 mb-2">Network Property Value</div>
						<svg viewBox="0 0 {chartWidth} {chartHeight}" class="w-full h-16">
							<defs>
								<linearGradient id="networkGradientLive" x1="0%" y1="0%" x2="0%" y2="100%">
									<stop offset="0%" style="stop-color:#3b82f6;stop-opacity:0.3" />
									<stop offset="100%" style="stop-color:#3b82f6;stop-opacity:0.05" />
								</linearGradient>
							</defs>
							<path d={generateAreaPath(simulationHistory.map(h => h.networkValue), chartWidth, chartHeight, padding)} fill="url(#networkGradientLive)" />
							<path d={generateSparklinePath(simulationHistory.map(h => h.networkValue), chartWidth, chartHeight, padding)} fill="none" stroke="#3b82f6" stroke-width="2" />
							<circle cx={chartWidth - padding} cy={getSparklineLastDotY(simulationHistory.map(h => h.networkValue), chartHeight, padding)} r="4" fill="#3b82f6" />
						</svg>
						<div class="flex justify-between text-xs text-slate-400 mt-1">
							<span>Month 1</span>
							<span>Month {networkMonth}</span>
						</div>
					</div>
					
					<!-- Your Net Worth Chart -->
					<div class="bg-white rounded-lg p-3 border border-slate-100">
						<div class="text-xs font-medium text-slate-600 mb-2">Your Net Worth</div>
						<svg viewBox="0 0 {chartWidth} {chartHeight}" class="w-full h-16">
							<defs>
								<linearGradient id="netWorthGradientLive" x1="0%" y1="0%" x2="0%" y2="100%">
									<stop offset="0%" style="stop-color:#22c55e;stop-opacity:0.3" />
									<stop offset="100%" style="stop-color:#22c55e;stop-opacity:0.05" />
								</linearGradient>
							</defs>
							<path d={generateAreaPath(simulationHistory.map(h => h.userNetWorth), chartWidth, chartHeight, padding)} fill="url(#netWorthGradientLive)" />
							<path d={generateSparklinePath(simulationHistory.map(h => h.userNetWorth), chartWidth, chartHeight, padding)} fill="none" stroke="#22c55e" stroke-width="2" />
							<circle cx={chartWidth - padding} cy={getSparklineLastDotY(simulationHistory.map(h => h.userNetWorth), chartHeight, padding)} r="4" fill="#22c55e" />
						</svg>
						<div class="flex justify-between text-xs text-slate-400 mt-1">
							<span>$100K start</span>
							<span>${(currentNetWorth / 1000).toFixed(0)}K now</span>
						</div>
					</div>
					
					<!-- Token Price Chart -->
					<div class="bg-white rounded-lg p-3 border border-slate-100">
						<div class="text-xs font-medium text-slate-600 mb-2">Token Price</div>
						<svg viewBox="0 0 {chartWidth} {chartHeight}" class="w-full h-16">
							<defs>
								<linearGradient id="tokenGradientLive" x1="0%" y1="0%" x2="0%" y2="100%">
									<stop offset="0%" style="stop-color:#a855f7;stop-opacity:0.3" />
									<stop offset="100%" style="stop-color:#a855f7;stop-opacity:0.05" />
								</linearGradient>
							</defs>
							<path d={generateAreaPath(simulationHistory.map(h => h.tokenPrice), chartWidth, chartHeight, padding)} fill="url(#tokenGradientLive)" />
							<path d={generateSparklinePath(simulationHistory.map(h => h.tokenPrice), chartWidth, chartHeight, padding)} fill="none" stroke="#a855f7" stroke-width="2" />
							<circle cx={chartWidth - padding} cy={getSparklineLastDotY(simulationHistory.map(h => h.tokenPrice), chartHeight, padding)} r="4" fill="#a855f7" />
						</svg>
						<div class="flex justify-between text-xs text-slate-400 mt-1">
							<span>$1.00 start</span>
							<span>${tokenPrice.toFixed(4)} now</span>
						</div>
					</div>
					
					<!-- Market Conditions Timeline -->
					<div class="bg-white rounded-lg p-3 border border-slate-100">
						<div class="text-xs font-medium text-slate-600 mb-2">Market Conditions</div>
						<div class="flex gap-0.5 h-16 items-end">
							{#each simulationHistory.slice(-60) as point, i}
								{@const barHeight = 20 + (point.reputationScore / 100) * 40}
								<div 
									class="flex-1 rounded-t transition-all"
									style="height: {barHeight}px; background-color: {getMarketConditionColor(point.marketCondition)}; opacity: {0.5 + (i / 120)}"
									title="Month {point.month}: {point.marketCondition}"
								></div>
							{/each}
						</div>
						<div class="flex justify-between text-xs text-slate-400 mt-1">
							<span class="flex items-center gap-1">
								<span class="w-2 h-2 rounded-full bg-green-500"></span> Boom
								<span class="w-2 h-2 rounded-full bg-blue-500 ml-2"></span> Stable
								<span class="w-2 h-2 rounded-full bg-amber-500 ml-2"></span> Stagnant
							</span>
							<span>Current: {marketCondition}</span>
						</div>
					</div>
				</div>
			</div>
			{/if}
			
			<!-- WA Market Conditions Panel -->
			<div class="mb-8 p-4 rounded-xl border 
				{marketCondition === 'boom' ? 'bg-green-50 border-green-200' : 
				 marketCondition === 'stable' ? 'bg-blue-50 border-blue-200' :
				 marketCondition === 'stagnant' ? 'bg-yellow-50 border-yellow-200' :
				 marketCondition === 'declining' ? 'bg-orange-50 border-orange-200' :
				 'bg-red-50 border-red-200'}">
				<div class="flex items-center justify-between mb-4">
					<div class="flex items-center gap-3">
						<div class="w-10 h-10 rounded-lg flex items-center justify-center
							{marketCondition === 'boom' ? 'bg-green-100' : 
							 marketCondition === 'stable' ? 'bg-blue-100' :
							 marketCondition === 'stagnant' ? 'bg-yellow-100' :
							 marketCondition === 'declining' ? 'bg-orange-100' : 'bg-red-100'}">
							<TrendingUp class="w-5 h-5 
								{marketCondition === 'boom' ? 'text-green-600' : 
								 marketCondition === 'stable' ? 'text-blue-600' :
								 marketCondition === 'stagnant' ? 'text-yellow-600' :
								 marketCondition === 'declining' ? 'text-orange-600 rotate-180' : 'text-red-600 rotate-180'}" />
						</div>
						<div>
							<h3 class="font-semibold text-gray-900">WA Market: {marketCondition.charAt(0).toUpperCase() + marketCondition.slice(1)}</h3>
							<p class="text-sm text-gray-600">Economic phase: {economicPhase} ({monthsInPhase} months)</p>
						</div>
					</div>
					<div class="text-right">
						<div class="text-sm font-medium text-gray-700">Consumer Confidence</div>
						<div class="text-2xl font-bold 
							{consumerConfidence >= 60 ? 'text-green-600' : 
							 consumerConfidence >= 40 ? 'text-yellow-600' : 'text-red-600'}">{consumerConfidence}</div>
					</div>
				</div>
				
				<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
					<div class="bg-white/60 rounded-lg p-3">
						<div class="text-xs text-gray-500 mb-1">Iron Ore Price</div>
						<div class="text-lg font-bold text-gray-900">${ironOrePrice.toFixed(0)}/t</div>
						<div class="text-xs {ironOrePrice >= 140 ? 'text-green-600' : ironOrePrice >= 100 ? 'text-blue-600' : ironOrePrice >= 80 ? 'text-yellow-600' : 'text-red-600'}">
							{ironOrePrice >= 140 ? 'Boom levels' : ironOrePrice >= 100 ? 'Healthy' : ironOrePrice >= 80 ? 'Under pressure' : 'Crisis'}
						</div>
					</div>
					<div class="bg-white/60 rounded-lg p-3">
						<div class="text-xs text-gray-500 mb-1">Population Growth</div>
						<div class="text-lg font-bold text-gray-900">{populationGrowthRate.toFixed(1)}%</div>
						<div class="text-xs {populationGrowthRate >= 2 ? 'text-green-600' : populationGrowthRate >= 1 ? 'text-blue-600' : populationGrowthRate >= 0 ? 'text-yellow-600' : 'text-red-600'}">
							{populationGrowthRate >= 2 ? 'Strong migration' : populationGrowthRate >= 1 ? 'Stable' : populationGrowthRate >= 0 ? 'Slowing' : 'Outflow'}
						</div>
					</div>
					<div class="bg-white/60 rounded-lg p-3">
						<div class="text-xs text-gray-500 mb-1">Vacancy Rate</div>
						<div class="text-lg font-bold text-gray-900">{((1 - networkOccupancyRate) * 100).toFixed(1)}%</div>
						<div class="text-xs {networkOccupancyRate >= 0.98 ? 'text-red-600' : networkOccupancyRate >= 0.95 ? 'text-green-600' : networkOccupancyRate >= 0.90 ? 'text-yellow-600' : 'text-orange-600'}">
							{networkOccupancyRate >= 0.98 ? 'Critical shortage' : networkOccupancyRate >= 0.95 ? 'Tight market' : networkOccupancyRate >= 0.90 ? 'Balanced' : 'Rising vacancies'}
						</div>
					</div>
					{#if true}
						{@const currentRate = getAppreciationRate() * 100}
						<div class="bg-white/60 rounded-lg p-3">
							<div class="text-xs text-gray-500 mb-1">Monthly Appreciation</div>
							<div class="text-lg font-bold {currentRate >= 0 ? 'text-green-600' : 'text-red-600'}">{currentRate >= 0 ? '+' : ''}{currentRate.toFixed(2)}%</div>
							<div class="text-xs text-gray-500">
								{currentRate >= 1 ? 'Strong growth' : currentRate >= 0 ? 'Modest growth' : currentRate >= -0.5 ? 'Slight decline' : 'Falling'}
							</div>
						</div>
					{/if}
				</div>
				
				{#if marketCondition === 'declining' || marketCondition === 'bust'}
					<div class="mt-4 p-3 bg-white/80 rounded-lg border border-amber-200">
						<div class="flex items-start gap-2">
							<AlertTriangle class="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
							<div>
								<div class="font-medium text-amber-800">Market Downturn Alert</div>
								<p class="text-sm text-amber-700 mt-1">
									Property values are {marketCondition === 'bust' ? 'falling significantly' : 'declining'}. 
									OSF provides mitigation through diversification, rental guarantees, and liquidity pools.
									Consider reviewing your portfolio exposure.
								</p>
							</div>
						</div>
					</div>
				{/if}
			</div>
			
			<!-- Financial Flows Diagram - Interactive Svelte Flow -->
			<Card.Root class="mb-8">
				<Card.Header>
					<Card.Title class="flex items-center gap-2">
						<Sparkles class="w-5 h-5 text-purple-600" />
						How Money Flows Through the Network
					</Card.Title>
					<Card.Description>
						Interactive diagram showing rental income flow through the OSF network
					</Card.Description>
				</Card.Header>
				<Card.Content>
					<MoneyFlowDiagram 
						monthlyRent={networkTotalPropertyValue * 0.004 * networkOccupancyRate}
						treasuryBalance={networkTreasury}
						yieldPercent={networkAverageYield}
						serviceFeePercent={8}
					/>
					<p class="text-xs text-gray-500 text-center mt-4">
						Property management, maintenance, legal, and other services are paid from rental income before distribution to token holders.
					</p>
				</Card.Content>
			</Card.Root>
			
			<!-- Network Participants with Avatars -->
			{#if Object.keys(poolAvatars).length > 0}
			<Card.Root class="mb-8">
				<Card.Header>
					<Card.Title class="flex items-center gap-2">
						<Users class="w-5 h-5 text-blue-600" />
						Network Participants
					</Card.Title>
					<Card.Description>Active roles in the OSF simulation</Card.Description>
				</Card.Header>
				<Card.Content>
					<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
						{#each Object.entries(poolAvatars).filter(([_, a]) => a.category === 'participant') as [role, avatar]}
							<div class="text-center group">
								<div class="relative w-20 h-20 mx-auto mb-2 rounded-xl overflow-hidden shadow-lg group-hover:shadow-xl transition-shadow">
									<img 
										src={avatar.image} 
										alt={formatRoleName(role)}
										class="w-full h-full object-cover group-hover:scale-105 transition-transform"
									/>
									{#if role === 'governor_ai'}
										<div class="absolute bottom-0 left-0 right-0 bg-blue-600/80 text-white text-xs py-0.5">
											AI
										</div>
									{/if}
								</div>
								<div class="text-sm font-medium text-gray-900 capitalize">
									{formatRoleName(role)}
								</div>
								<div class="text-xs text-gray-500 capitalize">{avatar.category}</div>
							</div>
						{/each}
					</div>
					
					<!-- Service Providers -->
					<div class="mt-6 pt-6 border-t border-gray-100">
						<h4 class="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
							<Wrench class="w-4 h-4 text-amber-600" />
							Service Providers
						</h4>
						<div class="flex flex-wrap gap-3">
							{#each Object.entries(poolAvatars).filter(([_, a]) => a.category === 'service') as [role, avatar]}
								<div class="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-2 hover:bg-gray-100 transition">
									<img 
										src={avatar.image} 
										alt={formatRoleName(role)}
										class="w-10 h-10 rounded-lg object-cover"
									/>
									<div class="text-sm font-medium text-gray-700 capitalize">
										{formatRoleName(role)}
									</div>
								</div>
							{/each}
						</div>
					</div>
				</Card.Content>
			</Card.Root>
			{/if}
			
			<!-- Two Column Layout -->
			<div class="grid md:grid-cols-2 gap-8">
				<!-- Role Balances -->
				<Card.Root>
					<Card.Header>
						<Card.Title>Your Balances by Role</Card.Title>
					</Card.Header>
					<Card.Content class="space-y-4">
						<div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
							<div class="flex items-center gap-3">
								<TrendingUp class="w-5 h-5 text-blue-600" />
								<div>
									<div class="font-medium text-gray-900">Investor</div>
									<div class="text-xs text-gray-500">{holdings.length} holdings</div>
								</div>
							</div>
							<div class="text-right">
								<div class="font-bold text-gray-900">${(balance + portfolioValue).toLocaleString()}</div>
								<div class="text-xs {totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}">
									{totalReturn >= 0 ? '+' : ''}{totalReturnPercent.toFixed(1)}%
								</div>
							</div>
						</div>
						
						<div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
							<div class="flex items-center gap-3">
								<Building class="w-5 h-5 text-cyan-600" />
								<div>
									<div class="font-medium text-gray-900">Renter</div>
									<div class="text-xs text-gray-500">{renterProperty ? 'Active lease' : 'No lease'}</div>
								</div>
							</div>
							<div class="text-right">
								<div class="font-bold text-gray-900">-${renterTotalPaid.toLocaleString()}</div>
								<div class="text-xs text-gray-500">{renterMonthsRented} months</div>
							</div>
						</div>
						
						<div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
							<div class="flex items-center gap-3">
								<Key class="w-5 h-5 text-emerald-600" />
								<div>
									<div class="font-medium text-gray-900">Tenant (Rent-to-Own)</div>
									<div class="text-xs text-gray-500">{tenantEquityPercent.toFixed(2)}% equity</div>
								</div>
							</div>
							<div class="text-right">
								<div class="font-bold text-gray-900">${tenantSavingsVsRent.toLocaleString()}</div>
								<div class="text-xs text-green-600">equity built</div>
							</div>
						</div>
						
						<div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
							<div class="flex items-center gap-3">
								<Home class="w-5 h-5 text-amber-600" />
								<div>
									<div class="font-medium text-gray-900">Homeowner</div>
									<div class="text-xs text-gray-500">${homeownerPropertyValue.toLocaleString()} property</div>
								</div>
							</div>
							<div class="text-right">
								<div class="font-bold text-gray-900">${homeownerRentalIncome.toLocaleString()}</div>
								<div class="text-xs text-gray-500">rental income</div>
							</div>
						</div>
						
						<div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
							<div class="flex items-center gap-3">
								<Wrench class="w-5 h-5 text-orange-600" />
								<div>
									<div class="font-medium text-gray-900">Service Provider</div>
									<div class="text-xs text-gray-500">{custodianManagedProperties} properties</div>
								</div>
							</div>
							<div class="text-right">
								<div class="font-bold text-gray-900">${custodianMonthlyFees.toLocaleString()}/mo</div>
								<div class="text-xs text-gray-500">fees earned</div>
							</div>
						</div>
						
						<div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
							<div class="flex items-center gap-3">
								<Landmark class="w-5 h-5 text-purple-600" />
								<div>
									<div class="font-medium text-gray-900">Foundation Partner</div>
									<div class="text-xs text-gray-500">${foundationTotalStaked.toLocaleString()} staked</div>
								</div>
							</div>
							<div class="text-right">
								<div class="font-bold text-gray-900">${foundationEarnings.toLocaleString()}</div>
								<div class="text-xs text-green-600">earnings</div>
							</div>
						</div>
					</Card.Content>
				</Card.Root>
				
				<!-- Network Events Log -->
				<Card.Root>
					<Card.Header>
						<Card.Title class="flex items-center gap-2">
							<FileText class="w-5 h-5 text-gray-600" />
							Network Activity Log
						</Card.Title>
					</Card.Header>
					<Card.Content class="p-0">
						{#if networkEvents.length === 0}
							<div class="p-8 text-center text-gray-500">
								<Play class="w-8 h-8 mx-auto mb-2 text-gray-400" />
								<p class="text-sm">Click "Simulate Month" to see financial events</p>
							</div>
						{:else}
							<div class="max-h-96 overflow-y-auto divide-y divide-gray-100">
								{#each networkEvents.slice(0, 20) as event}
									<div class="px-4 py-3 flex items-start gap-3">
										<div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 {
											event.type === 'dividend_paid' ? 'bg-green-100 text-green-600' :
											event.type === 'rent_collected' ? 'bg-blue-100 text-blue-600' :
											event.type === 'service_payment' ? 'bg-amber-100 text-amber-600' :
											event.type === 'stake_yield' ? 'bg-purple-100 text-purple-600' :
											'bg-gray-100 text-gray-600'
										}">
											{#if event.type === 'dividend_paid'}
												<DollarSign class="w-4 h-4" />
											{:else if event.type === 'rent_collected'}
												<Building class="w-4 h-4" />
											{:else if event.type === 'service_payment'}
												<Wrench class="w-4 h-4" />
											{:else if event.type === 'stake_yield'}
												<Landmark class="w-4 h-4" />
											{:else}
												<FileText class="w-4 h-4" />
											{/if}
										</div>
										<div class="flex-1 min-w-0">
											<div class="font-medium text-gray-900 text-sm">{event.description}</div>
											<div class="flex items-center gap-2 mt-0.5">
												<span class="text-xs text-gray-500">Month {event.month}</span>
												<span class="text-xs text-gray-400">•</span>
												<span class="text-xs text-gray-500">{event.fromRole} → {event.toRole}</span>
											</div>
										</div>
										{#if event.amount > 0}
											<div class="text-sm font-medium text-green-600">
												+${event.amount.toLocaleString(undefined, { maximumFractionDigits: 0 })}
											</div>
										{/if}
									</div>
								{/each}
							</div>
						{/if}
					</Card.Content>
				</Card.Root>
			</div>
			
			<!-- Simulation Note -->
			<div class="mt-8 bg-amber-50 border border-amber-200 rounded-xl p-4 text-center">
				<p class="text-sm text-amber-800">
					🎮 <strong>Unified Simulation:</strong> Click "Simulate Month" to advance all roles together. 
					Rent flows from tenants → treasury → investors. Service providers are paid from rental income.
					All transactions are connected in the network event log.
				</p>
			</div>
		</div>
		
		{:else if activeTab === 'governance'}
		<!-- Governance Section -->
		<div class="max-w-5xl mx-auto px-4 py-8">
			<div class="flex items-center justify-between mb-6">
				<div>
					<h1 class="text-2xl font-bold text-gray-900">Governance & Proposals</h1>
					<p class="text-gray-500">Vote on proposals that shape the OSF network</p>
				</div>
				<div class="text-right">
					<div class="text-sm text-gray-500">Your Voting Power</div>
					<div class="text-lg font-bold text-blue-600">{(portfolioValue / 1000).toFixed(1)}k tokens</div>
				</div>
			</div>
			
			<!-- Active Proposals -->
			<div class="grid gap-6">
				{#each proposals as proposal}
					<Card.Root class="hover:border-blue-200 transition">
						<Card.Content class="pt-6">
							<div class="flex items-start gap-6">
								<!-- Voting Panel -->
								<div class="flex flex-col items-center gap-2 p-4 bg-gray-50 rounded-lg min-w-[120px]">
									<div class="text-2xl font-bold text-gray-900">
										{Math.round((proposal.votes_for / (proposal.votes_for + proposal.votes_against)) * 100)}%
									</div>
									<div class="text-xs text-gray-500">approval</div>
									<div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
										<div 
											class="h-full bg-green-500 rounded-full" 
											style="width: {(proposal.votes_for / (proposal.votes_for + proposal.votes_against)) * 100}%"
										></div>
									</div>
									<div class="flex gap-2 mt-2 w-full">
										<Button size="sm" class="flex-1 text-xs bg-green-600 hover:bg-green-700">
											For
										</Button>
										<Button variant="outline" size="sm" class="flex-1 text-xs">
											Against
										</Button>
									</div>
								</div>
								
								<!-- Proposal Details -->
								<div class="flex-1">
									<div class="flex items-center gap-2 mb-2">
										<Badge variant="outline" class="bg-blue-50 text-blue-700 border-blue-200">
											{proposal.status}
										</Badge>
										<span class="text-sm text-gray-500">Ends in {proposal.ends_in}</span>
									</div>
									<h3 class="text-lg font-semibold text-gray-900 mb-2">{proposal.title}</h3>
									<p class="text-sm text-gray-600 mb-4">
										{#if proposal.title.includes('Melbourne')}
											Proposal to expand OSF property investments into the Melbourne metropolitan area, 
											targeting high-growth suburbs with strong rental yields.
										{:else}
											Proposal to reduce the network management fee from 0.5% to 0.4% annually, 
											improving returns for all token holders.
										{/if}
									</p>
									<div class="flex items-center gap-6 text-sm">
										<div>
											<span class="text-gray-500">For:</span>
											<span class="font-medium text-green-600 ml-1">{(proposal.votes_for / 1000).toFixed(0)}k tokens</span>
										</div>
										<div>
											<span class="text-gray-500">Against:</span>
											<span class="font-medium text-red-600 ml-1">{(proposal.votes_against / 1000).toFixed(0)}k tokens</span>
										</div>
										<div>
											<span class="text-gray-500">Quorum:</span>
											<span class="font-medium ml-1">67% required</span>
										</div>
									</div>
								</div>
							</div>
						</Card.Content>
					</Card.Root>
				{/each}
			</div>
			
			<!-- Governance Info -->
			<div class="mt-8 grid md:grid-cols-3 gap-6">
				<Card.Root>
					<Card.Content class="pt-6 text-center">
						<Vote class="w-8 h-8 text-blue-600 mx-auto mb-2" />
						<h3 class="font-medium text-gray-900 mb-1">Token-Weighted Voting</h3>
						<p class="text-sm text-gray-500">Your voting power equals your token holdings</p>
					</Card.Content>
				</Card.Root>
				<Card.Root>
					<Card.Content class="pt-6 text-center">
						<Shield class="w-8 h-8 text-green-600 mx-auto mb-2" />
						<h3 class="font-medium text-gray-900 mb-1">Transparent Governance</h3>
						<p class="text-sm text-gray-500">All votes are recorded (simulated)</p>
					</Card.Content>
				</Card.Root>
				<Card.Root>
					<Card.Content class="pt-6 text-center">
						<Users class="w-8 h-8 text-purple-600 mx-auto mb-2" />
						<h3 class="font-medium text-gray-900 mb-1">Community Driven</h3>
						<p class="text-sm text-gray-500">Any token holder can submit proposals</p>
					</Card.Content>
				</Card.Root>
			</div>
		</div>
		
		{:else if activeTab === 'leaderboard'}
		<!-- Leaderboard Section -->
		<div class="max-w-4xl mx-auto px-4 py-8">
			<div class="flex items-center justify-between mb-6">
				<div>
					<h1 class="text-2xl font-bold text-gray-900">Simulation Leaderboard</h1>
					<p class="text-gray-500">Top performers in the OSF simulation</p>
				</div>
				<div class="text-right">
					<div class="text-sm text-gray-500">Your Rank</div>
					<div class="text-lg font-bold text-amber-600">#{portfolioValue > 0 ? Math.max(1, 6 - Math.floor(portfolioValue / 20000)) : '-'}</div>
				</div>
			</div>
			
			<!-- Your Stats -->
			<Card.Root class="mb-8 border-blue-200 bg-blue-50">
				<Card.Content class="pt-6">
					<div class="flex items-center gap-4">
						<div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
							<span class="text-2xl font-bold text-blue-600">{displayName.charAt(0).toUpperCase()}</span>
						</div>
						<div class="flex-1">
							<div class="text-lg font-semibold text-gray-900">{displayName}</div>
							<div class="text-sm text-gray-600">Your simulation account</div>
						</div>
						<div class="text-right">
							<div class="text-2xl font-bold {totalReturnPercent >= 0 ? 'text-green-600' : 'text-red-600'}">
								{totalReturnPercent >= 0 ? '+' : ''}{totalReturnPercent.toFixed(1)}%
							</div>
							<div class="text-sm text-gray-500">Total Return</div>
						</div>
					</div>
				</Card.Content>
			</Card.Root>
			
			<!-- Leaderboard Table -->
			<Card.Root>
				<Card.Header>
					<Card.Title class="flex items-center gap-2">
						<Trophy class="w-5 h-5 text-amber-500" />
						Top Performers
					</Card.Title>
				</Card.Header>
				<Card.Content class="p-0">
					<div class="divide-y divide-gray-100">
						{#each leaderboard as entry, i}
							<div class="px-6 py-4 flex items-center gap-4 hover:bg-gray-50 transition">
								<div class="w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold
									{entry.rank === 1 ? 'bg-amber-100 text-amber-700' : 
									 entry.rank === 2 ? 'bg-gray-200 text-gray-700' :
									 entry.rank === 3 ? 'bg-orange-100 text-orange-700' :
									 'bg-gray-100 text-gray-500'}">
									{entry.rank}
								</div>
								<div class="flex-1">
									<div class="font-medium text-gray-900">{entry.display_name}</div>
									<div class="text-sm text-gray-500">
										{entry.rank === 1 ? '🏆 Top Investor' : 
										 entry.rank === 2 ? '🥈 Rising Star' :
										 entry.rank === 3 ? '🥉 Smart Trader' : 'Investor'}
									</div>
								</div>
								<div class="text-right">
									<div class="text-lg font-bold text-green-600">+{entry.total_return_percent.toFixed(1)}%</div>
									<div class="text-sm text-gray-500">${(100000 * (1 + entry.total_return_percent / 100)).toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
								</div>
							</div>
						{/each}
					</div>
				</Card.Content>
			</Card.Root>
			
			<!-- Achievements -->
			<div class="mt-8">
				<h2 class="text-lg font-semibold text-gray-900 mb-4">Achievements</h2>
				<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
					<Card.Root class="{holdings.length > 0 ? '' : 'opacity-50'}">
						<Card.Content class="pt-6 text-center">
							<div class="text-3xl mb-2">🏠</div>
							<div class="text-sm font-medium text-gray-900">First Investment</div>
							<div class="text-xs text-gray-500">{holdings.length > 0 ? 'Unlocked!' : 'Buy your first token'}</div>
						</Card.Content>
					</Card.Root>
					<Card.Root class="{holdings.length >= 3 ? '' : 'opacity-50'}">
						<Card.Content class="pt-6 text-center">
							<div class="text-3xl mb-2">📊</div>
							<div class="text-sm font-medium text-gray-900">Diversified</div>
							<div class="text-xs text-gray-500">{holdings.length >= 3 ? 'Unlocked!' : 'Own 3+ properties'}</div>
						</Card.Content>
					</Card.Root>
					<Card.Root class="{totalReturnPercent >= 10 ? '' : 'opacity-50'}">
						<Card.Content class="pt-6 text-center">
							<div class="text-3xl mb-2">📈</div>
							<div class="text-sm font-medium text-gray-900">Double Digits</div>
							<div class="text-xs text-gray-500">{totalReturnPercent >= 10 ? 'Unlocked!' : 'Reach 10% returns'}</div>
						</Card.Content>
					</Card.Root>
					<Card.Root class="{recurringEnabled ? '' : 'opacity-50'}">
						<Card.Content class="pt-6 text-center">
							<div class="text-3xl mb-2">🔄</div>
							<div class="text-sm font-medium text-gray-900">Auto-Investor</div>
							<div class="text-xs text-gray-500">{recurringEnabled ? 'Unlocked!' : 'Set up auto-invest'}</div>
						</Card.Content>
					</Card.Root>
				</div>
			</div>
		</div>
		
		{:else if activeTab === 'feedback'}
		<!-- Feedback Section with Community Sentiment -->
		<div class="max-w-5xl mx-auto px-4 py-8">
			<!-- Header -->
			<div class="flex items-center justify-between mb-6">
				<div>
					<h1 class="text-2xl font-bold text-gray-900">Community Feedback</h1>
					<p class="text-gray-500">Report bugs, request features, and help shape OSF</p>
				</div>
				<Button onclick={() => showFeedbackDialog = true}>
					<Plus class="w-4 h-4 mr-2" />
					Submit Feedback
				</Button>
			</div>
			
			<!-- Community Sentiment Meter -->
			{#if true}
			{@const sentiment = getSentimentDisplay(communitySentiment.score)}
			<Card.Root class="mb-6 bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
				<Card.Content class="pt-6">
					<div class="grid md:grid-cols-4 gap-6">
						<!-- Sentiment Score -->
						<div class="text-center">
							<div class="text-4xl mb-1">{sentiment.emoji}</div>
							<div class="font-semibold {sentiment.color}">{sentiment.label}</div>
							<div class="text-xs text-gray-500 mt-1">
								{communitySentiment.trend === 'rising' ? '📈 Improving' : 
								 communitySentiment.trend === 'falling' ? '📉 Declining' : '➡️ Stable'}
							</div>
						</div>
						
						<!-- Sentiment Bar -->
						<div class="md:col-span-2">
							<div class="text-sm font-medium text-gray-700 mb-2">Community Mood</div>
							<div class="h-4 bg-gradient-to-r from-red-300 via-yellow-300 to-green-300 rounded-full relative">
								<div 
									class="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white border-2 border-gray-700 rounded-full shadow-lg transition-all duration-500"
									style="left: calc({(communitySentiment.score + 1) / 2 * 100}% - 8px)"
								></div>
							</div>
							<div class="flex justify-between text-xs text-gray-500 mt-1">
								<span>Anxious</span>
								<span>Neutral</span>
								<span>Positive</span>
							</div>
						</div>
						
						<!-- Stats -->
						<div class="space-y-2">
							<div class="flex justify-between text-sm">
								<span class="text-gray-600">Resolution Rate</span>
								<span class="font-medium">{(communitySentiment.resolutionRate * 100).toFixed(0)}%</span>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-600">Total Feedback</span>
								<span class="font-medium">{feedbackItems.length}</span>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-600">Open Issues</span>
								<span class="font-medium">{feedbackItems.filter(f => f.status === 'open').length}</span>
							</div>
						</div>
					</div>
				</Card.Content>
			</Card.Root>
			{/if}
			
			<!-- Filters -->
			<div class="flex flex-wrap gap-3 mb-6">
				<div class="flex items-center gap-2 bg-white rounded-lg border border-gray-200 p-1">
					<button 
						class="px-3 py-1.5 text-sm rounded-md transition {feedbackFilter === 'all' ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-100'}"
						onclick={() => feedbackFilter = 'all'}
					>
						All
					</button>
					<button 
						class="px-3 py-1.5 text-sm rounded-md transition flex items-center gap-1 {feedbackFilter === 'bug' ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-100'}"
						onclick={() => feedbackFilter = 'bug'}
					>
						<Bug class="w-3.5 h-3.5" />
						Bugs
					</button>
					<button 
						class="px-3 py-1.5 text-sm rounded-md transition flex items-center gap-1 {feedbackFilter === 'enhancement' ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-100'}"
						onclick={() => feedbackFilter = 'enhancement'}
					>
						<Lightbulb class="w-3.5 h-3.5" />
						Features
					</button>
					<button 
						class="px-3 py-1.5 text-sm rounded-md transition flex items-center gap-1 {feedbackFilter === 'question' ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-100'}"
						onclick={() => feedbackFilter = 'question'}
					>
						<MessageSquare class="w-3.5 h-3.5" />
						Questions
					</button>
				</div>
				
				<select 
					class="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-600"
					bind:value={feedbackSort}
				>
					<option value="upvotes">Most Voted</option>
					<option value="newest">Newest First</option>
					<option value="priority">By Priority</option>
				</select>
			</div>
			
			<!-- Feedback List -->
			<div class="space-y-4">
				{#each getFilteredFeedback() as feedback}
					<Card.Root class="hover:border-gray-300 transition cursor-pointer">
						<Card.Content class="pt-6">
							<div class="flex gap-4">
								<!-- Voting -->
								<div class="flex flex-col items-center gap-1">
									<button 
										class="p-1 rounded hover:bg-gray-100 transition {feedback.user_vote === 1 ? 'text-green-600' : 'text-gray-400'}"
										onclick={() => handleVoteFeedback(feedback.id, 1)}
									>
										<ThumbsUp class="w-5 h-5" />
									</button>
									<span class="font-medium text-gray-900">{feedback.upvotes - feedback.downvotes}</span>
									<button 
										class="p-1 rounded hover:bg-gray-100 transition {feedback.user_vote === -1 ? 'text-red-600' : 'text-gray-400'}"
										onclick={() => handleVoteFeedback(feedback.id, -1)}
									>
										<ThumbsDown class="w-5 h-5" />
									</button>
								</div>
								
								<!-- Content -->
								<button type="button" class="flex-1 text-left" onclick={() => openFeedbackDetail(feedback)}>
									<div class="flex items-start gap-2 mb-2">
										{#if feedback.feedback_type === 'bug'}
											<Bug class="w-4 h-4 text-red-500 mt-1" />
										{:else if feedback.feedback_type === 'enhancement'}
											<Lightbulb class="w-4 h-4 text-amber-500 mt-1" />
										{:else}
											<MessageSquare class="w-4 h-4 text-blue-500 mt-1" />
										{/if}
										<div class="flex-1">
											<h3 class="font-medium text-gray-900">{feedback.title}</h3>
											<p class="text-sm text-gray-500 mt-1 line-clamp-2">{feedback.description}</p>
										</div>
									</div>
									
									<!-- Badges & Meta -->
									<div class="flex flex-wrap items-center gap-2 mt-3">
										<Badge variant="outline" class={getStatusColor(feedback.status)}>
											{feedback.status.replace('_', ' ')}
										</Badge>
										{#if feedback.ai_priority}
											<Badge variant="outline" class={getPriorityColor(feedback.ai_priority)}>
												{feedback.ai_priority}
											</Badge>
										{/if}
										{#if feedback.ai_category}
											<span class="text-xs text-gray-400 flex items-center gap-1">
												<Sparkles class="w-3 h-3" />
												{feedback.ai_category}
											</span>
										{/if}
										<span class="text-xs text-gray-400">by {feedback.author_name}</span>
										{#if (feedback as any).generated}
											<Badge variant="outline" class="text-xs bg-purple-50 text-purple-600 border-purple-200">
												NPC
											</Badge>
										{/if}
										{#if (feedback as any).market_context}
											<span class="text-xs px-1.5 py-0.5 rounded {
												(feedback as any).market_context === 'boom' ? 'bg-green-100 text-green-700' :
												(feedback as any).market_context === 'bust' ? 'bg-red-100 text-red-700' :
												'bg-gray-100 text-gray-600'
											}">
												{(feedback as any).market_context}
											</span>
										{/if}
										<span class="text-xs text-gray-400">•</span>
										<span class="text-xs text-gray-400">{feedback.created_at}</span>
										<span class="text-xs text-gray-400">•</span>
										<span class="text-xs text-gray-400 flex items-center gap-1">
											<MessageSquare class="w-3 h-3" />
											{feedback.comment_count}
										</span>
									</div>
									
									<!-- AI Summary -->
									{#if feedback.ai_summary}
										<div class="mt-3 p-2 bg-blue-50 rounded-lg border border-blue-100">
											<div class="flex items-center gap-1 text-xs text-blue-600 mb-1">
												<Sparkles class="w-3 h-3" />
												AI Summary
											</div>
											<p class="text-sm text-blue-800">{feedback.ai_summary}</p>
										</div>
									{/if}
								</button>
							</div>
						</Card.Content>
					</Card.Root>
				{/each}
			</div>
			
			<!-- Empty State -->
			{#if getFilteredFeedback().length === 0}
				<Card.Root>
					<Card.Content class="py-12 text-center">
						<div class="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
							<MessageSquare class="w-6 h-6 text-gray-400" />
						</div>
						<h3 class="font-medium text-gray-900 mb-1">No feedback yet</h3>
						<p class="text-sm text-gray-500 mb-4">Be the first to submit feedback in this category.</p>
						<Button onclick={() => showFeedbackDialog = true}>
							<Plus class="w-4 h-4 mr-2" />
							Submit Feedback
						</Button>
					</Card.Content>
				</Card.Root>
			{/if}
		</div>
		
		{:else if activeTab === 'ledger'}
		<!-- Ledger / Blockchain Log Section -->
		<div class="max-w-6xl mx-auto px-4 py-8">
			<div class="flex items-center justify-between mb-6">
				<div>
					<h2 class="text-2xl font-bold text-gray-900">Network Ledger</h2>
					<p class="text-gray-500">Immutable record of all network transactions</p>
				</div>
				<div class="flex items-center gap-3">
					<Badge variant="outline" class="bg-green-50 text-green-700 border-green-200">
						<span class="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
						Live
					</Badge>
					<Badge variant="outline">{networkEvents.length} transactions</Badge>
				</div>
			</div>
			
			<!-- Ledger Stats -->
			<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
				<Card.Root>
					<Card.Content class="pt-4">
						<div class="text-2xl font-bold text-gray-900">{networkEvents.length}</div>
						<div class="text-sm text-gray-500">Total Transactions</div>
					</Card.Content>
				</Card.Root>
				<Card.Root>
					<Card.Content class="pt-4">
						<div class="text-2xl font-bold text-blue-600">${networkEvents.filter(e => e.amount > 0).reduce((sum, e) => sum + e.amount, 0).toLocaleString()}</div>
						<div class="text-sm text-gray-500">Total Volume</div>
					</Card.Content>
				</Card.Root>
				<Card.Root>
					<Card.Content class="pt-4">
						<div class="text-2xl font-bold text-purple-600">{new Set(networkEvents.map(e => e.type)).size}</div>
						<div class="text-sm text-gray-500">Transaction Types</div>
					</Card.Content>
				</Card.Root>
				<Card.Root>
					<Card.Content class="pt-4">
						<div class="text-2xl font-bold text-green-600">Month {networkMonth}</div>
						<div class="text-sm text-gray-500">Current Block</div>
					</Card.Content>
				</Card.Root>
			</div>
			
			<!-- Ledger Table -->
			<Card.Root>
				<Card.Header class="border-b">
					<div class="flex items-center justify-between">
						<Card.Title class="flex items-center gap-2">
							<FileText class="w-5 h-5 text-gray-600" />
							Transaction Log
						</Card.Title>
						<div class="flex items-center gap-2 text-xs text-gray-500">
							<span class="font-mono bg-gray-100 px-2 py-1 rounded">Chain: OSF-Simulation</span>
						</div>
					</div>
				</Card.Header>
				<Card.Content class="p-0">
					{#if networkEvents.length === 0}
						<div class="text-center py-16">
							<FileText class="w-12 h-12 mx-auto mb-3 text-gray-300" />
							<p class="text-gray-500 mb-2">No transactions yet</p>
							<p class="text-sm text-gray-400">Simulate network activity to see transactions appear here</p>
						</div>
					{:else}
						<div class="overflow-x-auto">
							<table class="w-full text-sm">
								<thead class="bg-gray-50 border-b">
									<tr>
										<th class="px-4 py-3 text-left font-medium text-gray-500">Block</th>
										<th class="px-4 py-3 text-left font-medium text-gray-500">Tx Hash</th>
										<th class="px-4 py-3 text-left font-medium text-gray-500">Type</th>
										<th class="px-4 py-3 text-left font-medium text-gray-500">From</th>
										<th class="px-4 py-3 text-left font-medium text-gray-500">To</th>
										<th class="px-4 py-3 text-left font-medium text-gray-500">Description</th>
										<th class="px-4 py-3 text-right font-medium text-gray-500">Amount</th>
									</tr>
								</thead>
								<tbody class="divide-y divide-gray-100">
									{#each networkEvents as event, i}
										{@const txHash = `0x${event.id.toString(16).padStart(8, '0')}...${(event.id % 10000).toString(16).padStart(4, '0')}`}
										<tr class="hover:bg-gray-50 transition">
											<td class="px-4 py-3">
												<span class="font-mono text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
													#{event.month}
												</span>
											</td>
											<td class="px-4 py-3">
												<span class="font-mono text-xs text-gray-600" title={event.id.toString()}>
													{txHash}
												</span>
											</td>
											<td class="px-4 py-3">
												<Badge variant="outline" class="text-xs {
													event.type === 'rent_collected' ? 'bg-green-50 text-green-700 border-green-200' :
													event.type === 'dividend_paid' ? 'bg-blue-50 text-blue-700 border-blue-200' :
													event.type === 'token_trade' ? 'bg-purple-50 text-purple-700 border-purple-200' :
													event.type === 'equity_access' ? 'bg-amber-50 text-amber-700 border-amber-200' :
													event.type === 'service_payment' ? 'bg-orange-50 text-orange-700 border-orange-200' :
													event.type === 'governance_vote' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' :
													event.type === 'property_added' ? 'bg-teal-50 text-teal-700 border-teal-200' :
													'bg-gray-50 text-gray-700 border-gray-200'
												}">
													{event.type.replace(/_/g, ' ')}
												</Badge>
											</td>
											<td class="px-4 py-3">
												<span class="text-gray-700">{event.fromRole}</span>
											</td>
											<td class="px-4 py-3">
												<span class="text-gray-700">{event.toRole}</span>
											</td>
											<td class="px-4 py-3 max-w-xs truncate" title={event.description}>
												<span class="text-gray-600">{event.description}</span>
											</td>
											<td class="px-4 py-3 text-right">
												{#if event.amount > 0}
													<span class="font-medium text-green-600">
														+${event.amount.toLocaleString()}
													</span>
												{:else if event.amount < 0}
													<span class="font-medium text-red-600">
														-${Math.abs(event.amount).toLocaleString()}
													</span>
												{:else}
													<span class="text-gray-400">—</span>
												{/if}
											</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					{/if}
				</Card.Content>
			</Card.Root>
			
			<!-- Export / Technical Info -->
			<div class="mt-6 flex items-center justify-between text-sm text-gray-500">
				<div class="flex items-center gap-4">
					<span class="flex items-center gap-1">
						<CheckCircle class="w-4 h-4 text-green-500" />
						All transactions verified
					</span>
					<span class="font-mono bg-gray-100 px-2 py-1 rounded text-xs">
						Genesis: Block #0
					</span>
				</div>
				<div class="text-xs">
					Simulated blockchain ledger for demonstration purposes
				</div>
			</div>
		</div>
		
		{:else if activeTab === 'thinking'}
		<!-- AI Thinking Log - Marathon Agent "Thought Signatures" -->
		<div class="max-w-6xl mx-auto px-4 py-8">
			<div class="flex items-center justify-between mb-6">
				<div>
					<h2 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
						<Sparkles class="w-6 h-6 text-purple-600" />
						AI Thinking Log
					</h2>
					<p class="text-gray-600 mt-1">Real-time visibility into NPC decisions and autonomous agent reasoning</p>
				</div>
				<div class="flex items-center gap-3">
					<!-- Session Stats -->
					<div class="bg-purple-50 border border-purple-200 rounded-lg px-4 py-2 text-sm">
						<div class="text-purple-600 font-medium">Session: {formatElapsed(sessionElapsed)}</div>
						<div class="text-purple-500 text-xs">{totalSessionMonths} months simulated</div>
					</div>
					
					<!-- Marathon Mode Status -->
					{#if marathonMode}
						<div class="bg-amber-50 border border-amber-200 rounded-lg px-4 py-2 text-sm">
							<div class="text-amber-700 font-medium flex items-center gap-1">
								<Zap class="w-4 h-4" />
								Marathon: {marathonProgress.toFixed(1)}%
							</div>
							<div class="text-amber-600 text-xs">
								{marathonPaused ? 'Paused' : `Running for ${formatElapsed(marathonElapsed)}`}
							</div>
						</div>
					{/if}
				</div>
			</div>
			
			<!-- Marathon Mode Banner -->
			<div class="mb-6 p-4 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl text-white">
				<div class="flex items-center justify-between">
					<div>
						<h3 class="font-bold flex items-center gap-2">
							<Zap class="w-5 h-5" />
							Marathon Agent Mode
						</h3>
						<p class="text-purple-200 text-sm mt-1">
							Autonomous simulation spanning hours — 11 NPCs making decisions with visible reasoning
						</p>
					</div>
					<div class="flex items-center gap-3">
						<div class="text-right text-sm">
							<div class="text-purple-200">Target</div>
							<div class="font-bold">{marathonTargetMonths} months</div>
						</div>
						<div class="text-right text-sm">
							<div class="text-purple-200">Speed</div>
							<div class="font-bold">{(marathonInterval / 1000).toFixed(1)}s/tick</div>
						</div>
						{#if !marathonMode}
							<Button onclick={startMarathon} class="bg-white text-purple-600 hover:bg-purple-50">
								<Zap class="w-4 h-4 mr-2" />
								Start Marathon
							</Button>
						{:else}
							<Button onclick={stopMarathon} variant="outline" class="text-white border-white hover:bg-white/10">
								Stop
							</Button>
						{/if}
					</div>
				</div>
				
				<!-- Progress Bar -->
				{#if marathonMode}
					<div class="mt-4">
						<div class="flex justify-between text-xs text-purple-200 mb-1">
							<span>Progress: Month {networkMonth} of {marathonTargetMonths}</span>
							<span>{marathonProgress.toFixed(1)}%</span>
						</div>
						<div class="h-2 bg-purple-400/30 rounded-full overflow-hidden">
							<div 
								class="h-full bg-white rounded-full transition-all duration-500"
								style="width: {marathonProgress}%"
							></div>
						</div>
					</div>
				{/if}
			</div>
			
			<!-- NPC Performance Summary (Self-Correction Tracking) -->
			<div class="mb-6">
				<h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
					<Users class="w-5 h-5 text-gray-600" />
					NPC Performance (Self-Correction)
				</h3>
				<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
					{#each Object.entries(npcPerformance).slice(0, 6) as [name, perf]}
						{@const successRate = perf.decisions > 0 ? (perf.successes / perf.decisions * 100) : 0}
						<div class="bg-white border border-gray-200 rounded-lg p-3">
							<div class="font-medium text-gray-900 text-sm truncate">{name}</div>
							<div class="text-xs text-gray-500 mt-1">{perf.decisions} decisions</div>
							<div class="flex items-center gap-2 mt-2">
								<div class="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
									<div 
										class="h-full rounded-full {successRate >= 60 ? 'bg-green-500' : successRate >= 40 ? 'bg-amber-500' : 'bg-red-500'}"
										style="width: {successRate}%"
									></div>
								</div>
								<span class="text-xs font-medium {successRate >= 60 ? 'text-green-600' : successRate >= 40 ? 'text-amber-600' : 'text-red-600'}">
									{successRate.toFixed(0)}%
								</span>
							</div>
							{#if perf.strategyAdjustments > 0}
								<div class="text-xs text-purple-600 mt-1 flex items-center gap-1">
									<RefreshCw class="w-3 h-3" />
									{perf.strategyAdjustments} adjustments
								</div>
							{/if}
						</div>
					{/each}
				</div>
			</div>
			
			<!-- Thinking Log Stream -->
			<div class="bg-white border border-gray-200 rounded-xl overflow-hidden">
				<div class="bg-gray-50 border-b border-gray-200 px-4 py-3 flex items-center justify-between">
					<h3 class="font-semibold text-gray-900">Thought Stream</h3>
					<div class="text-sm text-gray-500">{aiThinkingLog.length} entries</div>
				</div>
				
				<div class="max-h-[500px] overflow-y-auto">
					{#if aiThinkingLog.length === 0}
						<div class="p-8 text-center text-gray-500">
							<Sparkles class="w-12 h-12 mx-auto mb-3 text-gray-300" />
							<p class="font-medium">No AI thoughts yet</p>
							<p class="text-sm mt-1">Run the simulation to see NPC reasoning</p>
							<Button onclick={simulateNetworkMonth} class="mt-4">
								<Play class="w-4 h-4 mr-2" />
								Simulate Month
							</Button>
						</div>
					{:else}
						<div class="divide-y divide-gray-100">
							{#each aiThinkingLog as thought}
								<div class="px-4 py-3 hover:bg-gray-50 transition">
									<div class="flex items-start gap-3">
										<!-- Level Icon -->
										<div class="mt-0.5">
											{#if thought.level === 'observation'}
												<div class="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center">
													<Eye class="w-3.5 h-3.5 text-blue-600" />
												</div>
											{:else if thought.level === 'analysis'}
												<div class="w-6 h-6 rounded-full bg-purple-100 flex items-center justify-center">
													<Target class="w-3.5 h-3.5 text-purple-600" />
												</div>
											{:else if thought.level === 'decision'}
												<div class="w-6 h-6 rounded-full bg-amber-100 flex items-center justify-center">
													<Zap class="w-3.5 h-3.5 text-amber-600" />
												</div>
											{:else if thought.level === 'action'}
												<div class="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center">
													<Play class="w-3.5 h-3.5 text-green-600" />
												</div>
											{:else if thought.level === 'reflection'}
												<div class="w-6 h-6 rounded-full bg-indigo-100 flex items-center justify-center">
													<RefreshCw class="w-3.5 h-3.5 text-indigo-600" />
												</div>
											{/if}
										</div>
										
										<!-- Content -->
										<div class="flex-1 min-w-0">
											<div class="flex items-center gap-2 flex-wrap">
												<span class="font-medium text-gray-900">{thought.agent}</span>
												<Badge variant="outline" class="text-xs capitalize">{thought.level}</Badge>
												<span class="text-xs text-gray-400">Month {thought.month}</span>
												{#if thought.confidence}
													<span class="text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-600">
														{thought.confidence}% confidence
													</span>
												{/if}
											</div>
											<p class="text-gray-700 text-sm mt-1">{thought.thought}</p>
										</div>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			</div>
			
			<!-- Marathon Agent Explanation -->
			<div class="mt-6 bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-xl p-6">
				<h3 class="font-bold text-purple-900 flex items-center gap-2">
					<Sparkles class="w-5 h-5" />
					Marathon Agent Architecture
				</h3>
				<p class="text-purple-800 text-sm mt-2">
					This simulation implements the <strong>Marathon Agent</strong> pattern from the Gemini 3 Hackathon: 
					autonomous systems for tasks spanning hours or days.
				</p>
				<div class="grid md:grid-cols-3 gap-4 mt-4">
					<div class="bg-white/60 rounded-lg p-4">
						<div class="font-medium text-purple-900">Thought Signatures</div>
						<p class="text-sm text-purple-700 mt-1">
							Each NPC decision follows: Observation → Analysis → Decision → Action → Reflection
						</p>
					</div>
					<div class="bg-white/60 rounded-lg p-4">
						<div class="font-medium text-purple-900">Self-Correction</div>
						<p class="text-sm text-purple-700 mt-1">
							NPCs adjust risk tolerance based on past performance without human supervision
						</p>
					</div>
					<div class="bg-white/60 rounded-lg p-4">
						<div class="font-medium text-purple-900">Multi-Step Continuity</div>
						<p class="text-sm text-purple-700 mt-1">
							State persists across 120+ months of autonomous simulation in marathon mode
						</p>
					</div>
				</div>
			</div>
		</div>
		
		{:else if activeTab === 'health'}
		<!-- Network Health & Self-Healing Dashboard -->
		<div class="max-w-6xl mx-auto px-4 py-8">
			<div class="flex items-center justify-between mb-6">
				<div>
					<h2 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
						<Activity class="w-6 h-6 text-green-600" />
						Network Health & Self-Healing
					</h2>
					<p class="text-gray-600 mt-1">Autonomous detection and recovery from network stress</p>
				</div>
				<div class="flex items-center gap-3">
					<!-- Overall Health Status -->
					<div class="px-4 py-2 rounded-lg font-medium flex items-center gap-2
						{overallHealthStatus === 'healthy' ? 'bg-green-100 text-green-800 border border-green-200' :
						 overallHealthStatus === 'warning' ? 'bg-yellow-100 text-yellow-800 border border-yellow-200' :
						 'bg-red-100 text-red-800 border border-red-200'}">
						{#if overallHealthStatus === 'healthy'}
							<CheckCircle class="w-5 h-5" />
						{:else if overallHealthStatus === 'warning'}
							<AlertTriangle class="w-5 h-5" />
						{:else}
							<AlertCircle class="w-5 h-5" />
						{/if}
						{overallHealthStatus.toUpperCase()}
					</div>
				</div>
			</div>
			
			<!-- Health Metrics Grid -->
			<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
				<div class="bg-white border border-gray-200 rounded-lg p-4">
					<div class="text-xs text-gray-500 mb-1">Liquidity Ratio</div>
					<div class="text-2xl font-bold {networkHealth.liquidityRatio >= 0.8 ? 'text-green-600' : networkHealth.liquidityRatio >= 0.5 ? 'text-yellow-600' : 'text-red-600'}">
						{(networkHealth.liquidityRatio * 100).toFixed(0)}%
					</div>
					<div class="text-xs text-gray-400 mt-1">Orders filled</div>
				</div>
				<div class="bg-white border border-gray-200 rounded-lg p-4">
					<div class="text-xs text-gray-500 mb-1">Exit Queue</div>
					<div class="text-2xl font-bold {exitQueue.filter(e => e.status === 'pending').length <= 5 ? 'text-green-600' : exitQueue.filter(e => e.status === 'pending').length <= 10 ? 'text-yellow-600' : 'text-red-600'}">
						{exitQueue.filter(e => e.status === 'pending').length}
					</div>
					<div class="text-xs text-gray-400 mt-1">Sellers waiting</div>
				</div>
				<!-- SUPPLY-SIDE: Buyer Waitlist -->
				<div class="bg-white border border-gray-200 rounded-lg p-4">
					<div class="text-xs text-gray-500 mb-1">Buyer Waitlist</div>
					<div class="text-2xl font-bold {buyerWaitlist.length <= 5 ? 'text-green-600' : buyerWaitlist.length <= 15 ? 'text-blue-600' : 'text-purple-600'}">
						{buyerWaitlist.length}
					</div>
					<div class="text-xs text-gray-400 mt-1">Investors waiting</div>
				</div>
				<!-- SUPPLY-SIDE: Rental Waitlist -->
				<div class="bg-white border border-gray-200 rounded-lg p-4">
					<div class="text-xs text-gray-500 mb-1">Rental Waitlist</div>
					<div class="text-2xl font-bold {rentalWaitlist.length <= 3 ? 'text-green-600' : rentalWaitlist.length <= 8 ? 'text-blue-600' : 'text-purple-600'}">
						{rentalWaitlist.length}
					</div>
					<div class="text-xs text-gray-400 mt-1">Renters waiting</div>
				</div>
				<div class="bg-white border border-gray-200 rounded-lg p-4">
					<div class="text-xs text-gray-500 mb-1">Trade Failures</div>
					<div class="text-2xl font-bold {networkHealth.tradeFailureRate <= 0.15 ? 'text-green-600' : networkHealth.tradeFailureRate <= 0.30 ? 'text-yellow-600' : 'text-red-600'}">
						{(networkHealth.tradeFailureRate * 100).toFixed(0)}%
					</div>
					<div class="text-xs text-gray-400 mt-1">Failed orders</div>
				</div>
				<div class="bg-white border border-gray-200 rounded-lg p-4">
					<div class="text-xs text-gray-500 mb-1">Rent Collection</div>
					<div class="text-2xl font-bold {networkHealth.rentCollectionRate >= 0.98 ? 'text-green-600' : networkHealth.rentCollectionRate >= 0.95 ? 'text-yellow-600' : 'text-red-600'}">
						{(networkHealth.rentCollectionRate * 100).toFixed(0)}%
					</div>
					<div class="text-xs text-gray-400 mt-1">On-time payments</div>
				</div>
				<div class="bg-white border border-gray-200 rounded-lg p-4">
					<div class="text-xs text-gray-500 mb-1">Occupancy</div>
					<div class="text-2xl font-bold {networkOccupancyRate >= 0.95 ? 'text-green-600' : networkOccupancyRate >= 0.85 ? 'text-yellow-600' : 'text-red-600'}">
						{(networkOccupancyRate * 100).toFixed(0)}%
					</div>
					<div class="text-xs text-gray-400 mt-1">Properties leased</div>
				</div>
				<div class="bg-white border border-gray-200 rounded-lg p-4">
					<div class="text-xs text-gray-500 mb-1">Maintenance</div>
					<div class="text-2xl font-bold {networkHealth.maintenanceBacklog <= 5 ? 'text-green-600' : networkHealth.maintenanceBacklog <= 15 ? 'text-yellow-600' : 'text-red-600'}">
						{networkHealth.maintenanceBacklog}
					</div>
					<div class="text-xs text-gray-400 mt-1">Items pending</div>
				</div>
			</div>
			
			<!-- Liquidity Pool Status -->
			<div class="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6 mb-8">
				<div class="flex items-center justify-between mb-4">
					<div class="flex items-center gap-3">
						<div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
							<PiggyBank class="w-6 h-6 text-blue-600" />
						</div>
						<div>
							<h3 class="font-semibold text-gray-900">Liquidity Pool (Stability Fund)</h3>
							<p class="text-sm text-gray-600">Emergency fund for absorbing distressed exits</p>
						</div>
					</div>
					<div class="text-right">
						<div class="text-2xl font-bold text-blue-600">${liquidityPool.balance.toLocaleString()}</div>
						<div class="text-sm text-gray-500">Available</div>
					</div>
				</div>
				
				<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
					<div class="bg-white/60 rounded-lg p-3">
						<div class="text-xs text-gray-500">Floor Bid Price</div>
						<div class="text-lg font-bold text-gray-900">${liquidityPool.floorBidPrice.toFixed(2)}</div>
						<div class="text-xs text-blue-600">{((1 - liquidityPool.floorBidPrice) * 100).toFixed(0)}% below NAV</div>
					</div>
					<div class="bg-white/60 rounded-lg p-3">
						<div class="text-xs text-gray-500">Total Deployed</div>
						<div class="text-lg font-bold text-gray-900">${liquidityPool.totalDeployed.toLocaleString()}</div>
						<div class="text-xs text-gray-500">Lifetime</div>
					</div>
					<div class="bg-white/60 rounded-lg p-3">
						<div class="text-xs text-gray-500">Tokens Held</div>
						<div class="text-lg font-bold text-gray-900">{liquidityPool.tokensHeld.toLocaleString()}</div>
						<div class="text-xs text-gray-500">From exits absorbed</div>
					</div>
					<div class="bg-white/60 rounded-lg p-3">
						<div class="text-xs text-gray-500">This Month</div>
						<div class="text-lg font-bold text-gray-900">{liquidityPool.deploymentsThisMonth}</div>
						<div class="text-xs text-gray-500">Deployments</div>
					</div>
				</div>
			</div>
			
			<!-- Exit Queue -->
			{#if exitQueue.length > 0}
				<div class="bg-white border border-gray-200 rounded-xl overflow-hidden mb-8">
					<div class="bg-gray-50 border-b border-gray-200 px-4 py-3 flex items-center justify-between">
						<h3 class="font-semibold text-gray-900 flex items-center gap-2">
							<LogOut class="w-5 h-5 text-gray-600" />
							Exit Queue
						</h3>
						<div class="text-sm text-gray-500">
							{exitQueue.filter(e => e.status === 'pending').length} pending, 
							{exitQueue.filter(e => e.status === 'matched' || e.status === 'filled').length} resolved
						</div>
					</div>
					<div class="divide-y divide-gray-100 max-h-64 overflow-y-auto">
						{#each exitQueue.slice(0, 10) as exit}
							<div class="px-4 py-3 flex items-center justify-between hover:bg-gray-50">
								<div class="flex items-center gap-3">
									<div class="w-8 h-8 rounded-full flex items-center justify-center
										{exit.status === 'pending' ? 'bg-yellow-100 text-yellow-600' :
										 exit.status === 'matched' ? 'bg-blue-100 text-blue-600' :
										 exit.status === 'partial' ? 'bg-purple-100 text-purple-600' :
										 'bg-green-100 text-green-600'}">
										{#if exit.status === 'pending'}
											<Clock class="w-4 h-4" />
										{:else if exit.status === 'matched'}
											<Handshake class="w-4 h-4" />
										{:else if exit.status === 'partial'}
											<ArrowRightLeft class="w-4 h-4" />
										{:else}
											<CheckCircle class="w-4 h-4" />
										{/if}
									</div>
									<div>
										<div class="font-medium text-gray-900">{exit.seller}</div>
										<div class="text-xs text-gray-500">{exit.propertyAddress.split(',')[0]}</div>
									</div>
								</div>
								<div class="text-right">
									<div class="font-medium text-gray-900">{exit.tokensForSale.toFixed(0)} tokens</div>
									<div class="text-xs text-gray-500">@ ${exit.askPrice.toFixed(2)} ({((1 - exit.askPrice) * 100).toFixed(0)}% discount)</div>
								</div>
								<div class="text-right">
									<Badge variant="outline" class="
										{exit.status === 'pending' ? 'text-yellow-600 border-yellow-300' :
										 exit.status === 'matched' ? 'text-blue-600 border-blue-300' :
										 exit.status === 'partial' ? 'text-purple-600 border-purple-300' :
										 'text-green-600 border-green-300'}">
										{exit.status}
									</Badge>
									{#if exit.matchedBuyer}
										<div class="text-xs text-gray-500 mt-1">→ {exit.matchedBuyer}</div>
									{/if}
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/if}
			
			<!-- SUPPLY SHORTAGE: Buyer & Rental Waitlists -->
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
				<!-- Investor Waitlist -->
				{#if buyerWaitlist.length > 0}
					<div class="bg-white border border-blue-200 rounded-xl overflow-hidden">
						<div class="bg-blue-50 border-b border-blue-200 px-4 py-3 flex items-center justify-between">
							<h3 class="font-semibold text-blue-900 flex items-center gap-2">
								<TrendingUp class="w-5 h-5 text-blue-600" />
								Investor Waitlist
							</h3>
							<div class="text-sm text-blue-600">
								${(buyerWaitlist.reduce((sum, b) => sum + b.desiredAmount, 0) / 1000).toFixed(0)}K waiting
							</div>
						</div>
						<div class="divide-y divide-blue-100 max-h-48 overflow-y-auto">
							{#each buyerWaitlist.slice(0, 8) as buyer}
								<div class="px-4 py-2 flex items-center justify-between hover:bg-blue-50/50">
									<div>
										<div class="font-medium text-gray-900 text-sm">{buyer.buyer}</div>
										<div class="text-xs text-gray-500">Waiting {networkMonth - buyer.waitingSince} months</div>
									</div>
									<div class="text-right">
										<div class="font-medium text-blue-600">${buyer.desiredAmount.toLocaleString()}</div>
										{#if buyer.priority === 'premium'}
											<Badge variant="outline" class="text-purple-600 border-purple-300 text-xs">Premium</Badge>
										{/if}
									</div>
								</div>
							{/each}
						</div>
						<div class="bg-blue-50/50 px-4 py-2 text-xs text-blue-600 text-center">
							Supply shortage: Consider listing more properties
						</div>
					</div>
				{:else}
					<div class="bg-gray-50 border border-gray-200 rounded-xl p-6 text-center">
						<TrendingUp class="w-8 h-8 mx-auto mb-2 text-gray-300" />
						<p class="text-sm text-gray-500">No investor waitlist</p>
						<p class="text-xs text-gray-400">Supply meets demand</p>
					</div>
				{/if}
				
				<!-- Rental Waitlist -->
				{#if rentalWaitlist.length > 0}
					<div class="bg-white border border-purple-200 rounded-xl overflow-hidden">
						<div class="bg-purple-50 border-b border-purple-200 px-4 py-3 flex items-center justify-between">
							<h3 class="font-semibold text-purple-900 flex items-center gap-2">
								<Home class="w-5 h-5 text-purple-600" />
								Rental Waitlist
							</h3>
							<div class="text-sm text-purple-600">
								{rentalWaitlist.length} renters waiting
							</div>
						</div>
						<div class="divide-y divide-purple-100 max-h-48 overflow-y-auto">
							{#each rentalWaitlist.slice(0, 8) as renter}
								<div class="px-4 py-2 flex items-center justify-between hover:bg-purple-50/50">
									<div>
										<div class="font-medium text-gray-900 text-sm">{renter.renter}</div>
										<div class="text-xs text-gray-500">
											{renter.preferredSuburb || 'Any suburb'} • Waiting {networkMonth - renter.waitingSince} months
										</div>
									</div>
									<div class="text-right">
										<div class="font-medium text-purple-600">${renter.maxRent.toFixed(0)}/wk max</div>
									</div>
								</div>
							{/each}
						</div>
						<div class="bg-purple-50/50 px-4 py-2 text-xs text-purple-600 text-center">
							Rental shortage: Low vacancy rate ({(networkHealth.rentalVacancyRate * 100).toFixed(1)}%)
						</div>
					</div>
				{:else}
					<div class="bg-gray-50 border border-gray-200 rounded-xl p-6 text-center">
						<Home class="w-8 h-8 mx-auto mb-2 text-gray-300" />
						<p class="text-sm text-gray-500">No rental waitlist</p>
						<p class="text-xs text-gray-400">Vacancy rate: {(networkHealth.rentalVacancyRate * 100).toFixed(1)}%</p>
					</div>
				{/if}
			</div>
			
			<!-- Active Healing Strategies -->
			<div class="bg-white border border-gray-200 rounded-xl overflow-hidden mb-8">
				<div class="bg-gray-50 border-b border-gray-200 px-4 py-3 flex items-center justify-between">
					<h3 class="font-semibold text-gray-900 flex items-center gap-2">
						<Heart class="w-5 h-5 text-red-500" />
						Self-Healing Strategies
					</h3>
					<div class="text-sm text-gray-500">
						{activeStrategies.filter(s => s.status === 'active').length} active, 
						{activeStrategies.filter(s => s.status === 'completed').length} completed
					</div>
				</div>
				
				{#if activeStrategies.length === 0}
					<div class="p-8 text-center text-gray-500">
						<ShieldCheck class="w-12 h-12 mx-auto mb-3 text-green-300" />
						<p class="font-medium">No healing strategies needed</p>
						<p class="text-sm mt-1">Network is operating within healthy parameters</p>
					</div>
				{:else}
					<div class="divide-y divide-gray-100">
						{#each activeStrategies as strategy}
							<div class="px-4 py-4">
								<div class="flex items-center justify-between mb-2">
									<div class="flex items-center gap-2">
										<div class="w-8 h-8 rounded-full flex items-center justify-center
											{strategy.status === 'active' ? 'bg-blue-100 text-blue-600' :
											 strategy.status === 'completed' ? 'bg-green-100 text-green-600' :
											 'bg-red-100 text-red-600'}">
											{#if strategy.status === 'active'}
												<RefreshCw class="w-4 h-4 animate-spin" />
											{:else if strategy.status === 'completed'}
												<CheckCircle class="w-4 h-4" />
											{:else}
												<AlertCircle class="w-4 h-4" />
											{/if}
										</div>
										<div>
											<div class="font-medium text-gray-900">{strategy.name}</div>
											<div class="text-xs text-gray-500">Activated month {strategy.activatedMonth}</div>
										</div>
									</div>
									<div class="text-right">
										{#if strategy.status === 'active'}
											<div class="text-sm font-medium text-blue-600">{strategy.progress.toFixed(0)}%</div>
										{:else if strategy.effectiveness}
											<div class="text-sm font-medium text-green-600">{strategy.effectiveness}% effective</div>
										{/if}
									</div>
								</div>
								
								{#if strategy.status === 'active'}
									<div class="h-2 bg-gray-100 rounded-full overflow-hidden mt-2">
										<div class="h-full bg-blue-500 rounded-full transition-all duration-500" style="width: {strategy.progress}%"></div>
									</div>
								{/if}
								
								<div class="mt-3 flex flex-wrap gap-2">
									{#each strategy.actions as action}
										<span class="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded">{action}</span>
									{/each}
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
			
			<!-- Self-Healing Explanation with Interactive Diagram -->
			<div class="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6">
				<h3 class="font-bold text-green-900 flex items-center gap-2 mb-4">
					<ShieldCheck class="w-5 h-5" />
					How OSF Self-Heals
				</h3>
				
				<!-- Interactive Cycle Diagram -->
				<div class="grid md:grid-cols-2 gap-6">
					<div>
						<SelfHealingDiagram activeStep={activeStrategies.length > 0 ? 'respond' : overallHealthStatus === 'warning' ? 'diagnose' : overallHealthStatus === 'critical' ? 'respond' : null} />
					</div>
					<div class="space-y-3">
						<p class="text-green-800 text-sm">
							Unlike traditional markets where distress cascades into foreclosures, OSF's network automatically detects and responds to stress through a continuous cycle:
						</p>
						<div class="space-y-2">
							<div class="bg-white/60 rounded-lg p-3 flex items-start gap-3">
								<span class="bg-blue-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center flex-shrink-0">1</span>
								<div>
									<div class="font-medium text-green-900 text-sm">Sense</div>
									<p class="text-xs text-green-700">Monitor liquidity, exit queues, occupancy in real-time</p>
								</div>
							</div>
							<div class="bg-white/60 rounded-lg p-3 flex items-start gap-3">
								<span class="bg-blue-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center flex-shrink-0">2</span>
								<div>
									<div class="font-medium text-green-900 text-sm">Diagnose</div>
									<p class="text-xs text-green-700">AI identifies root cause of network stress</p>
								</div>
							</div>
							<div class="bg-white/60 rounded-lg p-3 flex items-start gap-3">
								<span class="bg-blue-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center flex-shrink-0">3</span>
								<div>
									<div class="font-medium text-green-900 text-sm">Respond</div>
									<p class="text-xs text-green-700">Activate strategies: liquidity pool, buyer matching</p>
								</div>
							</div>
							<div class="bg-white/60 rounded-lg p-3 flex items-start gap-3">
								<span class="bg-blue-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center flex-shrink-0">4</span>
								<div>
									<div class="font-medium text-green-900 text-sm">Verify</div>
									<p class="text-xs text-green-700">Check if intervention is working</p>
								</div>
							</div>
							<div class="bg-white/60 rounded-lg p-3 flex items-start gap-3">
								<span class="bg-blue-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center flex-shrink-0">5</span>
								<div>
									<div class="font-medium text-green-900 text-sm">Learn</div>
									<p class="text-xs text-green-700">Improve strategy effectiveness over time</p>
								</div>
							</div>
						</div>
					</div>
				</div>
				
				<div class="mt-4 p-4 bg-white/80 rounded-lg border border-green-200">
					<div class="flex items-start gap-3">
						<Info class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
						<div>
							<div class="font-medium text-green-800">What Banks Can't Do</div>
							<p class="text-sm text-green-700 mt-1">
								Traditional lenders can only foreclose or hold. OSF can match distressed sellers with opportunistic buyers, 
								accelerate rent-to-own tenants into ownership, deploy liquidity pools, and offer partial exits — 
								because the network has visibility into all participants.
							</p>
						</div>
					</div>
				</div>
			</div>
		</div>
		{/if}
	{/if}
</div>

<!-- Marathon Synopsis Dialog -->
<Dialog.Root bind:open={showMarathonSynopsis}>
	<Dialog.Content class="max-w-4xl max-h-[90vh] overflow-y-auto">
		<Dialog.Header>
			<Dialog.Title class="flex items-center gap-2 text-2xl">
				<Trophy class="w-6 h-6 text-amber-500" />
				Marathon Complete — Simulation Synopsis
			</Dialog.Title>
			<Dialog.Description>
				Summary of {marathonSynopsis?.totalYears.toFixed(1)} years of autonomous simulation
			</Dialog.Description>
		</Dialog.Header>
		
		{#if marathonSynopsis}
			<div class="space-y-6 py-4">
				<!-- COOPERATIVE OUTCOMES - The Hero Section -->
				<div class="bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-xl p-6">
					<div class="flex items-center justify-between mb-4">
						<h3 class="font-bold text-xl flex items-center gap-2">
							<Heart class="w-6 h-6" />
							Collective Outcomes
						</h3>
						<div class="text-right">
							<div class="text-3xl font-bold">{marathonSynopsis.networkHealth?.grade || 'B'}</div>
							<div class="text-xs text-emerald-200">Network Health</div>
						</div>
					</div>
					
					<p class="text-emerald-100 text-sm mb-4">
						Over {marathonSynopsis.totalYears.toFixed(0)} years, the OSF network achieved these outcomes through cooperative ownership:
					</p>
					
					<!-- Key Collective Stats -->
					<div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
						<div class="bg-white/20 backdrop-blur rounded-lg p-3 text-center">
							<div class="text-2xl font-bold">{marathonSynopsis.collectiveOutcomes?.familiesHoused || 0}</div>
							<div class="text-xs text-emerald-100">Families Housed</div>
						</div>
						<div class="bg-white/20 backdrop-blur rounded-lg p-3 text-center">
							<div class="text-2xl font-bold">${((marathonSynopsis.collectiveOutcomes?.totalNetworkDividends || 0) / 1000).toFixed(0)}K</div>
							<div class="text-xs text-emerald-100">Dividends Distributed</div>
						</div>
						<div class="bg-white/20 backdrop-blur rounded-lg p-3 text-center">
							<div class="text-2xl font-bold">${((marathonSynopsis.collectiveOutcomes?.equityAccessedByHomeowners || 0) / 1000).toFixed(0)}K</div>
							<div class="text-xs text-emerald-100">Equity Accessed</div>
						</div>
						<div class="bg-white/20 backdrop-blur rounded-lg p-3 text-center">
							<div class="text-2xl font-bold">{marathonSynopsis.collectiveOutcomes?.crisesSurvived || 0}</div>
							<div class="text-xs text-emerald-100">Crises Survived</div>
						</div>
					</div>
					
					<!-- Zero Harm Stats -->
					<div class="bg-white/10 rounded-lg p-3 flex items-center justify-around text-center">
						<div>
							<div class="text-xl font-bold text-green-300">0</div>
							<div class="text-xs text-emerald-200">Evictions</div>
						</div>
						<div class="w-px h-8 bg-white/20"></div>
						<div>
							<div class="text-xl font-bold text-green-300">0</div>
							<div class="text-xs text-emerald-200">Foreclosures</div>
						</div>
						<div class="w-px h-8 bg-white/20"></div>
						<div>
							<div class="text-xl font-bold text-green-300">{marathonSynopsis.collectiveOutcomes?.rentToOwnCompletions || 0}</div>
							<div class="text-xs text-emerald-200">Became Homeowners</div>
						</div>
						<div class="w-px h-8 bg-white/20"></div>
						<div>
							<div class="text-xl font-bold text-green-300">{marathonSynopsis.collectiveOutcomes?.selfHealingActivations || 0}</div>
							<div class="text-xs text-emerald-200">Self-Healing Actions</div>
						</div>
					</div>
				</div>
				
				<!-- YOUR CONTRIBUTION - How you helped -->
				<div class="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-xl p-5">
					<div class="flex items-start gap-4">
						<div class="w-14 h-14 bg-indigo-600 rounded-xl flex items-center justify-center flex-shrink-0">
							<ShieldCheck class="w-7 h-7 text-white" />
						</div>
						<div class="flex-1">
							<div class="flex items-center gap-2 mb-1">
								<h3 class="font-bold text-indigo-900 text-lg">Your Contribution</h3>
								<span class="px-2 py-0.5 bg-indigo-600 text-white text-xs rounded-full font-medium">
									{marathonSynopsis.userContribution?.title || 'Participant'}
								</span>
							</div>
							<p class="text-indigo-700 text-sm mb-3">
								{marathonSynopsis.userContribution?.description || 'You participated in the network.'}
							</p>
							
							<div class="grid grid-cols-3 gap-3">
								<div class="bg-white rounded-lg p-2 text-center border border-indigo-100">
									<div class="text-lg font-bold text-indigo-600">
										${((marathonSynopsis.userContribution?.capitalDeployed || 0) / 1000).toFixed(0)}K
									</div>
									<div class="text-xs text-indigo-500">Capital Deployed</div>
								</div>
								<div class="bg-white rounded-lg p-2 text-center border border-indigo-100">
									<div class="text-lg font-bold text-indigo-600">
										{(marathonSynopsis.userContribution?.homesEnabled || 0).toFixed(1)}
									</div>
									<div class="text-xs text-indigo-500">Homes Enabled</div>
								</div>
								<div class="bg-white rounded-lg p-2 text-center border border-indigo-100">
									<div class="text-lg font-bold text-indigo-600">
										{marathonSynopsis.userContribution?.stabilityScore || 0}%
									</div>
									<div class="text-xs text-indigo-500">Stability Score</div>
								</div>
							</div>
							
							{#if marathonSynopsis.userContribution?.heldDuringDownturns}
								<div class="mt-3 flex items-center gap-2 text-sm text-green-700 bg-green-50 rounded-lg px-3 py-2">
									<CheckCircle class="w-4 h-4" />
									You held steady during market downturns — your patience helped stabilize the network
								</div>
							{/if}
						</div>
					</div>
				</div>
				
				<!-- Network Scale - Shows the magnitude of what was managed -->
				<div class="bg-gradient-to-r from-slate-800 to-slate-700 text-white rounded-xl p-5">
					<h3 class="font-semibold mb-4 flex items-center gap-2">
						<Building class="w-5 h-5" />
						Network Under Management
					</h3>
					
					<!-- Property Value Growth -->
					<div class="bg-white/10 rounded-lg p-4 mb-4">
						<div class="flex items-center justify-between mb-2">
							<span class="text-slate-300">Property Portfolio</span>
							<span class="text-sm px-2 py-0.5 rounded {marathonSynopsis.networkScale.propertyValueGrowth >= 0 ? 'bg-green-500/30 text-green-300' : 'bg-red-500/30 text-red-300'}">
								{marathonSynopsis.networkScale.propertyValueGrowth >= 0 ? '+' : ''}{marathonSynopsis.networkScale.propertyValueGrowth.toFixed(0)}%
							</span>
						</div>
						<div class="flex items-center gap-3">
							<div class="text-center">
								<div class="text-lg font-bold">${(marathonSynopsis.networkScale.startingPropertyValue / 1000000).toFixed(1)}M</div>
								<div class="text-xs text-slate-400">Start</div>
							</div>
							<div class="flex-1 flex items-center gap-1">
								<div class="flex-1 h-1 bg-slate-600 rounded-full overflow-hidden">
									<div class="h-full {marathonSynopsis.networkScale.propertyValueGrowth >= 0 ? 'bg-green-500' : 'bg-red-500'}" 
										style="width: {Math.min(100, Math.abs(marathonSynopsis.networkScale.propertyValueGrowth))}%"></div>
								</div>
								<ArrowRight class="w-4 h-4 text-slate-400" />
							</div>
							<div class="text-center">
								<div class="text-lg font-bold">${(marathonSynopsis.networkScale.totalPropertyValue / 1000000).toFixed(1)}M</div>
								<div class="text-xs text-slate-400">End</div>
							</div>
						</div>
						<div class="text-xs text-slate-400 mt-2 text-center">
							{marathonSynopsis.networkScale.propertiesUnderManagement} properties • ~${(marathonSynopsis.networkScale.totalPropertyValue / marathonSynopsis.networkScale.propertiesUnderManagement / 1000).toFixed(0)}K avg
						</div>
					</div>
					
					<div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-center mb-4">
						<div class="bg-white/10 rounded-lg p-3">
							<div class="text-2xl font-bold">{marathonSynopsis.networkScale.propertiesUnderManagement}</div>
							<div class="text-xs text-slate-300">Properties</div>
						</div>
						<div class="bg-white/10 rounded-lg p-3">
							<div class="text-2xl font-bold">{marathonSynopsis.networkScale.activeRentalContracts}</div>
							<div class="text-xs text-slate-300">Rental Contracts</div>
						</div>
						<div class="bg-white/10 rounded-lg p-3">
							<div class="text-2xl font-bold">{marathonSynopsis.networkScale.rentToOwnContracts}</div>
							<div class="text-xs text-slate-300">Rent-to-Own</div>
						</div>
						<div class="bg-white/10 rounded-lg p-3">
							<div class="text-2xl font-bold">{marathonSynopsis.networkScale.totalParticipants}</div>
							<div class="text-xs text-slate-300">Participants</div>
						</div>
					</div>
					
					<!-- Reserves (Treasury + Liquidity) -->
					<div class="bg-white/5 rounded-lg p-3 border border-white/10">
						<div class="text-xs text-slate-400 mb-2">Network Reserves (Operating + Emergency)</div>
						<div class="grid grid-cols-2 gap-3 text-center text-sm">
							<div>
								<div class="font-bold text-blue-300">${(networkTreasury / 1000).toFixed(0)}K</div>
								<div class="text-xs text-slate-400">Operating Treasury</div>
							</div>
							<div>
								<div class="font-bold text-green-300">${(liquidityPool.balance / 1000).toFixed(0)}K</div>
								<div class="text-xs text-slate-400">Liquidity Pool</div>
							</div>
						</div>
						<div class="text-xs text-slate-500 mt-2 text-center">
							~{((networkTreasury + liquidityPool.balance) / marathonSynopsis.networkScale.totalPropertyValue * 100).toFixed(1)}% of property value in reserves
						</div>
					</div>
				</div>
				
				<!-- Simulation Overview Stats -->
				<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
					<div class="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
						<div class="text-3xl font-bold text-blue-600">{marathonSynopsis.totalMonths}</div>
						<div class="text-sm text-blue-700">Months Simulated</div>
					</div>
					<div class="bg-purple-50 border border-purple-200 rounded-lg p-4 text-center">
						<div class="text-3xl font-bold text-purple-600">{marathonSynopsis.sessionDuration}</div>
						<div class="text-sm text-purple-700">Session Duration</div>
					</div>
					<div class="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
						<div class="text-3xl font-bold {marathonSynopsis.networkScale.propertyValueGrowth >= 0 ? 'text-green-600' : 'text-red-600'}">
							{marathonSynopsis.networkScale.propertyValueGrowth >= 0 ? '+' : ''}{marathonSynopsis.networkScale.propertyValueGrowth.toFixed(0)}%
						</div>
						<div class="text-sm text-green-700">Network Growth</div>
					</div>
					<div class="bg-amber-50 border border-amber-200 rounded-lg p-4 text-center">
						<div class="text-3xl font-bold text-amber-600">{marathonSynopsis.reputation.finalScore}/100</div>
						<div class="text-sm text-amber-700">Reputation Score</div>
					</div>
				</div>
				
				<!-- Your Portfolio Performance (Separate Section) -->
				<div class="bg-gradient-to-r from-slate-100 to-slate-50 border border-slate-300 rounded-xl p-4">
					<h3 class="font-semibold text-slate-800 mb-3 flex items-center gap-2">
						<Wallet class="w-5 h-5" />
						Your Portfolio Performance
						<span class="text-xs font-normal text-slate-500">(Your personal investments during the simulation)</span>
					</h3>
					
					<div class="grid md:grid-cols-4 gap-4">
						<div class="text-center">
							<div class="text-2xl font-bold text-slate-600">${marathonSynopsis.startingValue.toLocaleString()}</div>
							<div class="text-xs text-slate-500">Starting Net Worth</div>
						</div>
						<div class="text-center">
							<div class="text-2xl font-bold {marathonSynopsis.totalReturnPercent >= 0 ? 'text-green-600' : 'text-red-600'}">
								{marathonSynopsis.totalReturnPercent >= 0 ? '+' : ''}{marathonSynopsis.totalReturnPercent.toFixed(1)}%
							</div>
							<div class="text-xs text-slate-500">Total Return</div>
						</div>
						<div class="text-center">
							<div class="text-2xl font-bold text-green-600">+${marathonSynopsis.dividendsCollected.toLocaleString()}</div>
							<div class="text-xs text-slate-500">Dividends Collected</div>
						</div>
						<div class="text-center">
							<div class="text-2xl font-bold text-amber-600">${marathonSynopsis.endingValue.toLocaleString()}</div>
							<div class="text-xs text-slate-500">Final Net Worth</div>
						</div>
					</div>
					
					<div class="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
						<strong>💡 How this is calculated:</strong> Starting Net Worth ($100,000) = Cash + Token Holdings. 
						Final Net Worth = Your remaining cash balance + current value of all token holdings. 
						Total Return shows the change in your complete portfolio value over the simulation period.
					</div>
				</div>
				
				<!-- Performance Charts -->
				{#if marathonSynopsis.history.length > 0}
				<div class="bg-white border border-gray-200 rounded-xl p-4">
					<h3 class="font-semibold text-gray-900 mb-4 flex items-center gap-2">
						<Activity class="w-5 h-5" />
						Performance Over Time
					</h3>
					
					<div class="grid md:grid-cols-2 gap-6">
						<!-- Network Value Chart -->
						<div>
							<div class="text-sm text-gray-600 mb-2">Network Property Value</div>
							<div class="relative h-32 bg-gradient-to-b from-blue-50 to-white rounded-lg border border-blue-100 overflow-hidden">
								<svg class="w-full h-full" viewBox="0 0 400 120" preserveAspectRatio="none">
									<!-- Area fill -->
									<path 
										d={generateAreaPath(marathonSynopsis.history.map(h => h.networkValue), 400, 120, 10)}
										fill="url(#networkGradient)"
										opacity="0.3"
									/>
									<!-- Line -->
									<path 
										d={generateSparklinePath(marathonSynopsis.history.map(h => h.networkValue), 400, 120, 10)}
										fill="none"
										stroke="#3b82f6"
										stroke-width="2"
									/>
									<defs>
										<linearGradient id="networkGradient" x1="0" y1="0" x2="0" y2="1">
											<stop offset="0%" stop-color="#3b82f6" />
											<stop offset="100%" stop-color="#3b82f6" stop-opacity="0" />
										</linearGradient>
									</defs>
								</svg>
								<div class="absolute bottom-1 left-2 text-xs text-gray-500">Month 1</div>
								<div class="absolute bottom-1 right-2 text-xs text-gray-500">Month {marathonSynopsis.history.length}</div>
								<div class="absolute top-1 right-2 text-xs font-medium text-blue-600">
									${(marathonSynopsis.history[marathonSynopsis.history.length - 1]?.networkValue / 1000000).toFixed(1)}M
								</div>
							</div>
						</div>
						
						<!-- Your Net Worth Chart -->
						<div>
							<div class="text-sm text-gray-600 mb-2">Your Net Worth</div>
							<div class="relative h-32 bg-gradient-to-b from-emerald-50 to-white rounded-lg border border-emerald-100 overflow-hidden">
								<svg class="w-full h-full" viewBox="0 0 400 120" preserveAspectRatio="none">
									<path 
										d={generateAreaPath(marathonSynopsis.history.map(h => h.userNetWorth), 400, 120, 10)}
										fill="url(#userGradient)"
										opacity="0.3"
									/>
									<path 
										d={generateSparklinePath(marathonSynopsis.history.map(h => h.userNetWorth), 400, 120, 10)}
										fill="none"
										stroke="#10b981"
										stroke-width="2"
									/>
									<defs>
										<linearGradient id="userGradient" x1="0" y1="0" x2="0" y2="1">
											<stop offset="0%" stop-color="#10b981" />
											<stop offset="100%" stop-color="#10b981" stop-opacity="0" />
										</linearGradient>
									</defs>
								</svg>
								<div class="absolute bottom-1 left-2 text-xs text-gray-500">$100K start</div>
								<div class="absolute top-1 right-2 text-xs font-medium text-emerald-600">
									${(marathonSynopsis.history[marathonSynopsis.history.length - 1]?.userNetWorth / 1000).toFixed(0)}K
								</div>
							</div>
						</div>
						
						<!-- Token Price Chart -->
						<div>
							<div class="text-sm text-gray-600 mb-2">Token Price</div>
							<div class="relative h-32 bg-gradient-to-b from-purple-50 to-white rounded-lg border border-purple-100 overflow-hidden">
								<svg class="w-full h-full" viewBox="0 0 400 120" preserveAspectRatio="none">
									<path 
										d={generateAreaPath(marathonSynopsis.history.map(h => h.tokenPrice), 400, 120, 10)}
										fill="url(#tokenGradient)"
										opacity="0.3"
									/>
									<path 
										d={generateSparklinePath(marathonSynopsis.history.map(h => h.tokenPrice), 400, 120, 10)}
										fill="none"
										stroke="#8b5cf6"
										stroke-width="2"
									/>
									<defs>
										<linearGradient id="tokenGradient" x1="0" y1="0" x2="0" y2="1">
											<stop offset="0%" stop-color="#8b5cf6" />
											<stop offset="100%" stop-color="#8b5cf6" stop-opacity="0" />
										</linearGradient>
									</defs>
								</svg>
								<div class="absolute bottom-1 left-2 text-xs text-gray-500">$1.00 start</div>
								<div class="absolute top-1 right-2 text-xs font-medium text-purple-600">
									${marathonSynopsis.history[marathonSynopsis.history.length - 1]?.tokenPrice.toFixed(2)}
								</div>
							</div>
						</div>
						
						<!-- Market Conditions Timeline -->
						<div>
							<div class="text-sm text-gray-600 mb-2">Market Conditions</div>
							<div class="relative h-32 bg-gradient-to-b from-gray-50 to-white rounded-lg border border-gray-200 overflow-hidden">
								<svg class="w-full h-full" viewBox="0 0 400 120" preserveAspectRatio="none">
									{#each marathonSynopsis.history as point, i}
										{@const barWidth = 400 / marathonSynopsis.history.length}
										<rect 
											x={i * barWidth}
											y="10"
											width={barWidth}
											height="100"
											fill={getMarketConditionColor(point.marketCondition)}
											opacity="0.6"
										/>
									{/each}
								</svg>
								<div class="absolute bottom-1 left-2 right-2 flex justify-between text-xs">
									<span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-green-500"></span>Boom</span>
									<span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-blue-500"></span>Stable</span>
									<span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-yellow-500"></span>Stagnant</span>
									<span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-orange-500"></span>Declining</span>
									<span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-red-500"></span>Bust</span>
								</div>
							</div>
						</div>
					</div>
					
					<!-- Property Count & Reputation Over Time -->
					<div class="grid md:grid-cols-2 gap-6 mt-4">
						<div>
							<div class="text-sm text-gray-600 mb-2">Property Count</div>
							<div class="relative h-24 bg-gradient-to-b from-amber-50 to-white rounded-lg border border-amber-100 overflow-hidden">
								<svg class="w-full h-full" viewBox="0 0 400 90" preserveAspectRatio="none">
									<path 
										d={generateSparklinePath(marathonSynopsis.history.map(h => h.propertyCount), 400, 90, 10)}
										fill="none"
										stroke="#f59e0b"
										stroke-width="2"
									/>
								</svg>
								<div class="absolute top-1 left-2 text-xs text-gray-500">
									{marathonSynopsis.history[0]?.propertyCount || 0} properties
								</div>
								<div class="absolute top-1 right-2 text-xs font-medium text-amber-600">
									{marathonSynopsis.history[marathonSynopsis.history.length - 1]?.propertyCount || 0} properties
								</div>
							</div>
						</div>
						
						<div>
							<div class="text-sm text-gray-600 mb-2">Network Reputation</div>
							<div class="relative h-24 bg-gradient-to-b from-indigo-50 to-white rounded-lg border border-indigo-100 overflow-hidden">
								<svg class="w-full h-full" viewBox="0 0 400 90" preserveAspectRatio="none">
									<!-- Reference lines at 50 and 75 -->
									<line x1="0" y1="45" x2="400" y2="45" stroke="#e5e7eb" stroke-dasharray="4" />
									<line x1="0" y1="22" x2="400" y2="22" stroke="#e5e7eb" stroke-dasharray="4" />
									<path 
										d={generateSparklinePath(marathonSynopsis.history.map(h => h.reputationScore), 400, 90, 10)}
										fill="none"
										stroke="#6366f1"
										stroke-width="2"
									/>
								</svg>
								<div class="absolute top-1 left-2 text-xs text-gray-500">
									Score: {marathonSynopsis.history[0]?.reputationScore || 0}
								</div>
								<div class="absolute top-1 right-2 text-xs font-medium text-indigo-600">
									Score: {marathonSynopsis.history[marathonSynopsis.history.length - 1]?.reputationScore || 0}
								</div>
							</div>
						</div>
					</div>
				</div>
				{/if}
				
				<!-- Market Journey -->
				<div class="bg-gray-50 border border-gray-200 rounded-xl p-4">
					<h3 class="font-semibold text-gray-900 mb-3 flex items-center gap-2">
						<TrendingUp class="w-5 h-5" />
						Market Journey
					</h3>
					
					<div class="grid md:grid-cols-2 gap-4 mb-4">
						<div>
							<div class="text-sm text-gray-500 mb-2">Market Phases</div>
							<div class="space-y-2">
								{#each marathonSynopsis.marketPhases as phase}
									<div class="flex items-center justify-between">
										<span class="text-sm font-medium
											{phase.phase === 'Boom' ? 'text-green-600' :
											 phase.phase === 'Stable' ? 'text-blue-600' :
											 phase.phase === 'Stagnant' ? 'text-yellow-600' :
											 phase.phase === 'Declining' ? 'text-orange-600' : 'text-red-600'}">
											{phase.phase}
										</span>
										<span class="text-sm text-gray-600">{phase.months} months</span>
									</div>
								{/each}
							</div>
						</div>
						<div>
							<div class="text-sm text-gray-500 mb-2">WA Economic Drivers</div>
							<div class="space-y-2 text-sm">
								<div class="flex justify-between">
									<span class="text-gray-600">Iron Ore Range:</span>
									<span class="font-medium">${marathonSynopsis.ironOreRange.min.toFixed(0)} — ${marathonSynopsis.ironOreRange.max.toFixed(0)}/t</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-600">Population Growth:</span>
									<span class="font-medium">{marathonSynopsis.populationRange.min.toFixed(1)}% — {marathonSynopsis.populationRange.max.toFixed(1)}%</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-600">Worst Month:</span>
									<span class="font-medium text-red-600">Month {marathonSynopsis.worstMonth.month} ({marathonSynopsis.worstMonth.appreciation.toFixed(1)}%)</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-600">Best Month:</span>
									<span class="font-medium text-green-600">Month {marathonSynopsis.bestMonth.month} (+{marathonSynopsis.bestMonth.appreciation.toFixed(1)}%)</span>
								</div>
							</div>
						</div>
					</div>
				</div>
				
				<!-- Mitigations & Positive Actions -->
				{#if marathonSynopsis.mitigations.length > 0}
					<div class="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl overflow-hidden">
						<div class="bg-green-100/50 border-b border-green-200 px-4 py-3">
							<h3 class="font-semibold text-green-900 flex items-center gap-2">
								<ShieldCheck class="w-5 h-5" />
								Mitigations & Positive Actions
							</h3>
							<p class="text-sm text-green-700 mt-1">How OSF protected participants and improved outcomes</p>
						</div>
						<div class="divide-y divide-green-100">
							{#each marathonSynopsis.mitigations as mitigation}
								<div class="px-4 py-3">
									<div class="flex items-start gap-3">
										<div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
											<CheckCircle class="w-4 h-4 text-green-600" />
										</div>
										<div class="flex-1">
											<div class="font-medium text-green-900">{mitigation.action}</div>
											<div class="text-sm text-green-700 mt-1">
												<span class="font-medium">Trigger:</span> {mitigation.trigger}
											</div>
											<div class="text-sm text-green-700">
												<span class="font-medium">Outcome:</span> {mitigation.outcome}
											</div>
											<div class="text-xs text-green-600 mt-1 flex items-center gap-1">
												<Users class="w-3 h-3" />
												{mitigation.beneficiaries}
											</div>
										</div>
									</div>
								</div>
							{/each}
						</div>
					</div>
				{/if}
				
				<!-- Stakeholder Outcomes -->
				<div class="bg-white border border-gray-200 rounded-xl overflow-hidden">
					<div class="bg-gray-50 border-b border-gray-200 px-4 py-3">
						<h3 class="font-semibold text-gray-900 flex items-center gap-2">
							<Users class="w-5 h-5" />
							How Each Stakeholder Fared
						</h3>
					</div>
					<div class="divide-y divide-gray-100">
						{#each Object.entries(marathonSynopsis.stakeholders) as [role, outcome]}
							<div class="px-4 py-3">
								<div class="flex items-start justify-between">
									<div>
										<div class="font-medium text-gray-900 capitalize flex items-center gap-2">
											{role === 'investors' ? '💰' : 
											 role === 'renters' ? '🏠' :
											 role === 'tenants' ? '🔑' :
											 role === 'homeowners' ? '🏡' :
											 role === 'serviceProviders' ? '🔧' : '⚖️'}
											{role.replace(/([A-Z])/g, ' $1').trim()}
										</div>
										<p class="text-sm text-gray-600 mt-1">{outcome.details}</p>
									</div>
									<span class="text-lg flex-shrink-0 ml-4">{outcome.verdict}</span>
								</div>
							</div>
						{/each}
					</div>
				</div>
				
				<!-- Self-Healing Activity -->
				{#if marathonSynopsis.healingStrategiesUsed > 0 || marathonSynopsis.exitRequestsHandled > 0}
					<div class="bg-green-50 border border-green-200 rounded-xl p-4">
						<h3 class="font-semibold text-green-900 mb-3 flex items-center gap-2">
							<Heart class="w-5 h-5 text-red-500" />
							Self-Healing Activity
						</h3>
						<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
							<div class="bg-white/60 rounded-lg p-3 text-center">
								<div class="text-2xl font-bold text-green-700">{marathonSynopsis.healingStrategiesUsed}</div>
								<div class="text-xs text-green-600">Strategies Activated</div>
							</div>
							<div class="bg-white/60 rounded-lg p-3 text-center">
								<div class="text-2xl font-bold text-green-700">{marathonSynopsis.exitRequestsHandled}</div>
								<div class="text-xs text-green-600">Exits Handled</div>
							</div>
							<div class="bg-white/60 rounded-lg p-3 text-center">
								<div class="text-2xl font-bold text-green-700">${marathonSynopsis.liquidityDeployed.toLocaleString()}</div>
								<div class="text-xs text-green-600">Liquidity Deployed</div>
							</div>
							<div class="bg-white/60 rounded-lg p-3 text-center">
								<div class="text-2xl font-bold text-green-700">{marathonSynopsis.successfulMatches}</div>
								<div class="text-xs text-green-600">Buyer-Seller Matches</div>
							</div>
						</div>
					</div>
				{/if}
				
				<!-- Network Reputation & Growth -->
				<div class="bg-indigo-50 border border-indigo-200 rounded-xl p-4">
					<h3 class="font-semibold text-indigo-900 mb-3 flex items-center gap-2">
						<Star class="w-5 h-5" />
						Network Reputation & Growth
					</h3>
					
					<div class="grid md:grid-cols-2 gap-4">
						<!-- Reputation Score -->
						<div>
							<div class="flex items-center justify-between mb-2">
								<span class="text-sm text-indigo-700">Final Reputation Score</span>
								<span class="text-2xl font-bold {marathonSynopsis.reputation.finalScore >= 75 ? 'text-green-600' : marathonSynopsis.reputation.finalScore >= 50 ? 'text-amber-600' : 'text-red-600'}">
									{marathonSynopsis.reputation.finalScore}/100
								</span>
							</div>
							<div class="w-full h-3 bg-indigo-100 rounded-full mb-3">
								<div 
									class="h-full rounded-full {marathonSynopsis.reputation.finalScore >= 75 ? 'bg-green-500' : marathonSynopsis.reputation.finalScore >= 50 ? 'bg-amber-500' : 'bg-red-500'}"
									style="width: {marathonSynopsis.reputation.finalScore}%"
								></div>
							</div>
							
							<!-- Stakeholder breakdown -->
							<div class="grid grid-cols-2 gap-2 text-sm">
								<div class="flex justify-between">
									<span class="text-indigo-600">Investors:</span>
									<span class="font-medium">{marathonSynopsis.reputation.investorSatisfaction}%</span>
								</div>
								<div class="flex justify-between">
									<span class="text-indigo-600">Homeowners:</span>
									<span class="font-medium">{marathonSynopsis.reputation.homeownerSatisfaction}%</span>
								</div>
								<div class="flex justify-between">
									<span class="text-indigo-600">Renters:</span>
									<span class="font-medium">{marathonSynopsis.reputation.renterSatisfaction}%</span>
								</div>
								<div class="flex justify-between">
									<span class="text-indigo-600">Rent-to-Own:</span>
									<span class="font-medium">{marathonSynopsis.reputation.tenantSatisfaction}%</span>
								</div>
							</div>
						</div>
						
						<!-- Property Growth -->
						<div>
							<div class="text-sm text-indigo-700 mb-2">Network Growth</div>
							<div class="grid grid-cols-3 gap-2 text-center mb-3">
								<div class="bg-white/60 rounded-lg p-2">
									<div class="text-xl font-bold text-green-600">+{marathonSynopsis.reputation.propertiesAdded}</div>
									<div class="text-xs text-gray-600">Joined</div>
								</div>
								<div class="bg-white/60 rounded-lg p-2">
									<div class="text-xl font-bold text-red-600">-{marathonSynopsis.reputation.propertiesExited}</div>
									<div class="text-xs text-gray-600">Exited</div>
								</div>
								<div class="bg-white/60 rounded-lg p-2">
									<div class="text-xl font-bold {marathonSynopsis.reputation.netGrowth >= 0 ? 'text-green-600' : 'text-red-600'}">
										{marathonSynopsis.reputation.netGrowth >= 0 ? '+' : ''}{marathonSynopsis.reputation.netGrowth}
									</div>
									<div class="text-xs text-gray-600">Net</div>
								</div>
							</div>
							
							{#if marathonSynopsis.reputation.wordOfMouthMultiplier > 1.1}
								<div class="text-sm text-indigo-700 bg-white/60 rounded-lg p-2">
									🗣️ <span class="font-medium">{((marathonSynopsis.reputation.wordOfMouthMultiplier - 1) * 100).toFixed(0)}%</span> word-of-mouth bonus earned through sustained satisfaction
								</div>
							{/if}
						</div>
					</div>
				</div>
				
				<!-- Investor Performance Distribution -->
				<div class="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
					<h3 class="font-semibold text-emerald-900 mb-3 flex items-center gap-2">
						<TrendingUp class="w-5 h-5" />
						Investor Performance Distribution
					</h3>
					
					<!-- Summary Stats -->
					<div class="grid grid-cols-4 gap-3 mb-4">
						<div class="bg-white/60 rounded-lg p-3 text-center">
							<div class="text-xl font-bold text-green-600">{marathonSynopsis.investorDistribution.positiveCount}</div>
							<div class="text-xs text-gray-600">Positive Returns</div>
						</div>
						<div class="bg-white/60 rounded-lg p-3 text-center">
							<div class="text-xl font-bold text-red-600">{marathonSynopsis.investorDistribution.negativeCount}</div>
							<div class="text-xs text-gray-600">Negative Returns</div>
						</div>
						<div class="bg-white/60 rounded-lg p-3 text-center">
							<div class="text-xl font-bold {marathonSynopsis.investorDistribution.averageReturn >= 0 ? 'text-green-600' : 'text-red-600'}">
								{marathonSynopsis.investorDistribution.averageReturn >= 0 ? '+' : ''}{marathonSynopsis.investorDistribution.averageReturn.toFixed(1)}%
							</div>
							<div class="text-xs text-gray-600">Average Return</div>
						</div>
						<div class="bg-white/60 rounded-lg p-3 text-center">
							<div class="text-xl font-bold {marathonSynopsis.investorDistribution.median >= 0 ? 'text-green-600' : 'text-red-600'}">
								{marathonSynopsis.investorDistribution.median >= 0 ? '+' : ''}{marathonSynopsis.investorDistribution.median.toFixed(1)}%
							</div>
							<div class="text-xs text-gray-600">Median Return</div>
						</div>
					</div>
					
					<!-- Best & Worst -->
					<div class="grid md:grid-cols-2 gap-3 mb-4">
						<div class="bg-green-100 rounded-lg p-3 flex items-center justify-between">
							<div>
								<div class="text-xs text-green-700">Best Performer</div>
								<div class="font-semibold text-green-900">{marathonSynopsis.investorDistribution.best.name}</div>
							</div>
							<div class="text-xl font-bold text-green-600">
								{marathonSynopsis.investorDistribution.best.returnPercent >= 0 ? '+' : ''}{marathonSynopsis.investorDistribution.best.returnPercent.toFixed(1)}%
							</div>
						</div>
						<div class="bg-red-100 rounded-lg p-3 flex items-center justify-between">
							<div>
								<div class="text-xs text-red-700">Lowest Return</div>
								<div class="font-semibold text-red-900">{marathonSynopsis.investorDistribution.worst.name}</div>
							</div>
							<div class="text-xl font-bold text-red-600">
								{marathonSynopsis.investorDistribution.worst.returnPercent >= 0 ? '+' : ''}{marathonSynopsis.investorDistribution.worst.returnPercent.toFixed(1)}%
							</div>
						</div>
					</div>
					
					<!-- All Investors Ranked -->
					<div class="text-sm text-emerald-700 mb-2">All Investors Ranked by Return</div>
					<div class="space-y-1 max-h-48 overflow-y-auto">
						{#each marathonSynopsis.investorDistribution.all as investor, i}
							<div class="flex items-center justify-between p-2 rounded-lg {investor.name === 'You' ? 'bg-blue-100 border border-blue-300' : 'bg-white/40'}">
								<div class="flex items-center gap-2">
									<span class="text-xs text-gray-500 w-6">#{i + 1}</span>
									<span class="font-medium text-gray-900 {investor.name === 'You' ? 'text-blue-700' : ''}">
										{investor.name}
									</span>
									<span class="text-xs text-gray-500">({investor.strategy})</span>
								</div>
								<div class="flex items-center gap-3">
									<span class="text-xs text-gray-500">
										${(investor.startingValue / 1000).toFixed(0)}K → ${(investor.endingValue / 1000).toFixed(0)}K
									</span>
									<span class="font-bold {investor.returnPercent >= 0 ? 'text-green-600' : 'text-red-600'}">
										{investor.returnPercent >= 0 ? '+' : ''}{investor.returnPercent.toFixed(1)}%
									</span>
								</div>
							</div>
						{/each}
					</div>
				</div>
				
				<!-- NPC Performance -->
				{#if marathonSynopsis.topPerformers.length > 0}
					<div class="bg-purple-50 border border-purple-200 rounded-xl p-4">
						<h3 class="font-semibold text-purple-900 mb-3 flex items-center gap-2">
							<Award class="w-5 h-5" />
							NPC Performance
						</h3>
						<div class="grid md:grid-cols-2 gap-4">
							<div>
								<div class="text-sm text-purple-700 mb-2">Top Performers</div>
								{#each marathonSynopsis.topPerformers as npc, i}
									<div class="flex items-center justify-between py-1">
										<span class="text-sm">
											{i === 0 ? '🥇' : i === 1 ? '🥈' : '🥉'} {npc.name}
										</span>
										<span class="text-sm font-medium text-purple-700">{npc.successRate.toFixed(0)}% success</span>
									</div>
								{/each}
							</div>
							{#if marathonSynopsis.mostAdaptive.length > 0}
								<div>
									<div class="text-sm text-purple-700 mb-2">Most Adaptive (Self-Corrected)</div>
									{#each marathonSynopsis.mostAdaptive as npc}
										<div class="flex items-center justify-between py-1">
											<span class="text-sm">🔄 {npc.name}</span>
											<span class="text-sm font-medium text-purple-700">{npc.adjustments} adjustments</span>
										</div>
									{/each}
								</div>
							{/if}
						</div>
					</div>
				{/if}
				
				<!-- Counterfactual: Without OSF -->
				<div class="bg-red-50 border border-red-200 rounded-xl p-4">
					<h3 class="font-semibold text-red-900 mb-2 flex items-center gap-2">
						<AlertTriangle class="w-5 h-5" />
						Without OSF: The Counterfactual
					</h3>
					<p class="text-sm text-red-800">{marathonSynopsis.withoutOSF}</p>
				</div>
				
				<!-- Real Market Context -->
				<div class="bg-slate-100 border border-slate-200 rounded-xl p-4">
					<h3 class="font-semibold text-slate-800 mb-3 flex items-center gap-2">
						<Info class="w-5 h-5" />
						Real Market Context
						<span class="text-xs font-normal text-slate-500">(ABS & PropTrack Data)</span>
					</h3>
					
					<div class="grid md:grid-cols-3 gap-4 text-sm">
						<div class="bg-white rounded-lg p-3">
							<div class="text-slate-500 text-xs mb-1">WA Mean Price (2025)</div>
							<div class="text-xl font-bold text-slate-800">$947,900</div>
							<div class="text-xs text-green-600">+4.9% quarterly growth</div>
						</div>
						<div class="bg-white rounded-lg p-3">
							<div class="text-slate-500 text-xs mb-1">Simulation Avg Price</div>
							<div class="text-xl font-bold text-slate-800">
								${(marathonSynopsis.networkScale.totalPropertyValue / marathonSynopsis.networkScale.propertiesUnderManagement / 1000).toFixed(0)}K
							</div>
							<div class="text-xs {(marathonSynopsis.networkScale.totalPropertyValue / marathonSynopsis.networkScale.propertiesUnderManagement) < 947900 ? 'text-blue-600' : 'text-amber-600'}">
								{(marathonSynopsis.networkScale.totalPropertyValue / marathonSynopsis.networkScale.propertiesUnderManagement) < 947900 ? 'Below' : 'Above'} WA average
							</div>
						</div>
						<div class="bg-white rounded-lg p-3">
							<div class="text-slate-500 text-xs mb-1">National Context</div>
							<div class="text-xl font-bold text-slate-800">$1.05M</div>
							<div class="text-xs text-slate-500">Australian mean price</div>
						</div>
					</div>
					
					<div class="mt-3 text-xs text-slate-600 bg-white rounded-lg p-2">
						📊 <strong>Data sources:</strong> 
						<a href="https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/total-value-dwellings/latest-release" target="_blank" class="text-blue-600 hover:underline">ABS Total Value of Dwellings</a>, 
						<a href="https://www.proptrack.com.au/home-price-index/" target="_blank" class="text-blue-600 hover:underline">PropTrack Home Price Index</a>. 
						WA currently has the strongest property growth in Australia at +4.9% quarterly, driven by mining sector strength and population growth.
					</div>
				</div>
				
				<!-- Your Discoveries (Achievements) -->
				<div class="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-xl p-5">
					<h3 class="font-semibold text-amber-900 mb-4 flex items-center gap-2">
						<span class="text-xl">🎓</span>
						Your Discoveries
						<span class="text-sm font-normal text-amber-600 ml-auto">
							{unlockedAchievementsCount} of {achievements.length} unlocked
						</span>
					</h3>
					
					<div class="grid grid-cols-2 md:grid-cols-5 gap-2">
						{#each achievements as achievement}
							<div class="p-2 rounded-lg text-center transition-all {achievement.unlocked 
								? 'bg-white border border-amber-300 shadow-sm' 
								: 'bg-amber-100/50 border border-amber-200/50 opacity-60'}">
								<div class="text-2xl mb-1">{achievement.unlocked ? achievement.icon : '🔒'}</div>
								<div class="text-xs font-medium {achievement.unlocked ? 'text-amber-900' : 'text-amber-600'}">
									{achievement.title}
								</div>
								{#if achievement.unlocked && achievement.unlockedAt}
									<div class="text-xs text-amber-500">Month {achievement.unlockedAt}</div>
								{/if}
							</div>
						{/each}
					</div>
					
					<p class="text-xs text-amber-700 mt-3 text-center">
						Discoveries are unlocked by exploring the simulation — understanding different perspectives, 
						witnessing market cycles, and experiencing network resilience firsthand.
					</p>
				</div>
				
				<!-- Key Takeaway -->
				<div class="bg-blue-600 text-white rounded-xl p-6 text-center">
					<h3 class="font-bold text-xl mb-2">The OSF Difference</h3>
					<p class="text-blue-100 mb-4">
						Through {marathonSynopsis.totalMonths} months of autonomous simulation, including market booms and busts,
						OSF demonstrated that collective ownership + diversification + coordination = resilience.
					</p>
					<div class="flex justify-center gap-4">
						<button 
							onclick={() => showMarathonSynopsis = false} 
							class="px-4 py-2 rounded-lg border-2 border-white text-white font-medium hover:bg-white/10 transition"
						>
							Close
						</button>
						<button 
							onclick={() => { showMarathonSynopsis = false; activeTab = 'thinking'; }} 
							class="px-4 py-2 rounded-lg bg-white text-blue-600 font-medium hover:bg-blue-50 transition"
						>
							View AI Thinking Log
						</button>
					</div>
				</div>
			</div>
		{/if}
	</Dialog.Content>
</Dialog.Root>

<!-- Buy Dialog -->
<Dialog.Root bind:open={showBuyDialog}>
	<Dialog.Content>
		<Dialog.Header>
			<Dialog.Title>Simulate Investment</Dialog.Title>
			<Dialog.Description>
				{selectedProperty?.address}, {selectedProperty?.suburb} (simulated tokens)
			</Dialog.Description>
		</Dialog.Header>
		
		<div class="py-4 space-y-4">
			<div class="grid grid-cols-2 gap-4 text-sm">
				<div>
					<span class="text-gray-500">Property Value</span>
					<div class="font-medium text-gray-900">${selectedProperty?.valuation_aud?.toLocaleString()}</div>
				</div>
				<div>
					<span class="text-gray-500">Expected Yield</span>
					<div class="font-medium text-green-600">{selectedProperty?.yield_percent}% p.a.</div>
				</div>
			</div>
			
			<div>
				<label for="buy-amount" class="block text-sm font-medium text-gray-700 mb-2">Investment Amount (AUD)</label>
				<Input id="buy-amount" type="number" bind:value={buyAmount} min="100" max={balance} step="100" />
				<div class="flex justify-between text-sm text-gray-500 mt-1">
					<span>Min: $100</span>
					<span>Available: ${balance.toLocaleString()}</span>
				</div>
			</div>
			
			<div class="bg-gray-50 rounded-lg p-3">
				<div class="flex justify-between text-sm">
					<span class="text-gray-500">Tokens to receive</span>
					<span class="font-medium text-gray-900">{((buyAmount ?? 0) / (selectedProperty?.token_price || 1)).toLocaleString()}</span>
				</div>
				<div class="flex justify-between text-sm mt-1">
					<span class="text-gray-500">Estimated annual yield</span>
					<span class="font-medium text-green-600">${((buyAmount ?? 0) * (selectedProperty?.yield_percent || 0) / 100).toFixed(2)}</span>
				</div>
			</div>
		</div>
		
		<Dialog.Footer>
			<Button variant="outline" onclick={() => showBuyDialog = false}>Cancel</Button>
			<Button onclick={handleBuy} disabled={!buyAmount || buyAmount <= 0 || buyAmount > balance}>
				Simulate Trade (${(buyAmount ?? 0).toLocaleString()})
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Submit Feedback Dialog -->
<Dialog.Root bind:open={showFeedbackDialog}>
	<Dialog.Content class="max-w-lg">
		<Dialog.Header>
			<Dialog.Title>Submit Feedback</Dialog.Title>
			<Dialog.Description>
				Help us improve OSF by reporting bugs or suggesting features
			</Dialog.Description>
		</Dialog.Header>
		
		<div class="py-4 space-y-4">
			<!-- Type Selection -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">Type</label>
				<div class="flex gap-2">
					<button 
						type="button"
						class="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg border transition {newFeedbackType === 'bug' ? 'border-red-300 bg-red-50 text-red-700' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}"
						onclick={() => newFeedbackType = 'bug'}
					>
						<Bug class="w-4 h-4" />
						Bug Report
					</button>
					<button 
						type="button"
						class="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg border transition {newFeedbackType === 'enhancement' ? 'border-amber-300 bg-amber-50 text-amber-700' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}"
						onclick={() => newFeedbackType = 'enhancement'}
					>
						<Lightbulb class="w-4 h-4" />
						Feature
					</button>
					<button 
						type="button"
						class="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg border transition {newFeedbackType === 'question' ? 'border-blue-300 bg-blue-50 text-blue-700' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}"
						onclick={() => newFeedbackType = 'question'}
					>
						<MessageSquare class="w-4 h-4" />
						Question
					</button>
				</div>
			</div>
			
			<!-- Title -->
			<div>
				<label for="feedback-title" class="block text-sm font-medium text-gray-700 mb-2">Title</label>
				<Input 
					id="feedback-title"
					type="text" 
					placeholder="Brief summary of your feedback" 
					bind:value={newFeedbackTitle}
				/>
			</div>
			
			<!-- Description -->
			<div>
				<label for="feedback-desc" class="block text-sm font-medium text-gray-700 mb-2">Description</label>
				<textarea
					id="feedback-desc"
					class="w-full min-h-[120px] px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
					placeholder="Provide details about your feedback..."
					bind:value={newFeedbackDescription}
				></textarea>
			</div>
			
			<!-- AI Info -->
			<div class="p-3 bg-blue-50 rounded-lg border border-blue-100">
				<div class="flex items-center gap-2 text-sm text-blue-700">
					<Sparkles class="w-4 h-4" />
					<span>Our AI will automatically categorize and prioritize your feedback while preserving your original message.</span>
				</div>
			</div>
		</div>
		
		<Dialog.Footer>
			<Button variant="outline" onclick={() => showFeedbackDialog = false}>Cancel</Button>
			<Button onclick={handleSubmitFeedback} disabled={!newFeedbackTitle || !newFeedbackDescription}>
				<Send class="w-4 h-4 mr-2" />
				Submit
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Feedback Detail Dialog -->
<Dialog.Root bind:open={showFeedbackDetailDialog}>
	<Dialog.Content class="max-w-2xl max-h-[80vh] overflow-y-auto">
		<Dialog.Header>
			<div class="flex items-start gap-2">
				{#if selectedFeedback?.feedback_type === 'bug'}
					<Bug class="w-5 h-5 text-red-500 mt-1" />
				{:else if selectedFeedback?.feedback_type === 'enhancement'}
					<Lightbulb class="w-5 h-5 text-amber-500 mt-1" />
				{:else}
					<MessageSquare class="w-5 h-5 text-blue-500 mt-1" />
				{/if}
				<Dialog.Title class="flex-1">{selectedFeedback?.title}</Dialog.Title>
			</div>
			<div class="flex flex-wrap gap-2 mt-2">
				{#if selectedFeedback?.status}
					<Badge variant="outline" class={getStatusColor(selectedFeedback.status)}>
						{selectedFeedback.status.replace('_', ' ')}
					</Badge>
				{/if}
				{#if selectedFeedback?.ai_priority}
					<Badge variant="outline" class={getPriorityColor(selectedFeedback.ai_priority)}>
						{selectedFeedback.ai_priority}
					</Badge>
				{/if}
				{#if selectedFeedback?.ai_category}
					<Badge variant="outline">
						<Sparkles class="w-3 h-3 mr-1" />
						{selectedFeedback.ai_category}
					</Badge>
				{/if}
			</div>
		</Dialog.Header>
		
		<div class="py-4 space-y-6">
			<!-- Description -->
			<div>
				<h4 class="text-sm font-medium text-gray-700 mb-2">Description</h4>
				<p class="text-gray-600">{selectedFeedback?.description}</p>
			</div>
			
			<!-- AI Summary -->
			{#if selectedFeedback?.ai_summary}
				<div class="p-3 bg-blue-50 rounded-lg border border-blue-100">
					<div class="flex items-center gap-1 text-xs text-blue-600 mb-1">
						<Sparkles class="w-3 h-3" />
						AI Summary
					</div>
					<p class="text-sm text-blue-800">{selectedFeedback.ai_summary}</p>
				</div>
			{/if}
			
			<!-- Meta -->
			<div class="flex items-center gap-4 text-sm text-gray-500">
				<span>By {selectedFeedback?.author_name}</span>
				<span>•</span>
				<span>{selectedFeedback?.created_at}</span>
				<span>•</span>
				<div class="flex items-center gap-2">
					<ThumbsUp class="w-4 h-4" />
					{selectedFeedback?.upvotes}
					<ThumbsDown class="w-4 h-4 ml-2" />
					{selectedFeedback?.downvotes}
				</div>
			</div>
			
			<!-- Comments -->
			<div>
				<h4 class="text-sm font-medium text-gray-700 mb-3">
					Comments ({feedbackComments[selectedFeedback?.id]?.length || 0})
				</h4>
				
				<div class="space-y-3 mb-4">
					{#if feedbackComments[selectedFeedback?.id]?.length > 0}
						{#each feedbackComments[selectedFeedback?.id] as comment}
							<div class="p-3 rounded-lg {comment.is_official ? 'bg-blue-50 border border-blue-100' : 'bg-gray-50'}">
								<div class="flex items-center gap-2 mb-1">
									<span class="font-medium text-gray-900 text-sm">{comment.author_name}</span>
									{#if comment.is_official}
										<Badge variant="outline" class="text-xs bg-blue-100 text-blue-700 border-blue-200">Official</Badge>
									{/if}
									<span class="text-xs text-gray-400">{comment.created_at}</span>
								</div>
								<p class="text-sm text-gray-600">{comment.content}</p>
							</div>
						{/each}
					{:else}
						<p class="text-sm text-gray-500 py-4 text-center">No comments yet. Be the first to comment!</p>
					{/if}
				</div>
				
				<!-- Add Comment -->
				<div class="flex gap-2">
					<Input 
						type="text" 
						placeholder="Add a comment..." 
						bind:value={newComment}
						class="flex-1"
					/>
					<Button onclick={() => selectedFeedback && handleAddComment(selectedFeedback.id)} disabled={!newComment.trim()}>
						<Send class="w-4 h-4" />
					</Button>
				</div>
			</div>
		</div>
		
		<Dialog.Footer>
			<Button variant="outline" onclick={() => showFeedbackDetailDialog = false}>Close</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Renter Swap Property Dialog -->
<Dialog.Root bind:open={showRenterSwapDialog}>
	<Dialog.Content class="max-w-xl">
		<Dialog.Header>
			<Dialog.Title>Change Rental Property</Dialog.Title>
			<Dialog.Description>
				Select a new property to rent. Your current lease will be transferred.
			</Dialog.Description>
		</Dialog.Header>
		
		<div class="py-4">
			{#if renterProperty}
				{@const currentImgSrc = renterProperty._poolData?.images?.isometric || renterProperty.image}
				<div class="mb-4 p-3 bg-gray-50 rounded-lg flex gap-3">
					{#if currentImgSrc}
						<div class="w-16 h-14 flex-shrink-0 rounded overflow-hidden">
							<img 
								src={currentImgSrc.startsWith?.('data:') ? currentImgSrc : `data:image/png;base64,${currentImgSrc}`}
								alt={renterProperty.address}
								class="w-full h-full object-cover"
							/>
						</div>
					{/if}
					<div>
						<div class="text-xs text-gray-500 mb-1">Current Property</div>
						<div class="font-medium text-gray-900">{renterProperty.address}</div>
						<div class="text-sm text-gray-600">{renterProperty.suburb}</div>
					</div>
				</div>
			{/if}
			
			<div class="text-sm font-medium text-gray-700 mb-3">Available Properties</div>
			<div class="space-y-3 max-h-72 overflow-y-auto">
				{#each properties.filter(p => p.id !== renterProperty?.id) as property}
					{@const swapPropAny = property as any}
					{@const swapImgSrc = swapPropAny._poolData?.images?.isometric || swapPropAny.image}
					<button 
						onclick={() => { renterSwapProperty(property); showRenterSwapDialog = false; }}
						class="w-full flex gap-3 p-3 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition text-left group"
					>
						<!-- Thumbnail -->
						{#if swapImgSrc}
							<div class="w-20 h-16 flex-shrink-0 rounded overflow-hidden bg-gray-100">
								<img 
									src={swapImgSrc.startsWith?.('data:') ? swapImgSrc : `data:image/png;base64,${swapImgSrc}`}
									alt={property.address}
									class="w-full h-full object-cover group-hover:scale-105 transition-transform"
								/>
							</div>
						{:else}
							<div class="w-20 h-16 flex-shrink-0 rounded bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
								<Home class="w-6 h-6 text-gray-300" />
							</div>
						{/if}
						
						<!-- Details -->
						<div class="flex-1 min-w-0">
							<div class="font-medium text-gray-900 truncate">{property.address}</div>
							<div class="text-sm text-gray-500 flex items-center gap-2">
								<span>{property.suburb}</span>
								<span>•</span>
								<span class="flex items-center gap-1">
									<BedDouble class="w-3 h-3" />
									{property.bedrooms}
								</span>
								<span class="flex items-center gap-1">
									<Bath class="w-3 h-3" />
									{property.bathrooms}
								</span>
							</div>
							<div class="text-sm font-semibold text-blue-600 mt-1">
								${Math.round((property.valuation_aud || 800000) * 0.004).toLocaleString()}/month
							</div>
						</div>
					</button>
				{/each}
			</div>
		</div>
		
		<Dialog.Footer>
			<Button variant="outline" onclick={() => showRenterSwapDialog = false}>Cancel</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Add Property Dialog -->
<Dialog.Root bind:open={showAddPropertyDialog}>
	<Dialog.Content class="max-w-2xl max-h-[90vh] overflow-y-auto">
		<Dialog.Header>
			<Dialog.Title class="flex items-center gap-2">
				<Plus class="w-5 h-5 text-green-600" />
				Add New Property
			</Dialog.Title>
			<Dialog.Description>Add a simulated property to the network (like realestate.com.au listing)</Dialog.Description>
		</Dialog.Header>
		
		<div class="space-y-5 py-4">
			<!-- Location Section -->
			<div>
				<div class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
					<MapPin class="w-4 h-4" />
					Location
				</div>
				<div class="grid grid-cols-4 gap-3">
					<div class="col-span-4">
						<label for="prop-address" class="block text-sm text-gray-600 mb-1">Street Address *</label>
						<input 
							id="prop-address"
							type="text" 
							bind:value={newPropertyForm.address} 
							placeholder="e.g., 105 Gregory Street"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					
					<div class="col-span-2">
						<label for="prop-suburb" class="block text-sm text-gray-600 mb-1">Suburb *</label>
						<input 
							id="prop-suburb"
							type="text" 
							bind:value={newPropertyForm.suburb} 
							placeholder="e.g., Wembley"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					
					<div>
						<label for="prop-state" class="block text-sm text-gray-600 mb-1">State</label>
						<select 
							id="prop-state"
							bind:value={newPropertyForm.state}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						>
							{#each australianStates as state}
								<option value={state}>{state}</option>
							{/each}
						</select>
					</div>
					
					<div>
						<label for="prop-postcode" class="block text-sm text-gray-600 mb-1">Postcode</label>
						<input 
							id="prop-postcode"
							type="text" 
							bind:value={newPropertyForm.postcode} 
							placeholder="6014"
							maxlength="4"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
				</div>
			</div>
			
			<!-- Property Details Section -->
			<div>
				<div class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
					<Home class="w-4 h-4" />
					Property Details
				</div>
				<div class="grid grid-cols-4 gap-3">
					<div>
						<label for="prop-type" class="block text-sm text-gray-600 mb-1">Type</label>
						<select 
							id="prop-type"
							bind:value={newPropertyForm.property_type}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						>
							{#each propertyTypes as ptype}
								<option value={ptype}>{ptype.charAt(0).toUpperCase() + ptype.slice(1)}</option>
							{/each}
						</select>
					</div>
					
					<div>
						<label for="prop-beds" class="block text-sm text-gray-600 mb-1">
							<BedDouble class="w-3 h-3 inline mr-1" />Beds
						</label>
						<input 
							id="prop-beds"
							type="number" 
							bind:value={newPropertyForm.bedrooms} 
							min="0" 
							max="10"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					
					<div>
						<label for="prop-baths" class="block text-sm text-gray-600 mb-1">
							<Bath class="w-3 h-3 inline mr-1" />Baths
						</label>
						<input 
							id="prop-baths"
							type="number" 
							bind:value={newPropertyForm.bathrooms} 
							min="0" 
							max="10"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					
					<div>
						<label for="prop-cars" class="block text-sm text-gray-600 mb-1">
							<Car class="w-3 h-3 inline mr-1" />Cars
						</label>
						<input 
							id="prop-cars"
							type="number" 
							bind:value={newPropertyForm.car_spaces} 
							min="0" 
							max="10"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					
					<div>
						<label for="prop-land" class="block text-sm text-gray-600 mb-1">Land (m²)</label>
						<input 
							id="prop-land"
							type="number" 
							bind:value={newPropertyForm.land_size_sqm} 
							min="0" 
							step="10"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					
					<div>
						<label for="prop-floor" class="block text-sm text-gray-600 mb-1">Floor (m²)</label>
						<input 
							id="prop-floor"
							type="number" 
							bind:value={newPropertyForm.floor_size_sqm} 
							min="0" 
							step="10"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					
					<div>
						<label for="prop-year" class="block text-sm text-gray-600 mb-1">Year Built</label>
						<input 
							id="prop-year"
							type="number" 
							bind:value={newPropertyForm.year_built} 
							min="1900" 
							max="2026"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
				</div>
			</div>
			
			<!-- Financials Section -->
			<div>
				<div class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
					<DollarSign class="w-4 h-4" />
					Financials
				</div>
				<div class="grid grid-cols-2 gap-3">
					<div>
						<label for="prop-valuation" class="block text-sm text-gray-600 mb-1">Valuation (AUD)</label>
						<input 
							id="prop-valuation"
							type="number" 
							bind:value={newPropertyForm.valuation_aud} 
							min="50000" 
							step="10000"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					
					<div>
						<label for="prop-yield" class="block text-sm text-gray-600 mb-1">Expected Yield (%)</label>
						<input 
							id="prop-yield"
							type="number" 
							bind:value={newPropertyForm.yield_percent} 
							min="0" 
							max="15" 
							step="0.1"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
				</div>
			</div>
			
			<!-- Features Section -->
			<div>
				<div class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
					<Sparkles class="w-4 h-4" />
					Features
				</div>
				<div class="flex flex-wrap gap-2 max-h-24 overflow-y-auto">
					{#each availableFeatures as feature}
						<button
							type="button"
							onclick={() => toggleFeature(feature)}
							class="px-3 py-1.5 text-sm rounded-full border transition {newPropertyForm.features.includes(feature) ? 'bg-blue-100 border-blue-400 text-blue-700' : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-gray-300'}"
						>
							{#if newPropertyForm.features.includes(feature)}
								<Check class="w-3 h-3 inline mr-1" />
							{/if}
							{feature}
						</button>
					{/each}
				</div>
			</div>
			
			<!-- What's Special Section -->
			<div>
				<div class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
					<Award class="w-4 h-4" />
					What's Special (Highlights)
				</div>
				<div class="flex flex-wrap gap-2 max-h-24 overflow-y-auto">
					{#each availableHighlights as highlight}
						<button
							type="button"
							onclick={() => toggleHighlight(highlight)}
							class="px-3 py-1.5 text-sm rounded-full border transition {newPropertyForm.highlights.includes(highlight) ? 'bg-amber-100 border-amber-400 text-amber-700' : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-gray-300'}"
						>
							{#if newPropertyForm.highlights.includes(highlight)}
								<Check class="w-3 h-3 inline mr-1" />
							{/if}
							{highlight}
						</button>
					{/each}
				</div>
			</div>
			
			<!-- Costs & Rental Section (WA-specific) -->
			<div>
				<div class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
					<FileText class="w-4 h-4" />
					Annual Costs & Rental (WA)
				</div>
				<div class="grid grid-cols-4 gap-3">
					<div>
						<label for="prop-council" class="block text-sm text-gray-600 mb-1">Council Rates</label>
						<input 
							id="prop-council"
							type="number" 
							bind:value={newPropertyForm.council_rates} 
							min="0" 
							step="100"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					<div>
						<label for="prop-water" class="block text-sm text-gray-600 mb-1">Water Rates</label>
						<input 
							id="prop-water"
							type="number" 
							bind:value={newPropertyForm.water_rates} 
							min="0" 
							step="100"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					<div>
						<label for="prop-strata" class="block text-sm text-gray-600 mb-1">Strata Fees</label>
						<input 
							id="prop-strata"
							type="number" 
							bind:value={newPropertyForm.strata_fees} 
							min="0" 
							step="100"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					<div>
						<label for="prop-rent" class="block text-sm text-gray-600 mb-1">Est. Rent/week</label>
						<input 
							id="prop-rent"
							type="number" 
							bind:value={newPropertyForm.estimated_rent_pw} 
							min="0" 
							step="10"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
				</div>
			</div>
			
			<div class="bg-blue-50 text-blue-800 px-3 py-2 rounded-lg text-sm">
				<Info class="w-4 h-4 inline mr-1" />
				Properties added here are for simulation purposes only. No real assets are created.
			</div>
		</div>
		
		<Dialog.Footer>
			<Button variant="outline" onclick={() => showAddPropertyDialog = false}>Cancel</Button>
			<Button onclick={handleAddProperty} disabled={!newPropertyForm.address || !newPropertyForm.suburb}>
				<Plus class="w-4 h-4 mr-1" />
				Add Property
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Edit Property Dialog -->
<Dialog.Root bind:open={showEditPropertyDialog}>
	<Dialog.Content class="max-w-2xl max-h-[90vh] overflow-y-auto">
		<Dialog.Header>
			<Dialog.Title class="flex items-center gap-2">
				<Edit class="w-5 h-5 text-blue-600" />
				Edit Property
			</Dialog.Title>
			<Dialog.Description>Update property details in the simulation</Dialog.Description>
		</Dialog.Header>
		
		<div class="space-y-5 py-4">
			<!-- Location Section -->
			<div>
				<div class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
					<MapPin class="w-4 h-4" />
					Location
				</div>
				<div class="grid grid-cols-4 gap-3">
					<div class="col-span-4">
						<label for="edit-prop-address" class="block text-sm text-gray-600 mb-1">Street Address *</label>
						<input 
							id="edit-prop-address"
							type="text" 
							bind:value={newPropertyForm.address} 
							placeholder="e.g., 105 Gregory Street"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					
					<div class="col-span-2">
						<label for="edit-prop-suburb" class="block text-sm text-gray-600 mb-1">Suburb *</label>
						<input 
							id="edit-prop-suburb"
							type="text" 
							bind:value={newPropertyForm.suburb} 
							placeholder="e.g., Wembley"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					
					<div>
						<label for="edit-prop-state" class="block text-sm text-gray-600 mb-1">State</label>
						<select 
							id="edit-prop-state"
							bind:value={newPropertyForm.state}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						>
							{#each australianStates as state}
								<option value={state}>{state}</option>
							{/each}
						</select>
					</div>
					
					<div>
						<label for="edit-prop-postcode" class="block text-sm text-gray-600 mb-1">Postcode</label>
						<input 
							id="edit-prop-postcode"
							type="text" 
							bind:value={newPropertyForm.postcode} 
							placeholder="6014"
							maxlength="4"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
				</div>
			</div>
			
			<!-- Property Details Section -->
			<div>
				<div class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
					<Home class="w-4 h-4" />
					Property Details
				</div>
				<div class="grid grid-cols-4 gap-3">
					<div>
						<label for="edit-prop-type" class="block text-sm text-gray-600 mb-1">Type</label>
						<select 
							id="edit-prop-type"
							bind:value={newPropertyForm.property_type}
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						>
							{#each propertyTypes as ptype}
								<option value={ptype}>{ptype.charAt(0).toUpperCase() + ptype.slice(1)}</option>
							{/each}
						</select>
					</div>
					
					<div>
						<label for="edit-prop-beds" class="block text-sm text-gray-600 mb-1">
							<BedDouble class="w-3 h-3 inline mr-1" />Beds
						</label>
						<input 
							id="edit-prop-beds"
							type="number" 
							bind:value={newPropertyForm.bedrooms} 
							min="0" 
							max="10"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					
					<div>
						<label for="edit-prop-baths" class="block text-sm text-gray-600 mb-1">
							<Bath class="w-3 h-3 inline mr-1" />Baths
						</label>
						<input 
							id="edit-prop-baths"
							type="number" 
							bind:value={newPropertyForm.bathrooms} 
							min="0" 
							max="10"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					
					<div>
						<label for="edit-prop-cars" class="block text-sm text-gray-600 mb-1">
							<Car class="w-3 h-3 inline mr-1" />Cars
						</label>
						<input 
							id="edit-prop-cars"
							type="number" 
							bind:value={newPropertyForm.car_spaces} 
							min="0" 
							max="10"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					
					<div>
						<label for="edit-prop-land" class="block text-sm text-gray-600 mb-1">Land (m²)</label>
						<input 
							id="edit-prop-land"
							type="number" 
							bind:value={newPropertyForm.land_size_sqm} 
							min="0" 
							step="10"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					
					<div>
						<label for="edit-prop-floor" class="block text-sm text-gray-600 mb-1">Floor (m²)</label>
						<input 
							id="edit-prop-floor"
							type="number" 
							bind:value={newPropertyForm.floor_size_sqm} 
							min="0" 
							step="10"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					
					<div>
						<label for="edit-prop-year" class="block text-sm text-gray-600 mb-1">Year Built</label>
						<input 
							id="edit-prop-year"
							type="number" 
							bind:value={newPropertyForm.year_built} 
							min="1900" 
							max="2026"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
				</div>
			</div>
			
			<!-- Financials Section -->
			<div>
				<div class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
					<DollarSign class="w-4 h-4" />
					Financials
				</div>
				<div class="grid grid-cols-2 gap-3">
					<div>
						<label for="edit-prop-valuation" class="block text-sm text-gray-600 mb-1">Valuation (AUD)</label>
						<input 
							id="edit-prop-valuation"
							type="number" 
							bind:value={newPropertyForm.valuation_aud} 
							min="50000" 
							step="10000"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					
					<div>
						<label for="edit-prop-yield" class="block text-sm text-gray-600 mb-1">Expected Yield (%)</label>
						<input 
							id="edit-prop-yield"
							type="number" 
							bind:value={newPropertyForm.yield_percent} 
							min="0" 
							max="15" 
							step="0.1"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
				</div>
			</div>
			
			<!-- Features Section -->
			<div>
				<div class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
					<Sparkles class="w-4 h-4" />
					Features
				</div>
				<div class="flex flex-wrap gap-2 max-h-24 overflow-y-auto">
					{#each availableFeatures as feature}
						<button
							type="button"
							onclick={() => toggleFeature(feature)}
							class="px-3 py-1.5 text-sm rounded-full border transition {newPropertyForm.features.includes(feature) ? 'bg-blue-100 border-blue-400 text-blue-700' : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-gray-300'}"
						>
							{#if newPropertyForm.features.includes(feature)}
								<Check class="w-3 h-3 inline mr-1" />
							{/if}
							{feature}
						</button>
					{/each}
				</div>
			</div>
			
			<!-- What's Special Section -->
			<div>
				<div class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
					<Award class="w-4 h-4" />
					What's Special (Highlights)
				</div>
				<div class="flex flex-wrap gap-2 max-h-24 overflow-y-auto">
					{#each availableHighlights as highlight}
						<button
							type="button"
							onclick={() => toggleHighlight(highlight)}
							class="px-3 py-1.5 text-sm rounded-full border transition {newPropertyForm.highlights.includes(highlight) ? 'bg-amber-100 border-amber-400 text-amber-700' : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-gray-300'}"
						>
							{#if newPropertyForm.highlights.includes(highlight)}
								<Check class="w-3 h-3 inline mr-1" />
							{/if}
							{highlight}
						</button>
					{/each}
				</div>
			</div>
			
			<!-- Costs & Rental Section (WA-specific) -->
			<div>
				<div class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
					<FileText class="w-4 h-4" />
					Annual Costs & Rental (WA)
				</div>
				<div class="grid grid-cols-4 gap-3">
					<div>
						<label for="edit-prop-council" class="block text-sm text-gray-600 mb-1">Council Rates</label>
						<input 
							id="edit-prop-council"
							type="number" 
							bind:value={newPropertyForm.council_rates} 
							min="0" 
							step="100"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					<div>
						<label for="edit-prop-water" class="block text-sm text-gray-600 mb-1">Water Rates</label>
						<input 
							id="edit-prop-water"
							type="number" 
							bind:value={newPropertyForm.water_rates} 
							min="0" 
							step="100"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					<div>
						<label for="edit-prop-strata" class="block text-sm text-gray-600 mb-1">Strata Fees</label>
						<input 
							id="edit-prop-strata"
							type="number" 
							bind:value={newPropertyForm.strata_fees} 
							min="0" 
							step="100"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					<div>
						<label for="edit-prop-rent" class="block text-sm text-gray-600 mb-1">Est. Rent/week</label>
						<input 
							id="edit-prop-rent"
							type="number" 
							bind:value={newPropertyForm.estimated_rent_pw} 
							min="0" 
							step="10"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
				</div>
			</div>
		</div>
		
		<Dialog.Footer>
			<Button variant="outline" onclick={() => { showEditPropertyDialog = false; editingProperty = null; }}>Cancel</Button>
			<Button onclick={handleEditProperty} disabled={!newPropertyForm.address || !newPropertyForm.suburb}>
				<Check class="w-4 h-4 mr-1" />
				Save Changes
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Delete Property Dialog -->
<Dialog.Root bind:open={showDeletePropertyDialog}>
	<Dialog.Content class="max-w-md">
		<Dialog.Header>
			<Dialog.Title class="flex items-center gap-2 text-red-600">
				<Trash2 class="w-5 h-5" />
				Remove Property
			</Dialog.Title>
			<Dialog.Description>This action cannot be undone in the simulation</Dialog.Description>
		</Dialog.Header>
		
		<div class="py-4">
			{#if editingProperty}
				<div class="bg-gray-50 rounded-lg p-4 mb-4">
					<div class="font-medium text-gray-900">{editingProperty.address}</div>
					<div class="text-sm text-gray-500">{editingProperty.suburb}, {editingProperty.state}</div>
					<div class="text-sm text-gray-500 mt-1">
						{editingProperty.bedrooms} bed, {editingProperty.bathrooms} bath • ${editingProperty.valuation_aud?.toLocaleString()}
					</div>
				</div>
				
				{#if holdings.some(h => h.property_id === editingProperty.id)}
					<div class="bg-amber-50 text-amber-800 px-3 py-2 rounded-lg text-sm mb-4">
						<AlertTriangle class="w-4 h-4 inline mr-1" />
						You have investments in this property. They will be removed.
					</div>
				{/if}
				
				{#if renterProperty?.id === editingProperty.id}
					<div class="bg-amber-50 text-amber-800 px-3 py-2 rounded-lg text-sm mb-4">
						<AlertTriangle class="w-4 h-4 inline mr-1" />
						You are renting this property. Your lease will be terminated.
					</div>
				{/if}
				
				<p class="text-gray-600">Are you sure you want to remove this property from the simulation?</p>
			{/if}
		</div>
		
		<Dialog.Footer>
			<Button variant="outline" onclick={() => { showDeletePropertyDialog = false; editingProperty = null; }}>Cancel</Button>
			<Button variant="destructive" onclick={handleDeleteProperty}>
				<Trash2 class="w-4 h-4 mr-1" />
				Remove Property
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Manage Properties Dialog -->
<Dialog.Root bind:open={showManagePropertiesDialog}>
	<Dialog.Content class="max-w-3xl max-h-[80vh] overflow-y-auto">
		<Dialog.Header>
			<Dialog.Title class="flex items-center gap-2">
				<Settings class="w-5 h-5 text-gray-600" />
				Manage Properties
			</Dialog.Title>
			<Dialog.Description>{properties.length} properties in the simulation network</Dialog.Description>
		</Dialog.Header>
		
		<div class="py-4">
			<div class="flex justify-end mb-4">
				<Button size="sm" onclick={() => { showManagePropertiesDialog = false; openAddProperty(); }}>
					<Plus class="w-4 h-4 mr-1" />
					Add New Property
				</Button>
			</div>
			
			<div class="space-y-2">
				{#each properties as property}
					<div class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
						<div class="flex-1">
							<div class="flex items-center gap-2">
								<div class="font-medium text-gray-900">{property.address}</div>
								<Badge variant="secondary" class="text-xs">{property.property_type}</Badge>
							</div>
							<div class="text-sm text-gray-500">
								{property.suburb}, {property.state} • {property.bedrooms} bed, {property.bathrooms} bath
							</div>
							<div class="flex items-center gap-4 mt-1 text-sm">
								<span class="text-gray-700">${property.valuation_aud?.toLocaleString()}</span>
								<span class="text-green-600">{property.yield_percent}% yield</span>
								{#if holdings.some(h => h.property_id === property.id)}
									<Badge variant="outline" class="text-xs text-blue-600 border-blue-200">Invested</Badge>
								{/if}
								{#if renterProperty?.id === property.id}
									<Badge variant="outline" class="text-xs text-purple-600 border-purple-200">Renting</Badge>
								{/if}
							</div>
						</div>
						<div class="flex items-center gap-2">
							<Button size="sm" variant="ghost" onclick={() => { showManagePropertiesDialog = false; openEditProperty(property); }}>
								<Edit class="w-4 h-4" />
							</Button>
							<Button size="sm" variant="ghost" class="text-red-600 hover:text-red-700 hover:bg-red-50" onclick={() => { showManagePropertiesDialog = false; openDeleteProperty(property); }}>
								<Trash2 class="w-4 h-4" />
							</Button>
						</div>
					</div>
				{/each}
			</div>
			
			{#if properties.length === 0}
				<div class="text-center py-8 text-gray-500">
					<Building class="w-12 h-12 mx-auto mb-2 opacity-50" />
					<p>No properties in the network</p>
					<Button size="sm" class="mt-3" onclick={() => { showManagePropertiesDialog = false; openAddProperty(); }}>
						Add Your First Property
					</Button>
				</div>
			{/if}
		</div>
		
		<Dialog.Footer>
			<Button variant="outline" onclick={() => showManagePropertiesDialog = false}>Close</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Property Detail Dialog -->
<Dialog.Root bind:open={showPropertyDetailDialog}>
	<Dialog.Content class="max-w-3xl max-h-[90vh] overflow-y-auto">
		{#if detailProperty}
			<Dialog.Header>
				<Dialog.Title class="text-xl">
					{detailProperty.address}
				</Dialog.Title>
				<Dialog.Description>
					{detailProperty.suburb}, {detailProperty.state} {detailProperty.postcode || ''}
				</Dialog.Description>
			</Dialog.Header>
			
			<!-- Tab Navigation -->
			<div class="flex border-b border-gray-200 mb-4">
				<button 
					onclick={() => propertyDetailTab = 'overview'}
					class="px-4 py-2 text-sm font-medium border-b-2 transition {propertyDetailTab === 'overview' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}"
				>
					Overview
				</button>
				<button 
					onclick={() => propertyDetailTab = 'facts'}
					class="px-4 py-2 text-sm font-medium border-b-2 transition {propertyDetailTab === 'facts' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}"
				>
					Facts & Features
				</button>
				<button 
					onclick={() => propertyDetailTab = 'costs'}
					class="px-4 py-2 text-sm font-medium border-b-2 transition {propertyDetailTab === 'costs' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}"
				>
					Costs & Returns
				</button>
				<button 
					onclick={() => propertyDetailTab = 'history'}
					class="px-4 py-2 text-sm font-medium border-b-2 transition {propertyDetailTab === 'history' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}"
				>
					Price History
				</button>
				<button 
					onclick={() => propertyDetailTab = 'services'}
					class="px-4 py-2 text-sm font-medium border-b-2 transition {propertyDetailTab === 'services' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}"
				>
					Services
				</button>
			</div>
			
			<!-- Tab Content -->
			{#if propertyDetailTab === 'overview'}
				<div class="space-y-4">
					<!-- Hero Stats -->
					<div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6">
						<div class="flex items-baseline gap-3 mb-2">
							<span class="text-3xl font-bold text-gray-900">${detailProperty.valuation_aud?.toLocaleString()}</span>
							<span class="text-lg text-gray-500">${getPricePerSqm(detailProperty).toLocaleString()}/m²</span>
						</div>
						<div class="flex items-center gap-6 text-lg text-gray-700">
							<div class="flex items-center gap-2">
								<BedDouble class="w-5 h-5" />
								<span>{detailProperty.bedrooms} beds</span>
							</div>
							<div class="flex items-center gap-2">
								<Bath class="w-5 h-5" />
								<span>{detailProperty.bathrooms} baths</span>
							</div>
							<div class="flex items-center gap-2">
								<Car class="w-5 h-5" />
								<span>{detailProperty.car_spaces || 1} cars</span>
							</div>
							<div class="flex items-center gap-2">
								<Ruler class="w-5 h-5" />
								<span>{detailProperty.land_size_sqm > 0 ? `${detailProperty.land_size_sqm}m² land` : `${detailProperty.floor_size_sqm}m² floor`}</span>
							</div>
						</div>
					</div>
					
					<!-- What's Special -->
					{#if detailProperty.highlights && detailProperty.highlights.length > 0}
						<div>
							<h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
								<Sparkles class="w-5 h-5 text-amber-500" />
								What's Special
							</h3>
							<ul class="grid grid-cols-2 gap-2">
								{#each detailProperty.highlights as highlight}
									<li class="flex items-center gap-2 text-gray-700">
										<CheckCircle class="w-4 h-4 text-green-500" />
										{highlight}
									</li>
								{/each}
							</ul>
						</div>
					{/if}
					
					<!-- Quick Stats Grid -->
					<div class="grid grid-cols-4 gap-4">
						<div class="bg-gray-50 rounded-lg p-4 text-center">
							<div class="text-2xl font-bold text-green-600">{detailProperty.yield_percent}%</div>
							<div class="text-xs text-gray-500">Gross Yield</div>
						</div>
						<div class="bg-gray-50 rounded-lg p-4 text-center">
							<div class="text-2xl font-bold text-blue-600">{getNetYield(detailProperty).toFixed(1)}%</div>
							<div class="text-xs text-gray-500">Net Yield</div>
						</div>
						<div class="bg-gray-50 rounded-lg p-4 text-center">
							<div class="text-2xl font-bold text-gray-700">{detailProperty.year_built}</div>
							<div class="text-xs text-gray-500">Year Built</div>
						</div>
						<div class="bg-gray-50 rounded-lg p-4 text-center">
							<div class="text-2xl font-bold text-gray-700">{detailProperty.page_views?.toLocaleString()}</div>
							<div class="text-xs text-gray-500">Page Views</div>
						</div>
					</div>
					
					<!-- Rental Estimate -->
					{#if detailProperty.estimated_rent_pw}
						<div class="bg-blue-50 rounded-lg p-4">
							<div class="flex items-center justify-between">
								<div>
									<div class="text-sm font-medium text-blue-800">Estimated Rental Income</div>
									<div class="text-xs text-blue-600">Based on comparable properties in {detailProperty.suburb}</div>
								</div>
								<div class="text-right">
									<div class="text-xl font-bold text-blue-800">${detailProperty.estimated_rent_pw}/week</div>
									<div class="text-sm text-blue-600">${(detailProperty.estimated_rent_pw * 52).toLocaleString()}/year</div>
								</div>
							</div>
						</div>
					{/if}
				</div>
				
			{:else if propertyDetailTab === 'facts'}
				<div class="space-y-6">
					<!-- Property Type & Size -->
					<div>
						<h3 class="text-lg font-semibold text-gray-900 mb-3">Property Details</h3>
						<div class="grid grid-cols-2 gap-4">
							<div class="flex justify-between py-2 border-b border-gray-100">
								<span class="text-gray-600">Property Type</span>
								<span class="font-medium capitalize">{detailProperty.property_type}</span>
							</div>
							<div class="flex justify-between py-2 border-b border-gray-100">
								<span class="text-gray-600">Year Built</span>
								<span class="font-medium">{detailProperty.year_built}</span>
							</div>
							<div class="flex justify-between py-2 border-b border-gray-100">
								<span class="text-gray-600">Land Size</span>
								<span class="font-medium">{detailProperty.land_size_sqm > 0 ? `${detailProperty.land_size_sqm}m²` : 'N/A'}</span>
							</div>
							<div class="flex justify-between py-2 border-b border-gray-100">
								<span class="text-gray-600">Floor Size</span>
								<span class="font-medium">{detailProperty.floor_size_sqm}m²</span>
							</div>
							<div class="flex justify-between py-2 border-b border-gray-100">
								<span class="text-gray-600">Bedrooms</span>
								<span class="font-medium">{detailProperty.bedrooms}</span>
							</div>
							<div class="flex justify-between py-2 border-b border-gray-100">
								<span class="text-gray-600">Bathrooms</span>
								<span class="font-medium">{detailProperty.bathrooms}</span>
							</div>
							<div class="flex justify-between py-2 border-b border-gray-100">
								<span class="text-gray-600">Car Spaces</span>
								<span class="font-medium">{detailProperty.car_spaces || 1}</span>
							</div>
							<div class="flex justify-between py-2 border-b border-gray-100">
								<span class="text-gray-600">Listing Status</span>
								<Badge variant="outline" class="capitalize">{detailProperty.listing_status}</Badge>
							</div>
						</div>
					</div>
					
					<!-- Features -->
					{#if detailProperty.features && detailProperty.features.length > 0}
						<div>
							<h3 class="text-lg font-semibold text-gray-900 mb-3">Features</h3>
							<div class="flex flex-wrap gap-2">
								{#each detailProperty.features as feature}
									<Badge variant="outline" class="py-1 px-3">{feature}</Badge>
								{/each}
							</div>
						</div>
					{/if}
				</div>
				
			{:else if propertyDetailTab === 'costs'}
				<div class="space-y-6">
					<!-- Annual Costs -->
					<div>
						<h3 class="text-lg font-semibold text-gray-900 mb-3">Annual Costs (WA)</h3>
						<div class="bg-gray-50 rounded-lg p-4 space-y-3">
							<div class="flex justify-between py-2 border-b border-gray-200">
								<span class="text-gray-600">Council Rates</span>
								<span class="font-medium">${(detailProperty.council_rates || 0).toLocaleString()}/year</span>
							</div>
							<div class="flex justify-between py-2 border-b border-gray-200">
								<span class="text-gray-600">Water Rates</span>
								<span class="font-medium">${(detailProperty.water_rates || 0).toLocaleString()}/year</span>
							</div>
							{#if detailProperty.strata_fees > 0}
								<div class="flex justify-between py-2 border-b border-gray-200">
									<span class="text-gray-600">Strata Fees</span>
									<span class="font-medium">${detailProperty.strata_fees.toLocaleString()}/year</span>
								</div>
							{/if}
							<div class="flex justify-between py-2 font-semibold">
								<span class="text-gray-900">Total Annual Costs</span>
								<span class="text-gray-900">${getAnnualCosts(detailProperty).toLocaleString()}/year</span>
							</div>
						</div>
					</div>
					
					<!-- Returns Calculator -->
					<div>
						<h3 class="text-lg font-semibold text-gray-900 mb-3">Returns Analysis</h3>
						<div class="grid grid-cols-2 gap-4">
							<div class="bg-green-50 rounded-lg p-4">
								<div class="text-sm text-green-700 mb-1">Gross Rental Income</div>
								<div class="text-2xl font-bold text-green-800">
									${((detailProperty.estimated_rent_pw || 0) * 52).toLocaleString()}/year
								</div>
								<div class="text-xs text-green-600">${detailProperty.estimated_rent_pw}/week × 52</div>
							</div>
							<div class="bg-red-50 rounded-lg p-4">
								<div class="text-sm text-red-700 mb-1">Annual Costs</div>
								<div class="text-2xl font-bold text-red-800">
									${getAnnualCosts(detailProperty).toLocaleString()}/year
								</div>
								<div class="text-xs text-red-600">Rates + Water + Strata</div>
							</div>
							<div class="bg-blue-50 rounded-lg p-4">
								<div class="text-sm text-blue-700 mb-1">Net Rental Income</div>
								<div class="text-2xl font-bold text-blue-800">
									${(((detailProperty.estimated_rent_pw || 0) * 52) - getAnnualCosts(detailProperty)).toLocaleString()}/year
								</div>
								<div class="text-xs text-blue-600">After costs (excl. management)</div>
							</div>
							<div class="bg-purple-50 rounded-lg p-4">
								<div class="text-sm text-purple-700 mb-1">Net Yield</div>
								<div class="text-2xl font-bold text-purple-800">
									{getNetYield(detailProperty).toFixed(2)}%
								</div>
								<div class="text-xs text-purple-600">vs {detailProperty.yield_percent}% gross</div>
							</div>
						</div>
					</div>
				</div>
				
			{:else if propertyDetailTab === 'history'}
				<div class="space-y-4">
					<h3 class="text-lg font-semibold text-gray-900">Price History</h3>
					
					{#if detailProperty.price_history && detailProperty.price_history.length > 0}
						<div class="border border-gray-200 rounded-lg overflow-hidden">
							<table class="w-full">
								<thead class="bg-gray-50">
									<tr>
										<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
										<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Event</th>
										<th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Price</th>
										<th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">$/m²</th>
									</tr>
								</thead>
								<tbody class="divide-y divide-gray-200">
									{#each detailProperty.price_history as record, i}
										{@const prevPrice = detailProperty.price_history[i + 1]?.price}
										{@const changePercent = prevPrice ? ((record.price - prevPrice) / prevPrice * 100) : null}
										{@const size = detailProperty.land_size_sqm > 0 ? detailProperty.land_size_sqm : detailProperty.floor_size_sqm}
										<tr class="hover:bg-gray-50">
											<td class="px-4 py-3 text-sm text-gray-900">{record.date}</td>
											<td class="px-4 py-3 text-sm">
												<Badge variant={record.event.includes('Listed') ? 'default' : 'secondary'} class="text-xs">
													{record.event}
												</Badge>
											</td>
											<td class="px-4 py-3 text-sm text-right font-medium">
												${record.price.toLocaleString()}
												{#if changePercent !== null}
													<span class="ml-2 text-xs {changePercent >= 0 ? 'text-green-600' : 'text-red-600'}">
														{changePercent >= 0 ? '+' : ''}{changePercent.toFixed(1)}%
													</span>
												{/if}
											</td>
											<td class="px-4 py-3 text-sm text-right text-gray-500">
												${Math.round(record.price / size).toLocaleString()}/m²
											</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
						
						<!-- Capital Growth Summary -->
						{@const firstPrice = detailProperty.price_history[detailProperty.price_history.length - 1]?.price}
						{@const currentPrice = detailProperty.valuation_aud}
						{@const totalGrowth = firstPrice ? ((currentPrice - firstPrice) / firstPrice * 100) : 0}
						<div class="bg-gray-50 rounded-lg p-4">
							<div class="flex items-center justify-between">
								<div>
									<div class="text-sm font-medium text-gray-700">Total Capital Growth</div>
									<div class="text-xs text-gray-500">From first recorded sale</div>
								</div>
								<div class="text-right">
									<div class="text-xl font-bold {totalGrowth >= 0 ? 'text-green-600' : 'text-red-600'}">
										{totalGrowth >= 0 ? '+' : ''}{totalGrowth.toFixed(1)}%
									</div>
									<div class="text-sm text-gray-600">
										${(currentPrice - (firstPrice || currentPrice)).toLocaleString()}
									</div>
								</div>
							</div>
						</div>
					{:else}
						<div class="text-center py-8 text-gray-500">
							<Calendar class="w-12 h-12 mx-auto mb-2 opacity-50" />
							<p>No price history available</p>
						</div>
					{/if}
				</div>
				
			{:else if propertyDetailTab === 'services'}
				{@const propertyServices = getPropertyServiceHistory(detailProperty.id)}
				<div class="space-y-4">
					<div class="flex items-center justify-between">
						<h3 class="text-lg font-semibold text-gray-900">Service History</h3>
						<Badge variant="outline">{propertyServices.length} services</Badge>
					</div>
					
					{#if propertyServices.length > 0}
						<div class="border border-gray-200 rounded-lg overflow-hidden divide-y divide-gray-100">
							{#each propertyServices as service}
								<div class="p-4 flex items-start gap-4">
									<div class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0
										{service.type === 'task_completed' ? 'bg-green-100 text-green-600' : 
										 service.type === 'inspection' ? 'bg-blue-100 text-blue-600' : 
										 service.type === 'maintenance' ? 'bg-orange-100 text-orange-600' : 
										 'bg-gray-100 text-gray-600'}">
										{#if service.type === 'task_completed'}
											<CheckCircle class="w-5 h-5" />
										{:else if service.type === 'inspection'}
											<Search class="w-5 h-5" />
										{:else}
											<Wrench class="w-5 h-5" />
										{/if}
									</div>
									<div class="flex-1 min-w-0">
										<div class="font-medium text-gray-900">{service.description}</div>
										<div class="flex items-center gap-2 mt-1">
											<span class="text-sm text-gray-500">{service.date}</span>
											{#if service.serviceType}
												<Badge variant="outline" class="text-xs">{service.serviceType}</Badge>
											{/if}
											{#if service.status === 'completed'}
												<Badge variant="outline" class="text-xs bg-green-50 text-green-700 border-green-200">Completed</Badge>
											{:else if service.status === 'pending'}
												<Badge variant="outline" class="text-xs bg-amber-50 text-amber-700 border-amber-200">Pending</Badge>
											{/if}
										</div>
									</div>
									{#if service.amount}
										<div class="text-sm font-semibold text-gray-900">
											${service.amount.toLocaleString()}
										</div>
									{/if}
								</div>
							{/each}
						</div>
						
						<!-- Service Summary -->
						<div class="bg-gray-50 rounded-lg p-4">
							<div class="grid grid-cols-3 gap-4 text-center">
								<div>
									<div class="text-2xl font-bold text-gray-900">{propertyServices.length}</div>
									<div class="text-xs text-gray-500">Total Services</div>
								</div>
								<div>
									<div class="text-2xl font-bold text-green-600">
										{propertyServices.filter(s => s.status === 'completed').length}
									</div>
									<div class="text-xs text-gray-500">Completed</div>
								</div>
								<div>
									<div class="text-2xl font-bold text-gray-900">
										${propertyServices.filter(s => s.amount).reduce((sum, s) => sum + (s.amount || 0), 0).toLocaleString()}
									</div>
									<div class="text-xs text-gray-500">Total Cost</div>
								</div>
							</div>
						</div>
					{:else}
						<div class="text-center py-8 text-gray-500 bg-gray-50 rounded-lg">
							<Wrench class="w-12 h-12 mx-auto mb-2 opacity-50" />
							<p class="font-medium">No service history yet</p>
							<p class="text-sm mt-1">Service transactions will appear here when work is completed on this property.</p>
						</div>
					{/if}
				</div>
			{/if}
			
			<Dialog.Footer class="mt-6">
				<Button variant="outline" onclick={() => showPropertyDetailDialog = false}>Close</Button>
				<Button onclick={() => { showPropertyDetailDialog = false; openBuyDialog(detailProperty); }}>
					<DollarSign class="w-4 h-4 mr-1" />
					Invest in Property
				</Button>
			</Dialog.Footer>
		{/if}
	</Dialog.Content>
</Dialog.Root>

<!-- Role Info Dialog -->
<Dialog.Root bind:open={showRoleInfoDialog}>
	<Dialog.Content class="max-w-2xl max-h-[90vh] overflow-y-auto">
		<Dialog.Header>
			<Dialog.Title class="flex items-center gap-3">
				<div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
					<svelte:component this={roles.find(r => r.id === activeRole)?.icon || TrendingUp} class="w-5 h-5 text-blue-600" />
				</div>
				<div>
					<span class="text-xl">{roles.find(r => r.id === activeRole)?.label} Role</span>
					<p class="text-sm font-normal text-gray-500">{roles.find(r => r.id === activeRole)?.desc}</p>
				</div>
			</Dialog.Title>
		</Dialog.Header>
		
		<div class="py-4 space-y-6">
			<!-- Purpose -->
			<div>
				<h3 class="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
					<Target class="w-4 h-4 text-blue-600" />
					Purpose
				</h3>
				<p class="text-sm text-gray-600">
					{roleDetails[activeRole]?.purpose}
				</p>
			</div>
			
			<!-- Motivation -->
			<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
				<h3 class="text-sm font-semibold text-blue-900 mb-2 flex items-center gap-2">
					<Sparkles class="w-4 h-4 text-blue-600" />
					What's In It For You
				</h3>
				<p class="text-sm text-blue-800">
					{roleDetails[activeRole]?.motivation}
				</p>
			</div>
			
			<div class="grid md:grid-cols-2 gap-4">
				<!-- Rewards -->
				<div class="bg-green-50 border border-green-200 rounded-lg p-4">
					<h3 class="text-sm font-semibold text-green-900 mb-3 flex items-center gap-2">
						<Gift class="w-4 h-4 text-green-600" />
						Rewards
					</h3>
					<ul class="space-y-2">
						{#each roleDetails[activeRole]?.rewards || [] as reward}
							<li class="text-sm text-green-800 flex items-start gap-2">
								<CheckCircle class="w-4 h-4 text-green-600 shrink-0 mt-0.5" />
								{reward}
							</li>
						{/each}
					</ul>
				</div>
				
				<!-- Opportunities -->
				<div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
					<h3 class="text-sm font-semibold text-purple-900 mb-3 flex items-center gap-2">
						<Zap class="w-4 h-4 text-purple-600" />
						Opportunities
					</h3>
					<ul class="space-y-2">
						{#each roleDetails[activeRole]?.opportunities || [] as opportunity}
							<li class="text-sm text-purple-800 flex items-start gap-2">
								<ArrowUpRight class="w-4 h-4 text-purple-600 shrink-0 mt-0.5" />
								{opportunity}
							</li>
						{/each}
					</ul>
				</div>
				
				<!-- Risks -->
				<div class="bg-amber-50 border border-amber-200 rounded-lg p-4">
					<h3 class="text-sm font-semibold text-amber-900 mb-3 flex items-center gap-2">
						<AlertCircle class="w-4 h-4 text-amber-600" />
						Risks
					</h3>
					<ul class="space-y-2">
						{#each roleDetails[activeRole]?.risks || [] as risk}
							<li class="text-sm text-amber-800 flex items-start gap-2">
								<AlertCircle class="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
								{risk}
							</li>
						{/each}
					</ul>
				</div>
				
				<!-- Threats -->
				<div class="bg-red-50 border border-red-200 rounded-lg p-4">
					<h3 class="text-sm font-semibold text-red-900 mb-3 flex items-center gap-2">
						<AlertTriangle class="w-4 h-4 text-red-600" />
						Threats
					</h3>
					<ul class="space-y-2">
						{#each roleDetails[activeRole]?.threats || [] as threat}
							<li class="text-sm text-red-800 flex items-start gap-2">
								<AlertTriangle class="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
								{threat}
							</li>
						{/each}
					</ul>
				</div>
			</div>
			
			<!-- Simulation Note -->
			<div class="bg-gray-100 border border-gray-200 rounded-lg p-4 text-center">
				<p class="text-sm text-gray-600">
					🎮 This is a simulation. Explore this role risk-free with $100K in play money.
				</p>
			</div>
		</div>
		
		<Dialog.Footer>
			<Button onclick={() => showRoleInfoDialog = false}>Got it, let's explore!</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Simulation Info Dialog -->
<Dialog.Root bind:open={showSimulationInfoDialog}>
	<Dialog.Content class="max-w-xl">
		<Dialog.Header>
			<Dialog.Title class="flex items-center gap-3">
				<div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
					<Play class="w-5 h-5 text-blue-600" />
				</div>
				<div>
					<span class="text-xl">Time Simulation</span>
					<p class="text-sm font-normal text-gray-500">How the network simulation works</p>
				</div>
			</Dialog.Title>
		</Dialog.Header>
		
		<div class="py-4 space-y-5">
			<p class="text-gray-600">
				Click <strong>"+1 Month"</strong> to advance the entire network by one simulated month. 
				All roles progress together with connected financial flows.
			</p>
			
			<div class="space-y-3">
				<h4 class="font-medium text-gray-900">What happens each month:</h4>
				
				<div class="grid gap-2 text-sm">
					<div class="flex items-start gap-3 p-2 bg-green-50 rounded-lg">
						<TrendingUp class="w-4 h-4 text-green-600 mt-0.5" />
						<div>
							<span class="font-medium text-green-900">Properties Appreciate</span>
							<p class="text-green-700 text-xs">0.3-0.5% monthly growth, affecting token price</p>
						</div>
					</div>
					
					<div class="flex items-start gap-3 p-2 bg-blue-50 rounded-lg">
						<Building class="w-4 h-4 text-blue-600 mt-0.5" />
						<div>
							<span class="font-medium text-blue-900">Rent Collected</span>
							<p class="text-blue-700 text-xs">Tenants & renters pay → flows to treasury</p>
						</div>
					</div>
					
					<div class="flex items-start gap-3 p-2 bg-amber-50 rounded-lg">
						<Wrench class="w-4 h-4 text-amber-600 mt-0.5" />
						<div>
							<span class="font-medium text-amber-900">Service Providers Paid</span>
							<p class="text-amber-700 text-xs">8% of rent goes to property management</p>
						</div>
					</div>
					
					<div class="flex items-start gap-3 p-2 bg-purple-50 rounded-lg">
						<DollarSign class="w-4 h-4 text-purple-600 mt-0.5" />
						<div>
							<span class="font-medium text-purple-900">Dividends Distributed</span>
							<p class="text-purple-700 text-xs">80% of net rental income → token holders</p>
						</div>
					</div>
					
					<div class="flex items-start gap-3 p-2 bg-indigo-50 rounded-lg">
						<Landmark class="w-4 h-4 text-indigo-600 mt-0.5" />
						<div>
							<span class="font-medium text-indigo-900">Foundation Yields</span>
							<p class="text-indigo-700 text-xs">Stakers earn enhanced yield (+0.5%)</p>
						</div>
					</div>
				</div>
			</div>
			
			<div class="bg-gray-100 rounded-lg p-3 text-center">
				<p class="text-sm text-gray-600">
					💡 <strong>Tip:</strong> View the <button class="text-blue-600 underline" onclick={() => { showSimulationInfoDialog = false; activeTab = 'network'; }}>Network tab</button> to see all financial flows and the event log.
				</p>
			</div>
		</div>
		
		<Dialog.Footer>
			<Button onclick={() => showSimulationInfoDialog = false}>Got it!</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- AI Property Detail Modal -->
{#if showPropertyDetailModal && selectedPropertyDetail}
	<PropertyDetail 
		property={selectedPropertyDetail}
		onClose={closePoolPropertyDetail}
		onBuyTokens={(id) => {
			closePoolPropertyDetail();
			const prop = properties.find(p => p.id === id);
			if (prop) openBuyDialog(prop);
		}}
	/>
{/if}

<!-- Floating AI Chat Button -->
{#if isSignedUp}
	<!-- Chat Button (when closed) -->
	{#if !showFloatingChat}
		<button
			onclick={() => showFloatingChat = true}
			class="fixed bottom-6 right-6 z-40 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-full p-4 shadow-2xl hover:from-purple-700 hover:to-indigo-700 transition-all hover:scale-105 group"
		>
			<div class="relative">
				<Bot class="w-7 h-7" />
				<span class="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-white animate-pulse"></span>
			</div>
			<span class="absolute right-full mr-3 top-1/2 -translate-y-1/2 bg-gray-900 text-white text-sm px-3 py-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition whitespace-nowrap">
				Ask the AI Governor
			</span>
		</button>
	{/if}
	
	<!-- Chat Panel (when open) -->
	{#if showFloatingChat}
		<div class="fixed bottom-6 right-6 z-50 w-[400px] max-w-[calc(100vw-3rem)] max-h-[calc(100vh-6rem)] animate-in slide-in-from-bottom-4 fade-in duration-300">
			<div class="bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden flex flex-col h-[min(500px,calc(100vh-8rem))]">
				<!-- Header -->
				<div class="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-4 py-3 flex items-center justify-between flex-shrink-0">
					<div class="flex items-center gap-3">
						<div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
							<Bot class="w-5 h-5" />
						</div>
						<div>
							<div class="font-semibold">Network Governor</div>
							<div class="text-xs text-purple-200 flex items-center gap-1">
								<span class="w-2 h-2 bg-green-400 rounded-full"></span>
								Powered by Gemini
							</div>
						</div>
					</div>
					<div class="flex items-center gap-1">
						<button 
							onclick={() => floatingChatMinimized = !floatingChatMinimized}
							class="p-2 hover:bg-white/20 rounded-lg transition"
							title={floatingChatMinimized ? "Expand" : "Minimize"}
						>
							{#if floatingChatMinimized}
								<ChevronUp class="w-5 h-5" />
							{:else}
								<Minus class="w-5 h-5" />
							{/if}
						</button>
						<button 
							onclick={() => showFloatingChat = false}
							class="p-2 hover:bg-white/20 rounded-lg transition"
							title="Close"
						>
							<X class="w-5 h-5" />
						</button>
					</div>
				</div>
				
				<!-- Chat Content -->
				{#if !floatingChatMinimized}
					<div class="flex-1 overflow-hidden min-h-0">
						<GovernorChat apiBase={API_BASE} userId="user_1" hideHeader={true} />
					</div>
				{/if}
			</div>
		</div>
	{/if}
{/if}

<!-- Achievement Toast -->
{#if showAchievementToast && recentAchievement}
	<div class="fixed bottom-6 right-6 z-50 animate-in slide-in-from-bottom-4 fade-in duration-500">
		<div class="bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl shadow-2xl p-4 max-w-sm">
			<div class="flex items-center gap-3">
				<div class="text-3xl">{recentAchievement.icon}</div>
				<div>
					<div class="text-xs text-amber-100 font-medium uppercase tracking-wide">Discovery Unlocked!</div>
					<div class="font-bold text-lg">{recentAchievement.title}</div>
					<div class="text-sm text-amber-100">{recentAchievement.description}</div>
				</div>
			</div>
			<div class="mt-2 flex items-center justify-between text-xs text-amber-200">
				<span>{unlockedAchievementsCount} of {achievements.length} discoveries</span>
				<button onclick={() => showAchievementToast = false} class="hover:text-white">Dismiss</button>
			</div>
		</div>
	</div>
{/if}

<!-- Insight Moment Modal -->
{#if showInsightModal && currentInsight}
	<div class="fixed bottom-6 left-6 z-50 animate-in slide-in-from-left-4 fade-in duration-500">
		<div class="bg-white border border-slate-200 rounded-xl shadow-2xl p-5 max-w-md">
			<div class="flex items-start gap-4">
				<div class="text-3xl flex-shrink-0">{currentInsight.icon}</div>
				<div class="flex-1">
					<div class="flex items-center justify-between mb-1">
						<div class="text-xs text-blue-600 font-medium uppercase tracking-wide flex items-center gap-1">
							<Lightbulb class="w-3 h-3" />
							Insight
						</div>
						<button 
							onclick={() => showInsightModal = false} 
							class="text-gray-400 hover:text-gray-600 text-lg leading-none"
						>&times;</button>
					</div>
					<div class="font-bold text-gray-900 mb-2">{currentInsight.title}</div>
					<p class="text-sm text-gray-600 mb-3">{currentInsight.content}</p>
					<div class="bg-blue-50 border border-blue-100 rounded-lg p-2 text-xs text-blue-800">
						<strong>In OSF:</strong> {currentInsight.context}
					</div>
				</div>
			</div>
			{#if marathonMode}
				<div class="mt-3 h-1 bg-gray-100 rounded-full overflow-hidden">
					<div class="h-full bg-blue-500 animate-pulse" style="animation: shrink 6s linear forwards"></div>
				</div>
			{/if}
		</div>
	</div>
{/if}

<!-- Onboarding Modal -->
<Dialog.Root bind:open={showOnboardingModal}>
	<Dialog.Content class="max-w-lg">
		<Dialog.Header>
			<Dialog.Title class="flex items-center gap-2 text-xl">
				<span class="text-2xl">🏠</span>
				Welcome to OSF Simulation
			</Dialog.Title>
			<Dialog.Description>
				Experience AI-powered property investment
			</Dialog.Description>
		</Dialog.Header>
		
		<div class="py-4 space-y-4">
			<p class="text-gray-600">
				You have <strong class="text-gray-900">$100,000</strong> to invest in a tokenized property network. 
				<strong class="text-gray-900">11 AI investors</strong> will compete and cooperate alongside you.
			</p>
			
			<div class="bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-lg p-4">
				<h4 class="font-semibold text-emerald-900 mb-2">What makes OSF different?</h4>
				<ul class="text-sm text-emerald-800 space-y-1">
					<li>• <strong>Cooperative ownership</strong> — everyone benefits together</li>
					<li>• <strong>Self-healing network</strong> — protects during downturns</li>
					<li>• <strong>Real market data</strong> — based on Australian housing data</li>
				</ul>
			</div>
			
			<div class="border-t border-gray-200 pt-4">
				<p class="text-sm text-gray-500 mb-3">Choose your experience:</p>
				
				<div class="grid grid-cols-2 gap-3">
					<button 
						onclick={startQuickDemo}
						class="bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl p-4 text-left hover:from-purple-700 hover:to-indigo-700 transition"
					>
						<div class="flex items-center gap-2 mb-1">
							<Zap class="w-5 h-5" />
							<span class="font-bold">Quick Demo</span>
						</div>
						<p class="text-xs text-purple-200">See 1 year in ~15 seconds</p>
					</button>
					
					<button 
						onclick={startFullMarathon}
						class="bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl p-4 text-left hover:from-blue-700 hover:to-cyan-700 transition"
					>
						<div class="flex items-center gap-2 mb-1">
							<Target class="w-5 h-5" />
							<span class="font-bold">Marathon</span>
						</div>
						<p class="text-xs text-blue-200">Watch 10 years unfold</p>
					</button>
				</div>
				
				<button 
					onclick={() => dismissOnboarding(false)}
					class="w-full mt-3 text-center py-2 text-gray-500 hover:text-gray-700 text-sm transition"
				>
					Explore manually instead
				</button>
			</div>
		</div>
		
		<Dialog.Footer class="flex items-center justify-between">
			<label class="flex items-center gap-2 text-sm text-gray-500 cursor-pointer">
				<input 
					type="checkbox" 
					class="rounded border-gray-300"
					onchange={(e) => {
						if ((e.target as HTMLInputElement).checked) {
							localStorage.setItem('osf_onboarding_seen', 'true');
						} else {
							localStorage.removeItem('osf_onboarding_seen');
						}
					}}
				/>
				Don't show again
			</label>
			<Button variant="ghost" onclick={() => dismissOnboarding(false)}>Skip</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<style>
	@keyframes shrink {
		from { width: 100%; }
		to { width: 0%; }
	}
</style>

<!-- Achievements Panel (accessible from synopsis) -->
{#if false}
<!-- This will be shown in the synopsis modal -->
{/if}
