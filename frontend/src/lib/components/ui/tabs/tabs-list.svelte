<script lang="ts">
	import { Tabs as TabsPrimitive } from "bits-ui";
	import { cn } from "$lib/utils";

	type $$Props = TabsPrimitive.ListProps;

	let { class: className, children, ...restProps }: $$Props = $props();
</script>

<TabsPrimitive.List
	class={cn(
		"inline-flex h-10 items-center justify-center rounded-lg bg-gray-100 p-1 text-gray-500",
		className
	)}
	{...restProps}
>
	{@render children?.()}
</TabsPrimitive.List>
