import { PUBLIC_API_URL } from "$env/static/public";

export async function load(event) {
	const user_data_res = await event.fetch(`${PUBLIC_API_URL}/me`);
	console.log(user_data_res);
	const user_data = await user_data_res.json();
	console.log(user_data);

	return { user_data: user_data };
}
