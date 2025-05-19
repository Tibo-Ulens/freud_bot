export const ssr = false;

import type { PageLoad } from "./$types";

import { error } from "@sveltejs/kit";

import { Api } from "$lib/api";

export const load: PageLoad = async ({ fetch, url }) => {
	const response = await Api.get_guilds(fetch, url);

	if (response.tag === "err") {
		error(response.status);
	}

	return { guilds: response.data };
};
