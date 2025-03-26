import time
from flask import Flask, request, jsonify
import yake

app = Flask(__name__)

def extract_keywords_yake(text):
    start_time = time.time()
    # 영어 기준으로 1-그램 단어, 상위 10개 키워드, 중복 제한 0.3
    kw_extractor = yake.KeywordExtractor(lan="en", n=1, top=10, dedupLim=0.3)
    keywords = kw_extractor.extract_keywords(text)
    # score가 낮을수록 중요하므로 정렬 후 상위 10개 추출
    sorted_keywords = sorted(keywords, key=lambda x: x[1])
    top_keywords = [kw for kw, score in sorted_keywords[:10]]
    elapsed_time = time.time() - start_time
    return top_keywords, elapsed_time

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

if __name__ == '__main__':
    app.run(debug=True)
