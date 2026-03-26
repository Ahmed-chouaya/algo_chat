<script lang="ts">
  import { selectedProvider, providerLabels, providers, type Provider } from '$lib/stores/settings';
  import SettingsModal from './SettingsModal.svelte';
  
  let showSettings = $state(false);
  
  const providerList = providers;
  
  function handleProviderChange(e: Event) {
    const target = e.target as HTMLSelectElement;
    selectedProvider.set(target.value as Provider);
  }
</script>

<header class="header">
  <div class="header-left">
    <div class="logo">
      <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="32" height="32" rx="8" fill="var(--color-accent)"/>
        <path d="M8 16L12 20L16 12L20 16L24 10" stroke="var(--bg-base)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <h1 class="app-name">Math Algorithm Tool</h1>
  </div>
  
  <div class="header-right">
    <div class="provider-selector">
      <select onchange={handleProviderChange} value={$selectedProvider}>
        {#each providerList as provider}
          <option value={provider}>{providerLabels[provider]}</option>
        {/each}
      </select>
    </div>
    
    <button class="settings-btn" onclick={() => showSettings = !showSettings} aria-label="Settings">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="3"/>
        <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
      </svg>
    </button>
  </div>
</header>

<SettingsModal open={showSettings} onclose={() => showSettings = false} />

<style>
  .header {
    height: 56px;
    background: var(--bg-base);
    border-bottom: 1px solid var(--color-border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 var(--space-lg);
  }
  
  .header-left {
    display: flex;
    align-items: center;
    gap: var(--space-md);
  }
  
  .logo {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .app-name {
    font-family: var(--font-display);
    font-size: 24px;
    font-weight: 400;
    letter-spacing: -0.02em;
    color: var(--color-foreground);
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: var(--space-md);
  }
  
  .provider-selector select {
    background: var(--color-surface);
    color: var(--color-foreground);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-full);
    padding: 8px 16px;
    font-family: var(--font-body);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: var(--transition);
  }
  
  .provider-selector select:hover {
    border-color: var(--color-accent);
  }
  
  .provider-selector select:focus {
    outline: none;
    border-color: var(--color-accent);
  }
  
  .settings-btn {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-full);
    background: var(--color-surface);
    color: var(--color-foreground);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: var(--transition);
  }
  
  .settings-btn:hover {
    background: var(--color-accent);
    color: var(--bg-base);
  }
</style>