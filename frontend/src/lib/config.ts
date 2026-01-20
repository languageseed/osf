/**
 * OSF Frontend Configuration
 * 
 * Uses environment variables for production deployment.
 * Falls back to localhost for development.
 */

import { PUBLIC_API_URL, PUBLIC_MAINTENANCE_MODE, PUBLIC_MAINTENANCE_MESSAGE } from '$env/static/public';

// API base URL - set PUBLIC_API_URL in Vercel for production
export const API_BASE = PUBLIC_API_URL || 'http://localhost:8000';

// Full API path including version
export const API_V1 = `${API_BASE}/api/v1`;

// Maintenance mode - set PUBLIC_MAINTENANCE_MODE=true in Vercel to enable
export const MAINTENANCE_MODE = PUBLIC_MAINTENANCE_MODE === 'true';
export const MAINTENANCE_MESSAGE = PUBLIC_MAINTENANCE_MESSAGE || 'OSF is currently undergoing maintenance. Please check back soon.';

// Environment detection
export const IS_PRODUCTION = import.meta.env.PROD;
export const IS_DEVELOPMENT = import.meta.env.DEV;
