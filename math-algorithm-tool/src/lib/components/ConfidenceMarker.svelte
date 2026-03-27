<script lang="ts">
  import type { Confidence } from '$lib/processing';

  interface Props {
    confidence?: Confidence;
    reason?: string;
  }

  let { confidence = 'high', reason = '' }: Props = $props();
</script>

{#if confidence === 'high'}
  <!-- High confidence - no marker displayed (quiet by default) -->
{:else}
  <span 
    class="confidence-marker {confidence}" 
    title={reason}
    role="img"
    aria-label="{confidence} confidence: {reason}"
  >
    {#if confidence === 'medium'}?{/if}
    {#if confidence === 'low'}!{/if}
  </span>
{/if}

<style>
  .confidence-marker {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    font-size: 12px;
    font-weight: bold;
    cursor: help;
    flex-shrink: 0;
  }

  .high {
    background: var(--color-success);
    color: white;
  }

  .medium {
    background: var(--color-warning);
    color: black;
  }

  .low {
    background: var(--color-error);
    color: white;
  }
</style>
