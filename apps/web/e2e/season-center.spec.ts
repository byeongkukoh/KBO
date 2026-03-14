import { expect, test } from "@playwright/test";

test("renders seeded standings and player records", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByText(/시즌 팀 순위/)).toBeVisible();
  await expect(page.getByRole("heading", { name: "삼성 라이온즈" })).toBeVisible();
  await expect(page.getByRole("button", { name: "선수 기록" })).toBeVisible();

  await page.getByRole("button", { name: "선수 기록" }).click();

  await expect(page.getByText("타자 Top 5")).toBeVisible();
  await expect(page.getByText("평균자책점")).toBeVisible();

  await page.getByRole("button", { name: "전체 보기" }).click();

  await expect(page.getByText("전체 선수 기록")).toBeVisible();
  await page.getByRole("button", { name: "투수" }).click();
  await expect(page.getByText("원태인")).toBeVisible();
});
