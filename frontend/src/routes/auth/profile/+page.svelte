<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import { auth, logout, addRole, removeRole } from '$lib/auth.svelte';
	import { 
		UserCircle, 
		Mail, 
		Calendar, 
		LogOut, 
		TrendingUp, 
		Building, 
		Key, 
		Home, 
		Wrench, 
		Landmark,
		Check,
		Plus,
		ArrowLeft
	} from 'lucide-svelte';
	
	// Available roles
	const roles = [
		{ id: 'investor', label: 'Investor', icon: TrendingUp, desc: 'Buy property tokens & grow wealth', color: 'blue' },
		{ id: 'renter', label: 'Renter', icon: Building, desc: 'Find & manage your rental', color: 'cyan' },
		{ id: 'tenant', label: 'Tenant', icon: Key, desc: 'Rent-to-own pathway', color: 'emerald' },
		{ id: 'homeowner', label: 'Homeowner', icon: Home, desc: 'Access equity & manage property', color: 'amber' },
		{ id: 'custodian', label: 'Service Provider', icon: Wrench, desc: 'Earn fees for network services', color: 'orange' },
		{ id: 'foundation', label: 'Foundation Partner', icon: Landmark, desc: 'Stake capital & earn yields', color: 'purple' },
	];
	
	let isUpdating = $state<string | null>(null);
	
	onMount(() => {
		// Redirect to login if not authenticated
		if (!auth.isAuthenticated) {
			goto('/auth/login');
		}
	});
	
	async function toggleRole(roleId: string) {
		if (isUpdating) return;
		
		isUpdating = roleId;
		
		try {
			if (auth.user?.roles.includes(roleId)) {
				// Don't allow removing the last role
				if (auth.user.roles.length <= 1) {
					alert('You must have at least one role');
					return;
				}
				await removeRole(roleId);
			} else {
				await addRole(roleId);
			}
		} catch (e) {
			console.error('Failed to update role:', e);
		} finally {
			isUpdating = null;
		}
	}
	
	function handleLogout() {
		logout();
		goto('/');
	}
</script>

<svelte:head>
	<title>Profile | OSF Simulation</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<!-- Header -->
	<div class="bg-white border-b">
		<div class="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
			<a href="/simulate" class="flex items-center gap-2 text-gray-600 hover:text-gray-900">
				<ArrowLeft class="w-4 h-4" />
				Back to Simulation
			</a>
			<Button variant="ghost" size="sm" onclick={handleLogout}>
				<LogOut class="w-4 h-4 mr-2" />
				Sign out
			</Button>
		</div>
	</div>
	
	<div class="max-w-3xl mx-auto px-4 py-8 space-y-8">
		<!-- Profile Card -->
		<Card.Root>
			<Card.Header>
				<Card.Title class="flex items-center gap-2">
					<UserCircle class="w-5 h-5" />
					Your Profile
				</Card.Title>
			</Card.Header>
			<Card.Content class="space-y-4">
				{#if auth.user}
					<div class="flex items-center gap-4">
						<div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
							<span class="text-2xl font-bold text-blue-600">
								{auth.user.display_name?.[0] || auth.user.email?.[0] || '?'}
							</span>
						</div>
						<div>
							<h2 class="text-xl font-semibold text-gray-900">
								{auth.user.display_name || 'User'}
							</h2>
							<div class="flex items-center gap-2 text-gray-500 text-sm mt-1">
								<Mail class="w-4 h-4" />
								{auth.user.email}
							</div>
							<div class="flex items-center gap-2 text-gray-500 text-sm mt-1">
								<Calendar class="w-4 h-4" />
								Joined {new Date(auth.user.created_at).toLocaleDateString()}
							</div>
						</div>
					</div>
				{:else}
					<p class="text-gray-500">Loading...</p>
				{/if}
			</Card.Content>
		</Card.Root>
		
		<!-- Role Selection -->
		<Card.Root>
			<Card.Header>
				<Card.Title>Your Roles</Card.Title>
				<Card.Description>
					Select the roles you want to participate in. You can change these at any time.
				</Card.Description>
			</Card.Header>
			<Card.Content>
				<div class="grid gap-3">
					{#each roles as role}
						{@const isActive = auth.user?.roles.includes(role.id)}
						{@const Icon = role.icon}
						<button
							class="w-full p-4 text-left rounded-lg border-2 transition flex items-center gap-4 {
								isActive 
									? 'border-blue-500 bg-blue-50' 
									: 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
							}"
							onclick={() => toggleRole(role.id)}
							disabled={isUpdating === role.id}
						>
							<div class="w-10 h-10 rounded-lg flex items-center justify-center {
								isActive ? 'bg-blue-100' : 'bg-gray-100'
							}">
								<Icon class="w-5 h-5 {isActive ? 'text-blue-600' : 'text-gray-500'}" />
							</div>
							<div class="flex-1">
								<div class="flex items-center gap-2">
									<span class="font-medium text-gray-900">{role.label}</span>
									{#if isActive}
										<Badge variant="default" class="bg-blue-100 text-blue-700 border-0">Active</Badge>
									{/if}
								</div>
								<p class="text-sm text-gray-500">{role.desc}</p>
							</div>
							<div class="w-8 h-8 rounded-full flex items-center justify-center {
								isActive ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-400'
							}">
								{#if isUpdating === role.id}
									<span class="animate-spin">⏳</span>
								{:else if isActive}
									<Check class="w-4 h-4" />
								{:else}
									<Plus class="w-4 h-4" />
								{/if}
							</div>
						</button>
					{/each}
				</div>
			</Card.Content>
		</Card.Root>
		
		<!-- Actions -->
		<div class="flex justify-center">
			<Button href="/simulate" size="lg">
				Continue to Simulation →
			</Button>
		</div>
	</div>
</div>
