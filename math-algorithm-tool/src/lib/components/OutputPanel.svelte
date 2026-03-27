<script lang="ts">
  import { processedInput, isProcessing } from '$lib/stores/processing';
  import { algorithmStore } from '$lib/stores/algorithm';
  import { generatePythonCode, executePythonCode, type ExecutionResult } from '$lib/processing';
  import StepReview from './StepReview.svelte';
  
  let activeTab = $state<'steps' | 'code' | 'results'>('steps');
  let isGenerating = $state(false);
  let generationError = $state<string | null>(null);
  
  const tabs = [
    { id: 'steps', label: 'Steps' },
    { id: 'code', label: 'Code' },
    { id: 'results', label: 'Results' }
  ] as const;

  function handleConfirm() {
    algorithmStore.confirm();
  }

  function handleRegenerate() {
    // Reset confirmation and trigger re-processing
    algorithmStore.setSteps($algorithmStore.steps);
  }

  async function handleGenerateCode() {
    if ($algorithmStore.steps.length === 0) return;
    
    isGenerating = true;
    generationError = null;
    
    try {
      const result = await generatePythonCode($algorithmStore.steps);
      
      if (result.code) {
        algorithmStore.setGeneratedCode(result.code, result);
      }
      
      if (result.errors && result.errors.length > 0) {
        generationError = result.errors.join(', ');
      }
    } catch (error) {
      console.error('Code generation failed:', error);
      generationError = error?.toString() || 'Failed to generate code';
    } finally {
      isGenerating = false;
    }
  }

  async function handleRunCode() {
    if (!$algorithmStore.generatedCode) return;
    
    algorithmStore.setExecuting(true);
    algorithmStore.setExecutionResult(null);
    
    try {
      const result = await executePythonCode($algorithmStore.generatedCode);
      algorithmStore.setExecutionResult(result);
    } catch (error) {
      console.error('Code execution failed:', error);
      algorithmStore.setExecutionResult({
        stdout: '',
        stderr: '',
        return_code: -1,
        timed_out: false,
        memory_exceeded: false,
        execution_time_ms: 0,
        error_message: error?.toString() || 'Failed to execute code'
      });
    } finally {
      algorithmStore.setExecuting(false);
    }
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
              {#if $algorithmStore.generatedCode}
                <div class="code-display">
                  <pre><code>{$algorithmStore.generatedCode}</code></pre>
                </div>
                <div class="code-actions">
                  <button 
                    class="btn btn-primary btn-run" 
                    onclick={handleRunCode}
                    disabled={$algorithmStore.isExecuting}
                  >
                    {$algorithmStore.isExecuting ? 'Running...' : '▶ Run Code'}
                  </button>
                  <button 
                    class="btn btn-secondary" 
                    onclick={handleGenerateCode}
                    disabled={isGenerating}
                  >
                    {isGenerating ? 'Generating...' : 'Regenerate'}
                  </button>
                </div>
                {#if generationError}
                  <div class="error-message">{generationError}</div>
                {/if}
              {:else}
                <p>Click the button to generate Python code from the algorithm steps.</p>
                <button 
                  class="btn btn-primary btn-generate" 
                  onclick={handleGenerateCode}
                  disabled={isGenerating}
                >
                  {isGenerating ? 'Generating...' : 'Generate Code'}
                </button>
                {#if generationError}
                  <div class="error-message">{generationError}</div>
                {/if}
              {/if}
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
      {:else if activeTab === 'results'}
        <div class="results-panel">
          {#if $algorithmStore.executionResult}
            {@const result = $algorithmStore.executionResult}
            <div class="result-status" class:error={result.error_message || result.return_code !== 0}>
              {#if result.timed_out}
                <span class="status-icon">⏱️</span>
                <span>Execution timed out</span>
              {:else if result.memory_exceeded}
                <span class="status-icon">💾</span>
                <span>Memory limit exceeded</span>
              {:else if result.error_message}
                <span class="status-icon">⚠️</span>
                <span>{result.error_message}</span>
              {:else if result.return_code === 0}
                <span class="status-icon">✓</span>
                <span>Execution successful</span>
              {:else}
                <span class="status-icon">✗</span>
                <span>Execution failed (code {result.return_code})</span>
              {/if}
            </div>
            
            {#if result.execution_time_ms > 0}
              <div class="execution-time">
                Executed in {result.execution_time_ms}ms
              </div>
            {/if}
            
            {#if result.stdout}
              <div class="output-section">
                <h4>Output</h4>
                <pre class="output-text">{result.stdout}</pre>
              </div>
            {/if}
            
            {#if result.stderr}
              <div class="output-section error">
                <h4>Errors</h4>
                <pre class="output-text">{result.stderr}</pre>
              </div>
            {/if}
          {:else if $algorithmStore.generatedCode}
            <div class="content-placeholder">
              <p>Run your code to see results</p>
              <p class="hint">Click "Run Code" in the Code tab to execute the generated Python code.</p>
            </div>
          {:else}
            <div class="content-placeholder">
              <p>Results will appear here...</p>
              <p class="hint">Generate and run code to see execution results.</p>
            </div>
          {/if}
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
      {:else if activeTab === 'results'}
        <div class="content-placeholder">
          <p>Execution results will appear here...</p>
          <p class="hint">Run code to see stdout, stderr, and execution status.</p>
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
    background: none;
    border: none;
    cursor: pointer;
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

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-primary {
    background: var(--color-accent);
    color: var(--bg-base);
  }

  .btn-primary:hover:not(:disabled) {
    filter: brightness(1.1);
  }

  .btn-secondary {
    background: transparent;
    border: 1px solid var(--color-border);
    color: var(--color-foreground);
  }

  .btn-secondary:hover:not(:disabled) {
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

  .btn-run {
    background: var(--color-success);
  }

  .btn-run:hover:not(:disabled) {
    filter: brightness(1.1);
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

  .code-display {
    background: var(--color-surface);
    border-radius: var(--radius-lg);
    padding: var(--space-md);
    max-height: 400px;
    overflow-y: auto;
  }

  .code-display pre {
    margin: 0;
    font-family: var(--font-mono);
    font-size: 13px;
    color: var(--color-foreground);
    white-space: pre-wrap;
    word-break: break-word;
  }

  .code-actions {
    display: flex;
    gap: var(--space-md);
    margin-top: var(--space-lg);
    justify-content: center;
  }

  .error-message {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
    padding: var(--space-md);
    border-radius: var(--radius-md);
    margin-top: var(--space-md);
    font-size: 14px;
  }

  /* Results panel styles */
  .results-panel {
    min-height: 200px;
  }

  .result-status {
    display: flex;
    align-items: center;
    gap: var(--space-md);
    padding: var(--space-md) var(--space-lg);
    border-radius: var(--radius-lg);
    background: rgba(34, 197, 94, 0.1);
    color: var(--color-success);
    font-weight: 500;
    margin-bottom: var(--space-md);
  }

  .result-status.error {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
  }

  .status-icon {
    font-size: 20px;
  }

  .execution-time {
    font-size: 13px;
    color: var(--color-foreground);
    opacity: 0.6;
    margin-bottom: var(--space-lg);
  }

  .output-section {
    margin-bottom: var(--space-lg);
  }

  .output-section h4 {
    font-size: 14px;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0 0 var(--space-sm) 0;
  }

  .output-section.error h4 {
    color: #ef4444;
  }

  .output-text {
    background: var(--color-surface);
    border-radius: var(--radius-md);
    padding: var(--space-md);
    font-family: var(--font-mono);
    font-size: 13px;
    color: var(--color-foreground);
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 300px;
    overflow-y: auto;
  }
</style>
