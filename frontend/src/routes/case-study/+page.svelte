<script lang="ts">
	import { 
		MapPin, Home, Users, DollarSign, TrendingUp, Clock, 
		AlertTriangle, CheckCircle, PieChart, BarChart3,
		ArrowRight, Lock, Unlock, Percent, Building,
		Target, Zap, Scale
	} from 'lucide-svelte';
	
	let activeSection = $state('overview');
	
	const waMarket = {
		population: 2800000,
		households: 1100000,
		homeOwners: 715000,
		renters: 385000,
		medianHousePrice: 680000,
		medianUnitPrice: 450000,
		totalResidentialValue: 580000000000,
		totalProperties: 1050000,
		ownedOutright: 330000,
		mortgaged: 385000,
		averageEquity: 320000,
		totalHomeEquity: 280000000000,
		accessibleEquity: 84000000000,
		lockedEquity: 196000000000,
		firstHomeBuyersPerYear: 18000,
		avgTimeToSaveDeposit: 10.5,
		depositRequired: 136000,
		avgSavingsPerMonth: 1200,
		renterWantingToBuy: 230000,
		cantQualifyForMortgage: 115000,
		avgMortgageSize: 520000,
		avgMortgageRate: 6.5,
		avgMortgageTerm: 30,
		totalMortgageDebt: 200000000000,
		annualInterestPaid: 13000000000,
		householdsWithCCDebt: 440000,
		avgCCDebtPerHousehold: 4200,
		avgCCInterestRate: 21,
		totalCCDebt: 1848000000,
		annualCCInterest: 388000000,
		avgWeeklyRent: 620,
		annualRentPaid: 12400000000,
		rentIncreasePerYear: 8,
		avgAgentFee: 2.5,
		stampDuty: 25000,
		conveyancing: 2500,
		lmi: 15000,
	};
	
	// Note: With 20% deposit, LMI does NOT apply
	// We show LMI separately for those with <20% deposit
	const traditional = {
		yearsToSaveDeposit: waMarket.avgTimeToSaveDeposit,
		depositAmount: waMarket.depositRequired,
		mortgageAmount: waMarket.medianHousePrice - waMarket.depositRequired,
		monthlyMortgage: calculateMortgagePayment(
			waMarket.medianHousePrice - waMarket.depositRequired,
			waMarket.avgMortgageRate,
			waMarket.avgMortgageTerm
		),
		totalInterestPaid: calculateTotalInterest(
			waMarket.medianHousePrice - waMarket.depositRequired,
			waMarket.avgMortgageRate,
			waMarket.avgMortgageTerm
		),
		// Upfront costs WITHOUT LMI (20% deposit assumed)
		upfrontCosts: waMarket.stampDuty + waMarket.conveyancing,
		totalCostOfOwnership: 0,
	};
	traditional.totalCostOfOwnership = 
		waMarket.depositRequired + 
		traditional.totalInterestPaid + 
		traditional.upfrontCosts +
		(waMarket.medianHousePrice - waMarket.depositRequired);
	
	// Calculate realistic years to full ownership with compounding
	function calculateYearsToTarget(initial: number, monthly: number, annualReturn: number, target: number): number {
		const monthlyRate = annualReturn / 100 / 12;
		let balance = initial;
		let months = 0;
		const maxMonths = 600; // 50 years max
		
		while (balance < target && months < maxMonths) {
			balance = balance * (1 + monthlyRate) + monthly;
			months++;
		}
		return months / 12;
	}
	
	const osfYearsToOwnership = calculateYearsToTarget(
		5000, // initial investment
		waMarket.avgSavingsPerMonth, // monthly investment
		7, // annual return %
		waMarket.medianHousePrice // target
	);
	
	const osf = {
		yearsToSaveDeposit: 0,
		initialInvestment: 5000,
		monthlyInvestment: waMarket.avgSavingsPerMonth,
		targetEquity: waMarket.medianHousePrice,
		yearsToFullOwnership: Math.round(osfYearsToOwnership * 10) / 10, // Calculated: ~20.5 years
		totalInterestPaid: 0,
		upfrontCosts: waMarket.medianHousePrice * 0.01,
		networkAppreciation: 7,
		// Actual cash outlay (what you really pay out of pocket)
		totalCashOutlay: 5000 + (waMarket.medianHousePrice * 0.01) + (waMarket.avgSavingsPerMonth * 12 * osfYearsToOwnership),
	};
	
	function calculateMortgagePayment(principal: number, annualRate: number, years: number): number {
		const monthlyRate = annualRate / 100 / 12;
		const numPayments = years * 12;
		return principal * (monthlyRate * Math.pow(1 + monthlyRate, numPayments)) / (Math.pow(1 + monthlyRate, numPayments) - 1);
	}
	
	function calculateTotalInterest(principal: number, annualRate: number, years: number): number {
		const monthlyPayment = calculateMortgagePayment(principal, annualRate, years);
		return (monthlyPayment * years * 12) - principal;
	}
	
	const marketImpact = {
		unlockedEquityPotential: waMarket.lockedEquity * 0.5,
		annualInterestSavings: waMarket.annualInterestPaid * 0.9,
		annualCCSavings: waMarket.annualCCInterest * 0.95,
		newBuyersEnabled: waMarket.cantQualifyForMortgage * 0.7,
		rentersToOwners: waMarket.renterWantingToBuy * 0.4,
	};
	
	const projection10Year = {
		traditional: {
			homeOwnershipRate: 65,
			totalInterestPaid: waMarket.annualInterestPaid * 10,
			newFirstHomeBuyers: waMarket.firstHomeBuyersPerYear * 10,
			lockedEquity: waMarket.lockedEquity * 1.3,
		},
		osf: {
			homeOwnershipRate: 78,
			totalInterestPaid: waMarket.annualInterestPaid * 10 * 0.3,
			newFirstHomeBuyers: waMarket.firstHomeBuyersPerYear * 10 * 1.8,
			lockedEquity: waMarket.lockedEquity * 0.4,
		}
	};
	
	function formatBillions(n: number): string {
		return (n / 1000000000).toFixed(1) + 'B';
	}
	
	function formatMillions(n: number): string {
		return (n / 1000000).toFixed(0) + 'M';
	}
	
	function formatThousands(n: number): string {
		return (n / 1000).toFixed(0) + 'K';
	}
</script>

<div class="bg-gray-50 min-h-screen">
<div class="max-w-7xl mx-auto px-4 py-8">
	<!-- Header -->
	<div class="flex items-center justify-between mb-8">
		<div class="flex items-center gap-3">
			<div class="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
				<MapPin class="w-6 h-6 text-white" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-gray-900">Western Australia Market Context</h1>
				<p class="text-gray-500 text-sm">Real housing market data used in simulation</p>
			</div>
		</div>
		<a href="/simulate" class="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1">
			Try Simulation <ArrowRight class="w-4 h-4" />
		</a>
	</div>
	
	<!-- Key Stats Banner -->
	<div class="bg-blue-600 rounded-xl p-6 mb-8">
		<div class="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
			<div>
				<div class="text-2xl font-bold text-white">${formatBillions(waMarket.totalResidentialValue)}</div>
				<div class="text-sm text-blue-100">Total WA Property Value</div>
			</div>
			<div>
				<div class="text-2xl font-bold text-white">{(waMarket.households / 1000000).toFixed(1)}M</div>
				<div class="text-sm text-blue-100">Households</div>
			</div>
			<div>
				<div class="text-2xl font-bold text-white">${formatBillions(waMarket.lockedEquity)}</div>
				<div class="text-sm text-blue-100">Locked Equity</div>
			</div>
			<div>
				<div class="text-2xl font-bold text-white">{formatThousands(waMarket.cantQualifyForMortgage)}</div>
				<div class="text-sm text-blue-100">Can't Get Mortgage</div>
			</div>
			<div>
				<div class="text-2xl font-bold text-white">${formatBillions(waMarket.annualInterestPaid)}/yr</div>
				<div class="text-sm text-blue-100">Interest to Banks</div>
			</div>
		</div>
	</div>
	
	<!-- Navigation Tabs -->
	<div class="flex gap-2 mb-8 border-b border-gray-200 pb-4 overflow-x-auto">
		<button 
			onclick={() => activeSection = 'overview'}
			class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition whitespace-nowrap
				{activeSection === 'overview' ? 'bg-blue-600 text-white' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100'}">
			<PieChart class="w-4 h-4" />
			Market Overview
		</button>
		<button 
			onclick={() => activeSection = 'problem'}
			class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition whitespace-nowrap
				{activeSection === 'problem' ? 'bg-blue-600 text-white' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100'}">
			<AlertTriangle class="w-4 h-4" />
			The Problem
		</button>
		<button 
			onclick={() => activeSection = 'solution'}
			class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition whitespace-nowrap
				{activeSection === 'solution' ? 'bg-blue-600 text-white' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100'}">
			<CheckCircle class="w-4 h-4" />
			OSF Solution
		</button>
		<button 
			onclick={() => activeSection = 'comparison'}
			class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition whitespace-nowrap
				{activeSection === 'comparison' ? 'bg-blue-600 text-white' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100'}">
			<Scale class="w-4 h-4" />
			Side-by-Side
		</button>
		<button 
			onclick={() => activeSection = 'impact'}
			class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition whitespace-nowrap
				{activeSection === 'impact' ? 'bg-blue-600 text-white' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100'}">
			<TrendingUp class="w-4 h-4" />
			10-Year Impact
		</button>
	</div>
	
	<!-- Market Overview Section -->
	{#if activeSection === 'overview'}
		<div class="space-y-6">
			<div class="text-center mb-8">
				<h2 class="text-2xl font-bold text-gray-900 mb-2">Western Australia Housing Market</h2>
				<p class="text-gray-500">Current state of residential property in WA (2024-2025)</p>
			</div>
			
			<div class="grid md:grid-cols-3 gap-6">
				<div class="bg-white rounded-xl border border-gray-200 p-6">
					<h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
						<Home class="w-5 h-5 text-blue-600" />
						Property Values
					</h3>
					<div class="space-y-3">
						<div class="flex justify-between">
							<span class="text-gray-500">Median House</span>
							<span class="text-gray-900 font-medium">${waMarket.medianHousePrice.toLocaleString()}</span>
						</div>
						<div class="flex justify-between">
							<span class="text-gray-500">Median Unit</span>
							<span class="text-gray-900 font-medium">${waMarket.medianUnitPrice.toLocaleString()}</span>
						</div>
						<div class="flex justify-between">
							<span class="text-gray-500">Total Properties</span>
							<span class="text-gray-900 font-medium">{(waMarket.totalProperties / 1000000).toFixed(2)}M</span>
						</div>
						<div class="flex justify-between border-t border-gray-100 pt-3">
							<span class="text-gray-500">Total Market Value</span>
							<span class="text-blue-600 font-bold">${formatBillions(waMarket.totalResidentialValue)}</span>
						</div>
					</div>
				</div>
				
				<div class="bg-white rounded-xl border border-gray-200 p-6">
					<h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
						<Users class="w-5 h-5 text-blue-600" />
						Ownership Breakdown
					</h3>
					<div class="space-y-3">
						<div>
							<div class="flex justify-between mb-1">
								<span class="text-gray-500">Own Outright</span>
								<span class="text-gray-900 font-medium">30%</span>
							</div>
							<div class="w-full bg-blue-100 rounded-full h-2">
								<div class="bg-blue-600 h-2 rounded-full" style="width: 30%"></div>
							</div>
						</div>
						<div>
							<div class="flex justify-between mb-1">
								<span class="text-gray-500">Mortgaged</span>
								<span class="text-gray-900 font-medium">35%</span>
							</div>
							<div class="w-full bg-blue-100 rounded-full h-2">
								<div class="bg-blue-500 h-2 rounded-full" style="width: 35%"></div>
							</div>
						</div>
						<div>
							<div class="flex justify-between mb-1">
								<span class="text-gray-500">Renting</span>
								<span class="text-gray-900 font-medium">35%</span>
							</div>
							<div class="w-full bg-blue-100 rounded-full h-2">
								<div class="bg-blue-400 h-2 rounded-full" style="width: 35%"></div>
							</div>
						</div>
					</div>
					<div class="mt-4 pt-4 border-t border-gray-100 text-center">
						<div class="text-2xl font-bold text-blue-600">{waMarket.renters.toLocaleString()}</div>
						<div class="text-sm text-gray-500">Renter households</div>
					</div>
				</div>
				
				<div class="bg-white rounded-xl border border-gray-200 p-6">
					<h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
						<DollarSign class="w-5 h-5 text-blue-600" />
						Equity & Debt
					</h3>
					<div class="space-y-3">
						<div class="flex justify-between">
							<span class="text-gray-500">Total Home Equity</span>
							<span class="text-gray-900 font-medium">${formatBillions(waMarket.totalHomeEquity)}</span>
						</div>
						<div class="flex justify-between">
							<span class="text-gray-500">Mortgage Debt</span>
							<span class="text-gray-900 font-medium">${formatBillions(waMarket.totalMortgageDebt)}</span>
						</div>
						<div class="flex justify-between">
							<span class="text-gray-500">Credit Card Debt</span>
							<span class="text-gray-900 font-medium">${formatBillions(waMarket.totalCCDebt)}</span>
						</div>
						<div class="flex justify-between border-t border-gray-100 pt-3">
							<span class="text-gray-500">Annual Interest Paid</span>
							<span class="text-blue-600 font-bold">${formatBillions(waMarket.annualInterestPaid + waMarket.annualCCInterest)}</span>
						</div>
					</div>
				</div>
			</div>
			
			<div class="bg-white rounded-xl border border-gray-200 p-6">
				<h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
					<Target class="w-5 h-5 text-blue-600" />
					First Home Buyer Reality
				</h3>
				<div class="grid md:grid-cols-4 gap-6">
					<div class="bg-blue-50 rounded-lg p-4 text-center border border-blue-100">
						<div class="text-3xl font-bold text-blue-600">${formatThousands(waMarket.depositRequired)}</div>
						<div class="text-sm text-gray-500">Deposit Required (20%)</div>
					</div>
					<div class="bg-blue-50 rounded-lg p-4 text-center border border-blue-100">
						<div class="text-3xl font-bold text-blue-600">{waMarket.avgTimeToSaveDeposit} years</div>
						<div class="text-sm text-gray-500">Average Time to Save</div>
					</div>
					<div class="bg-blue-50 rounded-lg p-4 text-center border border-blue-100">
						<div class="text-3xl font-bold text-blue-600">{waMarket.firstHomeBuyersPerYear.toLocaleString()}</div>
						<div class="text-sm text-gray-500">First Home Buyers/Year</div>
					</div>
					<div class="bg-blue-50 rounded-lg p-4 text-center border border-blue-100">
						<div class="text-3xl font-bold text-blue-600">{waMarket.cantQualifyForMortgage.toLocaleString()}</div>
						<div class="text-sm text-gray-500">Can't Qualify for Mortgage</div>
					</div>
				</div>
			</div>
			
			<div class="bg-blue-50 rounded-lg p-4 border border-blue-100">
				<p class="text-sm text-gray-600">
					<strong class="text-gray-900">Data Sources:</strong> Reserve Bank of Australia (RBA), 
					Australian Bureau of Statistics (ABS), Real Estate Institute of Western Australia (REIWA), 
					CoreLogic Home Value Index. Data reflects 2024-2025 market conditions.
				</p>
			</div>
		</div>
	{/if}
	
	<!-- The Problem Section -->
	{#if activeSection === 'problem'}
		<div class="space-y-6">
			<div class="text-center mb-8">
				<h2 class="text-2xl font-bold text-gray-900 mb-2">The Problem with Traditional Housing</h2>
				<p class="text-gray-500">Why the current system fails Western Australians</p>
			</div>
			
			<div class="bg-white rounded-xl border border-gray-200 p-6">
				<h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
					<Lock class="w-6 h-6 text-blue-600" />
					Problem 1: $196 Billion in Locked Equity
				</h3>
				<div class="grid md:grid-cols-2 gap-6">
					<div>
						<p class="text-gray-600 mb-4">
							WA homeowners have <strong class="text-gray-900">$280 billion in home equity</strong>, 
							but most of it is inaccessible. Traditional options to access equity:
						</p>
						<ul class="space-y-2 text-sm">
							<li class="flex items-start gap-2">
								<span class="text-blue-600">•</span>
								<span class="text-gray-600"><strong class="text-gray-900">Home Equity Loan:</strong> More debt, 7%+ interest, income requirements</span>
							</li>
							<li class="flex items-start gap-2">
								<span class="text-blue-600">•</span>
								<span class="text-gray-600"><strong class="text-gray-900">Reverse Mortgage:</strong> Compounding debt, erodes estate, 7-8% interest</span>
							</li>
							<li class="flex items-start gap-2">
								<span class="text-blue-600">•</span>
								<span class="text-gray-600"><strong class="text-gray-900">Sell & Downsize:</strong> Lose your home, high transaction costs</span>
							</li>
						</ul>
					</div>
					<div class="bg-blue-50 rounded-lg p-4 border border-blue-100">
						<div class="text-center mb-4">
							<div class="text-4xl font-bold text-blue-600">${formatBillions(waMarket.lockedEquity)}</div>
							<div class="text-gray-500">Locked Away</div>
						</div>
						<div class="h-8 w-full bg-blue-200 rounded-full flex overflow-hidden">
							<div class="bg-blue-400 h-8 flex items-center justify-center text-xs text-white font-medium" style="width: 30%">
								Accessible
							</div>
							<div class="bg-blue-600 h-8 flex items-center justify-center text-xs text-white font-medium" style="width: 70%">
								Locked
							</div>
						</div>
					</div>
				</div>
			</div>
			
			<div class="bg-white rounded-xl border border-gray-200 p-6">
				<h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
					<Clock class="w-6 h-6 text-blue-600" />
					Problem 2: 10.5 Years to Save a Deposit
				</h3>
				<div class="grid md:grid-cols-2 gap-6">
					<div>
						<p class="text-gray-600 mb-4">
							The average WA renter needs <strong class="text-gray-900">10.5 years</strong> to save 
							a 20% deposit. Meanwhile:
						</p>
						<ul class="space-y-2 text-sm text-gray-600">
							<li class="flex items-start gap-2">
								<span class="text-blue-600">•</span>
								<span>House prices rise faster than savings (8% vs 4%)</span>
							</li>
							<li class="flex items-start gap-2">
								<span class="text-blue-600">•</span>
								<span>$12.4B/year paid in rent (gone forever)</span>
							</li>
							<li class="flex items-start gap-2">
								<span class="text-blue-600">•</span>
								<span>115,000 people can't qualify even with deposit</span>
							</li>
						</ul>
					</div>
					<div class="bg-blue-50 rounded-lg p-4 border border-blue-100">
						<h4 class="text-sm text-gray-500 mb-3">Time to Home Ownership</h4>
						<div class="space-y-3">
							<div>
								<div class="flex justify-between text-sm mb-1">
									<span class="text-gray-500">Save deposit</span>
									<span class="text-gray-900">10.5 years</span>
								</div>
								<div class="w-full bg-blue-200 rounded-full h-3">
									<div class="bg-blue-500 h-3 rounded-full" style="width: 26%"></div>
								</div>
							</div>
							<div>
								<div class="flex justify-between text-sm mb-1">
									<span class="text-gray-500">Pay off mortgage</span>
									<span class="text-gray-900">30 years</span>
								</div>
								<div class="w-full bg-blue-200 rounded-full h-3">
									<div class="bg-blue-600 h-3 rounded-full" style="width: 74%"></div>
								</div>
							</div>
							<div class="text-center pt-2 border-t border-blue-200">
								<div class="text-2xl font-bold text-blue-600">40.5 years</div>
								<div class="text-xs text-gray-500">Total journey to ownership</div>
							</div>
						</div>
					</div>
				</div>
			</div>
			
			<div class="bg-white rounded-xl border border-gray-200 p-6">
				<h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
					<DollarSign class="w-6 h-6 text-blue-600" />
					Problem 3: $13.4 Billion/Year to Banks
				</h3>
				<div class="grid md:grid-cols-3 gap-6">
					<div class="bg-blue-50 rounded-lg p-4 text-center border border-blue-100">
						<div class="text-3xl font-bold text-blue-600">${formatBillions(waMarket.annualInterestPaid)}</div>
						<div class="text-sm text-gray-500">Mortgage Interest/Year</div>
						<div class="text-xs text-gray-400 mt-1">At {waMarket.avgMortgageRate}% average rate</div>
					</div>
					<div class="bg-blue-50 rounded-lg p-4 text-center border border-blue-100">
						<div class="text-3xl font-bold text-blue-600">${formatMillions(waMarket.annualCCInterest)}</div>
						<div class="text-sm text-gray-500">Credit Card Interest/Year</div>
						<div class="text-xs text-gray-400 mt-1">At {waMarket.avgCCInterestRate}% average rate</div>
					</div>
					<div class="bg-blue-50 rounded-lg p-4 text-center border border-blue-100">
						<div class="text-3xl font-bold text-blue-600">${formatBillions(waMarket.annualRentPaid)}</div>
						<div class="text-sm text-gray-500">Rent Paid/Year</div>
						<div class="text-xs text-gray-400 mt-1">Building zero equity</div>
					</div>
				</div>
				<div class="mt-6 p-4 bg-blue-600 rounded-lg">
					<div class="text-center">
						<div class="text-sm text-blue-100">Total annual wealth transfer from WA households to banks/landlords:</div>
						<div class="text-4xl font-bold text-white mt-2">
							${formatBillions(waMarket.annualInterestPaid + waMarket.annualCCInterest + waMarket.annualRentPaid)}
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}
	
	<!-- OSF Solution Section -->
	{#if activeSection === 'solution'}
		<div class="space-y-6">
			<div class="text-center mb-8">
				<h2 class="text-2xl font-bold text-gray-900 mb-2">The OSF Solution for Western Australia</h2>
				<p class="text-gray-500">How OSF transforms the housing market</p>
			</div>
			
			<div class="bg-white rounded-xl border border-gray-200 p-6">
				<h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
					<Unlock class="w-6 h-6 text-blue-600" />
					Solution 1: Unlock $98 Billion in Equity
				</h3>
				<div class="grid md:grid-cols-2 gap-6">
					<div>
						<p class="text-gray-600 mb-4">
							OSF lets homeowners sell fractional equity to the network — 
							<strong class="text-gray-900">no debt, no interest, no income requirements</strong>.
						</p>
						<ul class="space-y-2 text-sm">
							<li class="flex items-start gap-2">
								<CheckCircle class="w-4 h-4 text-blue-600 mt-0.5" />
								<span class="text-gray-600">Sell 5-49% equity, keep living in your home</span>
							</li>
							<li class="flex items-start gap-2">
								<CheckCircle class="w-4 h-4 text-blue-600 mt-0.5" />
								<span class="text-gray-600">No monthly payments, no interest accruing</span>
							</li>
							<li class="flex items-start gap-2">
								<CheckCircle class="w-4 h-4 text-blue-600 mt-0.5" />
								<span class="text-gray-600">Buy back anytime at current market value</span>
							</li>
							<li class="flex items-start gap-2">
								<CheckCircle class="w-4 h-4 text-blue-600 mt-0.5" />
								<span class="text-gray-600">Retirees access equity without debt spiral</span>
							</li>
						</ul>
					</div>
					<div class="bg-blue-50 rounded-lg p-4 border border-blue-100">
						<div class="text-center mb-4">
							<div class="text-sm text-gray-500">Equity Unlockable via OSF</div>
							<div class="text-4xl font-bold text-blue-600">${formatBillions(marketImpact.unlockedEquityPotential)}</div>
							<div class="text-sm text-gray-400">50% of currently locked equity</div>
						</div>
					</div>
				</div>
			</div>
			
			<div class="bg-white rounded-xl border border-gray-200 p-6">
				<h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
					<Zap class="w-6 h-6 text-blue-600" />
					Solution 2: Start Ownership Journey Immediately
				</h3>
				<div class="grid md:grid-cols-2 gap-6">
					<div>
						<p class="text-gray-600 mb-4">
							No need to wait 10.5 years. Start building property wealth 
							<strong class="text-gray-900">with your first $100</strong>.
						</p>
						<ul class="space-y-2 text-sm">
							<li class="flex items-start gap-2">
								<CheckCircle class="w-4 h-4 text-blue-600 mt-0.5" />
								<span class="text-gray-600">Invest $100-$5,000 to start</span>
							</li>
							<li class="flex items-start gap-2">
								<CheckCircle class="w-4 h-4 text-blue-600 mt-0.5" />
								<span class="text-gray-600">Own fractional property from day 1</span>
							</li>
							<li class="flex items-start gap-2">
								<CheckCircle class="w-4 h-4 text-blue-600 mt-0.5" />
								<span class="text-gray-600">Tenant-to-owner pathway available</span>
							</li>
							<li class="flex items-start gap-2">
								<CheckCircle class="w-4 h-4 text-blue-600 mt-0.5" />
								<span class="text-gray-600">No income qualification required</span>
							</li>
						</ul>
					</div>
					<div class="bg-blue-50 rounded-lg p-4 border border-blue-100">
						<h4 class="text-sm text-gray-500 mb-3 text-center">New Buyers Enabled</h4>
						<div class="text-center mb-4">
							<div class="text-4xl font-bold text-blue-600">{marketImpact.newBuyersEnabled.toLocaleString()}</div>
							<div class="text-sm text-gray-400">People who couldn't get mortgages</div>
						</div>
						<div class="grid grid-cols-2 gap-4 text-center text-sm">
							<div>
								<div class="text-2xl font-bold text-blue-600">0</div>
								<div class="text-gray-500">Years to start</div>
							</div>
							<div>
								<div class="text-2xl font-bold text-blue-600">$100</div>
								<div class="text-gray-500">Minimum invest</div>
							</div>
						</div>
					</div>
				</div>
			</div>
			
			<div class="bg-white rounded-xl border border-gray-200 p-6">
				<h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
					<Percent class="w-6 h-6 text-blue-600" />
					Solution 3: Save $12+ Billion/Year in Interest
				</h3>
				<div class="grid md:grid-cols-3 gap-6">
					<div class="bg-blue-50 rounded-lg p-4 text-center border border-blue-100">
						<div class="text-3xl font-bold text-blue-600">${formatBillions(marketImpact.annualInterestSavings)}</div>
						<div class="text-sm text-gray-500">Mortgage Interest Saved</div>
						<div class="text-xs text-gray-400 mt-1">OSF mortgages at 0% interest</div>
					</div>
					<div class="bg-blue-50 rounded-lg p-4 text-center border border-blue-100">
						<div class="text-3xl font-bold text-blue-600">${formatMillions(marketImpact.annualCCSavings)}</div>
						<div class="text-sm text-gray-500">CC Interest Saved</div>
						<div class="text-xs text-gray-400 mt-1">Via debt recycling</div>
					</div>
					<div class="bg-blue-50 rounded-lg p-4 text-center border border-blue-100">
						<div class="text-3xl font-bold text-blue-600">${formatBillions(marketImpact.annualInterestSavings + marketImpact.annualCCSavings)}</div>
						<div class="text-sm text-gray-500">Total Annual Savings</div>
						<div class="text-xs text-gray-400 mt-1">Stays in WA households</div>
					</div>
				</div>
			</div>
		</div>
	{/if}
	
	<!-- Side-by-Side Comparison Section -->
	{#if activeSection === 'comparison'}
		<div class="space-y-6">
			<div class="text-center mb-8">
				<h2 class="text-2xl font-bold text-gray-900 mb-2">First Home Buyer: Traditional vs OSF</h2>
				<p class="text-gray-500">Buying the median WA home (${waMarket.medianHousePrice.toLocaleString()})</p>
			</div>
			
			<div class="grid md:grid-cols-2 gap-6">
				<!-- Traditional Path -->
				<div class="bg-white rounded-xl border border-gray-200 p-6">
					<h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
						<Building class="w-6 h-6 text-blue-600" />
						Traditional Mortgage
					</h3>
					
					<div class="space-y-4">
						<div class="bg-blue-50 rounded-lg p-4 border border-blue-100">
							<div class="text-sm text-gray-500 mb-2">Step 1: Save Deposit</div>
							<div class="flex justify-between">
								<span class="text-gray-600">20% deposit required</span>
								<span class="text-gray-900 font-bold">${waMarket.depositRequired.toLocaleString()}</span>
							</div>
							<div class="flex justify-between mt-1">
								<span class="text-gray-400 text-sm">Time to save (@ $1,200/mo)</span>
								<span class="text-gray-900">{waMarket.avgTimeToSaveDeposit} years</span>
							</div>
						</div>
						
						<div class="bg-blue-50 rounded-lg p-4 border border-blue-100">
							<div class="text-sm text-gray-500 mb-2">Step 2: Upfront Costs</div>
							<div class="space-y-1 text-sm">
								<div class="flex justify-between">
									<span class="text-gray-500">Stamp duty</span>
									<span class="text-gray-900">${waMarket.stampDuty.toLocaleString()}</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-500">Conveyancing</span>
									<span class="text-gray-900">${waMarket.conveyancing.toLocaleString()}</span>
								</div>
								<div class="flex justify-between border-t border-blue-200 pt-1 mt-1">
									<span class="text-gray-900">Total upfront</span>
									<span class="text-gray-900 font-bold">${traditional.upfrontCosts.toLocaleString()}</span>
								</div>
							</div>
							<div class="text-xs text-gray-400 mt-2">Note: LMI ($15K+) applies if deposit &lt;20%</div>
						</div>
						
						<div class="bg-blue-50 rounded-lg p-4 border border-blue-100">
							<div class="text-sm text-gray-500 mb-2">Step 3: 30-Year Mortgage</div>
							<div class="space-y-1 text-sm">
								<div class="flex justify-between">
									<span class="text-gray-500">Loan amount</span>
									<span class="text-gray-900">${traditional.mortgageAmount.toLocaleString()}</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-500">Interest rate</span>
									<span class="text-gray-900">{waMarket.avgMortgageRate}%</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-500">Monthly payment</span>
									<span class="text-gray-900">${Math.round(traditional.monthlyMortgage).toLocaleString()}</span>
								</div>
								<div class="flex justify-between border-t border-blue-200 pt-1 mt-1">
									<span class="text-gray-900">Total interest paid</span>
									<span class="text-gray-900 font-bold">${Math.round(traditional.totalInterestPaid).toLocaleString()}</span>
								</div>
							</div>
						</div>
						
						<div class="bg-gray-700 rounded-lg p-4">
							<div class="text-center">
								<div class="text-sm text-gray-300">Total Cash Outlay</div>
								<div class="text-3xl font-bold text-white">${Math.round(traditional.totalCostOfOwnership).toLocaleString()}</div>
								<div class="text-sm text-gray-400 mt-1">Over {waMarket.avgTimeToSaveDeposit + waMarket.avgMortgageTerm} years</div>
								<div class="text-xs text-gray-400 mt-1">(includes ${Math.round(traditional.totalInterestPaid).toLocaleString()} in interest)</div>
							</div>
						</div>
					</div>
				</div>
				
				<!-- OSF Path -->
				<div class="bg-white rounded-xl border border-gray-200 p-6">
					<h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
						<Home class="w-6 h-6 text-blue-600" />
						OSF Pathway
					</h3>
					
					<div class="space-y-4">
						<div class="bg-blue-50 rounded-lg p-4 border border-blue-100">
							<div class="text-sm text-gray-500 mb-2">Step 1: Start Immediately</div>
							<div class="flex justify-between">
								<span class="text-gray-600">Initial investment</span>
								<span class="text-blue-600 font-bold">${osf.initialInvestment.toLocaleString()}</span>
							</div>
							<div class="flex justify-between mt-1">
								<span class="text-gray-400 text-sm">Time to start</span>
								<span class="text-blue-600">0 years (now!)</span>
							</div>
						</div>
						
						<div class="bg-blue-50 rounded-lg p-4 border border-blue-100">
							<div class="text-sm text-gray-500 mb-2">Step 2: Minimal Upfront Costs</div>
							<div class="space-y-1 text-sm">
								<div class="flex justify-between">
									<span class="text-gray-500">Platform fee (1%)</span>
									<span class="text-gray-900">${osf.upfrontCosts.toLocaleString()}</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-500">Stamp duty</span>
									<span class="text-blue-600">$0 (fractional)</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-500">LMI</span>
									<span class="text-blue-600">$0</span>
								</div>
								<div class="flex justify-between border-t border-blue-200 pt-1 mt-1">
									<span class="text-gray-900">Total upfront</span>
									<span class="text-blue-600 font-bold">${osf.upfrontCosts.toLocaleString()}</span>
								</div>
							</div>
						</div>
						
						<div class="bg-blue-50 rounded-lg p-4 border border-blue-100">
							<div class="text-sm text-gray-500 mb-2">Step 3: Gradual Buyback</div>
							<div class="space-y-1 text-sm">
								<div class="flex justify-between">
									<span class="text-gray-500">Monthly investment</span>
									<span class="text-gray-900">${osf.monthlyInvestment.toLocaleString()}</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-500">Interest rate</span>
									<span class="text-blue-600 font-bold">0%</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-500">Network returns</span>
									<span class="text-blue-600">~{osf.networkAppreciation}%/year</span>
								</div>
								<div class="flex justify-between border-t border-blue-200 pt-1 mt-1">
									<span class="text-gray-900">Total interest paid</span>
									<span class="text-blue-600 font-bold">$0</span>
								</div>
							</div>
						</div>
						
						<div class="bg-blue-600 rounded-lg p-4">
							<div class="text-center">
								<div class="text-sm text-blue-100">Total Cash Outlay</div>
								<div class="text-3xl font-bold text-white">${Math.round(osf.totalCashOutlay).toLocaleString()}</div>
								<div class="text-sm text-blue-200 mt-1">Over {osf.yearsToFullOwnership} years</div>
								<div class="text-xs text-blue-200 mt-1">(7% network returns grow your investment)</div>
							</div>
						</div>
					</div>
				</div>
			</div>
			
			<!-- Savings Summary -->
			<div class="bg-blue-600 rounded-xl p-6">
				<h3 class="text-xl font-semibold text-white mb-4 text-center">Total Savings with OSF</h3>
				<div class="grid md:grid-cols-4 gap-6 text-center">
					<div>
						<div class="text-3xl font-bold text-white">${Math.round(traditional.totalCostOfOwnership - osf.totalCashOutlay).toLocaleString()}</div>
						<div class="text-sm text-blue-100">Total Cash Saved</div>
					</div>
					<div>
						<div class="text-3xl font-bold text-white">${Math.round(traditional.totalInterestPaid).toLocaleString()}</div>
						<div class="text-sm text-blue-100">Interest Avoided</div>
					</div>
					<div>
						<div class="text-3xl font-bold text-white">{waMarket.avgTimeToSaveDeposit} years</div>
						<div class="text-sm text-blue-100">Earlier Start</div>
					</div>
					<div>
						<div class="text-3xl font-bold text-white">{Math.round((waMarket.avgTimeToSaveDeposit + waMarket.avgMortgageTerm) - osf.yearsToFullOwnership)} years</div>
						<div class="text-sm text-blue-100">Faster Ownership</div>
					</div>
				</div>
			</div>
		</div>
	{/if}
	
	<!-- 10-Year Impact Section -->
	{#if activeSection === 'impact'}
		<div class="space-y-6">
			<div class="text-center mb-8">
				<h2 class="text-2xl font-bold text-gray-900 mb-2">10-Year Impact on Western Australia</h2>
				<p class="text-gray-500">What if OSF was adopted across WA?</p>
			</div>
			
			<div class="grid md:grid-cols-2 gap-6">
				<!-- Without OSF -->
				<div class="bg-white rounded-xl border border-gray-200 p-6">
					<h3 class="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
						<AlertTriangle class="w-6 h-6 text-blue-600" />
						Without OSF (2026-2036)
					</h3>
					<div class="space-y-4">
						<div class="flex justify-between items-center py-3 border-b border-gray-100">
							<span class="text-gray-500">Home ownership rate</span>
							<span class="text-gray-900 font-bold">{projection10Year.traditional.homeOwnershipRate}%</span>
						</div>
						<div class="flex justify-between items-center py-3 border-b border-gray-100">
							<span class="text-gray-500">Interest paid to banks</span>
							<span class="text-gray-900 font-bold">${formatBillions(projection10Year.traditional.totalInterestPaid)}</span>
						</div>
						<div class="flex justify-between items-center py-3 border-b border-gray-100">
							<span class="text-gray-500">New first home buyers</span>
							<span class="text-gray-900 font-bold">{(projection10Year.traditional.newFirstHomeBuyers / 1000).toFixed(0)}K</span>
						</div>
						<div class="flex justify-between items-center py-3">
							<span class="text-gray-500">Locked equity</span>
							<span class="text-gray-900 font-bold">${formatBillions(projection10Year.traditional.lockedEquity)}</span>
						</div>
					</div>
				</div>
				
				<!-- With OSF -->
				<div class="bg-white rounded-xl border border-gray-200 p-6">
					<h3 class="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
						<CheckCircle class="w-6 h-6 text-blue-600" />
						With OSF (2026-2036)
					</h3>
					<div class="space-y-4">
						<div class="flex justify-between items-center py-3 border-b border-gray-100">
							<span class="text-gray-500">Home ownership rate</span>
							<div class="text-right">
								<span class="text-blue-600 font-bold">{projection10Year.osf.homeOwnershipRate}%</span>
								<span class="text-blue-600 text-sm ml-2">+13%</span>
							</div>
						</div>
						<div class="flex justify-between items-center py-3 border-b border-gray-100">
							<span class="text-gray-500">Interest paid</span>
							<div class="text-right">
								<span class="text-blue-600 font-bold">${formatBillions(projection10Year.osf.totalInterestPaid)}</span>
								<span class="text-blue-600 text-sm ml-2">-70%</span>
							</div>
						</div>
						<div class="flex justify-between items-center py-3 border-b border-gray-100">
							<span class="text-gray-500">New first home buyers</span>
							<div class="text-right">
								<span class="text-blue-600 font-bold">{(projection10Year.osf.newFirstHomeBuyers / 1000).toFixed(0)}K</span>
								<span class="text-blue-600 text-sm ml-2">+80%</span>
							</div>
						</div>
						<div class="flex justify-between items-center py-3">
							<span class="text-gray-500">Locked equity</span>
							<div class="text-right">
								<span class="text-blue-600 font-bold">${formatBillions(projection10Year.osf.lockedEquity)}</span>
								<span class="text-blue-600 text-sm ml-2">-60%</span>
							</div>
						</div>
					</div>
				</div>
			</div>
			
			<!-- Summary Impact -->
			<div class="bg-blue-600 rounded-xl p-6">
				<h3 class="text-xl font-semibold text-white mb-6 text-center">10-Year Cumulative Impact</h3>
				<div class="grid md:grid-cols-4 gap-6 text-center">
					<div>
						<div class="text-4xl font-bold text-white">
							${formatBillions(projection10Year.traditional.totalInterestPaid - projection10Year.osf.totalInterestPaid)}
						</div>
						<div class="text-sm text-blue-100">Interest Savings</div>
						<div class="text-xs text-blue-200">Stays in WA households</div>
					</div>
					<div>
						<div class="text-4xl font-bold text-white">
							+{((projection10Year.osf.newFirstHomeBuyers - projection10Year.traditional.newFirstHomeBuyers) / 1000).toFixed(0)}K
						</div>
						<div class="text-sm text-blue-100">Additional Home Owners</div>
						<div class="text-xs text-blue-200">Families who couldn't before</div>
					</div>
					<div>
						<div class="text-4xl font-bold text-white">
							${formatBillions(projection10Year.traditional.lockedEquity - projection10Year.osf.lockedEquity)}
						</div>
						<div class="text-sm text-blue-100">Equity Unlocked</div>
						<div class="text-xs text-blue-200">Available for investment/needs</div>
					</div>
					<div>
						<div class="text-4xl font-bold text-white">
							+13%
						</div>
						<div class="text-sm text-blue-100">Ownership Rate</div>
						<div class="text-xs text-blue-200">From 65% to 78%</div>
					</div>
				</div>
			</div>
			
			<!-- Vision Statement -->
			<div class="bg-white rounded-xl border border-gray-200 p-8 text-center">
				<h3 class="text-2xl font-bold text-gray-900 mb-4">The Vision for WA</h3>
				<p class="text-lg text-gray-600 max-w-3xl mx-auto">
					By 2036, OSF could help <strong class="text-blue-600">143,000 more Western Australian families</strong> 
					achieve home ownership, save <strong class="text-blue-600">$91 billion in interest payments</strong>, 
					and unlock <strong class="text-blue-600">$117 billion in previously inaccessible home equity</strong>.
				</p>
				<p class="text-gray-500 mt-4">
					That's wealth that stays in Western Australia, building stronger communities.
				</p>
				<div class="mt-6">
					<a href="/simulate" class="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-3 rounded-lg transition">
						Experience the Simulation
						<ArrowRight class="w-5 h-5" />
					</a>
				</div>
			</div>
		</div>
	{/if}
</div>
</div>
