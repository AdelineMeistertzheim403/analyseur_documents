TERMES_TECHNIQUES_PAR_DEFAUT = [
    "API",
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
    "endpoint",
    "JSON"
]


def extraire_termes_depuis_texte(contenu):
    return [ligne.strip() for ligne in contenu.splitlines() if ligne.strip()]


def formater_statistiques(resultat, nombre_termes_recherches):
    lignes = [
        "STATISTIQUES GÉNÉRALES",
        "",
        f"Nombre de caractères : {resultat['nombre_caracteres']}",
        f"Nombre de mots : {resultat['nombre_mots']}",
        f"Nombre de phrases : {resultat['nombre_phrases']}"
    ]

    if resultat["nombre_phrases"] > 0:
        moyenne = resultat["nombre_mots"] / resultat["nombre_phrases"]
        lignes.append(f"Nombre moyen de mots par phrase : {moyenne:.2f}")

    if "phrases_longues" in resultat:
        lignes.append(f"Nombre de phrases longues : {len(resultat['phrases_longues'])}")

    lisibilite = resultat.get("lisibilite")
    if lisibilite:
        lignes.extend([
            "",
            "LISIBILITÉ",
            f"Niveau : {lisibilite['niveau']}",
            f"Score : {lisibilite['score']} / 100",
            f"Moyenne analysée : {lisibilite['moyenne_mots_phrase']:.2f} mots par phrase",
            f"Phrases longues : {lisibilite['pourcentage_phrases_longues']:.1f} %"
        ])

    lignes.append("")
    lignes.append(f"Nombre de termes techniques recherchés : {nombre_termes_recherches}")

    if "termes_techniques" in resultat:
        lignes.append(f"Nombre de termes techniques trouvés : {len(resultat['termes_techniques'])}")

    absents = resultat.get("termes_techniques_absents", [])
    lignes.append(f"Nombre de termes techniques non trouvés : {len(absents)}")

    return "\n".join(lignes) + "\n"


def formater_resume_qualite(resultat):
    resume = resultat.get("resume_qualite")

    if not resume:
        return "RÉSUMÉ QUALITÉ\n\nAucun résumé disponible.\n"

    lignes = [
        "RÉSUMÉ QUALITÉ",
        "",
        f"Niveau global : {resume['niveau']}",
        f"Score : {resume['score']} / 100",
        "",
        "POINTS FORTS"
    ]

    for point in resume["points_forts"]:
        lignes.append(f"- {point}")

    lignes.extend(["", "POINTS À AMÉLIORER"])
    for point in resume["points_a_ameliorer"]:
        lignes.append(f"- {point}")

    lignes.extend(["", "RECOMMANDATIONS"])
    for recommandation in resume["recommandations"]:
        lignes.append(f"- {recommandation}")

    return "\n".join(lignes) + "\n"


def formater_mots_frequents(resultat):
    lignes = ["MOTS LES PLUS FRÉQUENTS", ""]

    mots_frequents = resultat.get("mots_frequents", [])
    if not mots_frequents:
        lignes.append("Aucun mot fréquent détecté.")
        return "\n".join(lignes) + "\n"

    for index, (mot, frequence) in enumerate(mots_frequents, start=1):
        lignes.append(f"{index}. {mot} : {frequence}")

    return "\n".join(lignes) + "\n"


def formater_phrases_longues(resultat, limite):
    lignes = [f"PHRASES DE PLUS DE {limite} MOTS", ""]

    if "phrases_longues" not in resultat:
        lignes.append("La détection des phrases longues n'est pas encore disponible.")
        return "\n".join(lignes) + "\n"

    phrases_longues = resultat["phrases_longues"]
    if len(phrases_longues) == 0:
        lignes.append("Aucune phrase trop longue détectée.")
        return "\n".join(lignes) + "\n"

    for index, item in enumerate(phrases_longues, start=1):
        page = f"Page {item['page']} - " if item.get("page") else ""
        lignes.append(f"{index}. {page}{item['nombre_mots']} mots")

        alertes = item.get("alertes", [])
        if alertes:
            lignes.append(f"Alertes : {', '.join(alertes)}")

        connecteurs = item.get("connecteurs", [])
        if connecteurs:
            lignes.append(f"Connecteurs repérés : {', '.join(connecteurs)}")

        suggestion = item.get("suggestion")
        if suggestion:
            lignes.append(f"Suggestion : {suggestion}")

        lignes.append(item["phrase"])
        lignes.append("")

    return "\n".join(lignes) + "\n"


def formater_termes_techniques(resultat):
    lignes = ["TERMES TECHNIQUES DÉTECTÉS", ""]

    if "termes_techniques" not in resultat:
        lignes.append("La détection des termes techniques n'est pas encore disponible.")
        return "\n".join(lignes) + "\n"

    termes = resultat["termes_techniques"]
    if len(termes) == 0:
        lignes.append("Aucun terme technique détecté.")
    else:
        for item in termes:
            lignes.append(f"- {item['terme']} : {item['occurrences']} occurrence(s)")

    absents = resultat.get("termes_techniques_absents", [])
    lignes.extend(["", "TERMES NON TROUVÉS", ""])

    if not absents:
        lignes.append("Tous les termes recherchés ont été trouvés.")
    else:
        for terme in absents:
            lignes.append(f"- {terme}")

    return "\n".join(lignes) + "\n"


def creer_figure_analyse(resultat):
    try:
        from matplotlib.figure import Figure
    except ImportError:
        return None, "Matplotlib n'est pas installé.\nInstalle-le avec : pip install matplotlib"

    longueurs = resultat.get("longueurs_phrases", [])
    mots_frequents = resultat.get("mots_frequents", [])

    if not longueurs and not mots_frequents:
        return None, "Pas de données pour afficher les graphiques."

    figure = Figure(figsize=(10, 4.8), dpi=100)
    axe_hist = figure.add_subplot(1, 2, 1)
    axe_mots = figure.add_subplot(1, 2, 2)

    if longueurs:
        nb_classes = min(20, max(5, int(len(longueurs) ** 0.5)))
        axe_hist.hist(longueurs, bins=nb_classes, color="#4E79A7", edgecolor="white")
        axe_hist.set_title("Distribution des longueurs de phrases")
        axe_hist.set_xlabel("Nombre de mots")
        axe_hist.set_ylabel("Nombre de phrases")
    else:
        axe_hist.text(0.5, 0.5, "Aucune phrase exploitable", ha="center", va="center")
        axe_hist.set_title("Distribution des longueurs de phrases")
        axe_hist.set_xticks([])
        axe_hist.set_yticks([])

    if mots_frequents:
        mots = [mot for mot, _ in mots_frequents]
        frequences = [frequence for _, frequence in mots_frequents]
        axe_mots.barh(mots, frequences, color="#59A14F")
        axe_mots.invert_yaxis()
        axe_mots.set_title("Top mots fréquents")
        axe_mots.set_xlabel("Fréquence")
    else:
        axe_mots.text(0.5, 0.5, "Aucun mot fréquent", ha="center", va="center")
        axe_mots.set_title("Top mots fréquents")
        axe_mots.set_xticks([])
        axe_mots.set_yticks([])

    figure.tight_layout()
    return figure, None
