import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Badge } from "./Badge";
import { Button } from "./Button";
import { StatusPanel } from "./StatusPanel";
import { Surface } from "./Surface";
import { BrandMark } from "./BrandMark";
import { Dialog } from "./Dialog";
import { Field } from "./Field";
import { Popover } from "./Popover";
import { IconButton } from "./IconButton";
import { Card, CardContent, CardDescription, CardHeader, CardHeading, CardTitle } from "./Card";
import { Input, Textarea } from "./Input";
import { Breadcrumb } from "./Breadcrumb";
import { Skeleton } from "./Skeleton";
import { Table, TableBody, TableCell, TableContainer, TableHead, TableHeader, TableRow, TableRowHeader } from "./Table";
import { Tooltip } from "./Tooltip";

afterEach(cleanup);

describe("design-system React adapters", () => {
  it("renders the one canonical Scrooner upward-trend mark", () => {
    const { container } = render(<BrandMark size="large" />);
    const mark = container.querySelector("svg.ds-brand-mark");

    expect(mark).toHaveClass("ds-brand-mark--large");
    expect(mark?.querySelector(".ds-brand-mark__line")).toBeInTheDocument();
    expect(mark?.querySelector(".ds-brand-mark__arrow")).toBeInTheDocument();
  });

  it("gives dialogs a complete keyboard dismissal and initial-focus contract", () => {
    const close = vi.fn();
    render(<Dialog title="Rename screen" onClose={close}><input aria-label="Screen name" data-dialog-initial-focus /></Dialog>);

    expect(screen.getByRole("dialog", { name: "Rename screen" })).toBeInTheDocument();
    expect(screen.getByLabelText("Screen name")).toHaveFocus();
    fireEvent.keyDown(document, { key: "Escape" });
    expect(close).toHaveBeenCalledOnce();
  });

  it("keeps labels, help, and errors connected through the shared field contract", () => {
    const { rerender } = render(<Field htmlFor="email" label="Email" hint="Use your work email"><input id="email" /></Field>);
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByText("Use your work email")).toHaveClass("ds-help");

    rerender(<Field htmlFor="email" label="Email" error="Enter a valid email" errorId="email-error"><input id="email" aria-describedby="email-error" /></Field>);
    expect(screen.getByRole("alert")).toHaveTextContent("Enter a valid email");
  });

  it("dismisses reusable popovers with Escape", () => {
    const close = vi.fn();
    render(<Popover label="Save screen" onClose={close}><input aria-label="Name" data-popover-initial-focus /></Popover>);
    expect(screen.getByRole("dialog", { name: "Save screen" })).toBeInTheDocument();
    expect(screen.getByLabelText("Name")).toHaveFocus();
    fireEvent.keyDown(document, { key: "Escape" });
    expect(close).toHaveBeenCalledOnce();
  });

  it("supports system-owned overlay sizing, alignment, and density", () => {
    const close = vi.fn();
    const { rerender } = render(<Dialog title="Details" size="large" onClose={close}>Body</Dialog>);
    expect(screen.getByRole("dialog", { name: "Details" })).toHaveClass("ds-dialog--large");

    rerender(<Popover label="Filters" size="small" align="start" padded={false} onClose={close}><button>Apply</button></Popover>);
    expect(screen.getByRole("dialog", { name: "Filters" })).toHaveClass("ds-popover--small", "ds-popover--start", "ds-popover--flush");
  });

  it("composes typed visual variants without losing native attributes", () => {
    render(<Button variant="destructive" size="small" disabled>Delete screen</Button>);

    const button = screen.getByRole("button", { name: "Delete screen" });
    expect(button).toBeDisabled();
    expect(button).toHaveClass("ds-button", "ds-button--destructive", "ds-button--small");
  });

  it("owns loading and icon-only action semantics", () => {
    render(<><Button loading loadingLabel="Saving…">Save</Button><IconButton label="Remove condition" tone="destructive" icon={<span>×</span>} /></>);

    expect(screen.getByRole("button", { name: "Saving…" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Saving…" })).toHaveAttribute("aria-busy", "true");
    expect(screen.getByRole("button", { name: "Remove condition" })).toHaveClass("ds-icon-button--destructive");
  });

  it("keeps semantic tone text and surface composition available to consumers", () => {
    render(<Surface raised padded><Badge tone="warning">Partial coverage</Badge></Surface>);

    expect(screen.getByText("Partial coverage")).toHaveClass("ds-badge--warning");
    expect(screen.getByText("Partial coverage").parentElement).toHaveClass("ds-surface--raised", "ds-surface--padded");
  });

  it("announces errors assertively and exposes loading without a decorative label", () => {
    const { rerender } = render(<StatusPanel tone="negative" title="The screen did not run">Try again.</StatusPanel>);

    expect(screen.getByRole("alert")).toHaveAttribute("aria-live", "assertive");
    rerender(<StatusPanel title="Running your screen" busy>Criteria are preserved.</StatusPanel>);
    expect(screen.getByRole("status")).toHaveAttribute("aria-busy", "true");
  });

  it("renders premium card variants through the shared system contract", () => {
    render(
      <Card variant="raised" interactive>
        <CardHeader><CardHeading><CardTitle>Quality screen</CardTitle><CardDescription>Five durable filters</CardDescription></CardHeading></CardHeader>
        <CardContent>Results</CardContent>
      </Card>,
    );

    const card = screen.getByText("Results").closest("[data-slot='card']");
    expect(card).toHaveClass("ds-card", "ds-card--raised", "ds-card--interactive");
    expect(screen.getByRole("heading", { name: "Quality screen" })).toHaveClass("ds-card__title");
  });

  it("standardizes input and textarea density without page-owned classes", () => {
    render(<><Input aria-label="Threshold" numeric size="large" /><Textarea aria-label="Screen description" /></>);

    expect(screen.getByLabelText("Threshold")).toHaveClass("ds-control", "ds-control--large", "ds-control--mono");
    expect(screen.getByLabelText("Screen description")).toHaveClass("ds-control");
  });

  it("provides compact financial table alignment and sticky-column hooks", () => {
    render(<TableContainer aria-label="Companies"><Table><TableHeader><TableRow><TableHead data-sticky="true">Company</TableHead><TableHead data-align="right">ROE</TableHead></TableRow></TableHeader><TableBody><TableRow><TableRowHeader data-sticky="true">AAPL</TableRowHeader><TableCell data-align="right">42.1%</TableCell></TableRow></TableBody></Table></TableContainer>);

    expect(screen.getByRole("table")).toHaveClass("ds-table");
    expect(screen.getByRole("columnheader", { name: "ROE" })).toHaveAttribute("data-align", "right");
    expect(screen.getByRole("rowheader", { name: "AAPL" })).toHaveAttribute("data-sticky", "true");
  });

  it("renders shared breadcrumbs and non-announced skeletons", () => {
    const { container } = render(<><Breadcrumb items={[{ label: "Screens", href: "/app/screens" }, { label: "Quality" }]} /><Skeleton /></>);

    expect(screen.getByRole("navigation", { name: "Breadcrumb" })).toBeInTheDocument();
    expect(screen.getByText("Quality")).toHaveAttribute("aria-current", "page");
    expect(container.querySelector("[data-slot='skeleton']")).toHaveAttribute("aria-hidden", "true");
  });

  it("connects the shared tooltip trigger to its premium tooltip surface", () => {
    render(<Tooltip label="Return on equity" side="bottom" align="start">Net income divided by average equity.</Tooltip>);

    const trigger = screen.getByRole("button", { name: "About Return on equity" });
    const tooltip = screen.getByRole("tooltip");
    expect(trigger).toHaveClass("ds-tooltip__trigger");
    expect(trigger).toHaveAttribute("aria-describedby", tooltip.id);
    expect(tooltip).toHaveClass("ds-tooltip__content");
    expect(trigger.closest("[data-slot='tooltip']")).toHaveAttribute("data-side", "bottom");
    expect(trigger.closest("[data-slot='tooltip']")).toHaveAttribute("data-align", "start");
  });

  it("uses a restrained semantic icon for informational status", () => {
    const { container } = render(<StatusPanel tone="info" title="Formula note">Calculated from reported fundamentals.</StatusPanel>);

    expect(screen.getByRole("status")).toHaveClass("ds-alert--info");
    expect(container.querySelector(".ds-alert__mark--info svg")).toBeInTheDocument();
  });
});
