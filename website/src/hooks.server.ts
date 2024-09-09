import { redirect } from "@sveltejs/kit";

export async function handleFetch({ request, fetch }) {
	const response = await fetch(request);

	if (response.status == 401) {
		return redirect(302, "/unauthorized");
	}

	return response;
}
