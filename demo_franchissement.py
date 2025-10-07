"""
Version de test pour le nouveau système de franchissement de lignes.
"""

from battle_circle import Config, main

def demo_franchissement():
    """Configuration pour tester le système de franchissement des lignes."""
    print("=== DÉMO : Système de Franchissement de Lignes ===")
    
    # Configuration pour bien voir les franchissements
    Config.NOMBRE_PARTICIPANTS = 3
    Config.DENSITE_CIBLES_PAR_PIXEL = 0.1  # Moins de lignes pour mieux voir
    Config.NOMBRE_MIN_CIBLES = 60
    Config.TAILLE_CERCLE = 300
    
    # Mouvement modéré pour bien observer les franchissements
    Config.VITESSE_MOUVEMENT_JOUEUR = 1.8
    Config.VITESSE_MAX_JOUEUR = 100.0
    Config.AMPLITUDE_BRUIT_POSITION = 25.0
    
    # Lignes très fines
    Config.EPAISSEUR_LIGNE_NORMALE = 1
    Config.EPAISSEUR_LIGNE_CONTRE_ATTAQUE = 2
    
    # Score plus bas pour des parties plus courtes
    Config.CONDITION_VICTOIRE = 50
    
    print("Instructions :")
    print("- Les joueurs gagnent des points en FRANCHISSANT les lignes des autres")
    print("- Les lignes partent du centre vers le périmètre")
    print("- Plus fines et plus nombreuses pour un effet visuel spectaculaire")
    
    main()

if __name__ == "__main__":
    demo_franchissement()