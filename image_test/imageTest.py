import requests
from bs4 import BeautifulSoup

url = "https://velog.io/@panda_love/API-Rest-Restful-Rest-API-Restful-API-%EA%B0%9C%EB%85%90%EC%B0%A8%EC%9D%B4"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

og_image = soup.find("meta", property="og:image")
if og_image:
    thumbnail_url = og_image["content"]
    print("Thumbnail URL:", thumbnail_url)
else:
    print("No og:image meta tag found.")
