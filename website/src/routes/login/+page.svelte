<script lang="ts">
	import { Button } from "$lib/components/ui/button/index";

	import { PUBLIC_API_URL } from "$env/static/public";
	import discord_logo from "$lib/images/discord-mark-white.svg";
	import { page } from "$app/state";

	const redirect_url = page.url.searchParams.get("redirect");
	const auth_url = redirect_url
		? `${PUBLIC_API_URL}/auth/login?redirect=${redirect_url}`
		: `${PUBLIC_API_URL}/auth/login`;
</script>

<Button
	variant="outline"
	href={auth_url}
	class="flex flex-row flex-wrap content-around items-center h-auto
	mx-4 py-1 px-2 md:px-8 mt-32 text-[2rem] border-2"
>
	Log in with Discord

	<img src={discord_logo} alt="Discord logo" class="size-20 m-1 md:m-4 p-2 rounded-lg bg-[#5865f2]" />
</Button>
