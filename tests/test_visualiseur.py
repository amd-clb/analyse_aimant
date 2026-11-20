import tempfile
import unittest
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from aimant import Aimant
from calculateur import ResultatChamp
from visualiseur import VisualiseurChamp


class VisualiseurChampTests(unittest.TestCase):
    def test_le_slider_actualise_le_seuil_et_sauvegarde_l_image(self):
        aimant = Aimant(2.0, 1.0, "N35")
        resultat = ResultatChamp(
            aimant=aimant,
            offsets=np.array([0.0, 1.0]),
            gaps=np.array([0.1, 1.0, 2.0]),
            champ_norme_xz=np.array([[100.0, 60.0, 20.0], [80.0, 40.0, 10.0]]),
            champ_norme_yz=np.array([[110.0, 70.0, 30.0], [90.0, 50.0, 20.0]]),
            champ_bx_xz=np.array([[70.0, 40.0, 15.0], [50.0, 25.0, 5.0]]),
        )
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "comparaison.png"
            visualiseur = VisualiseurChamp()
            figure = visualiseur.creer_figure([resultat], chemin_image=chemin)

            try:
                visualiseur._slider.set_val(40)

                self.assertIn("40 mT", figure._suptitle.get_text())
                self.assertTrue(chemin.is_file())
                self.assertGreater(chemin.stat().st_size, 0)

                visualiseur._text_box.set_val("45,5")
                visualiseur._on_text_submit("45,5")

                self.assertAlmostEqual(visualiseur._slider.val, 45.5)
                self.assertIn("45.5 mT", figure._suptitle.get_text())

                visualiseur._on_text_submit("invalide")

                self.assertAlmostEqual(visualiseur._slider.val, 45.5)
                self.assertIn("Valeur invalide", figure._suptitle.get_text())
            finally:
                plt.close(figure)


if __name__ == "__main__":
    unittest.main()
