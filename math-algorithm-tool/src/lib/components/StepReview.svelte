<script lang="ts">
  import type { AlgorithmStep } from '$lib/processing';
  import ConfidenceMarker from './ConfidenceMarker.svelte';

  interface Props {
    steps?: AlgorithmStep[];
  }

  let { steps = [] }: Props = $props();
</script>

<section class="step-review">
  {#if steps.length === 0}
    <div class="empty-state">
      <p>No steps extracted yet</p>
      <p class="hint">Process an algorithm description to see the extracted steps.</p>
    </div>
  {:else}
    <div class="steps-list">
      {#each steps as step (step.stepNumber)}
        <article class="step">
          <header class="step-header">
            <span class="step-number">{step.stepNumber}.</span>
            <ConfidenceMarker 
              confidence={step.confidence} 
              reason={step.confidenceReason ?? ''} 
            />
          </header>
          
          <div class="step-content">
            <p class="description">{step.description}</p>
            
            <code class="code-equivalent">{step.codeEquivalent}</code>
            
            {#if step.variables && step.variables.length > 0}
              <div class="variables">
                <span class="variables-label">Variables:</span>
                {#each step.variables as variable}
                  <span class="variable">
                    <code>{variable.name}</code>: {variable.type}
                  </span>
                {/each}
              </div>
            {/if}
            
            {#if step.controlFlow}
              <span class="control-flow-badge">{step.controlFlow}</span>
            {/if}
          </div>
        </article>
      {/each}
    </div>
  {/if}
</section>

<style>
  .step-review {
    padding: var(--space-lg);
  }

  .empty-state {
    background: var(--color-surface);
    border-radius: var(--radius-lg);
    padding: var(--space-xl);
    text-align: center;
  }

  .empty-state p {
    color: var(--color-foreground);
    opacity: 0.8;
    margin: 0;
  }

  .empty-state .hint {
    font-size: 14px;
    opacity: 0.5;
    margin-top: var(--space-sm);
  }

  .steps-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-lg);
  }

  .step {
    background: var(--color-surface);
    border-radius: var(--radius-lg);
    padding: var(--space-lg);
    border-left: 3px solid var(--color-accent);
  }

  .step-header {
    display: flex;
    align-items: center;
    gap: var(--space-sm);
    margin-bottom: var(--space-md);
  }

  .step-number {
    font-size: 18px;
    font-weight: 700;
    color: var(--color-foreground);
  }

  .step-content {
    display: flex;
    flex-direction: column;
    gap: var(--space-md);
  }

  .description {
    font-size: 15px;
    line-height: 1.6;
    color: var(--color-foreground);
    margin: 0;
  }

  .code-equivalent {
    display: block;
    background: var(--bg-base);
    padding: var(--space-md);
    border-radius: var(--radius-md);
    font-family: var(--font-mono);
    font-size: 13px;
    color: var(--color-foreground);
    opacity: 0.7;
    overflow-x: auto;
  }

  .variables {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-sm);
    align-items: center;
  }

  .variables-label {
    font-size: 13px;
    font-weight: 600;
    color: var(--color-foreground);
    opacity: 0.7;
  }

  .variable {
    font-size: 13px;
    color: var(--color-foreground);
    background: var(--bg-base);
    padding: var(--space-xs) var(--space-sm);
    border-radius: var(--radius-md);
  }

  .variable code {
    font-family: var(--font-mono);
    font-size: 12px;
    color: var(--color-accent);
  }

  .control-flow-badge {
    display: inline-block;
    font-size: 12px;
    font-weight: 500;
    padding: var(--space-xs) var(--space-sm);
    background: var(--color-accent);
    color: white;
    border-radius: var(--radius-sm);
    text-transform: capitalize;
    width: fit-content;
  }
</style>
