export const ssr = false;

import type { PageLoad } from "./$types";

import { error } from "@sveltejs/kit";

import { Api } from "$lib/api";

export const load: PageLoad = async ({ fetch, url }) => {
	const v_res = await Api.is_verified(fetch, url);

	if (v_res.tag === "err") {
		error(v_res.status);
	}

	const m_res = await Api.me(fetch, url);

	if (m_res.tag === "err") {
		error(m_res.status);
	}

	return { verified: v_res.data, userdata: m_res.data };
};
