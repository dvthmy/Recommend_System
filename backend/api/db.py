from contextlib import contextmanager
from neo4j import GraphDatabase
from .config import settings

# ==============================
# Create Neo4j driver
# ==============================
_driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
)

# ==============================
# Check connection & current database
# ==============================
print(f"[OK] Connected to Neo4j URI: {settings.NEO4J_URI}")
try:
    with _driver.session(database=settings.NEO4J_DATABASE) as session:
        result = session.run("MATCH (u:User) RETURN count(u) AS n").single()
        print(f"[INFO] Database = '{settings.NEO4J_DATABASE}', total users = {result['n']}")
except Exception as e:
    print(f"[WARNING] Neo4j connection test failed: {e}")

# ==============================
# Context manager to get session
# ==============================
@contextmanager
def get_session():
    with _driver.session(database=settings.NEO4J_DATABASE) as session:
        yield session

# ==============================
# Close driver when app shuts down
# ==============================
def close_driver():
    _driver.close()
