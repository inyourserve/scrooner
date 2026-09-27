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
});
