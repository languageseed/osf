import adapterVercel from '@sveltejs/adapter-vercel';
import adapterAuto from '@sveltejs/adapter-auto';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

// Use Vercel adapter in production, auto adapter for local dev
const isVercel = process.env.VERCEL === '1';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),
	kit: {
		adapter: isVercel 
			? adapterVercel({
				runtime: 'nodejs20.x',
				regions: ['syd1'], // Sydney for Australian users
			})
			: adapterAuto()
	}
};

export default config;
