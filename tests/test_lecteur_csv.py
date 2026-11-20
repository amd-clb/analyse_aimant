import tempfile
import unittest
from pathlib import Path

from lecteur_csv import charger_aimants


class ChargerAimantsTests(unittest.TestCase):
    def test_charge_csv_francais_et_convertit_le_grade_en_mt(self):
        contenu = (
            "diamètre_mm;hauteur_mm;grade\n"
            "3,175;1,5875;N35\n"
            "5;2;N52\n"
        )
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "aimants.csv"
            chemin.write_text(contenu, encoding="utf-8")

            aimants = charger_aimants(chemin)

        self.assertEqual(len(aimants), 2)
        self.assertEqual(aimants[0].diametre_mm, 3.175)
        self.assertEqual(aimants[0].br_mt, 1190.0)
        self.assertEqual(aimants[1].br_mt, 1450.0)

    def test_convertit_pouces_fractions_et_millimetres_en_mm(self):
        contenu = (
            "diametre;hauteur;grade\n"
            "1/8\";1/16\";N35\n"
            "2.4mm;1.5 mm;N45\n"
            "3.175;1,5875;N52\n"
        )
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "aimants.csv"
            chemin.write_text(contenu, encoding="utf-8")

            aimants = charger_aimants(chemin)

        self.assertAlmostEqual(aimants[0].diametre_mm, 3.175)
        self.assertAlmostEqual(aimants[0].hauteur_mm, 1.5875)
        self.assertEqual(aimants[1].diametre_mm, 2.4)
        self.assertEqual(aimants[1].hauteur_mm, 1.5)
        self.assertEqual(aimants[2].diametre_mm, 3.175)
        self.assertEqual(aimants[2].hauteur_mm, 1.5875)

    def test_signale_un_grade_non_repertorie(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "aimants.csv"
            chemin.write_text(
                "diametre_mm;hauteur_mm;grade\n3;2;N99\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "Grade inconnu"):
                charger_aimants(chemin)

    def test_signale_une_fraction_invalide(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "aimants.csv"
            chemin.write_text(
                'diametre;hauteur;grade\n1/0";1/16";N52\n',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "longueur invalide"):
                charger_aimants(chemin)


if __name__ == "__main__":
    unittest.main()
