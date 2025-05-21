<script lang="ts">
	import type { PageProps } from "./$types";

	import * as Card from "$lib/components/ui/card/index";
	import * as Tabs from "$lib/components/ui/tabs/index";
	import { Badge } from "$lib/components/ui/badge";
	import { Input } from "$lib/components/ui/input/index";
	import * as Select from "$lib/components/ui/select/index";
	import * as Avatar from "$lib/components/ui/avatar";
	import discord_logo from "$lib/images/discord-mark-white.svg";
	import { PUBLIC_API_URL } from "$env/static/public";
	import { Api, type ApiResponse, type GuildConfig } from "$lib/api";

	import Fieldset from "./fieldset.svelte";
	import Label from "./label.svelte";
	import Form from "./form.svelte";
	import { page } from "$app/state";

	let { data }: PageProps = $props();

	console.log(data.guild);

	let form_data = $state({
		admin_role: data.guild.admin_role,
		logging_channel: data.guild.logging_channel,
		verification_logging_channel: data.guild.verification_logging_channel,
		verified_role: data.guild.verified_role,
		confession_channel: data.guild.confession_channel,
		confession_approval_channel: data.guild.confession_approval_channel,
		pin_reaction_threshold: data.guild.pin_reaction_threshold,
		request_verification_message: data.guild.request_verification_message,
	});

	let selected = $derived({
		admin_role: data.guild.roles.find((r) => r.id === form_data.admin_role),
		logging_channel: data.guild.channels.find((c) => c.id === form_data.logging_channel),
		verification_logging_channel: data.guild.channels.find(
			(c) => c.id === form_data.verification_logging_channel,
		),
		verified_role: data.guild.roles.find((r) => r.id === form_data.verified_role),
		confession_channel: data.guild.channels.find((c) => c.id === form_data.confession_channel),
		confession_approval_channel: data.guild.channels.find(
			(c) => c.id === form_data.confession_approval_channel,
		),
		pin_reaction_threshold: form_data.pin_reaction_threshold,
		request_verification_message: form_data.request_verification_message,
	});

	let response: ApiResponse<GuildConfig> | undefined = $state();

	async function update(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
		event.preventDefault();
		const form_data = new FormData(event.currentTarget);
		const req_data = Object.fromEntries(form_data.entries());

		response = await Api.update_guild(data.guild.id, JSON.stringify(req_data), fetch, page.url);
	}
</script>

{#snippet role_select()}
	<Select.Content>
		{#each data.guild.roles as role (role.id)}
			<Select.Item
				value={role.id}
				label={role.name}
				class="my-1"
				style="border-left: 4px solid #{role.color}"
			/>
		{/each}
	</Select.Content>
{/snippet}

{#snippet channel_select()}
	<Select.Content>
		{#each data.guild.channels as channel (channel.id)}
			<Select.Item value={channel.id} label={channel.name} class="my-1" />
		{/each}
	</Select.Content>
{/snippet}

<Card.Root class="m-0 px-0 md:m-4 md:px-12 flex flex-col flex-nowrap">
	<Card.Header style="container-type: normal">
		<Card.Title
			class="font-normal text-2xl text-center flex flex-row flex-wrap gap-2 justify-center items-center"
		>
			Configuring

			<Badge
				variant="outline"
				class="px-2 md:px-4 py-2 font-normal text-xl border-2 rounded-lg
					flex flex-row flex-nowrap justify-start items-center"
			>
				<Avatar.Root class="mr-4 size-14">
					<Avatar.Image src={data.guild.icon_url} alt="{data.guild.name} avatar" />

					<Avatar.Fallback>
						<img
							src={discord_logo}
							alt="Discord logo"
							class="size-14 p-2 rounded-lg bg-[#5865f2]"
						/>
					</Avatar.Fallback>
				</Avatar.Root>

				<span class="text-wrap">
					{data.guild.name}
				</span>
			</Badge>
		</Card.Title>
	</Card.Header>

	<Card.Content class="p-0">
		<Tabs.Root class="w-full md:w-full shadow-sm" value="General">
			<Tabs.List class="flex flex-row flex-wrap h-full">
				<Tabs.Trigger class="flex-0 text-lg" value="General">General</Tabs.Trigger>
				<Tabs.Trigger class="flex-0 text-lg" value="Verification">Verification</Tabs.Trigger>
				<Tabs.Trigger class="flex-0 text-lg" value="Confessions">Confessions</Tabs.Trigger>
				<Tabs.Trigger class="flex-0 text-lg" value="Messages">Messages</Tabs.Trigger>
				<Tabs.Trigger class="flex-0 text-lg" value="Utilities">Utilities</Tabs.Trigger>
			</Tabs.List>

			<Tabs.Content value="General">
				<Form action="{PUBLIC_API_URL}/config/{data.guild.id}" onsubmit={update}>
					<Fieldset legend="General">
						<Label target="admin_role">Admin Role</Label>
						<Select.Root type="single" bind:value={form_data.admin_role} name="admin_role">
							<Select.Trigger style="border: 2px solid #{selected.admin_role?.color}">
								{selected.admin_role?.name ?? "Select the admin role"}
							</Select.Trigger>

							{@render role_select()}
						</Select.Root>

						<Label target="logging_channel">Logging Channel</Label>
						<Select.Root
							type="single"
							bind:value={form_data.logging_channel}
							name="logging_channel"
						>
							<Select.Trigger>
								{selected.logging_channel?.name ?? "Select the logging channel"}
							</Select.Trigger>

							{@render channel_select()}
						</Select.Root>

						<Label target="verification_logging_channel">Verification Logging Channel</Label>
						<Select.Root
							type="single"
							bind:value={form_data.verification_logging_channel}
							name="verification_logging_channel"
						>
							<Select.Trigger>
								{selected.verification_logging_channel?.name ??
									"Select the verification logging channel"}
							</Select.Trigger>

							{@render channel_select()}
						</Select.Root>
					</Fieldset>
				</Form>
			</Tabs.Content>

			<Tabs.Content value="Verification">
				<Form action="{PUBLIC_API_URL}/config/{data.guild.id}" onsubmit={update}>
					<Fieldset legend="Verification">
						<Label target="verified_role">Verified Role</Label>
						<Select.Root type="single" bind:value={form_data.verified_role} name="verified_role">
							<Select.Trigger style="border: 2px solid #{selected.verified_role?.color}">
								{selected.verified_role?.name ?? "Select the verified role"}
							</Select.Trigger>

							{@render role_select()}
						</Select.Root>
					</Fieldset>
				</Form>
			</Tabs.Content>

			<Tabs.Content value="Confessions">
				<Form action="{PUBLIC_API_URL}/config/{data.guild.id}" onsubmit={update}>
					<Fieldset legend="Confessions">
						<Label target="confession_channel">Confession Channel</Label>
						<Select.Root
							type="single"
							bind:value={form_data.confession_channel}
							name="confession_channel"
						>
							<Select.Trigger>
								{selected.confession_channel?.name ?? "Select the confession channel"}
							</Select.Trigger>

							{@render channel_select()}
						</Select.Root>

						<Label target="confession_approval_channel">Confession Approval Channel</Label>
						<Select.Root
							type="single"
							bind:value={form_data.confession_approval_channel}
							name="confession_approval_channel"
						>
							<Select.Trigger>
								{selected.confession_approval_channel?.name ??
									"Select the confession approval channel"}
							</Select.Trigger>

							{@render channel_select()}
						</Select.Root>
					</Fieldset>
				</Form>
			</Tabs.Content>

			<Tabs.Content value="Messages">
				<Form action="{PUBLIC_API_URL}/config/{data.guild.id}" onsubmit={update}>
					<Fieldset legend="Messages">
						<Label target="request_verification_message">Verification Request Message</Label>

						<textarea
							name="request_verification_message"
							id="request_verification_message"
							value={selected.request_verification_message}
							class="w-full min-h-12 shadow-sm p-1 bg-accent"
						></textarea>
					</Fieldset>
				</Form>
			</Tabs.Content>

			<Tabs.Content class="shrink-0" value="Utilities">
				<Form action="{PUBLIC_API_URL}/config/{data.guild.id}" onsubmit={update}>
					<Fieldset legend="Utilities">
						<Label target="pin_reaction_threshold">Pin Reaction Threshold</Label>
						<Input
							type="number"
							name="pin_reaction_threshold"
							id="pin_reaction_threshold"
							value={selected.pin_reaction_threshold}
						/>
					</Fieldset>
				</Form>
			</Tabs.Content>
		</Tabs.Root>
	</Card.Content>
</Card.Root>
