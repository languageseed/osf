/**
 * Authentication store and utilities for OSF Demo.
 * 
 * Supports three modes (determined by backend):
 * - dev: Simple email login, no verification
 * - test: Predefined test accounts
 * - google: Full Google OAuth
 */

import { browser } from '$app/environment';
import { goto } from '$app/navigation';

// Types
export interface User {
	id: string;
	email: string;
	display_name: string | null;
	roles: string[];
	created_at: string;
}

export interface AuthConfig {
	mode: 'dev' | 'test' | 'google';
	google_client_id: string | null;
	google_enabled: boolean;
}

export interface TokenResponse {
	access_token: string;
	token_type: string;
	expires_in: number;
	user: User;
}

// State
let user = $state<User | null>(null);
let token = $state<string | null>(null);
let authConfig = $state<AuthConfig | null>(null);
let isLoading = $state(false);
let error = $state<string | null>(null);

import { API_BASE as CONFIG_API_BASE } from './config';

// API base URL
const API_BASE = CONFIG_API_BASE;

// Initialize from localStorage on load
if (browser) {
	const storedToken = localStorage.getItem('osf_token');
	const storedUser = localStorage.getItem('osf_user');
	
	if (storedToken && storedUser) {
		token = storedToken;
		try {
			user = JSON.parse(storedUser);
		} catch (e) {
			// Invalid stored user, clear storage
			localStorage.removeItem('osf_token');
			localStorage.removeItem('osf_user');
		}
	}
}

/**
 * Fetch with auth headers
 */
async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
	const headers = new Headers(options.headers);
	
	if (token) {
		headers.set('Authorization', `Bearer ${token}`);
	}
	
	if (!headers.has('Content-Type') && options.body) {
		headers.set('Content-Type', 'application/json');
	}
	
	return fetch(`${API_BASE}${url}`, {
		...options,
		headers,
	});
}

/**
 * Get auth configuration from backend
 */
export async function fetchAuthConfig(): Promise<AuthConfig> {
	try {
		const res = await fetch(`${API_BASE}/api/v1/auth/config`);
		if (!res.ok) {
			throw new Error('Failed to fetch auth config');
		}
		authConfig = await res.json();
		return authConfig;
	} catch (e) {
		// Default to dev mode if backend is unavailable
		authConfig = {
			mode: 'dev',
			google_client_id: null,
			google_enabled: false,
		};
		return authConfig;
	}
}

/**
 * Dev mode: Login with just an email
 */
export async function devLogin(email: string, displayName?: string): Promise<User> {
	isLoading = true;
	error = null;
	
	try {
		const res = await fetch(`${API_BASE}/api/v1/auth/dev/login`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				email,
				display_name: displayName,
			}),
		});
		
		if (!res.ok) {
			const data = await res.json();
			throw new Error(data.detail || 'Login failed');
		}
		
		const data: TokenResponse = await res.json();
		
		// Store token and user
		token = data.access_token;
		user = data.user;
		
		if (browser) {
			localStorage.setItem('osf_token', token);
			localStorage.setItem('osf_user', JSON.stringify(user));
		}
		
		return user;
		
	} catch (e) {
		error = e instanceof Error ? e.message : 'Login failed';
		throw e;
	} finally {
		isLoading = false;
	}
}

/**
 * Test mode: Login as a predefined test user
 */
export async function testLogin(userId: string): Promise<User> {
	isLoading = true;
	error = null;
	
	try {
		const res = await fetch(`${API_BASE}/api/v1/auth/test/login?user_id=${userId}`, {
			method: 'POST',
		});
		
		if (!res.ok) {
			const data = await res.json();
			throw new Error(data.detail || 'Login failed');
		}
		
		const data: TokenResponse = await res.json();
		
		// Store token and user
		token = data.access_token;
		user = data.user;
		
		if (browser) {
			localStorage.setItem('osf_token', token);
			localStorage.setItem('osf_user', JSON.stringify(user));
		}
		
		return user;
		
	} catch (e) {
		error = e instanceof Error ? e.message : 'Login failed';
		throw e;
	} finally {
		isLoading = false;
	}
}

/**
 * Google OAuth: Redirect to Google login
 */
export function googleLogin(): void {
	window.location.href = `${API_BASE}/api/v1/auth/google/login`;
}

/**
 * Handle OAuth callback token
 */
export async function handleOAuthCallback(callbackToken: string): Promise<User> {
	isLoading = true;
	error = null;
	
	try {
		// Store the token
		token = callbackToken;
		
		if (browser) {
			localStorage.setItem('osf_token', token);
		}
		
		// Fetch user info
		const res = await authFetch('/api/v1/auth/me');
		
		if (!res.ok) {
			throw new Error('Failed to get user info');
		}
		
		user = await res.json();
		
		if (browser && user) {
			localStorage.setItem('osf_user', JSON.stringify(user));
		}
		
		return user!;
		
	} catch (e) {
		error = e instanceof Error ? e.message : 'OAuth callback failed';
		throw e;
	} finally {
		isLoading = false;
	}
}

/**
 * Logout current user
 */
export function logout(): void {
	token = null;
	user = null;
	
	if (browser) {
		localStorage.removeItem('osf_token');
		localStorage.removeItem('osf_user');
	}
}

/**
 * Update user roles
 */
export async function updateRoles(roles: string[]): Promise<User> {
	if (!token) {
		throw new Error('Not authenticated');
	}
	
	const res = await authFetch('/api/v1/auth/me', {
		method: 'PATCH',
		body: JSON.stringify({ roles }),
	});
	
	if (!res.ok) {
		throw new Error('Failed to update roles');
	}
	
	user = await res.json();
	
	if (browser && user) {
		localStorage.setItem('osf_user', JSON.stringify(user));
	}
	
	return user;
}

/**
 * Add a role to current user
 */
export async function addRole(role: string): Promise<void> {
	if (!token) {
		throw new Error('Not authenticated');
	}
	
	const res = await authFetch(`/api/v1/auth/me/roles/${role}`, {
		method: 'POST',
	});
	
	if (!res.ok) {
		throw new Error('Failed to add role');
	}
	
	const data = await res.json();
	
	if (user) {
		user.roles = data.roles;
		if (browser) {
			localStorage.setItem('osf_user', JSON.stringify(user));
		}
	}
}

/**
 * Remove a role from current user
 */
export async function removeRole(role: string): Promise<void> {
	if (!token) {
		throw new Error('Not authenticated');
	}
	
	const res = await authFetch(`/api/v1/auth/me/roles/${role}`, {
		method: 'DELETE',
	});
	
	if (!res.ok) {
		throw new Error('Failed to remove role');
	}
	
	const data = await res.json();
	
	if (user) {
		user.roles = data.roles;
		if (browser) {
			localStorage.setItem('osf_user', JSON.stringify(user));
		}
	}
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
	return !!token && !!user;
}

/**
 * Require authentication - redirect to login if not authenticated
 */
export function requireAuth(): void {
	if (browser && !isAuthenticated()) {
		goto('/auth/login');
	}
}

// Export reactive getters
export function getUser() {
	return user;
}

export function getToken() {
	return token;
}

export function getAuthConfig() {
	return authConfig;
}

export function getIsLoading() {
	return isLoading;
}

export function getError() {
	return error;
}

// Export a reactive auth object for components
export const auth = {
	get user() { return user; },
	get token() { return token; },
	get config() { return authConfig; },
	get isLoading() { return isLoading; },
	get error() { return error; },
	get isAuthenticated() { return !!token && !!user; },
};
