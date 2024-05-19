import socket
import json
import asyncio
import asyncpg
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

app = FastAPI()

# 数据库连接参数
DB_HOST = "172.25.4.33"
DB_PORT = 5432
DB_NAME = "nauv"
DB_USER = "postgres"
DB_PASSWORD = "nauv2023"

# Pydantic模型用于接收和验证请求体中的数据
class Message(BaseModel):
    direction: str
    hex_code: str

# 数据库连接池
db_pool = None

@app.on_event("startup")
async def startup():
    global db_pool
    db_pool = await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST
    )

@app.on_event("shutdown")
async def shutdown():
    await db_pool.close()

@app.post("/send_message/")
async def send_message(message: Message):
    async with db_pool.acquire() as conn:
        await conn.execute("INSERT INTO message (direction, hex_code) VALUES ($1, $2)",
                           message.direction, message.hex_code)
    return {"status": "success", "message": "Message received"}

async def handle_database_notifications():
    while True:
        async with db_pool.acquire() as conn:
            # 查询数据库表command_data中未读的数据
            unread_data = await conn.fetch("SELECT * FROM command_data WHERE status = 0")

            # 如果有未读数据，则处理数据
            for data in unread_data:
                direction = data['direction']
                hex_code = data['hex_code']

                # 将数据组装成JSON格式并保存到缓存中
                message = {"direction": direction, "hex_code": hex_code}
                cached_notifications.append(message)

                # 更新数据状态为已读
                await conn.execute("UPDATE command_data SET status = 1 WHERE hex_code = $1", hex_code)

            # 等待一段时间后再次查询数据库
            await asyncio.sleep(1)

@app.get("/get_notifications/")
async def get_notifications():
    # 获取缓存中的通知消息并清空缓存
    global cached_notifications
    notifications = cached_notifications.copy()
    cached_notifications.clear()
    return notifications

@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(handle_database_notifications())

# 缓存通知消息的列表
cached_notifications = []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="172.25.4.33", port=802)
