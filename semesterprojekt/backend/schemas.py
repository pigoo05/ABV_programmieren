from pydantic import BaseModel


class Buchung(BaseModel):
    datum: str
    betrag: float
    kategorie: str
    typ: str
    beschreibung: str = ""
