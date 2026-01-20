<script lang="ts">
  /**
   * PropertyDetail - Rich property detail view with AI-generated content
   * 
   * Displays property with isometric image, floor plan, highlights,
   * descriptions, and investment information.
   */
  
  import { 
    X, Bed, Bath, Car, Maximize, MapPin, TrendingUp, 
    Home, Sparkles, DollarSign, Calendar, Building,
    ChevronLeft, ChevronRight, ExternalLink
  } from 'lucide-svelte';
  import { Button } from "$lib/components/ui/button";
  import * as Card from "$lib/components/ui/card";
  import { Badge } from "$lib/components/ui/badge";
  
  // Props
  interface Props {
    property: any;
    onClose?: () => void;
    onBuyTokens?: (propertyId: string) => void;
  }
  
  let { 
    property,
    onClose = () => {},
    onBuyTokens = () => {},
  }: Props = $props();
  
  // State
  let activeTab = $state<'features' | 'lifestyle' | 'investment'>('features');
  let activeImage = $state<'isometric' | 'floorplan'>('isometric');
  
  // Computed
  let data = $derived(property?.data || {});
  let listing = $derived(property?.listing || {});
  let images = $derived(property?.images || {});
  let highlights = $derived(listing?.highlights || []);
  let quickStats = $derived(listing?.quick_stats || {});
  let propertyFeatures = $derived(listing?.property_features || {});
  let nearby = $derived(listing?.nearby || {});
  
  // Icon mapping for highlights
  const highlightIcons: Record<string, any> = {
    pool: '🏊',
    location: '📍',
    layout: '🏠',
    views: '🌅',
    garden: '🌳',
    modern: '✨',
    family: '👨‍👩‍👧‍👦',
    investment: '📈',
  };
  
  function getHighlightIcon(icon: string): string {
    return highlightIcons[icon] || '✨';
  }
  
  function formatCurrency(value: number): string {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(2)}M`;
    }
    return `$${value.toLocaleString()}`;
  }
</script>

<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
  <div class="bg-white rounded-2xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col">
    
    <!-- Header with close button -->
    <div class="flex items-center justify-between px-6 py-4 border-b bg-gradient-to-r from-blue-50 to-purple-50">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
          <Home class="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 class="text-lg font-bold text-gray-900">{data.address}</h2>
          <p class="text-sm text-gray-500">{data.suburb}, WA {data.postcode}</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Badge variant="outline" class="text-green-600 border-green-200">
          {property?.status || 'Available'}
        </Badge>
        <Button variant="ghost" size="icon" onclick={onClose}>
          <X class="w-5 h-5" />
        </Button>
      </div>
    </div>
    
    <!-- Scrollable content -->
    <div class="flex-1 overflow-y-auto">
      
      <!-- Image Section -->
      <div class="relative">
        {#if images.isometric || images.floorplan}
          <div class="aspect-video bg-gray-100 relative">
            {#if activeImage === 'isometric' && images.isometric}
              <img 
                src={images.isometric} 
                alt="Property isometric view"
                class="w-full h-full object-cover"
              />
            {:else if activeImage === 'floorplan' && images.floorplan}
              <img 
                src={images.floorplan} 
                alt="Property floor plan"
                class="w-full h-full object-contain bg-white p-4"
              />
            {:else}
              <div class="w-full h-full flex items-center justify-center text-gray-400">
                <Building class="w-16 h-16" />
              </div>
            {/if}
            
            <!-- Image toggle buttons -->
            <div class="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2 bg-white/90 backdrop-blur rounded-lg p-1 shadow-lg">
              <button 
                class="px-3 py-1.5 rounded-md text-sm font-medium transition {activeImage === 'isometric' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:bg-gray-100'}"
                onclick={() => activeImage = 'isometric'}
              >
                3D View
              </button>
              <button 
                class="px-3 py-1.5 rounded-md text-sm font-medium transition {activeImage === 'floorplan' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:bg-gray-100'}"
                onclick={() => activeImage = 'floorplan'}
              >
                Floor Plan
              </button>
            </div>
          </div>
        {:else}
          <!-- Placeholder when no images -->
          <div class="aspect-video bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
            <div class="text-center">
              <Building class="w-16 h-16 text-blue-300 mx-auto mb-2" />
              <p class="text-sm text-gray-500">AI-generated images coming soon</p>
            </div>
          </div>
        {/if}
        
        <!-- Quick stats overlay -->
        <div class="absolute top-4 left-4 flex gap-2">
          <div class="bg-white/90 backdrop-blur rounded-lg px-3 py-1.5 flex items-center gap-1.5 shadow">
            <Bed class="w-4 h-4 text-blue-600" />
            <span class="font-medium">{data.bedrooms}</span>
          </div>
          <div class="bg-white/90 backdrop-blur rounded-lg px-3 py-1.5 flex items-center gap-1.5 shadow">
            <Bath class="w-4 h-4 text-blue-600" />
            <span class="font-medium">{data.bathrooms}</span>
          </div>
          <div class="bg-white/90 backdrop-blur rounded-lg px-3 py-1.5 flex items-center gap-1.5 shadow">
            <Car class="w-4 h-4 text-blue-600" />
            <span class="font-medium">{data.parking}</span>
          </div>
          {#if data.land_size}
            <div class="bg-white/90 backdrop-blur rounded-lg px-3 py-1.5 flex items-center gap-1.5 shadow">
              <Maximize class="w-4 h-4 text-blue-600" />
              <span class="font-medium">{data.land_size}m²</span>
            </div>
          {/if}
        </div>
      </div>
      
      <!-- Headline -->
      <div class="px-6 py-4 border-b">
        <h1 class="text-xl font-bold text-gray-900 mb-1">
          {listing.headline || `${data.property_type?.toUpperCase()} IN ${data.suburb?.toUpperCase()}`}
        </h1>
        <div class="flex items-center gap-4 text-sm text-gray-500">
          <span class="flex items-center gap-1">
            <MapPin class="w-4 h-4" />
            {data.suburb}, WA
          </span>
          <span>{data.property_type}</span>
          <span>{data.architectural_style}</span>
        </div>
      </div>
      
      <!-- Highlights -->
      {#if highlights.length > 0}
        <div class="px-6 py-4 border-b bg-gray-50">
          <div class="flex items-center gap-2 mb-3">
            <Sparkles class="w-4 h-4 text-purple-500" />
            <span class="text-sm font-medium text-gray-700">AI-Generated Highlights</span>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            {#each highlights as highlight}
              <div class="bg-white rounded-lg p-3 border shadow-sm">
                <div class="flex items-start gap-2">
                  <span class="text-lg">{getHighlightIcon(highlight.icon)}</span>
                  <div>
                    <div class="font-medium text-gray-900 text-sm">{highlight.title}</div>
                    <div class="text-xs text-gray-500 mt-0.5">{highlight.description}</div>
                  </div>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}
      
      <!-- Tabs -->
      <div class="border-b">
        <div class="px-6 flex gap-4">
          <button 
            class="py-3 text-sm font-medium border-b-2 transition {activeTab === 'features' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}"
            onclick={() => activeTab = 'features'}
          >
            Features
          </button>
          <button 
            class="py-3 text-sm font-medium border-b-2 transition {activeTab === 'lifestyle' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}"
            onclick={() => activeTab = 'lifestyle'}
          >
            Lifestyle
          </button>
          <button 
            class="py-3 text-sm font-medium border-b-2 transition {activeTab === 'investment' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}"
            onclick={() => activeTab = 'investment'}
          >
            Investment
          </button>
        </div>
      </div>
      
      <!-- Tab content -->
      <div class="px-6 py-4">
        {#if activeTab === 'features'}
          <div class="space-y-4">
            {#if listing.features_description?.content}
              <div>
                <h3 class="font-bold text-gray-900 mb-2">{listing.features_description.title || 'Features'}</h3>
                <p class="text-gray-600 text-sm leading-relaxed whitespace-pre-line">
                  {listing.features_description.content}
                </p>
              </div>
            {/if}
            
            <!-- Feature lists -->
            <div class="grid grid-cols-2 gap-4 mt-4">
              {#if propertyFeatures.indoor?.length}
                <div>
                  <h4 class="font-medium text-gray-900 mb-2 text-sm">Indoor Features</h4>
                  <ul class="space-y-1">
                    {#each propertyFeatures.indoor as feature}
                      <li class="text-sm text-gray-600 flex items-center gap-2">
                        <span class="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                        {feature}
                      </li>
                    {/each}
                  </ul>
                </div>
              {/if}
              {#if propertyFeatures.outdoor?.length}
                <div>
                  <h4 class="font-medium text-gray-900 mb-2 text-sm">Outdoor Features</h4>
                  <ul class="space-y-1">
                    {#each propertyFeatures.outdoor as feature}
                      <li class="text-sm text-gray-600 flex items-center gap-2">
                        <span class="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                        {feature}
                      </li>
                    {/each}
                  </ul>
                </div>
              {/if}
            </div>
          </div>
          
        {:else if activeTab === 'lifestyle'}
          <div class="space-y-4">
            {#if listing.lifestyle_description?.content}
              <div>
                <h3 class="font-bold text-gray-900 mb-2">{listing.lifestyle_description.title || 'Lifestyle'}</h3>
                <p class="text-gray-600 text-sm leading-relaxed whitespace-pre-line">
                  {listing.lifestyle_description.content}
                </p>
              </div>
            {/if}
            
            <!-- Nearby -->
            <div class="grid grid-cols-2 gap-4 mt-4">
              {#if nearby.schools?.length}
                <div>
                  <h4 class="font-medium text-gray-900 mb-2 text-sm">Nearby Schools</h4>
                  <ul class="space-y-1">
                    {#each nearby.schools as school}
                      <li class="text-sm text-gray-600">
                        {typeof school === 'string' ? school : `${school.name} (${school.distance})`}
                      </li>
                    {/each}
                  </ul>
                </div>
              {/if}
              {#if nearby.amenities?.length}
                <div>
                  <h4 class="font-medium text-gray-900 mb-2 text-sm">Amenities</h4>
                  <ul class="space-y-1">
                    {#each nearby.amenities as amenity}
                      <li class="text-sm text-gray-600">{amenity}</li>
                    {/each}
                  </ul>
                </div>
              {/if}
            </div>
          </div>
          
        {:else if activeTab === 'investment'}
          <div class="space-y-4">
            <!-- Investment metrics -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-blue-50 rounded-lg p-3">
                <div class="text-xs text-blue-600 mb-1">Valuation</div>
                <div class="text-lg font-bold text-blue-900">{formatCurrency(data.valuation || 0)}</div>
              </div>
              <div class="bg-green-50 rounded-lg p-3">
                <div class="text-xs text-green-600 mb-1">Gross Yield</div>
                <div class="text-lg font-bold text-green-900">{data.gross_yield || 0}%</div>
              </div>
              <div class="bg-purple-50 rounded-lg p-3">
                <div class="text-xs text-purple-600 mb-1">Token Price</div>
                <div class="text-lg font-bold text-purple-900">$1.00</div>
              </div>
              <div class="bg-amber-50 rounded-lg p-3">
                <div class="text-xs text-amber-600 mb-1">Available</div>
                <div class="text-lg font-bold text-amber-900">100%</div>
              </div>
            </div>
            
            <!-- Rates -->
            {#if listing.rates}
              <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="font-medium text-gray-900 mb-2 text-sm">Annual Rates</h4>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <span class="text-xs text-gray-500">Council Rates</span>
                    <div class="font-medium">${listing.rates.council?.toLocaleString() || 'TBA'}/year</div>
                  </div>
                  <div>
                    <span class="text-xs text-gray-500">Water Rates</span>
                    <div class="font-medium">${listing.rates.water?.toLocaleString() || 'TBA'}/year</div>
                  </div>
                </div>
              </div>
            {/if}
            
            <!-- Investment calculator preview -->
            <div class="bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg p-4 text-white">
              <div class="flex items-center justify-between">
                <div>
                  <h4 class="font-medium mb-1">Invest in this property</h4>
                  <p class="text-sm text-white/80">Buy tokens to earn rental income</p>
                </div>
                <Button 
                  variant="secondary" 
                  onclick={() => onBuyTokens(property.id)}
                >
                  <TrendingUp class="w-4 h-4 mr-2" />
                  Buy Tokens
                </Button>
              </div>
            </div>
          </div>
        {/if}
      </div>
      
    </div>
    
    <!-- Footer actions -->
    <div class="px-6 py-4 border-t bg-gray-50 flex items-center justify-between">
      <div class="text-sm text-gray-500">
        Property ID: {property?.id}
      </div>
      <div class="flex gap-2">
        <Button variant="outline" onclick={onClose}>Close</Button>
        <Button onclick={() => onBuyTokens(property?.id)}>
          <DollarSign class="w-4 h-4 mr-2" />
          Invest Now
        </Button>
      </div>
    </div>
    
  </div>
</div>
