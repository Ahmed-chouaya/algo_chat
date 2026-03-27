<script lang="ts">
  import { processedInput, isProcessing } from '$lib/stores/processing';
  
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
    {#if $isProcessing}
      <div class="content-placeholder">
        <p>Processing algorithm...</p>
        <p class="hint">Extracting LaTeX and parsing steps.</p>
      </div>
    {:else if $processedInput.sections.length > 0}
      {#if activeTab === 'steps'}
        <div class="steps-content">
          {#each $processedInput.sections as section}
            {#if section.title}
              <h3 class="section-title">{section.title}</h3>
            {/if}
            <p class="section-content">{section.content}</p>
          {/each}
          
          {#if $processedInput.latex_expressions.length > 0}
            <div class="latex-expressions">
              <h4>Extracted LaTeX Expressions</h4>
              {#each $processedInput.latex_expressions as expr}
                <code class="latex-item">{expr.latex}</code>
              {/each}
            </div>
          {/if}
        </div>
      {:else if activeTab === 'code'}
        <div class="content-placeholder">
          <p>Code generation...</p>
          <p class="hint">Step extraction complete. Code generation available in next phase.</p>
        </div>
      {:else if activeTab === 'explanation'}
        <div class="content-placeholder">
          <p>Explanation will appear here...</p>
          <p class="hint">Detailed explanation of the algorithm and its implementation.</p>
        </div>
      {/if}
    {:else}
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
  
  .steps-content {
    display: flex;
    flex-direction: column;
    gap: var(--space-md);
  }
  
  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0;
  }
  
  .section-content {
    font-size: 14px;
    line-height: 1.6;
    color: var(--color-foreground);
    opacity: 0.9;
    margin: 0;
  }
  
  .latex-expressions {
    margin-top: var(--space-lg);
    padding-top: var(--space-md);
    border-top: 1px solid var(--color-border);
  }
  
  .latex-expressions h4 {
    font-size: 14px;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0 0 var(--space-sm) 0;
  }
  
  .latex-item {
    display: block;
    background: var(--color-surface);
    padding: var(--space-sm) var(--space-md);
    border-radius: var(--radius-md);
    font-family: var(--font-mono);
    font-size: 13px;
    margin-bottom: var(--space-xs);
  }
</style>