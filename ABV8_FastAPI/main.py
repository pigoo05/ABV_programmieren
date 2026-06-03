"""
ABV 8 – FastAPI Buchungsverwaltung
===================================
Starten:     uvicorn main:app --reload
Swagger UI:  http://127.0.0.1:8000/docs
Redoc:       http://127.0.0.1:8000/redoc

Lesen Sie AUFGABE.md fuer die vollstaendigen Aufgabenstellungen.
"""
from typing import Optional
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from database import get_connection, init_db
from models import BookingCreate

init_db()   # ← plain sync function, no await needed

app = FastAPI(
    title="Buchungsverwaltung API",
    version="1.0.0",
    description="Uebungs-API fuer ABV 8 – FastAPI & Backend-Kommunikation",
)


# =============================================================
# BEREITS IMPLEMENTIERT – Diese Endpunkte laufen schon.
# Lesen Sie sie sorgfaeltig durch bevor Sie mit Aufgabe 2 beginnen.
# =============================================================


@app.get("/bookings", tags=["Buchungen"], summary="Alle Buchungen abrufen")
def get_bookings(
    category: Optional[str] = Query(default=None, description="Filter nach Kategorie (z. B. 'Marketing')"),
    is_paid: Optional[bool] = Query(default=None, description="Filter nach Zahlungsstatus"),
):
    """
    Gibt alle Buchungen zurueck.

    Bereits implementiert: Basis-Abfrage ohne Filter – alle Buchungen werden zurueckgegeben.

    ╔══════════════════════════════════════════╗
    ║  AUFGABE 3 – Filter-Logik ergaenzen      ║
    ╚══════════════════════════════════════════╝
    Die Query-Parameter `category` und `is_paid` werden bereits entgegengenommen,
    aber noch nicht genutzt. Ergaenze die Logik mit if/elif-Zweigen:

    - Nur category angegeben  → SQL mit WHERE category = ?
    - Nur is_paid angegeben   → SQL mit WHERE is_paid = ?
    - Beide angegeben         → SQL mit WHERE category = ? AND is_paid = ?
    - Nichts angegeben        → alle Buchungen (bereits implementiert)

    Nutze in jedem Zweig pd.read_sql_query() mit einem passenden SQL-String.
    Siehe AUFGABE.md Aufgabe 3 fuer Hinweise und eine alternative pandas-Loesung.
    """
    conn = get_connection()
    # ---- Aufgabe 3: if/elif-Zweige hier ergaenzen -----------------------
    df = pd.read_sql_query("SELECT * FROM buchungen", conn)
    # ---------------------------------------------------------------------
    conn.close()
    return df.to_dict(orient="records")


@app.post("/bookings", status_code=201, tags=["Buchungen"], summary="Neue Buchung erstellen")
def create_booking(booking: BookingCreate):
    """
    Erstellt eine neue Buchung. FastAPI validiert den Request-Body automatisch
    gegen das BookingCreate-Schema aus models.py.

    Die neue Zeile wird per pandas `to_sql` mit `if_exists='append'` in die
    Datenbank geschrieben – kein manuelles INSERT noetig.
    """
    conn = get_connection()
    df_new = pd.DataFrame([booking.model_dump()])
    df_new["is_paid"] = df_new["is_paid"].astype(int)   # bool → 0/1 fuer SQLite
    df_new.to_sql("buchungen", conn, if_exists="append", index=False)
    conn.close()
    return {"message": "Buchung erstellt"}


# =============================================================
# AUFGABE 2 – GET /bookings/find?booking_id=...
# =============================================================


@app.get("/bookings/find", tags=["Buchungen"], summary="Einzelne Buchung per Query-Parameter abrufen")
def get_booking_by_id(booking_id: int = Query(description="ID der gesuchten Buchung")):
    """
    Gibt eine einzelne Buchung anhand ihrer ID zurueck.

    ╔══════════════════════════════════════════╗
    ║  AUFGABE 2 – Implementierung             ║
    ╚══════════════════════════════════════════╝
    Implementiere diesen Endpunkt Schritt fuer Schritt:

    1. Datenbankverbindung herstellen (get_connection()).
    2. Buchung mit pd.read_sql_query() und einem WHERE-Filter laden.
    3. Falls der zurueckgegebene DataFrame leer ist (df.empty):
           raise HTTPException(status_code=404, detail="Buchung nicht gefunden")
    4. Verbindung schliessen und ersten Eintrag als Dictionary zurueckgeben.

    Beispiel:  GET /bookings/find?booking_id=1
               → {"booking_id": 1, "booking_date": "2025-01-10", ...}
    """
    # TODO: Implementierung hier
    raise HTTPException(status_code=501, detail="Noch nicht implementiert")


# =============================================================
# AUFGABE 4 – PUT /bookings/{booking_id}/pay
# =============================================================


@app.put("/bookings/{booking_id}/pay", tags=["Buchungen"], summary="Buchung als bezahlt markieren")
def mark_booking_paid(booking_id: int):
    """
    Markiert eine Buchung als bezahlt (is_paid = 1).

    ╔══════════════════════════════════════════╗
    ║  AUFGABE 4 – Implementierung             ║
    ╚══════════════════════════════════════════╝
    Implementiere diesen Endpunkt mit folgender Logik:

    1. Buchung in der Datenbank suchen.
       → Falls nicht vorhanden: 404 mit "Buchung nicht gefunden"

    2. Pruefen ob die Buchung bereits bezahlt ist (is_paid == 1).
       → Falls ja: 400 mit "Buchung ist bereits als bezahlt markiert"

    3. is_paid auf 1 setzen, Aenderung committen.

    4. Erfolgsmeldung zurueckgeben:
       {"message": "Buchung als bezahlt markiert", "booking_id": booking_id}

    Beispiel:  PUT /bookings/5/pay
    """
    # TODO: Implementierung hier
    raise HTTPException(status_code=501, detail="Noch nicht implementiert")


# =============================================================
# HAUSAUFGABE – GET /stats
# =============================================================


@app.get("/stats", tags=["Statistiken"], summary="Finanzstatistiken abrufen")
def get_stats():
    """
    Gibt aggregierte Finanzstatistiken zurueck.

    ╔══════════════════════════════════════════╗
    ║  HAUSAUFGABE – Statistik-Endpunkt        ║
    ╚══════════════════════════════════════════╝
    Implementiere diesen Endpunkt so, dass er folgendes Dictionary liefert:

    {
        "total_bookings":  <int>,     Gesamtanzahl aller Buchungen
        "total_revenue":   <float>,   Summe aller Einnahmen (booking_type='revenue')
        "total_expenses":  <float>,   Summe aller Ausgaben  (booking_type='expense')
        "net_profit":      <float>,   Einnahmen - Ausgaben
        "paid_rate_pct":   <float>,   Anteil bezahlter Buchungen in % (2 Nachkommastellen)
        "by_category": [
            {
                "category": <str>,
                "revenue":  <float>,
                "expenses": <float>,
                "net":      <float>,
                "count":    <int>
            },
            ...                       sortiert nach net absteigend
        ]
    }

    Hinweise:
    - Lade alle Buchungen mit pd.read_sql_query() in einen DataFrame.
    - Nutze pandas-Operationen (groupby, agg, sum, mean) fuer die Berechnungen.
    - Alle float-Werte sollen auf 2 Nachkommastellen gerundet sein.
    - Der Endpunkt soll auch bei einer leeren Datenbank ohne Fehler laufen
      (z. B. paid_rate_pct = 0.0 wenn keine Buchungen vorhanden).

    WICHTIG fuer naechste Woche:
    Dieser Endpunkt wird von einer Streamlit-App direkt aufgerufen.
    Halte dich exakt an das Schema oben – Feldnamen und Typen muessen stimmen.
    """
    # TODO: Implementierung hier
    raise HTTPException(status_code=501, detail="Noch nicht implementiert")
