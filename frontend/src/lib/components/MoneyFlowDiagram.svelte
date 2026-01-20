<script lang="ts">
	import { SvelteFlow, Background, type Node, type Edge } from '@xyflow/svelte';
	import '@xyflow/svelte/dist/style.css';
	
	// Custom node components
	import MoneyFlowNode from './MoneyFlowNode.svelte';
	
	// Props for dynamic values
	interface Props {
		monthlyRent?: number;
		treasuryBalance?: number;
		yieldPercent?: number;
		serviceFeePercent?: number;
	}
	
	let { 
		monthlyRent = 99000, 
		treasuryBalance = 100000, 
		yieldPercent = 4.4,
		serviceFeePercent = 8
	}: Props = $props();
	
	const nodeTypes = {
		moneyFlow: MoneyFlowNode
	} as const;
	
	// Define nodes
	let nodes = $derived<Node[]>([
		{
			id: 'renters',
			type: 'moneyFlow',
			position: { x: 0, y: 80 },
			data: { 
				label: 'Renters & Tenants',
				subtitle: 'Pay rent weekly/monthly',
				value: `→ $${Math.round(monthlyRent / 1000)}k/mo`,
				color: 'blue',
				icon: 'building'
			},
			draggable: false
		},
		{
			id: 'treasury',
			type: 'moneyFlow',
			position: { x: 280, y: 80 },
			data: { 
				label: 'Network Treasury',
				subtitle: 'Collects rent, pays expenses',
				value: `$${treasuryBalance.toLocaleString()}`,
				color: 'purple',
				icon: 'landmark'
			},
			draggable: false
		},
		{
			id: 'holders',
			type: 'moneyFlow',
			position: { x: 560, y: 80 },
			data: { 
				label: 'Token Holders',
				subtitle: 'Receive dividends',
				value: `${yieldPercent.toFixed(1)}% yield`,
				color: 'green',
				icon: 'trending'
			},
			draggable: false
		},
		{
			id: 'services',
			type: 'moneyFlow',
			position: { x: 280, y: 260 },
			data: { 
				label: 'Service Providers',
				subtitle: `${serviceFeePercent}% of rent`,
				value: 'Maintenance & Mgmt',
				color: 'amber',
				icon: 'wrench'
			},
			draggable: false
		}
	]);
	
	// Define edges with animation
	let edges = $derived<Edge[]>([
		{
			id: 'e-rent',
			source: 'renters',
			target: 'treasury',
			animated: true,
			style: 'stroke: #3b82f6; stroke-width: 3px;',
			label: 'Rent',
			labelStyle: 'fill: #3b82f6; font-weight: 600; font-size: 12px;'
		},
		{
			id: 'e-dividends',
			source: 'treasury',
			target: 'holders',
			animated: true,
			style: 'stroke: #22c55e; stroke-width: 3px;',
			label: 'Dividends',
			labelStyle: 'fill: #22c55e; font-weight: 600; font-size: 12px;'
		},
		{
			id: 'e-fees',
			source: 'treasury',
			target: 'services',
			sourceHandle: 'bottom',
			targetHandle: 'top',
			animated: false,
			style: 'stroke: #f59e0b; stroke-width: 2px;',
			label: `${serviceFeePercent}%`,
			labelStyle: 'fill: #f59e0b; font-weight: 600; font-size: 11px;'
		}
	]);
</script>

<div class="h-[320px] w-full bg-gradient-to-br from-slate-50 to-white rounded-xl border border-gray-200 overflow-hidden">
	<SvelteFlow 
		{nodes} 
		{edges}
		nodeTypes={nodeTypes as any}
		fitView
		fitViewOptions={{ padding: 0.3 }}
		nodesDraggable={false}
		nodesConnectable={false}
		elementsSelectable={false}
		panOnDrag={false}
		zoomOnScroll={false}
		zoomOnPinch={false}
		zoomOnDoubleClick={false}
		preventScrolling={false}
	>
		<Background gap={20} />
	</SvelteFlow>
</div>

<style>
	:global(.svelte-flow__edge-path) {
		stroke-linecap: round;
	}
	
	:global(.svelte-flow__edge.animated path) {
		stroke-dasharray: 5;
		animation: dash 0.5s linear infinite;
	}
	
	@keyframes dash {
		to {
			stroke-dashoffset: -10;
		}
	}
</style>
