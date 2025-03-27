import requests
from bs4 import BeautifulSoup

def extract_main_content(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    print("=== DEBUG: HTTP Status:", res.status_code)
    print("=== DEBUG: Response length:", len(res.text))
    
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 제거할 태그 (광고, 스크립트, 메뉴 등)
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        tag.decompose()
    
    candidates = soup.find_all(['article', 'section', 'div', 'main'])
    print("=== DEBUG: Found candidates count:", len(candidates))
    
    main_text = ''
    max_len = 0
    for tag in candidates:
        text = tag.get_text(separator='\n', strip=True)
        if len(text) > max_len:
            main_text = text
            max_len = len(text)
    
    print("=== DEBUG: Extracted main_text length:", len(main_text))
    return main_text
