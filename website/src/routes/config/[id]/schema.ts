import { z } from "zod";

export const form_schema = z.object({
	verified_role: z.string().optional(),
	admin_role: z.string().optional(),
	logging_channel: z.string().optional(),
	verification_logging_channel: z.string().optional(),
	confession_approval_channel: z.string().optional(),
	confession_channel: z.string().optional(),
	pin_reaction_threshold: z.number().min(1),
	request_verification_message: z.string(),
});

export type FormSchema = typeof form_schema;
