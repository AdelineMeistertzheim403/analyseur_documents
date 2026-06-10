# Analyseur de Documents

Application Python avec interface graphique pour analyser des fichiers `.txt` et `.pdf`.

Le projet calcule des statistiques textuelles, détecte les mots fréquents, repère les phrases trop longues, analyse leur complexité, identifie les termes techniques présents ou absents, génère un résumé qualité, puis permet d'exporter les résultats et les graphiques.

## Sommaire

1. Présentation
2. Fonctionnalités
3. Architecture du projet
4. Installation complète
5. Utilisation
6. Détails de l'analyse
7. Structure des résultats
8. Personnalisation
9. Limitations connues
10. Pistes d'amélioration

## 1. Présentation

Ce projet est conçu pour analyser rapidement des documents académiques ou techniques.

Il inclut :

- une interface graphique avec `customtkinter`,
- un moteur d'analyse textuelle,
- une extraction PDF basée sur PyMuPDF,
- un résumé qualité lisible,
- un export de rapport en plusieurs formats,
- un export séparé des graphiques.

## 2. Fonctionnalités

- Lecture de fichiers `.txt` et `.pdf`.
- Statistiques globales :
  - nombre de caractères,
  - nombre de mots,
  - nombre de phrases,
  - moyenne de mots par phrase.
- Score de lisibilité sur 100.
- Résumé qualité avec points forts, points à améliorer et recommandations.
- Top des mots fréquents.
- Détection des phrases longues avec seuil configurable.
- Affichage de la page PDF associée aux phrases longues.
- Détection des phrases longues à risque :
  - beaucoup de virgules,
  - parenthèses,
  - connecteurs logiques,
  - manque de ponctuation interne.
- Suggestions simples pour couper certaines phrases longues.
- Détection des termes techniques avec nombre d'occurrences.
- Affichage des termes techniques non trouvés.
- Options d'analyse dans l'interface :
  - ignorer les titres,
  - ignorer figures, tableaux et annexes,
  - analyser seulement la zone Introduction → Conclusion.
- Graphiques :
  - distribution des longueurs de phrases,
  - top des mots les plus fréquents.
- Export du rapport aux formats `.pdf`, `.html`, `.txt` et `.csv`.
- Export des graphiques aux formats `.png`, `.pdf` et `.svg`.
- Bascule thème clair/sombre.

## 3. Architecture du projet

```text
Analyseur_documents/
├── analyseur.py
├── analyseur_phrases.py
├── lecteur_pdf.py
├── export_pdf.py
├── interface.py
├── interface_helpers.py
├── main.py
└── README.md
```

Rôle des fichiers :

- `main.py` : point d'entrée de l'application.
- `interface.py` : interface utilisateur, options d'analyse, onglets et boutons d'export.
- `interface_helpers.py` : formatage des résultats et génération des graphiques.
- `analyseur.py` : coordination de l'analyse globale.
- `analyseur_phrases.py` : découpage des phrases, détection des phrases longues et complexité.
- `lecteur_pdf.py` : extraction du texte PDF et conservation des numéros de page.
- `export_pdf.py` : export des rapports et des graphiques.

## 4. Installation complète

Cette section part du principe que Python n'est pas encore installé sur la machine.

### 4.1 Installer Python

Le projet nécessite Python `3.10` ou plus récent.

#### Windows

1. Aller sur le site officiel : <https://www.python.org/downloads/>
2. Télécharger la dernière version stable de Python pour Windows.
3. Lancer l'installateur.
4. Cocher impérativement :

```text
Add python.exe to PATH
```

5. Cliquer sur `Install Now`.
6. Ouvrir PowerShell ou l'invite de commandes, puis vérifier :

```bash
python --version
pip --version
```

Si la commande `python` ne fonctionne pas, essayer :

```bash
py --version
```

#### macOS

Méthode recommandée avec Homebrew :

1. Installer Homebrew si nécessaire : <https://brew.sh/>
2. Installer Python :

```bash
brew install python
```

3. Vérifier l'installation :

```bash
python3 --version
pip3 --version
```

Autre méthode possible : télécharger Python depuis <https://www.python.org/downloads/macos/>.

#### Linux

Sur Ubuntu ou Debian :

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-tk
```

Sur certaines versions d'Ubuntu, `pip` et la création d'environnements virtuels ne sont pas installés par défaut. Les paquets importants sont donc :

- `python3` : le langage Python,
- `python3-pip` : l'outil d'installation des dépendances,
- `python3-venv` : la création de l'environnement virtuel `.venv`,
- `python3-tk` : nécessaire pour l'interface graphique Tkinter.

Sur Fedora :

```bash
sudo dnf install python3 python3-pip
```

Sur Arch Linux :

```bash
sudo pacman -S python python-pip
```

Vérifier ensuite :

```bash
python3 --version
python3 -m pip --version
```

Si `python3 -m pip --version` affiche `No module named pip`, installer ou réinstaller `pip` :

```bash
sudo apt update
sudo apt install python3-pip
```

### 4.2 Récupérer le projet

Si le projet est déjà sur la machine, ouvrir un terminal dans le dossier `Analyseur_documents`.

Sinon, avec Git :

```bash
git clone <url-du-repot>
cd Analyseur_documents
```

Si le projet a été téléchargé en `.zip`, le décompresser puis ouvrir un terminal dans le dossier extrait.

### 4.3 Créer un environnement virtuel

L'environnement virtuel permet d'installer les dépendances du projet sans modifier le Python global de la machine.

#### Windows

```bash
python -m venv .venv
```

Si `python` ne fonctionne pas :

```bash
py -m venv .venv
```

#### macOS / Linux

```bash
python3 -m venv .venv
```

Vérifier ensuite que le fichier d'activation existe :

```bash
ls .venv/bin/activate
```

Si cette commande affiche `Aucun fichier ou dossier de ce nom`, l'environnement virtuel n'a pas été créé. Sur Ubuntu / Debian, installer d'abord le paquet manquant :

```bash
sudo apt update
sudo apt install python3-venv
python3 -m venv .venv
```

### 4.4 Activer l'environnement virtuel

#### Windows PowerShell

```bash
.venv\Scripts\Activate.ps1
```

Si PowerShell bloque l'activation avec une erreur de politique d'exécution :

```bash
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Puis relancer :

```bash
.venv\Scripts\Activate.ps1
```

#### Windows cmd

```bash
.venv\Scripts\activate.bat
```

#### macOS / Linux

```bash
source .venv/bin/activate
```

Une fois activé, le terminal affiche généralement `(.venv)` au début de la ligne.

Attention : il faut bien activer le fichier `activate`, pas le dossier `bin`.

Commande correcte :

```bash
source .venv/bin/activate
```

Commande incorrecte :

```bash
source .venv/bin
```

### 4.5 Installer les dépendances

Avec l'environnement virtuel activé :

#### Windows

```bash
python -m pip install --upgrade pip
python -m pip install customtkinter pymupdf matplotlib
```

#### macOS / Linux

```bash
python -m pip install --upgrade pip
python -m pip install customtkinter pymupdf matplotlib
```

Après activation de `.venv`, la commande `python` doit normalement pointer vers le Python de l'environnement virtuel. Pour vérifier :

```bash
which python
python -m pip --version
```

Le chemin doit contenir `.venv`.

### 4.6 Lancer l'application

#### Windows

```bash
python main.py
```

Ou, si nécessaire :

```bash
py main.py
```

#### macOS / Linux

```bash
python3 main.py
```

### 4.7 Résolution des problèmes fréquents

#### `python` n'est pas reconnu sur Windows

- Vérifier que Python est installé.
- Réinstaller Python en cochant `Add python.exe to PATH`.
- Essayer la commande `py` à la place de `python`.

#### `pip` n'est pas reconnu

Utiliser plutôt :

```bash
python -m pip --version
```

Ou sur macOS / Linux :

```bash
python3 -m pip --version
```

Sur Ubuntu / Debian, si le message est :

```text
/usr/bin/python3: No module named pip
```

installer `pip` :

```bash
sudo apt update
sudo apt install python3-pip
```

Puis revenir dans le dossier du projet et recréer l'environnement virtuel si nécessaire :

```bash
cd Analyseur_documents
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install customtkinter pymupdf matplotlib
```

#### `.venv/bin/activate` est introuvable sur Linux ou macOS

Ce message signifie généralement que l'environnement virtuel n'a pas encore été créé, ou que le terminal n'est pas placé dans le dossier du projet.

Vérifier le dossier courant :

```bash
pwd
ls
```

Le dossier doit contenir `main.py`, `README.md` et les autres fichiers du projet.

Créer ensuite l'environnement virtuel :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Sur Ubuntu / Debian, si la création échoue, installer `python3-venv` :

```bash
sudo apt update
sudo apt install python3-venv
python3 -m venv .venv
source .venv/bin/activate
```

#### `python3 -m install ...` affiche `No module named install`

La commande est incomplète : il manque `pip`.

Commande incorrecte :

```bash
python3 -m install customtkinter pymupdf matplotlib
```

Commande correcte, une fois `.venv` activé :

```bash
python -m pip install customtkinter pymupdf matplotlib
```

#### Erreur avec `customtkinter`, `fitz` ou `matplotlib`

Réinstaller les dépendances dans l'environnement virtuel :

```bash
python -m pip install customtkinter pymupdf matplotlib
```

Sur macOS / Linux :

```bash
python3 -m pip install customtkinter pymupdf matplotlib
```

#### L'interface graphique ne s'ouvre pas sous Linux

Installer les composants Tkinter du système.

Ubuntu / Debian :

```bash
sudo apt update
sudo apt install python3-tk
```

Si l'erreur indique exactement :

```text
ModuleNotFoundError: No module named 'tkinter'
```

cela signifie que Python fonctionne, que les dépendances du projet peuvent être installées, mais que le module graphique système `tkinter` manque.

Sur Ubuntu, faire :

```bash
sudo apt update
sudo apt install python3-tk
```

Puis vérifier :

```bash
python3 -c "import tkinter; print('Tkinter OK')"
```

Si la machine utilise Python 3.12 et que l'erreur continue, installer le paquet spécifique :

```bash
sudo apt install python3.12-tk
```

Puis relancer depuis le dossier du projet :

```bash
source .venv/bin/activate
python main.py
```

Après activation de `.venv`, utiliser plutôt `python main.py` que `python3 main.py`, pour être sûr d'utiliser l'environnement virtuel actif.

Fedora :

```bash
sudo dnf install python3-tkinter
```

## 5. Utilisation

Lancer l'application :

```bash
python main.py
```

Sur macOS / Linux, utiliser plutôt :

```bash
python3 main.py
```

Étapes dans l'interface :

1. Cliquer sur `Choisir un fichier`.
2. Sélectionner un document `.txt` ou `.pdf`.
3. Définir la limite `Phrase trop longue à partir de`.
4. Ajuster les options d'analyse si besoin.
5. Cliquer sur `Analyser`.
6. Consulter les onglets :
   - `Statistiques`
   - `Résumé qualité`
   - `Mots fréquents`
   - `Phrases longues`
   - `Termes techniques`
   - `Graphiques`
7. Cliquer sur `Exporter rapport` pour enregistrer un rapport.
8. Cliquer sur `Exporter graphiques` pour enregistrer les graphiques.

## 6. Détails de l'analyse

### 6.1 Extraction PDF

Le module `lecteur_pdf.py` utilise :

```python
page.get_text("dict")
```

Cela permet de récupérer le texte, la taille de police, la police utilisée, le gras et le numéro de page.

### 6.2 Découpage des phrases

Le module `analyseur_phrases.py` prépare le texte avant segmentation :

- normalisation des retours à la ligne,
- recollement des mots coupés par césure,
- filtrage des titres probables,
- filtrage des blocs non narratifs,
- segmentation avec la ponctuation finale : `.`, `!`, `?`.

### 6.3 Phrases longues

Une phrase est signalée si son nombre de mots est strictement supérieur au seuil choisi.

Chaque phrase longue peut contenir :

- le nombre de mots,
- la page PDF si disponible,
- les alertes de complexité,
- les connecteurs repérés,
- une suggestion de découpage.

### 6.4 Termes techniques

Les termes saisis dans l'interface sont recherchés dans le document.

Le résultat distingue :

- les termes trouvés avec leur nombre d'occurrences,
- les termes non trouvés.

### 6.5 Résumé qualité

Le résumé qualité combine :

- score de lisibilité,
- nombre de phrases longues,
- proportion de phrases longues,
- complexité des phrases longues,
- termes techniques absents.

### 6.6 Exports

Le rapport peut être exporté en :

- `.pdf`,
- `.html`,
- `.txt`,
- `.csv`.

Les graphiques peuvent être exportés en :

- `.png`,
- `.pdf`,
- `.svg`.

## 7. Structure des résultats

La fonction `analyser_texte(...)` retourne un dictionnaire de ce type :

```python
{
    "nombre_caracteres": int,
    "nombre_mots": int,
    "nombre_phrases": int,
    "mots_frequents": list[tuple[str, int]],
    "phrases_longues": list[dict],
    "longueurs_phrases": list[int],
    "lisibilite": dict,
    "termes_techniques": list[dict],
    "termes_techniques_absents": list[str],
    "resume_qualite": dict
}
```

Exemple d'élément dans `phrases_longues` :

```python
{
    "phrase": "...",
    "nombre_mots": 42,
    "page": 7,
    "nombre_virgules": 4,
    "nombre_parentheses": 0,
    "connecteurs": ["cependant", "de plus"],
    "alertes": ["4 virgules", "2 connecteurs logiques"],
    "suggestion": "Essaie de couper cette phrase autour de « cependant »."
}
```

Exemple d'élément dans `termes_techniques` :

```python
{
    "terme": "Docker",
    "occurrences": 3
}
```

## 8. Personnalisation

### 8.1 Ajouter des mots à ignorer

Modifier l'ensemble `MOTS_A_IGNORER` dans `analyseur.py`.

### 8.2 Définir les termes techniques

Saisir les termes dans la zone dédiée de l'interface, un terme par ligne.

### 8.3 Modifier les connecteurs de phrase complexe

Modifier la liste `CONNECTEURS` dans `analyseur_phrases.py`.

### 8.4 Ajuster les heuristiques PDF

Adapter les fonctions suivantes selon le type de documents analysés :

- `_est_titre_visuel(...)` dans `lecteur_pdf.py`,
- `est_titre_probable(...)` dans `analyseur_phrases.py`,
- `filtrer_blocs_non_narratifs(...)` dans `analyseur_phrases.py`.

## 9. Limitations connues

- Certains PDF très bruités peuvent encore perturber l'extraction.
- Les tableaux complexes, les colonnes multiples ou les PDF OCRisés peuvent produire des résultats imparfaits.
- Les suggestions de reformulation sont heuristiques.
- La détection des termes techniques se base sur une recherche textuelle, pas sur une analyse sémantique.
- Le projet ne contient pas encore de tests automatisés.

## 10. Pistes d'amélioration

- Ajouter des tests unitaires avec `pytest`.
- Exporter aussi en `.json`.
- Ajouter un mode CLI pour analyser plusieurs fichiers en lot.
- Sauvegarder les préférences utilisateur dans un fichier JSON.
- Comparer deux versions d'un même document.
- Ajouter une détection des répétitions de mots ou d'expressions.
