"""
Démonstrations de différentes configurations pour la Bataille de Lignes sur Cercle.
Modifiez les paramètres ci-dessous et relancez le script pour tester différents modes.
"""

# Import de la configuration depuis le script principal
from battle_circle import Config, main

def demo_battle_rapide():
    """Configuration pour une bataille rapide et intense."""
    print("=== DÉMO : Bataille Rapide ===")
    Config.NOMBRE_PARTICIPANTS = 4
    Config.CONDITION_VICTOIRE = 100
    Config.VITESSE_JEU = 2.0
    Config.TAILLE_CERCLE = 300
    Config.MODE_BATAILLE = "Interaction"
    Config.VITESSE_MOUVEMENT_JOUEUR = 1.0
    main()

def demo_bataille_lente():
    """Configuration pour une bataille stratégique lente."""
    print("=== DÉMO : Bataille Stratégique ===")
    Config.NOMBRE_PARTICIPANTS = 2
    Config.CONDITION_VICTOIRE = 300
    Config.VITESSE_JEU = 0.5
    Config.TAILLE_CERCLE = 400
    Config.MODE_BATAILLE = "Interaction"
    Config.VITESSE_MOUVEMENT_JOUEUR = 0.3
    main()

def demo_chaos_maximum():
    """Configuration pour un chaos maximum avec 5 joueurs."""
    print("=== DÉMO : Chaos Maximum ===")
    Config.NOMBRE_PARTICIPANTS = 5
    Config.CONDITION_VICTOIRE = 150
    Config.VITESSE_JEU = 1.5
    Config.TAILLE_CERCLE = 350
    Config.MODE_BATAILLE = "Interaction"
    Config.VITESSE_MOUVEMENT_JOUEUR = 0.8
    Config.AMPLITUDE_BRUIT_POSITION = 30.0
    main()

def demo_enregistrement_video():
    """Configuration optimale pour l'enregistrement vidéo."""
    print("=== DÉMO : Configuration Enregistrement Vidéo ===")
    Config.NOMBRE_PARTICIPANTS = 3
    Config.CONDITION_VICTOIRE = 250
    Config.VITESSE_JEU = 1.2
    Config.TAILLE_CERCLE = 350
    Config.MODE_BATAILLE = "Interaction"
    Config.VITESSE_MOUVEMENT_JOUEUR = 0.6
    Config.EPAISSEUR_LIGNE_NORMALE = 3
    Config.EPAISSEUR_LIGNE_CONTRE_ATTAQUE = 5
    main()

if __name__ == "__main__":
    print("Choisissez une démonstration :")
    print("1. Bataille Rapide")
    print("2. Bataille Stratégique")
    print("3. Chaos Maximum")
    print("4. Configuration Enregistrement Vidéo")
    print("5. Configuration par défaut")
    
    choice = input("Votre choix (1-5) : ").strip()
    
    if choice == "1":
        demo_battle_rapide()
    elif choice == "2":
        demo_bataille_lente()
    elif choice == "3":
        demo_chaos_maximum()
    elif choice == "4":
        demo_enregistrement_video()
    elif choice == "5":
        main()
    else:
        print("Choix invalide, lancement de la configuration par défaut.")
        main()