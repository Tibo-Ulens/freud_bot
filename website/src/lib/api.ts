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

export type Guild = {
	id: string;
	name: string;
	icon_url: string | null;
};

export type GuildInfo = {
	id: string;
	name: string;
	icon_url: string | null;
	channels: Array<Channel>;
	roles: Array<Role>;
	verified_role: string | undefined;
	admin_role: string | undefined;
	logging_channel: string | undefined;
	verification_logging_channel: string | undefined;
	confession_approval_channel: string | undefined;
	confession_channel: string | undefined;
	pin_reaction_threshold: number;
	request_verification_message: string;
};

export type Channel = {
	id: string;
	name: string;
};

export type Role = {
	id: string;
	name: string;
	color: string;
};

export type GuildConfig = {
	guild_id: string;
	verified_role: string | null;
	admin_role: string | null;
	logging_channel: string | null;
	verification_logging_channel: string | null;
	confession_approval_channel: string | null;
	confession_channel: string | null;
	pin_reaction_threshold: number;
	request_verification_message: string;
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

	public static async get_guilds(fetch: Fetch, url: URL): Promise<ApiResponse<Array<Guild>>> {
		console.log("fetching manageable guilds");

		const guild_res = await fetch(`${PUBLIC_API_URL}/config/guilds`, {
			credentials: "include",
		});

		if (guild_res.status === 401) {
			return redirect(307, `/login?redirect=${encodeURIComponent(url.href)}`);
		}

		if (guild_res.status === 200) {
			const guild_data = await guild_res.json();
			return { tag: "ok", data: guild_data };
		}

		const error_data = await guild_res.json();
		const error = { tag: "err", status: guild_res.status, ...error_data };

		return error;
	}

	public static async get_guild_info(id: string, fetch: Fetch, url: URL): Promise<ApiResponse<GuildInfo>> {
		console.log("fetching guild info");

		const guild_res = await fetch(`${PUBLIC_API_URL}/config/guild/${id}`, {
			credentials: "include",
		});

		if (guild_res.status === 401) {
			return redirect(307, `/login?redirect=${encodeURIComponent(url.href)}`);
		}

		if (guild_res.status === 200) {
			const guild_data = await guild_res.json();
			return { tag: "ok", data: guild_data };
		}

		const error_data = await guild_res.json();
		const error = { tag: "err", status: guild_res.status, ...error_data };

		return error;
	}

	public static async update_guild(
		id: string,
		data: string,
		fetch: Fetch,
		url: URL,
	): Promise<ApiResponse<GuildConfig>> {
		console.log("updating guild config");

		const response = await fetch(`${PUBLIC_API_URL}/config/guild/${id}`, {
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
			const config_data = await response.json();
			return { tag: "ok", data: config_data };
		}

		const error_data = await response.json();
		const error = { tag: "err", status: response.status, ...error_data };

		return error;
	}

	public static async request_verify(fetch: Fetch, data: string, url: URL): Promise<ApiResponse<null>> {
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

	public static async verify_code(fetch: Fetch, code: string, url: URL): Promise<ApiResponse<null>> {
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
