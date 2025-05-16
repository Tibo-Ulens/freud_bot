<script lang="ts">
	import type { PageProps } from "./$types";

	let { data }: PageProps = $props();
	console.log(data);
</script>

<img
	alt="{data.user_data.username} avatar"
	src="https://cdn.discordapp.com/avatars/{data.user_data.id}/{data.user_data.avatar}.png"
/>
