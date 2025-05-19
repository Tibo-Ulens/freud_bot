<script lang="ts">
	import type { PageProps } from "./$types";

	import * as Card from "$lib/components/ui/card/index";
	import { badgeVariants } from "$lib/components/ui/badge";
	import * as Avatar from "$lib/components/ui/avatar";
	import { cn } from "$lib/utils";

	let { data }: PageProps = $props();
</script>

{#if data.guilds.length === 0}
	No Guilds Found
{:else}
	<Card.Root class="m-1 px-1 md:m-4 md:px-12">
		<Card.Header>
			<Card.Title class="font-normal text-2xl text-center">
				Pick a server to configure
			</Card.Title>
		</Card.Header>

		<Card.Content class="flex flex-col flex-nowrap gap-4 px-2 md:px-6">
			{#each data.guilds as guild (guild.id)}
				<a
					href="/config/{guild.id}"
					class={cn(
						badgeVariants({ variant: "outline" }),
						"px-2 md:px-4 py-2 font-normal text-xl border-2 rounded-lg \
						w-full flex flex-row flex-nowrap justify-start items-center \
						focus-visible:ring-ring focus-visible:outline-none focus-visible:ring-2",
					)}
				>
					<Avatar.Root class="mr-4 size-14">
						<Avatar.Image src={guild.icon_url} alt="{guild.name} avatar" />
					</Avatar.Root>

					<span class="text-wrap">
						{guild.name}
					</span>
				</a>
			{/each}
		</Card.Content>
	</Card.Root>
{/if}
