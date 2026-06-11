import math
import re
from collections import Counter

from analyseur_phrases import (
    CONNECTEURS,
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

FORMULES_GENERIQUES = [
    "il est important de",
    "il convient de",
    "il est essentiel de",
    "dans un monde où",
    "cela permet de",
    "cet aspect souligne",
    "il est nécessaire de",
    "de manière générale",
    "en conclusion",
    "d'une part",
    "d'autre part",
    "non seulement",
    "mais aussi"
]

MOTIF_LISTE_PUCE = re.compile(
    r"^\s*(?:[-*•●○▪▫–—✓]|[0-9]+[.)]|[a-zA-Z][.)])\s+"
)


def extraire_page_ligne(ligne):
    match = re.match(r"^@@PAGE:(\d+)@@\s*(.*)$", ligne)
    if not match:
        return None, ligne

    return int(match.group(1)), match.group(2)


def compter_caracteres(texte):
    return len(nettoyer_marqueurs_pages(texte))


def extraire_mots(texte):
    texte = nettoyer_marqueurs_pages(texte).lower()
    return re.findall(r"\b[a-zàâäéèêëîïôöùûüçœ]+\b", texte)


def compter_mots(texte):
    mots = extraire_mots(texte)
    return len(mots)


def est_ligne_liste_puce(texte):
    return MOTIF_LISTE_PUCE.match(texte) is not None


def analyser_structure_document(texte):
    lignes_textuelles = []
    listes_puces = []

    for ligne in texte.splitlines():
        page, contenu = extraire_page_ligne(ligne.strip())
        contenu = contenu.strip()

        if not contenu:
            continue

        lignes_textuelles.append({
            "page": page,
            "texte": contenu
        })

        if est_ligne_liste_puce(contenu):
            listes_puces.append({
                "page": page,
                "texte": contenu
            })

    return {
        "nombre_lignes_textuelles": len(lignes_textuelles),
        "nombre_listes_puces": len(listes_puces),
        "listes_puces": listes_puces
    }


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


def calculer_repartition_longueurs(longueurs_phrases):
    categories = {
        "Courtes (0-15)": 0,
        "Moyennes (16-30)": 0,
        "Longues (31-45)": 0,
        "Très longues (46+)": 0
    }

    for longueur in longueurs_phrases:
        if longueur <= 15:
            categories["Courtes (0-15)"] += 1
        elif longueur <= 30:
            categories["Moyennes (16-30)"] += 1
        elif longueur <= 45:
            categories["Longues (31-45)"] += 1
        else:
            categories["Très longues (46+)"] += 1

    return categories


def compter_phrases_longues_par_page(phrases_longues):
    compteur = Counter()

    for item in phrases_longues:
        page = item.get("page")
        if page:
            compteur[page] += 1

    return dict(sorted(compteur.items()))


def compter_alertes_complexite(phrases_longues):
    compteur = Counter()

    for item in phrases_longues:
        for alerte in item.get("alertes", []):
            compteur[alerte] += 1

    return dict(compteur.most_common())


def compter_connecteurs(texte):
    texte_minuscule = nettoyer_marqueurs_pages(texte).lower()
    compteur = Counter()

    for connecteur in CONNECTEURS:
        occurrences = len(re.findall(rf"\b{re.escape(connecteur)}\b", texte_minuscule))
        if occurrences:
            compteur[connecteur] = occurrences

    return dict(compteur.most_common(10))


def compter_formules_generiques(texte):
    texte_minuscule = nettoyer_marqueurs_pages(texte).lower()
    compteur = Counter()

    for formule in FORMULES_GENERIQUES:
        occurrences = len(re.findall(rf"\b{re.escape(formule)}\b", texte_minuscule))
        if occurrences:
            compteur[formule] = occurrences

    return dict(compteur.most_common())


def calculer_indice_style_artificiel(texte, longueurs_phrases, connecteurs, formules_generiques):
    mots = extraire_mots(texte)
    total_mots = len(mots)
    mots_uniques = len(set(mots))
    diversite_lexicale = (mots_uniques / total_mots) if total_mots else 0
    total_connecteurs = sum(connecteurs.values())
    total_formules = sum(formules_generiques.values())
    nombre_phrases = len(longueurs_phrases)

    moyenne = sum(longueurs_phrases) / nombre_phrases if nombre_phrases else 0
    variance = (
        sum((longueur - moyenne) ** 2 for longueur in longueurs_phrases) / nombre_phrases
        if nombre_phrases else 0
    )
    ecart_type = math.sqrt(variance)
    regularite = 0
    if moyenne:
        regularite = max(0, 1 - (ecart_type / moyenne))

    score = 0
    signaux = []
    details = {
        "Régularité des phrases": 0,
        "Connecteurs fréquents": 0,
        "Formules génériques": 0,
        "Faible diversité lexicale": 0
    }

    if nombre_phrases >= 5 and regularite >= 0.72:
        valeur = min(30, round(regularite * 30))
        score += valeur
        details["Régularité des phrases"] = valeur
        signaux.append("Longueur des phrases très régulière.")

    if total_connecteurs:
        ratio_connecteurs = total_connecteurs / max(1, nombre_phrases)
        valeur = min(25, round(ratio_connecteurs * 18))
        score += valeur
        details["Connecteurs fréquents"] = valeur
        if valeur >= 8:
            signaux.append("Connecteurs logiques fréquents.")

    if total_formules:
        valeur = min(25, total_formules * 8)
        score += valeur
        details["Formules génériques"] = valeur
        signaux.append("Formules génériques repérées.")

    if total_mots >= 120 and diversite_lexicale < 0.38:
        valeur = min(20, round((0.38 - diversite_lexicale) * 100))
        score += valeur
        details["Faible diversité lexicale"] = valeur
        signaux.append("Diversité lexicale faible.")

    score = max(0, min(100, score))
    if score >= 65:
        niveau = "Élevé"
    elif score >= 35:
        niveau = "Moyen"
    else:
        niveau = "Faible"

    if not signaux:
        signaux.append("Aucun signal stylistique fort détecté.")

    return {
        "score": score,
        "niveau": niveau,
        "signaux": signaux,
        "details": details,
        "diversite_lexicale": diversite_lexicale,
        "regularite_phrases": regularite,
        "note": "Cet indice ne prouve pas qu'un texte a été généré par IA. Il signale seulement des caractéristiques stylistiques à relire."
    }


def generer_resume_qualite(resultat):
    lisibilite = resultat["lisibilite"]
    phrases_longues = resultat["phrases_longues"]
    termes_absents = resultat["termes_techniques_absents"]
    phrases_complexes = [
        item for item in phrases_longues
        if item.get("alertes")
    ]
    indice_style = resultat.get("indice_style_artificiel", {})

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

    if indice_style.get("niveau") in {"Moyen", "Élevé"}:
        points_a_ameliorer.append(
            f"Indice de style potentiellement artificiel : {indice_style['niveau'].lower()}."
        )

    if not points_forts:
        points_forts.append("Le document contient assez d'informations pour produire une analyse.")

    recommandations = []
    if phrases_longues:
        recommandations.append("Commencer par retravailler les phrases longues listées dans l'onglet dédié.")
    if phrases_complexes:
        recommandations.append("Prioriser les phrases avec beaucoup de virgules, parenthèses ou connecteurs.")
    if termes_absents:
        recommandations.append("Vérifier si les termes techniques absents sont réellement attendus dans ce document.")
    if indice_style.get("niveau") in {"Moyen", "Élevé"}:
        recommandations.append("Relire les passages très génériques ou trop réguliers pour les rendre plus personnels et précis.")
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
    connecteurs_frequents = compter_connecteurs(texte)
    formules_generiques = compter_formules_generiques(texte)
    indice_style = calculer_indice_style_artificiel(
        texte,
        longueurs_phrases,
        connecteurs_frequents,
        formules_generiques
    )

    resultat = {
        "nombre_caracteres": compter_caracteres(texte),
        "nombre_mots": compter_mots(texte),
        "nombre_phrases": nombre_phrases,
        "structure_document": analyser_structure_document(texte),
        "mots_frequents": mots_les_plus_frequents(texte),
        "phrases_longues": phrases_longues,
        "longueurs_phrases": longueurs_phrases,
        "repartition_longueurs": calculer_repartition_longueurs(longueurs_phrases),
        "phrases_longues_par_page": compter_phrases_longues_par_page(phrases_longues),
        "alertes_complexite": compter_alertes_complexite(phrases_longues),
        "connecteurs_frequents": connecteurs_frequents,
        "formules_generiques": formules_generiques,
        "indice_style_artificiel": indice_style,
        "lisibilite": calculer_lisibilite(longueurs_phrases, len(phrases_longues)),
        "termes_techniques": termes_trouves,
        "termes_techniques_absents": termes_absents
    }
    resultat["resume_qualite"] = generer_resume_qualite(resultat)

    return resultat
