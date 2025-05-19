<script lang="ts">
	import type { PageProps } from "./$types";

	let { data }: PageProps = $props();

	console.log(data.guilds);
</script>

{#if data.guilds.length === 0}
	No Guilds Found
{:else}
	{#each data.guilds as guild (guild.id)}
		{guild.name}
	{/each}
{/if}
