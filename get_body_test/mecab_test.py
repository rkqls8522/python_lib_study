from konlpy.tag import Mecab

mecab = Mecab(dicpath='C:/mecab/mecab-ko-dic') 

def is_last_token_noun(word: str) -> bool:
    try:
        pos = mecab.pos(word)
        last_tag = pos[-1][1]
        print("전체 분석 결과:", pos)
        print("마지막 태그:", last_tag)
        
        if any(sub in last_tag for sub in ["NNG", "NNP", "XSN", "SL", "SH", "SN"]):
            print(f"조건 만족: 마지막 태그에 지정한 품사가 포함됩니다. ({last_tag})")
            return True
        else:
            print(f"조건 불만족: 마지막 태그에 지정한 품사가 포함되지 않습니다. ({last_tag})")
            return False
    except Exception as e:
        print(f"분석 오류: {e}")
        return False

print(is_last_token_noun("사랑"))    
print(is_last_token_noun("사랑이란"))
print(is_last_token_noun("사랑함"))  
print(is_last_token_noun("사랑하는"))
print(is_last_token_noun("사랑하던"))
print(is_last_token_noun("사랑할게"))

test_words = ["rest", "restful", "rest함", "restful한 것", "status", "station", "ssafy", "ssafy생"]
for word in test_words:
    print(f"{word} -> {is_last_token_noun(word)}")
