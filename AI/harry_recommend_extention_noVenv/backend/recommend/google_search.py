import requests

def google_search(query):
    print("=== DEBUG: Query:", query)
    
    # 구글 API 키와 Custom Search Engine ID
    api_key = 'AIzaSyDRyCoZnlPqJFHRx3NfXsOusZRefYZKZhU'
    cx = 'e2b867cad4f524704'
    
    # 요청 파라미터
    params = {
        'q': query,
        'key': api_key,
        'cx': cx,
        'num': 3,
    }
    
    # 구글 Custom Search API 요청
    response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
    
    # 상태 코드 확인
    if response.status_code != 200:
        print("=== DEBUG: Failed to fetch the search results, HTTP Status Code:", response.status_code)
        return []
    
    print("=== DEBUG: HTTP Status:", response.status_code)
    
    # JSON 응답에서 결과 추출
    search_results = response.json()
    
    results = []
    default_thumbnail = "https://thebook.io/img/080412/243.jpg"
    
    # 검색 결과에서 제목, 링크, 썸네일 이미지 추출
    if 'items' in search_results:
        for item in search_results['items']:  
            title = item.get('title')
            link = item.get('link')
            thumbnail = item.get('pagemap', {}).get('cse_thumbnail', [{}])[0].get('src')
            # 썸네일 이미지가 없으면 기본 이미지 사용
            if not thumbnail:
                thumbnail = default_thumbnail
            results.append({
                "title": title, 
                "link": link,
                "thumbnail": thumbnail
            })
    
    print("=== DEBUG: Search results count:", len(results))
    return results
