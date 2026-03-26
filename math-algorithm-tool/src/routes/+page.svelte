<script lang="ts">
  import Header from '$lib/components/Header.svelte';
  import SplitView from '$lib/components/SplitView.svelte';
  import InputPanel from '$lib/components/InputPanel.svelte';
  import OutputPanel from '$lib/components/OutputPanel.svelte';
</script>

<Header />

<SplitView>
  <InputPanel />
  <OutputPanel />
</SplitView>