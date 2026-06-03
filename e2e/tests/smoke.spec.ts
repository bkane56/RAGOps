import { test, expect } from "@playwright/test";

test("overview page loads", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "RAGOps Platform" })).toBeVisible();
});

test("navigation links exist", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("link", { name: "Documents" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Ask" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Compare" })).toBeVisible();
});

test("ask page has question input", async ({ page }) => {
  await page.goto("/ask");
  await expect(page.getByTestId("question-input")).toBeVisible();
});
