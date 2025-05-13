<script lang="ts">
	import "../lib.scss";

	import { page } from "$app/state";

	let { children } = $props();
</script>

<nav>
	<div id="nav-inner">
		<a class:active={page.url.pathname === "/"} href="/">Home</a>
		<a class:active={page.url.pathname === "/verify"} href="/verify">Verify</a>
		<a class:active={page.url.pathname === "/config"} href="/config">Config</a>
		<a class:active={page.url.pathname === "/logout"} href="/logout">Logout</a>
	</div>
</nav>

{@render children()}

<style lang="scss">
	@use "../colors.scss";

	nav {
		position: sticky;
		top: 0;
		width: 100%;
		background-color: colors.$dark1;
		display: flex;
		flex-flow: row nowrap;
		justify-content: flex-start;
		align-items: center;
		z-index: 1000;

		// Disable scrollbar but keep functionality
		&::-webkit-scrollbar {
			display: none; // Chrome
		}

		-ms-overflow-style: none; // Edge + IE
		scrollbar-width: none; // Firefox

		#nav-inner {
			background-color: colors.$dark1;
			width: 100%;
			flex: 0 1 auto;
			display: flex;
			flex-flow: row nowrap;
			justify-content: flex-start;
			align-items: center;

			a {
				padding: 1rem;
				flex: 0 1 auto;

				font-weight: 500;
				font-size: 1rem;
				letter-spacing: 1px;
				line-height: 1rem;
				text-transform: uppercase;
				text-align: start;
				text-decoration: none;
				border: 0;
				outline: 0;
				color: colors.$foreground;

				&:hover {
					cursor: pointer;
					background-color: colors.$dark3;
				}

				&.active {
					border-bottom: 1px solid colors.$primary;
				}

				&:last-child {
					margin-left: auto;
				}

				&:focus {
					box-shadow:
						0 0 0 0.2rem colors.$dark1,
						0 0 0 0.3rem colors.$light-blue;
				}
			}
		}
	}
</style>
