import requests
from bs4 import BeautifulSoup
import time

# 가져올 URL 리스트
urls = [
    "https://velog.io/@panda_love/API-Rest-Restful-Rest-API-Restful-API-%EA%B0%9C%EB%85%90%EC%B0%A8%EC%9D%B4",
    "https://nunbu.tistory.com/140",
    "https://n.news.naver.com/article/031/0000915382?cds=news_media_pc&type=editn",
    "https://m.blog.naver.com/winsweet/222150766228",
    "https://sordid-daffodil-392.notion.site/0910-09dcf02db02b4a93a57bc94e51114d81?pvs=4",
    "https://www.notion.so/0910-09dcf02db02b4a93a57bc94e51114d81",
    "https://www.facebook.com/photo/?fbid=1495213657529303&set=ecnf.100063715247289",
    "https://n.news.naver.com/article/031/0000915382?cds=news_media_pc&type=editn",
    # "https://n.news.naver.com/article/031/0000915382?cds=news_media_pc&type=editn",
    # "https://blog.naver.com/soonsblog/223791387875",
    # "https://www.instagram.com/fly_yuna/",
    # "https://job.ssafy.com/job/employmentinfo/jobinfo/jobinfoView.do"
]

headers = {"User-Agent": "Mozilla/5.0"}
start_time = time.time()
num = 0


for url in urls:
    num = num+1
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # og:image 태그 찾기
    
    og_image = soup.find("meta", property="og:image")
    if og_image and "content" in og_image.attrs:
        thumbnail_url = og_image["content"]
        print(f"{num} - Thumbnail URL for {url}: \n {thumbnail_url}")
    else:
        print(f"{num} - Not Found : No og:image meta tag found for {url} : \n https://i.namu.wiki/i/tNtmOpCy91gkISbnTiKww59h-9A9ZZ6AGvdu0W9qo17poq-RaLyAiWnGb01yuEgQQfEVjcsLkFiavIFDzHvNXI7Hc3F5lF7uitUVfXMA3YGfvFWoQrpUWlv6DAIjXQ1ukzW8VxN6PjOuuLMUi-oKbA.webp")

end_time = time.time()
total_time = end_time - start_time
print(f"\n⏱ 총 실행 시간: {total_time:.2f}초")
