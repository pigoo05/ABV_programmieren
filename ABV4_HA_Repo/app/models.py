from dataclasses import dataclass
from app.utils import normalize_name


@dataclass
class Student:
    name: str
    points: int
    passed: bool

    @classmethod
    def from_csv_row(cls, row):
        name = normalize_name(row["name"])
        points = int(row["points"])
        passed = bool(row["passed"])
        return cls(name=name, points=points, passed=passed)
