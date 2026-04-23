import pymysql
from config import Config


def get_connection():
    """Return a new PyMySQL connection."""
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def execute(sql: str, params: tuple = (), fetchone: bool = False):
    """Run a query and optionally return results."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if fetchone:
                return cur.fetchone()
            return cur.fetchall()
    finally:
        conn.close()


def execute_write(sql: str, params: tuple = ()) -> int:
    """Run INSERT/UPDATE/DELETE, return lastrowid."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.lastrowid
    finally:
        conn.close()