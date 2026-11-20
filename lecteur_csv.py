import csv
import math
import re
import unicodedata
from fractions import Fraction
from pathlib import Path

from aimant import Aimant


_FRACTION = re.compile(r"([+-]?\d+)\s*/\s*(\d+)$")
_MIXED_FRACTION = re.compile(r"([+-]?\d+)\s+(\d+)\s*/\s*(\d+)$")


def _normaliser_entete(value):
    normalized = unicodedata.normalize("NFKD", value.strip().lower())
    without_accents = "".join(
        character for character in normalized
        if not unicodedata.combining(character)
    )
    return without_accents.replace(" ", "_")


def _lire_longueur(value, colonne, numero_ligne):
    try:
        texte = value.strip().lower().replace("″", '"').replace("′", "'")
        facteur_mm = 1.0
        if texte.endswith(('"', "'")):
            facteur_mm = 25.4
            texte = texte[:-1].strip()
        else:
            unites_mm = ("millimetres", "millimeters", "millimetre", "millimeter", "mm")
            unites_pouces = ("pouces", "pouce", "inches", "inch", "in", "po")
            unite = next(
                (suffix for suffix in unites_mm + unites_pouces if texte.endswith(suffix)),
                None,
            )
            if unite is not None:
                texte = texte[:-len(unite)].strip()
                if unite in unites_pouces:
                    facteur_mm = 25.4

        texte_nombre = texte.replace(",", ".")
        fraction_mixte = _MIXED_FRACTION.fullmatch(texte_nombre)
        fraction = _FRACTION.fullmatch(texte_nombre)
        if fraction_mixte:
            entier, numerateur, denominateur = map(int, fraction_mixte.groups())
            valeur = entier + math.copysign(
                float(Fraction(numerateur, denominateur)), entier
            )
        elif fraction:
            numerateur, denominateur = map(int, fraction.groups())
            valeur = float(Fraction(numerateur, denominateur))
        else:
            valeur = float(texte_nombre)
        valeur *= facteur_mm
        if not math.isfinite(valeur):
            raise ValueError("la longueur doit être finie")
        return valeur
    except (AttributeError, ValueError, ZeroDivisionError) as error:
        raise ValueError(
            f"Ligne {numero_ligne} : longueur invalide pour "
            f"{colonne!r} : {value!r}."
        ) from error


def charger_aimants(chemin):
    chemin = Path(chemin)
    with chemin.open("r", encoding="utf-8-sig", newline="") as fichier:
        extrait = fichier.read(4096)
        if not extrait.strip():
            raise ValueError(f"Le fichier CSV {chemin} est vide.")
        fichier.seek(0)
        try:
            dialecte = csv.Sniffer().sniff(extrait, delimiters=";,\t")
        except csv.Error as error:
            raise ValueError(
                f"Impossible de détecter le séparateur de {chemin}; "
                "utilisez une virgule ou un point-virgule."
            ) from error

        lecteur = csv.DictReader(fichier, dialect=dialecte)
        if lecteur.fieldnames is None:
            raise ValueError(f"Le fichier CSV {chemin} ne contient pas d'en-tête.")

        colonnes = {_normaliser_entete(name): name for name in lecteur.fieldnames}
        aliases = {
            "diametre": ("diametre_mm", "diametre"),
            "hauteur": ("hauteur_mm", "hauteur"),
            "grade": ("grade",),
        }
        selection = {}
        for cible, noms in aliases.items():
            source = next((colonnes[nom] for nom in noms if nom in colonnes), None)
            if source is None:
                attendues = ", ".join(noms)
                raise ValueError(
                    f"Colonne manquante dans {chemin} : {attendues}."
                )
            selection[cible] = source

        aimants = []
        for numero_ligne, ligne in enumerate(lecteur, start=2):
            try:
                diametre = _lire_longueur(
                    ligne[selection["diametre"]], "diametre", numero_ligne
                )
                hauteur = _lire_longueur(
                    ligne[selection["hauteur"]], "hauteur", numero_ligne
                )
                grade = ligne[selection["grade"]].strip()
                if not grade:
                    raise ValueError(f"Ligne {numero_ligne} : grade vide.")
                aimants.append(Aimant(diametre, hauteur, grade))
            except (AttributeError, KeyError) as error:
                raise ValueError(
                    f"Ligne {numero_ligne} incomplète dans {chemin}."
                ) from error
            except ValueError as error:
                raise ValueError(f"{chemin} : {error}") from error

    if not aimants:
        raise ValueError(f"Aucun aimant trouvé dans {chemin}.")
    return aimants
