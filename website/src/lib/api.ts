import { PUBLIC_API_URL } from "$env/static/public";
import { redirect } from "@sveltejs/kit";

type Fetch = (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;

export type ApiData<T> = { tag: "ok"; data: T };
export type ApiError = {
	tag: "err";
	status: number;
	text: string;
	code: number;
	info: string | null;
};
export type ApiResponse<T> = ApiData<T> | ApiError;

export type UserData = {
	id: string;
	username: string;
	avatar: string;
};

export class Api {
	public static async me(fetch: Fetch, url: URL): Promise<ApiResponse<UserData>> {
		console.log("fetching userdata");

		const user_data_res = await fetch(`${PUBLIC_API_URL}/me`, {
			credentials: "include",
		});

		if (user_data_res.status === 401) {
			return redirect(307, `/login?redirect=${encodeURIComponent(url.href)}`);
		}

		if (user_data_res.status === 200) {
			const user_data = await user_data_res.json();
			return { tag: "ok", data: user_data };
		}

		const error_data = await user_data_res.json();
		const error = { tag: "err", status: user_data_res.status, ...error_data };

		return error;
	}

	public static async request_verify(
		fetch: Fetch,
		data: string,
		url: URL,
	): Promise<ApiResponse<null>> {
		console.log("requesting verification code");

		const response = await fetch(`${PUBLIC_API_URL}/verify/request`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: data,
		});

		if (response.status === 401) {
			return redirect(307, `/login?redirect=${encodeURIComponent(url.href)}`);
		}

		if (response.status === 204) {
			return { tag: "ok", data: null };
		}

		const error_data = await response.json();
		const error = { tag: "err", status: response.status, ...error_data };

		return error;
	}

	public static async verify_code(
		fetch: Fetch,
		code: string,
		url: URL,
	): Promise<ApiResponse<null>> {
		console.log("verifying code");

		const verify_res = await fetch(`${PUBLIC_API_URL}/verify/${code}`, {
			credentials: "include",
			method: "POST",
		});

		if (verify_res.status === 401) {
			return redirect(307, `/login?redirect=${encodeURIComponent(url.href)}`);
		}

		if (verify_res.status === 204) {
			return { tag: "ok", data: null };
		}

		const error_data = await verify_res.json();
		const error = { tag: "err", status: verify_res.status, ...error_data };

		return error;
	}

	public static async is_verified(fetch: Fetch, url: URL): Promise<ApiResponse<boolean>> {
		console.log("checking if verified");

		const response = await fetch(`${PUBLIC_API_URL}/verify/check`);

		if (response.status === 401) {
			return redirect(307, `/login?redirect=${encodeURIComponent(url.href)}`);
		}

		if (response.status === 200) {
			const status = await response.json();

			return { tag: "ok", data: status };
		}

		const error_data = await response.json();
		const error = { tag: "err", status: response.status, ...error_data };

		return error;
	}
}
