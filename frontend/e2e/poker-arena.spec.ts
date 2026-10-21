import { expect, test, type Page } from "@playwright/test";

async function playUntilFinished(page: Page) {
  let capturedFlop = false;
  for (let turn = 0; turn < 80; turn += 1) {
    if (await page.getByRole("button", { name: "Next hand" }).count()) return;
    const action = page.getByRole("button", { name: /Check|Call/ }).first();
    if (await action.count() && await action.isEnabled()) {
      await action.click();
    } else {
      const raise = page.getByRole("button", { name: /Bet \/ Raise/ });
      const fold = page.getByRole("button", { name: /Fold/ });
      if (await raise.count() && await raise.isEnabled()) await raise.click();
      else if (await fold.count() && await fold.isEnabled()) await fold.click();
      else await page.waitForTimeout(350);
    }
    await page.waitForTimeout(350);
    if (!capturedFlop && await page.locator(".board-cards .playing-card").count() >= 3) {
      await page.screenshot({ path: `test-results/arena-${await page.evaluate(() => innerWidth)}-flop.png`, fullPage: true });
      capturedFlop = true;
    }
  }
  await expect(page.getByRole("button", { name: "Next hand" })).toBeVisible();
}

test("plays a complete hand at desktop and mobile sizes", async ({ page }) => {
  for (const viewport of [{ width: 1280, height: 800 }, { width: 390, height: 844 }]) {
    await page.setViewportSize(viewport);
    await page.goto("/arena");
    await expect(page.getByRole("region", { name: "Poker Arena" })).toBeVisible();
    await expect(page.locator(".poker-seat")).toHaveCount(3);
    await expect(page.locator(".card-back")).toHaveCount(4);
    await expect(page.locator("svg.card-face")).toHaveCount(2);
    await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
    await page.screenshot({ path: `test-results/arena-${viewport.width}-preflop.png`, fullPage: true });
    await playUntilFinished(page);
    await expect(page.locator('[aria-label="Showdown result"]')).toBeVisible();
    await expect(page.locator(".showdown-panel")).toBeVisible();
    await page.screenshot({ path: `test-results/arena-${viewport.width}-showdown.png`, fullPage: true });
  }
});

test("keeps all seats inside the responsive table at requested widths", async ({ page }) => {
  for (const viewport of [{ width: 390, height: 844 }, { width: 768, height: 1024 }, { width: 1280, height: 800 }, { width: 1920, height: 1080 }]) {
    await page.setViewportSize(viewport);
    await page.goto("/arena");
    await page.getByLabel("Players").selectOption("9");
    await expect(page.locator(".poker-seat")).toHaveCount(9);
    const geometry = await page.locator(".poker-seat").evaluateAll((elements) => elements.map((element) => {
      const box = element.getBoundingClientRect();
      return { left: box.left, right: box.right, top: box.top, bottom: box.bottom };
    }));
    expect(geometry.every((box) => box.left >= 0 && box.right <= viewport.width && box.top >= 0)).toBe(true);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
  }
});

test("captures an all-in resolution at desktop and mobile sizes", async ({ page }) => {
  for (const viewport of [{ width: 1280, height: 800 }, { width: 390, height: 844 }]) {
    await page.setViewportSize(viewport);
    await page.goto("/arena");
    const allIn = page.locator("button.action-all-in");
    await expect(allIn).toBeEnabled();
    await allIn.click();
    await expect(page.getByRole("button", { name: "Next hand" })).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: `test-results/arena-${viewport.width}-all-in.png`, fullPage: true });
  }
});
