from konlpy.tag import Okt

okt = Okt()
text = "인프라 도커 자바 - Google 검색"
print(okt.nouns(text))  # 명사만 추출
print(okt.pos(text))    # 품사 태깅해서 확인
