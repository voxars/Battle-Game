# Bataille de Lignes sur Cercle

Une simulation en temps réel d'une bataille entre joueurs sur un cercle avec interactions avancées, optimisée pour l'enregistrement vidéo en format vertical (9:16).

## Fonctionnalités

- **Rendu fluide 60 FPS** avec optimisations de performance
- **Format vertical 9:16** (720x1280) idéal pour l'enregistrement vidéo
- **Interactions avancées** entre joueurs avec système de contre-attaque
- **Mouvement physique dynamique** avec rebonds sur les parois et entre joueurs
- **Système de collision** avec rebonds élastiques et répulsion
- **Système de réduction de puissance** temporaire
- **Zones d'interférence** avec probabilités de redistribution des cibles
- **Effets visuels** pour les contre-attaques (clignotement et épaisseur variable)

## Installation

1. Assurez-vous d'avoir Python 3.7+ installé
2. Installez les dépendances :
   ```bash
   pip install pygame numpy
   ```

## Utilisation

### Lancement simple
```bash
python battle_circle.py
```

### Configurations de démonstration
```bash
python demo_configs.py

# Version ultra-dynamique pour tester les rebonds
python demo_dynamique.py
```

## Configuration

Tous les paramètres sont modifiables au début du fichier `battle_circle.py` dans la classe `Config` :

### Paramètres de jeu
- `NOMBRE_PARTICIPANTS` : 2 à 5 joueurs (défaut: 3)
- `CONDITION_VICTOIRE` : Points nécessaires pour gagner (défaut: 200)
- `VITESSE_JEU` : Multiplicateur de vitesse (défaut: 1.0)
- `TAILLE_CERCLE` : Rayon du cercle de jeu (défaut: 350)
- `MODE_BATAILLE` : "Interaction", "Proximité", "Influence" (défaut: "Interaction")

### Paramètres d'affichage
- `LARGEUR` x `HAUTEUR` : Résolution (défaut: 720x1280)
- `FPS` : Images par seconde (défaut: 60)
- Couleurs personnalisables pour chaque élément

### Paramètres de gameplay avancés
- `REDUCTION_PUISSANCE_DUREE` : Durée de l'affaiblissement (défaut: 6 frames)
- `ZONE_INTERFERENCE_ANGLE` : Angle d'interférence (défaut: 30°)
- `PROBABILITE_INTERFERENCE` : Probabilité de redistribution (défaut: 25%)
- `VITESSE_MOUVEMENT_JOUEUR` : Force du bruit de Perlin (défaut: 2.0)
- `VITESSE_MAX_JOUEUR` : Vitesse maximum en pixels/seconde (défaut: 150.0)
- `COEFFICIENT_REBOND` : Élasticité des rebonds (défaut: 0.8)
- `FORCE_REPULSION_JOUEURS` : Force de répulsion entre joueurs (défaut: 500.0)
- `RAYON_JOUEUR` : Taille des joueurs en pixels (défaut: 8.0)

## Logique de jeu

### Mode "Interaction" (recommandé)
1. **Attribution par proximité** : Chaque cible appartient au joueur le plus proche
2. **Mouvement physique dynamique** : 
   - Les joueurs ont une vélocité et rebondissent sur les parois du cercle
   - Collisions élastiques entre joueurs avec répulsion
   - Forces de bruit de Perlin pour un mouvement organique
   - Indicateurs visuels de direction et vitesse
3. **Système de contre-attaque** :
   - Quand un joueur perd une cible, il subit une réduction de puissance (-1.0) pendant 6 frames
   - Les cibles à moins de 30° de la cible perdue ont 25% de chance d'être redistribuées
   - Les lignes de contre-attaque sont plus épaisses et clignotent en blanc

### Optimisations de performance
- **Surfaces mises en cache** pour l'arrière-plan et l'interface utilisateur
- **Calculs de distance optimisés** (carré de la distance)
- **Mise à jour conditionnelle** des cibles (tous les 2 frames)
- **Rendu par lots** pour les éléments similaires

## Contrôles

- **Échap** : Quitter l'application
- **Fermer la fenêtre** : Alt+F4 ou clic sur X

## Configurations prédéfinies

Le fichier `demo_configs.py` propose plusieurs configurations :

1. **Bataille Rapide** : 4 joueurs, objectif 100, vitesse x2
2. **Bataille Stratégique** : 2 joueurs, objectif 300, vitesse x0.5
3. **Chaos Maximum** : 5 joueurs, mouvement amplifié
4. **Enregistrement Vidéo** : Configuration optimale pour capture

## Structure du code

- `Config` : Classe de configuration centralisée
- `SimplexNoise` : Générateur de bruit de Perlin personnalisé
- `Player` : Classe joueur avec mouvement et états
- `Target` : Classe cible avec effets visuels
- `BattleGame` : Classe principale du jeu

## Enregistrement vidéo

L'application est optimisée pour l'enregistrement vidéo :
- Format vertical 9:16 parfait pour les réseaux sociaux
- 60 FPS constants pour un rendu fluide
- Interface claire dans le tiers supérieur
- Contraste élevé pour une bonne visibilité

Utilisez des logiciels comme OBS Studio pour capturer la fenêtre de jeu.

## Personnalisation

Vous pouvez facilement :
- Modifier les couleurs dans `Config.COULEURS_JOUEURS`
- Ajuster les paramètres de gameplay
- Changer la résolution (en gardant le ratio 9:16)
- Ajouter de nouveaux modes de bataille

## Licence

Projet développé par GitHub Copilot - Libre d'utilisation pour l'éducation et la démonstration.