/**
 * Pool Store - Manages property and avatar pools from the backend API
 * 
 * Provides reactive state for:
 * - Pre-generated property listings with AI images
 * - Character avatars for role selection
 */

// Pool state
let properties = $state<PoolProperty[]>([]);
let avatars = $state<Record<string, PoolAvatar>>({});
let loading = $state(false);
let error = $state<string | null>(null);
let poolStatus = $state<PoolStatus | null>(null);

// Types
export interface PoolProperty {
  id: string;
  status: 'draft' | 'available' | 'enabled';
  address: string;
  suburb: string;
  property_type: string;
  bedrooms: number;
  bathrooms: number;
  valuation: number;
  headline: string;
  has_images: boolean;
  // Optional highlights at top level (legacy format)
  highlights?: Array<{
    icon: string;
    title: string;
    description: string;
  }>;
  // Full data when fetched individually
  data?: {
    address: string;
    suburb: string;
    state: string;
    postcode: string;
    property_type: string;
    bedrooms: number;
    bathrooms: number;
    parking: number;
    land_size: number;
    build_area: number;
    year_built: number;
    architectural_style: string;
    features: string[];
    valuation: number;
    gross_yield: number;
  };
  listing?: {
    property_id: string;
    headline: string;
    subheadline: string;
    highlights: Array<{
      icon: string;
      title: string;
      description: string;
    }>;
    quick_stats: {
      bedrooms: number;
      bathrooms: number;
      parking: number;
      land_size: string;
      build_area: string;
      property_type: string;
      status: string;
    };
    features_description: {
      title: string;
      content: string;
    };
    lifestyle_description: {
      title: string;
      content: string;
    };
    property_features: {
      indoor: string[];
      outdoor: string[];
    };
    nearby: {
      schools: Array<{ name: string; distance: string; type: string }>;
      amenities: string[];
    };
    rates: {
      council: number;
      water: number;
    };
    image_brief: Record<string, string>;
    floorplan_brief: Record<string, any>;
  };
  images?: {
    isometric: string;
    floorplan: string;
  };
}

export interface PoolAvatar {
  role: string;
  category: 'participant' | 'service';
  image: string;
  generated_at: string;
}

export interface PoolStatus {
  exists: boolean;
  count: number;
  generated_at: string;
  available: number;
  enabled: number;
}

import { API_V1 } from './config';

// API base URL - defaults to configured value
let apiBase = API_V1;

/**
 * Initialize the pool store with API base URL (optional, uses config default)
 */
export function initPool(base?: string) {
  if (base) apiBase = base;
}

/**
 * Fetch pool status
 */
export async function fetchPoolStatus(): Promise<PoolStatus | null> {
  try {
    const res = await fetch(`${apiBase}/pool/properties/status`);
    if (res.ok) {
      poolStatus = await res.json();
      return poolStatus;
    }
  } catch (e) {
    console.error('Failed to fetch pool status:', e);
  }
  return null;
}

/**
 * Fetch properties from the pool
 */
export async function fetchProperties(limit = 12, status?: string): Promise<PoolProperty[]> {
  loading = true;
  error = null;
  
  try {
    const params = new URLSearchParams();
    if (limit) params.set('limit', limit.toString());
    if (status) params.set('status', status);
    
    const res = await fetch(`${apiBase}/pool/properties?${params}`);
    if (!res.ok) {
      throw new Error(`Failed to fetch properties: ${res.status}`);
    }
    
    properties = await res.json();
    return properties;
  } catch (e) {
    error = e instanceof Error ? e.message : 'Unknown error';
    console.error('Failed to fetch properties:', e);
    return [];
  } finally {
    loading = false;
  }
}

/**
 * Fetch a single property with full details
 */
export async function fetchProperty(id: string): Promise<PoolProperty | null> {
  try {
    const res = await fetch(`${apiBase}/pool/properties/${id}`);
    if (!res.ok) {
      throw new Error(`Failed to fetch property: ${res.status}`);
    }
    
    const property = await res.json();
    
    // Update in the local array if exists
    const idx = properties.findIndex(p => p.id === id);
    if (idx >= 0) {
      properties[idx] = property;
    }
    
    return property;
  } catch (e) {
    console.error('Failed to fetch property:', e);
    return null;
  }
}

/**
 * Fetch avatars from the pool
 */
export async function fetchAvatars(): Promise<Record<string, PoolAvatar>> {
  try {
    const res = await fetch(`${apiBase}/pool/avatars`);
    if (!res.ok) {
      throw new Error(`Failed to fetch avatars: ${res.status}`);
    }
    
    avatars = await res.json();
    return avatars;
  } catch (e) {
    console.error('Failed to fetch avatars:', e);
    return {};
  }
}

/**
 * Get avatar by role
 */
export async function fetchAvatar(role: string): Promise<PoolAvatar | null> {
  try {
    const res = await fetch(`${apiBase}/pool/avatars/${role}`);
    if (!res.ok) {
      return null;
    }
    return await res.json();
  } catch (e) {
    console.error('Failed to fetch avatar:', e);
    return null;
  }
}

/**
 * Enable the next available property
 */
export async function enableNextProperty(): Promise<{ property_id: string; suburb: string } | null> {
  try {
    const res = await fetch(`${apiBase}/pool/properties/enable-next`, { method: 'POST' });
    if (!res.ok) {
      throw new Error(`Failed to enable property: ${res.status}`);
    }
    
    const result = await res.json();
    
    // Refresh properties list
    await fetchProperties();
    
    return result;
  } catch (e) {
    console.error('Failed to enable property:', e);
    return null;
  }
}

// Export reactive getters
export function getProperties() {
  return properties;
}

export function getAvatars() {
  return avatars;
}

export function getLoading() {
  return loading;
}

export function getError() {
  return error;
}

export function getPoolStatus() {
  return poolStatus;
}

// Filter helpers
export function getParticipantAvatars(): Record<string, PoolAvatar> {
  return Object.fromEntries(
    Object.entries(avatars).filter(([_, v]) => v.category === 'participant')
  );
}

export function getServiceAvatars(): Record<string, PoolAvatar> {
  return Object.fromEntries(
    Object.entries(avatars).filter(([_, v]) => v.category === 'service')
  );
}

export function getEnabledProperties(): PoolProperty[] {
  return properties.filter(p => p.status === 'enabled' || p.status === 'available');
}
