import re
from collections import Counter

import fitz


def _extraire_mots(texte):
    return re.findall(r"\b[\wÀ-ÿœŒ]+\b", texte, flags=re.UNICODE)


def _normaliser_ligne_pdf(texte):
    texte = texte.strip().lower()
    texte = re.sub(r"\d+", "<nombre>", texte)
    return re.sub(r"\s+", " ", texte)


def _taille_police_normale(lignes):
    tailles = [
        round(ligne["taille"], 1)
        for ligne in lignes
        if ligne["texte"] and len(_extraire_mots(ligne["texte"])) >= 3
    ]

    if not tailles:
        return 0

    return Counter(tailles).most_common(1)[0][0]


def _est_titre_visuel(ligne, taille_normale):
    texte = ligne["texte"].strip()
    mots = _extraire_mots(texte)

    if not texte or not taille_normale:
        return False

    if re.search(r"[.!?]$", texte):
        return False

    if len(mots) > 14:
        return False

    if ligne["taille"] >= taille_normale + 1.5:
        return True

    if ligne["gras"] and ligne["taille"] >= taille_normale and len(mots) <= 10:
        return True

    return False


def _extraire_lignes_pdf(document):
    lignes = []

    for numero_page, page in enumerate(document, start=1):
        donnees = page.get_text("dict")

        for bloc in donnees.get("blocks", []):
            if bloc.get("type") != 0:
                continue

            for ligne in bloc.get("lines", []):
                textes = []
                tailles = []
                gras = False

                for span in ligne.get("spans", []):
                    texte_span = span.get("text", "")
                    if texte_span:
                        textes.append(texte_span)
                        tailles.append(span.get("size", 0))

                    police = span.get("font", "").lower()
                    if "bold" in police or "black" in police or "semibold" in police:
                        gras = True

                texte = " ".join("".join(textes).split())
                if not texte:
                    continue

                lignes.append({
                    "page": numero_page,
                    "texte": texte,
                    "texte_normalise": _normaliser_ligne_pdf(texte),
                    "taille": max(tailles) if tailles else 0,
                    "gras": gras,
                    "bbox": ligne.get("bbox", (0, 0, 0, 0)),
                    "hauteur_page": page.rect.height
                })

    return lignes


def _est_dans_zone_entete_pied(ligne, marge_haut_ratio, marge_bas_ratio):
    hauteur_page = ligne["hauteur_page"]
    y_haut = ligne["bbox"][1]
    y_bas = ligne["bbox"][3]
    limite_haut = hauteur_page * marge_haut_ratio
    limite_bas = hauteur_page * (1 - marge_bas_ratio)

    return y_bas < limite_haut or y_haut > limite_bas


def _detecter_lignes_repetees(
    lignes,
    seuil_ratio=0.4,
    marge_haut_ratio=0.08,
    marge_bas_ratio=0.08
):
    if not lignes:
        return set()

    pages = {ligne["page"] for ligne in lignes}
    nombre_pages = len(pages)

    if nombre_pages < 2:
        return set()

    occurrences_par_page = {}

    for ligne in lignes:
        if not _est_dans_zone_entete_pied(ligne, marge_haut_ratio, marge_bas_ratio):
            continue

        texte_normalise = ligne["texte_normalise"]
        if len(texte_normalise) <= 2:
            continue

        occurrences_par_page.setdefault(texte_normalise, set()).add(ligne["page"])

    seuil = max(2, int(nombre_pages * seuil_ratio))

    return {
        texte
        for texte, pages_ligne in occurrences_par_page.items()
        if len(pages_ligne) >= seuil
    }


def _raison_ligne_ignoree(
    ligne,
    lignes_repetees,
    marge_haut_ratio,
    marge_bas_ratio
):
    hauteur_page = ligne["hauteur_page"]
    y_haut = ligne["bbox"][1]
    y_bas = ligne["bbox"][3]
    limite_haut = hauteur_page * marge_haut_ratio
    limite_bas = hauteur_page * (1 - marge_bas_ratio)

    if y_bas < limite_haut:
        return "en-tête"

    if y_haut > limite_bas:
        return "pied de page"

    if ligne["texte_normalise"] in lignes_repetees:
        return "ligne répétée"

    return None


def _detecter_numeros_pages_affiches(lignes, marge_bas_ratio):
    numeros = {}

    for ligne in lignes:
        texte = ligne["texte"].strip()
        hauteur_page = ligne["hauteur_page"]
        y_haut = ligne["bbox"][1]
        limite_bas = hauteur_page * (1 - marge_bas_ratio)

        if y_haut <= limite_bas:
            continue

        if re.fullmatch(r"\d{1,4}", texte):
            numeros[ligne["page"]] = int(texte)

    return numeros


def lire_pdf(
    chemin_fichier,
    ignorer_titres=True,
    ignorer_entetes_pieds=True,
    marge_haut_ratio=0.08,
    marge_bas_ratio=0.08,
    seuil_repetition=0.4,
    retourner_details=False
):
    document = fitz.open(chemin_fichier)

    try:
        lignes = _extraire_lignes_pdf(document)
        taille_normale = _taille_police_normale(lignes)
        numeros_pages_affiches = _detecter_numeros_pages_affiches(
            lignes,
            marge_bas_ratio
        )
        lignes_repetees = (
            _detecter_lignes_repetees(
                lignes,
                seuil_ratio=seuil_repetition,
                marge_haut_ratio=marge_haut_ratio,
                marge_bas_ratio=marge_bas_ratio
            )
            if ignorer_entetes_pieds
            else set()
        )
        lignes_texte = []
        lignes_ignorees = []

        for ligne in lignes:
            raison = None

            if ignorer_entetes_pieds:
                raison = _raison_ligne_ignoree(
                    ligne,
                    lignes_repetees,
                    marge_haut_ratio,
                    marge_bas_ratio
                )

            if raison:
                lignes_ignorees.append({
                    "page": numeros_pages_affiches.get(ligne["page"], ligne["page"]),
                    "page_pdf": ligne["page"],
                    "texte": ligne["texte"],
                    "raison": raison
                })
                continue

            if ignorer_titres and _est_titre_visuel(ligne, taille_normale):
                continue

            page_affichee = numeros_pages_affiches.get(ligne["page"], ligne["page"])
            lignes_texte.append(
                f"@@PAGE:{page_affichee}@@ @@PDFPAGE:{ligne['page']}@@ {ligne['texte']}"
            )

        texte = "\n".join(lignes_texte)

        if retourner_details:
            return {
                "texte": texte,
                "nettoyage_pdf": {
                    "lignes_ignorees": lignes_ignorees,
                    "nombre_lignes_ignorees": len(lignes_ignorees),
                    "marge_haut_ratio": marge_haut_ratio,
                    "marge_bas_ratio": marge_bas_ratio,
                    "seuil_repetition": seuil_repetition
                }
            }

        return texte
    finally:
        document.close()
