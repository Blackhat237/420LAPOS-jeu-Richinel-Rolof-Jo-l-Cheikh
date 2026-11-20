"""
Divine un nombre - un jeu en Python avec 4 classes.

Classes :
    1. Joueur     : garde le nom, le nombre d'essais et le score du joueur.
    2. Nombre     : contient le nombre secret et compare les propositions.
    3. Partie     : gère le déroulement d'une partie (saisie, indices, victoire).
    4. Jeu        : gère le menu, les niveaux, les parties multiples et la sauvegarde.

Pour jouer : python divine_un_nombre.py
"""

import json
import os
import random

# Fichier de sauvegarde, placé à côté du programme
FICHIER_SAUVEGARDE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "sauvegarde_divine.json"
)


class Joueur:
    """Représente le joueur et ses statistiques."""

    def __init__(self, nom):
        self.nom = nom
        self.essais = 0
        self.parties_jouees = 0
        self.parties_gagnees = 0
        self.meilleur_score = None  # plus petit nombre d'essais

    def nouvel_essai(self):
        self.essais += 1

    def reinitialiser_essais(self):
        self.essais = 0

    def enregistrer_resultat(self, gagne):
        self.parties_jouees += 1
        if gagne:
            self.parties_gagnees += 1
            if self.meilleur_score is None or self.essais < self.meilleur_score:
                self.meilleur_score = self.essais

    def vers_dict(self):
        """Données à sauvegarder."""
        return {
            "parties_jouees": self.parties_jouees,
            "parties_gagnees": self.parties_gagnees,
            "meilleur_score": self.meilleur_score,
        }

    def charger_dict(self, donnees):
        """Recharge les statistiques ; ignore toute valeur invalide."""
        try:
            jouees = int(donnees.get("parties_jouees", 0))
            gagnees = int(donnees.get("parties_gagnees", 0))
            meilleur = donnees.get("meilleur_score")
            meilleur = int(meilleur) if meilleur is not None else None
        except (TypeError, ValueError, AttributeError):
            return
        if jouees < 0 or gagnees < 0 or gagnees > jouees:
            return
        self.parties_jouees = jouees
        self.parties_gagnees = gagnees
        self.meilleur_score = meilleur

    def __str__(self):
        meilleur = self.meilleur_score if self.meilleur_score is not None else "-"
        return (
            f"{self.nom} : {self.parties_gagnees} victoire(s) sur "
            f"{self.parties_jouees} partie(s) | meilleur score : {meilleur} essai(s)"
        )


class Nombre:
    """Contient le nombre secret et compare les propositions."""

    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum
        self.secret = random.randint(minimum, maximum)

    def comparer(self, proposition):
        """Retourne 'trop_petit', 'trop_grand' ou 'correct'."""
        if proposition < self.secret:
            return "trop_petit"
        if proposition > self.secret:
            return "trop_grand"
        return "correct"

    def est_dans_intervalle(self, valeur):
        return self.minimum <= valeur <= self.maximum


class Partie:
    """Gère une partie complète pour un joueur."""

    def __init__(self, joueur, minimum, maximum, essais_max):
        self.joueur = joueur
        self.nombre = Nombre(minimum, maximum)
        self.essais_max = essais_max

    def demander_proposition(self):
        """Demande un nombre valide au joueur. Retourne None si le joueur quitte."""
        while True:
            try:
                texte = input(
                    f"Ton choix ({self.nombre.minimum}-{self.nombre.maximum}, "
                    f"'q' pour quitter) : "
                ).strip()
            except EOFError:
                return None

            if texte.lower() in ("q", "quitter"):
                return None

            try:
                valeur = int(texte)
            except ValueError:
                print("  Entrée invalide : écris un nombre entier.")
                continue

            if not self.nombre.est_dans_intervalle(valeur):
                print(
                    f"  Le nombre doit être entre {self.nombre.minimum} "
                    f"et {self.nombre.maximum}."
                )
                continue

            return valeur

    def jouer(self):
        """Joue la partie. Retourne True si gagnée, False sinon."""
        self.joueur.reinitialiser_essais()
        print(
            f"\nJ'ai choisi un nombre entre {self.nombre.minimum} et "
            f"{self.nombre.maximum}. Tu as {self.essais_max} essais."
        )

        while self.joueur.essais < self.essais_max:
            restants = self.essais_max - self.joueur.essais
            print(f"\nEssais restants : {restants}")
            proposition = self.demander_proposition()

            if proposition is None:
                print(f"Tu abandonnes... Le nombre était {self.nombre.secret}.")
                self.joueur.enregistrer_resultat(False)
                return False

            self.joueur.nouvel_essai()
            resultat = self.nombre.comparer(proposition)

            if resultat == "correct":
                print(
                    f"Bravo {self.joueur.nom} ! Tu as trouvé {self.nombre.secret} "
                    f"en {self.joueur.essais} essai(s) !"
                )
                self.joueur.enregistrer_resultat(True)
                return True
            elif resultat == "trop_petit":
                print("C'est plus grand !")
            else:
                print("C'est plus petit !")

        print(f"\nPerdu ! Le nombre était {self.nombre.secret}.")
        self.joueur.enregistrer_resultat(False)
        return False


class Jeu:
    """Menu principal : choix du niveau, parties multiples, statistiques."""

    NIVEAUX = {
        "1": ("Facile", 1, 20, 8),
        "2": ("Moyen", 1, 100, 10),
        "3": ("Difficile", 1, 1000, 12),
    }

    def __init__(self, fichier=FICHIER_SAUVEGARDE):
        self.joueur = None
        self.fichier = fichier

    def lire_sauvegardes(self):
        """Lit le fichier de sauvegarde. Retourne {} s'il est absent ou abîmé."""
        try:
            with open(self.fichier, "r", encoding="utf-8") as f:
                donnees = json.load(f)
            return donnees if isinstance(donnees, dict) else {}
        except (OSError, ValueError):
            return {}

    def sauvegarder(self):
        """Enregistre les statistiques du joueur actuel."""
        if self.joueur is None:
            return False
        donnees = self.lire_sauvegardes()
        donnees[self.joueur.nom] = self.joueur.vers_dict()
        try:
            with open(self.fichier, "w", encoding="utf-8") as f:
                json.dump(donnees, f, ensure_ascii=False, indent=2)
            return True
        except OSError:
            print("  (Impossible de sauvegarder la progression.)")
            return False

    def charger(self):
        """Recharge les statistiques du joueur s'il a déjà joué. Retourne True si trouvé."""
        donnees = self.lire_sauvegardes().get(self.joueur.nom)
        if isinstance(donnees, dict):
            self.joueur.charger_dict(donnees)
            return self.joueur.parties_jouees > 0
        return False

    def demander_nom(self):
        try:
            nom = input("Quel est ton nom ? ").strip()
        except EOFError:
            nom = ""
        return nom if nom else "Joueur"

    def choisir_niveau(self):
        print("\nChoisis un niveau :")
        for cle, (nom, mini, maxi, essais) in self.NIVEAUX.items():
            print(f"  {cle}. {nom} (nombre entre {mini} et {maxi}, {essais} essais)")

        while True:
            try:
                choix = input("Niveau (1-3) : ").strip()
            except EOFError:
                return None
            if choix in self.NIVEAUX:
                return self.NIVEAUX[choix]
            print("  Choix invalide. Entre 1, 2 ou 3.")

    def rejouer(self):
        while True:
            try:
                reponse = input("\nRejouer ? (o/n) : ").strip().lower()
            except EOFError:
                return False
            if reponse in ("o", "oui"):
                return True
            if reponse in ("n", "non"):
                return False
            print("  Réponds par 'o' ou 'n'.")

    def demarrer(self):
        print("=" * 40)
        print("      DIVINE UN NOMBRE")
        print("=" * 40)
        self.joueur = Joueur(self.demander_nom())
        if self.charger():
            print(f"\nContent de te revoir {self.joueur.nom} !")
            print("Progression chargée : " + str(self.joueur))
        else:
            print(f"\nSalut {self.joueur.nom} !")

        while True:
            niveau = self.choisir_niveau()
            if niveau is None:
                break
            _, minimum, maximum, essais_max = niveau
            partie = Partie(self.joueur, minimum, maximum, essais_max)
            partie.jouer()
            if self.sauvegarder():
                print("\n(Progression sauvegardée.)")
            print(str(self.joueur))
            if not self.rejouer():
                break

        print(f"\nMerci d'avoir joué, {self.joueur.nom} ! À bientôt.")


def main():
    Jeu().demarrer()


if __name__ == "__main__":
    main()
