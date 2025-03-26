import time
import re
import numpy as np
from flask import Flask, request, jsonify
from gensim.models import FastText
from rake_nltk import Rake
from konlpy.tag import Mecab

app = Flask(__name__)

# ----------------- 1. Mecab을 이용한 형태소 전처리 -----------------
def preprocess_text_with_mecab(text):
    """
    텍스트를 줄 단위로 분리한 후, 각 줄에서 Mecab으로 형태소 분석을 수행합니다.
    조사나 불필요한 품사는 제거하고, 주로 명사(NNG, NNP 등)만 추출합니다.
    반환: 각 문장을 토큰 리스트로 구성한 리스트
    """
    mecab = Mecab(dicpath='C:/mecab/mecab-ko-dic')
    sentences = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            tokens = []
            pos_tags = mecab.pos(line)
            for word, tag in pos_tags:
                if tag.startswith('NN'):
                    tokens.append(word)
            if tokens:
                sentences.append(tokens)
    return sentences

# ----------------- 2. FastText를 이용한 키워드 추출 (Mecab 전처리 사용) -----------------
def extract_keywords_fasttext_with_mecab(text):
    start_time = time.time()
    # Mecab을 이용한 전처리: 각 문장을 명사 토큰 리스트로 변환
    sentences = preprocess_text_with_mecab(text)
    if not sentences:
        return [], 0.0
    
    # FastText 모델 학습 (전처리된 토큰 리스트 사용)
    model = FastText(sentences, vector_size=100, window=5, min_count=1, workers=1, epochs=50)
    vocab = model.wv.index_to_key

    # 길이가 2자 이상인 단어들의 벡터를 이용해 문서 평균 벡터 계산
    valid_vectors = [model.wv[word] for word in vocab if len(word) > 1]
    if not valid_vectors:
        doc_vec = np.zeros(model.vector_size)
    else:
        doc_vec = np.mean(valid_vectors, axis=0)
    
    # 코사인 유사도 계산 함수
    def cosine_similarity(vec1, vec2):
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0
        return np.dot(vec1, vec2) / (norm1 * norm2)
    
    similarities = {}
    for word in vocab:
        if len(word) <= 1:
            continue
        sim = cosine_similarity(model.wv[word], doc_vec)
        similarities[word] = sim
    
    # 유사도가 높은 순으로 정렬하여 상위 10개 단어 선택
    sorted_words = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    top_words = [word for word, sim in sorted_words[:10]]
    elapsed_time = time.time() - start_time
    return top_words, elapsed_time

# ----------------- 3. RAKE를 이용한 키워드 추출 (원본 텍스트 사용) -----------------
def extract_keywords_rake(text):
    start_time = time.time()
    r = Rake()  # 기본 불용어 사전 사용
    r.extract_keywords_from_text(text)
    phrases_with_scores = r.get_ranked_phrases_with_scores()
    
    # 각 구에서 단어별 점수를 누적
    keyword_scores = {}
    for score, phrase in phrases_with_scores:
        words = re.findall(r'\b\w+\b', phrase)
        for word in words:
            word_lower = word.lower()
            keyword_scores[word_lower] = keyword_scores.get(word_lower, 0) + score
    sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
    top_keywords = [word for word, score in sorted_keywords[:10]]
    elapsed_time = time.time() - start_time
    return top_keywords, elapsed_time

# ----------------- 4. Flask API Endpoint -----------------
@app.route('/extract_keywords_with_mecab', methods=['POST'])
def extract_keywords():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    text = data['text']
    
    result = {}
    
    # FastText (Mecab 전처리 사용)로 추출한 키워드
    ft_keywords, ft_time = extract_keywords_fasttext_with_mecab(text)
    result['fasttext'] = {'keywords': ft_keywords, 'execution_time': ft_time}
    
    # RAKE로 추출한 키워드
    rake_keywords, rake_time = extract_keywords_rake(text)
    result['rake'] = {'keywords': rake_keywords, 'execution_time': rake_time}
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
