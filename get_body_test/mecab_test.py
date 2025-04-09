from konlpy.tag import Mecab

mecab = Mecab(dicpath='C:/mecab/mecab-ko-dic')  # 설치 경로에 따라 수정

def is_last_token_noun(word: str) -> bool:
    try:
        pos = mecab.pos(word)
        last_tag = pos[-1][1]              # 마지막 토큰의 품사 태그 추출
        
        # 조건: 마지막 태그가 'N'으로 시작하거나, 'SL', 'SN', 'SH' 중 하나라면 True
        if last_tag.startswith('N') or last_tag in ['SL', 'SN', 'SH', 'ETN', 'XSN']:
            print("전체 분석 결과:", pos)       # 전체 품사 태그 확인 (디버깅용)
            print("마지막 태그:", last_tag)     # 마지막 태그 확인 (디버깅용)
            print(f"조건 만족: 마지막 태그가 {last_tag} 입니다.")
            return True
        else:
            # print("조건 미충족")
            return False
    except Exception as e:
        print(f"분석 오류: {e}")
        return False

# 예제 테스트
print(is_last_token_noun("사랑"))       # [('사랑', 'NNG')] → 마지막 태그 'NNG' → 조건 만족 → True
print(is_last_token_noun("사랑이란"))     # [('사랑', 'NNG'), ('이란', 'JX')] → 마지막 태그 'JX' → False
print(is_last_token_noun("사랑함"))       # [('사랑', 'NNG'), ('함', 'XSV+ETN')] → 마지막 태그 'XSV+ETN' → False
print(is_last_token_noun("사랑하는"))     # [('사랑', 'NNG'), ('하', 'XSV'), ('는', 'ETM')] → 마지막 태그 'ETM' → False
print(is_last_token_noun("사랑하던"))     # [('사랑', 'NNG'), ('하', 'XSV'), ('던', 'ETM')] → 마지막 태그 'ETM' → False
print(is_last_token_noun("사랑할게"))     # [('사랑', 'NNG'), ('할', 'XSV+ETM'), ('게', 'NNB+JKS')] → 마지막 태그 'NNB+JKS' → 조건 만족 → True

# 추가 테스트 (영문 혹은 혼합 단어의 경우)
print(is_last_token_noun("rest"))       # 분석 결과에 따라 마지막 태그가 'SL', 'SN', 'SH'라면 True
print(is_last_token_noun("restful"))    # 분석 결과에 따라 True일 수도 있음
print(is_last_token_noun("rest함"))      # 분석 결과에 따라 True 또는 False
print(is_last_token_noun("restful한 것")) # 분석 결과에 따라 결정됨
print(is_last_token_noun("status")) # 분석 결과에 따라 결정됨
print(is_last_token_noun("station")) # 분석 결과에 따라 결정됨
print(is_last_token_noun("ssafy"))
print(is_last_token_noun("ssafy생"))
