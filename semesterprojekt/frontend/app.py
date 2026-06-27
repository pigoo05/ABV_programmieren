import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "http://127.0.0.1:8000"

st.title("Einfaches Buchungssystem")

st.write("Mit dieser Anwendung koennen Einnahmen und Ausgaben erfasst und ausgewertet werden.")

st.header("Neue Buchung erfassen")

datum = st.date_input("Buchungsdatum")
betrag = st.number_input("Betrag", min_value=0.0, step=1.0)
kategorie = st.text_input("Kategorie")
typ = st.selectbox("Buchungstyp", ["Einnahme", "Ausgabe"])
beschreibung = st.text_input("Beschreibung")

if st.button("Buchung speichern"):
    if betrag <= 0:
        st.error("Der Betrag muss groesser als 0 sein.")
    elif kategorie == "":
        st.error("Bitte eine Kategorie eingeben.")
    else:
        neue_buchung = {
            "datum": str(datum),
            "betrag": betrag,
            "kategorie": kategorie,
            "typ": typ,
            "beschreibung": beschreibung
        }

        antwort = requests.post(API_URL + "/buchungen", json=neue_buchung)

        if antwort.status_code == 200:
            st.success("Buchung wurde gespeichert.")
            st.rerun()
        else:
            st.error("Fehler beim Speichern der Buchung.")

st.header("Gespeicherte Buchungen")

antwort = requests.get(API_URL + "/buchungen")

if antwort.status_code == 200:
    buchungen = antwort.json()

    if len(buchungen) > 0:
        df = pd.DataFrame(buchungen)
        st.dataframe(df)
    else:
        st.info("Es wurden noch keine Buchungen gespeichert.")
else:
    st.error("Buchungen konnten nicht geladen werden.")


st.header("GuV-Auswertung")

antwort_guv = requests.get(API_URL + "/auswertung/guv")

if antwort_guv.status_code == 200:
    guv = antwort_guv.json()

    einnahmen = guv["einnahmen"]
    ausgaben = guv["ausgaben"]
    gewinn = guv["gewinn"]

    spalte1, spalte2, spalte3 = st.columns(3)

    spalte1.metric("Einnahmen", f"{einnahmen:.2f} EUR")
    spalte2.metric("Ausgaben", f"{ausgaben:.2f} EUR")
    spalte3.metric("Gewinn", f"{gewinn:.2f} EUR")

    st.subheader("Mini-Dashboard")

    werte = [einnahmen, ausgaben, gewinn]
    namen = ["Einnahmen", "Ausgaben", "Gewinn"]

    fig, ax = plt.subplots()
    ax.bar(namen, werte)
    ax.set_ylabel("Betrag in EUR")
    ax.set_title("Uebersicht der GuV")

    st.pyplot(fig)

else:
    st.error("Die GuV-Auswertung konnte nicht geladen werden.")


st.subheader("Ausgaben nach Kategorie")

antwort_kategorien = requests.get(API_URL + "/auswertung/kategorien")

if antwort_kategorien.status_code == 200:
    kategorien = antwort_kategorien.json()

    if len(kategorien) > 0:
        df_kategorien = pd.DataFrame(kategorien)

        st.dataframe(df_kategorien)

        fig2, ax2 = plt.subplots()
        ax2.bar(df_kategorien["kategorie"], df_kategorien["betrag"])
        ax2.set_ylabel("Betrag in EUR")
        ax2.set_title("Ausgaben nach Kategorie")

        st.pyplot(fig2)
    else:
        st.info("Es wurden noch keine Ausgaben gespeichert.")
else:
    st.error("Die Kategorie-Auswertung konnte nicht geladen werden.")
