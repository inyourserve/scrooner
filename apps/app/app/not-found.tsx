import Link from "next/link";
import { SearchX } from "lucide-react";
import { StatusPage } from "@/components/layout/StatusPage";
import { Button } from "@/components/ui/Button";

export default function NotFound() { return <StatusPage code="404" eyebrow="Page not found" title="That page isn’t in our filings" description="The address may be incorrect, or the page may have moved. You can return to the homepage or continue exploring US public companies." icon={<SearchX size={30} strokeWidth={1.7} />} primaryAction={<Button asChild><Link href="/explore">Explore companies</Link></Button>} />; }
