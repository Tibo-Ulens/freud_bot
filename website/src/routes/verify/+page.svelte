<script lang="ts">
	import type { PageProps } from "./$types";

	import { PUBLIC_API_URL } from "$env/static/public";
	import { page } from "$app/state";

	import * as Card from "$lib/components/ui/card";
	import { Input } from "$lib/components/ui/input/index";
	import { Button } from "$lib/components/ui/button/index";
	import { Badge } from "$lib/components/ui/badge";
	import * as Avatar from "$lib/components/ui/avatar";
	import { Api, type ApiResponse } from "$lib/api";
	import X from "@lucide/svelte/icons/x";

	let { data }: PageProps = $props();

	let response: ApiResponse<null> | undefined = $state();

	async function verify(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
		event.preventDefault();
		const form_data = new FormData(event.currentTarget);
		const data = Object.fromEntries(form_data.entries());

		response = await Api.request_verify(fetch, JSON.stringify(data), page.url);
	}
</script>

<Card.Root class="m-4 px-12">
	{#if data.verified}
		<Card.Content class="flex flex-row items-center justify-center">
			<X class="mr-4 text-red-500 stroke-3 size-8" />
			You are already verified
		</Card.Content>
	{:else}
		<Card.Header>
			<Card.Title class="font-normal text-2xl text-center">
				Verify your email for the account
				<Badge
					variant="outline"
					class="ml-2 px-4 py-2 font-normal text-2xl border-2 rounded-3xl"
				>
					{data.userdata.username}

					<Avatar.Root class="ml-4 size-14">
						<Avatar.Image
							src="https://cdn.discordapp.com/avatars/{data.userdata.id}/{data
								.userdata.avatar}.png"
							alt="{data.userdata.username} avatar"
						/>
					</Avatar.Root>
				</Badge>
			</Card.Title>
		</Card.Header>

		<Card.Content>
			<form
				method="POST"
				action="{PUBLIC_API_URL}/verify/request"
				onsubmit={verify}
				class="flex flex-col content-start items-center"
			>
				<Input type="email" name="email" id="email" placeholder="bob@ugent.be" />

				<Button
					type="submit"
					class="w-32 p-4 my-4 hover:cursor-pointer uppercase tracking-[1px]"
				>
					Send Email
				</Button>
			</form>
		</Card.Content>

		<Card.Footer class="flex flex-row justify-center text-center">
			{#if response?.tag === "ok"}
				An email has been sent, make sure to check your spam
				<br />
				It could take a few minutes for the email to arrive
			{:else if response?.tag === "err"}
				<X class="mr-4 text-red-500 stroke-3 size-8" />

				{#if response.info === "discord_id"}
					That profile is already verified
				{:else if response.info === "email"}
					That email is already in use
				{/if}
			{/if}
		</Card.Footer>
	{/if}
</Card.Root>
