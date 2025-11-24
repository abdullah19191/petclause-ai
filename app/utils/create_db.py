import sqlite3

conn = sqlite3.connect("ordinances.db")
cur = conn.cursor()

# Create table
cur.execute("""
CREATE TABLE IF NOT EXISTS ordinances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    text TEXT NOT NULL
)
""")

# Insert sample ordinances (you can replace these later)
sample_data = [
    ("Denver", "It is unlawful to require pet deposits for service animals. Tenants must not be restricted based on animal breed or weight if the animal is a service or support animal."),
    ("Austin", "Pet fees must not exceed $300 unless stated otherwise by city regulations. Service animals are not classified as pets."),
    ("Berlin", "Landlords must allow pets unless they demonstrate a justified reason. Blanket bans on all pets are illegal in Berlin under tenancy law.")
]

cur.executemany("INSERT INTO ordinances (city, text) VALUES (?, ?)", sample_data)

conn.commit()
conn.close()

print("Database created and sample data inserted.")
