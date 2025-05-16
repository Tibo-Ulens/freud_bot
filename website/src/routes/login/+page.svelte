<script lang="ts">
	import { Button } from "$lib/components/ui/button/index";

	import { PUBLIC_API_URL } from "$env/static/public";
	import discord_logo from "$lib/images/discord-mark-white.svg";
</script>

<Button
	variant="outline"
	href="{PUBLIC_API_URL}/auth/login"
	class="flex flex-row content-around items-center h-auto
	pt-4 pb-4 pl-8 pr-8 mt-32 text-[2rem] border-2"
>
	Log in with Discord

	<img src={discord_logo} alt="Discord logo" class="w-20 h-20 m-4 p-2 rounded-lg bg-[#5865f2]" />
</Button>
