import json
from typing import List, Dict, Optional

class Livre:
    def __init__(self, titre: str, auteur: str, disponible: bool = True):
        self.titre = titre
        self.auteur = auteur
        self.disponible = disponible

    def to_dict(self) -> Dict:
        return {
            "titre": self.titre,
            "auteur": self.auteur,
            "disponible": self.disponible
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Livre':
        return cls(data["titre"], data["auteur"], data["disponible"])

class Membre:
    def __init__(self, nom: str, id: int):
        self.nom = nom
        self.id = id
        self.livres_empruntes: List[str] = []

    def to_dict(self) -> Dict:
        return {
            "nom": self.nom,
            "id": self.id,
            "livres_empruntes": self.livres_empruntes
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Membre':
        membre = cls(data["nom"], data["id"])
        membre.livres_empruntes = data.get("livres_empruntes", [])
        return membre

class GestionnaireFichiers:
    @staticmethod
    def charger_donnees(chemin: str) -> Dict:
        try:
            with open(chemin, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f'Fichier non trouvé: {chemin}')
            return {"bibliotheque": [], "membres": []}
        except json.decoder.JSONDecodeError as e:
            print(f'Erreur de décodage JSON: {e}')
            return {"bibliotheque": [], "membres": []}
        except Exception as e:
            print(f'Erreur: {e}')
            return {"bibliotheque": [], "membres": []}

    @staticmethod
    def sauvegarder_donnees(chemin: str, donnees: Dict) -> None:
        with open(chemin, 'w', encoding='utf-8') as f:
            json.dump(donnees, f, indent=4, ensure_ascii=False)

class Bibliotheque:
    def __init__(self):
        self.gestionnaire = GestionnaireFichiers()
        self.livres: List[Livre] = []
        self.membres: List[Membre] = []
        self.charger_donnees()

    def charger_donnees(self) -> None:
        donnees_bibli = self.gestionnaire.charger_donnees('data/bibli.json')
        donnees_membres = self.gestionnaire.charger_donnees('data/membre.json')

        self.livres = [Livre.from_dict(livre) for livre in donnees_bibli.get('bibliotheque', [])]
        self.membres = [Membre.from_dict(membre) for membre in donnees_membres.get('membres', [])]

    def sauvegarder_bibliotheque(self) -> None:
        donnees = {
            "bibliotheque": [livre.to_dict() for livre in self.livres]
        }
        self.gestionnaire.sauvegarder_donnees('data/bibli.json', donnees)

    def sauvegarder_membres(self) -> None:
        donnees = {
            "membres": [membre.to_dict() for membre in self.membres]
        }
        self.gestionnaire.sauvegarder_donnees('data/membre.json', donnees)

    def ajouter_livre(self, titre: Optional[str] = None, auteur: Optional[str] = None) -> None:
        if titre is None:
            titre = input("Entrez le titre du livre : ").strip()
        if auteur is None:
            auteur = input("Entrez l'auteur du livre : ").strip()

        if any(livre.titre.lower() == titre.lower() and livre.auteur.lower() == auteur.lower() 
               for livre in self.livres):
            print("Ce livre existe déjà dans la bibliothèque!")
            return

        nouveau_livre = Livre(titre, auteur)
        self.livres.append(nouveau_livre)
        self.sauvegarder_bibliotheque()
        print(f"Le livre '{titre}' de {auteur} a été ajouté avec succès!")

    def afficher_livres(self, disponible: Optional[bool] = None) -> None:
        if not self.livres:
            print("La bibliothèque est vide!")
            return

        print("\nListe des livres:")
        print("-" * 50)
        for livre in self.livres:
            if disponible is None or livre.disponible == disponible:
                status = "disponible" if livre.disponible else "emprunté"
                print(f"Titre: {livre.titre}")
                print(f"Auteur: {livre.auteur}")
                print(f"Statut: {status}")
                print("-" * 50)

    def obtenir_livres_disponibles(self) -> List[str]:
        return [livre.titre for livre in self.livres if livre.disponible]

    def obtenir_livres_empruntes(self) -> List[str]:
        return [livre.titre for livre in self.livres if not livre.disponible]

    def emprunter_livre(self, titre: str) -> None:
        for livre in self.livres:
            if livre.titre.lower() == titre.lower():
                if livre.disponible:
                    livre.disponible = False
                    self.sauvegarder_bibliotheque()
                    print(f"Le livre '{titre}' a été emprunté avec succès!")
                else:
                    print(f"Désolé, le livre '{titre}' est déjà emprunté.")
                return
        print(f"Le livre '{titre}' n'existe pas dans la bibliothèque.")

    def retourner_livre(self, titre: str) -> None:
        for livre in self.livres:
            if livre.titre.lower() == titre.lower():
                if not livre.disponible:
                    livre.disponible = True
                    self.sauvegarder_bibliotheque()
                    print(f"Le livre '{titre}' a été retourné avec succès!")
                else:
                    print(f"Le livre '{titre}' n'était pas emprunté.")
                return
        print(f"Le livre '{titre}' n'existe pas dans la bibliothèque.")

    def supprimer_livre(self, titre: str) -> None:
        for i, livre in enumerate(self.livres):
            if livre.titre.lower() == titre.lower():
                del self.livres[i]
                self.sauvegarder_bibliotheque()
                print(f"Le livre '{titre}' a été supprimé avec succès!")
                return
        print(f"Le livre '{titre}' n'existe pas dans la bibliothèque.")

    def rechercher_livre(self, recherche: str) -> None:
        recherche = recherche.lower()
        resultats = [livre for livre in self.livres 
                    if recherche in livre.titre.lower() or recherche in livre.auteur.lower()]

        if resultats:
            print("\nRésultats de la recherche:")
            print("-" * 50)
            for livre in resultats:
                status = "disponible" if livre.disponible else "emprunté"
                print(f"Titre: {livre.titre}")
                print(f"Auteur: {livre.auteur}")
                print(f"Statut: {status}")
                print("-" * 50)
        else:
            print("Aucun livre trouvé.")

class Interface:
    def __init__(self):
        self.bibliotheque = Bibliotheque()

    def afficher_menu(self) -> None:
        while True:
            print("\nOptions:")
            print("1. Ajouter un livre")
            print("2. Afficher tous les livres")
            print("3. Afficher les livres disponibles")
            print("4. Afficher les livres empruntés")
            print("5. Emprunter un livre")
            print("6. Retourner un livre")
            print("7. Supprimer un livre")
            print("8. Rechercher un livre")
            print("9. Quitter")

            choix = input("\nChoisissez une option (1-9) : ")

            if choix == "1":
                self.bibliotheque.ajouter_livre()
            elif choix == "2":
                self.bibliotheque.afficher_livres()
            elif choix == "3":
                self.bibliotheque.afficher_livres(disponible=True)
            elif choix == "4":
                self.bibliotheque.afficher_livres(disponible=False)
            elif choix == "5":
                livres_disponibles = self.bibliotheque.obtenir_livres_disponibles()
                for i, titre in enumerate(livres_disponibles, 1):
                    print(f'{i}. {titre}')
                if livres_disponibles:
                    try:
                        choix = int(input("Entrez le numéro du livre à emprunter : ")) - 1
                        if 0 <= choix < len(livres_disponibles):
                            self.bibliotheque.emprunter_livre(livres_disponibles[choix])
                        else:
                            print("Numéro invalide.")
                    except ValueError:
                        print("Veuillez entrer un numéro valide.")
            elif choix == "6":
                livres_empruntes = self.bibliotheque.obtenir_livres_empruntes()
                for i, titre in enumerate(livres_empruntes, 1):
                    print(f'{i}. {titre}')
                if livres_empruntes:
                    try:
                        choix = int(input("Entrez le numéro du livre à rendre : ")) - 1
                        if 0 <= choix < len(livres_empruntes):
                            self.bibliotheque.retourner_livre(livres_empruntes[choix])
                        else:
                            print("Numéro invalide.")
                    except ValueError:
                        print("Veuillez entrer un numéro valide.")
            elif choix == "7":
                titre = input("Entrez le titre du livre à supprimer : ")
                self.bibliotheque.supprimer_livre(titre)
            elif choix == "8":
                recherche = input("Entrez le titre ou l'auteur à rechercher : ")
                self.bibliotheque.rechercher_livre(recherche)
            elif choix == "9" or choix.lower() in ["q", "quit", "exit"]:
                print("Au revoir!")
                break
            else:
                print("Option invalide. Veuillez réessayer.")

if __name__ == "__main__":
    interface = Interface()
    interface.afficher_menu()