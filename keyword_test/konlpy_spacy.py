import yake
import spacy
from konlpy.tag import Okt
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

# 1️⃣ 한국어 & 영어 전처리 (형태소 분석)
okt = Okt()
nlp = spacy.load("en_core_web_sm")

def extract_nouns(text):
    """한국어 & 영어 명사 추출"""
    # 한국어 명사 추출
    korean_nouns = okt.nouns(text)
    
    # 영어 명사 추출
    doc = nlp(text)
    english_nouns = [token.text for token in doc if token.pos_ == "NOUN"]
    
    return korean_nouns + english_nouns

# 2️⃣ 문장에서 키워드 추출
kw_extractor = yake.KeywordExtractor(lan="en", n=2, top=10)

def extract_keywords(text):
    keywords = kw_extractor.extract_keywords(text)
    return [word for word, score in keywords]

# 3️⃣ TF-IDF 기반 중요도 평가
def compute_tfidf(texts):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray().sum(axis=0)
    
    return {feature_names[i]: scores[i] for i in range(len(feature_names))}

# 4️⃣ 테스트 문장 (한국어 + 영어 혼합)
texts = [
    "인공지능(AI)이 미래를 변화시키고 있다. AI is transforming the future of technology.",
    "자연어 처리는 매우 중요하다. NLP is essential for machine learning applications.",
    "Python과 TensorFlow를 사용하여 딥러닝 모델을 개발할 수 있다."
]

# 5️⃣ 명사 추출 & 키워드 평가
all_nouns = []
for text in texts:
    nouns = extract_nouns(text)
    keywords = extract_keywords(text)
    all_nouns.append(" ".join(nouns + keywords))  # 명사 + 키워드 결합

# 6️⃣ TF-IDF 점수 계산
tfidf_scores = compute_tfidf(all_nouns)

# 7️⃣ 결과 출력
sorted_keywords = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)
for word, score in sorted_keywords[:10]:  # 상위 10개 키워드
    print(f"{word}: {score:.4f}")
