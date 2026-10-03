import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { HeaderMenu } from "./HeaderMenu";

describe("HeaderMenu", () => {
  afterEach(cleanup);

  it("opens and closes from the same trigger", () => {
    render(<HeaderMenu authenticated />);
    const trigger = screen.getByRole("button", { name: "Open navigation" });

    fireEvent.click(trigger);
    expect(screen.getByRole("dialog", { name: "Navigation" })).toBeInTheDocument();

    fireEvent.pointerDown(screen.getByRole("button", { name: "Close navigation" }));
    fireEvent.click(screen.getByRole("button", { name: "Close navigation" }));
    expect(screen.queryByRole("dialog", { name: "Navigation" })).not.toBeInTheDocument();
  });
});
