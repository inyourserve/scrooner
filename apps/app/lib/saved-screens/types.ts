import type { ScreenQueryPayload } from "@/lib/screener/types";

export interface SavedScreen {
  id: number;
  name: string;
  query: ScreenQueryPayload;
  created_at: string;
  updated_at: string;
}

export type AccessTokenProvider = () => Promise<string | null>;

