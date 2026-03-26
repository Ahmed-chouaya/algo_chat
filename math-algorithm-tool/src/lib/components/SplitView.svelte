<script lang="ts">
  import type { Snippet } from 'svelte';
  
  interface Props {
    children: Snippet;
  }
  
  let { children }: Props = $props();
</script>

<div class="split-view">
  {@render children()}
</div>

<style>
  .split-view {
    display: grid;
    grid-template-columns: 40fr 60fr;
    height: calc(100vh - 56px);
    width: 100%;
    overflow: hidden;
  }
  
  @media (max-width: 1024px) {
    .split-view {
      grid-template-columns: 1fr;
      grid-template-rows: 1fr 1fr;
    }
  }
  
  @media (max-width: 768px) {
    .split-view {
      grid-template-rows: 1fr;
    }
  }
</style>