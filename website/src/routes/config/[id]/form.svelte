<script lang="ts">
	import FormButton from "$lib/components/ui/form/form-button.svelte";

	let { children, action, onsubmit } = $props();
</script>

<form {action} method="POST" {onsubmit} class="p-4 flex flex-col flex-nowrap">
	{@render children()}

	<FormButton>Save</FormButton>
</form>
