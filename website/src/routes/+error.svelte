<script>
	import { page } from "$app/stores";
	import { redirect } from "@sveltejs/kit";
</script>

<h1>{$page.status}: {$page.error?.message}</h1>
