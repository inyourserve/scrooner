import { permanentRedirect } from "next/navigation";

export default function LegacyScreener() {
  permanentRedirect("/");
}
