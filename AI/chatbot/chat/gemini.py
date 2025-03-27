import requests
import json
from datetime import datetime, timedelta
import pymysql  # mysql.connector 대신 pymysql 사용
from typing import Optional, Dict
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
GEMINI_API_KEY = "AIzaSyDwxwFfDd-Z4GQq5kfMDVa1GgUtDlUOOaA"

# DB 연결 풀 설정
DB_POOL = PooledDB(
    creator=pymysql,
    maxconnections=5,  # 최대 연결 수
    mincached=1,       # 최소 캐시 연결 수
    maxcached=3,       # 최대 캐시 연결 수
    host='stg-yswa-kr-practice-db-master.mariadb.database.azure.com',
    port=3306,
    user='S12P22A408@stg-yswa-kr-practice-db-master',
    password='t9hurA0fqX',
    database='S12P22A408',
    charset='utf8mb4',
    cursorclass=DictCursor
)

def parse_gemini_response(response_json: Dict) -> Optional[tuple]:
    try:
        text = response_json['candidates'][0]['content']['parts'][0]['text']
        lines = text.strip().split('\n')
        
        # A:로 시작하는 줄이 있는지 확인 (일정인 경우에만 존재)
        if any(line.strip().startswith('A:') for line in lines):
            timestamp_line = next(line for line in lines if line.strip().startswith('A:'))
            content_line = next(line for line in lines if line.strip().startswith('B:'))
            
            timestamp = timestamp_line.replace('A:', '').strip()
            content = content_line.replace('B:', '').strip()
            
            # timestamp를 datetime 객체로 변환
            expire_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M')
            alarm_time = expire_time - timedelta(days=1)
            
            # 세 번째 줄부터의 내용을 응답 메시지로 사용
            response_message = '\n'.join(line for line in lines 
                                       if not line.strip().startswith(('A:', 'B:'))).strip()
            
            return True, expire_time, alarm_time, content, response_message
        else:
            # 일정이 아닌 경우
            return False, text.strip()
                
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(f"Full response text: {text}")
    return None

def save_to_database(userId: str, expire_time: datetime, alarm_time: datetime, content: str):
    try:
        print("Getting connection from pool...")
        conn = DB_POOL.connection()
        print("Got connection from pool")
        
        with conn.cursor() as cursor:
            print("Cursor created")
            
            expire_time_str = expire_time.strftime('%Y-%m-%d %H:%M:%S')
            alarm_time_str = alarm_time.strftime('%Y-%m-%d %H:%M:%S')
            
            query = """
            INSERT INTO schedules (userId, content, ExpireTime, AlarmTime)
            VALUES (%s, %s, %s, %s)
            """
            values = (userId, content, expire_time_str, alarm_time_str)
            
            print(f"Executing query with values: {values}")
            cursor.execute(query, values)
            conn.commit()
            
            # 확인
            cursor.execute("SELECT * FROM schedules ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            print(f"Last inserted record: {result}")
            
    except Exception as e:
        print(f"Error: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()
            print("Connection returned to pool")

def process_gemini_request(userId: str, message: str):
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    
    data = {
        "contents": [{
            "parts": [{
                "text": f"""오늘은 {current_date} 입니다.
                당신은 친근하고 다정한 AI 비서입니다.

                만약 메시지가 일정이나 약속에 대한 내용이라면:
                1. 첫 줄에 "A: YYYY-MM-DD HH:mm" 형식으로 날짜와 시간을 작성 (시간 없으면 00:00)
                2. 두 번째 줄에 "B: " 뒤에 일정 내용을 작성
                3. 세 번째 줄에 일정 추가 확인과 함께 친근하게 응답

                예시 (일정인 경우):
                A: 2024-03-20 14:00
                B: 회의
                네, 3월 20일 오후 2시 회의 일정을 추가했어요! 하루 전에 다시 알려드릴게요 😊

                일정이 아닌 경우에는 친근하고 공감하는 말투로 자연스럽게 대화해주세요.
                예시 (일정이 아닌 경우):
                "추어탕 드시고 싶으시군요! 이 날씨에 따뜻한 추어탕 정말 좋을 것 같아요 😊"

                입력 메시지:
                {message}"""
            }]
        }]
    }
    
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)
        response_json = response.json()
        
        print("Gemini Response:", response_json)
        
        # 응답 파싱
        parsed_data = parse_gemini_response(response_json)
        if parsed_data:
            if parsed_data[0]:  # 일정인 경우
                _, expire_time, alarm_time, content, response_message = parsed_data
                save_to_database(userId, expire_time, alarm_time, content)
                
                return {
                    "success": True,
                    "message": response_message,
                    "schedule": {
                        "dateTime": expire_time.strftime('%Y-%m-%d %H:%M'),
                        "content": content
                    }
                }
            else:  # 일정이 아닌 경우
                _, response_message = parsed_data
                return {
                    "success": True,
                    "message": response_message
                }
        
        return {
            "success": False,
            "message": "죄송합니다. 메시지를 이해하지 못했어요. 다시 말씀해주시겠어요?"
        }
        
    except Exception as e:
        print(f"Error occurred: {e}")
        return {
            "success": False,
            "message": "죄송합니다. 오류가 발생했어요. 잠시 후 다시 시도해주세요."
        }
