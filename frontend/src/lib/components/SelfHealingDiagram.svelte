<script lang="ts">
	import { SvelteFlow, Background, type Node, type Edge } from '@xyflow/svelte';
	import '@xyflow/svelte/dist/style.css';
	
	import SelfHealingNode from './SelfHealingNode.svelte';
	
	interface Props {
		activeStep?: 'sense' | 'diagnose' | 'respond' | 'verify' | 'learn' | null;
	}
	
	let { activeStep = null }: Props = $props();
	
	const nodeTypes = {
		healingStep: SelfHealingNode
	} as const;
	
	// Circular layout for the cycle
	const centerX = 200;
	const centerY = 150;
	const radius = 130;
	
	// Define nodes in a circle
	let nodes = $derived<Node[]>([
		{
			id: 'sense',
			type: 'healingStep',
			position: { x: centerX + radius * Math.cos(-Math.PI/2), y: centerY + radius * Math.sin(-Math.PI/2) - 30 },
			data: { 
				label: 'Sense',
				description: 'Monitor metrics',
				icon: 'activity',
				active: activeStep === 'sense'
			},
			draggable: false
		},
		{
			id: 'diagnose',
			type: 'healingStep',
			position: { x: centerX + radius * Math.cos(-Math.PI/5), y: centerY + radius * Math.sin(-Math.PI/5) - 20 },
			data: { 
				label: 'Diagnose',
				description: 'Root cause',
				icon: 'search',
				active: activeStep === 'diagnose'
			},
			draggable: false
		},
		{
			id: 'respond',
			type: 'healingStep',
			position: { x: centerX + radius * Math.cos(Math.PI/5), y: centerY + radius * Math.sin(Math.PI/5) + 10 },
			data: { 
				label: 'Respond',
				description: 'Activate strategy',
				icon: 'zap',
				active: activeStep === 'respond'
			},
			draggable: false
		},
		{
			id: 'verify',
			type: 'healingStep',
			position: { x: centerX + radius * Math.cos(3*Math.PI/5), y: centerY + radius * Math.sin(3*Math.PI/5) + 10 },
			data: { 
				label: 'Verify',
				description: 'Check results',
				icon: 'check',
				active: activeStep === 'verify'
			},
			draggable: false
		},
		{
			id: 'learn',
			type: 'healingStep',
			position: { x: centerX + radius * Math.cos(4*Math.PI/5), y: centerY + radius * Math.sin(4*Math.PI/5) - 20 },
			data: { 
				label: 'Learn',
				description: 'Improve strategy',
				icon: 'brain',
				active: activeStep === 'learn'
			},
			draggable: false
		}
	]);
	
	// Define edges connecting the cycle
	let edges = $derived<Edge[]>([
		{
			id: 'e-sense-diagnose',
			source: 'sense',
			target: 'diagnose',
			animated: activeStep === 'sense',
			style: activeStep === 'sense' ? 'stroke: #3b82f6; stroke-width: 3px;' : 'stroke: #94a3b8; stroke-width: 2px;',
			type: 'smoothstep'
		},
		{
			id: 'e-diagnose-respond',
			source: 'diagnose',
			target: 'respond',
			animated: activeStep === 'diagnose',
			style: activeStep === 'diagnose' ? 'stroke: #3b82f6; stroke-width: 3px;' : 'stroke: #94a3b8; stroke-width: 2px;',
			type: 'smoothstep'
		},
		{
			id: 'e-respond-verify',
			source: 'respond',
			target: 'verify',
			animated: activeStep === 'respond',
			style: activeStep === 'respond' ? 'stroke: #3b82f6; stroke-width: 3px;' : 'stroke: #94a3b8; stroke-width: 2px;',
			type: 'smoothstep'
		},
		{
			id: 'e-verify-learn',
			source: 'verify',
			target: 'learn',
			animated: activeStep === 'verify',
			style: activeStep === 'verify' ? 'stroke: #3b82f6; stroke-width: 3px;' : 'stroke: #94a3b8; stroke-width: 2px;',
			type: 'smoothstep'
		},
		{
			id: 'e-learn-sense',
			source: 'learn',
			target: 'sense',
			animated: activeStep === 'learn',
			style: activeStep === 'learn' ? 'stroke: #3b82f6; stroke-width: 3px;' : 'stroke: #94a3b8; stroke-width: 2px;',
			type: 'smoothstep'
		}
	]);
</script>

<div class="h-[350px] w-full bg-gradient-to-br from-blue-50/50 to-white rounded-xl border border-blue-100 overflow-hidden">
	<SvelteFlow 
		{nodes} 
		{edges}
		nodeTypes={nodeTypes as any}
		fitView
		fitViewOptions={{ padding: 0.2 }}
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
	:global(.svelte-flow__edge.animated path) {
		stroke-dasharray: 5;
		animation: dash 0.4s linear infinite;
	}
	
	@keyframes dash {
		to {
			stroke-dashoffset: -10;
		}
	}
</style>
