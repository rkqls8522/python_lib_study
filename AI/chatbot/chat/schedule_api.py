from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import pymysql
from dbutils.pooled_db import PooledDB

# 라우터 생성
router = APIRouter(
    prefix="/schedules",
    tags=["schedules"]
)

# DB 연결 풀 설정
DB_POOL = PooledDB(
    creator=pymysql,
    maxconnections=5,
    mincached=1,
    maxcached=3,
    host='stg-yswa-kr-practice-db-master.mariadb.database.azure.com',
    port=3306,
    user='S12P22A408@stg-yswa-kr-practice-db-master',
    password='t9hurA0fqX',
    database='S12P22A408',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

class Schedule(BaseModel):
    id: Optional[int] = None
    userId: str
    content: str
    ExpireTime: datetime
    AlarmTime: datetime

class ScheduleUpdate(BaseModel):
    content: Optional[str] = None
    ExpireTime: Optional[datetime] = None
    AlarmTime: Optional[datetime] = None

@router.get("/{user_id}", response_model=List[Schedule])
async def get_schedules(user_id: str):
    try:
        conn = DB_POOL.connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM schedules WHERE userId = %s ORDER BY ExpireTime",
                (user_id,)
            )
            schedules = cursor.fetchall()
            return schedules
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.put("/{schedule_id}", response_model=Schedule)
async def update_schedule(schedule_id: int, schedule: ScheduleUpdate):
    try:
        conn = DB_POOL.connection()
        with conn.cursor() as cursor:
            update_fields = []
            values = []
            if schedule.content is not None:
                update_fields.append("content = %s")
                values.append(schedule.content)
            if schedule.ExpireTime is not None:
                update_fields.append("ExpireTime = %s")
                values.append(schedule.ExpireTime)
            if schedule.AlarmTime is not None:
                update_fields.append("AlarmTime = %s")
                values.append(schedule.AlarmTime)
            
            if not update_fields:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            values.append(schedule_id)
            query = f"""
                UPDATE schedules 
                SET {', '.join(update_fields)}
                WHERE id = %s
                """
            cursor.execute(query, values)
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Schedule not found")
            
            cursor.execute("SELECT * FROM schedules WHERE id = %s", (schedule_id,))
            updated_schedule = cursor.fetchone()
            conn.commit()
            
            return updated_schedule
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: int):
    try:
        conn = DB_POOL.connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM schedules WHERE id = %s", (schedule_id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Schedule not found")
            conn.commit()
            return {"message": "Schedule deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close() 