<script lang="ts">
	import { cn } from "$lib/utils";
	import type { HTMLAttributes } from "svelte/elements";

	type $$Props = HTMLAttributes<HTMLParagraphElement>;

	let { class: className, children, ...restProps }: $$Props = $props();
</script>

<p class={cn("text-sm text-gray-500", className)} {...restProps}>
	{@render children?.()}
</p>
