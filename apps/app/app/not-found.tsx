import Link from "next/link";
import { PublicPage } from "@/components/public/PublicPage";
export default function NotFound() { return <PublicPage title="Page not found" description="That address does not match a public Scrooner page."><section className="public-callout"><h2>Keep researching</h2><p>Check the address, return to the homepage, or search for a covered company.</p><p><Link className="ds-button ds-button--primary" href="/">Go to homepage</Link></p></section></PublicPage>; }
