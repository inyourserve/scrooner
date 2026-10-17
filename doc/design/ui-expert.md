You are a world-class UI/UX designer and senior frontend engineer. I am building **Scrooner**, a premium US stock screener and stock research platform for serious investors.

Use **shadcn/ui** as the design foundation:
https://ui.shadcn.com/docs

Your job is to upgrade the full product UI into a premium, clean, fast, trustworthy financial product. Do not only make it look good. Build and protect a complete design system.
## Product Context

Scrooner is for US stock screening, watchlists, saved screens, alerts, financial data, ownership data, insider data, sectors, industries, and investor research.

The design should feel like:

- Bloomberg-quality data density, but easier to use
- Linear-level polish
- Vercel-level clarity
- Stripe-level visual discipline
- Modern fintech trust, not crypto/gambling style
- Premium SaaS, not generic dashboard template

Avoid childish colors, heavy gradients, huge cards, unnecessary animations, and over-decorated UI.

## Core Design Direction

Create a visual language that feels:

- Premium
- Calm
- Data-first
- Investor-grade
- Fast
- Trustworthy
- Sharp
- Minimal but not empty
- Dense but not cluttered

The product should be usable by a serious investor who wants to scan 100s of stocks quickly.

## Start With Theming

First, create a proper theme using shadcn + Tailwind CSS variables.

Define:

- Light mode colors
- Dark mode colors
- Background layers
- Surface colors
- Border colors
- Muted text
- Primary action color
- Success color
- Warning color
- Danger color
- Positive stock movement color
- Negative stock movement color
- Neutral data color
- Chart palette
- Table row hover color
- Active navigation state

Important:
Do not use loud green/red everywhere. Financial positive/negative colors should be readable, calm, and accessible.

Suggested style direction:

Light mode:
- Background: near-white, slightly cool
- Surface: white
- Secondary surface: light gray/blue-gray
- Text: near-black
- Muted text: slate/gray
- Border: soft gray
- Primary: deep blue, black, or refined indigo
- Positive: controlled green
- Negative: controlled red

Dark mode:
- Background: deep navy/charcoal, not pure black
- Surface: slightly lifted dark surface
- Border: subtle slate
- Text: soft white
- Muted text: gray/slate
- Positive/negative colors must remain readable

Create the theme in a maintainable way using CSS variables, not random one-off Tailwind colors.

## Typography

Create a full typography system.

Use a premium, readable font stack. Prefer one of:

- Inter
- Geist
- Satoshi
- IBM Plex Sans
- Manrope

For financial tables and numbers, use tabular numbers:
- `font-variant-numeric: tabular-nums;`

Define clear text styles for:

- Page title
- Section title
- Card title
- Table header
- Table cell
- Metric value
- Metric label
- Supporting text
- Empty state text
- Form labels
- Error messages
- Navigation labels

Rules:
- Do not use oversized headings inside dashboards.
- Data pages should prioritize scanning, not hero-style typography.
- Numbers should align properly.
- Use compact line heights for tables.
- Use enough contrast for readability.

## Layout System

Create a consistent layout system for the app.

Required areas:

- Marketing pages
- App dashboard under `/app`
- Screener pages
- Stock detail pages
- Watchlist
- Saved screens
- Alerts
- Account/settings
- Affiliate marketing page
- Affiliate dashboard

Use:

- Consistent max-widths
- Responsive containers
- Proper spacing scale
- Sticky app header where useful
- Sidebar or top navigation depending on page context
- Breadcrumbs where useful
- Clear page hierarchy

Rules:
- Avoid nested cards.
- Avoid excessive card borders.
- Avoid floating dashboard boxes everywhere.
- Tables and filters should feel native to the product, not like copied admin UI.

### Implemented layout contract

Scrooner uses one global frame for the header, page content, sticky research navigation, and footer. This is the most important alignment rule in the product.

- `--ds-container-frame` is the maximum outer frame. It is currently `1600px`.
- `--ds-container-gutter` and `--ds-container-gutter-compact` are the only horizontal page gutters. Each token represents one side: 48px per side on larger screens and 20px per side on compact screens.
- `.ds-container` aligns navigation and footer content to the global frame.
- `PageShell` aligns every normal page to the same frame.
- Every `PageShell` uses the same global frame. There are no page-width variants.
- Dashboards, saved screens, create-screen, screen results, company pages, settings, and public directories therefore share the same left edge, right edge, and usable width.
- Readability is controlled inside components: prose uses a reading measure, forms choose an appropriate field measure, and tables use the available frame. The page itself is never narrowed.
- Marketing home and authentication may use specialized internal compositions, but their navigation and footer still use the global frame.

The logo, page heading, primary surface, table edge, sticky company navigation, and footer brand share the global frame guides. Narrow prose and form content stays left-aligned inside that frame rather than independently centering the whole page.

Do not add page-level rules such as `width: min(100% - 32px, ...)`, arbitrary `max-width`, or `margin: 0 auto` to create a new page container. Use `PageShell`; component-level measures are allowed for prose, dialogs, forms, and search fields.

### Spacing ownership

Spacing must have one owner:

- `PageShell` owns page-top, page-bottom, and viewport gutter spacing.
- `PageHeader` owns the gap below the page introduction.
- Section components own spacing between sections.
- Cards and surfaces own their internal padding.
- Tables own cell padding, never surrounding page padding.
- The header and footer own only their vertical padding; `.ds-container` owns their horizontal alignment.

Never compensate for a parent alignment problem with child margins. Avoid negative margins for normal layout. Do not stack page padding, section padding, and card padding unless each layer has a clear semantic purpose.

### Alignment QA

At 1440px, 1280px, 1024px, 768px, and 390px verify:

- Header logo and page frame begin on the same vertical guide.
- Sticky stock navigation and company content begin on that guide.
- Screen-results and financial tables use the bounded data frame.
- Page titles do not jump horizontally between loading, empty, error, and success states.
- Footer content uses the same guide as the header.
- Mobile gutters are identical across public, authenticated, company, and screener routes.
- Horizontal scrolling occurs inside a table viewport, not on the document body.

## Theme Architecture And Learnings

The theme is semantic, token-driven, and shared by every route.

- `packages/design-system/src/tokens.css` is the only source of truth for palette, semantic colors, typography, spacing, radii, shadows, controls, motion, and container dimensions.
- Light mode values live in the canonical `:root` contract.
- Dark mode overrides semantic tokens under the theme selector; components do not contain separate dark-mode color implementations.
- Components consume semantic intent such as `--ds-color-bg-surface`, `--ds-color-text-secondary`, `--ds-color-border-default`, and `--ds-color-positive`. They must not consume arbitrary hex colors.
- Positive and negative colors express financial meaning only. Navy is used for brand and action emphasis so links and buttons do not falsely imply gains.
- shadcn-compatible variables map to Scrooner semantic tokens, keeping third-party primitives consistent without creating a second theme.
- Theme preference is applied before the application paints and is then controlled by the shared theme toggle. This prevents a light-theme flash when dark mode is selected.
- Surfaces, tables, inputs, menus, dialogs, skeletons, focus rings, hover states, and charts must be reviewed in both themes.

Important implementation learning: adding dark colors page by page creates visual drift and missed states. Override semantic tokens once, then fix any component that bypasses the token contract. Compatibility aliases are temporary migration tools, not permission to create another palette.

## Design-System Enforcement

The design-system checker is part of the product architecture, not optional linting. It verifies the shared package entry point, required tokens and implementation files, color and typography discipline, token references, accessibility contrast, minimum targets, and prohibited page-level styles.

Any new route should begin with `PageShell` and shared primitives. If a design cannot fit the system, improve the system deliberately instead of adding a one-page exception. Loading, empty, error, and success states must use the same shell and geometry as the final page.

## Responsiveness

Design properly for:

- Desktop
- Laptop
- Tablet
- Mobile

Mobile is not an afterthought.

For responsive behavior:

- Tables should have horizontal scroll or column priority logic.
- Filters should collapse into drawer/sheet on mobile.
- Sidebar should collapse.
- Top actions should remain accessible.
- Important stock metrics should stack cleanly.
- Avoid text overflow and broken layouts.
- Navigation should remain simple.

Test key screens at:
- 1440px
- 1280px
- 1024px
- 768px
- 390px

## Dark Mode

Dark mode must be first-class.

Do not just invert colors.

Check:

- Tables
- Charts
- Badges
- Inputs
- Dropdowns
- Modals
- Tooltips
- Hover states
- Active states
- Borders
- Skeleton loading states
- Empty states

Dark mode should feel premium and investor-focused, not overly neon.

## Component System

Use shadcn/ui components properly and customize them into our product system.

Audit and improve:

- Button
- Input
- Select
- Combobox
- Command menu
- Tabs
- Dropdown menu
- Dialog
- Sheet
- Popover
- Tooltip
- Badge
- Card
- Table
- Data table
- Checkbox
- Radio
- Switch
- Slider
- Skeleton
- Alert
- Toast
- Pagination
- Breadcrumb
- Navigation menu
- Sidebar
- Accordion

For each component:
- Define variants
- Define spacing
- Define hover/focus/disabled states
- Define dark mode behavior
- Define loading state
- Define error state where applicable

### Implemented component contract

- Shared components expose semantic variants; page CSS must not restyle their fundamental states.
- Buttons use primary, secondary, outline, ghost, and destructive hierarchy. Loading preserves button geometry and disables repeat submission.
- Inputs share control height, border, focus ring, invalid, disabled, readonly, placeholder, and dark-mode behavior.
- Cards and surfaces are structural. Interactive elevation is reserved for genuinely clickable content.
- Badges communicate compact status and never replace explanatory text for material states.
- Status, empty, loading, and error components preserve the same geometry as successful content.
- Dialogs and popovers use the shared overlay, elevation, motion, focus, and responsive width contracts.
- Skeletons use a theme-aware highlight and match the final component shape to avoid layout shift.
- All financial tables use the shared `ds-data-table` contract for density, tabular numbers, scrolling, focus, sticky regions, hover behavior, sorting, and pagination.
- Domain components may add column widths or semantic highlighting, but must not redefine the shared table anatomy.

### Trust-critical journey contract

Company research, screen creation, raw screen results, and saved-screen results use the same workspace title scale, eyebrow style, research alignment, action hierarchy, surface radius, data-table density, and trust language. These pages must feel like consecutive steps in one research workflow.

Trust cues should be factual and close to the data: source, period, freshness, missing-data treatment, and formula version. Avoid decorative security claims or vague labels such as “AI powered.” Primary actions advance the research task; export, columns, website, and similar utilities remain secondary or ghost actions.

## Buttons

Create button hierarchy:

- Primary: main action
- Secondary: less important action
- Ghost: table/action row utilities
- Destructive: dangerous action
- Outline: secondary neutral action
- Icon button: compact controls

Examples:
- Create screen
- Save screen
- Add to watchlist
- Set alert
- Export
- Share
- Login
- Join affiliate program

Buttons should be compact, sharp, and consistent.

## Forms And Filters

This is critical for Scrooner.

Design filters for stock screening beautifully.

Filter types may include:

- Market cap
- P/E ratio
- Revenue growth
- Profit margin
- Dividend yield
- Sector
- Industry
- Analyst rating
- Insider buying
- Institutional ownership
- Price movement
- Volume
- Valuation
- Financial health

UX rules:
- Filters must be easy to add, remove, edit, and reset.
- Active filters should be clearly visible.
- Use chips/badges for active filters.
- Use drawers/sheets where needed.
- Use range inputs carefully.
- Provide clear empty states.
- Save screen flow should be polished.
- Logged-out users can explore, but creating screens requires login.

## Data Tables

Data tables are the heart of the product.

Create premium tables for:

- Stock screener
- Watchlist
- Saved screens
- Alerts
- Affiliate referrals
- Affiliate commissions
- Stock financials
- Insider transactions
- Ownership data

Table requirements:

- Sticky header where useful
- Sortable columns
- Clear hover state
- Compact row density
- Column alignment
- Right-align numbers
- Left-align names
- Use tabular numbers
- Use badges for sector, rating, status
- Positive/negative movement styling
- Loading skeleton
- Empty state
- Error state
- Pagination
- Column visibility controls if needed
- Mobile behavior

Do not make tables look like generic admin panels. They should feel like financial terminals made simpler.

## Charts And Data Visualization

Design chart styles for:

- Price movement
- Revenue
- Net income
- Free cash flow
- Margins
- Ownership trends
- Insider transactions
- Sector performance
- Affiliate revenue

Rules:
- Use restrained colors.
- Charts must be readable in dark mode.
- Use clear legends.
- Avoid too many grid lines.
- Tooltips should be clean and useful.
- Numbers should be formatted correctly.
- Do not over-animate charts.

## Navigation

Design a clean navigation system.

Public site navigation:
- Home
- Screener
- Stocks
- Sectors
- Industries
- Pricing
- Open Data
- Affiliate
- Login
- Join

Logged-in app navigation under `/app`:
- Dashboard
- Screener
- Watchlist
- Saved Screens
- Alerts
- Account
- Affiliate Dashboard, if user is affiliate

Rules:
- Keep navigation simple.
- Current page should be obvious.
- Use icons carefully.
- Avoid too many nav items.
- Mobile nav should be clean.

## Key Pages To Design

Redesign or create these pages with the new system:

### 1. Public Screener Page

Goal:
Let users explore US stocks and understand value before login.

Must include:
- Search
- Popular screens
- Filters preview
- Stock table
- Login prompt for saving/creating custom screens

### 2. Create Screen Page

Goal:
Logged-in users create custom stock screens.

Must include:
- Filter builder
- Live results table
- Save screen action
- Reset filters
- Screen name
- Empty state
- Loading state

### 3. Stock Detail Page

Goal:
Give a clean research view of one stock.

Sections:
- Header with stock name, ticker, price, movement
- Key metrics
- Financials
- Balance sheet
- Cash flow
- Ownership
- Insider activity
- Similar companies
- Related screens
- Add to watchlist
- Set alert

### 4. Watchlist

Goal:
Quickly monitor selected stocks.

Must include:
- Watchlist table
- Price movement
- Key metrics
- Alerts shortcut
- Empty state

### 5. Saved Screens

Goal:
Users manage screens they created.

Must include:
- Screen cards or table
- Last updated
- Number of matching stocks
- Edit
- Run
- Delete
- Empty state

### 6. Alerts

Goal:
Users manage stock alerts.

Must include:
- Alert table
- Alert type
- Condition
- Status
- Trigger history
- Create alert
- Pause/delete

### 7. Affiliate Marketing Page

Goal:
Convince creators, finance bloggers, YouTubers, newsletter writers, and investing educators to join.

Must include:
- Clear hero
- Commission structure
- Who should join
- How it works
- Example earning calculation
- Trust section
- FAQ
- Join/login CTA

Design should be conversion-focused but still premium.

### 8. Affiliate Dashboard

Goal:
Affiliate users track performance.

Must include:
- Revenue summary
- Clicks
- Signups
- Paid conversions
- Conversion rate
- Pending commission
- Approved commission
- Payout status
- Referral link
- Copy link button
- Commission table
- Payout history
- Performance chart

## States

Design all important states:

- Loading
- Empty
- Error
- No data
- Partial data
- Locked/login required
- Permission denied
- Success toast
- Form validation error
- Saving
- Saved
- Disabled
- Hover
- Focus
- Active

This is very important. Do not only design the happy path.

## Microcopy

Scrooner sounds like a precise research partner: calm, direct, financially literate, and honest about what the data can and cannot establish. Copy should reduce the time between a user’s question and a defensible decision. It must never sound like a trading tip, a generic AI assistant, or an enterprise-software brochure.

### Voice principles

- Lead with the user’s outcome: “Compare companies” rather than “Unlock powerful comparison capabilities.”
- Prefer concrete verbs and nouns. Use “Create a screen,” “Sort by market cap,” and “View filings.”
- Be concise without becoming cryptic. A label names the action; supporting copy explains only the consequence a user cannot infer.
- Sound confident about product behavior and appropriately cautious about financial interpretation.
- Use plain English first. Introduce financial terminology when it improves precision, not prestige.
- State limitations next to the affected data. Never hide freshness, coverage, missing-data treatment, or methodology behind promotional language.
- Never invent urgency, certainty, popularity, performance, or exclusivity.

### Product vocabulary

Use one term for each concept across navigation, pages, dialogs, and status messages:

- **Query:** the plain-language or structured instruction entered by the user.
- **Screen:** the reusable set of criteria produced from a query. Users create, edit, run, and save screens.
- **Results:** the companies returned by a screen. Use “matches” only in a count or action where the relationship is useful, such as “Show matches.”
- **Criteria:** the individual conditions inside a screen. Use “filters” only for familiar UI controls or when space is constrained.
- **Company:** the entity being researched. Use “stock” for a security, price, ticker, or market-specific context—not as a universal synonym for company.
- **Saved screen:** the durable user-owned screen. Never alternate with “saved query.”
- **Reported fundamentals:** values calculated from reported company data under Scrooner’s documented methodology.

### Style rules

- Use sentence case everywhere except ticker symbols and established abbreviations.
- Buttons begin with a verb: “Show matches,” “Save screen,” “Edit criteria,” “Export CSV.”
- Headings name the destination or outcome; they do not repeat navigation breadcrumbs.
- Use contractions in conversational guidance and recovery messages, but avoid casual filler.
- Prefer active voice and present tense.
- Use numerals for quantities and dates; format units consistently with the data table.
- Do not use exclamation marks, rhetorical questions, emojis, or decorative claims such as “AI-powered,” “smart,” “powerful,” “world-class,” or “revolutionary.”
- Do not say “successfully.” If the interface shows the completed result, the adverb adds nothing.
- Do not blame the user. Explain what happened and give the next useful action.

### State-writing pattern

- **Loading:** name the object or operation: “Loading screen results,” “Sorting by market cap.” Avoid “Please wait.”
- **Empty:** state what is absent, then offer the most likely next step: “No companies match every criterion. Remove or loosen a condition.”
- **Error:** state what could not be completed, preserve what is safe, and provide recovery: “We couldn’t sort these results. Your current order is unchanged. Try again.”
- **Partial data:** quantify the gap and explain treatment: “18 companies were excluded because a required metric was unavailable.”
- **Confirmation:** name the completed state: “Screen saved.” Avoid congratulatory language.
- **Authentication:** explain the value of signing in at the moment it matters: “Sign in to save this screen and run it again later.”

### Preferred interface copy

- “Create screen”
- “Show matches”
- “Save screen”
- “Edit criteria”
- “Add criterion”
- “No companies match every criterion”
- “Sign in to save this screen”
- “Data updated 4 min ago”
- “Commission pending”
- “Payout approved”

Every copy review must verify terminology, factual support, action clarity, state recovery, accessibility when read out of visual context, and consistency between desktop and mobile variants.

## Accessibility

Follow accessibility best practices:

- Proper contrast
- Keyboard navigation
- Focus states
- Accessible dropdowns/dialogs
- Labels for inputs
- ARIA where needed
- Do not rely only on color for gains/losses
- Support screen readers for key actions
- Hit targets should be usable on mobile

## Motion

Use motion very carefully.

Allowed:
- Subtle hover transitions
- Smooth sheet/dialog open
- Skeleton loading
- Small chart transitions

Avoid:
- Fancy page animations
- Distracting motion
- Crypto-style glowing effects
- Over-animated dashboard cards

## Implementation Rules

Use:

- shadcn/ui
- Tailwind CSS
- CSS variables
- Lucide icons if icons are needed
- Reusable components
- Clean component naming
- Consistent spacing and variants

Create reusable components like:

- `PageHeader`
- `MetricCard`
- `DataTable`
- `FilterBuilder`
- `ActiveFilterChips`
- `StockPriceChange`
- `StockLogo`
- `EmptyState`
- `LoadingSkeleton`
- `UpgradePrompt`
- `AffiliateStatCard`
- `CommissionTable`
- `ChartCard`

But do not over-abstract too early. Build components when they are clearly reused.

## Design Quality Bar

Before finalizing, check:

- Does it feel like a serious financial product?
- Is it easy to scan?
- Are tables readable?
- Is dark mode actually polished?
- Does mobile work?
- Are filters easy to use?
- Are numbers aligned?
- Are colors restrained?
- Are empty/loading/error states handled?
- Is spacing consistent?
- Does it look custom, not like default shadcn?
- Would a paying user trust this product?

### Verified-state rules

- Never render a service failure as an empty collection. “Nothing saved” is only valid after a successful empty response.
- Preserve the canonical `query` parameter across create, results, edit, and save journeys; old aliases may be read for compatibility but must not become new links.
- A result table must include predicate metrics, nested boolean-query metrics, explicitly selected display metrics, and the active sort metric.
- Empty pagination reads `0–0 of 0`; ranges may never imply a result that does not exist.
- Validate narrow layouts in a real browser at an exact device viewport. Source inspection and resized screenshots alone do not prove the absence of horizontal overflow.
- Theme initialization may run before hydration, but the root must explicitly tolerate that intentional attribute difference without emitting runtime warnings.

## Final Output Expected

Start implementation in this order:

1. Theme tokens and CSS variables
2. Typography system
3. Layout shell
4. Navigation
5. Core shadcn component styling
6. Table system
7. Filter builder system
8. Screener page
9. Stock detail page
10. Watchlist, saved screens, alerts
11. Affiliate page
12. Affiliate dashboard
13. Dark mode polish
14. Mobile polish
15. Final QA pass

Do not ask me for every small decision. Make strong design decisions like a senior product designer. If something is unclear, choose the option that makes Scrooner feel more premium, trustworthy, and useful for US stock investors.
