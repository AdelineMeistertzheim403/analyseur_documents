import re


def _extraire_mots(texte):
    texte = texte.lower()
    return re.findall(r"\b[a-zàâäéèêëîïôöùûüçœ]+\b", texte)


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
        r"\n\s*(liste des abréviations|table des illustrations|résumé|annexes)\b",
        texte_normalise[fin_match.end():],
        flags=re.IGNORECASE
    )

    if sections_fin:
        fin = fin_match.end() + sections_fin.start()

    return texte_normalise[debut:fin]


def filtrer_blocs_non_narratifs(texte):
    # Supprime les lignes techniques ou structurelles qui polluent la segmentation.
    lignes_filtres = []

    motifs_lignes = [
        r"^(figure|annexe|table des illustrations|liste des abréviations|mots-clés)\b",
        r"^(route dynamique|clé dictionnaire|appel api métadonnées|lecture table dictionary|construction configuration|overrides dictionaryregistry\.ts|chargement des données|affichage tableau)$",
        r"^(oui|non)$",
        r"^(key|count|icon_name|fa_icon|icon_color|active|is_external|champ|description)$"
    ]

    for ligne in texte.split("\n"):
        ligne_propre = ligne.strip()

        if not ligne_propre:
            lignes_filtres.append("")
            continue

        if any(re.match(motif, ligne_propre, flags=re.IGNORECASE) for motif in motifs_lignes):
            continue

        if re.search(r"[{}\[\]]|/admin/|dictionarykey|icon_name|fa_icon", ligne_propre, flags=re.IGNORECASE):
            continue

        lignes_filtres.append(ligne)

    return "\n".join(lignes_filtres)


def preparer_texte_pour_phrases(texte, mode_memoire=True, filtrer_blocs=True):
    # Pipeline unique de preparation pour garantir un comportement coherent.
    texte_prepare = normaliser_texte_pour_phrases(texte)

    if mode_memoire:
        texte_prepare = extraire_zone_memoire(texte_prepare)

    if filtrer_blocs:
        texte_prepare = filtrer_blocs_non_narratifs(texte_prepare)

    return texte_prepare


def est_ligne_parasite(ligne):
    ligne = ligne.strip()

    if not ligne:
        return True

    if re.fullmatch(r"\d+", ligne):
        return True

    if re.search(r"\.{5,}", ligne):
        return True

    if ligne.startswith("Adeline Meistertzheim"):
        return True

    if "Stage dans l’entreprise Patas Monkey" in ligne:
        return True

    if re.match(r"^(figure|annexe|table des illustrations)\b", ligne, flags=re.IGNORECASE):
        return True

    mots = _extraire_mots(ligne)

    if re.match(r"^\d+(?:\.\d+)*\s+", ligne) and not re.search(r"[.!?]$", ligne):
        return True

    if ligne.endswith(":") and len(mots) <= 12:
        return True

    if ":" in ligne and len(mots) <= 10 and not re.search(r"[.!?]$", ligne):
        return True

    if len(mots) <= 4 and not re.search(r"[.!?]$", ligne):
        return True

    return False


def decouper_phrases(texte, mode_memoire=True, filtrer_blocs=True):
    # Decoupe en phrases en tenant compte des artefacts frequents des PDF.
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

        for ligne in lignes:
            if est_ligne_parasite(ligne):
                continue

            ligne = re.sub(r"\s+", " ", ligne).strip()
            if not ligne:
                continue

            if ligne_courante:
                ligne_courante = f"{ligne_courante} {ligne}"
            else:
                ligne_courante = ligne

            # Decoupage principal sur les fins de phrase (. ! ?).
            if re.search(r"[.!?][\"')\]]?$", ligne_courante):
                segments = re.split(r"(?<=[.!?])\s+", ligne_courante)
                for segment in segments:
                    segment = re.sub(r"\s+", " ", segment).strip()
                    if segment:
                        phrases.append(segment)
                ligne_courante = ""

        if ligne_courante:
            phrases.append(ligne_courante)

    return phrases


def compter_phrases(texte, mode_memoire=True, filtrer_blocs=True):
    phrases = [
        phrase for phrase in decouper_phrases(
            texte,
            mode_memoire=mode_memoire,
            filtrer_blocs=filtrer_blocs
        )
        if phrase.endswith((".", "!", "?"))
    ]
    return len(phrases)


def detecter_phrases_longues(texte, limite_mots=35, mode_memoire=True, filtrer_blocs=True):
    # Reutilise exactement le meme decoupage que le comptage des phrases.
    phrases = decouper_phrases(
        texte,
        mode_memoire=mode_memoire,
        filtrer_blocs=filtrer_blocs
    )

    phrases_longues = []

    for phrase in phrases:
        # Ignore les blocs qui ne se terminent pas par une ponctuation de phrase.
        if not phrase.endswith((".", "!", "?")):
            continue

        mots = _extraire_mots(phrase)

        if len(mots) > limite_mots:
            phrases_longues.append({
                "phrase": phrase.strip(),
                "nombre_mots": len(mots)
            })

    return phrases_longues


def extraire_longueurs_phrases(texte, mode_memoire=True, filtrer_blocs=True):
    phrases = decouper_phrases(
        texte,
        mode_memoire=mode_memoire,
        filtrer_blocs=filtrer_blocs
    )

    longueurs = []

    for phrase in phrases:
        if not phrase.endswith((".", "!", "?")):
            continue

        mots = _extraire_mots(phrase)
        if mots:
            longueurs.append(len(mots))

    return longueurs
