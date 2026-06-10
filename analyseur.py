import re
from collections import Counter

from analyseur_phrases import (
    compter_phrases,
    detecter_phrases_longues,
    extraire_longueurs_phrases,
    nettoyer_marqueurs_pages,
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
    return len(nettoyer_marqueurs_pages(texte))


def extraire_mots(texte):
    texte = nettoyer_marqueurs_pages(texte).lower()
    return re.findall(r"\b[a-zàâäéèêëîïôöùûüçœ]+\b", texte)


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

    texte = nettoyer_marqueurs_pages(texte)
    termes_trouves = []
    termes_absents = []

    for terme in termes_techniques:
        terme_nettoye = terme.strip()

        if not terme_nettoye:
            continue

        motif = rf"(?<!\w){re.escape(terme_nettoye)}(?!\w)"
        occurrences = len(re.findall(motif, texte, flags=re.IGNORECASE))

        if occurrences > 0:
            termes_trouves.append({
                "terme": terme_nettoye,
                "occurrences": occurrences
            })
        else:
            termes_absents.append(terme_nettoye)

    return termes_trouves, termes_absents


def calculer_lisibilite(longueurs_phrases, nombre_phrases_longues):
    if not longueurs_phrases:
        return {
            "score": 0,
            "niveau": "Non calculable",
            "moyenne_mots_phrase": 0,
            "pourcentage_phrases_longues": 0
        }

    nombre_phrases = len(longueurs_phrases)
    moyenne = sum(longueurs_phrases) / nombre_phrases
    pourcentage_longues = (nombre_phrases_longues / nombre_phrases) * 100

    score = 100
    score -= max(0, moyenne - 18) * 2
    score -= pourcentage_longues * 1.5
    score = max(0, min(100, round(score)))

    if score >= 80:
        niveau = "Bonne"
    elif score >= 60:
        niveau = "Correcte"
    elif score >= 40:
        niveau = "À améliorer"
    else:
        niveau = "Difficile"

    return {
        "score": score,
        "niveau": niveau,
        "moyenne_mots_phrase": moyenne,
        "pourcentage_phrases_longues": pourcentage_longues
    }


def generer_resume_qualite(resultat):
    lisibilite = resultat["lisibilite"]
    phrases_longues = resultat["phrases_longues"]
    termes_absents = resultat["termes_techniques_absents"]
    phrases_complexes = [
        item for item in phrases_longues
        if item.get("alertes")
    ]

    points_forts = []
    points_a_ameliorer = []

    if lisibilite["score"] >= 80:
        points_forts.append("La lisibilité globale est bonne.")
    elif lisibilite["score"] >= 60:
        points_forts.append("La lisibilité globale reste correcte.")
    else:
        points_a_ameliorer.append("La lisibilité globale peut être améliorée.")

    if len(phrases_longues) == 0:
        points_forts.append("Aucune phrase trop longue n'a été détectée.")
    else:
        points_a_ameliorer.append(f"{len(phrases_longues)} phrase(s) dépassent la limite choisie.")

    if lisibilite["moyenne_mots_phrase"] and lisibilite["moyenne_mots_phrase"] <= 20:
        points_forts.append("La longueur moyenne des phrases est maîtrisée.")
    elif lisibilite["moyenne_mots_phrase"] > 20:
        points_a_ameliorer.append("La longueur moyenne des phrases est élevée.")

    if phrases_complexes:
        points_a_ameliorer.append(
            f"{len(phrases_complexes)} phrase(s) longues présentent aussi des signes de complexité."
        )

    if termes_absents:
        points_a_ameliorer.append(f"{len(termes_absents)} terme(s) recherché(s) sont absents.")
    elif resultat["termes_techniques"]:
        points_forts.append("Tous les termes techniques recherchés ont été trouvés.")

    if not points_forts:
        points_forts.append("Le document contient assez d'informations pour produire une analyse.")

    recommandations = []
    if phrases_longues:
        recommandations.append("Commencer par retravailler les phrases longues listées dans l'onglet dédié.")
    if phrases_complexes:
        recommandations.append("Prioriser les phrases avec beaucoup de virgules, parenthèses ou connecteurs.")
    if termes_absents:
        recommandations.append("Vérifier si les termes techniques absents sont réellement attendus dans ce document.")
    if not recommandations:
        recommandations.append("Aucune action prioritaire évidente : l'analyse ne signale pas de problème majeur.")

    return {
        "niveau": lisibilite["niveau"],
        "score": lisibilite["score"],
        "points_forts": points_forts,
        "points_a_ameliorer": points_a_ameliorer,
        "recommandations": recommandations
    }


def analyser_texte(
    texte,
    limite_phrase_longue=35,
    termes_techniques=None,
    mode_memoire=True,
    filtrer_blocs_non_narratifs_actif=True,
    ignorer_titres=True
):
    nombre_phrases = compter_phrases(
        texte,
        mode_memoire=mode_memoire,
        filtrer_blocs=filtrer_blocs_non_narratifs_actif,
        ignorer_titres=ignorer_titres
    )
    phrases_longues = detecter_phrases_longues(
        texte,
        limite_mots=limite_phrase_longue,
        mode_memoire=mode_memoire,
        filtrer_blocs=filtrer_blocs_non_narratifs_actif,
        ignorer_titres=ignorer_titres
    )
    longueurs_phrases = extraire_longueurs_phrases(
        texte,
        mode_memoire=mode_memoire,
        filtrer_blocs=filtrer_blocs_non_narratifs_actif,
        ignorer_titres=ignorer_titres
    )
    termes_trouves, termes_absents = detecter_termes_techniques(
        texte,
        termes_techniques=termes_techniques
    )

    resultat = {
        "nombre_caracteres": compter_caracteres(texte),
        "nombre_mots": compter_mots(texte),
        "nombre_phrases": nombre_phrases,
        "mots_frequents": mots_les_plus_frequents(texte),
        "phrases_longues": phrases_longues,
        "longueurs_phrases": longueurs_phrases,
        "lisibilite": calculer_lisibilite(longueurs_phrases, len(phrases_longues)),
        "termes_techniques": termes_trouves,
        "termes_techniques_absents": termes_absents
    }
    resultat["resume_qualite"] = generer_resume_qualite(resultat)

    return resultat
