# ABV 8 – FastAPI & Backend-Kommunikation
## REST-API · Datenbankanbindung · Validierung · Debugging

In diesem Uebungsblatt entwickeln Sie eine vollstaendige **Buchungsverwaltungs-API** mit FastAPI und SQLite.
Anders als in den vorherigen Blaettern arbeiten Sie nicht in einem Notebook, sondern mit echten Python-Skripten,
die Sie mit `uvicorn` als Webserver starten.

| # | Thema | Lernziel |
|---|-------|----------|
| 1 | Code lesen & verstehen | FastAPI-Struktur verstehen, Swagger UI kennenlernen |
| 2 | GET nach ID | Path-Parameter, 404-Fehlerbehandlung |
| 3 | Filtern mit Query-Parametern | Optionale Parameter, dynamische SQL-Queries |
| 4 | PUT – Zustand aendern | Update-Endpunkt mit Validierungslogik |
| 5 | Debugging | Laufzeit- und Logikfehler in einem DELETE-Endpunkt finden |
| HA | Statistik-Endpunkt | Aggregation, Vorbereitung auf Streamlit (naechste Woche) |

---

## Setup – Server starten

### Voraussetzungen
FastAPI und Uvicorn installieren

```bash
uv add fastapi[standard]
```

### Datenbank befuellen (einmalig)

Fuehren Sie das Seed-Skript aus dem `ABV8_FastAPI`-Ordner aus:

```bash
cd ABV8_FastAPI
uv run seed.py
```

Ausgabe: `15 Beispiel-Buchungen wurden in die Datenbank geschrieben.`

### Server starten

```bash
uv run uvicorn main:app --reload
```

Oeffnen Sie dann **http://127.0.0.1:8000/docs** im Browser.
Dort finden Sie die **Swagger UI** – eine interaktive Dokumentation aller Endpunkte,
in der Sie Anfragen direkt ausprobieren koennen, ohne ein extra Tool zu brauchen.

---

## Aufgabe 1 – Code lesen und verstehen

### a) Dateistruktur erkunden

Bevor Sie mit Programmieren beginnen, lesen Sie alle vier Dateien durch:

| Datei | Inhalt |
|-------|--------|
| `database.py` | SQLite-Verbindung und Tabellen-Initialisierung |
| `models.py` | Pydantic-Schema fuer Request-Validierung |
| `seed.py` | Befuellt die Datenbank mit Testdaten |
| `main.py` | Die eigentliche FastAPI-Anwendung |

### b) Swagger UI erkunden

Starten Sie den Server und oeffnen Sie http://127.0.0.1:8000/docs.
Fuehren Sie die zwei bereits fertigen Endpunkte aus:

1. **`GET /bookings`** – Alle Buchungen abrufen. Was gibt der Endpunkt zurueck?
2. **`POST /bookings`** – Legen Sie eine neue Buchung an. Nutzen Sie dazu den „Try it out"-Button.

**Beispiel-Body fuer POST /bookings:**
```json
{
  "booking_date": "2025-06-02",
  "booking_type": "revenue",
  "category": "Beratung",
  "partner_name": "Testkunde GmbH",
  "amount_net": 1500.00,
  "currency": "EUR",
  "is_paid": false
}
```
---

## Aufgabe 2 – GET /bookings/find?booking_id=...

### Ziel
Implementieren Sie den Endpunkt `GET /bookings/find` in `main.py`.
Die Buchungs-ID wird **nicht als Pfad-Parameter** (`/bookings/1`) uebergeben,
sondern als **Query-Parameter** (`/bookings/find?booking_id=1`).

Nutzen Sie `pd.read_sql_query()` fuer den Datenbankzugriff.

### Erwartetes Verhalten

| Anfrage | Erwartete Antwort |
|---------|------------------|
| `GET /bookings/find?booking_id=1` | `{"booking_id": 1, "booking_date": "2025-01-10", ...}` |
| `GET /bookings/find?booking_id=999` | `{"detail": "Buchung nicht gefunden"}` mit Status `404` |

### Vorgehen

```python
# Schritt 1: Datenbankverbindung
conn = get_connection()

# Schritt 2: Buchung per pandas laden
df = pd.read_sql_query(
    "SELECT * FROM buchungen WHERE booking_id = ?",
    conn,
    params=[booking_id]
)

# Schritt 3: Fehlerfall – leerer DataFrame bedeutet: nicht gefunden
if df.empty:
    raise HTTPException(status_code=404, detail="Buchung nicht gefunden")

# Schritt 4: Verbindung schliessen, ersten Eintrag zurueckgeben
conn.close()
return df.iloc[0].to_dict()
```

<details>
<summary><b>Tipp – Query-Parameter vs. Pfad-Parameter</b></summary>

| Art | Beispiel-URL | FastAPI-Signatur |
|-----|-------------|------------------|
| Pfad-Parameter | `/bookings/1` | `def f(booking_id: int):` |
| Query-Parameter | `/bookings/find?booking_id=1` | `def f(booking_id: int = Query(...)):` |

Beide Varianten lesen eine ID aus der URL. Query-Parameter sind flexibler,
weil mehrere optional kombiniert werden koennen.

</details>

<details>
<summary><b>Tipp – HTTPException</b></summary>

```python
raise HTTPException(status_code=404, detail="Buchung nicht gefunden")
```

FastAPI fangt diese Exception automatisch ab und schickt eine JSON-Antwort
mit HTTP-Status 404.

</details>

---

## Aufgabe 3 – Filtern mit Query-Parametern

### Ziel
Erweitern Sie `GET /bookings` in `main.py` um eine Filterlogik.
Die Endpunkt-Signatur mit den Parametern `category` und `is_paid` ist bereits vorhanden –
Sie muessen nur die SQL-Abfrage anpassen.

### Erwartetes Verhalten

| Anfrage | Ergebnis |
|---------|---------|
| `GET /bookings` | Alle Buchungen |
| `GET /bookings?category=Marketing` | Nur Buchungen der Kategorie „Marketing" |
| `GET /bookings?is_paid=false` | Nur unbezahlte Buchungen |
| `GET /bookings?category=Beratung&is_paid=true` | Bezahlte Beratungs-Buchungen |


<details>
<summary><b>Ansatz A – Fuer jeden Fall eine eigene, direkte SQL-Abfrage</b></summary>

```python
conn = get_connection()

if category is not None and is_paid is not None:
    df = pd.read_sql_query(
        "SELECT * FROM buchungen WHERE category = ? AND is_paid = ?",
        conn, params=[category, int(is_paid)]
    )
elif category is not None:
    df = pd.read_sql_query(
        "SELECT * FROM buchungen WHERE category = ?",
        conn, params=[category]
    )
elif is_paid is not None:
    df = pd.read_sql_query(
        "SELECT * FROM buchungen WHERE is_paid = ?",
        conn, params=[int(is_paid)]
    )
else:
    df = pd.read_sql_query("SELECT * FROM buchungen", conn)

conn.close()
return df.to_dict(orient="records")
```
</details>

<details>
<summary><b>Ansatz B – Alles laden, dann mit pandas filtern (einfacher, aber Achtung!)</b></summary>

Alternativ koennen Sie erst alle Daten laden und danach in Python filtern:

```python
conn = get_connection()
df = pd.read_sql_query("SELECT * FROM buchungen", conn)
conn.close()

if category is not None:
    df = df[df["category"] == category]
if is_paid is not None:
    df = df[df["is_paid"] == int(is_paid)]

return df.to_dict(orient="records")
```

**Warum ist das problematisch bei echten Anwendungen?**

- Bei einer Tabelle mit **Millionen Eintraegen** werden alle Daten in den Arbeitsspeicher
  geladen – auch wenn am Ende nur 10 Zeilen benoetigt werden.
- Datenbankserver sind fuer genau dieses Filtern optimiert (Indizes, Query-Planner).
  Den Filter in Python zu machen verschenkt diesen Vorteil vollstaendig.
- Fuer kleine Datensaetze (wie unsere Uebungs-DB) ist Ansatz B praktisch – in der
  Praxis immer Ansatz A bevorzugen.

</details>

---

## Aufgabe 4 – PUT /bookings/{booking_id}/pay

### Ziel
Implementieren Sie `PUT /bookings/{booking_id}/pay`.
Dieser Endpunkt markiert eine Buchung als bezahlt.

### Erwartetes Verhalten

| Situation | HTTP-Status | Antwort |
|-----------|------------|---------|
| Buchung existiert und ist offen | `200` | `{"message": "Buchung als bezahlt markiert", "booking_id": 5}` |
| Buchung nicht vorhanden | `404` | `{"detail": "Buchung nicht gefunden"}` |
| Buchung bereits bezahlt | `400` | `{"detail": "Buchung ist bereits als bezahlt markiert"}` |

### Vorgehen

```
1. conn = get_connection()
2. row = ... SELECT ... fetchone()
3. if row is None → HTTPException(404)
4. if row["is_paid"] == 1 → HTTPException(400)
5. conn.execute("UPDATE buchungen SET is_paid = 1 WHERE booking_id = ?", (booking_id,))
6. conn.commit()
7. conn.close()
8. return {"message": ..., "booking_id": booking_id}
```

<details>
<summary><b>Tipp – Buchung pruefen mit pandas</b></summary>

Nutzen Sie `pd.read_sql_query()` um die Buchung zu laden und zu pruefen:

```python
conn = get_connection()
df = pd.read_sql_query(
    "SELECT * FROM buchungen WHERE booking_id = ?",
    conn, params=[booking_id]
)

if df.empty:
    raise HTTPException(status_code=404, detail="Buchung nicht gefunden")

if df.iloc[0]["is_paid"] == 1:
    raise HTTPException(status_code=400, detail="Buchung ist bereits als bezahlt markiert")
```

Fuer das eigentliche UPDATE verwenden Sie `conn.execute()`,
da pandas `to_sql` keine UPDATE-Operationen unterstuetzt:

```python
conn.execute(
    "UPDATE buchungen SET is_paid = 1 WHERE booking_id = ?", (booking_id,)
)
conn.commit()
conn.close()
```

</details>

---

## Hausaufgabe – Statistik-Endpunkt (Vorbereitung auf naechste Woche)

### Hintergrund

Naechste Woche werden Sie eine **Streamlit-App** bauen, die diesen API-Endpunkt aufruft
und die Daten als interaktive Charts darstellt.
Damit das klappt, muss `GET /stats` exakt das richtige Schema liefern.

### Aufgabe

Implementieren Sie `GET /stats` in `main.py` gemaess dem Docstring.

Das Ergebnis soll so aussehen (Werte koennen variieren):

```json
{
  "total_bookings": 15,
  "total_revenue": 36150.0,
  "total_expenses": 5389.0,
  "net_profit": 30761.0,
  "paid_rate_pct": 73.33,
  "by_category": [
    {"category": "Beratung",  "revenue": 19000.0, "expenses": 0.0,    "net": 19000.0, "count": 3},
    {"category": "Marketing", "revenue": 12500.0, "expenses": 1800.0, "net": 10700.0, "count": 4},
    {"category": "Support",   "revenue":  4650.0, "expenses": 0.0,    "net":  4650.0, "count": 2},
    {"category": "Software",  "revenue":     0.0, "expenses": 1090.0, "net": -1090.0, "count": 3},
    {"category": "Buero",     "revenue":     0.0, "expenses": 2100.0, "net": -2100.0, "count": 3}
  ]
}
```

<details>
<summary><b>Tipp – Gesamtstatistiken mit pandas berechnen</b></summary>

```python
conn = get_connection()
df = pd.read_sql_query("SELECT * FROM buchungen", conn)
conn.close()

total_bookings = len(df)
total_revenue  = round(float(df[df["booking_type"] == "revenue"]["amount_net"].sum()), 2)
total_expenses = round(float(df[df["booking_type"] == "expense"]["amount_net"].sum()), 2)
net_profit     = round(total_revenue - total_expenses, 2)
paid_rate_pct  = round(df["is_paid"].mean() * 100, 2) if total_bookings > 0 else 0.0
```

</details>

<details>
<summary><b>Tipp – by_category mit groupby aufbauen</b></summary>

```python
by_category = []
for cat, group in df.groupby("category"):
    revenue  = round(float(group[group["booking_type"] == "revenue"]["amount_net"].sum()), 2)
    expenses = round(float(group[group["booking_type"] == "expense"]["amount_net"].sum()), 2)
    by_category.append({
        "category": cat,
        "revenue":  revenue,
        "expenses": expenses,
        "net":      round(revenue - expenses, 2),
        "count":    len(group),
    })

# Sortieren nach net absteigend
by_category.sort(key=lambda x: x["net"], reverse=True)
```

**Alternativ kompakter mit `.agg()`:**

```python
grouped = (
    df.assign(
        revenue  = df["amount_net"].where(df["booking_type"] == "revenue",  0),
        expenses = df["amount_net"].where(df["booking_type"] == "expense", 0),
    )
    .groupby("category")
    .agg(revenue=("revenue", "sum"), expenses=("expenses", "sum"), count=("booking_id", "count"))
    .reset_index()
)
grouped["net"] = grouped["revenue"] - grouped["expenses"]
grouped = grouped.sort_values("net", ascending=False)
by_category = grouped.round(2).to_dict(orient="records")
```

</details>

### Anforderungen fuer naechste Woche

Ihr `GET /stats`-Endpunkt wird naechste Woche direkt von einer Streamlit-App konsumiert.
Stellen Sie sicher, dass:

- [ ] Der Endpunkt mit HTTP 200 antwortet (kein 501 mehr)
- [ ] Alle Feldnamen **exakt** wie im Schema oben sind
- [ ] Keine `null`-Werte in der Antwort vorkommen
- [ ] Der Endpunkt auch bei einer leeren Datenbank nicht abstuerzt
- [ ] Sie den Server lokal starten koennen: `uvicorn main:app --reload`

---

## Referenz – Nuetzliche Befehle

| Befehl | Beschreibung |
|--------|-------------|
| `uvicorn main:app --reload` | Server starten (auto-reload bei Aenderungen) |
| `python seed.py` | Datenbank mit Beispieldaten befuellen |
| `curl http://127.0.0.1:8000/bookings` | Alle Buchungen (PowerShell: `Invoke-RestMethod`) |
| `http://127.0.0.1:8000/docs` | Swagger UI im Browser |
| `http://127.0.0.1:8000/redoc` | ReDoc-Dokumentation im Browser |

## Referenz – HTTP-Statuscodes

| Code | Bedeutung | Wann verwenden |
|------|-----------|---------------|
| `200 OK` | Erfolgreich | Standard bei GET, PUT |
| `201 Created` | Ressource erstellt | POST bei erfolgreichem Erstellen |
| `400 Bad Request` | Fehlerhafte Anfrage | Ungueltige Eingabe (z. B. schon bezahlt) |
| `404 Not Found` | Nicht gefunden | ID existiert nicht |
| `422 Unprocessable Entity` | Validierungsfehler | Pydantic schlaegt an (automatisch) |
| `501 Not Implemented` | Noch nicht implementiert | Platzhalter in den Aufgaben |
