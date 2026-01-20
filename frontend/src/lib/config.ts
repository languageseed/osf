/**
 * OSF Frontend Configuration
 * 
 * Uses environment variables for production deployment.
 * Falls back to localhost for development.
 */

// API base URL - set PUBLIC_API_URL in Vercel for production
export const API_BASE = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';

// Full API path including version
export const API_V1 = `${API_BASE}/api/v1`;

// Feature flags
export const ENABLE_AUTH = import.meta.env.PUBLIC_ENABLE_AUTH === 'true';
export const ENABLE_ANALYTICS = import.meta.env.PUBLIC_ENABLE_ANALYTICS === 'true';

// Environment detection
export const IS_PRODUCTION = import.meta.env.PROD;
export const IS_DEVELOPMENT = import.meta.env.DEV;
