<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	
	let { chart, id = 'mermaid-' + Math.random().toString(36).substr(2, 9) } = $props<{ chart: string; id?: string }>();
	
	let container: HTMLDivElement;
	let rendered = $state(false);
	let error = $state<string | null>(null);
	
	onMount(async () => {
		if (!browser) return;
		
		try {
			// Dynamic import to avoid SSR issues
			const mermaid = (await import('mermaid')).default;
			
			mermaid.initialize({
				startOnLoad: false,
				theme: 'dark',
				themeVariables: {
					primaryColor: '#3b82f6',
					primaryTextColor: '#fff',
					primaryBorderColor: '#60a5fa',
					lineColor: '#64748b',
					secondaryColor: '#10b981',
					tertiaryColor: '#1e293b',
					background: '#0f172a',
					mainBkg: '#1e293b',
					secondBkg: '#334155',
					border1: '#475569',
					border2: '#64748b',
					arrowheadColor: '#64748b',
					fontFamily: 'ui-sans-serif, system-ui, sans-serif',
					fontSize: '14px',
					textColor: '#e2e8f0',
					nodeTextColor: '#fff',
				},
			});
			
			const { svg } = await mermaid.render(id, chart);
			container.innerHTML = svg;
			rendered = true;
		} catch (e) {
			console.error('Mermaid render error:', e);
			error = String(e);
		}
	});
</script>

<div bind:this={container} class="mermaid-container flex justify-center overflow-x-auto py-4">
	{#if !rendered && !error}
		<div class="animate-pulse text-slate-500">Loading diagram...</div>
	{/if}
	{#if error}
		<div class="text-red-400 text-sm bg-red-900/20 p-4 rounded">Failed to render diagram</div>
	{/if}
</div>

<style>
	.mermaid-container :global(svg) {
		max-width: 100%;
		height: auto;
	}
</style>
