import numpy as np
import matplotlib.pyplot as plt
import magpylib as magpy

# --- 1. PARAMÈTRES DE L'AIMANT & DU TUBE ---
D = 2/16 * 25.4             # Diamètre 1/8" (mm)
H = 1/16 * 25.4                  # Hauteur 1/16" (mm)
Br = 1450.0                 # Rémanence N52 (mT)
B_cible = 30.0              # Seuil cible (mT)

rayon_tube = D / 2.0        # Rayon d'analyse du tube : de 0 (axe) à D/2 (bord de l'aimant)
gap_min = 0.1               # Air gap min depuis la face plate (mm)
gap_max = 3.0               # Air gap max depuis la face plate (mm)

# Création de la grille 2D sur le demi-plan [0, rayon_tube] par symétrie
offsets = np.linspace(0.0, rayon_tube, 80)   # Axe horizontal : décalage radial r (mm)
gaps = np.linspace(gap_min, gap_max, 150)    # Axe vertical : air gap surface (mm)
OFF, G = np.meshgrid(offsets, gaps, indexing='ij')

# Points d'observation dans les 2 plans orthogonaux (XZ = vers pôle +X, YZ = perpendiculaire +Y)
pts_XZ = np.column_stack([OFF.ravel(), np.zeros(OFF.size), H/2 + G.ravel()])
pts_YZ = np.column_stack([np.zeros(OFF.size), OFF.ravel(), H/2 + G.ravel()])

# --- 2. CALCUL DU CHAMP VIA MAGPYLIB (CPU VECTORISÉ) ---
aimant = magpy.magnet.Cylinder(polarization=(Br, 0, 0), dimension=(D, H))

B_vec_XZ = aimant.getB(pts_XZ)
B_vec_YZ = aimant.getB(pts_YZ)

B_norm_XZ = np.linalg.norm(B_vec_XZ, axis=1).reshape(OFF.shape)
B_norm_YZ = np.linalg.norm(B_vec_YZ, axis=1).reshape(OFF.shape)
Bx_XZ = np.abs(B_vec_XZ[:, 0]).reshape(OFF.shape)

# --- 3. EXTRACTION DES AIR GAPS MAX GARANTIS AU BORD DU TUBE (r = rayon_tube) ---
g_garanti_norme = min(
    gaps[np.argmin(np.abs(B_norm_XZ[-1, :] - B_cible))],
    gaps[np.argmin(np.abs(B_norm_YZ[-1, :] - B_cible))]
)
g_garanti_Bx = gaps[np.argmin(np.abs(Bx_XZ[-1, :] - B_cible))]

print(f"Air gap MAX garanti (|B| >= {B_cible} mT sur r in [0, {rayon_tube:.3f} mm]) : {g_garanti_norme:.2f} mm")
print(f"Air gap MAX garanti (|Bx| >= {B_cible} mT capteur 1-axe X)               : {g_garanti_Bx:.2f} mm")

# --- 4. VISUALISATION HEATMAP 2D ---
fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharey=True)

configs = [
    (B_norm_XZ, "Plan XZ (Décalage vers le pôle +X)"),
    (B_norm_YZ, "Plan YZ (Décalage perpendiculaire +Y)")
]

for ax, (data, titre) in zip(axes, configs):
    im = ax.pcolormesh(OFF, G, data, shading='auto', cmap='viridis', vmin=0, vmax=250)
    cs = ax.contour(
        OFF, G, data,
        levels=[15, 20, 30, 50, 100, 150, 200],
        colors=['white', 'white', '#EF4444', 'white', 'white', 'white', 'white'],
        linewidths=[0.9, 0.9, 2.5, 0.9, 0.9, 0.9, 0.9]
    )
    ax.clabel(cs, inline=True, fontsize=8.5, fmt='%d mT')
    ax.set_title(titre, fontweight='bold')
    ax.set_xlabel("Décalage radial r (mm) [0 = axe central]")

axes[0].set_ylabel("Air gap depuis la face plate supérieure (mm)")
cbar = fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.92, pad=0.02)
cbar.set_label("Densité de flux magnétique |B| (mT)")

plt.suptitle(
    f"Cartographie 2D dans le demi-tube (r = 0 à {rayon_tube:.2f} mm) — Aimant N52 Ø{D}×{H} mm\n"
    f"Air gap max garanti au bord (r={rayon_tube:.2f} mm) : {g_garanti_norme:.2f} mm (|B|) | {g_garanti_Bx:.2f} mm (|Bx|)",
    fontsize=10.5, fontweight='bold', y=1.03
)
plt.show()