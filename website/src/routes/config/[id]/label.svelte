<script lang="ts">
	import { Label } from "$lib/components/ui/label";

	let { children, target } = $props();
</script>

<Label for={target} class="mt-4 mb-2 text-sm text-wrap">
	{@render children()}
</Label>
