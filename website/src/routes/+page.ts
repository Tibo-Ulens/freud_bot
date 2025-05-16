export const ssr = false;

import type { PageLoad } from "./(app)/$types";

import { PUBLIC_API_URL } from "$env/static/public";
import { redirect } from "@sveltejs/kit";

export const load: PageLoad = async ({ fetch }) => {
	console.log("fetching userdata");

	const user_data_res = await fetch(`${PUBLIC_API_URL}/me`, {
		credentials: "include",
	});

	if (user_data_res.status == 401) {
		return redirect(307, "/login");
	}

	const user_data = await user_data_res.json();

	return { user_data: user_data };
};
