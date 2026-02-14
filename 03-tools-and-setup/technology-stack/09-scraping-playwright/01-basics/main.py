import asyncio
from typing import Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

URL: str = "https://example.com"
SCREENSHOT_PATH: str = "screenshots/example.png"

async def run_session(headless: bool) -> None:
    # Browser adalah proses besar; kita isolasi sesi via context agar state (cookies, storage)
    # tidak bocor antar run dan lebih mudah diulang secara deterministik.
    async with async_playwright() as p:
        browser: Browser = await p.chromium.launch(headless=headless)
        context: BrowserContext = await browser.new_context()
        page: Page = await context.new_page()

        await page.goto(URL, wait_until="domcontentloaded")
        title: str = await page.title()
        print(f"Title (headless={headless}): {title}")

        await page.screenshot(path=SCREENSHOT_PATH, full_page=True)

        # Locator bersifat lazy dan auto-waiting; lebih stabil untuk elemen dinamis.
        heading_locator = page.locator("h1")
        heading_text: Optional[str] = await heading_locator.first.text_content()
        print(f"H1 (headless={headless}): {heading_text}")

        # Selalu tutup context dan browser untuk melepas resource OS.
        await context.close()
        await browser.close()

async def main() -> None:
    # Demo headless=True dan headless=False untuk melihat perbedaan perilaku UI.
    await run_session(headless=True)
    await run_session(headless=False)

if __name__ == "__main__":
    asyncio.run(main())
