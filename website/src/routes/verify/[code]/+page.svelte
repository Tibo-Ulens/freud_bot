<script lang="ts">
	import type { PageProps } from "./$types";

	import Check from "@lucide/svelte/icons/check";
	import X from "@lucide/svelte/icons/x";
	import * as Card from "$lib/components/ui/card";
	import { Separator } from "$lib/components/ui/separator/index";
	import { Button } from "$lib/components/ui/button/index";
	import { Badge } from "$lib/components/ui/badge";
	import * as Avatar from "$lib/components/ui/avatar";

	let { data }: PageProps = $props();
</script>

{#if data.code_response.tag === "ok"}
	<Card.Root class="mt-4">
		<Card.Content class="flex flex-row items-center justify-center">
			<Check class="mr-4 text-green-500 stroke-3 size-8" />
			You have verified successfully
		</Card.Content>
	</Card.Root>
{:else if data.code_response.tag === "err"}
	<Card.Root class="mt-4 flex flex-col">
		<Card.Content class="flex flex-row items-center justify-center">
			<X class="mr-4 text-red-500 stroke-3 size-8" />
			Something went wrong
		</Card.Content>

		<Separator />

		<Card.Footer class="flex flex-col items-center justify-center p-6">
			{#if data.code_response.code === 8}
				<div class="flex flex-row items-center justify-center">
					<Badge variant="outline" class="mr-2 px-2 py-1 font-normal text-md border-2 rounded-3xl">
						{data.userdata.username}

						<Avatar.Root class="ml-2 size-8">
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

					has not yet requested a confirmation code
				</div>

				<div>
					Go
					<Button variant="link" href="/verify" class="inline p-0 text-base">here</Button>
					to request one
				</div>
			{:else if data.code_response.code === 10}
				<div class="flex flex-row items-center justify-center">
					This confirmation code is not valid for

					<Badge variant="outline" class="ml-2 px-2 py-1 font-normal text-md border-2 rounded-3xl">
						{data.userdata.username}

						<Avatar.Root class="ml-2 size-8">
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
				</div>
			{:else}
				{data.code_response.text}
			{/if}
		</Card.Footer>
	</Card.Root>
{/if}
