export const ssr = false;
export const prerender = true;

import { PUBLIC_API_URL } from "$env/static/public";
import { redirect } from "@sveltejs/kit";

export async function load(event) {
	console.log("fetching userdata");

	const user_data_res = await event.fetch(`${PUBLIC_API_URL}/me`, {
		credentials: "include",
	});

	if (user_data_res.status == 401) {
		return redirect(302, "/login");
	}

	const user_data = await user_data_res.json();

	return { user_data: user_data };
}
