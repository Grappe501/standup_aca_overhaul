// src/lib/sections.ts
// Stand Up Arkansas — ACA Overhaul
// Single source of truth for labels, ordering, and route helpers.

export const SECTION_LABELS = {
    "start-here": "Start Here",
    "the-problem": "The Problem",
    "the-backbone": "The Backbone",
    proposal: "The Proposal",
    congress: "For Congress",
    library: "Library",
  
    // Future / optional sections (safe placeholders)
    loopholes: "Loopholes",
    rural: "Rural",
  } as const;
  
  export type SectionSlug = keyof typeof SECTION_LABELS;
  
  /**
   * Canonical ordering for the primary reading flow.
   * Used for:
   * - Home cards
   * - Congress navigation
   * - Guided flows
   * - Future Library grouping
   */
  export const SECTION_ORDER: SectionSlug[] = [
    "start-here",
    "the-problem",
    "the-backbone",
    "proposal",
    "congress",
  ];
  
  /**
   * Secondary / appendix-style sections.
   * Not part of the core reading flow.
   */
  export const SECONDARY_SECTIONS: SectionSlug[] = ["library", "loopholes", "rural"];
  
  /**
   * Normalize a path/route into a clean pathname.
   * Examples:
   *  - "the-backbone"        -> "/the-backbone"
   *  - "/the-backbone/"      -> "/the-backbone"
   *  - "/the-backbone/x/y"   -> "/the-backbone/x/y"
   */
  export function normalizePathname(input: string): string {
    const s = (input ?? "").toString().trim();
    if (!s) return "/";
    const withSlash = s.startsWith("/") ? s : `/${s}`;
    const collapsed = withSlash.replace(/\/{2,}/g, "/");
    return collapsed.length > 1 ? collapsed.replace(/\/+$/g, "") : "/";
  }
  
  /**
   * Get the first segment (slug) from a route/path.
   * Example:
   *  "/the-backbone/overview" -> "the-backbone"
   */
  export function firstSegmentFromRoute(route: string): SectionSlug | null {
    const pathname = normalizePathname(route);
    const seg = pathname.split("/").filter(Boolean)[0];
    if (!seg) return null;
    return (seg in SECTION_LABELS ? (seg as SectionSlug) : null);
  }
  
  /**
   * Convert a route segment into a human-friendly title.
   * Fallback when a label is not explicitly defined.
   */
  export function titleizeSegment(seg: string): string {
    const s = (seg ?? "").toString().trim();
    if (!s) return "";
    return s
      .replace(/[-_]+/g, " ")
      .replace(/\s+/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase());
  }
  
  /**
   * Resolve a label from a full route or path.
   * Example:
   *  "/the-backbone/overview" -> "The Backbone"
   */
  export function sectionLabelFromRoute(route: string): string | null {
    const seg = firstSegmentFromRoute(route);
    if (!seg) return null;
    return SECTION_LABELS[seg] ?? titleizeSegment(seg);
  }
  
  /**
   * Return ordered core sections with labels.
   * Useful for building nav menus or card grids.
   */
  export function getOrderedSections(): { slug: SectionSlug; label: string }[] {
    return SECTION_ORDER.map((slug) => ({
      slug,
      label: SECTION_LABELS[slug] ?? titleizeSegment(slug),
    }));
  }
  
  /**
   * Return ordered secondary sections with labels.
   */
  export function getSecondarySections(): { slug: SectionSlug; label: string }[] {
    return SECONDARY_SECTIONS.map((slug) => ({
      slug,
      label: SECTION_LABELS[slug] ?? titleizeSegment(slug),
    }));
  }
  
  /**
   * Test whether a slug is part of the core reading flow.
   */
  export function isCoreSection(slug: string): slug is SectionSlug {
    return (slug as SectionSlug) in SECTION_LABELS && SECTION_ORDER.includes(slug as SectionSlug);
  }
  