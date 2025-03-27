import asyncio
import aiohttp
from bs4 import BeautifulSoup

headers_async = {"User-Agent": "Mozilla/5.0"}

async def fetch_thumbnail(session, url):
    try:
        async with session.get(url, headers=headers_async, timeout=5) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                return og_image["content"]
            else:
                return "https://thebook.io/img/080412/243.jpg"
    except Exception as e:
        return "https://thebook.io/img/080412/243.jpg"

def get_thumbnails(urls):
    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_thumbnail(session, url) for url in urls]
            return await asyncio.gather(*tasks)
    return asyncio.run(main())
