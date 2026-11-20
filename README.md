# Analyse et comparaison de champs magnétiques

Le programme compare plusieurs aimants cylindriques à partir d’un fichier CSV. Il convertit leur grade en rémanence nominale `Br`, calcule le champ dans deux directions de déplacement autour de l’aimant, affiche les cartes avec une échelle commune et enregistre l’image.

## Grades pris en charge

Grades disponibles : **N35, N38, N40, N42, N45, N48, N50 et N52**. Les valeurs nominales de la table fournie sont converties de teslas en milliteslas :

| Grade | Br nominal (T) | Br utilisé (mT) |
|---|---:|---:|
| N35 | 1,19 | 1190 |
| N38 | 1,24 | 1240 |
| N40 | 1,27 | 1270 |
| N42 | 1,30 | 1300 |
| N45 | 1,35 | 1350 |
| N48 | 1,40 | 1400 |
| N50 | 1,43 | 1430 |
| N52 | 1,45 | 1450 |

Un grade inconnu ou une dimension invalide produit une erreur explicite.

## Format CSV

Le fichier `aimants.csv` fourni sert d’exemple et de modèle :

```csv
diametre;hauteur;grade
1/8in;1/16in;N35
3.175mm;1.5875mm;N45
0.125in;0.0625in;N52
```

Les dimensions sont converties en millimètres avant le calcul. Vous pouvez écrire `1/16"`, `1/16in`, `2.4mm`, ou un nombre sans unité (interprété en millimètres). Les fractions et les décimales avec point ou virgule sont acceptées; un pouce vaut exactement 25,4 mm. Les en-têtes `diametre`/`diamètre` et `hauteur`, avec ou sans suffixe `_mm`, sont acceptés. Le séparateur `;` permet d’utiliser les virgules décimales françaises. Les grades ne sont pas sensibles à la casse.

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Exécution

Depuis le dossier du projet :

```powershell
python visualisation.py
```

Par défaut, le programme lit `aimants.csv`, affiche les résultats dans la console et enregistre l’image sous `comparaison_aimants.png` avant d’ouvrir la fenêtre Matplotlib.

Dans la fenêtre, le curseur **Seuil |B| (mT)** déplace la courbe rouge. Vous pouvez aussi saisir directement une valeur dans le champ **Saisie (mT)**, puis valider avec Entrée. Les décimales avec un point ou une virgule sont acceptées; la valeur doit être comprise entre 1 mT et la limite du curseur. Une saisie invalide affiche un message et conserve le seuil précédent. Les valeurs d’air gap estimées pour `|B|` et `|Bx|` suivent le seuil sélectionné. L’image PNG est mise à jour automatiquement quand le seuil change.

Les chemins peuvent être précisés :

```powershell
python visualisation.py --csv chemin\vers\aimants.csv --sortie resultats\comparaison.png
```

Chaque aimant occupe une rangée avec deux vues décrites sans abréviations de plans : déplacement radial parallèle à l’aimantation (+X) et déplacement radial perpendiculaire à l’aimantation (+Y). Une échelle de couleur commune facilite la comparaison. Le résumé console indique pour chaque aimant l’air gap estimé selon `|B|` et selon `|Bx|`.

## Organisation du code

- `aimant.py` : modèle de l’aimant et conversion grade–`Br`
- `lecteur_csv.py` : validation et chargement du CSV
- `calculateur.py` : calcul vectorisé du champ avec Magpylib
- `visualiseur.py` : comparaison et sauvegarde des figures
- `visualisation.py` : point d’entrée en ligne de commande
- `tests/` : tests du chargement CSV et de la conversion des grades
