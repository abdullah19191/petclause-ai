import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "ordinances.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def list_cities():
    """Return all cities in the DB."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT city FROM ordinances ORDER BY city ASC")
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_ordinance(city: str) -> str:
    """Return the ordinance text for a given city."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM ordinances WHERE city = ?", (city,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return "No ordinance found for this city."
    return row[0]
