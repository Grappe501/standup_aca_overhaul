import { defineCollection, z } from "astro:content";

const docsMigrated = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string().optional(),
    route: z.string().optional(),
    source: z.string().optional(),
  }),
});

export const collections = {
  docs_migrated: docsMigrated,
};
