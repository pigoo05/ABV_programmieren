import pandas as pd
from backend.database import get_connection


# Einnahmen, Ausgaben und Gewinn berechnen
def berechne_guv(startdatum=None, enddatum=None):
    connection = get_connection()
    df = pd.read_sql_query("SELECT * FROM buchungen", connection)
    connection.close()

    if df.empty:
        return {
            "einnahmen": 0,
            "ausgaben": 0,
            "gewinn": 0
        }

    if startdatum is not None and enddatum is not None:
        df = df[(df["datum"] >= startdatum) & (df["datum"] <= enddatum)]

    if df.empty:
        return {
            "einnahmen": 0,
            "ausgaben": 0,
            "gewinn": 0
        }

    einnahmen = df[df["typ"] == "Einnahme"]["betrag"].sum()
    ausgaben = df[df["typ"] == "Ausgabe"]["betrag"].sum()
    gewinn = einnahmen - ausgaben

    return {
        "einnahmen": round(einnahmen, 2),
        "ausgaben": round(ausgaben, 2),
        "gewinn": round(gewinn, 2)
    }


# Ausgaben nach Kategorien gruppieren
def ausgaben_nach_kategorie():
    connection = get_connection()
    df = pd.read_sql_query("SELECT * FROM buchungen", connection)
    connection.close()

    if df.empty:
        return []

    ausgaben = df[df["typ"] == "Ausgabe"]

    if ausgaben.empty:
        return []

    gruppiert = ausgaben.groupby("kategorie")["betrag"].sum().reset_index()

    ergebnis = []
    for index, row in gruppiert.iterrows():
        ergebnis.append({
            "kategorie": row["kategorie"],
            "betrag": round(row["betrag"], 2)
        })

    return ergebnis