# PostCSS CSS-package resolution needs a style entry

**Problem or clarification**

Both frontends imported `@scrooner/design-system`, and the package exported its
CSS root through `exports`, but a PostCSS/Tailwind resolver could still fail
with `ENOENT: open '@scrooner/design-system'`.

**How it was found**

The package symlinks and CSS files were present and readable, so this was not a
missing install. Inspection of the installed Tailwind resolver showed that CSS
imports are resolved with the `style` main field and `style` export condition.
The design-system manifest declared neither explicitly.

**Fix / decision**

`packages/design-system/package.json` now points both its top-level `style`
field and root `style` export condition to `./src/index.css`, while retaining a
default export for other bundlers. `scripts/check_design_system.py` now enforces
both entries. Next.js and Astro production builds pass with the package import.

**Why it matters going forward**

A CSS-only package needs a CSS-native manifest contract, not only a generic
package export. Keep application imports package-based; make the package
understandable to PostCSS, Tailwind, Vite, and JavaScript-aware bundlers instead
of bypassing it with fragile relative paths.
