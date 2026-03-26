<script lang="ts">
  let algorithmInput = $state('');
  
  function handleSubmit() {
    // TODO: Connect to backend processing
    console.log('Submitting algorithm:', algorithmInput);
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
    <button class="btn btn-outline">Import PDF</button>
    <button class="btn btn-outline">Import Text</button>
  </div>
  
  <button class="btn btn-submit" onclick={handleSubmit}>
    Process Algorithm
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
</style>