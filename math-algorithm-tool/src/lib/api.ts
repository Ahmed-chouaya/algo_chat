import { invoke } from '@tauri-apps/api/core';

export type Provider = 'nvidia' | 'openai' | 'anthropic';

export async function setApiKey(provider: Provider, apiKey: string): Promise<void> {
  return invoke('set_api_key', { provider, apiKey });
}

export async function getApiKey(provider: Provider): Promise<string> {
  return invoke('get_api_key', { provider });
}

export async function deleteApiKey(provider: Provider): Promise<void> {
  return invoke('delete_api_key', { provider });
}

export async function getProviders(): Promise<string[]> {
  return invoke('get_all_providers');
}