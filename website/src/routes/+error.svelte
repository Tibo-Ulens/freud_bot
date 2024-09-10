<script>
	import { page } from "$app/stores";
	import { PUBLIC_API_URL } from "$env/static/public";
</script>

<h1>{$page.status}: {$page.error?.message}</h1>

{#if $page.status === 401}
	<a title="Discord OAuth2" href="{PUBLIC_API_URL}/auth/login">Authenticate via Discord</a>
{/if}
