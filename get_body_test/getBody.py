import requests
from bs4 import BeautifulSoup

def extract_main_content(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 제거할 태그 (광고, 스크립트, 메뉴 등)
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        tag.decompose()

    # 텍스트 덩어리가 많이 들어갈 만한 태그들만 추림
    candidates = soup.find_all(['article', 'section', 'div', 'main'])

    # 가장 긴 텍스트 가진 블럭을 본문으로 판단
    main_text = ''
    max_len = 0

    for tag in candidates:
        text = tag.get_text(separator='\n', strip=True)
        # print("현재 보고 있는 텍스트")
        # print(text)
        # print("\n")
        if len(text) > max_len:
            main_text = text
            max_len = len(text)

    return main_text

# 사용 예시
url = "https://velog.io/@panda_love/API-Rest-Restful-Rest-API-Restful-API-%EA%B0%9C%EB%85%90%EC%B0%A8%EC%9D%B4"
main_content = extract_main_content(url)
# print(main_content[:1000])  # 길면 앞 1000자만 출력
print(main_content)
