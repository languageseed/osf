<script lang="ts">
	import { Handle, Position } from '@xyflow/svelte';
	import { Activity, Search, Zap, CheckCircle, Brain } from 'lucide-svelte';
	
	interface Props {
		data: {
			label: string;
			description: string;
			icon: 'activity' | 'search' | 'zap' | 'check' | 'brain';
			active: boolean;
		};
	}
	
	let { data }: Props = $props();
	
	const icons = {
		activity: Activity,
		search: Search,
		zap: Zap,
		check: CheckCircle,
		brain: Brain
	};
	
	let IconComponent = $derived(icons[data.icon] || Activity);
</script>

<div class="relative">
	<Handle type="target" position={Position.Left} class="!bg-blue-400 !w-2 !h-2" />
	
	<div class="rounded-xl p-3 min-w-[100px] text-center transition-all duration-300 {data.active ? 'bg-blue-100 border-2 border-blue-500 shadow-lg scale-110' : 'bg-white border border-gray-200 shadow-sm'}">
		<div class="flex justify-center mb-1">
			<div class="{data.active ? 'text-blue-600' : 'text-gray-500'}">
				<IconComponent class="w-6 h-6" />
			</div>
		</div>
		<div class="font-semibold text-sm {data.active ? 'text-blue-900' : 'text-gray-700'}">{data.label}</div>
		<div class="text-xs {data.active ? 'text-blue-600' : 'text-gray-500'} mt-0.5">{data.description}</div>
	</div>
	
	<Handle type="source" position={Position.Right} class="!bg-blue-400 !w-2 !h-2" />
</div>
