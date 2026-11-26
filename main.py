Voilà la v2, celle avec les points, les indices chaud / froid, le niveau Expert et le classement top 3. C'est le code complet, tu peux le copier-coller tel quel.

python
"""
Divine un nombre - un jeu en Python avec 4 classes.

Classes :
    1. Joueur     : garde le nom, le nombre d'essais et le score du joueur.
    2. Nombre     : contient le nombre secret et compare les propositions.
    3. Partie     : gère le déroulement d'une partie (saisie, indices, victoire).
    4. Jeu        : gère le menu, les niveaux, les parties multiples et la sauvegarde.

Version améliorée (v2) — même squelette, 4 ajouts seulement :
    - Points : 1000 de base, -50 par essai après le 1er, +200 si gagné en 3 essais ou moins,
      bonus niveau (Facile 0, Moyen 100, Difficile 300, Expert 500).
    - Indices chaud / froid : Très chaud (écart <= 3), Chaud (<= 10), Tiède (<= 25), sinon Froid.
    - Niveau Expert : 1 à 5000, 15 essais.
    - Classement : top 3 des joueurs, trié par meilleur score en points.

Pour jouer : python main.py
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
        self.points = 0  # points de la dernière partie gagnée, 0 sinon
        self.meilleur_points = None  # plus grand nombre de points en une victoire

    def nouvel_essai(self):
        self.essais += 1

    def reinitialiser_essais(self):
        self.essais = 0

    def enregistrer_resultat(self, gagne, points_gagnes=0):
        self.parties_jouees += 1
        if gagne:
            self.parties_gagnees += 1
            if self.meilleur_score is None or self.essais < self.meilleur_score:
                self.meilleur_score = self.essais
            self.points = points_gagnes
            if self.meilleur_points is None or points_gagnes > self.meilleur_points:
                self.meilleur_points = points_gagnes
        else:
            self.points = 0

    def vers_dict(self):
        """Données à sauvegarder."""
        return {
            "parties_jouees": self.parties_jouees,
            "parties_gagnees": self.parties_gagnees,
            "meilleur_score": self.meilleur_score,
            "meilleur_points": self.meilleur_points,
        }

    def charger_dict(self, donnees):
        """Recharge les statistiques ; ignore toute valeur invalide."""
        try:
            jouees = int(donnees.get("parties_jouees", 0))
            gagnees = int(donnees.get("parties_gagnees", 0))
            meilleur = donnees.get("meilleur_score")
            meilleur = int(meilleur) if meilleur is not None else None
            meilleur_pts = donnees.get("meilleur_points")
            meilleur_pts = int(meilleur_pts) if meilleur_pts is not None else None
        except (TypeError, ValueError, AttributeError):
            return
        if jouees < 0 or gagnees < 0 or gagnees > jouees:
            return
        if meilleur_pts is not None and meilleur_pts < 0:
            return
        self.parties_jouees = jouees
        self.parties_gagnees = gagnees
        self.meilleur_score = meilleur
        self.meilleur_points = meilleur_pts

    def __str__(self):
        meilleur = self.meilleur_score if self.meilleur_score is not None else "-"
        texte = (
            f"{self.nom} : {self.parties_gagnees} victoire(s) sur "
            f"{self.parties_jouees} partie(s) | meilleur score : {meilleur} essai(s)"
        )
        if self.meilleur_points is not None:
            texte += f" | meilleur : {self.meilleur_points} points"
        return texte


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

    def chaleur(self, proposition):
        """Retourne 'Très chaud', 'Chaud', 'Tiède' ou 'Froid' selon l'écart."""
        ecart = abs(proposition - self.secret)
        if ecart <= 3:
            return "Très chaud"
        if ecart <= 10:
            return "Chaud"
        if ecart <= 25:
            return "Tiède"
        return "Froid"

    def est_dans_intervalle(self, valeur):
        return self.minimum <= valeur <= self.maximum


class Partie:
    """Gère une partie complète pour un joueur."""

    def __init__(self, joueur, minimum, maximum, essais_max, bonus_niveau=0):
        self.joueur = joueur
        self.nombre = Nombre(minimum, maximum)
        self.essais_max = essais_max
        self.bonus_niveau = bonus_niveau

    def calculer_points(self):
        """1000 de base, -50 par essai après le 1er, +200 si <= 3 essais, + bonus niveau."""
        points = 1000 - 50 * (self.joueur.essais - 1)
        if self.joueur.essais <= 3:
            points += 200
        points += self.bonus_niveau
        return max(100, points)

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
                points = self.calculer_points()
                print(
                    f"Bravo {self.joueur.nom} ! Tu as trouvé {self.nombre.secret} "
                    f"en {self.joueur.essais} essai(s) ! Tu gagnes {points} points !"
                )
                self.joueur.enregistrer_resultat(True, points)
                return True
            elif resultat == "trop_petit":
                print(f"C'est plus grand ! ({self.nombre.chaleur(proposition)})")
            else:
                print(f"C'est plus petit ! ({self.nombre.chaleur(proposition)})")

        print(f"\nPerdu ! Le nombre était {self.nombre.secret}.")
        self.joueur.enregistrer_resultat(False)
        return False


class Jeu:
    """Menu principal : choix du niveau, parties multiples, statistiques."""

    NIVEAUX = {
        "1": ("Facile", 1, 20, 8),
        "2": ("Moyen", 1, 100, 10),
        "3": ("Difficile", 1, 1000, 12),
        "4": ("Expert", 1, 5000, 15),
    }

    BONUS_NIVEAU = {
        "Facile": 0,
        "Moyen": 100,
        "Difficile": 300,
        "Expert": 500,
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

    def afficher_classement(self):
        """Affiche le top 3, trié par meilleur score en points."""
        donnees = self.lire_sauvegardes()
        classement = []
        for nom, stats in donnees.items():
            if not isinstance(stats, dict):
                continue
            points = stats.get("meilleur_points")
            if not isinstance(points, int):
                continue
            meilleur = stats.get("meilleur_score")
            meilleur = meilleur if isinstance(meilleur, int) else 9999
            classement.append((nom, points, meilleur))
        if not classement:
            return
        classement.sort(key=lambda x: (-x[1], x[2]))
        print("\n--- Classement (top 3) ---")
        for i, (nom, points, meilleur) in enumerate(classement[:3], 1):
            print(f"  {i}. {nom} : {points} points (meilleur : {meilleur} essai(s))")

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
                choix = input("Niveau (1-4) : ").strip()
            except EOFError:
                return None
            if choix in self.NIVEAUX:
                return self.NIVEAUX[choix]
            print("  Choix invalide. Entre 1, 2, 3 ou 4.")

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
            nom_niveau, minimum, maximum, essais_max = niveau
            bonus = self.BONUS_NIVEAU.get(nom_niveau, 0)
            partie = Partie(self.joueur, minimum, maximum, essais_max, bonus)
            partie.jouer()
            if self.sauvegarder():
                print("\n(Progression sauvegardée.)")
            print(str(self.joueur))
            self.afficher_classement()
            if not self.rejouer():
                break

        print(f"\nMerci d'avoir joué, {self.joueur.nom} ! À bientôt.")


def main():
    Jeu().demarrer()


if __name__ == "__main__":
    main()


Le fichier est aussi prêt ici, si tu préfères le télécharger au lieu de copier.
