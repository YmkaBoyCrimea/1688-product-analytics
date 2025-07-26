
import asyncio
from playwright.async_api import async_playwright
import gspread
from oauth2client.service_account import ServiceAccountCredentials

KEY_PATH = "ymka-467019-ff08c5919879.json"
SPREADSHEET_NAME = "1688 Product Analytics"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_PATH, scope)
client = gspread.authorize(credentials)
worksheet = client.open(SPREADSHEET_NAME).sheet1

async def fetch_product_data(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)

        try:
            title = await page.locator('meta[name="keywords"]').get_attribute("content")
        except:
            title = "не найдено"

        try:
            price_text = await page.locator('.price').all_inner_texts()
            if price_text:
                price = price_text[0].strip().replace("¥", "").split("-")[0]
            else:
                price = "не найдено"
        except:
            price = "не найдено"

        try:
            image_url = await page.locator('img[data-spm-click]').first.get_attribute("src")
            if image_url and image_url.startswith("//"):
                image_url = "https:" + image_url
        except:
            image_url = "не найдено"

        await browser.close()
        return title, price, image_url

async def process_sheet():
    records = worksheet.get_all_records()
    for i, row in enumerate(records, start=2):
        url = row.get("Ссылка на товар")
        if not url:
            continue

        print(f"🔄 Обработка строки {i} — {url}")
        title, price, image_url = await fetch_product_data(url)
        worksheet.update_cell(i, 2, title)
        worksheet.update_cell(i, 3, image_url)
        worksheet.update_cell(i, 4, price)

if __name__ == "__main__":
    asyncio.run(process_sheet())
