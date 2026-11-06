import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// Vitest runs without `globals`, so Testing Library's automatic cleanup is
// never registered. Without it, a test file's last rendered tree stays mounted
// and React's scheduler can fire after jsdom is torn down ("window is not
// defined", CI run 41313158728). Unmount after every test, in every file.
afterEach(() => {
  cleanup();
});
