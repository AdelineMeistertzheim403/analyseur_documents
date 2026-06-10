import re
from collections import Counter

import fitz


def _extraire_mots(texte):
    return re.findall(r"\b[\wÀ-ÿœŒ]+\b", texte, flags=re.UNICODE)


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
                    "taille": max(tailles) if tailles else 0,
                    "gras": gras
                })

    return lignes


def lire_pdf(chemin_fichier, ignorer_titres=True):
    document = fitz.open(chemin_fichier)

    try:
        lignes = _extraire_lignes_pdf(document)
        taille_normale = _taille_police_normale(lignes)
        lignes_texte = []

        for ligne in lignes:
            if ignorer_titres and _est_titre_visuel(ligne, taille_normale):
                continue

            lignes_texte.append(f"@@PAGE:{ligne['page']}@@ {ligne['texte']}")

        return "\n".join(lignes_texte)
    finally:
        document.close()
