import time
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

# 정규표현식
import re

# YAKE 라이브러리
import yake

app = Flask(__name__)

# ----------------- 1. TF-IDF -----------------
def extract_keywords_tfidf(text):
    start_time = time.time()
    vectorizer = TfidfVectorizer(ngram_range=(1,2), stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray()[0]
    sorted_indices = scores.argsort()[::-1]
    top_keywords = [feature_names[i] for i in sorted_indices[:10]]
    elapsed_time = time.time() - start_time
    return top_keywords, elapsed_time

# ----------------- 2. RAKE -----------------
def extract_keywords_rake(text):
    start_time = time.time()
    r = Rake()  # 기본 불용어 사전 사용
    r.extract_keywords_from_text(text)
    phrases_with_scores = r.get_ranked_phrases_with_scores()
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

# ----------------- 3. TextRank -----------------
def extract_keywords_textrank(text):
    start_time = time.time()
    try:
        keywords_list = summa_keywords(text, words=10, split=True)
        if not keywords_list:
            keywords_list = summa_keywords(text, ratio=1.0, split=True)
    except Exception as e:
        keywords_list = []
    elapsed_time = time.time() - start_time
    return keywords_list, elapsed_time

# ----------------- 4. Word2Vec -----------------
def extract_keywords_word2vec(text):
    start_time = time.time()
    sentences = [sentence.split() for sentence in text.splitlines() if sentence.strip()]
    if not sentences:
        return [], 0.0
    model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=1, epochs=50)
    vocab = model.wv.index_to_key
    valid_vectors = [model.wv[word] for word in vocab if word.isalpha() and len(word) > 1]
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
        if not word.isalpha() or len(word) <= 1:
            continue
        sim = cosine_similarity(model.wv[word], doc_vec)
        similarities[word] = sim
    sorted_words = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    top_words = [word for word, sim in sorted_words[:10]]
    elapsed_time = time.time() - start_time
    return top_words, elapsed_time

# ----------------- 5. FastText -----------------
def extract_keywords_fasttext(text):
    start_time = time.time()
    sentences = [sentence.split() for sentence in text.splitlines() if sentence.strip()]
    if not sentences:
        return [], 0.0
    model = FastText(sentences, vector_size=100, window=5, min_count=1, workers=1, epochs=50)
    vocab = model.wv.index_to_key
    valid_vectors = [model.wv[word] for word in vocab if word.isalpha() and len(word) > 1]
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
        if not word.isalpha() or len(word) <= 1:
            continue
        sim = cosine_similarity(model.wv[word], doc_vec)
        similarities[word] = sim
    sorted_words = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    top_words = [word for word, sim in sorted_words[:10]]
    elapsed_time = time.time() - start_time
    return top_words, elapsed_time

# ----------------- 6. YAKE (English) -----------------
def extract_keywords_yake(text):
    start_time = time.time()
    kw_extractor = yake.KeywordExtractor(lan="en", n=1, top=10, dedupLim=0.3)
    keywords = kw_extractor.extract_keywords(text)
    sorted_keywords = sorted(keywords, key=lambda x: x[1])
    top_keywords = [kw for kw, score in sorted_keywords[:10]]
    elapsed_time = time.time() - start_time
    return top_keywords, elapsed_time

# ----------------- 7. YAKE (영어+한국어) -----------------
def extract_keywords_yake_en_ko(text):
    start_time = time.time()
    kw_extractor_en = yake.KeywordExtractor(lan="en", n=1, top=10, dedupLim=0.3)
    keywords_en = kw_extractor_en.extract_keywords(text)
    sorted_keywords_en = sorted(keywords_en, key=lambda x: x[1])
    top_keywords_en = [kw for kw, score in sorted_keywords_en[:10]]
    
    kw_extractor_ko = yake.KeywordExtractor(lan="ko", n=1, top=10, dedupLim=0.3)
    keywords_ko = kw_extractor_ko.extract_keywords(text)
    sorted_keywords_ko = sorted(keywords_ko, key=lambda x: x[1])
    top_keywords_ko = [kw for kw, score in sorted_keywords_ko[:10]]
    
    elapsed_time = time.time() - start_time
    return {'en': top_keywords_en, 'ko': top_keywords_ko}, elapsed_time

# ----------------- 8. YAKE (Multi-language) -----------------
def extract_keywords_yake_multi(text):
    start_time = time.time()
    kw_extractor = yake.KeywordExtractor(lan="multi", n=1, top=10, dedupLim=0.3)
    keywords = kw_extractor.extract_keywords(text)
    sorted_keywords = sorted(keywords, key=lambda x: x[1])
    top_keywords = [kw for kw, score in sorted_keywords[:10]]
    elapsed_time = time.time() - start_time
    return top_keywords, elapsed_time

# ----------------- Flask API Endpoint -----------------
@app.route('/extract_keywords', methods=['POST'])
def extract_keywords_endpoint():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    result = {}
    
    tfidf_keywords, tfidf_time = extract_keywords_tfidf(text)
    result['tfidf'] = {'keywords': tfidf_keywords, 'execution_time': tfidf_time}
    
    rake_keywords, rake_time = extract_keywords_rake(text)
    result['rake'] = {'keywords': rake_keywords, 'execution_time': rake_time}
    
    textrank_keywords, textrank_time = extract_keywords_textrank(text)
    result['textrank'] = {'keywords': textrank_keywords, 'execution_time': textrank_time}
    
    word2vec_keywords, word2vec_time = extract_keywords_word2vec(text)
    result['word2vec'] = {'keywords': word2vec_keywords, 'execution_time': word2vec_time}
    
    fasttext_keywords, fasttext_time = extract_keywords_fasttext(text)
    result['fasttext'] = {'keywords': fasttext_keywords, 'execution_time': fasttext_time}
    
    yake_en_keywords, yake_en_time = extract_keywords_yake(text)
    result['yake_en'] = {'keywords': yake_en_keywords, 'execution_time': yake_en_time}
    
    yake_en_ko_keywords, yake_en_ko_time = extract_keywords_yake_en_ko(text)
    result['yake_en_ko'] = {'keywords': yake_en_ko_keywords, 'execution_time': yake_en_ko_time}
    
    yake_multi_keywords, yake_multi_time = extract_keywords_yake_multi(text)
    result['yake_multi'] = {'keywords': yake_multi_keywords, 'execution_time': yake_multi_time}

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
