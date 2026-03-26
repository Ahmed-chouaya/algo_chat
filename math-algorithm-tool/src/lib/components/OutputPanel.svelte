<script lang="ts">
  let activeTab = $state('steps');
  
  const tabs = [
    { id: 'steps', label: 'Steps' },
    { id: 'code', label: 'Code' },
    { id: 'explanation', label: 'Explanation' }
  ] as const;
</script>

<section class="output-panel">
  <nav class="tab-nav">
    {#each tabs as tab}
      <button 
        class="tab-btn" 
        class:active={activeTab === tab.id}
        onclick={() => activeTab = tab.id}
      >
        {tab.label}
      </button>
    {/each}
  </nav>
  
  <div class="tab-content">
    {#if activeTab === 'steps'}
      <div class="content-placeholder">
        <p>Algorithm steps will appear here...</p>
        <p class="hint">Process an algorithm description to see structured steps.</p>
      </div>
    {:else if activeTab === 'code'}
      <div class="content-placeholder">
        <p>Generated code will appear here...</p>
        <p class="hint">Executable Python code will be generated from the algorithm.</p>
      </div>
    {:else if activeTab === 'explanation'}
      <div class="content-placeholder">
        <p>Explanation will appear here...</p>
        <p class="hint">Detailed explanation of the algorithm and its implementation.</p>
      </div>
    {/if}
  </div>
</section>

<style>
  .output-panel {
    background: var(--bg-base);
    padding: var(--space-lg);
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
  }
  
  .tab-nav {
    display: flex;
    gap: var(--space-lg);
    border-bottom: 1px solid var(--color-border);
    padding-bottom: var(--space-md);
    margin-bottom: var(--space-lg);
  }
  
  .tab-btn {
    font-family: var(--font-body);
    font-size: 14px;
    font-weight: 500;
    color: var(--color-foreground);
    opacity: 0.6;
    padding: var(--space-sm) 0;
    position: relative;
    transition: var(--transition);
  }
  
  .tab-btn:hover {
    opacity: 0.8;
  }
  
  .tab-btn.active {
    opacity: 1;
    color: var(--color-foreground);
  }
  
  .tab-btn.active::after {
    content: '';
    position: absolute;
    bottom: -13px;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--color-accent);
  }
  
  .tab-content {
    flex: 1;
    overflow-y: auto;
  }
  
  .content-placeholder {
    background: var(--color-surface);
    border-radius: var(--radius-lg);
    padding: var(--space-lg);
    min-height: 200px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
  }
  
  .content-placeholder p {
    color: var(--color-foreground);
    opacity: 0.8;
  }
  
  .content-placeholder .hint {
    font-size: 14px;
    opacity: 0.5;
    margin-top: var(--space-sm);
  }
</style>