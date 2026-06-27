# Gruppenmitglieder

- Oskar Pit Pigola (Matrikelnummer: 5587852)


# Einfaches Buchungssystem

Dieses Projekt ist ein Semesterprojekt im Modul **ABV Programmieren fuer Wirtschaftswissenschaftlerinnen und Wirtschaftswissenschaftler**.

Die Anwendung ist ein einfaches Buchungssystem. Nutzer koennen Einnahmen und Ausgaben erfassen, gespeicherte Buchungen anzeigen und eine einfache GuV-Auswertung betrachten.

## Funktionen

- Neue Buchungen erfassen
- Buchungen dauerhaft in einer SQLite-Datenbank speichern
- Gespeicherte Buchungen anzeigen
- Einnahmen, Ausgaben und Gewinn berechnen
- GuV-Auswertung visualisieren
- Mini-Dashboard mit Auswertung der Ausgaben nach Kategorien

## Technologien

- Python
- FastAPI
- Streamlit
- SQLite
- Pydantic
- Pandas
- Matplotlib
- Requests

## Projektstruktur

semesterprojekt/
- backend/
  - main.py
  - database.py
  - schemas.py
  - analysis.py
- frontend/
  - app.py
- data/
- README.md
- AI_USAGE.md
- pyproject.toml
- uv.lock

## Aufbau der Anwendung

Die Anwendung besteht aus drei Hauptbestandteilen:

1. **Frontend**  
   Das Frontend wurde mit Streamlit umgesetzt. Dort koennen neue Buchungen eingetragen und gespeicherte Buchungen angezeigt werden.

2. **Backend**  
   Das Backend wurde mit FastAPI umgesetzt. Es nimmt die Daten aus dem Frontend entgegen, validiert sie und speichert sie in der Datenbank.

3. **Datenbank**  
   Die Buchungen werden in einer SQLite-Datenbank gespeichert. Das Frontend greift nicht direkt auf die Datenbank zu, sondern kommuniziert ueber die API mit dem Backend.

## Datenmodell

Eine Buchung besteht aus folgenden Feldern:

- Datum
- Betrag
- Kategorie
- Buchungstyp: Einnahme oder Ausgabe
- Beschreibung

Die Daten werden ueber ein Pydantic-Modell validiert, bevor sie gespeichert werden.

## GuV-Auswertung

Die Anwendung berechnet eine einfache GuV-Auswertung:

Einnahmen - Ausgaben = Gewinn

Die Berechnung erfolgt im Backend mit Pandas. Das Ergebnis wird im Frontend angezeigt und mit einem Balkendiagramm visualisiert.

## Kreative Erweiterung

Als kreative Erweiterung enthaelt die Anwendung ein Mini-Dashboard. Dieses zeigt nicht nur die einfache GuV-Auswertung, sondern auch die Ausgaben nach Kategorien.

Dadurch kann erkannt werden, welche Kostenbereiche besonders relevant sind. Die Ausgaben werden dazu nach Kategorie gruppiert und zusaetzlich als Diagramm dargestellt.

## Lokaler Start

Das Projekt wird mit zwei Terminalfenstern gestartet.

### 1. Backend starten

Im Projektordner `semesterprojekt`:

uv run uvicorn backend.main:app --reload

Das Backend ist danach erreichbar unter:

http://127.0.0.1:8000

Die automatische API-Dokumentation von FastAPI ist erreichbar unter:

http://127.0.0.1:8000/docs

### 2. Frontend starten

In einem zweiten Terminalfenster im gleichen Projektordner:

uv run streamlit run frontend/app.py

Das Frontend ist danach erreichbar unter:

http://localhost:8501

## Bedienung

1. Backend starten
2. Frontend starten
3. Im Frontend eine neue Buchung erfassen
4. Buchung speichern
5. Gespeicherte Buchungen, GuV-Auswertung und Mini-Dashboard ansehen

## KI-Nutzung

KI wurde unterstuetzend eingesetzt. Genauere Informationen stehen in der Datei `AI_USAGE.md`.