export const ssr = false;

import type { PageLoad } from "./$types";

import { PUBLIC_API_URL } from "$env/static/public";
import { redirect } from "@sveltejs/kit";

export const load: PageLoad = async ({ params, fetch }) => {
	console.log("verifying code");

	const verify_res = await fetch(`${PUBLIC_API_URL}/verify/${params.code}`, {
		credentials: "include",
		method: "POST",
	});

	if (verify_res.status === 401) {
		return redirect(307, "/login");
	}

	return { status: verify_res.status };
};
