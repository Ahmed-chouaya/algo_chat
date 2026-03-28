<script lang="ts">
  import { processAlgorithmInput, importFile } from '$lib/processing';
  import { processedInput, isProcessing, processingError } from '$lib/stores/processing';
  import { open } from '@tauri-apps/plugin-dialog';
  
  let algorithmInput = $state('');
  
  async function handleSubmit() {
    if (!algorithmInput.trim()) {
      return;
    }
    
    $isProcessing = true;
    $processingError = null;
    
    try {
      const result = await processAlgorithmInput(algorithmInput);
      $processedInput = result;
    } catch (error) {
      console.error('Processing error:', error);
      $processingError = error instanceof Error ? error.message : 'Failed to process algorithm';
    } finally {
      $isProcessing = false;
    }
  }
  
  async function handleImportPdf() {
    try {
      const selected = await open({
        multiple: false,
        filters: [{ name: 'PDF', extensions: ['pdf'] }]
      });
      
      if (selected) {
        $isProcessing = true;
        $processingError = null;
        
        const result = await importFile(selected as string);
        
        if (result.success) {
          algorithmInput = result.content;
        } else {
          $processingError = result.error || 'Failed to import PDF';
        }
      }
    } catch (error) {
      console.error('Import error:', error);
      $processingError = error instanceof Error ? error.message : 'Failed to import PDF';
    } finally {
      $isProcessing = false;
    }
  }
  
  async function handleImportText() {
    try {
      const selected = await open({
        multiple: false,
        filters: [{ name: 'Text', extensions: ['txt', 'md'] }]
      });
      
      if (selected) {
        $isProcessing = true;
        $processingError = null;
        
        const result = await importFile(selected as string);
        
        if (result.success) {
          algorithmInput = result.content;
        } else {
          $processingError = result.error || 'Failed to import file';
        }
      }
    } catch (error) {
      console.error('Import error:', error);
      $processingError = error instanceof Error ? error.message : 'Failed to import file';
    } finally {
      $isProcessing = false;
    }
  }
</script>

<aside class="input-panel">
  <div class="textarea-container">
    <textarea 
      class="algorithm-input"
      placeholder="Paste your algorithm description here..."
      bind:value={algorithmInput}
    ></textarea>
  </div>
  
  <div class="import-buttons">
    <button class="btn btn-outline" onclick={handleImportPdf}>Import PDF</button>
    <button class="btn btn-outline" onclick={handleImportText}>Import Text</button>
  </div>
  
  {#if $processingError}
    <div class="error-message">{$processingError}</div>
  {/if}
  
  <button class="btn btn-submit" onclick={handleSubmit} disabled={$isProcessing}>
    {#if $isProcessing}
      Processing...
    {:else}
      Process Algorithm
    {/if}
  </button>
</aside>

<style>
  .input-panel {
    background: var(--color-surface);
    padding: var(--space-lg);
    border-right: 1px solid var(--color-border);
    display: flex;
    flex-direction: column;
    gap: var(--space-md);
    min-width: 320px;
  }
  
  .textarea-container {
    flex: 1;
    min-height: 200px;
  }
  
  .algorithm-input {
    width: 100%;
    height: 100%;
    min-height: 200px;
    background: var(--bg-base);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--space-lg);
    font-family: var(--font-body);
    font-size: 18px;
    color: var(--color-foreground);
    resize: vertical;
    transition: var(--transition);
  }
  
  .algorithm-input::placeholder {
    color: var(--color-foreground);
    opacity: 0.5;
  }
  
  .algorithm-input:focus {
    outline: none;
    border-color: var(--color-accent);
  }
  
  .import-buttons {
    display: flex;
    gap: var(--space-sm);
  }
  
  .btn {
    font-family: var(--font-body);
    font-weight: 500;
    font-size: 14px;
    padding: 12px 20px;
    border-radius: var(--radius-full);
    transition: var(--transition);
  }
  
  .btn-outline {
    background: transparent;
    border: 1px solid var(--color-border);
    color: var(--color-foreground);
  }
  
  .btn-outline:hover {
    border-color: var(--color-accent);
    color: var(--color-accent);
  }
  
  .btn-submit {
    background: var(--color-accent);
    color: var(--bg-base);
    font-weight: 600;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    height: 48px;
    width: 100%;
  }
  
  .btn-submit:hover {
    filter: brightness(1.1);
  }
  
  .btn-submit:active {
    transform: scale(0.98);
  }
  
  .btn-submit:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
  
  .error-message {
    color: #ef4444;
    font-size: 14px;
    padding: var(--space-sm);
    background: rgba(239, 68, 68, 0.1);
    border-radius: var(--radius-md);
  }
</style>