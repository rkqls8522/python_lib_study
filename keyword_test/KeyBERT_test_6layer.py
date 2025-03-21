from keybert import KeyBERT
import time

load_start = time.time()
print("KeyBERT 모델 초기화 중...")

# KeyBERT 모델 초기화 (다국어 지원 모델 사용)
kw_model = KeyBERT(model='distiluse-base-multilingual-cased-v2')

load_end = time.time()
print(f"KeyBERT 모델 초기화 완료 (로딩 시간: {load_end - load_start:.2f}초)\n")

extract_start = time.time()

title = "사용자 히스토리에서 키워드 추출하는 모델들 성능 비교&분석"

keywords = kw_model.extract_keywords(title, top_n=3)
print(f"제목: {title}")
print("키워드:", keywords)

extract_end = time.time()
print(f"\n전체 문장 처리 시간: {extract_end - extract_start:.2f}초")
