from dataclasses import dataclass
import math


BR_NOMINAL_MT = {
    "N35": 1190.0,
    "N38": 1240.0,
    "N40": 1270.0,
    "N42": 1300.0,
    "N45": 1350.0,
    "N48": 1400.0,
    "N50": 1430.0,
    "N52": 1450.0,
}


@dataclass(frozen=True)
class Aimant:
    diametre_mm: float
    hauteur_mm: float
    grade: str

    def __post_init__(self):
        if not math.isfinite(self.diametre_mm) or self.diametre_mm <= 0:
            raise ValueError("Le diamètre doit être un nombre positif.")
        if not math.isfinite(self.hauteur_mm) or self.hauteur_mm <= 0:
            raise ValueError("La hauteur doit être un nombre positif.")

        grade = self.grade.strip().upper()
        if grade not in BR_NOMINAL_MT:
            grades = ", ".join(BR_NOMINAL_MT)
            raise ValueError(f"Grade inconnu {self.grade!r}. Grades acceptés : {grades}.")
        object.__setattr__(self, "grade", grade)

    @property
    def br_mt(self):
        return BR_NOMINAL_MT[self.grade]
