# Système de Timer - Battle Game

## Vue d'ensemble
Le jeu dispose maintenant d'un système de timer configurable qui permet de limiter la durée des parties. Quand le temps expire, le joueur avec le score le plus élevé remporte automatiquement la partie.

## Configuration

### Paramètre principal
- `DUREE_PARTIE` : Durée de la partie en secondes (défaut : 120 secondes = 2 minutes)

```python
# Dans la classe Config
DUREE_PARTIE: int = 120  # 2 minutes par défaut
```

## Fonctionnalités

### Affichage du timer
- **Position** : Centre de l'écran, sous le titre
- **Format** : MM:SS (minutes:secondes)
- **Couleurs** :
  - Blanc : Plus de 30 secondes restantes
  - Rouge : Moins de 30 secondes restantes (alerte)
  - Jaune : "TEMPS ÉCOULÉ" quand la partie est terminée

### Conditions de victoire
Le jeu peut se terminer de deux façons :
1. **Par score** : Un joueur atteint la condition de victoire (paramètre `CONDITION_VICTOIRE`)
2. **Par temps** : Le timer expire, le joueur avec le score le plus élevé gagne

### Logique du timer
- Le timer commence au lancement du jeu
- Décompte en temps réel (60 FPS)
- Quand il atteint 0, la méthode `determine_winner_by_time()` est appelée
- Le jeu continue à fonctionner après l'expiration pour permettre l'affichage du résultat

## Implémentation technique

### Variables de classe BattleGame
```python
self.game_start_time = time.time()      # Timestamp de début
self.remaining_time = Config.DUREE_PARTIE  # Temps restant
self.game_ended = False                 # État de fin de partie
self.winner_by_time = None             # Gagnant par temps (si applicable)
```

### Mise à jour du timer
```python
def update(self):
    # Mise à jour du timer
    if not self.game_ended:
        self.remaining_time = Config.DUREE_PARTIE - (current_time - self.game_start_time)
        if self.remaining_time <= 0:
            self.remaining_time = 0
            self.game_ended = True
            self.determine_winner_by_time()
```

### Détermination du gagnant
```python
def determine_winner_by_time(self):
    # Trouver le joueur avec le score le plus élevé
    active_players = [p for p in self.players.values() if not p.is_eliminated]
    if active_players:
        winner = max(active_players, key=lambda p: p.score)
        self.winner_by_time = winner.id
        print(f"Temps écoulé ! Joueur {winner.id + 1} remporte la partie avec {winner.score} points !")
```

## Exemples d'utilisation

### Configuration standard (2 minutes)
```python
# Utilisation par défaut - pas de modification nécessaire
game = BattleGame()
game.run()
```

### Configuration courte pour tests (30 secondes)
```python
# Modifier la configuration avant de créer le jeu
Config.DUREE_PARTIE = 30
game = BattleGame()
game.run()
```

### Configuration longue (5 minutes)
```python
Config.DUREE_PARTIE = 300  # 5 minutes
game = BattleGame()
game.run()
```

## Fichiers de démonstration

### demo_timer.py
Démonstration avec un timer de 30 secondes pour tests rapides :
- 2 joueurs seulement
- Condition de victoire réduite (50 points)
- Timer court pour observer rapidement le comportement

```bash
python demo_timer.py
```

## Intégration avec les autres systèmes

### Système d'élimination
- Les joueurs éliminés ne sont pas considérés pour la victoire par temps
- Seuls les joueurs actifs (non éliminés) peuvent gagner par temps

### Système de score
- Le score continue d'évoluer même après l'expiration du timer
- La détermination du gagnant se fait au moment exact de l'expiration
- Égalité : en cas de scores identiques, le premier joueur trouvé gagne (ordre de création)

### Interface utilisateur
- L'UI se met à jour chaque seconde pour afficher le timer
- Le timer reste affiché même après expiration
- Message de victoire affiché dans la console

## Notes techniques

### Performance
- Mise à jour UI optimisée : recalcul seulement si nécessaire ou toutes les secondes
- Timer basé sur `time.time()` pour précision en temps réel
- Pas d'impact sur les performances de jeu (60 FPS maintenu)

### Robustesse
- Gestion des cas d'égalité de score
- Prise en compte des joueurs éliminés
- Continues après expiration pour permettre l'observation
- Message clair en console pour indiquer la fin de partie