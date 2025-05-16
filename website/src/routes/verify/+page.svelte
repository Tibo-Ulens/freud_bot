<script lang="ts">
	import type { PageProps } from "./$types";

	import { PUBLIC_API_URL } from "$env/static/public";

	import * as Card from "$lib/components/ui/card";
	import { Input } from "$lib/components/ui/input/index";
	import { Button } from "$lib/components/ui/button/index";
	import { Badge } from "$lib/components/ui/badge";
	import * as Avatar from "$lib/components/ui/avatar";

	let { data }: PageProps = $props();

	let verify_state = $state("");
	let error_message = $state("");

	async function verify(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
		event.preventDefault();
		const form_data = new FormData(event.currentTarget);
		const data = Object.fromEntries(form_data.entries());

		const response = await fetch(event.currentTarget.action, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify(data),
		});

		if (response.status === 204) {
			verify_state = "success";
		} else {
			verify_state = "failure";
			error_message = await response.text();
		}

		console.log(verify_state);
		console.log(error_message);
	}
</script>

<Card.Root class="m-4 px-12">
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
						src="https://cdn.discordapp.com/avatars/{data.userdata.id}/{data.userdata
							.avatar}.png"
						alt="{data.userdata.username} avatar"
					/>
					<Avatar.Fallback>
						{data.userdata.username} avatar
					</Avatar.Fallback>
				</Avatar.Root>
			</Badge>
		</Card.Title>
	</Card.Header>

	<Card.Content>
		<form
			method="POST"
			action="{PUBLIC_API_URL}/request_verify"
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

	<Card.Footer class="justify-center text-center">
		{#if verify_state === "success"}
			An email has been sent, make sure to check your spam
			<br />
			It could take a few minutes for the email to arrive
		{:else if verify_state === "failure"}
			{error_message}
		{/if}
	</Card.Footer>
</Card.Root>
