import { permanentRedirect } from "next/navigation";

export default function LegacySavedScreensPage() {
  permanentRedirect("/app/screens");
}
