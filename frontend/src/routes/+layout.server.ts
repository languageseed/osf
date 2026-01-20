import { env } from '$env/dynamic/public';

export function load() {
	return {
		maintenanceMode: env.PUBLIC_MAINTENANCE_MODE === 'true',
		maintenanceMessage: env.PUBLIC_MAINTENANCE_MESSAGE || 'OSF is currently undergoing maintenance. Please check back soon.'
	};
}
