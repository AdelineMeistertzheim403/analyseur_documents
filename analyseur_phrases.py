import re


CONNECTEURS = [
    "cependant",
    "toutefois",
    "néanmoins",
    "mais",
    "car",
    "donc",
    "ainsi",
    "en effet",
    "de plus",
    "par ailleurs",
    "tandis que",
    "alors que",
    "c'est pourquoi"
]


def _extraire_mots(texte):
    texte = texte.lower()
    return re.findall(r"\b[a-zàâäéèêëîïôöùûüçœ]+\b", texte)


def _extraire_page_ligne(ligne):
    match = re.match(r"^@@PAGE:(\d+)@@\s*(.*)$", ligne)
    if not match:
        return None, ligne

    return int(match.group(1)), match.group(2)


def nettoyer_marqueurs_pages(texte):
    return re.sub(r"@@PAGE:\d+@@\s*", "", texte)


def normaliser_texte_pour_phrases(texte):
    texte = texte.replace("\r\n", "\n").replace("\r", "\n")
    # Recolle les mots coupes par un retour a la ligne dans les PDF.
    texte = re.sub(r"(\w)-\n(\w)", r"\1\2", texte)
    return texte


def extraire_zone_memoire(texte):
    # Limite l'analyse narrative a la zone Introduction -> Conclusion.
    texte_normalise = normaliser_texte_pour_phrases(texte)

    debut = None
    for match in re.finditer(r"\bintroduction\b", texte_normalise, flags=re.IGNORECASE):
        extrait = texte_normalise[match.start():match.start() + 800]
        if re.search(r"\.{5,}", extrait):
            continue
        if len(_extraire_mots(extrait)) < 40:
            continue
        debut = match.start()
        break

    if debut is None:
        return texte_normalise

    fin_match = None
    for match in re.finditer(r"\bconclusion\b", texte_normalise, flags=re.IGNORECASE):
        if match.start() > debut:
            extrait = texte_normalise[match.start():match.start() + 800]
            if re.search(r"\.{5,}", extrait):
                continue
            fin_match = match
            break

    if not fin_match:
        return texte_normalise[debut:]

    fin = len(texte_normalise)
    sections_fin = re.search(
        r"\n\s*(?:@@PAGE:\d+@@\s*)?(liste des abréviations|table des illustrations|résumé|annexes)\b",
        texte_normalise[fin_match.end():],
        flags=re.IGNORECASE
    )

    if sections_fin:
        fin = fin_match.end() + sections_fin.start()

    return texte_normalise[debut:fin]


def filtrer_blocs_non_narratifs(texte):
    lignes_filtres = []

    motifs_lignes = [
        r"^(figure|annexe|table des illustrations|liste des abréviations|mots-clés)\b",
        r"^(route dynamique|clé dictionnaire|appel api métadonnées|lecture table dictionary|construction configuration|overrides dictionaryregistry\.ts|chargement des données|affichage tableau)$",
        r"^(oui|non)$",
        r"^(key|count|icon_name|fa_icon|icon_color|active|is_external|champ|description)$"
    ]

    for ligne in texte.split("\n"):
        page, contenu = _extraire_page_ligne(ligne.strip())
        prefixe = f"@@PAGE:{page}@@ " if page else ""
        ligne_propre = contenu.strip()

        if not ligne_propre:
            lignes_filtres.append("")
            continue

        if any(re.match(motif, ligne_propre, flags=re.IGNORECASE) for motif in motifs_lignes):
            continue

        if re.search(r"[{}\[\]]|/admin/|dictionarykey|icon_name|fa_icon", ligne_propre, flags=re.IGNORECASE):
            continue

        lignes_filtres.append(prefixe + contenu)

    return "\n".join(lignes_filtres)


def est_titre_probable(ligne):
    ligne = ligne.strip()

    if not ligne:
        return False

    if re.search(r"[.!?]$", ligne):
        return False

    mots = _extraire_mots(ligne)

    if len(mots) < 2:
        return False

    if re.match(r"^\d+(?:\.\d+)*\s+", ligne):
        return True

    if len(mots) <= 10 and not re.search(r"[,;]", ligne):
        return True

    if ligne.isupper() and len(mots) <= 12:
        return True

    return False


def preparer_texte_pour_phrases(texte, mode_memoire=True, filtrer_blocs=True):
    texte_prepare = normaliser_texte_pour_phrases(texte)

    if mode_memoire:
        texte_prepare = extraire_zone_memoire(texte_prepare)

    if filtrer_blocs:
        texte_prepare = filtrer_blocs_non_narratifs(texte_prepare)

    return texte_prepare


def est_ligne_parasite(ligne, ignorer_titres=True):
    ligne = ligne.strip()

    if not ligne:
        return True

    if re.fullmatch(r"\d+", ligne):
        return True

    if re.search(r"\.{5,}", ligne):
        return True

    if ligne.startswith("Adeline Meistertzheim"):
        return True

    if "Stage dans l'entreprise Patas Monkey" in ligne:
        return True

    if re.match(r"^(figure|annexe|table des illustrations)\b", ligne, flags=re.IGNORECASE):
        return True

    mots = _extraire_mots(ligne)

    if ignorer_titres and est_titre_probable(ligne):
        return True

    if ligne.endswith(":") and len(mots) <= 12:
        return True

    if ":" in ligne and len(mots) <= 10 and not re.search(r"[.!?]$", ligne):
        return True

    if len(mots) <= 4 and not re.search(r"[.!?]$", ligne):
        return True

    return False


def _ajouter_segments(phrases, ligne_courante, page_courante):
    segments = re.split(r"(?<=[.!?])\s+", ligne_courante)

    for segment in segments:
        segment = re.sub(r"\s+", " ", segment).strip()
        if segment:
            phrases.append({
                "phrase": segment,
                "page": page_courante
            })


def decouper_phrases_details(
    texte,
    mode_memoire=True,
    filtrer_blocs=True,
    ignorer_titres=True
):
    texte_normalise = preparer_texte_pour_phrases(
        texte,
        mode_memoire=mode_memoire,
        filtrer_blocs=filtrer_blocs
    )
    blocs = re.split(r"\n{2,}", texte_normalise)
    phrases = []

    for bloc in blocs:
        bloc = bloc.strip()
        if not bloc:
            continue

        lignes = [ligne.strip() for ligne in bloc.split("\n")]
        ligne_courante = ""
        page_courante = None

        for ligne in lignes:
            page, ligne = _extraire_page_ligne(ligne)

            if est_ligne_parasite(ligne, ignorer_titres=ignorer_titres):
                continue

            ligne = re.sub(r"\s+", " ", ligne).strip()
            if not ligne:
                continue

            if ligne_courante:
                ligne_courante = f"{ligne_courante} {ligne}"
            else:
                ligne_courante = ligne
                page_courante = page

            if re.search(r"[.!?][\"')\]]?$", ligne_courante):
                _ajouter_segments(phrases, ligne_courante, page_courante)
                ligne_courante = ""
                page_courante = None

        if ligne_courante:
            phrases.append({
                "phrase": re.sub(r"\s+", " ", ligne_courante).strip(),
                "page": page_courante
            })

    return phrases


def decouper_phrases(
    texte,
    mode_memoire=True,
    filtrer_blocs=True,
    ignorer_titres=True
):
    return [
        item["phrase"]
        for item in decouper_phrases_details(
            texte,
            mode_memoire=mode_memoire,
            filtrer_blocs=filtrer_blocs,
            ignorer_titres=ignorer_titres
        )
    ]


def compter_phrases(
    texte,
    mode_memoire=True,
    filtrer_blocs=True,
    ignorer_titres=True
):
    phrases = [
        item for item in decouper_phrases_details(
            texte,
            mode_memoire=mode_memoire,
            filtrer_blocs=filtrer_blocs,
            ignorer_titres=ignorer_titres
        )
        if item["phrase"].endswith((".", "!", "?"))
    ]
    return len(phrases)


def analyser_complexite_phrase(phrase):
    phrase_minuscule = phrase.lower()
    connecteurs_trouves = [
        connecteur
        for connecteur in CONNECTEURS
        if re.search(rf"\b{re.escape(connecteur)}\b", phrase_minuscule)
    ]
    nombre_virgules = phrase.count(",")
    nombre_parentheses = phrase.count("(") + phrase.count(")")
    alertes = []

    if nombre_virgules >= 4:
        alertes.append(f"{nombre_virgules} virgules")

    if nombre_parentheses >= 2:
        alertes.append("présence de parenthèses")

    if len(connecteurs_trouves) >= 2:
        alertes.append(f"{len(connecteurs_trouves)} connecteurs logiques")

    if nombre_virgules == 0 and len(_extraire_mots(phrase)) >= 35:
        alertes.append("peu de ponctuation interne")

    suggestion = "Essaie de couper cette phrase en deux."
    if connecteurs_trouves:
        suggestion = f"Essaie de couper cette phrase autour de « {connecteurs_trouves[0]} »."
    elif nombre_virgules >= 2:
        suggestion = "Essaie de transformer une partie après une virgule en nouvelle phrase."

    return {
        "nombre_virgules": nombre_virgules,
        "nombre_parentheses": nombre_parentheses,
        "connecteurs": connecteurs_trouves,
        "alertes": alertes,
        "suggestion": suggestion
    }


def detecter_phrases_longues(
    texte,
    limite_mots=35,
    mode_memoire=True,
    filtrer_blocs=True,
    ignorer_titres=True
):
    phrases = decouper_phrases_details(
        texte,
        mode_memoire=mode_memoire,
        filtrer_blocs=filtrer_blocs,
        ignorer_titres=ignorer_titres
    )

    phrases_longues = []

    for item in phrases:
        phrase = item["phrase"]

        if not phrase.endswith((".", "!", "?")):
            continue

        mots = _extraire_mots(phrase)

        if len(mots) > limite_mots:
            analyse_complexite = analyser_complexite_phrase(phrase)
            phrases_longues.append({
                "phrase": phrase.strip(),
                "nombre_mots": len(mots),
                "page": item["page"],
                **analyse_complexite
            })

    return phrases_longues


def extraire_longueurs_phrases(
    texte,
    mode_memoire=True,
    filtrer_blocs=True,
    ignorer_titres=True
):
    phrases = decouper_phrases_details(
        texte,
        mode_memoire=mode_memoire,
        filtrer_blocs=filtrer_blocs,
        ignorer_titres=ignorer_titres
    )

    longueurs = []

    for item in phrases:
        phrase = item["phrase"]
        if not phrase.endswith((".", "!", "?")):
            continue

        mots = _extraire_mots(phrase)
        if mots:
            longueurs.append(len(mots))

    return longueurs
