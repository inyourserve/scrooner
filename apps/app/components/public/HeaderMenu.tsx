"use client";

import Link from "next/link";
import { LayoutDashboard, Menu, Plus, Search, Star, X } from "lucide-react";
import { useState } from "react";
import { Popover } from "@/components/ui/Popover";

export function HeaderMenu({ authenticated }: { authenticated: boolean }) {
  const [open, setOpen] = useState(false);
  const close = () => setOpen(false);

  return <div className="header-menu">
    <button className="header-menu__trigger" type="button" aria-label={open ? "Close navigation" : "Open navigation"} aria-haspopup="dialog" aria-expanded={open} onPointerDown={(event) => event.stopPropagation()} onClick={() => setOpen((value) => !value)}>
      {open ? <X size={18} aria-hidden="true" /> : <Menu size={18} aria-hidden="true" />}
    </button>
    {open && <Popover label="Navigation" onClose={close} className="header-menu__popover">
      <Link href="/explore" onClick={close}><Search size={16} aria-hidden="true" />Explore</Link>
      <Link href="/app/screens/new" onClick={close}><Plus size={16} aria-hidden="true" />Create screen</Link>
      {authenticated && <Link href="/app/screens" onClick={close}><Star size={16} aria-hidden="true" />Saved screens</Link>}
      <Link href="/app" onClick={close}><LayoutDashboard size={16} aria-hidden="true" />Dashboard</Link>
    </Popover>}
  </div>;
}
