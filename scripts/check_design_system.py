#!/usr/bin/env python3
"""Validate the single Next.js frontend's design-system invariants."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / "packages/design-system/src/tokens.css"
APP_ENTRY = ROOT / "apps/app/app/globals.css"
PACKAGE_MANIFEST = ROOT / "packages/design-system/package.json"

REQUIRED_IMPLEMENTATION = (
    ROOT / "apps/app/app/design-system/page.tsx",
    ROOT / "apps/app/app/home.css",
    ROOT / "apps/app/app/company-research.css",
    ROOT / "apps/app/components/layout/AppShell.tsx",
    ROOT / "apps/app/components/layout/PageHeader.tsx",
    ROOT / "apps/app/components/ui/Badge.tsx",
    ROOT / "apps/app/components/ui/Button.tsx",
    ROOT / "apps/app/components/ui/Card.tsx",
    ROOT / "apps/app/components/ui/Input.tsx",
    ROOT / "apps/app/components/ui/StatusPanel.tsx",
    ROOT / "apps/app/components/ui/Surface.tsx",
)

APPLICATION_SOURCE_ROOTS = (
    ROOT / "apps/app/app",
    ROOT / "apps/app/components",
    ROOT / "packages/design-system/src",
)

SOURCE_SUFFIXES = {".css", ".tsx"}
RAW_COLOR = re.compile(r"(?:(?<!&)#[0-9a-f]{3,8}\b|rgba?\()", re.IGNORECASE)
# A brand icon's own official colors (e.g. Google's four-color "G") are a
# real, standard exemption -- these render inside an inline SVG via the
# `fill` attribute, a fundamentally different mechanism from a CSS color
# declaration, and no design token would be correct here even in
# principle: the icon's colors are mandated by the brand, not by this
# product's own palette.
SVG_FILL_ATTR = re.compile(r'\bfill\s*=\s*["\']#[0-9a-f]{3,8}\b', re.IGNORECASE)
INLINE_PAGE_STYLE = re.compile(r"<style(?:\s|>)", re.IGNORECASE)
RAW_FONT_WEIGHT = re.compile(r"font-weight\s*:\s*[1-9]00\b", re.IGNORECASE)
RAW_FONT_SIZE = re.compile(r"font-size\s*:\s*(\d+(?:\.\d+)?)px\b", re.IGNORECASE)
# References with an explicit CSS fallback are allowed to be component-level
# extension points. Bare references must resolve somewhere in the shared or
# application sources; otherwise the browser silently drops the declaration.
TOKEN_REFERENCE = re.compile(r"var\(\s*(--ds-[a-z0-9-]+)\s*\)", re.IGNORECASE)
TOKEN_DEFINITION = re.compile(r"(--ds-[a-z0-9-]+)\s*:", re.IGNORECASE)
TOKEN_VALUE = re.compile(r"^\s*(--ds-[a-z0-9-]+)\s*:\s*([^;]+);", re.IGNORECASE | re.MULTILINE)
HEX_COLOR = re.compile(r"^#[0-9a-f]{6}$", re.IGNORECASE)

REQUIRED_TOKENS = {
    "--ds-color-bg-canvas",
    "--ds-color-bg-surface",
    "--ds-color-text-primary",
    "--ds-color-text-secondary",
    "--ds-color-border-default",
    "--ds-color-action",
    "--ds-color-negative",
    "--ds-color-warning",
    "--ds-font-family-sans",
    "--ds-font-family-editorial",
    "--ds-font-family-mono",
    "--ds-space-4",
    "--ds-radius-md",
    "--ds-shadow-surface",
    "--ds-target-min",
    "--ds-focus-ring",
}


def fail(message: str) -> None:
    raise SystemExit(f"design-system check failed: {message}")


for path in (
    PACKAGE_MANIFEST,
    TOKENS,
    ROOT / "packages/design-system/src/foundation.css",
    ROOT / "packages/design-system/src/primitives.css",
    ROOT / "packages/design-system/src/index.css",
):
    if not path.is_file():
        fail(f"missing {path.relative_to(ROOT)}")

manifest = json.loads(PACKAGE_MANIFEST.read_text())
if manifest.get("style") != "./src/index.css":
    fail("package manifest must expose ./src/index.css through the style field")

root_export = manifest.get("exports", {}).get(".")
if not isinstance(root_export, dict) or root_export.get("style") != "./src/index.css":
    fail("package root export must define the CSS style condition")

for path in REQUIRED_IMPLEMENTATION:
    if not path.is_file():
        fail(f"missing implementation contract {path.relative_to(ROOT)}")

token_source = TOKENS.read_text()
definitions = re.findall(r"^\s*(--ds-[a-z0-9-]+)\s*:", token_source, re.MULTILINE)
duplicates = sorted({name for name in definitions if definitions.count(name) > 1})
if duplicates:
    fail(f"duplicate token definitions: {', '.join(duplicates)}")

missing = sorted(REQUIRED_TOKENS.difference(definitions))
if missing:
    fail(f"missing required tokens: {', '.join(missing)}")

token_values = dict(TOKEN_VALUE.findall(token_source))


def resolve_hex(token_name: str, seen: set[str] | None = None) -> str:
    """Resolve a simple token alias to its six-digit hex palette value."""

    chain = set() if seen is None else seen
    if token_name in chain:
        fail(f"cyclic color token reference at {token_name}")
    chain.add(token_name)
    value = token_values.get(token_name, "").strip()
    if HEX_COLOR.fullmatch(value):
        return value
    reference = TOKEN_REFERENCE.fullmatch(value)
    if reference:
        return resolve_hex(reference.group(1), chain)
    fail(f"contrast token {token_name} must resolve to a six-digit hex color")


def relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return (0.2126 * linear[0]) + (0.7152 * linear[1]) + (0.0722 * linear[2])


def contrast_ratio(foreground: str, background: str) -> float:
    light, dark = sorted(
        (relative_luminance(foreground), relative_luminance(background)), reverse=True
    )
    return (light + 0.05) / (dark + 0.05)


# Muted text is routinely used at 11-13px, so it needs normal-text AA
# contrast on every shared neutral surface.
for background_token in (
    "--ds-color-bg-surface",
    "--ds-color-bg-canvas",
    "--ds-color-bg-subtle",
):
    ratio = contrast_ratio(resolve_hex("--ds-color-text-muted"), resolve_hex(background_token))
    if ratio < 4.5:
        fail(
            "--ds-color-text-muted must maintain 4.5:1 contrast against "
            f"{background_token}; received {ratio:.2f}:1"
        )

for path in (APP_ENTRY,):
    if '@import "@scrooner/design-system"' not in path.read_text():
        fail(f"{path.relative_to(ROOT)} does not import the shared entry point")

raw_color_violations: list[str] = []
raw_typography_violations: list[str] = []
application_sources: list[Path] = []
for source_root in APPLICATION_SOURCE_ROOTS:
    for path in source_root.rglob("*"):
        if path.suffix not in SOURCE_SUFFIXES or path == TOKENS or path.name.endswith(".test.tsx"):
            continue
        application_sources.append(path)
        for line_number, line in enumerate(path.read_text().splitlines(), start=1):
            if RAW_COLOR.search(line) and not SVG_FILL_ATTR.search(line):
                raw_color_violations.append(f"{path.relative_to(ROOT)}:{line_number}")
            if path.suffix == ".css" and RAW_FONT_WEIGHT.search(line):
                raw_typography_violations.append(
                    f"{path.relative_to(ROOT)}:{line_number} raw font weight"
                )
            size = RAW_FONT_SIZE.search(line) if path.suffix == ".css" else None
            # The 9px/10px values are the explicitly documented dense-table
            # exception in frontend-guardrails.md; all normal UI typography
            # must consume the discrete --ds-font-size-* scale.
            if size and float(size.group(1)) not in {9, 10}:
                raw_typography_violations.append(
                    f"{path.relative_to(ROOT)}:{line_number} raw font size"
                )

if raw_color_violations:
    fail("raw color values outside tokens.css: " + ", ".join(raw_color_violations))

if raw_typography_violations:
    fail("raw typography values outside tokens.css: " + ", ".join(raw_typography_violations))

all_design_sources = [TOKENS, *application_sources]
available_custom_properties: set[str] = set()
referenced_custom_properties: set[str] = set()
for path in all_design_sources:
    source = path.read_text()
    available_custom_properties.update(TOKEN_DEFINITION.findall(source))
    referenced_custom_properties.update(TOKEN_REFERENCE.findall(source))

undefined_references = sorted(referenced_custom_properties.difference(available_custom_properties))
if undefined_references:
    fail("undefined design-token references: " + ", ".join(undefined_references))

inline_page_styles: list[str] = []
for pages_root in (ROOT / "apps/app/app",):
    for path in pages_root.rglob("*"):
        if path.suffix != ".tsx":
            continue
        if INLINE_PAGE_STYLE.search(path.read_text()):
            inline_page_styles.append(str(path.relative_to(ROOT)))

if inline_page_styles:
    fail("page-level <style> blocks must be extracted: " + ", ".join(inline_page_styles))

primitive_source = (ROOT / "packages/design-system/src/primitives.css").read_text()
default_button = re.search(r"\.ds-button\s*\{(?P<body>.*?)\}", primitive_source, re.DOTALL)
if not default_button or "min-height: var(--ds-target-min)" not in default_button.group("body"):
    fail("default .ds-button must use the shared 44px minimum target token")

print(
    f"design-system contract: {len(definitions)} tokens; "
    f"{len(REQUIRED_IMPLEMENTATION)} implementation contracts; "
    "Next.js entry point connected; AA muted text and 44px default targets; "
    "no raw colors, typography, or undefined application tokens"
)
