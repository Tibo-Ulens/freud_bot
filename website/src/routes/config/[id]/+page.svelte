<script lang="ts">
	import type { PageProps } from "./$types";

	import * as Card from "$lib/components/ui/card/index";
	import { Badge } from "$lib/components/ui/badge";
	import * as Avatar from "$lib/components/ui/avatar";

	let { data }: PageProps = $props();

	console.log(data.guild);
</script>

<Card.Root class="m-1 px-1 md:m-4 md:px-12">
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
				{#if data.guild.icon_url}
					<Avatar.Root class="mr-4 size-14">
						<Avatar.Image src={data.guild.icon_url} alt="{data.guild.name} avatar" />
					</Avatar.Root>
				{/if}

				<span class="text-wrap">
					{data.guild.name}
				</span>
			</Badge>
		</Card.Title>
	</Card.Header>

	<Card.Content>foo</Card.Content>
</Card.Root>
