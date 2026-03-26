import { writable, derived } from 'svelte/store';

export type Provider = 'nvidia' | 'openai' | 'anthropic';

export const selectedProvider = writable<Provider>('nvidia');
export const savedProviders = writable<Set<Provider>>(new Set());

export const providerLabels: Record<Provider, string> = {
  nvidia: 'NVIDIA',
  openai: 'OpenAI',
  anthropic: 'Anthropic'
};

export const providers: Provider[] = ['nvidia', 'openai', 'anthropic'];