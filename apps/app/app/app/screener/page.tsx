import { permanentRedirect } from "next/navigation";

export default function LegacyScreenerPage() {
  permanentRedirect("/app/screens/new");
}
