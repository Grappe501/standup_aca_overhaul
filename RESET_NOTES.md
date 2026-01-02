# ACA Overhaul Reset (Scaffold Preserved)

This reset removes all previously ingested content files and keeps the Astro + MDX scaffold intact.

## What changed
- Removed root-level exported HTML artifacts.
- Replaced the `docs_migrated` content collection with a fresh `docs` collection.
- Added minimal placeholder MDX entries for top-level routes so the site runs before re-ingestion.
- Updated routing pages to reference the new `docs` collection and fail gracefully if an entry is missing.

## Next step
Re-ingest clean DOCX sources into `src/content/docs/` (or via your ingest pipeline) so the frontmatter includes:
- `title`
- `route` (preferred)
- `source` (optional)

The catch-all router (`src/pages/[...slug].astro`) resolves by `route` first, then by slug.
