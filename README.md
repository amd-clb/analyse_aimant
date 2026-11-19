# Analyse du champ magnétique d’un aimant

Ce projet visualise le champ magnétique produit par un petit aimant cylindrique N52 dans un demi-tube. Il utilise NumPy pour construire une grille de calcul et Magpylib pour calculer le champ.

## Aimant modélisé

- Format : 1/8 × 1/16 pouce
- Diamètre : 3,175 mm
- Hauteur : 1,5875 mm
- Rémanence : 1450 mT
- Seuil cible : 30 mT
- Grille radiale : 80 points
- Grille d’air gap : 150 points

## Fonctionnalités

- Calcul vectorisé du champ magnétique dans les plans XZ et YZ
- Cartographie 2D de la norme du champ avec Matplotlib
- Courbes d’isochamp à 15, 20, 30, 50, 100, 150 et 200 mT
- Recherche de l’air gap maximal garanti
- Affichage de deux critères :
  - norme totale du champ `|B|`
  - composante axiale `|Bx|`

## Prérequis

- Python 3
- Windows PowerShell
- Un environnement graphique compatible avec Matplotlib

## Installation

Depuis le dossier du projet :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Exécution

```powershell
python visualisation.py
```

Le programme affiche dans la console :

- l’air gap maximal garanti selon `|B|`
- l’air gap maximal garanti pour un capteur à axe X selon `|Bx|`

Une fenêtre Matplotlib présente ensuite les cartes du champ dans les plans XZ et YZ.

## Structure du projet

```text
.
├── visualisation.py
├── requirements.txt
└── README.md
```

## Paramètres modifiables

Les principaux paramètres sont déclarés au début de `visualisation.py` :

```python
D = 2 / 16 * 25.4
H = 1 / 16 * 25.4
Br = 1450.0
B_cible = 30.0

gap_min = 0.1
gap_max = 3.0
```

Il est également possible d’ajuster :

- `np.linspace(0.0, rayon_tube, 80)` pour la résolution radiale
- `np.linspace(gap_min, gap_max, 150)` pour la résolution verticale
- les niveaux affichés dans `ax.contour`
- les paramètres d’affichage de la heatmap

## Dépendances principales

- NumPy
- Matplotlib
- Magpylib
- SciPy
