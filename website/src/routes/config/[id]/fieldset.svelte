<script lang="ts">
	let { children, legend } = $props();
</script>

<fieldset class="flex flex-col flex-nowrap justify-center items-start my-2">
	<legend class="pb-2 my-4 border-b-2 text-center w-full border-primary">
		{legend}
	</legend>

	{@render children()}
</fieldset>
