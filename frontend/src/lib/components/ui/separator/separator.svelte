<script lang="ts">
	import { cn } from "$lib/utils";
	import type { HTMLAttributes } from "svelte/elements";

	type $$Props = HTMLAttributes<HTMLDivElement> & {
		orientation?: "horizontal" | "vertical";
		decorative?: boolean;
	};

	let {
		class: className,
		orientation = "horizontal",
		decorative = true,
		...restProps
	}: $$Props = $props();
</script>

<div
	role={decorative ? "none" : "separator"}
	aria-orientation={decorative ? undefined : orientation}
	class={cn(
		"shrink-0 bg-gray-200",
		orientation === "horizontal" ? "h-[1px] w-full" : "h-full w-[1px]",
		className
	)}
	{...restProps}
/>
