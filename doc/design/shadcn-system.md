Yes. **Shadcn is an excellent choice for Scrooner**, but don't ship “default shadcn.” Shadcn is intentionally open code: you own the components and are expected to turn them into your own design system. Its current theming system is built around semantic CSS variables, which is exactly what we should exploit. ([shadcn/ui][1])

For Scrooner, I would establish a **Scrooner UI System** before polishing individual pages.

## Scrooner visual direction

Think:

**Screener.in simplicity + Linear polish + institutional financial terminal discipline.**

Not:

**colorful SaaS dashboard + 25 cards + gradients everywhere.**

Premium for Scrooner should feel:

> Quiet, dense, precise, extremely fast, trustworthy.

Especially because financial data itself is the product.

---

# 1. Stop using default Shadcn styling

The biggest mistake would be:

```tsx
<Card>
  <CardHeader>
  <CardTitle>Revenue</CardTitle>
  </CardHeader>
  <CardContent>...</CardContent>
</Card>
```

...50 times on every page.

It immediately starts looking like a shadcn demo.

Instead, use shadcn as primitives and create:

```text
components/
├── ui/                  ← shadcn primitives
│
├── scrooner/
│   ├── metric.tsx
│   ├── financial-table.tsx
│   ├── stock-header.tsx
│   ├── section-header.tsx
│   ├── delta.tsx
│   ├── data-value.tsx
│   ├── chart-tooltip.tsx
│   ├── company-logo.tsx
│   ├── ticker-badge.tsx
│   └── empty-state.tsx
```

Your developers should mostly build pages from **Scrooner components**, not raw shadcn components.

---

# 2. Establish design tokens first

Shadcn itself recommends CSS variables for theming. ([shadcn/ui][2])

I would start approximately here:

| Token             | Direction              |
| ----------------- | ---------------------- |
| App background    | `#FAFAFA` / near white |
| Main surface      | `#FFFFFF`              |
| Primary text      | `#111111`              |
| Secondary text    | `#666666`              |
| Muted text        | `#8A8A8A`              |
| Border            | `#E8E8E8`              |
| Subtle background | `#F7F7F7`              |
| Positive          | restrained green       |
| Negative          | restrained red         |
| Brand/action      | one Scrooner accent    |
| Radius            | 6–8px                  |
| Shadows           | almost none            |

The key distinction is:

**border > shadow**

Financial software looks better when information is separated structurally instead of floating inside giant shadows.

For example:

```css
:root {
  --background: #fafafa;
  --foreground: #111111;

  --card: #ffffff;
  --card-foreground: #111111;

  --muted: #f7f7f7;
  --muted-foreground: #717171;

  --border: #e8e8e8;
  --input: #e5e5e5;

  --positive: #16803c;
  --negative: #c9362b;

  --radius: 0.5rem;
}
```

These aren't sacred values; the important thing is to define them **centrally**.

---

# 3. Typography will make the biggest difference

Use one excellent sans-serif.

My preference:

**Geist → Inter → system font stack**

Avoid having 5 font weights everywhere.

### Scrooner typography system

| Usage            |    Size | Weight |
| ---------------- | ------: | -----: |
| Page title       |    24px |    600 |
| Stock price      | 28–32px |    600 |
| Section heading  |    16px |    600 |
| Table heading    | 12–13px |    500 |
| Standard content |    14px |    400 |
| Financial data   |    14px |    500 |
| Supporting label |    12px |    400 |

Most importantly:

```css
font-variant-numeric: tabular-nums;
```

Or Tailwind:

```tsx
className="tabular-nums"
```

for:

```text
$213.42
18.26%
$3.42T
42.17
$95.4B
```

Every number in a column should visually align.

That tiny detail makes a financial product look much more professional.

---

# 4. Reduce radius

One of the easiest ways to make a product look less like a generic SaaS app.

Avoid:

```text
rounded-2xl
rounded-3xl
```

everywhere.

Prefer:

```text
Buttons       6px
Inputs        6px
Cards         8px
Dropdowns     8px
Tooltips      6px
Badges        4px / pill only when concept requires it
```

You want Scrooner to feel **precise rather than playful**.

---

# 5. Don't put every section inside cards

For something like:

```text
Apple Inc.

Price
Market Cap
PE Ratio
ROIC

Revenue
Profit
Balance Sheet
Cash Flow
Ownership
Insiders
```

don't do:

```text
┌──────── Card ─────────┐
└───────────────────────┘

┌──────── Card ─────────┐
└───────────────────────┘

┌──────── Card ─────────┐
└───────────────────────┘
```

Prefer:

```text
Apple Inc.                                      $278.31
AAPL · NASDAQ                                  +1.42%

────────────────────────────────────────────────────────

Market Cap    P/E       ROIC       Revenue Growth
$4.12T        31.4x     48.2%      +6.4%

────────────────────────────────────────────────────────

Financials

Revenue
2022       2023       2024       2025       TTM
394B       383B       391B       416B       431B

────────────────────────────────────────────────────────

Profit & Loss
...
```

That is much closer to the **KISS BORING** principle Scrooner should follow.

---

# 6. Make tables the hero

For Scrooner, tables are not secondary UI.

**Tables are one of your primary product surfaces.**

Shadcn's current data-table approach combines its Table primitive with TanStack Table, allowing sorting, filtering, visibility, pagination and custom behavior rather than forcing a generic data-grid abstraction. ([shadcn/ui][3])

Build your own:

```tsx
<ScroonerFinancialTable />
```

with strict rules.

| Property         | Scrooner                |
| ---------------- | ----------------------- |
| Row height       | 42–46px                 |
| Header           | 12px muted              |
| Number alignment | right                   |
| Label alignment  | left                    |
| Numbers          | tabular                 |
| Borders          | subtle horizontal       |
| Vertical borders | generally none          |
| Zebra rows       | generally no            |
| Hover            | very subtle             |
| Negative         | red only where useful   |
| Positive         | green only where useful |
| Missing          | `—`                     |
| Units            | consistent              |
| Sticky column    | when useful             |
| Sticky header    | long datasets           |

For example:

```text
                  2022      2023      2024      2025
Revenue          394.3B    383.3B    391.0B    416.2B
Growth             7.8%     -2.8%      2.0%      6.4%
Operating Profit 119.4B    114.3B    123.2B    133.1B
OP Margin          30.3%     29.8%     31.5%     32.0%
```

This should feel beautiful even with **zero charts**.

---

# 7. Use color extremely carefully

Do not make:

**green = Scrooner brand**

because green already carries financial meaning.

Use green primarily for:

```text
Positive return
Positive change
Improvement
Buy/increase where semantically appropriate
```

Red:

```text
Loss
Negative change
Deterioration
```

Then choose a separate neutral brand/action color.

Potentially:

**deep blue / indigo / near-black**

for:

```text
Links
Selected tabs
Primary CTA
Focus states
Active filters
```

This keeps meaning unambiguous.

---

# 8. Stock header should become a signature component

Something like:

```text
┌─────────────────────────────────────────────────────────────┐

 [AAPL]  Apple Inc.                                  ☆ Watch

         AAPL · NASDAQ · Technology

 $278.31
 +$3.42 (+1.24%) today

 Market Cap    P/E      ROIC      Div Yield
 $4.12T        31.4x    48.2%     0.43%

 Overview   Financials   Ownership   Insiders   Filings

└─────────────────────────────────────────────────────────────┘
```

Not necessarily inside a literal card.

This should be:

```tsx
<StockHeader />
```

and every company gets exactly the same hierarchy.

---

# 9. Premium charts = less chart decoration

Shadcn's current chart component uses Recharts and supports shared theme/config tokens, so you can make chart appearance globally consistent. ([shadcn/ui][4])

For Scrooner:

```text
NO gradients under every line
NO rainbow datasets
NO huge legends
NO thick gridlines
NO unnecessary animation
NO giant chart titles inside cards
```

Instead:

```text
thin grid
subtle axis
good tooltip
one dominant series
clear period selector
precise hover values
```

Something like:

```text
Revenue

$120B ┤                          ●
      │                   ●──────
 $90B ┤            ●──────
      │     ●──────
 $60B ┤─────
      └────────────────────────────
       2021  2022  2023  2024  2025

       Annual   Quarterly
```

Tooltip quality is more important than chart decoration.

---

# 10. Buttons should be boring

You probably need four variants:

```tsx
<Button variant="default" />
<Button variant="secondary" />
<Button variant="outline" />
<Button variant="ghost" />
```

But resist using `default` everywhere.

For Scrooner, a huge percentage of actions should be:

```text
ghost
outline
text link
```

Primary filled buttons should be reserved for genuinely primary actions.

Example:

```text
[ Add to Watchlist ]      ← outline

Set Alert                  ← ghost/text

[ Run Screen ]             ← primary
```

This dramatically reduces visual noise.

---

# 11. Icons: Lucide, 16–18px

Don't use big icons inside giant colored circles.

Avoid:

```text
      🏢
  Company Info
```

Prefer:

```text
Building2   Company
```

Usually:

```tsx
className="size-4"
```

or:

```tsx
className="size-[18px]"
```

Keep stroke widths and icon sizes consistent.

---

# 12. Perfect the interaction states

This is where many products lose the premium feeling.

Every interactive element needs:

```text
Default
Hover
Active
Focus
Disabled
Loading
Empty
Error
Success
```

For example, don't show:

```text
Loading...
```

when a financial table loads.

Show a skeleton matching the exact table layout.

And avoid random spinners everywhere.

---

# 13. Motion should barely be noticeable

Use roughly:

```text
120–180ms
```

for:

```text
hover
dropdown
tooltip
tab state
popover
sidebar
```

Avoid spring/bounce effects.

Premium financial software should feel **instant**, not animated.

---

# 14. Search can become a premium interaction

Instead of a boring search input:

```text
Search stock...
```

create:

```text
⌕ Search companies, tickers or screens...            ⌘ K
```

Then:

```text
Recent
Apple                         AAPL
Microsoft                     MSFT

Companies
Amazon                        AMZN

Screens
High ROIC Compounders
FCF Growth Stocks
```

Using shadcn:

```text
Command
Dialog
Popover
Input
```

This could become one of Scrooner's signature interactions.

---

# 15. Use whitespace deliberately

Premium doesn't necessarily mean lots of whitespace.

For Scrooner:

**macro whitespace = generous**

**data density = tight**

Example:

```text
32px between major sections

16–20px section padding

8px between label/value

4–8px within compact controls

44px table rows
```

This gives you:

**calm page + dense information.**

Exactly what an investing product needs.

---

# 16. Build these Scrooner components

This is probably the highest-leverage engineering decision.

```text
<ScroonerShell />

<PageHeader />

<StockHeader />

<CompanyIdentity />

<Metric />
<MetricGroup />

<Delta />

<DataValue />

<SectionHeader />

<FinancialTable />

<DataTable />

<StockChart />

<ChartTooltip />

<PeriodSelector />

<TickerBadge />

<CompanyLogo />

<WatchlistButton />

<SearchCommand />

<EmptyState />

<ErrorState />

<TableSkeleton />

<ChartSkeleton />
```

Then your frontend engineers stop solving visual styling independently on every page.

---

# 17. One component should have one visual language

For example, never have:

```text
Page 1
Section title = 22px bold

Page 2
Section title = 18px semibold

Page 3
Section title = 16px bold

Page 4
Section title = inside CardHeader
```

Instead:

```tsx
<SectionHeader
  title="Financials"
  description="Annual consolidated results"
/>
```

everywhere.

This sounds boring.

It is also how products start feeling expensive.

---

# 18. Desktop width matters

Avoid the common:

```tsx
max-w-7xl
```

without thinking about what the page contains.

Scrooner contains wide financial tables.

I'd probably use roughly:

```text
Normal content:
max-width ~1280px

Stock/company pages:
max-width ~1440px

Long reading content:
max-width ~760–820px
```

Don't force financial data into blog-width containers.

---

# 19. Mobile shouldn't simply stack every card

On mobile prioritize:

```text
Company
Price
Change

Key metrics

Chart

Financials

Ownership

Other sections
```

Make tables horizontally scrollable but preserve:

```text
first column
header
year labels
```

where technically feasible.

Don't transform a 15-row financial table into 60 giant cards.

---

# 20. Don't change primitive libraries just for fashion

One current Shadcn detail: new Shadcn projects now default to **Base UI**, while Radix remains supported. Their own guidance explicitly cautions production apps against switching primitive libraries just because something newer exists. ([shadcn/ui][5])

So if Scrooner already uses shadcn + Radix:

**keep it.**

The premium improvement should happen **above the primitive layer**.

---

# What I'd implement next

In this order:

1. **Create Scrooner design tokens** — colors, typography, spacing, radius, shadows, motion.
2. **Customize Button/Input/Badge/Table/Tabs** globally.
3. **Create `DataValue`, `Delta`, `Metric`, `SectionHeader`.**
4. **Build one killer `FinancialTable`.**
5. **Build the stock header.**
6. **Create the stock search/⌘K experience.**
7. **Standardize charts and chart tooltips.**
8. **Standardize skeleton/error/empty states.**
9. **Apply the system to one Apple company page first.**
10. Only after Apple looks nearly perfect, roll the system across all **5,200+ companies**.

### The rule I'd give the frontend team

> **Do not make Scrooner beautiful by adding things. Make it beautiful by removing inconsistency.**

And for this product specifically:

> **Data is the decoration. Typography, spacing and hierarchy make it premium.**

If we follow that, Scrooner can look significantly more expensive than the typical shadcn SaaS dashboard **without becoming flashy or violating the simple/boring product philosophy.**
