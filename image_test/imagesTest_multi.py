import requests
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor

# 가져올 URL 리스트
urls = [
    "https://velog.io/@panda_love/API-Rest-Restful-Rest-API-Restful-API-%EA%B0%9C%EB%85%90%EC%B0%A8%EC%9D%B4",
    "https://velog.io/@panda_love/API-Rest-Restful-Rest-API-Restful-API-%EA%B0%9C%EB%85%90%EC%B0%A8%EC%9D%B4",
    "https://nunbu.tistory.com/140",
    "https://n.news.naver.com/article/031/0000915382?cds=news_media_pc&type=editn",
    "https://m.blog.naver.com/winsweet/222150766228",
    "https://sordid-daffodil-392.notion.site/0910-09dcf02db02b4a93a57bc94e51114d81?pvs=4",
    "https://www.notion.so/0910-09dcf02db02b4a93a57bc94e51114d81",
    "https://www.facebook.com/photo/?fbid=1495213657529303&set=ecnf.100063715247289",
    "https://n.news.naver.com/article/031/0000915382?cds=news_media_pc&type=editn",
    "https://blog.naver.com/soonsblog/223791387875",
    "https://www.instagram.com/fly_yuna/",
    "https://job.ssafy.com/job/employmentinfo/jobinfo/jobinfoView.do"
]

headers = {"User-Agent": "Mozilla/5.0"}

# 실행 시간 측정 시작
start_time = time.time()

# 페이지 크롤링 함수 정의
def fetch_og_image(url, num):
    try:
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        # og:image 태그 찾기
        og_image = soup.find("meta", property="og:image")
        if og_image and "content" in og_image.attrs:
            thumbnail_url = og_image["content"]
            print(f"{num} - Thumbnail URL for {url}: \n {thumbnail_url}")
        else:
            print(f"{num} - Not Found : No og:image meta tag found for {url}")
    except requests.RequestException as e:
        print(f"{num} - Error fetching {url}: {e}")

# 멀티스레딩 실행 (최대 8개 스레드 동시 실행)
with ThreadPoolExecutor(max_workers=8) as executor:
    executor.map(fetch_og_image, urls, range(1, len(urls) + 1))

# 실행 시간 측정 종료
end_time = time.time()

# 총 실행 시간 출력
total_time = end_time - start_time
print(f"\n⏱ 총 실행 시간: {total_time:.2f}초")
