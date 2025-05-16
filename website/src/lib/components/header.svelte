<script lang="ts">
	import { page } from "$app/state";

	import Menu from "@lucide/svelte/icons/menu";

	import { useSidebar } from "$lib/components/ui/sidebar/index";
	import ThemeSwitcher from "$lib/components/theme-switcher.svelte";

	import freud from "$lib/images/freud.png";
	import Github from "$lib/components/icons/github.svelte";

	const sidebar = useSidebar();
</script>

<header
	class="sticky top-0 z-50 w-full border-b border-border flex flex-row flex-nowrap justify-center"
>
	<div class="flex px-2 md:px-4 h-14 w-full max-w-screen-xl items-center content-center">
		<div class="hidden md:flex h-full">
			<span class="mr-6 flex items-center space-x-2">
				<img src={freud} alt="Freud" class="size-12 rounded-full" />
				<span class="hidden font-bold xl:inline-block">FreudBot</span>
			</span>
			<nav class="flex items-center content-center">
				<a
					class="focus-visible:ring-ring focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 rounded-md hover:text-foreground hover:bg-accent text-foreground/80 h-full px-2 content-center"
					class:active={page.url.pathname === "/"}
					href="/">Home</a
				>
				<a
					class="focus-visible:ring-ring focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 rounded-md hover:text-foreground hover:bg-accent text-foreground/80 h-full px-2 content-center"
					class:active={page.url.pathname === "/verify"}
					href="/verify">Verify</a
				>
				<a
					class="focus-visible:ring-ring focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 rounded-md hover:text-foreground hover:bg-accent text-foreground/80 h-full px-2 content-center"
					class:active={page.url.pathname === "/config"}
					href="/config">Config</a
				>
			</nav>
		</div>

		<button
			onclick={() => sidebar.toggle()}
			class="md:hidden inline-flex items-center justify-center mr-auto
			disabled:pointer-events-none hover:cursor-pointer p-2"
		>
			<Menu />
		</button>

		<div class="flex flex-1 h-full items-center justify-end">
			<a
				class="focus-visible:ring-ring focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 rounded-md hidden md:inline hover:text-foreground hover:bg-accent text-foreground/80 h-full px-2 content-center"
				href="/auth/logout">Logout</a
			>

			<Github />

			<ThemeSwitcher />
		</div>
	</div>
</header>

<style>
	nav {
		-ms-overflow-style: none;
	}

	nav::-webkit-scrollbar {
		display: none;
	}

	nav > a.active {
		border-bottom: 2px solid var(--color-primary);
	}
</style>
