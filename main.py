import json

# Initialisation de la bibliothèque
bibliotheque = []

# read json file1
try:
    f1 = open('data/bibli.json', 'r', encoding='utf-8')
    data = json.load(f1)
    bibliotheque = data.get('bibliotheque')
    f1.close()
except FileNotFoundError:
    print('File not found')
except json.decoder.JSONDecodeError as e:
    print('JSON Decode Error:', e)
except Exception as e:
    print('Error:', e)

def save(data):
    with open('data/bibli.json', 'w', encoding='utf-8') as outfile:
        data = {'bibliotheque': data}
        json.dump(data, outfile, indent=4, ensure_ascii=False)
        
def dispotable(avaliable=True):
    '''
    returns a table of books avaliable.
    if False is passed as param, returns the books that have been borrowed
    '''
    table = []
    for livre in bibliotheque:
        if avaliable == livre['disponible']: table.append(livre['titre'])
    return table


def ajouter_livre(titre=None, auteur=None):
    """Ajoute un nouveau livre à la bibliothèque."""
    if titre is None:
        titre = input("Entrez le titre du livre : ").strip()
    if auteur is None:
        auteur = input("Entrez l'auteur du livre : ").strip()
    
    # Vérification des doublons
    for livre in bibliotheque:
        if livre["titre"].lower() == titre.lower() and livre["auteur"].lower() == auteur.lower():
            print("Ce livre existe déjà dans la bibliothèque!")
            return
    
    nouveau_livre = {
        "titre": titre,
        "auteur": auteur,
        "disponible": True
    }
    bibliotheque.append(nouveau_livre)
    save(bibliotheque)
    print(f"Le livre '{titre}' de {auteur} a été ajouté avec succès!")

def afficher_livres(disponible=None):
    """Affiche les livres de la bibliothèque avec filtre optionnel."""
    if not bibliotheque:
        print("La bibliothèque est vide!")
        return
    
    print("\nListe des livres:")
    print("-" * 50)
    for livre in bibliotheque:
        if disponible is None or livre["disponible"] == disponible:
            status = "disponible" if livre["disponible"] else "emprunté"
            print(f"Titre: {livre['titre']}")
            print(f"Auteur: {livre['auteur']}")
            print(f"Statut: {status}")
            print("-" * 50)

def emprunter_livre(titre):
    """Permet d'emprunter un livre."""
    for livre in bibliotheque:
        if livre["titre"].lower() == titre.lower():
            if livre["disponible"]:
                livre["disponible"] = False
                save(bibliotheque)
                print(f"Le livre '{titre}' a été emprunté avec succès!")
            else:
                print(f"Désolé, le livre '{titre}' est déjà emprunté.")
            return
    print(f"Le livre '{titre}' n'existe pas dans la bibliothèque.")

def retourner_livre(titre):
    """Permet de retourner un livre."""
    for livre in bibliotheque:
        if livre["titre"].lower() == titre.lower():
            if not livre["disponible"]:
                livre["disponible"] = True
                save(bibliotheque)
                print(f"Le livre '{titre}' a été retourné avec succès!")
            else:
                print(f"Le livre '{titre}' n'était pas emprunté.")
            return
    print(f"Le livre '{titre}' n'existe pas dans la bibliothèque.")

def supprimer_livre(titre):
    """Permet de supprimer un livre de la bibliothèque."""
    for i, livre in enumerate(bibliotheque):
        if livre["titre"].lower() == titre.lower():
            del bibliotheque[i]
            save(bibliotheque)
            print(f"Le livre '{titre}' a été supprimé avec succès!")
            return
    print(f"Le livre '{titre}' n'existe pas dans la bibliothèque.")

def rechercher_livre(recherche):
    """Recherche un livre par titre ou auteur."""
    recherche = recherche.lower()
    resultats = []
    for livre in bibliotheque:
        if recherche in livre["titre"].lower() or recherche in livre["auteur"].lower():
            resultats.append(livre)
    
    if resultats:
        print("\nRésultats de la recherche:")
        print("-" * 50)
        for livre in resultats:
            status = "disponible" if livre["disponible"] else "emprunté"
            print(f"Titre: {livre['titre']}")
            print(f"Auteur: {livre['auteur']}")
            print(f"Statut: {status}")
            print("-" * 50)
    else:
        print("Aucun livre trouvé.")

# Menu principal
def menu_principal():
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
            ajouter_livre()
        elif choix == "2":
            afficher_livres()
        elif choix == "3":
            afficher_livres(disponible=True)
        elif choix == "4":
            afficher_livres(disponible=False)
        elif choix == "5":
            books = dispotable()
            for i, title in enumerate(books):
                print(f'{i+1}. {title}')
            book = int(input("Entrez le numéro du livre à emprunter : ")) - 1
            emprunter_livre(books[book])
        elif choix == "6":
            books = dispotable(False)
            for i, title in enumerate(books):
                print(f'{i+1}. {title}')
            book = int(input("Entrez le numéro du livre à rendre : ")) - 1
            retourner_livre(books[book])
        elif choix == "7":
            titre = input("Entrez le titre du livre à supprimer : ")
            supprimer_livre(titre)
        elif choix == "8":
            recherche = input("Entrez le titre ou l'auteur à rechercher : ")
            rechercher_livre(recherche)
        elif choix == "9":
            print("Au revoir!")
            break
        else:
            print("Option invalide. Veuillez réessayer.")

menu_principal()