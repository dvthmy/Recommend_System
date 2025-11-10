from contextlib import contextmanager
from neo4j import GraphDatabase
from .config import settings

# ==============================
# ⚙️  Tạo driver Neo4j
# ==============================
_driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
)

# ==============================
# 🔍 Kiểm tra kết nối & DB đang dùng
# ==============================
print(f"✅ Connected to Neo4j URI: {settings.NEO4J_URI}")
try:
    with _driver.session(database=settings.NEO4J_DATABASE) as session:
        result = session.run("MATCH (u:User) RETURN count(u) AS n").single()
        print(f"🔍 Database = '{settings.NEO4J_DATABASE}', total users = {result['n']}")
except Exception as e:
    print(f"⚠️ Neo4j connection test failed: {e}")

# ==============================
# 📦 Context manager để lấy session
# ==============================
@contextmanager
def get_session():
    with _driver.session(database=settings.NEO4J_DATABASE) as session:
        yield session

# ==============================
# ❌ Đóng driver khi app tắt
# ==============================
def close_driver():
    _driver.close()
