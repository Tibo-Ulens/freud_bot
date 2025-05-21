<script lang="ts">
	import "../app.css";

	import { ModeWatcher } from "mode-watcher";

	import * as Sidebar from "$lib/components/ui/sidebar/index";
	import AppSidebar from "$lib/components/app-sidebar.svelte";

	import Header from "$lib/components/header.svelte";

	let { children } = $props();
</script>

<ModeWatcher />

<Sidebar.Provider class="flex flex-col flex-nowrap w-full h-full items-center content-start">
	<Header />

	<main class="max-w-screen-xl w-full h-full flex flex-col flex-nowrap items-center content-start">
		{@render children()}
	</main>

	<AppSidebar />
</Sidebar.Provider>
