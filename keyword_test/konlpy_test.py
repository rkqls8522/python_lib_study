from konlpy.tag import Okt #형태소 분석기
from collections import Counter # 키워드 카운트 세기
import re # 정규표현식
import time

# 테스트용 방문기록 리스트
visit_titles = [
    "운영체제 및 메모리 관리",
    "개발자 포트폴리오 제작법",
    "이력",
    "할 일",
    "노션 200% 활용법: 노션 포트폴리오 도전기 | 요즘IT",
    "챗GPT로 PPT 10배 빠르게 만들기 (feat. Gamma) | 요즘IT",
    "panda_love (Aurora) / 작성글 - velog",
    "Emoji Homepage 👀 - Copy and paste emoji. 💨 Fast and 👌 Simple.",
    "경력 정리 도움",
    "홍광호(Aurora)의 포트폴리오",
    "Framer",
    "헤이링 서비스 설명",
    "(1) 사방팔방",
    "테스트 인프라 구축 4. 자바 애플리케이션 모니터링 및 테스트 도구 설정",
     "마음이 조급한 5시간 브금 - YouTube",
    "ID",
    "사방팔방 – Figma",
    "사방팔방 – Figma",
    "사방팔방 – Figma",
    "사방팔방 – Figma",
    "Figma",
    "인프라 도커 자바 - Google 검색",
    "Google 고급검색",
    "인프라 도커 자바 - Google 검색",
    "인프라 도커 자바 - Google 검색",
    "특화 프로젝트.미정",
    "사용자 히스토리에서 키워드 추출하는 모델들 성능 비교&분석",
    "사용자 히스토리에서 키워드 추출하는 모델들 성능 비교&분석",
    "(1) 요구사항 명세서",
    "요구사항 명세서",
    "방문기록 제목 정리",
    "테스트 인프라 구축 4. 자바 애플리케이션 모니터링 및 테스트 도구 설정",
    "인프라 자바 도커 - Google 검색",
    "ChatGPT",
    "Semi-BookMark Manager",
    "특화 프로젝트.미정",
    "SSAFY_1학기 강의 노트 | 전체 보기",
    "출석현황 목록",
    "삼성 청년 SW 아카데미",
    "홍광호진료확인서.pdf",
    "홍광호님 진료 확인서 보내드립니다.",
    "받은메일함(2768) : 네이버 메일",
    "[토익&토익Speaking] '다행히도 4시부터 4시 30분까지가 자유 시간입니다.'의 영어표현은?",
    "내게쓴메일함(6) : 네이버 메일",
    "Redis DB 특징과 사용법",
    "KoNLPy 라이브러리 설명",
    "[SSAFY취업지원센터] 다대다 온/오프 모의면접 컨설팅 신청(25년 3월 24일~26일)",
    "(101) CarShop프로젝트 시연 - YouTube",
    "최종관통 - 프레젠테이션 - Canva",
    "[SSAFY] IT포트폴리오 실습 양식(타이틀 입력하기!)"
]

start_time = time.time()


# 불필요한 단어 리스트 (조사, 일반적인 단어 등)
stopwords = {"및", "이력", "할 일", "작성글", "홈페이지", "설명", "도움", "서비스"}

# KoNLPy Okt 형태소 분석기 초기화. 명사만 추출할 것임.
okt = Okt()

# 명사 추출 함수
def extract_keywords(titles):
    all_nouns = [] # 명사 저장할 리스트
    
    for title in titles:
        title = re.sub(r"[^가-힣a-zA-Z0-9\s]", "", title)  # 특수문자 제거
        nouns = okt.nouns(title)  # 명사 추출
        filtered_nouns = [n for n in nouns if n not in stopwords and len(n) > 1]  # 불필요한 단어 제거
        all_nouns.extend(filtered_nouns)
    
    return Counter(all_nouns)

# 키워드 분석 실행
keyword_counts = extract_keywords(visit_titles)

# 상위 10개 키워드 출력
print("방문기록에서 추출된 주요 키워드 TOP :")
for word, count in keyword_counts.most_common():# 정렬해서 보여주겠다.
    print(f"- {word}: {count}회")

# visit_titles의 사이즈

end_time = time.time()
total_time = end_time - start_time
print(f"\n⏱ 총 실행 시간: {total_time:.2f}초")