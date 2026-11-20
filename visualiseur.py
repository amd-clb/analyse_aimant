import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, TextBox


class VisualiseurChamp:
    NIVEAUX_MT = (15, 20, 50, 100, 150, 200)

    def __init__(self, seuil_mt=30.0):
        self.seuil_mt = seuil_mt
        self._slider = None
        self._text_box = None
        self._on_text_submit = None

    def creer_figure(self, resultats, chemin_image=None):
        if not resultats:
            raise ValueError("Aucun résultat à visualiser.")

        nombre = len(resultats)
        figure = plt.figure(
            figsize=(11, max(6.5, 4.2 * nombre + 1.3)),
            constrained_layout=True,
        )
        grille = figure.add_gridspec(
            nrows=nombre + 1,
            ncols=2,
            height_ratios=[1] * nombre + [0.18],
        )
        axes = np.empty((nombre, 2), dtype=object)
        for ligne in range(nombre):
            for colonne in range(2):
                if ligne == 0 and colonne == 0:
                    axes[ligne, colonne] = figure.add_subplot(grille[ligne, colonne])
                else:
                    axes[ligne, colonne] = figure.add_subplot(
                        grille[ligne, colonne],
                        sharex=axes[0, 0],
                        sharey=axes[0, 0],
                    )

        controles = grille[nombre, :].subgridspec(
            nrows=1,
            ncols=2,
            width_ratios=(3, 1),
            wspace=0.08,
        )
        slider_ax = figure.add_subplot(controles[0, 0])
        text_box_ax = figure.add_subplot(controles[0, 1])
        maximum = max(
            float(np.max(data))
            for resultat in resultats
            for data in (resultat.champ_norme_xz, resultat.champ_norme_yz)
        )
        vmax = max(250.0, math.ceil(maximum / 50.0) * 50.0)
        niveaux = [niveau for niveau in self.NIVEAUX_MT if niveau < maximum]

        image = None
        panels = []
        for ligne, resultat in enumerate(resultats):
            aimant = resultat.aimant
            titre_aimant = (
                f"{aimant.grade} — Ø{aimant.diametre_mm:g} × "
                f"{aimant.hauteur_mm:g} mm — Br {aimant.br_mt:.0f} mT"
            )
            directions = (
                (
                    resultat.champ_norme_xz,
                    "Déplacement radial parallèle à l’aimantation (+X)",
                ),
                (
                    resultat.champ_norme_yz,
                    "Déplacement radial perpendiculaire à l’aimantation (+Y)",
                ),
            )
            for colonne, (data, direction) in enumerate(directions):
                ax = axes[ligne, colonne]
                image = ax.pcolormesh(
                    resultat.offsets,
                    resultat.gaps,
                    data.T,
                    shading="auto",
                    cmap="viridis",
                    vmin=0,
                    vmax=vmax,
                )
                if niveaux:
                    contours = ax.contour(
                        resultat.offsets,
                        resultat.gaps,
                        data.T,
                        levels=niveaux,
                        colors="white",
                        linewidths=0.8,
                    )
                    ax.clabel(contours, inline=True, fontsize=8, fmt="%d mT")
                ax.set_title(
                    f"{titre_aimant}\n{direction}",
                    fontsize=9,
                    fontweight="bold",
                )
                ax.set_xlabel("Décalage radial (mm)")
                if colonne == 0:
                    ax.set_ylabel("Air gap depuis la face (mm)")
                panels.append((ax, data, resultat))

        figure.colorbar(
            image,
            ax=axes.ravel().tolist(),
            shrink=0.92,
            pad=0.02,
            label="Densité de flux magnétique |B| (mT)",
        )
        titre = figure.suptitle(
            "",
            fontsize=12,
            fontweight="bold",
        )
        seuil_max = max(100.0, math.ceil(maximum / 50.0) * 50.0)
        self._slider = Slider(
            slider_ax,
            "Seuil |B| (mT)",
            1.0,
            seuil_max,
            valinit=min(self.seuil_mt, seuil_max),
            valstep=0.1,
            valfmt="%1.1f",
        )
        self._text_box = TextBox(
            text_box_ax,
            "Saisie (mT)",
            initial=f"{self._slider.val:g}",
        )
        contours_seuil = []

        def actualiser_seuil(valeur):
            seuil = float(valeur)
            self.seuil_mt = seuil
            for contour in contours_seuil:
                contour.remove()
            contours_seuil.clear()

            for ax, data, resultat in panels:
                if float(np.min(data)) < seuil < float(np.max(data)):
                    contour = ax.contour(
                        resultat.offsets,
                        resultat.gaps,
                        data.T,
                        levels=[seuil],
                        colors="#EF4444",
                        linewidths=2.5,
                    )
                    contours_seuil.append(contour)

            titre.set_text(
                f"Comparaison des champs magnétiques — "
                f"seuil sélectionné : {seuil:g} mT (courbe rouge)"
            )
            titre.set_color("black")
            self._text_box.set_val(f"{seuil:g}")
            for ligne, resultat in enumerate(resultats):
                gap_norme, gap_bx = resultat.gaps_estimés(seuil)
                axes[ligne, 1].set_title(
                    "Déplacement radial perpendiculaire à l’aimantation (+Y)\n"
                    f"Air gap estimé au seuil : |B| {gap_norme:.2f} mm"
                    f" — |Bx| {gap_bx:.2f} mm",
                    fontsize=9,
                    fontweight="bold",
                )
            figure.canvas.draw_idle()
            if chemin_image is not None:
                self.enregistrer(figure, chemin_image)

        def soumettre_seuil(texte):
            try:
                seuil = float(texte.strip().replace(",", "."))
            except ValueError:
                titre.set_text(
                    f"Valeur invalide. Entrez un nombre entre 1 et "
                    f"{seuil_max:g} mT; seuil conservé : {self.seuil_mt:g} mT."
                )
                titre.set_color("red")
                self._text_box.set_val(f"{self.seuil_mt:g}")
                figure.canvas.draw_idle()
                return

            if not math.isfinite(seuil) or not 1.0 <= seuil <= seuil_max:
                titre.set_text(
                    f"Valeur invalide. Entrez un nombre entre 1 et "
                    f"{seuil_max:g} mT; seuil conservé : {self.seuil_mt:g} mT."
                )
                titre.set_color("red")
                self._text_box.set_val(f"{self.seuil_mt:g}")
                figure.canvas.draw_idle()
                return

            self._slider.set_val(seuil)

        self._slider.on_changed(actualiser_seuil)
        self._text_box.on_submit(soumettre_seuil)
        self._on_text_submit = soumettre_seuil
        actualiser_seuil(self._slider.val)
        return figure

    def enregistrer(self, figure, chemin):
        chemin = Path(chemin)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(chemin, dpi=200, bbox_inches="tight")
        return chemin
