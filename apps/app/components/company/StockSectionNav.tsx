"use client";

import { useEffect, useRef, useState } from "react";

export interface StockSectionLink { id: string; label: string }

export function StockSectionNav({ sections }: { sections: StockSectionLink[] }) {
  const [active, setActive] = useState(sections[0]?.id ?? "");
  const navRef = useRef<HTMLElement>(null);
  useEffect(() => {
    const elements = sections.map(({ id }) => document.getElementById(id)).filter((item): item is HTMLElement => Boolean(item));
    const observer = new IntersectionObserver((entries) => { const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0]; if (visible) setActive(visible.target.id); }, { rootMargin: "-22% 0px -68%", threshold: [0, .2, .6] });
    elements.forEach((element) => observer.observe(element));
    return () => observer.disconnect();
  }, [sections]);
  useEffect(() => { navRef.current?.querySelector(`[href="#${active}"]`)?.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" }); }, [active]);
  return <nav className="stock-section-nav" aria-label="Company research sections" ref={navRef}><div className="stock-section-nav__frame ds-container"><div className="stock-section-nav__track">{sections.map((section) => <a className={active === section.id ? "is-active" : undefined} href={`#${section.id}`} aria-current={active === section.id ? "location" : undefined} key={section.id}>{section.label}</a>)}</div></div></nav>;
}
