<script lang="ts">
	import { 
		ArrowRight, Users, Bot, FileText, Sparkles, Cpu,
		Clock, DollarSign, Home, TrendingUp, Shield, Zap,
		Play, ChevronRight, Lock, Unlock, Heart
	} from 'lucide-svelte';
</script>

<!-- Hero Section - Clear Value Proposition -->
<section class="relative text-white overflow-hidden">
	<!-- Background Image -->
	<div class="absolute inset-0">
		<img 
			src="/hero-osf.png" 
			alt="OSF - Cooperative Property Ownership" 
			class="w-full h-full object-cover"
		/>
		<div class="absolute inset-0 bg-gradient-to-r from-slate-900/80 via-slate-900/60 to-slate-900/40"></div>
	</div>
	
	<!-- Content -->
	<div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28">
		<div class="max-w-3xl">
			<h1 class="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight mb-6">
				What if everyone could
				<span class="text-blue-400">own property?</span>
			</h1>
			<p class="text-xl md:text-2xl text-slate-200 mb-4 leading-relaxed">
				<strong class="text-white">Open Source Fund</strong> is a cooperative property network 
				where people invest together, share returns, and build wealth — without needing a $140K deposit.
			</p>
			<p class="text-lg text-slate-300 mb-8">
				This is an AI-powered simulation. Experience 10 years of property investment in minutes.
			</p>
			<div class="flex flex-col sm:flex-row gap-4">
				<a href="/simulate" class="inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-4 rounded-xl transition text-lg shadow-lg">
					<Play class="w-5 h-5" />
					Start Simulation
				</a>
				<a href="#the-problem" class="inline-flex items-center justify-center gap-2 bg-white/10 hover:bg-white/20 text-white font-medium px-8 py-4 rounded-xl transition text-lg border border-white/30 backdrop-blur-sm">
					Why This Matters
					<ChevronRight class="w-5 h-5" />
				</a>
			</div>
			<p class="text-sm text-slate-400 mt-6 flex items-center gap-4">
				<span class="flex items-center gap-1">
					<Sparkles class="w-4 h-4 text-purple-400" />
					Powered by Gemini 3
				</span>
				<span>•</span>
				<span>No real money</span>
				<span>•</span>
				<span>Educational sandbox</span>
			</p>
		</div>
	</div>
</section>

<!-- The Problem Section -->
<section id="the-problem" class="bg-slate-900 text-white py-16">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="text-center mb-12">
			<h2 class="text-3xl md:text-4xl font-bold mb-4">The Housing Problem</h2>
			<p class="text-slate-400 text-lg max-w-2xl mx-auto">
				The traditional path to property ownership is broken. Here's what Australians face today.
			</p>
		</div>
		
		<div class="grid md:grid-cols-3 gap-6">
			<div class="bg-slate-800 rounded-2xl p-6 border border-slate-700">
				<div class="w-12 h-12 bg-red-500/20 rounded-xl flex items-center justify-center mb-4">
					<Clock class="w-6 h-6 text-red-400" />
				</div>
				<div class="text-4xl font-bold text-red-400 mb-2">10.5 years</div>
				<div class="text-slate-300 font-medium mb-2">To save a deposit</div>
				<p class="text-sm text-slate-500">
					Average time for a renter to save 20% deposit while house prices rise faster than savings.
				</p>
			</div>
			
			<div class="bg-slate-800 rounded-2xl p-6 border border-slate-700">
				<div class="w-12 h-12 bg-amber-500/20 rounded-xl flex items-center justify-center mb-4">
					<Lock class="w-6 h-6 text-amber-400" />
				</div>
				<div class="text-4xl font-bold text-amber-400 mb-2">$196B</div>
				<div class="text-slate-300 font-medium mb-2">Locked equity</div>
				<p class="text-sm text-slate-500">
					Homeowners have wealth trapped in their homes with no way to access it without selling or more debt.
				</p>
			</div>
			
			<div class="bg-slate-800 rounded-2xl p-6 border border-slate-700">
				<div class="w-12 h-12 bg-rose-500/20 rounded-xl flex items-center justify-center mb-4">
					<DollarSign class="w-6 h-6 text-rose-400" />
				</div>
				<div class="text-4xl font-bold text-rose-400 mb-2">$13B/year</div>
				<div class="text-slate-300 font-medium mb-2">Paid to banks</div>
				<p class="text-sm text-slate-500">
					Western Australians pay this much in mortgage interest annually — wealth transferred away from families.
				</p>
			</div>
		</div>
		
		<div class="mt-8 text-center">
			<a href="/case-study" class="text-blue-400 hover:text-blue-300 text-sm font-medium inline-flex items-center gap-1">
				See full market data <ArrowRight class="w-4 h-4" />
			</a>
		</div>
	</div>
</section>

<!-- The Solution Section -->
<section class="bg-white py-16">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="text-center mb-12">
			<h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">The OSF Solution</h2>
			<p class="text-gray-600 text-lg max-w-2xl mx-auto">
				A cooperative network where everyone can participate in property ownership — not just the wealthy.
			</p>
		</div>
		
		<div class="grid md:grid-cols-3 gap-8">
			<div class="text-center">
				<div class="w-16 h-16 bg-green-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
					<Unlock class="w-8 h-8 text-green-600" />
				</div>
				<h3 class="text-xl font-semibold text-gray-900 mb-2">Start with $100</h3>
				<p class="text-gray-600">
					No $140K deposit needed. Buy fractional property ownership and start building equity immediately.
				</p>
			</div>
			
			<div class="text-center">
				<div class="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
					<Users class="w-8 h-8 text-blue-600" />
				</div>
				<h3 class="text-xl font-semibold text-gray-900 mb-2">Cooperative Ownership</h3>
				<p class="text-gray-600">
					Pool resources with other investors. Diversify across many properties. Share in rental income.
				</p>
			</div>
			
			<div class="text-center">
				<div class="w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
					<Shield class="w-8 h-8 text-purple-600" />
				</div>
				<h3 class="text-xl font-semibold text-gray-900 mb-2">Network Protection</h3>
				<p class="text-gray-600">
					Self-healing mechanisms protect everyone during downturns. No one faces hardship alone.
				</p>
			</div>
		</div>
	</div>
</section>

<!-- Try It Section -->
<section class="bg-gradient-to-br from-blue-600 to-indigo-700 py-16">
	<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
		<h2 class="text-3xl md:text-4xl font-bold text-white mb-4">
			Experience It Yourself
		</h2>
		<p class="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
			You have <strong class="text-white">$100,000</strong> to invest. Watch 10 years of market cycles, 
			economic booms and busts, and see how cooperative ownership performs.
		</p>
		
		<div class="grid sm:grid-cols-2 gap-4 max-w-lg mx-auto mb-8">
			<a href="/simulate" class="bg-white hover:bg-blue-50 text-blue-700 font-semibold px-6 py-4 rounded-xl transition flex items-center justify-center gap-2">
				<Zap class="w-5 h-5" />
				Quick Demo (1 year)
			</a>
			<a href="/simulate" class="bg-white/10 hover:bg-white/20 text-white font-semibold px-6 py-4 rounded-xl transition border border-white/30 flex items-center justify-center gap-2">
				<TrendingUp class="w-5 h-5" />
				Full Marathon (10 years)
			</a>
		</div>
		
		<div class="flex flex-wrap justify-center gap-6 text-sm text-blue-200">
			<span class="flex items-center gap-2">
				<Users class="w-4 h-4" />
				11 AI investors compete with you
			</span>
			<span class="flex items-center gap-2">
				<Bot class="w-4 h-4" />
				Chat with AI Governor
			</span>
			<span class="flex items-center gap-2">
				<Home class="w-4 h-4" />
				Real Perth property data
			</span>
		</div>
	</div>
</section>

<!-- What You'll See Section -->
<section class="bg-gray-50 py-16">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="text-center mb-12">
			<h2 class="text-3xl font-bold text-gray-900 mb-4">What You'll Experience</h2>
			<p class="text-gray-600 max-w-2xl mx-auto">
				The simulation lets you explore different perspectives in the property ecosystem.
			</p>
		</div>
		
		<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
			<a href="/simulate" class="group bg-white rounded-xl p-6 border border-gray-200 hover:border-blue-300 hover:shadow-lg transition-all">
				<div class="flex items-center gap-3 mb-3">
					<div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center group-hover:bg-blue-600 transition">
						<TrendingUp class="w-5 h-5 text-blue-600 group-hover:text-white transition" />
					</div>
					<h3 class="font-semibold text-gray-900">Investor</h3>
				</div>
				<p class="text-sm text-gray-600">
					Buy network tokens, earn dividends from rental income, watch your portfolio grow through market cycles.
				</p>
			</a>
			
			<a href="/simulate" class="group bg-white rounded-xl p-6 border border-gray-200 hover:border-green-300 hover:shadow-lg transition-all">
				<div class="flex items-center gap-3 mb-3">
					<div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center group-hover:bg-green-600 transition">
						<Home class="w-5 h-5 text-green-600 group-hover:text-white transition" />
					</div>
					<h3 class="font-semibold text-gray-900">Tenant</h3>
				</div>
				<p class="text-sm text-gray-600">
					Rent a property while building equity. Part of your rent goes toward ownership — a path to homeownership.
				</p>
			</a>
			
			<a href="/simulate" class="group bg-white rounded-xl p-6 border border-gray-200 hover:border-amber-300 hover:shadow-lg transition-all">
				<div class="flex items-center gap-3 mb-3">
					<div class="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center group-hover:bg-amber-600 transition">
						<Unlock class="w-5 h-5 text-amber-600 group-hover:text-white transition" />
					</div>
					<h3 class="font-semibold text-gray-900">Homeowner</h3>
				</div>
				<p class="text-sm text-gray-600">
					Access your home equity without selling or taking on debt. Sell fractional ownership to the network.
				</p>
			</a>
			
			<a href="/simulate" class="group bg-white rounded-xl p-6 border border-gray-200 hover:border-purple-300 hover:shadow-lg transition-all">
				<div class="flex items-center gap-3 mb-3">
					<div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center group-hover:bg-purple-600 transition">
						<Bot class="w-5 h-5 text-purple-600 group-hover:text-white transition" />
					</div>
					<h3 class="font-semibold text-gray-900">AI Governor</h3>
				</div>
				<p class="text-sm text-gray-600">
					Chat with the network's AI about market conditions, get portfolio advice, understand what's happening.
				</p>
			</a>
			
			<a href="/simulate" class="group bg-white rounded-xl p-6 border border-gray-200 hover:border-rose-300 hover:shadow-lg transition-all">
				<div class="flex items-center gap-3 mb-3">
					<div class="w-10 h-10 bg-rose-100 rounded-lg flex items-center justify-center group-hover:bg-rose-600 transition">
						<Users class="w-5 h-5 text-rose-600 group-hover:text-white transition" />
					</div>
					<h3 class="font-semibold text-gray-900">11 AI Investors</h3>
				</div>
				<p class="text-sm text-gray-600">
					Watch autonomous AI personas — retirees, traders, market makers — make their own investment decisions.
				</p>
			</a>
			
			<a href="/simulate" class="group bg-white rounded-xl p-6 border border-gray-200 hover:border-teal-300 hover:shadow-lg transition-all">
				<div class="flex items-center gap-3 mb-3">
					<div class="w-10 h-10 bg-teal-100 rounded-lg flex items-center justify-center group-hover:bg-teal-600 transition">
						<FileText class="w-5 h-5 text-teal-600 group-hover:text-white transition" />
					</div>
					<h3 class="font-semibold text-gray-900">Network Ledger</h3>
				</div>
				<p class="text-sm text-gray-600">
					Every transaction logged transparently. Rent payments, dividends, trades — all visible and verifiable.
				</p>
			</a>
		</div>
	</div>
</section>

<!-- Tech Section (for hackathon judges) -->
<section class="bg-slate-900 text-white py-16">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="text-center mb-12">
			<div class="inline-flex items-center gap-2 bg-purple-500/20 text-purple-400 text-sm font-medium px-4 py-2 rounded-full mb-4">
				<Sparkles class="w-4 h-4" />
				Gemini 3 Hackathon — Marathon Agent Track
			</div>
			<h2 class="text-2xl md:text-3xl font-bold mb-2">Built with Gemini 3</h2>
			<p class="text-slate-400 max-w-2xl mx-auto">
				This simulation demonstrates how Gemini's extended context window enables fundamentally different application designs.
			</p>
		</div>
		
		<div class="grid md:grid-cols-4 gap-6 text-center mb-12">
			<div>
				<div class="text-3xl md:text-4xl font-bold text-purple-400 mb-2">50K+</div>
				<div class="text-slate-400 text-sm">Tokens per batch tick</div>
			</div>
			<div>
				<div class="text-3xl md:text-4xl font-bold text-blue-400 mb-2">10 years</div>
				<div class="text-slate-400 text-sm">Autonomous simulation</div>
			</div>
			<div>
				<div class="text-3xl md:text-4xl font-bold text-green-400 mb-2">11 NPCs</div>
				<div class="text-slate-400 text-sm">AI-driven investors</div>
			</div>
			<div>
				<div class="text-3xl md:text-4xl font-bold text-amber-400 mb-2">Real data</div>
				<div class="text-slate-400 text-sm">ABS/RBA market metrics</div>
			</div>
		</div>
		
		<div class="grid md:grid-cols-2 gap-8">
			<div class="bg-slate-800 rounded-xl p-6 border border-slate-700">
				<div class="flex items-center gap-3 mb-4">
					<div class="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
						<Zap class="w-5 h-5 text-blue-400" />
					</div>
					<div>
						<h3 class="font-semibold text-white">Phase 1: Real-Time</h3>
						<p class="text-sm text-slate-400">Gemini 3 Flash</p>
					</div>
				</div>
				<p class="text-slate-300 text-sm">
					Streaming chat with the AI Governor. Low-latency responses for conversational interactions about market conditions and portfolio advice.
				</p>
			</div>
			
			<div class="bg-slate-800 rounded-xl p-6 border border-slate-700">
				<div class="flex items-center gap-3 mb-4">
					<div class="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
						<Cpu class="w-5 h-5 text-purple-400" />
					</div>
					<div>
						<h3 class="font-semibold text-white">Phase 2: Batch Tick</h3>
						<p class="text-sm text-slate-400">Gemini 3 Pro</p>
					</div>
				</div>
				<p class="text-slate-300 text-sm">
					Monthly batch processing of entire simulation state. All properties, participants, and actions processed in single coherent requests.
				</p>
			</div>
		</div>
		
		<div class="mt-8 text-center">
			<a href="/about" class="text-purple-400 hover:text-purple-300 text-sm font-medium inline-flex items-center gap-1">
				Learn more about the architecture <ArrowRight class="w-4 h-4" />
			</a>
		</div>
	</div>
</section>

<!-- Final CTA -->
<section class="bg-white py-12">
	<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
		<h2 class="text-2xl md:text-3xl font-bold text-gray-900 mb-4">
			Ready to explore the future of property ownership?
		</h2>
		<p class="text-gray-600 mb-6">
			No signup required. Start the simulation and see what cooperative ownership could look like.
		</p>
		<a href="/simulate" class="inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-4 rounded-xl transition text-lg">
			<Play class="w-5 h-5" />
			Launch Simulation
		</a>
	</div>
</section>
