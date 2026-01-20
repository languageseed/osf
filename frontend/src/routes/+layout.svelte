<script lang="ts">
	import '../app.css';
	import { Toaster } from 'svelte-sonner';
	import { Menu, X, Wrench, Clock } from 'lucide-svelte';
	
	let { children, data } = $props();
	
	let showMobileMenu = $state(false);
</script>

<Toaster richColors position="top-right" />

{#if data.maintenanceMode}
<!-- Maintenance Mode Screen -->
<div class="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-4">
	<div class="max-w-lg w-full text-center">
		<!-- Logo -->
		<div class="mb-8">
			<div class="w-20 h-20 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-blue-500/30">
				<span class="text-white font-bold text-3xl">OSF</span>
			</div>
			<h1 class="text-2xl font-bold text-white">Open Source Fund</h1>
			<p class="text-blue-300 text-sm mt-1">Simulation Sandbox</p>
		</div>
		
		<!-- Maintenance Card -->
		<div class="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-8">
			<div class="w-16 h-16 bg-amber-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
				<Wrench class="w-8 h-8 text-amber-400" />
			</div>
			
			<h2 class="text-xl font-semibold text-white mb-3">Under Maintenance</h2>
			<p class="text-slate-300 mb-6">{data.maintenanceMessage}</p>
			
			<div class="flex items-center justify-center gap-2 text-slate-400 text-sm">
				<Clock class="w-4 h-4" />
				<span>We'll be back shortly</span>
			</div>
		</div>
		
		<!-- Footer -->
		<div class="mt-8 text-slate-500 text-xs">
			<p>Gemini 3 Hackathon | Marathon Agent Track</p>
		</div>
	</div>
</div>
{:else}
<div class="min-h-screen bg-white flex flex-col">
	<!-- Hackathon + Simulation Banner -->
	<div class="bg-gradient-to-r from-purple-900 to-indigo-900 text-white text-xs sm:text-sm text-center py-2 px-4">
		<span class="font-medium">🏆 Gemini 3 Hackathon</span>
		<span class="mx-2 text-purple-300">|</span>
		<span class="text-purple-200">Marathon Agent Track</span>
		<span class="mx-2 text-purple-300">|</span>
		<span class="hidden sm:inline text-purple-200">🎮 Simulation Mode — No real money</span>
	</div>
	
	<!-- Navigation - Clean, professional like CommBank/ANZ -->
	<nav class="border-b border-gray-200 bg-white sticky top-0 z-50">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex items-center justify-between h-16">
				<!-- Logo -->
				<a href="/" class="flex items-center gap-2">
					<div class="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
						<span class="text-white font-bold text-lg">OSF</span>
					</div>
					<div class="hidden sm:flex flex-col">
						<span class="text-lg font-semibold text-gray-900 leading-tight">Open Source Fund</span>
						<span class="text-xs text-amber-600 font-medium leading-tight">Simulation Sandbox</span>
					</div>
				</a>
				
				<!-- Desktop Navigation - Simplified for Hackathon -->
				<div class="hidden md:flex items-center gap-8">
					<!-- Simulation - Primary CTA -->
					<a href="/simulate" class="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium text-sm transition">
						<span class="relative flex h-2 w-2">
							<span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
							<span class="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
						</span>
						Simulation
					</a>
					
					<a href="/about" class="text-gray-700 hover:text-gray-900 font-medium text-sm transition">
						How It Works
					</a>
					
					<a href="/case-study" class="text-gray-700 hover:text-gray-900 font-medium text-sm transition">
						Market Context
					</a>
				</div>
				
				<!-- CTA Button -->
				<div class="hidden md:flex items-center gap-3">
					<a href="/simulate" class="bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm px-5 py-2.5 rounded-lg transition">
						Start Simulation
					</a>
				</div>
				
				<!-- Mobile Menu Button -->
				<button 
					onclick={() => showMobileMenu = !showMobileMenu}
					class="md:hidden p-2 text-gray-600 hover:text-gray-900">
					{#if showMobileMenu}
						<X class="w-6 h-6" />
					{:else}
						<Menu class="w-6 h-6" />
					{/if}
				</button>
			</div>
		</div>
		
		<!-- Mobile Menu - Simplified -->
		{#if showMobileMenu}
			<div class="md:hidden border-t border-gray-200 bg-white">
				<div class="px-4 py-4 space-y-1">
					<a href="/simulate" onclick={() => showMobileMenu = false} class="block py-3 text-blue-600 font-medium">
						🎮 Try Simulation
					</a>
					
					<div class="border-t border-gray-100 my-2"></div>
					
					<a href="/about" onclick={() => showMobileMenu = false} class="block py-2 text-gray-700">How It Works</a>
					<a href="/case-study" onclick={() => showMobileMenu = false} class="block py-2 text-gray-700">Market Context</a>
					
					<div class="pt-4">
						<a href="/simulate" onclick={() => showMobileMenu = false} class="block w-full bg-blue-600 text-white text-center font-medium py-3 rounded-lg">
							Start Simulation
						</a>
					</div>
				</div>
			</div>
		{/if}
	</nav>
	
	<!-- Main Content -->
	<main class="flex-1">
		{@render children()}
	</main>
	
	<!-- Simplified Footer for Hackathon -->
	<footer class="bg-slate-900 text-white">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
			<div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
				<div class="flex items-center gap-3">
					<div class="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
						<span class="text-white font-bold">OSF</span>
					</div>
					<div>
						<span class="font-semibold">Open Source Fund</span>
						<span class="ml-2 text-xs bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded">Simulation</span>
					</div>
				</div>
				
				<div class="flex flex-wrap gap-6 text-sm text-slate-400">
					<a href="/simulate" class="hover:text-white transition">Simulation</a>
					<a href="/about" class="hover:text-white transition">How It Works</a>
					<a href="/case-study" class="hover:text-white transition">Market Context</a>
				</div>
			</div>
			
			<div class="border-t border-slate-800 mt-6 pt-6">
				<div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
					<div class="text-sm text-slate-400 max-w-2xl">
						<p class="mb-1 font-medium text-amber-400">
							⚠️ Simulation sandbox — not a financial product
						</p>
					<p class="text-xs text-slate-500">
						No real money, no real assets, no financial advice. Powered by Gemini 3 & Imagen 3.
					</p>
				</div>
				<div class="text-xs text-slate-500">
					© 2026 OSF Simulation | Hackathon Demo
				</div>
				</div>
			</div>
		</div>
	</footer>
</div>
{/if}
