export const ssr = false;

import type { PageLoad } from "./$types";

import { error } from "@sveltejs/kit";

import { Api } from "$lib/api";

export const load: PageLoad = async ({ params, fetch, url }) => {
	const response = await Api.get_guild_info(params.id, fetch, url);

	if (response.tag === "err") {
		error(response.status);
	}

	return { guild: response.data };
};
