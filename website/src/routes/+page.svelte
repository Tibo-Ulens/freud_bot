<script>
	export let data;
	console.log(data);
</script>

{#if data.user_data}
	<img
		alt="{data.user_data.username} avatar"
		src="https://cdn.discordapp.com/avatars/{data.user_data.id}/{data.user_data.avatar}.png"
	/>
{:else}
	<a title="Discord OAuth2" href="api/auth/login">Authenticate via Discord</a>
{/if}
