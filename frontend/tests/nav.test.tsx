import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { Nav } from "@/components/layout/Nav";

vi.mock("next/navigation", () => ({
  usePathname: () => "/ask",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

describe("Nav", () => {
  it("renders navigation links", () => {
    render(<Nav />);
    expect(screen.getByText("RAGOps")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Ask" })).toHaveAttribute("href", "/ask");
    expect(screen.getByRole("link", { name: "Documents" })).toHaveAttribute("href", "/documents");
  });
});
