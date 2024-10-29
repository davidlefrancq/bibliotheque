import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class Livre:
    def __init__(self, titre: str, auteur: str, disponible: bool = True, emprunteur_id: Optional[int] = None):
        self.titre = titre
        self.auteur = auteur
        self.disponible = disponible
        self.emprunteur_id = emprunteur_id
        self.date_emprunt = None

    def to_dict(self) -> Dict:
        return {
            "titre": self.titre,
            "auteur": self.auteur,
            "disponible": self.disponible,
            "emprunteur_id": self.emprunteur_id,
            "date_emprunt": self.date_emprunt.isoformat() if self.date_emprunt else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Livre':
        livre = cls(data["titre"], data["auteur"], data["disponible"], data.get("emprunteur_id"))
        if data.get("date_emprunt"):
            livre.date_emprunt = datetime.fromisoformat(data["date_emprunt"])
        return livre


class Membre:
    LIMITE_EMPRUNTS = 3  # Limitation du nombre de livres empruntables
    
    def __init__(self, nom: str, id: int):
        self.nom = nom
        self.id = id
        self.livres_empruntes: List[str] = []
        self.penalites = 0

    def peut_emprunter(self) -> bool:
        return len(self.livres_empruntes) < self.LIMITE_EMPRUNTS and self.penalites == 0

    def to_dict(self) -> Dict:
        return {
            "nom": self.nom,
            "id": self.id,
            "livres_empruntes": self.livres_empruntes,
            "penalites": self.penalites
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Membre':
        # Gestion des différents formats possibles pour les clés
        id_membre = data.get("id")
        if id_membre is None:
            raise ValueError(f"Données de membre invalides : id manquant dans {data}")
        
        membre = cls(data["nom"], id_membre)
        membre.livres_empruntes = data.get("livres_empruntes", [])
        membre.penalites = data.get("penalites", 0)
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

        with open(chemin, 'w', encoding='utf-8') as f:
            json.dump(donnees, f, indent=4, ensure_ascii=False)

class Bibliotheque:
    def __init__(self):
        self.gestionnaire = GestionnaireFichiers()
        self.livres: List[Livre] = []
        self.membres: List[Membre] = []
        self.prochain_id = 1
        self.charger_donnees()

    def charger_donnees(self) -> None:
        donnees_bibli = self.gestionnaire.charger_donnees('data/bibli.json')
        donnees_membres = self.gestionnaire.charger_donnees('data/membre.json')

        try:
            self.livres = [Livre.from_dict(livre) for livre in donnees_bibli.get('bibliotheque', [])]
            self.membres = []
            for membre_data in donnees_membres.get('membres', []):
                try:
                    membre = Membre.from_dict(membre_data)
                    self.membres.append(membre)
                except (KeyError, ValueError) as e:
                    print(f"Erreur lors du chargement d'un membre: {e}")
                    continue

            # Mettre à jour prochain_id
            if self.membres:
                self.prochain_id = max(membre.id for membre in self.membres) + 1
            else:
                self.prochain_id = 1

        except Exception as e:
            print(f"Erreur lors du chargement des données: {e}")
            self.livres = []
            self.membres = []
            self.prochain_id = 1

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

    def verifier_penalites(self) -> None:
        maintenant = datetime.now()
        for livre in self.livres:
            if not livre.disponible and livre.date_emprunt:
                duree_emprunt = maintenant - livre.date_emprunt
                if duree_emprunt > timedelta(days=14):
                    membre = next((m for m in self.membres if m.id == livre.emprunteur_id), None)
                    if membre:
                        membre.penalites += 1
                        self.sauvegarder_membres()

    def inscrire_membre(self, nom: Optional[str] = None) -> None:
        if nom is None:
            nom = input("Entrez le nom du membre : ").strip()
        
        nouveau_membre = Membre(nom, self.prochain_id)
        self.membres.append(nouveau_membre)
        self.prochain_id += 1
        self.sauvegarder_membres()
        print(f"Le membre '{nom}' a été inscrit avec succès! (ID: {nouveau_membre.id})")

    def afficher_membre(self, id: Optional[int] = None) -> None:
        if id is None:
            try:
                id = int(input("Entrez l'ID du membre : "))
            except ValueError:
                print("ID invalide!")
                return

        membre = next((m for m in self.membres if m.id == id), None)
        if membre:
            print(f"\nInformations du membre:")
            print(f"Nom: {membre.nom}")
            print(f"ID: {membre.id}")
            print(f"Pénalités: {membre.penalites}")
            if membre.livres_empruntes:
                print("Livres empruntés:")
                for titre in membre.livres_empruntes:
                    print(f"- {titre}")
            else:
                print("Aucun livre emprunté")
        else:
            print("Membre non trouvé!")

    def emprunter_livre(self, titre: str, id_membre: Optional[int] = None) -> None:
        if id_membre is None:
            try:
                id_membre = int(input("Entrez l'ID du membre : "))
            except ValueError:
                print("ID invalide!")
                return

        membre = next((m for m in self.membres if m.id == id_membre), None)
        if not membre:
            print("Membre non trouvé!")
            return

        if not membre.peut_emprunter():
            if membre.penalites > 0:
                print("Ce membre a des pénalités et ne peut pas emprunter de livres!")
            else:
                print(f"Ce membre a déjà emprunté le maximum de livres autorisé ({membre.LIMITE_EMPRUNTS})!")
            return

        livre = next((l for l in self.livres if l.titre.lower() == titre.lower()), None)
        if not livre:
            print(f"Le livre '{titre}' n'existe pas dans la bibliothèque.")
            return

        if not livre.disponible:
            print(f"Désolé, le livre '{titre}' est déjà emprunté.")
            return

        livre.disponible = False
        livre.emprunteur_id = membre.id
        livre.date_emprunt = datetime.now()
        membre.livres_empruntes.append(titre)
        
        self.sauvegarder_bibliotheque()
        self.sauvegarder_membres()
        print(f"Le livre '{titre}' a été emprunté avec succès par {membre.nom}!")

    def retourner_livre(self, titre: str, id_membre: Optional[int] = None) -> None:
        if id_membre is None:
            try:
                id_membre = int(input("Entrez l'ID du membre : "))
            except ValueError:
                print("ID invalide!")
                return

        membre = next((m for m in self.membres if m.id == id_membre), None)
        if not membre:
            print("Membre non trouvé!")
            return

        livre = next((l for l in self.livres if l.titre.lower() == titre.lower()), None)
        if not livre:
            print(f"Le livre '{titre}' n'existe pas dans la bibliothèque.")
            return

        if livre.emprunteur_id != membre.id:
            print(f"Ce livre n'a pas été emprunté par ce membre.")
            return

        livre.disponible = True
        livre.emprunteur_id = None
        livre.date_emprunt = None
        membre.livres_empruntes.remove(titre)
        
        self.sauvegarder_bibliotheque()
        self.sauvegarder_membres()
        print(f"Le livre '{titre}' a été retourné avec succès par {membre.nom}!")

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
                if not livre.disponible:
                    membre = next((m for m in self.membres if m.id == livre.emprunteur_id), None)
                    if membre:
                        print(f"Emprunté par: {membre.nom} (ID: {membre.id})")
                print("-" * 50)

    def obtenir_livres_disponibles(self) -> List[str]:
        return [livre.titre for livre in self.livres if livre.disponible]

    def obtenir_livres_empruntes(self) -> List[str]:
        return [livre.titre for livre in self.livres if not livre.disponible]

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
            print("9. Inscrire un membre")
            print("10. Afficher les informations d'un membre")
            print("11. Quitter")

            choix = input("\nChoisissez une option (1-11) : ")

            if choix == "1":
                self.bibliotheque.ajouter_livre()
            elif choix == "2":
                self.bibliotheque.afficher_livres()
            elif choix == "3":
                self.bibliotheque.afficher_livres(disponible=True)
            elif choix == "4":
                self.bibliotheque.afficher_livres(disponible=False)
            elif choix == "5":
                self.bibliotheque.verifier_penalites()
                livres_disponibles = self.bibliotheque.obtenir_livres_disponibles()
                if not livres_disponibles:
                    print("Aucun livre disponible pour l'emprunt.")
                    continue
                
                print("\nLivres disponibles:")
                for i, titre in enumerate(livres_disponibles, 1):
                    print(f'{i}. {titre}')
                
                try:
                    choix_livre = int(input("\nEntrez le numéro du livre à emprunter : ")) - 1
                    if 0 <= choix_livre < len(livres_disponibles):
                        id_membre = int(input("Entrez l'ID du membre : "))
                        self.bibliotheque.emprunter_livre(livres_disponibles[choix_livre], id_membre)
                    else:
                        print("Numéro de livre invalide.")
                except ValueError:
                    print("Veuillez entrer un numéro valide.")
            elif choix == "6":
                livres_empruntes = self.bibliotheque.obtenir_livres_empruntes()
                if not livres_empruntes:
                    print("Aucun livre emprunté à retourner.")
                    continue
                
                print("\nLivres empruntés:")
                for i, titre in enumerate(livres_empruntes, 1):
                    print(f'{i}. {titre}')
                
                try:
                    choix_livre = int(input("\nEntrez le numéro du livre à rendre : ")) - 1
                    if 0 <= choix_livre < len(livres_empruntes):
                        id_membre = int(input("Entrez l'ID du membre : "))
                        self.bibliotheque.retourner_livre(livres_empruntes[choix_livre], id_membre)
                    else:
                        print("Numéro de livre invalide.")
                except ValueError:
                    print("Veuillez entrer un numéro valide.")
            elif choix == "7":
                titre = input("Entrez le titre du livre à supprimer : ")
                self.bibliotheque.supprimer_livre(titre)
            elif choix == "8":
                recherche = input("Entrez le titre ou l'auteur à rechercher : ")
                self.bibliotheque.rechercher_livre(recherche)
            elif choix == "9":
                self.bibliotheque.inscrire_membre()
            elif choix == "10":
                self.bibliotheque.afficher_membre()
            elif choix == "11" or choix.lower() in ["q", "quit", "exit"]:
                print("Au revoir!")
                break
            else:
                print("Option invalide. Veuillez réessayer.")

if __name__ == "__main__":
    interface = Interface()
    interface.afficher_menu()