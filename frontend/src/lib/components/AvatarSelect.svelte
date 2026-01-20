<script lang="ts">
  /**
   * AvatarSelect - Avatar selection component for role selection
   * 
   * Displays available avatars from the pre-generated pool
   * and allows users to select their avatar.
   */
  
  import { Check, User, Loader2 } from 'lucide-svelte';
  
  // Props
  interface Props {
    avatars: Record<string, { role: string; category: string; image: string }>;
    selectedRole?: string;
    onSelect?: (role: string) => void;
    category?: 'participant' | 'service' | 'all';
    columns?: number;
  }
  
  let { 
    avatars = {},
    selectedRole = undefined,
    onSelect = () => {},
    category = 'all',
    columns = 4,
  }: Props = $props();
  
  // Filter avatars by category
  let filteredAvatars = $derived(() => {
    if (category === 'all') return avatars;
    return Object.fromEntries(
      Object.entries(avatars).filter(([_, v]) => v.category === category)
    );
  });
  
  // Role display names
  const roleNames: Record<string, string> = {
    investor: 'Investor',
    investor_female: 'Investor',
    renter: 'Renter',
    renter_female: 'Renter',
    homeowner: 'Homeowner',
    homeowner_female: 'Homeowner',
    foundation_partner: 'Foundation Partner',
    governor_ai: 'AI Governor',
    market_maker: 'Market Maker',
    plumber: 'Plumber',
    electrician: 'Electrician',
    gardener: 'Gardener',
    cleaner: 'Cleaner',
    painter: 'Painter',
    handyman: 'Handyman',
    building_inspector: 'Building Inspector',
    real_estate_agent: 'Real Estate Agent',
    pool_tech: 'Pool Technician',
    security_tech: 'Security Tech',
    hvac_tech: 'HVAC Technician',
    locksmith: 'Locksmith',
    pest_control: 'Pest Control',
    roofer: 'Roofer',
    conveyancer: 'Conveyancer',
    accountant: 'Accountant',
  };
  
  function getRoleName(role: string): string {
    // Remove variant suffix (e.g., investor_1 -> investor)
    const baseRole = role.replace(/_\d+$/, '');
    return roleNames[baseRole] || role.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }
</script>

<div class="grid gap-4" style="grid-template-columns: repeat({columns}, minmax(0, 1fr))">
  {#each Object.entries(filteredAvatars()) as [role, avatar]}
    <button
      class="relative group p-3 rounded-xl border-2 transition-all duration-200 {selectedRole === role ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200' : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'}"
      onclick={() => onSelect(role)}
    >
      <!-- Avatar image -->
      <div class="aspect-square rounded-lg overflow-hidden bg-gray-100 mb-2">
        {#if avatar.image}
          <img 
            src={avatar.image} 
            alt={getRoleName(role)}
            class="w-full h-full object-cover"
          />
        {:else}
          <div class="w-full h-full flex items-center justify-center text-gray-300">
            <User class="w-8 h-8" />
          </div>
        {/if}
      </div>
      
      <!-- Role name -->
      <div class="text-center">
        <div class="text-sm font-medium text-gray-900 truncate">
          {getRoleName(role)}
        </div>
        <div class="text-xs text-gray-500 capitalize">
          {avatar.category}
        </div>
      </div>
      
      <!-- Selected indicator -->
      {#if selectedRole === role}
        <div class="absolute top-2 right-2 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
          <Check class="w-4 h-4 text-white" />
        </div>
      {/if}
    </button>
  {/each}
</div>

{#if Object.keys(filteredAvatars()).length === 0}
  <div class="col-span-full text-center py-8 text-gray-500">
    <User class="w-12 h-12 mx-auto mb-2 text-gray-300" />
    <p>No avatars available</p>
    <p class="text-sm">Run the avatar generation script first</p>
  </div>
{/if}
