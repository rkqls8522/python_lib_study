import time
import re
import numpy as np
from flask import Flask, request, jsonify
from gensim.models import FastText
from rake_nltk import Rake
from konlpy.tag import Mecab

app = Flask(__name__)

def nounify(keyword):
    """
    전달받은 키워드 문자열을 Mecab으로 분석하여 명사(태그가 NN*인 부분)만 남깁니다.
    예: "청년내일채움공제가" -> "청년내일채움공제"
    """
    mecab = Mecab(dicpath='C:/mecab/mecab-ko-dic')
    pos_tags = mecab.pos(keyword)
    noun_tokens = [word for word, tag in pos_tags if tag.startswith('NN')]
    return "".join(noun_tokens) if noun_tokens else keyword

def tokenize_text(text):
    """
    원본 텍스트를 줄 단위로 나눈 후, 각 줄에서 단순 정규표현식으로 단어 토큰을 추출합니다.
    (FastText 학습 데이터를 위해 사용)
    """
    sentences = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            # 한글, 영문, 숫자 등을 포함하는 단어 추출
            tokens = re.findall(r'\w+', line)
            if tokens:
                sentences.append(tokens)
    return sentences

def extract_keywords_fasttext(text):
    """
    1. 원본 텍스트를 tokenize_text()로 토큰화하여 FastText 학습 데이터로 사용합니다.
    2. FastText 모델로 각 단어의 코사인 유사도를 계산하여 중요도 순 상위 10개 단어를 추출합니다.
    3. 추출된 각 키워드에 대해 nounify()를 적용해 명사화합니다.
    """
    start_time = time.time()
    sentences = tokenize_text(text)
    if not sentences:
        return [], 0.0

    model = FastText(sentences, vector_size=100, window=5, min_count=1, workers=1, epochs=50)
    vocab = model.wv.index_to_key

    # 2자 이상인 단어들만 고려하여 문서 평균 벡터 계산
    valid_vectors = [model.wv[word] for word in vocab if len(word) > 1]
    if not valid_vectors:
        doc_vec = np.zeros(model.vector_size)
    else:
        doc_vec = np.mean(valid_vectors, axis=0)

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

    sorted_words = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    top_words = [word for word, sim in sorted_words[:10]]
    # 3. 추출된 각 키워드를 Mecab으로 명사화
    top_words = [nounify(word) for word in top_words]
    elapsed_time = time.time() - start_time
    return top_words, elapsed_time

def extract_keywords_rake(text):
    """
    1. RAKE를 이용해 원본 텍스트에서 키워드를 추출합니다.
    2. 추출된 키워드(구절에서 단어 단위로 점수 누적) 중 상위 10개 단어를 선택합니다.
    3. 각 키워드에 대해 nounify()를 적용해 명사화합니다.
    """
    start_time = time.time()
    r = Rake()  # 기본 불용어 사전 사용
    r.extract_keywords_from_text(text)
    phrases_with_scores = r.get_ranked_phrases_with_scores()

    keyword_scores = {}
    for score, phrase in phrases_with_scores:
        # 구절 내 단어 단위로 분리
        words = re.findall(r'\w+', phrase)
        for word in words:
            word_lower = word.lower()
            keyword_scores[word_lower] = keyword_scores.get(word_lower, 0) + score

    sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
    top_keywords = [word for word, score in sorted_keywords[:10]]
    # 각 키워드에 대해 명사화 적용
    top_keywords = [nounify(word) for word in top_keywords]
    elapsed_time = time.time() - start_time
    return top_keywords, elapsed_time

@app.route('/extract_keywords_with_mecab', methods=['POST'])
def extract_keywords_api():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    text = data['text']

    result = {}

    # FastText 기반 키워드 추출 후 Mecab 명사화
    ft_keywords, ft_time = extract_keywords_fasttext(text)
    result['fasttext'] = {'keywords': ft_keywords, 'execution_time': ft_time}

    # RAKE 기반 키워드 추출 후 Mecab 명사화
    rake_keywords, rake_time = extract_keywords_rake(text)
    result['rake'] = {'keywords': rake_keywords, 'execution_time': rake_time}

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
