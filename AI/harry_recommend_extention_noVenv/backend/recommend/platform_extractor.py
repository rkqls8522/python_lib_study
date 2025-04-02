import tldextract
from collections import Counter
import json

# 🔹 주어진 JSON 데이터
json_data = '''
[
  {
    "url": "https://chatgpt.com/c/67ec857d-f0a0-8002-8c10-778f081a5248",
    "title": "크롬 기록 리스트 변환",
    "timestamp": "2025-04-02 00:31:57"
  },
  {
    "url": "https://chatgpt.com/",
    "title": "ChatGPT",
    "timestamp": "2025-04-02 00:31:15"
  },
  {
    "url": "https://openai.com/chatgpt/overview/",
    "title": "ChatGPT | OpenAI",
    "timestamp": "2025-04-02 00:31:13"
  },
  {
    "url": "https://www.google.com/search?q=chat+gpt&oq=&gs_lcrp=EgZjaHJvbWUqCQgAEEUYOxjCAzIJCAAQRRg7GMIDMgkIARBFGDsYwgMyCQgCEEUYOxjCAzIJCAMQRRg7GMIDMgkIBBBFGDsYwgMyCQgFEEUYOxjCAzIJCAYQRRg7GMIDMgkIBxBFGDsYwgPSAQg4MjRqMGoxNagCCLACAQ&sourceid=chrome&ie=UTF-8",
    "title": "chat gpt - Google 검색",
    "timestamp": "2025-04-02 00:31:12"
  },
  {
    "url": "https://chatgpt.com/c/67eb6c3c-3c5c-8002-891e-b6f27f21f068",
    "title": "로컬 브랜치 원격 푸시",
    "timestamp": "2025-04-02 00:28:16"
  }
]
'''

# 🔹 JSON 파싱
data = json.loads(json_data)

# 🔹 2차 도메인 추출 함수
def get_second_level_domain(url):
    ext = tldextract.extract(url)
    return ext.domain  # ex: 'google', 'openai', 'chatgpt'

# 🔹 URL에서 2차 도메인만 추출하여 리스트 생성
second_level_domains = [get_second_level_domain(item["url"]) for item in data]

# 🔹 도메인별 개수 집계
domain_counts = Counter(second_level_domains)

# 🔹 결과 출력
print("2차 도메인별 등장 횟수:")
for domain, count in domain_counts.items():
    print(f"{domain}: {count}회")
