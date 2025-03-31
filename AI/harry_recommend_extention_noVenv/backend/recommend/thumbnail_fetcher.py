import aiohttp
import asyncio
from bs4 import BeautifulSoup

headers_async = {"User-Agent": "Mozilla/5.0"}

async def fetch_thumbnail(session, url):
    try:
        async with session.get(url, headers=headers_async, timeout=5) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                image_url = og_image["content"]
                # URL이 '//'로 시작하면 'https:'를 붙여 절대 URL로 만듦
                if image_url.startswith("//"):
                    image_url = "https:" + image_url
                return image_url
            else:
                return "https://thebook.io/img/080412/243.jpg"
    except Exception as e:
        return "https://thebook.io/img/080412/243.jpg"

# get_thumbnails를 async 함수로 변경
async def get_thumbnails(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_thumbnail(session, url) for url in urls]
        return await asyncio.gather(*tasks)
