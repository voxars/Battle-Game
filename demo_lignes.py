"""
Version de démonstration avec beaucoup de cibles/lignes pour un effet visuel spectaculaire.
"""

from battle_circle import Config, main

def demo_lignes_nombreuses():
    """Configuration pour tester un grand nombre de lignes visuelles."""
    print("=== DÉMO : Effet Visuel avec Nombreuses Lignes ===")
    
    # Paramètres pour un maximum de lignes
    Config.DENSITE_CIBLES_PAR_PIXEL = 0.2  # Une cible tous les 5 pixels (très dense)
    Config.NOMBRE_MIN_CIBLES = 100  # Au minimum 100 cibles
    
    # Configuration de jeu adaptée
    Config.NOMBRE_PARTICIPANTS = 3
    Config.TAILLE_CERCLE = 350  # Cercle de taille normale
    Config.CONDITION_VICTOIRE = 300  # Plus long pour profiter de l'effet
    
    # Mouvement modéré pour bien voir les lignes
    Config.VITESSE_MOUVEMENT_JOUEUR = 1.5
    Config.VITESSE_MAX_JOUEUR = 120.0
    Config.AMPLITUDE_BRUIT_POSITION = 30.0
    
    # Lignes plus fines pour éviter la surcharge visuelle
    Config.EPAISSEUR_LIGNE_NORMALE = 1
    Config.EPAISSEUR_LIGNE_CONTRE_ATTAQUE = 3
    
    main()

def demo_lignes_ultra_denses():
    """Configuration pour un effet visuel maximal avec lignes ultra-denses."""
    print("=== DÉMO : Effet Visuel ULTRA - Lignes Très Denses ===")
    
    # Paramètres pour un effet spectaculaire
    Config.DENSITE_CIBLES_PAR_PIXEL = 0.3  # Une cible tous les 3.3 pixels (ultra-dense)
    Config.NOMBRE_MIN_CIBLES = 150  # Minimum très élevé
    
    # Plus de joueurs pour plus de couleurs
    Config.NOMBRE_PARTICIPANTS = 4
    Config.TAILLE_CERCLE = 400  # Cercle plus grand = plus de lignes
    Config.CONDITION_VICTOIRE = 250
    
    # Mouvement rapide pour un effet dynamique
    Config.VITESSE_MOUVEMENT_JOUEUR = 2.5
    Config.VITESSE_MAX_JOUEUR = 180.0
    Config.AMPLITUDE_BRUIT_POSITION = 40.0
    Config.COEFFICIENT_REBOND = 0.9
    
    # Lignes très fines
    Config.EPAISSEUR_LIGNE_NORMALE = 1
    Config.EPAISSEUR_LIGNE_CONTRE_ATTAQUE = 2
    
    main()

if __name__ == "__main__":
    print("Choisissez une démonstration :")
    print("1. Lignes nombreuses (densité normale+)")
    print("2. Lignes ultra-denses (effet spectaculaire)")
    
    choice = input("Votre choix (1-2) : ").strip()
    
    if choice == "1":
        demo_lignes_nombreuses()
    elif choice == "2":
        demo_lignes_ultra_denses()
    else:
        print("Choix invalide, lancement de la version ultra-dense.")
        demo_lignes_ultra_denses()