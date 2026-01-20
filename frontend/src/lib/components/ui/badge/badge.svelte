<script lang="ts" module>
	import { tv, type VariantProps } from "tailwind-variants";

	export const badgeVariants = tv({
		base: "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
		variants: {
			variant: {
				default: "border-transparent bg-blue-600 text-white",
				secondary: "border-transparent bg-gray-100 text-gray-900",
				destructive: "border-transparent bg-red-600 text-white",
				outline: "border-gray-200 text-gray-900",
				success: "border-transparent bg-green-100 text-green-800",
				warning: "border-transparent bg-amber-100 text-amber-800",
			},
		},
		defaultVariants: {
			variant: "default",
		},
	});

	export type BadgeVariant = VariantProps<typeof badgeVariants>["variant"];
	export type BadgeProps = {
		variant?: BadgeVariant;
		class?: string;
	};
</script>

<script lang="ts">
	import { cn } from "$lib/utils";
	import type { HTMLAttributes } from "svelte/elements";

	type $$Props = HTMLAttributes<HTMLDivElement> & BadgeProps;

	let { class: className, variant = "default", children, ...restProps }: $$Props = $props();
</script>

<div class={cn(badgeVariants({ variant }), className)} {...restProps}>
	{@render children?.()}
</div>
