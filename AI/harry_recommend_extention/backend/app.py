import requests
from flask import Flask, request, jsonify
from recommend.content_extractor import extract_main_content
from recommend.keyword_extractor import extract_keywords_yake
from recommend.google_search import google_search
from recommend.thumbnail_fetcher import get_thumbnails
from flask_cors import CORS
import time

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
@app.after_request
def after_request(response):
    # 요청이 JSON을 포함할 때, 'Content-Type' 헤더 허용
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response

@app.route('/extract_keywords', methods=['POST'])
def extract_keywords_endpoint():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    text = data['text']
    top_keywords, elapsed_time = extract_keywords_yake(text)
    result = {
        'yake': {
            'keywords': top_keywords,
            'execution_time': elapsed_time
        }
    }
    return jsonify(result)


@app.route('/recommend', methods=['POST'])
def recommend():
    start_time = time.time()  # 시작 시간 기록
    
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'No url provided'}), 400

    url = data['url']
    
    # a. 본문 텍스트 추출
    extract_start_time = time.time()
    main_text = extract_main_content(url)
    extract_elapsed_time = time.time() - extract_start_time
    print(f"본문 텍스트 추출 소요 시간: {extract_elapsed_time:.2f}초")
    
    if not main_text:
        return jsonify({'error': 'Could not extract main content'}), 400

    # b. 키워드 추출
    keyword_start_time = time.time()
    top_keywords, _ = extract_keywords_yake(main_text)
    keyword_elapsed_time = time.time() - keyword_start_time
    print(f"키워드 추출 소요 시간: {keyword_elapsed_time:.2f}초")
    
    # c. 구글 검색 실행
    search_start_time = time.time()
    query = " AND ".join(top_keywords)
    search_results = google_search(query)
    search_elapsed_time = time.time() - search_start_time
    print(f"구글 검색 소요 시간: {search_elapsed_time:.2f}초")
    
    if not search_results:
        return jsonify({'error': 'No search results found'}), 400

    # d. 썸네일 이미지 가져오기
    thumbnail_start_time = time.time()
    result_urls = [item["link"] for item in search_results]
    thumbnails = get_thumbnails(result_urls)
    thumbnail_elapsed_time = time.time() - thumbnail_start_time
    print(f"썸네일 이미지 가져오기 소요 시간: {thumbnail_elapsed_time:.2f}초")
    
    recommendations = []
    for idx, item in enumerate(search_results):
        recommendations.append({
            "title": item["title"],
            "link": item["link"],
            "thumbnail": thumbnails[idx] if idx < len(thumbnails) else ""
        })

    total_elapsed_time = time.time() - start_time
    print(f"전체 소요 시간: {total_elapsed_time:.2f}초")

    return jsonify({
        "keywords": top_keywords,
        "query": query,
        "recommendations": recommendations
    })


if __name__ == '__main__':
    app.run(debug=True)
