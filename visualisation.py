import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from calculateur import CalculateurChamp
from lecteur_csv import charger_aimants
from visualiseur import VisualiseurChamp


def analyser(csv_path, output_path):
    aimants = charger_aimants(csv_path)
    calculateur = CalculateurChamp()
    resultats = [calculateur.calculer(aimant) for aimant in aimants]

    for resultat in resultats:
        aimant = resultat.aimant
        gap_norme, gap_bx = resultat.gaps_estimés(calculateur.seuil_mt)
        print(
            f"{aimant.grade} Ø{aimant.diametre_mm:g} × "
            f"{aimant.hauteur_mm:g} mm (Br={aimant.br_mt:.0f} mT) :"
        )
        print(
            f"  Air gap estimé selon |B|  : "
            f"{gap_norme:.2f} mm"
        )
        print(
            f"  Air gap estimé selon |Bx| : "
            f"{gap_bx:.2f} mm"
        )

    visualiseur = VisualiseurChamp(seuil_mt=calculateur.seuil_mt)
    figure = visualiseur.creer_figure(resultats, chemin_image=output_path)
    chemin_image = Path(output_path)
    print(f"Image enregistrée : {chemin_image.resolve()}")
    plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Compare les champs magnétiques d'aimants définis dans un CSV."
    )
    parser.add_argument(
        "--csv",
        default="aimants.csv",
        help="Fichier CSV des aimants (défaut : aimants.csv).",
    )
    parser.add_argument(
        "--sortie",
        default="comparaison_aimants.png",
        help="Chemin de l'image à enregistrer (défaut : comparaison_aimants.png).",
    )
    arguments = parser.parse_args()
    analyser(Path(arguments.csv), Path(arguments.sortie))


if __name__ == "__main__":
    main()
