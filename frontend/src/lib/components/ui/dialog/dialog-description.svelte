<script lang="ts">
	import { Dialog as DialogPrimitive } from "bits-ui";
	import { cn } from "$lib/utils";

	type $$Props = DialogPrimitive.DescriptionProps;

	let { class: className, children, ...restProps }: $$Props = $props();
</script>

<DialogPrimitive.Description
	class={cn("text-sm text-gray-500", className)}
	{...restProps}
>
	{@render children?.()}
</DialogPrimitive.Description>
