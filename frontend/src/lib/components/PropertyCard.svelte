<script lang="ts">
  /**
   * PropertyCard - Compact property card with AI-generated image
   * 
   * Displays a property preview with isometric image, key stats,
   * and action buttons.
   */
  
  import { Building, Bed, Bath, Car, Eye, Sparkles } from 'lucide-svelte';
  import { Button } from "$lib/components/ui/button";
  import { Badge } from "$lib/components/ui/badge";
  
  // Props
  interface Props {
    property: any;
    onDetails?: (property: any) => void;
    onInvest?: (property: any) => void;
    compact?: boolean;
  }
  
  let { 
    property,
    onDetails = () => {},
    onInvest = () => {},
    compact = false,
  }: Props = $props();
  
  // Derived values
  let data = $derived(property?.data || property || {});
  let listing = $derived(property?.listing || {});
  let images = $derived(property?.images || {});
  let hasAiContent = $derived(!!listing?.headline || !!images?.isometric);
  
  function formatPrice(value: number): string {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(2)}M`;
    }
    return `$${value?.toLocaleString() || '0'}`;
  }
  
  function getPricePerSqm(): string {
    const size = data.land_size || data.build_area || data.land_size_sqm || data.floor_size_sqm || 200;
    const valuation = data.valuation || data.valuation_aud || 0;
    return Math.round(valuation / size).toLocaleString();
  }
</script>

<button 
  type="button" 
  class="border border-gray-200 rounded-xl overflow-hidden hover:border-blue-400 hover:shadow-xl transition-all duration-300 cursor-pointer text-left w-full bg-white group"
  onclick={() => onDetails(property)}
>
  <!-- Property Image -->
  <div class="h-40 relative overflow-hidden {compact ? 'h-32' : 'h-40'}">
    {#if images?.isometric}
      <img 
        src={images.isometric} 
        alt={data.address || 'Property'}
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
      />
    {:else}
      <div class="w-full h-full bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
        <Building class="w-12 h-12 text-blue-300" />
      </div>
    {/if}
    
    <!-- Overlays -->
    <div class="absolute top-2 left-2 flex gap-1">
      <Badge variant="secondary" class="bg-white/90 backdrop-blur text-xs shadow-sm">
        {data.property_type || 'Property'}
      </Badge>
      {#if hasAiContent}
        <Badge variant="secondary" class="bg-purple-500/90 text-white text-xs shadow-sm">
          <Sparkles class="w-3 h-3 mr-1" />
          AI
        </Badge>
      {/if}
    </div>
    
    <div class="absolute bottom-2 right-2">
      <Badge class="bg-green-600 text-white text-xs shadow-sm">
        {data.gross_yield || data.yield_percent || 4.2}% yield
      </Badge>
    </div>
    
    <!-- Gradient overlay for better text readability -->
    <div class="absolute inset-x-0 bottom-0 h-20 bg-gradient-to-t from-black/30 to-transparent"></div>
  </div>
  
  <!-- Property Details -->
  <div class="p-4">
    <!-- Price -->
    <div class="flex items-baseline gap-2 mb-1">
      <span class="text-xl font-bold text-gray-900">
        {formatPrice(data.valuation || data.valuation_aud || 0)}
      </span>
      <span class="text-sm text-gray-500">${getPricePerSqm()}/m²</span>
    </div>
    
    <!-- Headline or Address -->
    {#if listing?.headline && !compact}
      <div class="font-medium text-gray-900 text-sm leading-snug mb-1 line-clamp-2">
        {listing.headline}
      </div>
    {/if}
    <div class="text-sm text-gray-600">{data.address}</div>
    <div class="text-xs text-gray-500 mb-3">
      {data.suburb}, {data.state || 'WA'} {data.postcode || ''}
    </div>
    
    <!-- Property Features -->
    <div class="flex items-center gap-4 text-sm text-gray-600 mb-3">
      <div class="flex items-center gap-1" title="Bedrooms">
        <Bed class="w-4 h-4 text-gray-400" />
        <span>{data.bedrooms}</span>
      </div>
      <div class="flex items-center gap-1" title="Bathrooms">
        <Bath class="w-4 h-4 text-gray-400" />
        <span>{data.bathrooms}</span>
      </div>
      <div class="flex items-center gap-1" title="Parking">
        <Car class="w-4 h-4 text-gray-400" />
        <span>{data.parking || data.car_spaces || 1}</span>
      </div>
    </div>
    
    <!-- Highlights preview -->
    {#if listing?.highlights?.length && !compact}
      <div class="flex flex-wrap gap-1 mb-3">
        {#each listing.highlights.slice(0, 2) as highlight}
          <Badge variant="outline" class="text-xs py-0.5 border-gray-200">
            {highlight.title}
          </Badge>
        {/each}
        {#if listing.highlights.length > 2}
          <Badge variant="outline" class="text-xs py-0.5 border-gray-200">
            +{listing.highlights.length - 2}
          </Badge>
        {/if}
      </div>
    {/if}
    
    <!-- Actions -->
    <div class="flex justify-between items-center pt-3 border-t border-gray-100">
      <div class="flex items-center gap-1 text-xs text-gray-400">
        <Eye class="w-3 h-3" />
        <span>{property.page_views || Math.floor(Math.random() * 50) + 10} views</span>
      </div>
      <div class="flex gap-2">
        <Button 
          size="sm" 
          variant="outline" 
          onclick={(e: Event) => { e.stopPropagation(); onDetails(property); }}
        >
          Details
        </Button>
        <Button 
          size="sm"
          onclick={(e: Event) => { e.stopPropagation(); onInvest(property); }}
        >
          Invest
        </Button>
      </div>
    </div>
  </div>
</button>
