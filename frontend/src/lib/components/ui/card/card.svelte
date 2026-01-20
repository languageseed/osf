<script lang="ts">
	import { cn } from "$lib/utils";
	import type { HTMLAttributes } from "svelte/elements";

	type $$Props = HTMLAttributes<HTMLDivElement>;

	let { class: className, children, ...restProps }: $$Props = $props();
</script>

<div
	class={cn(
		"rounded-xl border border-gray-200 bg-white text-gray-900 shadow-sm",
		className
	)}
	{...restProps}
>
	{@render children?.()}
</div>
