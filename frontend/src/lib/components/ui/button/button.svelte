<script lang="ts" module>
	import { tv, type VariantProps } from "tailwind-variants";

	export const buttonVariants = tv({
		base: "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
		variants: {
			variant: {
				default: "bg-blue-600 text-white hover:bg-blue-700",
				destructive: "bg-red-600 text-white hover:bg-red-700",
				outline: "border border-gray-200 bg-white hover:bg-gray-50 hover:text-gray-900",
				secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200",
				ghost: "hover:bg-gray-100 hover:text-gray-900",
				link: "text-blue-600 underline-offset-4 hover:underline",
				success: "bg-green-600 text-white hover:bg-green-700",
			},
			size: {
				default: "h-10 px-4 py-2",
				sm: "h-9 rounded-md px-3",
				lg: "h-11 rounded-lg px-8",
				icon: "h-10 w-10",
			},
		},
		defaultVariants: {
			variant: "default",
			size: "default",
		},
	});

	export type ButtonVariant = VariantProps<typeof buttonVariants>["variant"];
	export type ButtonSize = VariantProps<typeof buttonVariants>["size"];
	export type ButtonProps = {
		variant?: ButtonVariant;
		size?: ButtonSize;
		class?: string;
	};
</script>

<script lang="ts">
	import { cn } from "$lib/utils";
	import type { HTMLButtonAttributes } from "svelte/elements";

	type $$Props = HTMLButtonAttributes & ButtonProps;

	let {
		class: className,
		variant = "default",
		size = "default",
		children,
		...restProps
	}: $$Props = $props();
</script>

<button class={cn(buttonVariants({ variant, size }), className)} {...restProps}>
	{@render children?.()}
</button>
