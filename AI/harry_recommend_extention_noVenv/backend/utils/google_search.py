import requests
import urllib.parse

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
    
    # 검색 결과에서 링크와 제목을 추출합니다.
    if 'items' in search_results:
        for item in search_results['items'][:3]:  # 최대 3개의 검색 결과만 추출
            title = item['title']
            link = item['link']
            results.append({"title": title, "link": link})
    
    print("=== DEBUG: Search results count:", len(results))
    return results
