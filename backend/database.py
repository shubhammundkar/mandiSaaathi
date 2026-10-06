import sqlite3
from typing import Any, List, Optional, Tuple
from backend.config import DATABASE_PATH, DATA_DIR

def init_db() -> None:
    """Ensures database directory exists and creates base schema tables if needed."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mandi_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state TEXT NOT NULL,
                district TEXT NOT NULL,
                market TEXT NOT NULL,
                commodity TEXT NOT NULL,
                variety TEXT,
                grade TEXT,
                arrival_date TEXT NOT NULL,
                min_price REAL NOT NULL,
                max_price REAL NOT NULL,
                modal_price REAL NOT NULL,
                arrival_quantity REAL,
                source TEXT NOT NULL DEFAULT 'snapshot' CHECK(source IN ('live', 'snapshot', 'sample')),
                is_sample INTEGER DEFAULT 0,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uq_mandi_prices 
            ON mandi_prices(market, commodity, variety, arrival_date);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_commodity_market 
            ON mandi_prices(commodity, market, arrival_date);
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop TEXT NOT NULL,
                district TEXT NOT NULL,
                language TEXT DEFAULT 'mr',
                nickname TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farmer_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop TEXT NOT NULL,
                market TEXT NOT NULL,
                price REAL NOT NULL,
                quantity REAL,
                report_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query: str, params: Tuple[Any, ...] = ()) -> int:
    """Executes an INSERT/UPDATE/DELETE query and returns rowcount."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount

def fetch_all(query: str, params: Tuple[Any, ...] = ()) -> List[dict]:
    """Fetches all rows as a list of dictionaries."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def fetch_one(query: str, params: Tuple[Any, ...] = ()) -> Optional[dict]:
    """Fetches a single row as a dictionary."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
