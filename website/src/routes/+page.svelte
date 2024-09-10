<script>
	import { PUBLIC_API_URL } from "$env/static/public";

	export let data;
	console.log(data);
</script>

<img
	alt="{data.user_data.username} avatar"
	src="https://cdn.discordapp.com/avatars/{data.user_data.id}/{data.user_data.avatar}.png"
/>

<a href="{PUBLIC_API_URL}/auth/logout">LOGOUT</a>
