from dataclasses import dataclass

import magpylib as magpy
import numpy as np

from aimant import Aimant


@dataclass
class ResultatChamp:
    aimant: Aimant
    offsets: np.ndarray
    gaps: np.ndarray
    champ_norme_xz: np.ndarray
    champ_norme_yz: np.ndarray
    champ_bx_xz: np.ndarray

    def gaps_estimés(self, seuil_mt):
        gap_norme = min(
            self.gaps[np.argmin(np.abs(self.champ_norme_xz[-1, :] - seuil_mt))],
            self.gaps[np.argmin(np.abs(self.champ_norme_yz[-1, :] - seuil_mt))],
        )
        gap_bx = self.gaps[
            np.argmin(np.abs(self.champ_bx_xz[-1, :] - seuil_mt))
        ]
        return float(gap_norme), float(gap_bx)


class CalculateurChamp:
    def __init__(
        self,
        seuil_mt=30.0,
        gap_min_mm=0.1,
        gap_max_mm=3.0,
        nombre_offsets=80,
        nombre_gaps=150,
    ):
        self.seuil_mt = seuil_mt
        self.gap_min_mm = gap_min_mm
        self.gap_max_mm = gap_max_mm
        self.nombre_offsets = nombre_offsets
        self.nombre_gaps = nombre_gaps

    def calculer(self, aimant):
        rayon = aimant.diametre_mm / 2.0
        offsets = np.linspace(0.0, rayon, self.nombre_offsets)
        gaps = np.linspace(self.gap_min_mm, self.gap_max_mm, self.nombre_gaps)
        off, gap = np.meshgrid(offsets, gaps, indexing="ij")

        points_xz = np.column_stack(
            [off.ravel(), np.zeros(off.size), aimant.hauteur_mm / 2 + gap.ravel()]
        )
        points_yz = np.column_stack(
            [np.zeros(off.size), off.ravel(), aimant.hauteur_mm / 2 + gap.ravel()]
        )

        source = magpy.magnet.Cylinder(
            polarization=(aimant.br_mt, 0, 0),
            dimension=(aimant.diametre_mm, aimant.hauteur_mm),
        )
        champ_xz = source.getB(points_xz)
        champ_yz = source.getB(points_yz)
        forme = off.shape
        norme_xz = np.linalg.norm(champ_xz, axis=1).reshape(forme)
        norme_yz = np.linalg.norm(champ_yz, axis=1).reshape(forme)
        bx_xz = np.abs(champ_xz[:, 0]).reshape(forme)

        return ResultatChamp(
            aimant=aimant,
            offsets=offsets,
            gaps=gaps,
            champ_norme_xz=norme_xz,
            champ_norme_yz=norme_yz,
            champ_bx_xz=bx_xz,
        )
