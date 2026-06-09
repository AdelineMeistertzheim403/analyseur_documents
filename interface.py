import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

import customtkinter as ctk

from analyseur import analyser_texte
from lecteur_pdf import lire_pdf
from export_pdf import exporter_resultat


class AnalyseurApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analyseur de documents")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.chemin_fichier = None
        self.resultat = None

        self.creer_interface()

    def creer_interface(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        self.frame_header = ctk.CTkFrame(self.root, corner_radius=15)
        self.frame_header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.frame_header.grid_columnconfigure(0, weight=1)

        titre = ctk.CTkLabel(
            self.frame_header,
            text="Analyseur de documents",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        titre.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        sous_titre = ctk.CTkLabel(
            self.frame_header,
            text="Analyse rapidement tes fichiers PDF ou TXT : statistiques, mots fréquents, phrases longues et termes techniques.",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        sous_titre.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")

        self.frame_actions = ctk.CTkFrame(self.root, corner_radius=15)
        self.frame_actions.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.frame_actions.grid_columnconfigure(3, weight=1)

        bouton_choisir = ctk.CTkButton(
            self.frame_actions,
            text="Choisir un fichier",
            command=self.choisir_fichier,
            width=160
        )
        bouton_choisir.grid(row=0, column=0, padx=(15, 8), pady=15)

        bouton_analyser = ctk.CTkButton(
            self.frame_actions,
            text="Analyser",
            command=self.analyser_document,
            width=130
        )
        bouton_analyser.grid(row=0, column=1, padx=8, pady=15)

        bouton_exporter = ctk.CTkButton(
            self.frame_actions,
            text="Exporter",
            command=self.exporter_rapport,
            width=130
        )
        bouton_exporter.grid(row=0, column=2, padx=8, pady=15)

        self.label_fichier = ctk.CTkLabel(
            self.frame_actions,
            text="Aucun fichier sélectionné",
            text_color="gray"
        )
        self.label_fichier.grid(row=0, column=3, padx=15, pady=15, sticky="w")

        self.frame_options = ctk.CTkFrame(self.root, corner_radius=15)
        self.frame_options.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.frame_options.grid_columnconfigure(0, weight=1)
        self.frame_options.grid_rowconfigure(1, weight=1)

        self.creer_options()
        self.creer_onglets()

    def creer_options(self):
        frame_ligne_options = ctk.CTkFrame(self.frame_options, fg_color="transparent")
        frame_ligne_options.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")

        label_limite = ctk.CTkLabel(
            frame_ligne_options,
            text="Phrase trop longue à partir de :"
        )
        label_limite.pack(side="left", padx=(0, 8))

        self.input_limite_phrase = ctk.CTkEntry(
            frame_ligne_options,
            width=70,
            justify="center"
        )
        self.input_limite_phrase.insert(0, "35")
        self.input_limite_phrase.pack(side="left")

        label_mots = ctk.CTkLabel(
            frame_ligne_options,
            text="mots"
        )
        label_mots.pack(side="left", padx=8)

        bouton_mode = ctk.CTkButton(
            frame_ligne_options,
            text="Changer thème",
            command=self.changer_theme,
            width=130
        )
        bouton_mode.pack(side="right", padx=5)

    def creer_onglets(self):
        self.tabview = ctk.CTkTabview(
            self.frame_options,
            corner_radius=15
        )
        self.tabview.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")

        self.tabview.add("Statistiques")
        self.tabview.add("Mots fréquents")
        self.tabview.add("Phrases longues")
        self.tabview.add("Termes techniques")

        self.zone_stats = self.creer_zone_texte(self.tabview.tab("Statistiques"))
        self.zone_mots = self.creer_zone_texte(self.tabview.tab("Mots fréquents"))
        self.zone_phrases = self.creer_zone_texte(self.tabview.tab("Phrases longues"))
        self.zone_termes = self.creer_zone_texte(self.tabview.tab("Termes techniques"))

    def creer_zone_texte(self, parent):
        zone_texte = ctk.CTkTextbox(
            parent,
            wrap="word",
            font=ctk.CTkFont(size=14)
        )
        zone_texte.pack(expand=True, fill="both", padx=10, pady=10)
        return zone_texte

    def changer_theme(self):
        mode_actuel = ctk.get_appearance_mode()

        if mode_actuel == "Dark":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")

    def choisir_fichier(self):
        chemin = filedialog.askopenfilename(
            title="Choisir un document",
            filetypes=[
                ("Documents texte et PDF", "*.txt *.pdf"),
                ("Fichiers texte", "*.txt"),
                ("Fichiers PDF", "*.pdf")
            ]
        )

        if chemin:
            self.chemin_fichier = chemin
            nom_fichier = Path(chemin).name
            self.label_fichier.configure(
                text=f"Fichier : {nom_fichier}",
                text_color="white"
            )
            self.vider_resultats()

    def lire_document(self):
        if not self.chemin_fichier:
            messagebox.showwarning(
                "Aucun fichier",
                "Veuillez sélectionner un fichier avant de lancer l'analyse."
            )
            return None

        extension = Path(self.chemin_fichier).suffix.lower()

        if extension == ".txt":
            with open(self.chemin_fichier, "r", encoding="utf-8") as fichier:
                return fichier.read()

        if extension == ".pdf":
            return lire_pdf(self.chemin_fichier)

        messagebox.showerror(
            "Format non supporté",
            "Seuls les fichiers .txt et .pdf sont acceptés."
        )
        return None

    def analyser_document(self):
        texte = self.lire_document()

        if not texte:
            return

        try:
            limite_phrase_longue = int(self.input_limite_phrase.get())
        except ValueError:
            messagebox.showerror(
                "Valeur invalide",
                "La limite des phrases longues doit être un nombre entier."
            )
            return

        if limite_phrase_longue <= 0:
            messagebox.showerror(
                "Valeur invalide",
                "La limite doit être supérieure à 0."
            )
            return

        self.resultat = analyser_texte(
            texte,
            limite_phrase_longue=limite_phrase_longue
        )

        self.afficher_resultat()

        messagebox.showinfo(
            "Analyse terminée",
            "Le document a bien été analysé."
        )

    def afficher_resultat(self):
        self.vider_resultats()

        self.afficher_statistiques()
        self.afficher_mots_frequents()
        self.afficher_phrases_longues()
        self.afficher_termes_techniques()

    def afficher_statistiques(self):
        self.zone_stats.insert("end", "STATISTIQUES GÉNÉRALES\n\n")

        self.zone_stats.insert(
            "end",
            f"Nombre de caractères : {self.resultat['nombre_caracteres']}\n"
        )

        self.zone_stats.insert(
            "end",
            f"Nombre de mots : {self.resultat['nombre_mots']}\n"
        )

        self.zone_stats.insert(
            "end",
            f"Nombre de phrases : {self.resultat['nombre_phrases']}\n"
        )

        if self.resultat["nombre_phrases"] > 0:
            moyenne = self.resultat["nombre_mots"] / self.resultat["nombre_phrases"]
            self.zone_stats.insert(
                "end",
                f"Nombre moyen de mots par phrase : {moyenne:.2f}\n"
            )

        if "phrases_longues" in self.resultat:
            self.zone_stats.insert(
                "end",
                f"Nombre de phrases longues : {len(self.resultat['phrases_longues'])}\n"
            )

    def afficher_mots_frequents(self):
        self.zone_mots.insert("end", "MOTS LES PLUS FRÉQUENTS\n\n")

        if len(self.resultat["mots_frequents"]) == 0:
            self.zone_mots.insert("end", "Aucun mot fréquent détecté.\n")
            return

        for index, (mot, frequence) in enumerate(self.resultat["mots_frequents"], start=1):
            self.zone_mots.insert(
                "end",
                f"{index}. {mot} : {frequence}\n"
            )

    def afficher_phrases_longues(self):
        limite = self.input_limite_phrase.get()

        self.zone_phrases.insert(
            "end",
            f"PHRASES DE PLUS DE {limite} MOTS\n\n"
        )

        if "phrases_longues" not in self.resultat:
            self.zone_phrases.insert(
                "end",
                "La détection des phrases longues n'est pas encore disponible.\n"
            )
            return

        if len(self.resultat["phrases_longues"]) == 0:
            self.zone_phrases.insert(
                "end",
                "Aucune phrase trop longue détectée.\n"
            )
            return

        for index, item in enumerate(self.resultat["phrases_longues"], start=1):
            self.zone_phrases.insert(
                "end",
                f"{index}. {item['nombre_mots']} mots\n"
            )
            self.zone_phrases.insert(
                "end",
                f"{item['phrase']}\n\n"
            )

    def afficher_termes_techniques(self):
        self.zone_termes.insert("end", "TERMES TECHNIQUES DÉTECTÉS\n\n")

        if "termes_techniques" not in self.resultat:
            self.zone_termes.insert(
                "end",
                "La détection des termes techniques n'est pas encore disponible.\n"
            )
            return

        if len(self.resultat["termes_techniques"]) == 0:
            self.zone_termes.insert(
                "end",
                "Aucun terme technique détecté.\n"
            )
            return

        for terme in self.resultat["termes_techniques"]:
            self.zone_termes.insert("end", f"- {terme}\n")

    def vider_resultats(self):
        zones = [
            self.zone_stats,
            self.zone_mots,
            self.zone_phrases,
            self.zone_termes
        ]

        for zone in zones:
            zone.delete("1.0", "end")

    def exporter_rapport(self):
        if not self.resultat:
            messagebox.showwarning(
                "Aucune analyse",
                "Veuillez analyser un document avant d'exporter le rapport."
            )
            return

        chemin_sortie = filedialog.asksaveasfilename(
            title="Exporter le rapport",
            defaultextension=".txt",
            filetypes=[
                ("Fichier texte", "*.txt")
            ]
        )

        if chemin_sortie:
            exporter_resultat(self.resultat, chemin_sortie)
            messagebox.showinfo(
                "Export terminé",
                "Le rapport a bien été exporté."
            )