import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		// host: "localhost",
		// port: 5173,
		// cors: {
		// 	origin: ["http://localhost:5173", "http://localhost:3000"],
		// 	methods: ["GET", "POST", "PUT"],
		// 	credentials: true,
		// },
	},
});
