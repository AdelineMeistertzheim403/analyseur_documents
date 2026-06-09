# Analyseur de Documents

Application Python avec interface graphique pour analyser des fichiers `.txt` et `.pdf`.

Le projet calcule des statistiques textuelles, détecte les mots fréquents, repère les phrases trop longues et identifie des termes techniques.

## Sommaire

1. Présentation
2. Fonctionnalités
3. Architecture du projet
4. Prérequis
5. Installation
6. Utilisation
7. Détails de l'analyse linguistique
8. Structure des résultats
9. Personnalisation
10. Limitations connues
11. Pistes d'amélioration

## 1. Présentation

Ce projet est conçu pour analyser rapidement des documents académiques ou techniques.

Il inclut :
- une interface graphique moderne (`customtkinter`),
- un moteur d'analyse textuelle (`analyseur.py`),
- un lecteur PDF (`lecteur_pdf.py`) basé sur PyMuPDF,
- un export du rapport (`export_pdf.py`) en format texte.

## 2. Fonctionnalités

- Lecture de fichiers `.txt` et `.pdf`.
- Statistiques globales :
	- nombre de caractères,
	- nombre de mots,
	- nombre de phrases,
	- moyenne de mots par phrase.
- Top des mots fréquents (hors mots ignorés).
- Détection des phrases longues avec seuil configurable dans l'interface.
- Détection de termes techniques saisie par l'utilisateur (un terme par ligne).
- Visualisation graphique :
	- distribution des longueurs de phrases,
	- top mots les plus fréquents.
- Export du rapport d'analyse au format `.txt`.
- Bascule thème clair/sombre dans l'interface.

## 3. Architecture du projet

Arborescence principale :

```text
Analyseur_documents/
├── analyseur.py
├── lecteur_pdf.py
├── export_pdf.py
├── interface.py
├── main.py
├── README.md
└── documents/
```

Rôle des fichiers :

- `main.py`
	- Point d'entrée de l'application.
	- Instancie la fenêtre principale `customtkinter`.

- `interface.py`
	- Interface utilisateur (choix de fichier, lancement analyse, affichage onglets, export).
	- Lit le seuil de détection des phrases longues saisi par l'utilisateur.
	- Appelle `analyser_texte(...)` puis met à jour les onglets.

- `analyseur.py`
	- Cœur métier de l'analyse linguistique.
	- Fonctions de comptage et extraction.
	- Prétraitement robuste pour documents PDF (normalisation, nettoyage, segmentation).

- `lecteur_pdf.py`
	- Extraction du texte brut depuis les pages PDF (`fitz` / PyMuPDF).

- `export_pdf.py`
	- Génération d'un rapport texte à partir du dictionnaire résultat.

## 4. Prérequis

- Python 3.10+ (3.14 fonctionne dans votre environnement actuel).
- Système : Windows, Linux ou macOS.
- Dépendances Python :
	- `customtkinter`
	- `pymupdf`
	- `matplotlib`

## 5. Installation

Depuis la racine du projet :

```bash
python -m venv .venv
```

Activation de l'environnement virtuel :

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (cmd)
.venv\Scripts\activate.bat

# Linux / macOS
source .venv/bin/activate
```

Installation des dépendances :

```bash
pip install customtkinter pymupdf matplotlib
```

## 6. Utilisation

### Lancer l'application

```bash
python main.py
```

### Étapes dans l'interface

1. Cliquer sur `Choisir un fichier`.
2. Sélectionner un document `.txt` ou `.pdf`.
3. Définir la limite "phrase trop longue" (par défaut : `35`).
4. Cliquer sur `Analyser`.
5. Consulter les onglets :
	 - `Statistiques`
	 - `Mots fréquents`
	 - `Phrases longues`
	 - `Termes techniques`
	 - `Graphiques`
6. Cliquer sur `Exporter` pour enregistrer un rapport `.txt`.

## 7. Détails de l'analyse linguistique

### 7.1 Extraction des mots

- Les mots sont extraits avec une expression régulière compatible français.
- Le texte est transformé en minuscules.
- Certains mots-outils sont ignorés via `MOTS_A_IGNORER`.

### 7.2 Comptage des phrases

Le découpage des phrases est renforcé pour de meilleurs résultats sur PDF :

1. Normalisation des retours à la ligne.
2. Re-collage des mots césurés (`mot-\nif` -> `motif`).
3. Option `mode_memoire=True` :
	 - extraction préférentielle de la zone narrative `Introduction -> Conclusion`.
4. Option `filtrer_blocs_non_narratifs_actif=True` :
	 - suppression de lignes non narratives (figures, annexes, blocs techniques, etc.).
5. Segmentation en phrases via ponctuation terminale (`.`, `!`, `?`).

### 7.3 Phrases longues

- Une phrase est signalée si son nombre de mots est strictement supérieur au seuil choisi.
- Le seuil est transmis depuis l'interface via :
	- `analyser_texte(texte, limite_phrase_longue=...)`

### 7.4 Termes techniques

Le module recherche les termes saisis dans l'interface (un terme par ligne).

### 7.5 Graphiques

L'onglet `Graphiques` affiche :
- un histogramme de la distribution des longueurs de phrases,
- un diagramme en barres horizontal des mots les plus fréquents.

## 8. Structure des résultats

La fonction `analyser_texte(...)` retourne un dictionnaire avec les clés :

```python
{
		"nombre_caracteres": int,
		"nombre_mots": int,
		"nombre_phrases": int,
		"mots_frequents": list[tuple[str, int]],
		"phrases_longues": list[dict],
		"longueurs_phrases": list[int],
		"termes_techniques": list[str]
}
```

Exemple d'élément dans `phrases_longues` :

```python
{
		"phrase": "...",
		"nombre_mots": 42
}
```

## 9. Personnalisation

### 9.1 Ajouter des mots à ignorer

Modifier l'ensemble `MOTS_A_IGNORER` dans `analyseur.py`.

### 9.2 Définir les termes techniques

Saisir les termes dans la zone dédiée de l'interface (un terme par ligne).

### 9.3 Changer le nombre de mots fréquents affichés

La fonction `mots_les_plus_frequents(texte, nombre=10)` utilise `10` par défaut.

### 9.4 Ajuster les heuristiques PDF

Vous pouvez adapter :
- `extraire_zone_memoire(...)`
- `filtrer_blocs_non_narratifs(...)`
- `est_ligne_parasite(...)`

selon le type de documents analysés.

## 10. Limitations connues

- Certains PDF très bruités (colonnes, tableaux complexes, OCR imparfait) peuvent encore perturber la segmentation des phrases.
- La détection des termes techniques fonctionne par présence textuelle simple (pas de modèle NLP contextuel).
- Le projet n'implémente pas encore de tests automatisés.

## 11. Pistes d'amélioration

- Ajouter une configuration utilisateur persistante (JSON/YAML) pour :
	- seuil phrase longue,
	- mots ignorés,
	- termes techniques.
- Exporter aussi en `.csv` ou `.json`.
- Intégrer des tests unitaires (`pytest`) pour `analyseur.py`.
- Ajouter un mode CLI pour automatiser les analyses en lot.
