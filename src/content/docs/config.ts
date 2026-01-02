// src/content/config.ts
// Astro Content Collections config
// Stand Up Arkansas — ACA Overhaul (DOCX/MD(X) ingestion target)

import { defineCollection, z } from "astro:content";

const docs = defineCollection({
  type: "content",
  schema: z.object({
    // Display title (falls back to titleized slug if omitted)
    title: z.string().optional(),

    // Canonical route for this entry (preferred over /<slug>)
    // Examples: "/the-problem", "/proposal/overview"
    route: z
      .string()
      .optional()
      .refine(
        (v) => v === undefined || v.startsWith("/"),
        "route must start with '/' (example: '/the-problem')"
      ),

    // Optional summary fields used by the Library card UI
    description: z.string().optional(),
    summary: z.string().optional(),
    kicker: z.string().optional(),

    // Optional metadata you may want later (safe to ignore for now)
    section: z.string().optional(), // e.g., "the-problem" | "the-backbone" | "proposal"
    order: z.number().int().optional(), // manual ordering within a section
    tags: z.array(z.string()).optional(),
    draft: z.boolean().optional(),
  }),
});

export const collections = {
  docs,
};
