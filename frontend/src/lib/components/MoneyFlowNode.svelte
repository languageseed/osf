<script lang="ts">
	import { Handle, Position } from '@xyflow/svelte';
	import { Building, Landmark, TrendingUp, Wrench } from 'lucide-svelte';
	
	interface Props {
		data: {
			label: string;
			subtitle: string;
			value: string;
			color: 'blue' | 'purple' | 'green' | 'amber';
			icon: 'building' | 'landmark' | 'trending' | 'wrench';
		};
	}
	
	let { data }: Props = $props();
	
	const colorClasses = {
		blue: {
			bg: 'bg-blue-50',
			border: 'border-blue-200',
			iconBg: 'text-blue-600',
			title: 'text-blue-900',
			subtitle: 'text-blue-600',
			value: 'text-blue-700'
		},
		purple: {
			bg: 'bg-purple-50',
			border: 'border-purple-200',
			iconBg: 'text-purple-600',
			title: 'text-purple-900',
			subtitle: 'text-purple-600',
			value: 'text-purple-700'
		},
		green: {
			bg: 'bg-green-50',
			border: 'border-green-200',
			iconBg: 'text-green-600',
			title: 'text-green-900',
			subtitle: 'text-green-600',
			value: 'text-green-700'
		},
		amber: {
			bg: 'bg-amber-50',
			border: 'border-amber-200',
			iconBg: 'text-amber-600',
			title: 'text-amber-900',
			subtitle: 'text-amber-600',
			value: 'text-amber-700'
		}
	};
	
	// Use $derived for reactivity
	let colors = $derived(colorClasses[data.color] || colorClasses.blue);
	
	const icons = {
		building: Building,
		landmark: Landmark,
		trending: TrendingUp,
		wrench: Wrench
	};
	
	let IconComponent = $derived(icons[data.icon] || Building);
</script>

<div class="relative">
	<!-- Input handle (left side) -->
	<Handle type="target" position={Position.Left} class="!bg-gray-400 !w-2 !h-2" />
	
	<!-- Node content -->
	<div class="{colors.bg} {colors.border} border-2 rounded-xl p-4 min-w-[160px] text-center shadow-sm hover:shadow-md transition-shadow">
		<div class="flex justify-center mb-2">
			<div class="{colors.iconBg}">
				<IconComponent class="w-8 h-8" />
			</div>
		</div>
		<div class="font-semibold {colors.title} text-sm">{data.label}</div>
		<div class="text-xs {colors.subtitle} mt-1">{data.subtitle}</div>
		<div class="text-lg font-bold {colors.value} mt-2">{data.value}</div>
	</div>
	
	<!-- Output handle (right side) -->
	<Handle type="source" position={Position.Right} class="!bg-gray-400 !w-2 !h-2" />
	
	<!-- Bottom handle for service providers connection -->
	<Handle type="source" position={Position.Bottom} id="bottom" class="!bg-gray-400 !w-2 !h-2" />
	<Handle type="target" position={Position.Top} id="top" class="!bg-gray-400 !w-2 !h-2" />
</div>
