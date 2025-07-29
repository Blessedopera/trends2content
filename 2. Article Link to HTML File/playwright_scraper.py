import asyncio
from playwright.async_api import async_playwright
from markdown2 import markdown
import html2text

async def scrape_article(url: str, output_html_file="article_output.html"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set to True to hide browser
        page = await browser.new_page(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ))

        print(f"🌐 Navigating to: {url}")
        await page.goto(url, wait_until='networkidle')
        await page.wait_for_timeout(3000)  # Wait for JS to load

        html_content = await page.content()
        await browser.close()

        # Convert to Markdown then styled HTML
        markdown_text = html2text.html2text(html_content)
        readable_html = markdown(markdown_text)

        with open(output_html_file, "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Scraped Article</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; padding: 2rem; max-width: 800px; margin: auto; }}
        h1, h2, h3 {{ color: #222; }}
        pre, code {{ background: #f4f4f4; padding: 0.5em; border-radius: 5px; overflow-x: auto; display: block; }}
    </style>
</head>
<body>
{readable_html}
</body>
</html>""")

        print(f"✅ Saved readable article to: {output_html_file}")

# Run the async function
if __name__ == "__main__":
    url = "https://www.webpronews.com/julius-ai-raises-10m-seed-funding-for-ai-data-analysis-platform/"
    asyncio.run(scrape_article(url))
