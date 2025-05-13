<script lang="ts">
	import type { PageProps } from "./$types";

	import { PUBLIC_API_URL } from "$env/static/public";

	let { data }: PageProps = $props();

	let verify_state = $state("");
	let error_message = $state("");

	async function verify(event: SubmitEvent & { currentTarget: EventTarget & HTMLFormElement }) {
		event.preventDefault();
		const form_data = new FormData(event.currentTarget);
		const data = Object.fromEntries(form_data.entries());

		const response = await fetch(event.currentTarget.action, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify(data),
		});

		if (response.status === 204) {
			verify_state = "success";
		} else {
			verify_state = "failure";
			error_message = await response.text();
		}

		console.log(verify_state);
		console.log(error_message);
	}
</script>

<form method="POST" action="{PUBLIC_API_URL}/request_verify" onsubmit={verify}>
	<fieldset>
		<legend>Verify your email for the account {data.user_data.username}</legend>

		<input type="email" name="email" id="email" placeholder="bob@ugent.be" />
	</fieldset>

	<input type="submit" value="Send Email" />
</form>

<div id="status-message">
	{#if verify_state === "success"}
		An email has been sent, make sure to check your spam
	{:else if verify_state === "failure"}
		{error_message}
	{/if}
</div>

<style lang="scss">
	@use "sass:color";
	@use "../../colors.scss";

	form {
		display: flex;
		flex-flow: column;
		justify-content: flex-start;

		background-color: colors.$dark1;
		padding: 1rem 3rem;
		margin: 1rem;

		fieldset {
			border: none;
			margin: 0;
			padding: 0;
			display: flex;
			flex-flow: column nowrap;

			legend {
				padding: 0 0.5rem;
				margin: 0 auto 1rem auto;
				font-size: 1.5rem;
			}

			input {
				background: transparent;
				color: colors.$foreground;
				border: 0;
				outline: 0;
				border-radius: 8px 8px 0 0;
				border-bottom: 1px solid colors.$primary;
				font-size: 1rem;
				letter-spacing: 0.25px;
				padding: 0.5rem;
				margin: 1rem 0 2rem 0;
				flex: 0 1 100%;

				&:last-child {
					margin-bottom: 1rem;
				}
			}
		}

		input[type="submit"] {
			min-width: 9rem;
			padding: 0.75rem 1.5rem;
			font-size: 1.125rem;
			text-transform: uppercase;
			letter-spacing: 1px;
			line-height: 1rem;
			outline: 0;
			margin: 1rem;
			transition: all 0.25s;
			flex: 0 1 auto;
			text-align: center;

			border: 1px solid colors.$primary;
			background-color: transparent;
			color: colors.$foreground;

			&:hover {
				cursor: pointer;
				background-color: color.adjust(colors.$background, $lightness: 5%);
			}

			&:focus {
				box-shadow:
					0 0 0 0.2rem colors.$dark1,
					0 0 0 0.25rem colors.$light-blue;
			}
		}
	}
</style>
