import socket
import uuid
import datetime
import psycopg2
from fastapi import FastAPI, HTTPException, requests
from pydantic import BaseModel
from starlette.responses import JSONResponse

app = FastAPI()

# # TCP服务器的IP地址和端口号
# tcp_server_ip = '172.25.4.33'  # TCP服务器的IP地址
# tcp_server_port = 7500  # TCP服务器的端口号
#
# # 创建TCP套接字
# tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
# # 连接到TCP服务器
# tcp_client_socket.connect((tcp_server_ip, tcp_server_port))

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


class User_login(BaseModel):
    username: str
    password: str


class User_register(BaseModel):
    username: str
    password: str
    email: str


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
def login(user: User_login):
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
def register(user: User_register):
    try:
        # 获取POST请求中的用户信息
        username = user.username
        password = user.password
        email = user.email

        # 连接到数据库
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查用户名是否已存在
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        if result:
            # 如果用户名已存在，则返回状态码 409
            raise HTTPException(status_code=409, detail="Username already exists")

        # 插入新用户
        query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, password, email))
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



@app.post("/direction")
def send_direction(info: dict):
    direction = info.get("direction")
    hex_codes = {
        'up': 'FD5A0D0A',
        'down': 'FD540D0A',
        'left': 'FD4CD0A',
        'right': 'FD520D0A'
    }

    # 连接到数据库
    conn = get_db_connection()
    cursor = conn.cursor()

    if direction in hex_codes:
        hex_code = hex_codes[direction]

        # 获取当前时间
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 将数据存入数据库
        cursor.execute("INSERT INTO command_data (direction, hex_code, status, command_time) VALUES (%s, %s, %s, %s)",
                       (direction, hex_code, 0, current_time))
        conn.commit()

        result = {"direction": direction, "hex_code": hex_code}
        print(result)  # 打印返回结果
        return result
        return result
    else:
        raise HTTPException(status_code=400, detail="Invalid direction")


