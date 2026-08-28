import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { Badge } from "./Badge";
import { Button } from "./Button";
import { StatusPanel } from "./StatusPanel";
import { Surface } from "./Surface";
import { BrandMark } from "./BrandMark";

afterEach(cleanup);

describe("design-system React adapters", () => {
  it("renders the Scrooner research-aperture mark instead of a chart glyph", () => {
    const { container } = render(<BrandMark size="large" />);
    const mark = container.querySelector("svg.ds-brand-mark");

    expect(mark).toHaveClass("ds-brand-mark--large");
    expect(mark?.querySelector(".ds-brand-mark__frame")).toBeInTheDocument();
    expect(mark?.querySelector(".ds-brand-mark__point")).toBeInTheDocument();
    expect(mark?.querySelectorAll("rect, [class*='bar']")).toHaveLength(0);
  });

  it("composes typed visual variants without losing native attributes", () => {
    render(<Button variant="destructive" size="small" disabled>Delete screen</Button>);

    const button = screen.getByRole("button", { name: "Delete screen" });
    expect(button).toBeDisabled();
    expect(button).toHaveClass("ds-button", "ds-button--destructive", "ds-button--small");
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
});
