import Link from "next/link";
import { ChevronRight } from "lucide-react";

export type BreadcrumbItem = { label: string; href?: string };

export function Breadcrumb({ items, label = "Breadcrumb" }: { items: BreadcrumbItem[]; label?: string }) {
  return <nav className="ds-breadcrumb" aria-label={label}><ol>{items.map((item, index) => {
    const current = index === items.length - 1;
    return <li key={`${item.label}-${index}`}>{index > 0 && <ChevronRight size={13} aria-hidden="true" />}{item.href && !current ? <Link href={item.href}>{item.label}</Link> : <span aria-current={current ? "page" : undefined}>{item.label}</span>}</li>;
  })}</ol></nav>;
}
