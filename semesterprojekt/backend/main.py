from fastapi import FastAPI
from backend.database import create_table, get_connection
from backend.schemas import Buchung
from backend.analysis import berechne_guv, ausgaben_nach_kategorie

app = FastAPI()


@app.on_event("startup")
def beim_start():
    create_table()


@app.get("/")
def startseite():
    return {"message": "Backend laeuft"}


@app.post("/buchungen")
def buchung_speichern(buchung: Buchung):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO buchungen (datum, betrag, kategorie, typ, beschreibung)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            buchung.datum,
            buchung.betrag,
            buchung.kategorie,
            buchung.typ,
            buchung.beschreibung,
        ),
    )

    connection.commit()
    connection.close()

    return {"message": "Buchung wurde gespeichert"}


@app.get("/buchungen")
def buchungen_anzeigen():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM buchungen ORDER BY datum DESC")
    rows = cursor.fetchall()

    buchungen = []
    for row in rows:
        buchungen.append({
            "id": row["id"],
            "datum": row["datum"],
            "betrag": row["betrag"],
            "kategorie": row["kategorie"],
            "typ": row["typ"],
            "beschreibung": row["beschreibung"],
        })

    connection.close()

    return buchungen


@app.get("/auswertung/guv")
def guv_anzeigen():
    return berechne_guv()


@app.get("/auswertung/kategorien")
def kategorien_anzeigen():
    return ausgaben_nach_kategorie()
