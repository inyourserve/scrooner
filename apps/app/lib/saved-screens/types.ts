import type { ScreenQueryPayload } from "@/lib/screener/types";

export interface SavedScreen {
  id: number;
  name: string;
  slug: string;
  query: ScreenQueryPayload;
  created_at: string;
  updated_at: string;
  run?: ScreenRunPage | null;
}

export interface ScreenRunPage {
  run_id: string;
  query_text: string;
  normalized_query: ScreenQueryPayload;
  total_count: number;
  items: import("@/lib/screener/types").MatchedCompany[];
  excluded_missing_data: import("@/lib/screener/types").MissingCompany[];
  excluded_inactive: string[];
  cursor: string | null;
  previous_cursor?: string | null;
  next_cursor: string | null;
  ran_at: string;
  corrections?: Array<{
    source_text: string;
    corrected_text: string;
    kind: string;
    requires_confirmation: boolean;
  }>;
}

export type AccessTokenProvider = () => Promise<string | null>;
