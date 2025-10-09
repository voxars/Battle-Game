# 🎮 Bataille de Lignes sur Cercle - v1.0

Une simulation en temps réel spectaculaire d'une bataille entre joueurs sur un cercle avec des interactions avancées, une physique réaliste et des effets audio immersifs. Optimisée pour l'enregistrement vidéo en format vertical (9:16).

## ✨ Fonctionnalités Principales

### 🎯 Gameplay Avancé
- **Interface de configuration interactive** avec personnalisation complète des parties
- **Physique réaliste** avec collisions divergentes et rebonds naturels
- **Système d'élimination** progressif basé sur la possession de lignes
- **Accélération progressive** toutes les 20 secondes pour intensifier l'action
- **Timer de partie** avec compte à rebours visuel
- **Système de scoring** en temps réel avec classement dynamique

### 🎵 Système Audio Immersif
- **Sons synthétiques** générés en temps réel (aucun fichier externe)
- **Collision avec bords** : Son métallique grave (300ms)
- **Collision entre joueurs** : Son cristallin aigu (200ms) 
- **Vol de ligne** : Son mélodieux adouci (300ms)
- **Élimination** : Son dramatique avec descente de fréquence (1.5s)
- **Alerte fin de jeu** : Son d'urgence prioritaire pour les 3 dernières secondes

### 🎨 Rendu Visuel Optimisé
- **60 FPS constants** avec optimisations de performance avancées
- **Format vertical 9:16** (720x1280) parfait pour les réseaux sociaux
- **Animations de confettis** lors des éliminations
- **Interface utilisateur moderne** avec scores affichés près de l'action
- **Effets visuels dynamiques** : lignes pulsantes, couleurs réactives
- **Indicateurs d'état** : vitesse, direction, puissance des joueurs

## 🚀 Installation

### Prérequis
- **Python 3.13+** (recommandé) ou Python 3.7+
- **Windows, macOS, ou Linux**

### Installation des dépendances
```bash
pip install pygame==2.6.1 numpy
```

### Vérification de l'installation
```bash
python -c "import pygame, numpy; print('✅ Toutes les dépendances sont installées!')"
```

## 🎮 Utilisation

### Lancement du jeu
```bash
python battle_circle.py
```

Le jeu démarre automatiquement avec l'interface de configuration où vous pouvez :
- **Choisir le nombre de joueurs** (2-4)
- **Définir la durée de partie** (30s à 5 minutes)
- **Personnaliser les noms** et couleurs des joueurs
- **Configurer les paramètres avancés**

## ⚙️ Configuration

### Interface de Configuration Intégrée
Le jeu propose une interface graphique complète pour configurer chaque partie :

#### 🎯 Paramètres de Base
- **Nombre de joueurs** : 2 à 6 joueurs
- **Durée de partie** : 30 secondes à 5 minutes
- **Noms personnalisés** pour chaque joueur
- **Couleurs personnalisées** avec sélecteur intuitif

#### 🔧 Paramètres Avancés (Classe Config)
```python
# Paramètres de jeu
NOMBRE_PARTICIPANTS = 6          # Nombre maximum de joueurs
DUREE_PARTIE = 120              # Durée par défaut (secondes)
TAILLE_CERCLE = 350             # Rayon du cercle de bataille

# Paramètres d'affichage
LARGEUR, HAUTEUR = 720, 1280    # Résolution 9:16
FPS = 60                        # Images par seconde

# Paramètres de physique
COEFFICIENT_REBOND = 0.9        # Élasticité des rebonds
VITESSE_INITIALE = 150.0        # Vitesse de départ des joueurs
VITESSE_MIN_GARANTIE = 120.0    # Vitesse minimum garantie

# Paramètres audio
VOLUME_COLLISIONS = 0.4-0.5     # Volume des collisions
VOLUME_ELIMINATION = 0.6        # Volume des éliminations
VOLUME_ALERTE_FIN = 1.0         # Volume de l'alerte (prioritaire)
```

## 🎯 Règles du Jeu

### Principe de Base
- **Objectif** : Posséder le maximum de lignes sur le cercle
- **Mécanisme** : Les joueurs se déplacent et capturent les lignes par collision ou franchissement
- **Victoire** : Le joueur avec le plus de lignes à la fin du timer gagne

### Système de Physique Avancé
1. **Mouvement Naturel** :
   - Bruit de Perlin individuel pour chaque joueur (mouvement organique)
   - Vitesse initiale de 150 pixels/seconde avec garantie minimum de 120
   - Accélération progressive (+15%) toutes les 20 secondes

2. **Collisions Intelligentes** :
   - **Bords du cercle** : Rebond vers le centre avec variation ±20°
   - **Entre joueurs** : Rebonds divergents avec angle minimum de 90°
   - **Effet d'énergie** : Les collisions augmentent la vitesse (+30-40%)

3. **Système d'Élimination** :
   - Un joueur est éliminé quand il n'a plus aucune ligne
   - Animation de confettis lors des éliminations
   - Réduction progressive du nombre de joueurs actifs

### Mécaniques de Capture
1. **Collision directe** : Toucher une ligne avec son cercle de joueur
2. **Franchissement** : Traverser une ligne appartenant à un adversaire
3. **Vol automatique** : Les lignes changent de propriétaire instantanément

### Système de Progression
- **Timer visible** avec compte à rebours
- **Scores en temps réel** affichés près du cercle
- **Alerte sonore** dramatique aux 3 dernières secondes
- **Classement final** avec animation de victoire

## 🎮 Contrôles

### Interface de Configuration
- **Clic souris** : Naviguer dans les menus et options
- **Champs de texte** : Saisie directe pour noms et durées
- **Boutons** : Validation et navigation entre les écrans

### Pendant le Jeu
- **Le jeu est entièrement automatique** - aucune intervention requise
- **Échap** : Quitter l'application
- **Alt+F4** ou **X** : Fermer la fenêtre

## 📊 Modes de Jeu Recommandés

### 🏃‍♂️ Bataille Express (30-60s)
- **2-3 joueurs** pour action intense
- **Idéal pour** : Démonstrations rapides, tests

### ⚔️ Bataille Standard (2-3 minutes)  
- **3-4 joueurs** pour équilibre optimal
- **Idéal pour** : Parties complètes, enregistrements

### 🎥 Mode Enregistrement (1-2 minutes)
- **4-6 joueurs** pour maximum de spectacle
- **Noms courts** pour meilleure lisibilité
- **Couleurs contrastées** pour distinction claire

## 🏗️ Architecture Technique

### Structure du Code
```
battle_circle.py (2000+ lignes)
├── SoundManager          # Système audio synthétique
├── Confetti             # Animations de particules
├── Config               # Configuration centralisée
├── SimplexNoise         # Générateur de bruit de Perlin
├── Player               # Logique des joueurs
├── Target               # Système de lignes/cibles
├── GameSetupUI          # Interface de configuration
└── BattleCircleGame     # Moteur principal
```

### Optimisations de Performance
- **Surfaces mises en cache** : Interface et arrière-plan
- **Calculs vectoriels optimisés** avec NumPy
- **Rendu conditionnel** : Mise à jour intelligente
- **Gestion mémoire** : Réutilisation des objets

## 🎥 Enregistrement Vidéo

### Configuration Optimale
- **Format 9:16 (720x1280)** : Parfait pour TikTok, Instagram, YouTube Shorts
- **60 FPS garantis** : Rendu ultra-fluide
- **Interface épurée** : Scores proches de l'action
- **Contraste élevé** : Excellente visibilité

### Logiciels Recommandés
- **OBS Studio** (gratuit) : Capture d'écran professionnelle
- **Bandicam** : Enregistrement haute qualité
- **NVIDIA ShadowPlay** : Pour cartes graphiques NVIDIA

### Conseils d'Enregistrement
1. **Réduire les autres applications** pour maximiser les performances
2. **Utiliser des noms courts** pour les joueurs (4-6 caractères)
3. **Choisir des couleurs contrastées** pour une meilleure distinction
4. **Durée optimale** : 1-2 minutes pour maintenir l'attention

## 🎨 Personnalisation

### Modification des Couleurs
```python
# Dans la classe Config
COULEURS_JOUEURS = [
    (255, 100, 100),  # Rouge
    (100, 150, 255),  # Bleu
    (100, 255, 100),  # Vert
    (255, 255, 100)   # Jaune
]
```

### Ajustement de la Physique
```python
# Vitesses et forces
VITESSE_INITIALE = 150.0        # Vitesse de départ
COEFFICIENT_REBOND = 0.9        # Élasticité (0.1 = mou, 1.0 = parfait)
FORCE_REPULSION = 500.0         # Force entre joueurs
```

### Personnalisation Audio
```python
# Dans SoundManager, modifier les fréquences et durées
start_freq = 400    # Fréquence de base
duration = 0.3      # Durée du son
volume = 0.5        # Volume (0.0 à 1.0)
```

## 🚀 Version 1.0 - Fonctionnalités Complètes

✅ **Interface de configuration graphique**  
✅ **Système audio synthétique complet**  
✅ **Physique de collision avancée**  
✅ **Système d'élimination et timer**  
✅ **Animations et effets visuels**  
✅ **Optimisations de performance**  
✅ **Support multi-joueurs (2-6)**  
✅ **Format vidéo 9:16 optimisé**  

## 📄 Licence

**Bataille de Lignes sur Cercle v1.0**  
Développé par **GitHub Copilot** - Octobre 2025  

Libre d'utilisation pour l'éducation, la démonstration et le divertissement.  
Crédit apprécié mais non obligatoire.

---

## 📋 Changelog v1.0

### � Version 1.0 - Release Complète (7 Octobre 2025)
- ✅ **Interface de configuration complète** avec UI graphique
- ✅ **Système audio synthétique** avec 5 types de sons différents
- ✅ **Physique de collision avancée** avec rebonds divergents à 90°
- ✅ **Système d'élimination** avec animations de confettis
- ✅ **Timer de partie** avec alerte de fin dramatique
- ✅ **Interface utilisateur optimisée** avec scores près du cercle
- ✅ **Accélération progressive** pour maintenir l'intensité
- ✅ **Optimisations de performance** pour 60 FPS garantis
- ✅ **Support multi-joueurs** complet (2-6 joueurs)
- ✅ **Documentation complète** avec guide d'utilisation

### 🔧 Améliorations Techniques
- Générateur de sons synthétiques sans dépendances externes
- Physique de collision naturelle et réaliste  
- Système de priorité audio pour l'alerte de fin
- Interface de scoring dynamique repositionnée
- Gestion intelligente de la vitesse et des éliminations

---

🎮 **La v1.0 est prête ! Lancez `python battle_circle.py` et que le meilleur gagne !** 🎮