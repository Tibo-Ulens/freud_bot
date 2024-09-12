<script lang="ts">
	import { PUBLIC_API_URL } from "$env/static/public";
	import discord_logo from "$lib/images/discord-mark-white.svg";
</script>

<a href="{PUBLIC_API_URL}/auth/login">
	login with discord

	<img src={discord_logo} alt="Discord logo" />
</a>

<style lang="scss">
	@import "../../lib/scss/variables.scss";

	a {
		margin-top: 8rem;
		text-decoration: none;
		font-size: 2rem;
		background-color: lighten($background, 3);
		color: $foreground;

		padding: 1rem 2rem;
		border-radius: 8px;

		display: flex;
		flex-flow: row;
		justify-content: space-around;
		align-items: center;

		&:hover {
			background-color: lighten($background, 5);
		}

		img {
			width: 5rem;
			height: 5rem;
			margin: 1rem 1rem 1rem 2rem;
			padding: 0.5rem;
			border-radius: 8px;
			background-color: #5865f2;
		}
	}
</style>
