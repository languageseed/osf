<script lang="ts">
	import { Tabs as TabsPrimitive } from "bits-ui";
	import { cn } from "$lib/utils";

	type $$Props = TabsPrimitive.ContentProps;

	let { class: className, children, ...restProps }: $$Props = $props();
</script>

<TabsPrimitive.Content
	class={cn(
		"mt-2 ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2",
		className
	)}
	{...restProps}
>
	{@render children?.()}
</TabsPrimitive.Content>
