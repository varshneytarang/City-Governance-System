import psycopg2
from psycopg2.extras import RealDictCursor
from finance_agent.config import settings

class FinanceDepartmentDatabase:
    """Finance DB connection and query helpers (mirrors water_agent)."""
    def __init__(self):
        self.conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            cursor_factory=RealDictCursor,
        )

    def close(self):
        self.conn.close()

    def fetch_budget_context(self, location=None):
        with self.conn.cursor() as cur:
            if location:
                cur.execute("SELECT * FROM finance_context WHERE location = %s", (location,))
            else:
                cur.execute("SELECT * FROM finance_context LIMIT 1")
            return cur.fetchone()

    def fetch_audit_log(self, limit=10):
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM finance_audit ORDER BY timestamp DESC LIMIT %s", (limit,))
            return cur.fetchall()

# Factory for queries (for patching in tests)
def get_finance_queries():
    return FinanceDepartmentDatabase()
