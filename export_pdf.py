def exporter_resultat(resultat, chemin_sortie):
    # Exporte le rapport en texte brut pour rester lisible et partageable.
    with open(chemin_sortie, "w", encoding="utf-8") as fichier:
        fichier.write("=== Rapport d'analyse ===\n\n")
        fichier.write(f"Nombre de caractères : {resultat['nombre_caracteres']}\n")
        fichier.write(f"Nombre de mots : {resultat['nombre_mots']}\n")
        fichier.write(f"Nombre de phrases : {resultat['nombre_phrases']}\n")

        fichier.write("\nMots les plus fréquents :\n")
        for mot, frequence in resultat["mots_frequents"]:
            fichier.write(f"- {mot} : {frequence}\n")

        fichier.write("\nPhrases trop longues :\n")
        # Chaque entree contient la phrase complete et son nombre de mots.
        for item in resultat["phrases_longues"]:
            fichier.write(f"- {item['nombre_mots']} mots : {item['phrase']}\n")

        fichier.write("\nTermes techniques détectés :\n")
        for terme in resultat["termes_techniques"]:
            fichier.write(f"- {terme}\n")