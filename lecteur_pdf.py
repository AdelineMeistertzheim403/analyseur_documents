import fitz


def lire_pdf(chemin_fichier):
    # Concatene le texte de chaque page pour fournir un seul bloc a l'analyseur.
    document = fitz.open(chemin_fichier)
    texte = ""

    for page in document:
        texte += page.get_text()

    document.close()
    return texte