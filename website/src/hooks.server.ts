import { error } from "@sveltejs/kit";

export async function handleFetch({ request, fetch }) {
	const response = await fetch(request);

	if (response.status == 401) {
		return error(401, { message: "unauthorized" });
	}

	return response;
}
