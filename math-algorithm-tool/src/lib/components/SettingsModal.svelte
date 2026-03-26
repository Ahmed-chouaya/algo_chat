<script lang="ts">
  import { setApiKey, getApiKey, deleteApiKey, type Provider } from '$lib/api';
  import { selectedProvider, savedProviders, providerLabels, providers } from '$lib/stores/settings';
  
  interface Props {
    open: boolean;
    onclose: () => void;
  }
  
  let { open = false, onclose }: Props = $props();
  
  let apiKeys = $state<Record<Provider, string>>({
    nvidia: '',
    openai: '',
    anthropic: ''
  });
  
  let showPassword = $state<Record<Provider, boolean>>({
    nvidia: false,
    openai: false,
    anthropic: false
  });
  
  let saving = $state<Record<Provider, boolean>>({
    nvidia: false,
    openai: false,
    anthropic: false
  });
  
  let loadError = $state<Record<Provider, string>>({
    nvidia: '',
    openai: '',
    anthropic: ''
  });
  
  // Load saved API keys when modal opens
  $effect(() => {
    if (open) {
      loadSavedKeys();
    }
  });
  
  async function loadSavedKeys() {
    for (const provider of providers) {
      try {
        const key = await getApiKey(provider);
        if (key) {
          savedProviders.update(set => {
            set.add(provider);
            return set;
          });
        }
      } catch (e) {
        // Key doesn't exist or other error - that's fine
        loadError[provider] = '';
      }
    }
  }
  
  async function saveApiKey(provider: Provider) {
    if (!apiKeys[provider]) return;
    
    saving[provider] = true;
    try {
      await setApiKey(provider, apiKeys[provider]);
      savedProviders.update(set => {
        set.add(provider);
        return set;
      });
      apiKeys[provider] = '';
    } catch (e) {
      console.error(`Failed to save API key for ${provider}:`, e);
    } finally {
      saving[provider] = false;
    }
  }
  
  async function removeApiKey(provider: Provider) {
    try {
      await deleteApiKey(provider);
      savedProviders.update(set => {
        set.delete(provider);
        return set;
      });
    } catch (e) {
      console.error(`Failed to delete API key for ${provider}:`, e);
    }
  }
  
  function handleOverlayClick(e: MouseEvent) {
    if (e.target === e.currentTarget) {
      onclose();
    }
  }
</script>

{#if open}
  <div class="modal-overlay" onclick={handleOverlayClick} role="dialog" aria-modal="true">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Settings</h2>
        <button class="close-btn" onclick={onclose} aria-label="Close">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>
      
      <div class="modal-body">
        <!-- API Keys Section -->
        <section class="section">
          <h3>API Keys</h3>
          <p class="section-desc">Your API keys are stored securely in your system's keychain.</p>
          
          {#each providers as provider}
            <div class="api-key-row">
              <label for="api-key-{provider}">{providerLabels[provider]}</label>
              <div class="input-group">
                <input
                  id="api-key-{provider}"
                  type={showPassword[provider] ? 'text' : 'password'}
                  placeholder={$savedProviders.has(provider) ? '••••••••' : `Enter ${providerLabels[provider]} API key`}
                  bind:value={apiKeys[provider]}
                />
                <button
                  class="icon-btn"
                  onclick={() => showPassword[provider] = !showPassword[provider]}
                  aria-label={showPassword[provider] ? 'Hide password' : 'Show password'}
                >
                  {#if showPassword[provider]}
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                      <line x1="1" y1="1" x2="23" y2="23"/>
                    </svg>
                  {:else}
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                  {/if}
                </button>
                <button
                  class="save-btn"
                  onclick={() => saveApiKey(provider)}
                  disabled={!apiKeys[provider] || saving[provider]}
                >
                  {#if saving[provider]}
                    Saving...
                  {:else}
                    Save
                  {/if}
                </button>
                {#if $savedProviders.has(provider)}
                  <span class="saved-indicator" title="API key saved">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                  </span>
                  <button
                    class="remove-btn"
                    onclick={() => removeApiKey(provider)}
                    title="Remove API key"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M18 6L6 18M6 6l12 12"/>
                    </svg>
                  </button>
                {/if}
              </div>
            </div>
          {/each}
        </section>
        
        <!-- Default Provider Section -->
        <section class="section">
          <h3>Default Provider</h3>
          <p class="section-desc">Select which AI provider to use by default.</p>
          
          <div class="provider-options">
            {#each providers as provider}
              <label class="provider-option">
                <input
                  type="radio"
                  name="default-provider"
                  value={provider}
                  checked={$selectedProvider === provider}
                  onchange={() => selectedProvider.set(provider)}
                />
                <span class="radio-custom"></span>
                <span class="provider-name">{providerLabels[provider]}</span>
              </label>
            {/each}
          </div>
        </section>
        
        <!-- About Section -->
        <section class="section">
          <h3>About</h3>
          <div class="about-info">
            <p><strong>Math Algorithm Tool</strong></p>
            <p class="version">Version 0.1.0</p>
            <p class="desc">Transform mathematical algorithm descriptions from papers into working implementations.</p>
          </div>
        </section>
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  
  .modal-content {
    width: 480px;
    max-height: 90vh;
    background: var(--color-surface);
    border-radius: 24px;
    padding: 32px;
    overflow-y: auto;
  }
  
  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
  }
  
  .modal-header h2 {
    font-family: var(--font-display);
    font-size: 32px;
    font-weight: 400;
    color: var(--color-foreground);
  }
  
  .close-btn {
    width: 36px;
    height: 36px;
    border-radius: var(--radius-full);
    background: transparent;
    color: var(--color-foreground);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: var(--transition);
    opacity: 0.7;
  }
  
  .close-btn:hover {
    background: var(--color-accent);
    color: var(--bg-base);
    opacity: 1;
  }
  
  .modal-body {
    display: flex;
    flex-direction: column;
    gap: 32px;
  }
  
  .section h3 {
    font-family: var(--font-display);
    font-size: 18px;
    font-weight: 500;
    color: var(--color-foreground);
    margin-bottom: 8px;
  }
  
  .section-desc {
    font-size: 14px;
    color: var(--color-foreground);
    opacity: 0.6;
    margin-bottom: 16px;
  }
  
  .api-key-row {
    margin-bottom: 16px;
  }
  
  .api-key-row label {
    display: block;
    font-size: 14px;
    font-weight: 500;
    color: var(--color-foreground);
    margin-bottom: 8px;
  }
  
  .input-group {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .input-group input {
    flex: 1;
    height: 40px;
    padding: 0 12px;
    background: var(--bg-base);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    color: var(--color-foreground);
    font-size: 14px;
    transition: var(--transition);
  }
  
  .input-group input:focus {
    border-color: var(--color-accent);
  }
  
  .input-group input::placeholder {
    color: var(--color-foreground);
    opacity: 0.4;
  }
  
  .icon-btn {
    width: 36px;
    height: 36px;
    border-radius: var(--radius-full);
    background: var(--bg-base);
    color: var(--color-foreground);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: var(--transition);
    opacity: 0.7;
  }
  
  .icon-btn:hover {
    opacity: 1;
    color: var(--color-accent);
  }
  
  .save-btn {
    height: 36px;
    padding: 0 16px;
    background: var(--color-accent);
    color: var(--bg-base);
    font-size: 14px;
    font-weight: 600;
    border-radius: var(--radius-full);
    transition: var(--transition);
  }
  
  .save-btn:hover:not(:disabled) {
    opacity: 0.9;
  }
  
  .save-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .saved-indicator {
    color: var(--color-accent);
    display: flex;
    align-items: center;
  }
  
  .remove-btn {
    width: 24px;
    height: 24px;
    border-radius: var(--radius-full);
    background: transparent;
    color: var(--color-foreground);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: var(--transition);
    opacity: 0.5;
  }
  
  .remove-btn:hover {
    background: #ef4444;
    color: white;
    opacity: 1;
  }
  
  .provider-options {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .provider-option {
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
    padding: 8px 0;
  }
  
  .provider-option input {
    display: none;
  }
  
  .radio-custom {
    width: 20px;
    height: 20px;
    border: 2px solid var(--color-border);
    border-radius: 50%;
    position: relative;
    transition: var(--transition);
  }
  
  .provider-option input:checked + .radio-custom {
    border-color: var(--color-accent);
  }
  
  .provider-option input:checked + .radio-custom::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 10px;
    height: 10px;
    background: var(--color-accent);
    border-radius: 50%;
  }
  
  .provider-name {
    font-size: 16px;
    color: var(--color-foreground);
  }
  
  .about-info {
    padding: 16px;
    background: var(--bg-base);
    border-radius: var(--radius-lg);
  }
  
  .about-info p {
    margin: 0;
    font-size: 14px;
    color: var(--color-foreground);
  }
  
  .about-info .version {
    opacity: 0.6;
    margin: 4px 0;
  }
  
  .about-info .desc {
    opacity: 0.8;
    margin-top: 8px;
  }
</style>