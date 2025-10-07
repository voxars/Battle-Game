"""
Version de démonstration avec mouvement très dynamique pour tester les rebonds.
"""

from battle_circle import Config, main

def demo_mouvement_dynamique():
    """Configuration pour tester le mouvement dynamique et les rebonds."""
    print("=== DÉMO : Mouvement Dynamique avec Rebonds ===")
    
    # Paramètres pour un mouvement plus visible
    Config.NOMBRE_PARTICIPANTS = 4
    Config.VITESSE_MOUVEMENT_JOUEUR = 3.0
    Config.VITESSE_MAX_JOUEUR = 200.0
    Config.COEFFICIENT_REBOND = 0.9  # Rebonds plus élastiques
    Config.FORCE_REPULSION_JOUEURS = 800.0  # Plus de répulsion
    Config.AMPLITUDE_BRUIT_POSITION = 50.0  # Forces de bruit plus importantes
    Config.RAYON_JOUEUR = 12.0  # Joueurs plus gros pour voir les collisions
    
    # Cercle plus petit pour plus d'interactions
    Config.TAILLE_CERCLE = 280
    
    # Vitesse de jeu plus rapide
    Config.VITESSE_JEU = 1.5
    Config.CONDITION_VICTOIRE = 150
    
    main()

if __name__ == "__main__":
    demo_mouvement_dynamique()