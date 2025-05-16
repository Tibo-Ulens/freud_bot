export const ssr = false;

import type { PageLoad } from "./$types";

import { Api } from "$lib/api";
import { error } from "@sveltejs/kit";

export const load: PageLoad = async ({ params, url, fetch }) => {
	const me_response = await Api.me(fetch, url);

	if (me_response.tag === "err") {
		error(me_response.status);
	}

	const code_response = await Api.verify_code(fetch, params.code, url);

	return { userdata: me_response.data, code_response: code_response };
};
