<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { handleOAuthCallback } from '$lib/auth.svelte';
	import { Loader2, AlertCircle } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	
	let error = $state<string | null>(null);
	let isProcessing = $state(true);
	
	onMount(async () => {
		// Get token from URL
		const token = $page.url.searchParams.get('token');
		const urlError = $page.url.searchParams.get('error');
		
		if (urlError) {
			error = urlError;
			isProcessing = false;
			return;
		}
		
		if (!token) {
			error = 'No token received from authentication';
			isProcessing = false;
			return;
		}
		
		try {
			await handleOAuthCallback(token);
			// Redirect to simulation
			goto('/simulate');
		} catch (e) {
			error = e instanceof Error ? e.message : 'Authentication failed';
			isProcessing = false;
		}
	});
</script>

<svelte:head>
	<title>Authenticating... | OSF Simulation</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-4">
	<div class="text-center">
		{#if isProcessing}
			<div class="flex flex-col items-center gap-4">
				<Loader2 class="w-12 h-12 animate-spin text-blue-600" />
				<div>
					<h1 class="text-xl font-semibold text-gray-900">Completing sign in...</h1>
					<p class="text-gray-500 text-sm mt-1">Please wait while we verify your credentials</p>
				</div>
			</div>
		{:else if error}
			<div class="flex flex-col items-center gap-4">
				<div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
					<AlertCircle class="w-8 h-8 text-red-600" />
				</div>
				<div>
					<h1 class="text-xl font-semibold text-gray-900">Authentication Failed</h1>
					<p class="text-red-600 text-sm mt-1">{error}</p>
				</div>
				<Button href="/auth/login" class="mt-4">
					Try Again
				</Button>
			</div>
		{/if}
	</div>
</div>
