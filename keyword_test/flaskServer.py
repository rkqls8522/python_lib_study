from flask import Flask, request, jsonify
from keybert import KeyBERT
import time

app = Flask(__name__)

# 애플리케이션 시작 시 모델 로드 (한 번만 실행)
print("KeyBERT 모델 초기화 중...")
load_start = time.time()


# kw_model = KeyBERT(model='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
kw_model = KeyBERT(model='sentence-transformers/paraphrase-MiniLM-L6-v2')
# kw_model = KeyBERT(model='distiluse-base-multilingual-cased-v2')


load_end = time.time()
print(f"KeyBERT 모델 초기화 완료 (로딩 시간: {load_end - load_start:.2f}초)")

@app.route('/extract', methods=['POST'])
def extract_keywords():
    data = request.get_json()
    # 'titles' 키로 리스트를 받도록 변경
    titles = data.get('titles', [])
    if not titles or not isinstance(titles, list):
        return jsonify({'error': 'No titles provided or titles is not a list'}), 400

    results = []
    total_start = time.time()
    for title in titles:
        start = time.time()
        keywords = kw_model.extract_keywords(title, top_n=3)
        end = time.time()
        results.append({
            'title': title,
            'keywords': keywords,
            'processing_time': f"{end - start:.2f}초"
        })
    total_end = time.time()

    return jsonify({
        'results': results,
        'total_processing_time': f"{total_end - total_start:.2f}초"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
