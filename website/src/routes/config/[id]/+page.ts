export const ssr = false;

import type { PageLoad } from "./$types";

import { error } from "@sveltejs/kit";

import { Api } from "$lib/api";
import { superValidate } from "sveltekit-superforms";
import { zod } from "sveltekit-superforms/adapters";
import { form_schema } from "./schema";

export const load: PageLoad = async ({ params, fetch, url }) => {
	const [response, form] = await Promise.all([
		Api.get_guild_info(params.id, fetch, url),
		superValidate(zod(form_schema)),
	]);

	if (response.tag === "err") {
		error(response.status);
	}

	return {
		guild: response.data,
		form: form,
	};
};
