import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse

app = FastAPI()

# 数据库连接参数
DB_HOST = "172.25.4.33"
DB_PORT = "5432"
DB_NAME = "nauv"
DB_USER = "postgres"
DB_PASSWORD = "nauv2023"


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


class User(BaseModel):
    username: str
    password: str


class Status(BaseModel):
    status: str
    lon: float
    lat: float
    dir: float
    depth: float
    roll: float
    elevation: float
    tem: float
    speed: float
    power: float
    # 添加其他字段


@app.post("/api/login_in")
def login(user: User):
    try:
        # 获取POST请求中的用户信息
        username = user.username
        password = user.password

        # 连接到数据库
        conn = get_db_connection()
        cursor = conn.cursor()

        # 执行查询语句
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s",
            (username, password)
        )
        result = cursor.fetchone()

        if result:
            return {"message": "Logged in successfully"}
        else:
            raise HTTPException(status_code=401, detail="Invalid username or password")

    except psycopg2.Error as e:
        # 数据库错误
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        # 其他未知错误
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 关闭数据库连接
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.post("/api/register")
def register(user: User):
    try:
        # 获取POST请求中的用户信息
        username = user.username
        password = user.password

        # 连接到数据库
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查用户名是否已存在
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        if result:
            raise HTTPException(status_code=409, detail="Username already exists")

        # 插入新用户
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, password))
        conn.commit()

        return {"message": "Registration successful"}

    except psycopg2.Error as e:
        # 数据库错误
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        # 其他未知错误
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 关闭数据库连接
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.get("/api/status")
def get_last_status():
    try:
        # 连接到数据库
        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询最后一行数据
        cursor.execute("SELECT lon, lat, dir, depth, roll, elevation, tem, speed, power, dates, times FROM status ORDER BY id DESC LIMIT 1")
        data = cursor.fetchone()

        if data:
            return {
                "lon": data[0],
                "lat": data[1],
                "dir": data[2],
                "depth": data[3],
                "roll": data[4],
                "elevation": data[5],
                "tem": data[6],
                "speed": data[7],
                "power": data[8],
                "date": data[9],
                "time": data[10]
                # 添加其他字段的值
            }
        else:
            raise HTTPException(status_code=404, detail="No status data found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/track")
def track():
    try:
        # 连接到数据库
        conn = get_db_connection()
        cursor = conn.cursor()

        # 从数据库中获取经纬度信息
        cursor.execute("SELECT lon, lat FROM status")
        rows = cursor.fetchall()

        # 将经纬度数据转换为字典列表
        data = [{"lon": row[0], "lat": row[1]} for row in rows]

        # 关闭数据库连接
        cursor.close()
        conn.close()

        # 将数据转换为JSON响应并返回给客户端
        return JSONResponse(content=data)

    except psycopg2.Error as e:
        # 数据库错误
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        # 其他未知错误
        raise HTTPException(status_code=500, detail=str(e))




