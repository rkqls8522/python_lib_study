import timeit

# 테스트 대상 태그 문자열과 조건 리스트
setup_code = """
last_tag = "XSV+ETN"  # 예시 문자열 (실제 상황에 맞게 변경 가능)
conditions = ["NNG", "NNP", "XSN", "SL", "SH", "SN"]
"""

# 방법 1: 직접 startswith 체인 방식
test_code_chain = """
result = (last_tag.startswith("NNG") or 
          last_tag.startswith("NNP") or 
          last_tag.startswith("XSN") or 
          last_tag.startswith("SL") or 
          last_tag.startswith("SH") or 
          last_tag.startswith("SN"))
"""

# 방법 2: for 루프를 돌면서 하나라도 조건에 해당하면 break하는 방식
test_code_for = """
result = False
for sub in conditions:
    if last_tag.startswith(sub):
        result = True
        break
"""

# 각각 1,000,000 회씩 실행하여 측정 (숫자는 상황에 따라 변경 가능)
num_executions = 10**6

time_chain = timeit.timeit(stmt=test_code_chain, setup=setup_code, number=num_executions)
time_for = timeit.timeit(stmt=test_code_for, setup=setup_code, number=num_executions)

print("직접 startswith 체인 방식의 실행 시간: {:.6f}초".format(time_chain))
print("for 루프 방식의 실행 시간: {:.6f}초".format(time_for))
