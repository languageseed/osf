<script lang="ts">
	import { 
		ArrowRight, Bot, Users, FileText, Cpu, Sparkles, 
		Building, ChartBar, Clock, Zap, Database, Globe,
		CheckCircle, Play
	} from 'lucide-svelte';
</script>

<!-- Hero -->
<section class="bg-gradient-to-b from-slate-900 to-slate-800 text-white py-16">
	<div class="max-w-4xl mx-auto px-4 text-center">
		<div class="inline-flex items-center gap-2 bg-purple-500/20 text-purple-400 text-sm font-medium px-4 py-2 rounded-full mb-6">
			<Sparkles class="w-4 h-4" />
			Built with Gemini 3 Flash & Pro
		</div>
		<h1 class="text-4xl md:text-5xl font-bold mb-6">
			How the Simulation Works
		</h1>
		<p class="text-xl text-slate-300 mb-8">
			A deep dive into the AI architecture powering OSF's property investment simulation.
		</p>
		<a href="/simulate" class="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-3 rounded-lg transition">
			<Play class="w-5 h-5" />
			Try the Simulation
		</a>
	</div>
</section>

<!-- Two-Phase Architecture -->
<section class="bg-white py-16">
	<div class="max-w-6xl mx-auto px-4">
		<div class="text-center mb-12">
			<h2 class="text-3xl font-bold text-gray-900 mb-4">Two-Phase Processing Architecture</h2>
			<p class="text-gray-600 max-w-2xl mx-auto">
				OSF maximizes Gemini's extended context window through a novel two-phase processing model.
			</p>
		</div>
		
		<div class="grid md:grid-cols-2 gap-8">
			<!-- Phase 1 -->
			<div class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-8 border border-blue-200">
				<div class="flex items-center gap-3 mb-6">
					<div class="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center">
						<Zap class="w-6 h-6 text-white" />
					</div>
					<div>
						<h3 class="text-xl font-bold text-gray-900">Phase 1: Real-Time</h3>
						<p class="text-sm text-gray-500">Between simulation ticks</p>
					</div>
				</div>
				<ul class="space-y-3">
					<li class="flex items-start gap-3">
						<CheckCircle class="w-5 h-5 text-blue-600 mt-0.5" />
						<span class="text-gray-700"><strong>Governor Chat:</strong> AI agent answers questions about market conditions and portfolio advice</span>
					</li>
					<li class="flex items-start gap-3">
						<CheckCircle class="w-5 h-5 text-blue-600 mt-0.5" />
						<span class="text-gray-700"><strong>Portfolio Advisor:</strong> Personalized investment guidance using Gemini Flash</span>
					</li>
					<li class="flex items-start gap-3">
						<CheckCircle class="w-5 h-5 text-blue-600 mt-0.5" />
						<span class="text-gray-700"><strong>Streaming Responses:</strong> Low-latency conversational AI for immediate feedback</span>
					</li>
				</ul>
				<div class="mt-6 p-3 bg-blue-100 rounded-lg text-sm text-blue-800">
					<strong>Model:</strong> gemini-3-flash • <strong>Context:</strong> ~10K tokens
				</div>
			</div>
			
			<!-- Phase 2 -->
			<div class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-8 border border-purple-200">
				<div class="flex items-center gap-3 mb-6">
					<div class="w-12 h-12 bg-purple-600 rounded-xl flex items-center justify-center">
						<Database class="w-6 h-6 text-white" />
					</div>
					<div>
						<h3 class="text-xl font-bold text-gray-900">Phase 2: Batch Tick</h3>
						<p class="text-sm text-gray-500">Once per simulation month</p>
					</div>
				</div>
				<ul class="space-y-3">
					<li class="flex items-start gap-3">
						<CheckCircle class="w-5 h-5 text-purple-600 mt-0.5" />
						<span class="text-gray-700"><strong>Full State Processing:</strong> All properties, participants, actions in one request</span>
					</li>
					<li class="flex items-start gap-3">
						<CheckCircle class="w-5 h-5 text-purple-600 mt-0.5" />
						<span class="text-gray-700"><strong>NPC Decisions:</strong> 11 autonomous agents make investment decisions</span>
					</li>
					<li class="flex items-start gap-3">
						<CheckCircle class="w-5 h-5 text-purple-600 mt-0.5" />
						<span class="text-gray-700"><strong>Event Generation:</strong> Economic cycles, market events, news articles</span>
					</li>
				</ul>
				<div class="mt-6 p-3 bg-purple-100 rounded-lg text-sm text-purple-800">
					<strong>Model:</strong> gemini-3-pro • <strong>Context:</strong> ~50K+ tokens
				</div>
			</div>
		</div>
	</div>
</section>

<!-- Key Components -->
<section class="bg-gray-50 py-16">
	<div class="max-w-6xl mx-auto px-4">
		<div class="text-center mb-12">
			<h2 class="text-3xl font-bold text-gray-900 mb-4">Simulation Components</h2>
		</div>
		
		<div class="grid md:grid-cols-3 gap-6">
			<!-- NPC System -->
			<div class="bg-white rounded-xl p-6 border border-gray-200">
				<Users class="w-10 h-10 text-green-600 mb-4" />
				<h3 class="text-lg font-bold text-gray-900 mb-2">11 AI NPCs</h3>
				<p class="text-gray-600 text-sm mb-4">
					Diverse personalities including conservative retirees, aggressive traders, 
					and an automated market maker—each with goal-driven behavior.
				</p>
				<div class="text-xs text-gray-500">
					Personalities: Conservative, Moderate, Aggressive, Market Maker, Developer
				</div>
			</div>
			
			<!-- Economic Cycles -->
			<div class="bg-white rounded-xl p-6 border border-gray-200">
				<ChartBar class="w-10 h-10 text-amber-600 mb-4" />
				<h3 class="text-lg font-bold text-gray-900 mb-2">Economic Cycles</h3>
				<p class="text-gray-600 text-sm mb-4">
					5-phase economic simulation (Expansion, Peak, Contraction, Trough, Recovery) 
					that affects property values and NPC behavior.
				</p>
				<div class="text-xs text-gray-500">
					Calibrated to real Australian RBA/ABS data
				</div>
			</div>
			
			<!-- Network Ledger -->
			<div class="bg-white rounded-xl p-6 border border-gray-200">
				<FileText class="w-10 h-10 text-blue-600 mb-4" />
				<h3 class="text-lg font-bold text-gray-900 mb-2">Network Ledger</h3>
				<p class="text-gray-600 text-sm mb-4">
					Every transaction logged with blockchain-style hashes. 
					Rent, dividends, trades, votes—all visible in the Ledger tab.
				</p>
				<div class="text-xs text-gray-500">
					Full transparency of all network activity
				</div>
			</div>
			
			<!-- Visual Generation -->
			<div class="bg-white rounded-xl p-6 border border-gray-200">
				<Building class="w-10 h-10 text-rose-600 mb-4" />
				<h3 class="text-lg font-bold text-gray-900 mb-2">Imagen 3 Visuals</h3>
				<p class="text-gray-600 text-sm mb-4">
					AI-generated isometric property renders and character avatars 
					create a cohesive visual identity.
				</p>
				<div class="text-xs text-gray-500">
					Pre-generated pools for instant retrieval
				</div>
			</div>
			
			<!-- Market Data -->
			<div class="bg-white rounded-xl p-6 border border-gray-200">
				<Globe class="w-10 h-10 text-teal-600 mb-4" />
				<h3 class="text-lg font-bold text-gray-900 mb-2">Real Market Data</h3>
				<p class="text-gray-600 text-sm mb-4">
					Australian housing metrics from RBA, ABS, and REIWA calibrate 
					property valuations, yields, and event probabilities.
				</p>
				<div class="text-xs text-gray-500">
					Perth/WA focus with real median prices and vacancy rates
				</div>
			</div>
			
			<!-- Real-Time Sync -->
			<div class="bg-white rounded-xl p-6 border border-gray-200">
				<Clock class="w-10 h-10 text-indigo-600 mb-4" />
				<h3 class="text-lg font-bold text-gray-900 mb-2">SSE Synchronization</h3>
				<p class="text-gray-600 text-sm mb-4">
					Server-Sent Events keep all clients synchronized. 
					When the simulation month advances, everyone sees it.
				</p>
				<div class="text-xs text-gray-500">
					Configurable tick rates: Test (30s) to Realtime (1hr)
				</div>
			</div>
		</div>
	</div>
</section>

<!-- Tech Stack -->
<section class="bg-white py-16">
	<div class="max-w-4xl mx-auto px-4">
		<div class="text-center mb-12">
			<h2 class="text-3xl font-bold text-gray-900 mb-4">Technology Stack</h2>
		</div>
		
		<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
			<div class="bg-gray-50 rounded-xl p-4 text-center">
				<div class="font-bold text-gray-900">Frontend</div>
				<div class="text-sm text-gray-500">SvelteKit 2.0, Svelte 5 Runes</div>
			</div>
			<div class="bg-gray-50 rounded-xl p-4 text-center">
				<div class="font-bold text-gray-900">Backend</div>
				<div class="text-sm text-gray-500">FastAPI, Python 3.11+</div>
			</div>
			<div class="bg-gray-50 rounded-xl p-4 text-center">
				<div class="font-bold text-gray-900">AI</div>
				<div class="text-sm text-gray-500">Gemini 3 Flash/Pro, Imagen 3</div>
			</div>
			<div class="bg-gray-50 rounded-xl p-4 text-center">
				<div class="font-bold text-gray-900">Database</div>
				<div class="text-sm text-gray-500">SQLite + SQLAlchemy 2.0</div>
			</div>
		</div>
	</div>
</section>

<!-- CTA -->
<section class="bg-gradient-to-r from-purple-600 to-blue-600 py-12">
	<div class="max-w-4xl mx-auto px-4 text-center">
		<h2 class="text-2xl font-bold text-white mb-4">Ready to explore?</h2>
		<p class="text-purple-100 mb-6">
			Experience the simulation with a $100K simulated portfolio.
		</p>
		<a href="/simulate" class="inline-flex items-center gap-2 bg-white hover:bg-gray-50 text-purple-600 font-semibold px-8 py-4 rounded-lg transition">
			Launch Simulation
			<ArrowRight class="w-5 h-5" />
		</a>
	</div>
</section>
