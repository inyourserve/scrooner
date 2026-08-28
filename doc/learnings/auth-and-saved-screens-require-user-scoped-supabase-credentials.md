# Authentication and saved screens require user-scoped Supabase credentials

> **Status:** Frontend activation blocked safely on 2026-08-22  
> **Scope:** `apps/app` Supabase Auth, shared cookies, and saved-screen CRUD

## Outcome

The repository contains a server-side Supabase project URL and service-role
credential for the Python backend, but it does not contain the publishable
credential required by a browser or a user-scoped Next.js SSR client. The
service-role credential cannot be used as a substitute: it is secret and can
bypass Row Level Security.

For that reason, login, registration, session refresh, and saved-screen writes
were not represented as working frontend features. The safe work completed
independently of those credentials is:

- an explicit non-secret environment contract in `apps/app/.env.example`;
- a fail-closed auth-configuration check that ignores service-role values; and
- a tested redirect-back sanitizer that prevents login open redirects.

## Current official implementation boundary

Current Supabase guidance for a cookie-session framework such as Next.js is to
use `@supabase/ssr`, create separate browser and per-request server clients,
and run session refresh from Next.js Proxy. Protected data must use
`supabase.auth.getClaims()` or a fresh `getUser()` result; server code must not
authorize from `getSession()` alone.

The current dependency versions verified on 2026-08-22 are:

- `@supabase/ssr` `0.12.4`; and
- `@supabase/supabase-js` `2.112.3`.

These should be exact pins with the lockfile committed. This matters for
Scrooner's cross-subdomain policy: `@supabase/ssr` `0.12.3` fixed a domain-
scoped cookie-deletion bug affecting name-keyed cookie stores such as Next.js.
Do not revive the cached `0.6.1` package found on the workstation.

## Inputs required to activate the feature

1. Add `NEXT_PUBLIC_SUPABASE_URL` to the Next.js build and runtime environment.
2. Add `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` from the Supabase Connect dialog.
3. Never add `SUPABASE_SERVICE_ROLE_KEY` to `apps/app` or any `NEXT_PUBLIC_`
   variable.
4. Install and pin the two official packages above, then commit the regenerated
   lockfile.
5. Confirm the session-scope decision. The repository's current locked design
   requires `Domain=.scrooner.com` in production and no explicit cookie domain
   on localhost. That deliberately sends the HttpOnly session cookie to both
   `scrooner.com` and `app.scrooner.com`, increasing the public site's security
   responsibility. If the Astro site only needs a sign-in link rather than a
   logged-in nav, host-only cookies on `app.scrooner.com` are safer and the
   design decision should be revised before implementation.
6. Configure Supabase Auth Site URL as `https://app.scrooner.com` and allow only
   the exact callback/recovery URLs used by the app. Localhost callbacks should
   be development-only.
7. Configure production email delivery before beta; default SMTP limits and
   customization rules are not a production mail service.

## Required implementation and verification

Once those inputs exist, the frontend implementation is:

1. Add browser, server, and Proxy Supabase clients using `getAll`/`setAll`.
2. Trigger `getClaims()` in Proxy so refreshed cookies reach both the request
   and response.
3. Add email/password sign-in, registration, email confirmation callback,
   forgot-password, update-password, and server-side sign-out routes.
4. Validate `redirect_url` with the checked-in sanitizer before every redirect.
5. Add a server-only data-access layer that validates identity for every saved-
   screen read or mutation, obtains the user's access token, and forwards it to
   `apps/backend`. Never accept a user ID from a form or browser payload.
6. Keep `/screener` public. Gate only Save, `/screens`, screen rename/delete,
   account, and other personalized operations.
7. Test anonymous, expired, and valid sessions; cookie refresh; sign-out; two-
   user isolation; malicious redirect URLs; and production cookie attributes.
8. Test the real production topology across both subdomains. A localhost test
   cannot prove the `Domain=.scrooner.com` contract.

## Saved-screen UX contract

Saved screens store criteria, not result snapshots. A successful screen exposes
one **Save screen** action. Anonymous users go through login and return to the
same result. Authenticated users name and save in place. `/screens` lists the
name, readable criteria, and update time; rerun executes the stored query against
current data. Rename is inline, and delete requires confirmation. The UI must
not claim last-run freshness because the current backend model does not store a
run timestamp.

## Sources checked

- Supabase SSR and Next.js client setup: https://supabase.com/docs/guides/auth/server-side/creating-a-client
- Supabase server-package selection: https://supabase.com/docs/guides/auth/choosing-a-server-package
- Supabase changelog breaking changes: https://supabase.com/changelog?types=breaking-change
- `@supabase/ssr` changelog: https://github.com/supabase/ssr/blob/main/CHANGELOG.md
- Local Next.js 16 authentication, Proxy, cookies, forms, and environment-variable guides under `apps/app/node_modules/next/dist/docs/`
