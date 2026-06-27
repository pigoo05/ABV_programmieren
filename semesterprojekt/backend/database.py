import sqlite3
# Pfad zur SQLite Datenbank
DB_PATH = "data/bookungen.db"

# Verbindung zur Datenbank herstellen
def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

# Tabelle fuer Buchungen erstellen, falls sie noch nicht existiert
def create_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buchungen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datum TEXT NOT NULL,
            betrag REAL NOT NULL,
            kategorie TEXT NOT NULL,
            typ TEXT NOT NULL,
            beschreibung TEXT
        )
    """)

    connection.commit()
    connection.close()
