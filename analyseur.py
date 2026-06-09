import re
from collections import Counter

from analyseur_phrases import (
    compter_phrases,
    detecter_phrases_longues,
    extraire_longueurs_phrases,
)


MOTS_A_IGNORER = {
    "le", "la", "les", "un", "une", "des",
    "de", "du", "dans", "en", "et", "à",
    "au", "aux", "pour", "par", "avec",
    "ce", "cette", "ces", "sur", "que",
    "qui", "est", "sont", "être", "plus"
}

TERMES_TECHNIQUES = [
    "API",
    "React",
    "React Native",
    "Docker",
    "base de données",
    "SQL",
    "NoSQL",
    "Spring Boot",
    "Laravel",
    "Dolibarr",
    "interface utilisateur",
    "authentification",
    "serveur",
    "endpoint",
    "JSON"
]


def compter_caracteres(texte):
    return len(texte)


def extraire_mots(texte):
    texte = texte.lower()
    mots = re.findall(r"\b[a-zàâäéèêëîïôöùûüçœ]+\b", texte)
    return mots


def compter_mots(texte):
    mots = extraire_mots(texte)
    return len(mots)


def mots_les_plus_frequents(texte, nombre=10):
    mots = extraire_mots(texte)

    mots_filtres = [
        mot for mot in mots
        if mot not in MOTS_A_IGNORER and len(mot) > 2
    ]

    compteur = Counter(mots_filtres)
    return compteur.most_common(nombre)

def detecter_termes_techniques(texte, termes_techniques=None):
    if termes_techniques is None:
        termes_techniques = []

    termes_trouves = []
    texte_minuscule = texte.lower()

    for terme in termes_techniques:
        terme_nettoye = terme.strip()

        if not terme_nettoye:
            continue

        if terme_nettoye.lower() in texte_minuscule:
            termes_trouves.append(terme_nettoye)

    return termes_trouves

def analyser_texte(
    texte,
    limite_phrase_longue=35,
    termes_techniques=None,
    mode_memoire=True,
    filtrer_blocs_non_narratifs_actif=True
):
    return {
        "nombre_caracteres": compter_caracteres(texte),
        "nombre_mots": compter_mots(texte),
        "nombre_phrases": compter_phrases(
            texte,
            mode_memoire=mode_memoire,
            filtrer_blocs=filtrer_blocs_non_narratifs_actif
        ),
        "mots_frequents": mots_les_plus_frequents(texte),
        "phrases_longues": detecter_phrases_longues(
            texte,
            limite_mots=limite_phrase_longue,
            mode_memoire=mode_memoire,
            filtrer_blocs=filtrer_blocs_non_narratifs_actif
        ),
        "longueurs_phrases": extraire_longueurs_phrases(
            texte,
            mode_memoire=mode_memoire,
            filtrer_blocs=filtrer_blocs_non_narratifs_actif
        ),
        "termes_techniques": detecter_termes_techniques(
            texte,
            termes_techniques=termes_techniques
        )
    }
