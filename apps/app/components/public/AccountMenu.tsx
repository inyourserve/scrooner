"use client";

import Link from "next/link";
import { useState } from "react";
import { ChevronDown, LogOut, Settings, Star, UserRound } from "lucide-react";
import { logout } from "@/app/auth/actions";
import { Popover } from "@/components/ui/Popover";

function displayName(email: string | null) {
  if (!email) return "Account";
  const local = email.split("@")[0] ?? email;
  return local.replace(/[._-]+/g, " ");
}

// The one account control shown once a visitor is known to be signed in --
// used identically whether that was learned server-side (AppShell, passing
// a real email straight away) or client-side (HeaderAuthAction, once its
// session check resolves).
export function AccountMenu({ email }: { email: string | null }) {
  const [open, setOpen] = useState(false);
  const close = () => setOpen(false);

  return (
    <div className="account-menu">
      <button
        type="button"
        className="account-menu-trigger"
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
      >
        <UserRound size={15} aria-hidden="true" />
        <span>{displayName(email)}</span>
        <ChevronDown size={14} aria-hidden="true" />
      </button>
      {open && (
        <Popover label="Account menu" onClose={close} className="account-menu-popover">
          <Link className="account-menu-item" href="/app/screens" onClick={close}><Star size={16} aria-hidden="true" />Saved screens</Link>
          <Link className="account-menu-item" href="/app/account" onClick={close}><Settings size={16} aria-hidden="true" />Account settings</Link>
          <div className="account-menu-divider" role="separator" />
          <form action={logout}>
            <button className="account-menu-item account-menu-item--danger" type="submit">
              <LogOut size={16} aria-hidden="true" />Sign out
            </button>
          </form>
        </Popover>
      )}
    </div>
  );
}
