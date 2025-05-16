<script lang="ts">
	import { PUBLIC_API_URL } from "$env/static/public";
	import * as Sidebar from "$lib/components/ui/sidebar/index";

	import freud from "$lib/images/freud.png";

	const routes = [
		{
			name: "Home",
			href: "/",
		},
		{
			name: "Verify",
			href: "/verify",
		},
		{
			name: "Config",
			href: "/config",
		},
	];
</script>

<Sidebar.Root variant="floating">
	<Sidebar.Header>
		<span class="mr-6 flex items-center space-x-2">
			<img src={freud} alt="Freud" class="size-12 rounded-full" />
			<span class="font-bold">FreudBot</span>
		</span>
	</Sidebar.Header>

	<Sidebar.Separator class="border-b-2 border-sidebar-border m-0" />

	<Sidebar.Content>
		<Sidebar.Group>
			<Sidebar.Menu>
				{#each routes as route (route.href)}
					<Sidebar.MenuItem>
						<Sidebar.MenuButton>
							{#snippet child({ props })}
								<a
									{...props}
									class="
										hover:bg-accent text-foreground/80 h-8 p-6 content-center
										flex w-full items-center overflow-hidden rounded-none
									"
									href={route.href}
								>
									{route.name}
								</a>
							{/snippet}
						</Sidebar.MenuButton>
					</Sidebar.MenuItem>
				{/each}
			</Sidebar.Menu>
		</Sidebar.Group>

		<Sidebar.Group class="flex flex-1 justify-end">
			<Sidebar.MenuItem>
				<Sidebar.MenuButton>
					{#snippet child({ props })}
						<a
							{...props}
							class="
								hover:bg-accent text-foreground/80 h-8 p-6 content-center
								flex w-full items-center overflow-hidden rounded-none
							"
							href="{PUBLIC_API_URL}/auth/logout"
						>
							Logout
						</a>
					{/snippet}
				</Sidebar.MenuButton>
			</Sidebar.MenuItem>
		</Sidebar.Group>
	</Sidebar.Content>
</Sidebar.Root>
