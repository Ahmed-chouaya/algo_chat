<script lang="ts">
  import { processedInput, isProcessing } from '$lib/stores/processing';
  import { algorithmStore } from '$lib/stores/algorithm';
  import StepReview from './StepReview.svelte';
  
  let activeTab = $state('steps');
  
  const tabs = [
    { id: 'steps', label: 'Steps' },
    { id: 'code', label: 'Code' },
    { id: 'explanation', label: 'Explanation' }
  ] as const;

  function handleConfirm() {
    algorithmStore.confirm();
  }

  function handleRegenerate() {
    // Reset confirmation and trigger re-processing
    algorithmStore.setSteps($algorithmStore.steps);
  }
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
          {#if $algorithmStore.steps.length > 0}
            <!-- Show step review with confidence markers -->
            <StepReview steps={$algorithmStore.steps} />
            
            <!-- Confirmation UI (D-04: Stage gate) -->
            {#if !$algorithmStore.confirmed}
              <div class="confirmation-panel">
                <p class="confirmation-text">Review the steps above to ensure they correctly interpret the algorithm.</p>
                <div class="confirmation-buttons">
                  <button class="btn btn-secondary" onclick={handleRegenerate}>
                    Regenerate
                  </button>
                  <button class="btn btn-primary" onclick={handleConfirm}>
                    Confirm Steps
                  </button>
                </div>
              </div>
            {:else}
              <div class="confirmed-badge">
                ✓ Steps confirmed - Ready for code generation
              </div>
            {/if}
          {:else}
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
          {/if}
        </div>
      {:else if activeTab === 'code'}
        <div class="code-generation-panel">
          {#if $algorithmStore.steps.length > 0}
            {#if $algorithmStore.confirmed}
              <p>Code will be generated here...</p>
              <p class="hint">Click "Generate Code" to create the implementation.</p>
              <button class="btn btn-primary btn-generate">
                Generate Code
              </button>
            {:else}
              <div class="gate-notice">
                <span class="gate-icon">🔒</span>
                <p>Confirm step interpretation to enable code generation</p>
              </div>
            {/if}
          {:else}
            <div class="content-placeholder">
              <p>Code generation...</p>
              <p class="hint">Step extraction complete. Code generation available in next phase.</p>
            </div>
          {/if}
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

  /* Confirmation panel styles */
  .confirmation-panel {
    background: var(--color-surface);
    border-radius: var(--radius-lg);
    padding: var(--space-lg);
    margin-top: var(--space-lg);
    border: 1px solid var(--color-border);
  }

  .confirmation-text {
    font-size: 14px;
    color: var(--color-foreground);
    margin: 0 0 var(--space-lg) 0;
  }

  .confirmation-buttons {
    display: flex;
    gap: var(--space-md);
    justify-content: flex-end;
  }

  .btn {
    font-family: var(--font-body);
    font-weight: 500;
    font-size: 14px;
    padding: 10px 20px;
    border-radius: var(--radius-full);
    transition: var(--transition);
    cursor: pointer;
    border: none;
  }

  .btn-primary {
    background: var(--color-accent);
    color: var(--bg-base);
  }

  .btn-primary:hover {
    filter: brightness(1.1);
  }

  .btn-secondary {
    background: transparent;
    border: 1px solid var(--color-border);
    color: var(--color-foreground);
  }

  .btn-secondary:hover {
    border-color: var(--color-accent);
    color: var(--color-accent);
  }

  .confirmed-badge {
    background: rgba(34, 197, 94, 0.1);
    color: var(--color-success);
    padding: var(--space-md) var(--space-lg);
    border-radius: var(--radius-lg);
    font-size: 14px;
    font-weight: 500;
    margin-top: var(--space-lg);
    text-align: center;
  }

  .code-generation-panel {
    min-height: 200px;
  }

  .code-generation-panel .content-placeholder {
    background: var(--color-surface);
    border-radius: var(--radius-lg);
    padding: var(--space-xl);
    min-height: 200px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
  }

  .code-generation-panel p {
    color: var(--color-foreground);
    opacity: 0.8;
    margin: 0;
  }

  .code-generation-panel .hint {
    font-size: 14px;
    opacity: 0.5;
    margin-top: var(--space-sm);
  }

  .btn-generate {
    margin-top: var(--space-lg);
    padding: 12px 32px;
    font-size: 16px;
  }

  .gate-notice {
    background: var(--color-surface);
    border-radius: var(--radius-lg);
    padding: var(--space-xl);
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-md);
  }

  .gate-notice p {
    color: var(--color-foreground);
    opacity: 0.7;
    margin: 0;
  }

  .gate-icon {
    font-size: 32px;
  }
</style>