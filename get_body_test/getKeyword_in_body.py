from flask import Flask, request, jsonify

# TF-IDF 관련 라이브러리
from sklearn.feature_extraction.text import TfidfVectorizer

# RAKE 관련 라이브러리
from rake_nltk import Rake

# TextRank: summa의 keywords 함수를 활용 (텍스트 요약 기반)
from summa import keywords as summa_keywords

# Word2Vec, FastText 관련 라이브러리 (gensim 사용)
from gensim.models import Word2Vec, FastText
import numpy as np

# YAKE 라이브러리
import yake

app = Flask(__name__)

# ----------------- 1. TF-IDF -----------------
def extract_keywords_tfidf(text):
    """
    TF-IDF를 이용하여 단일 문서(텍스트) 내에서 키워드 상위 5개를 추출.
    (단일 문서에서는 idf가 모두 동일하게 나오므로, 실질적으로는 단순 빈도 기반의 효과를 가짐짐.)
    """
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray()[0]
    sorted_indices = scores.argsort()[::-1]
    top_keywords = [feature_names[i] for i in sorted_indices[:5]]
    return top_keywords

# ----------------- 2. RAKE -----------------
def extract_keywords_rake(text):
    """
    RAKE는 불용어와 구두점을 기준으로 문장을 분할하여 후보 구를 생성하고, 각 후보에 점수를 부여.
    여기서는 상위 5개의 구를 반환.
    """
    r = Rake()  # 기본 불용어 사전 사용
    r.extract_keywords_from_text(text)
    phrases = r.get_ranked_phrases()
    return phrases[:5]

# ----------------- 3. TextRank -----------------
def extract_keywords_textrank(text):
    """
    summa의 keywords 함수를 사용하여 TextRank 기반으로 키워드를 추출.
    """
    try:
        keywords_list = summa_keywords(text, words=5, split=True)
    except Exception as e:
        keywords_list = []
    return keywords_list

# ----------------- 4. Word2Vec -----------------
def extract_keywords_word2vec(text):
    """
    Word2Vec은 문장 내 단어들을 임베딩한 후,
    전체 문서 벡터(모든 단어 벡터의 평균)와의 코사인 유사도를 기준으로
    각 단어의 중요도를 산정하는 방식으로 키워드를 추출.
    (여기서는 단순한 예제로 문장을 '.' 기준으로 분리하여 학습.)
    """
    sentences = [sentence.split() for sentence in text.split('.') if sentence.strip()]
    if not sentences:
        return []
    model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=1, epochs=50)
    vocab = model.wv.index_to_key
    doc_vec = np.mean([model.wv[word] for word in vocab], axis=0)

    def cosine_similarity(vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    similarities = {}
    for word in vocab:
        sim = cosine_similarity(model.wv[word], doc_vec)
        similarities[word] = sim
    sorted_words = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    top_words = [word for word, sim in sorted_words[:5]]
    return top_words

# ----------------- 5. FastText -----------------
def extract_keywords_fasttext(text):
    """
    FastText는 Word2Vec과 유사하게 동작하지만, n-gram 정보를 활용하여 단어 형태 변화를 더 잘 포착합니다.
    Word2Vec과 동일한 방식으로 전체 문서 벡터와의 유사도를 계산해 상위 5개 단어를 반환.
    """
    sentences = [sentence.split() for sentence in text.split('.') if sentence.strip()]
    if not sentences:
        return []
    model = FastText(sentences, vector_size=100, window=5, min_count=1, workers=1, epochs=50)
    vocab = model.wv.index_to_key
    doc_vec = np.mean([model.wv[word] for word in vocab], axis=0)
    
    def cosine_similarity(vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    similarities = {}
    for word in vocab:
        sim = cosine_similarity(model.wv[word], doc_vec)
        similarities[word] = sim
    sorted_words = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    top_words = [word for word, sim in sorted_words[:5]]
    return top_words

# ----------------- 6. YAKE -----------------
def extract_keywords_yake(text):
    """
    YAKE는 단일 문서 내 통계적 특징(단어 위치, 주변 단어 등)을 고려하여 키워드를 추출.
    일단 언어 옵션을 "en"으로 지정..
    """
    kw_extractor = yake.KeywordExtractor(lan="en", n=1, top=5)
    keywords = kw_extractor.extract_keywords(text)
    sorted_keywords = sorted(keywords, key=lambda x: x[1])
    top_keywords = [kw for kw, score in sorted_keywords[:5]]
    return top_keywords

# ----------------- Flask API Endpoint -----------------
@app.route('/extract_keywords', methods=['POST'])
def extract_keywords():
    """
    POST 요청 시 JSON 본문에서 "text" 필드에 해당하는 텍스트를 받아,
    6가지 방법으로 각각 중요 키워드 10개씩을 추출하여 JSON 형태로 반환.
    """
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    result = {
        'tfidf': extract_keywords_tfidf(text),
        'rake': extract_keywords_rake(text),
        'textrank': extract_keywords_textrank(text),
        'word2vec': extract_keywords_word2vec(text),
        'fasttext': extract_keywords_fasttext(text),
        'yake': extract_keywords_yake(text)
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
