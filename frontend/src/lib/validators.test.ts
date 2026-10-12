import { describe, it, expect } from "vitest";
import { isValidEmail, passwordStrength } from "@/lib/validators";

describe("validators", () => {
  it("validates email", () => {
    expect(isValidEmail("a@b.com")).toBe(true);
    expect(isValidEmail("bad")).toBe(false);
  });
  it("scores password strength", () => {
    expect(passwordStrength("short")).toBe(0);
    expect(passwordStrength("longpass1!")).toBeGreaterThanOrEqual(3);
  });
});
