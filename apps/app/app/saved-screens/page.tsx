import { PageHeader } from "@/components/layout/PageHeader";
import { SavedScreensClient } from "@/components/saved-screens/SavedScreensClient";

export default function SavedScreensPage() {
  return <main className="main-content saved-screens-content" id="main-content"><PageHeader eyebrow="Your workspace" title="Saved screens" description="Rerun saved criteria against the latest available data." /><p className="saved-screens-note">Saved screens store criteria, not frozen results. Match counts may change as company data changes.</p><SavedScreensClient /></main>;
}
