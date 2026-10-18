import type { CollectionEntry } from "astro:content";
import config from "@/config";

/**
 * Determines whether a post is eligible to be listed/rendered.
 *
 * - Shows drafts only in the local development server
 * - In production, excludes scheduled posts until `pubDatetime` minus the configured margin
 * - In dev, shows scheduled posts to make authoring easier
 */
export function postFilter({ data }: CollectionEntry<"posts">) {
  const isPublishTimePassed =
    Date.now() >
    new Date(data.pubDatetime).getTime() - config.posts.scheduledPostMargin;
  return import.meta.env.DEV || (!data.draft && isPublishTimePassed);
}
