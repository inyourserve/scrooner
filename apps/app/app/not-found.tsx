import Link from "next/link";
import { PublicPage } from "@/components/public/PublicPage";
export default function NotFound() { return <PublicPage title="We couldn’t find that page" description="The page may have moved, or the address may be incorrect."><section className="public-callout"><h2>Continue your research</h2><p>Return home to search for a company or create a new screen.</p><p><Link className="ds-button ds-button--primary" href="/">Return home</Link></p></section></PublicPage>; }
