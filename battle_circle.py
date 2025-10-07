"""
Bataille de Lignes sur Cercle - Application Python
Une simulation en temps réel d'une bataille entre joueurs sur un cercle
avec interactions avancées et rendu optimisé pour l'enregistrement vidéo (9:16).

Auteur: GitHub Copilot
Date: 7 octobre 2025
"""

import pygame
import math
import random
import numpy as np
from typing import List, Tuple, Dict, Optional
import time


class Config:
    """Classe de configuration centralisée pour tous les paramètres du jeu."""
    
    # Paramètres de jeu modifiables
    NOMBRE_PARTICIPANTS: int = 3
    CONDITION_VICTOIRE: int = 200
    VITESSE_JEU: float = 1.0  # tentatives/frame
    TAILLE_CERCLE: int = 350
    MODE_BATAILLE: str = "Interaction"  # "Proximité", "Influence", "Interaction"
    
    # Paramètres d'affichage
    LARGEUR: int = 720
    HAUTEUR: int = 1280  # Ratio 9:16
    FPS: int = 60
    
    # Couleurs (RGB)
    COULEUR_FOND = (15, 15, 30)
    COULEUR_CERCLE = (80, 80, 120)
    COULEUR_CIBLE_LIBRE = (100, 100, 100)
    COULEUR_TEXTE = (255, 255, 255)
    COULEUR_CONTRE_ATTAQUE = (255, 255, 255)
    
    # Couleurs des joueurs
    COULEURS_JOUEURS = [
        (255, 100, 100),  # Rouge
        (100, 255, 100),  # Vert
        (100, 100, 255),  # Bleu
        (255, 255, 100),  # Jaune
        (255, 100, 255),  # Magenta
    ]
    
    # Paramètres de gameplay avancés
    REDUCTION_PUISSANCE_DUREE: int = 6  # frames
    REDUCTION_PUISSANCE_VALEUR: float = 1.0
    ZONE_INTERFERENCE_ANGLE: float = 30.0  # degrés
    PROBABILITE_INTERFERENCE: float = 0.25
    DUREE_CLIGNOTEMENT: int = 5  # frames
    EPAISSEUR_LIGNE_NORMALE: int = 2
    EPAISSEUR_LIGNE_CONTRE_ATTAQUE: int = 4
    
    # Paramètres de mouvement
    VITESSE_MOUVEMENT_JOUEUR: float = 2.0
    AMPLITUDE_BRUIT_POSITION: float = 20.0
    VITESSE_MAX_JOUEUR: float = 150.0  # pixels/seconde
    RAYON_JOUEUR: float = 8.0
    COEFFICIENT_REBOND: float = 0.8
    FORCE_REPULSION_JOUEURS: float = 500.0
    
    @classmethod
    def get_center_x(cls) -> float:
        """Retourne le centre X de l'écran."""
        return cls.LARGEUR // 2
    
    @classmethod
    def get_center_y(cls) -> float:
        """Retourne le centre Y de l'écran (légèrement décalé vers le bas)."""
        return cls.HAUTEUR // 2 + 50
    
    @classmethod
    def get_ui_area_height(cls) -> float:
        """Retourne la hauteur de la zone d'interface utilisateur (tiers supérieur)."""
        return cls.HAUTEUR // 3


class SimplexNoise:
    """Implémentation simple du bruit de Perlin pour le mouvement des joueurs."""
    
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
        
        # Génération de la table de permutation
        self.perm = list(range(256))
        random.shuffle(self.perm)
        self.perm += self.perm  # Doubler pour éviter les débordements
    
    def fade(self, t: float) -> float:
        """Fonction de lissage."""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def lerp(self, a: float, b: float, t: float) -> float:
        """Interpolation linéaire."""
        return a + t * (b - a)
    
    def grad(self, hash_val: int, x: float, y: float) -> float:
        """Calcul du gradient."""
        h = hash_val & 15
        u = x if h < 8 else y
        v = y if h < 4 else (x if h == 12 or h == 14 else 0)
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)
    
    def noise(self, x: float, y: float) -> float:
        """Génère le bruit de Perlin en 2D."""
        # Coordonnées de la cellule
        X = int(x) & 255
        Y = int(y) & 255
        
        # Position relative dans la cellule
        x -= int(x)
        y -= int(y)
        
        # Courbes de lissage
        u = self.fade(x)
        v = self.fade(y)
        
        # Hachage des coordonnées des 4 coins de la cellule
        A = self.perm[X] + Y
        AA = self.perm[A]
        AB = self.perm[A + 1]
        B = self.perm[X + 1] + Y
        BA = self.perm[B]
        BB = self.perm[B + 1]
        
        # Interpolation
        res = self.lerp(
            self.lerp(self.grad(self.perm[AA], x, y),
                     self.grad(self.perm[BA], x - 1, y), u),
            self.lerp(self.grad(self.perm[AB], x, y - 1),
                     self.grad(self.perm[BB], x - 1, y - 1), u), v)
        
        return res


# Instance globale du générateur de bruit
noise_generator = SimplexNoise()


class Player:
    """Classe représentant un joueur dans la bataille de lignes."""
    
    def __init__(self, player_id: int, color: Tuple[int, int, int], center_x: float, center_y: float, circle_radius: float):
        """
        Initialise un joueur.
        
        Args:
            player_id: Identifiant unique du joueur
            color: Couleur RGB du joueur
            center_x, center_y: Centre du cercle de jeu
            circle_radius: Rayon du cercle de jeu
        """
        self.id = player_id
        self.color = color
        self.score = 0
        self.power_factor = 1.0  # Facteur de puissance normal
        
        # Positions et mouvement
        self.center_x = center_x
        self.center_y = center_y
        self.circle_radius = circle_radius
        
        # Position initiale aléatoire à l'intérieur du cercle
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(100, circle_radius * 0.7)  # Plus loin du centre
        self.x = center_x + distance * math.cos(angle)
        self.y = center_y + distance * math.sin(angle)
        
        # Vélocité pour le mouvement physique
        self.vx = random.uniform(-50, 50)  # Vitesse initiale aléatoire
        self.vy = random.uniform(-50, 50)
        
        # Base pour le bruit de Perlin (force d'attraction/répulsion)
        self.noise_offset_x = random.uniform(0, 1000)
        self.noise_offset_y = random.uniform(0, 1000)
        self.noise_time = 0.0
        
        # Rayon du joueur
        self.radius = Config.RAYON_JOUEUR
        
        # État de puissance réduite
        self.power_reduction_frames = 0
        self.was_power_reduced = False
        
        # Cibles possédées par ce joueur
        self.owned_targets: List[int] = []
        
    def update_position(self, time_factor: float, other_players: List['Player']):
        """Met à jour la position du joueur avec physique de rebond."""
        self.noise_time += time_factor * Config.VITESSE_MOUVEMENT_JOUEUR
        
        # Forces de bruit de Perlin (plus subtiles maintenant)
        noise_x = noise_generator.noise(
            self.noise_offset_x + self.noise_time,
            self.noise_offset_y
        )
        noise_y = noise_generator.noise(
            self.noise_offset_x,
            self.noise_offset_y + self.noise_time
        )
        
        # Appliquer les forces de bruit à la vélocité
        force_x = noise_x * Config.AMPLITUDE_BRUIT_POSITION
        force_y = noise_y * Config.AMPLITUDE_BRUIT_POSITION
        
        self.vx += force_x * time_factor
        self.vy += force_y * time_factor
        
        # Répulsion entre joueurs
        for other in other_players:
            if other.id != self.id:
                dx = self.x - other.x
                dy = self.y - other.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                min_distance = (self.radius + other.radius) * 2.5
                if distance < min_distance and distance > 0:
                    # Force de répulsion
                    force_magnitude = Config.FORCE_REPULSION_JOUEURS / (distance * distance)
                    force_x = (dx / distance) * force_magnitude
                    force_y = (dy / distance) * force_magnitude
                    
                    self.vx += force_x * time_factor
                    self.vy += force_y * time_factor
        
        # Limiter la vitesse maximum
        speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        if speed > Config.VITESSE_MAX_JOUEUR:
            factor = Config.VITESSE_MAX_JOUEUR / speed
            self.vx *= factor
            self.vy *= factor
        
        # Mettre à jour la position
        new_x = self.x + self.vx * time_factor
        new_y = self.y + self.vy * time_factor
        
        # Collision avec les parois du cercle
        dx = new_x - self.center_x
        dy = new_y - self.center_y
        distance_from_center = math.sqrt(dx * dx + dy * dy)
        
        max_distance = self.circle_radius - self.radius
        if distance_from_center > max_distance:
            # Rebond sur la paroi
            # Normaliser le vecteur de position
            nx = dx / distance_from_center
            ny = dy / distance_from_center
            
            # Projeter la vélocité sur la normale et la tangente
            dot_product = self.vx * nx + self.vy * ny
            
            # Réflexion de la vélocité avec coefficient de rebond
            self.vx = (self.vx - 2 * dot_product * nx) * Config.COEFFICIENT_REBOND
            self.vy = (self.vy - 2 * dot_product * ny) * Config.COEFFICIENT_REBOND
            
            # Repositionner le joueur à la limite
            factor = max_distance / distance_from_center
            new_x = self.center_x + dx * factor
            new_y = self.center_y + dy * factor
        
        self.x = new_x
        self.y = new_y
    
    def update_power_reduction(self):
        """Met à jour l'état de réduction de puissance."""
        if self.power_reduction_frames > 0:
            self.power_reduction_frames -= 1
            self.power_factor = 1.0 - Config.REDUCTION_PUISSANCE_VALEUR
            self.was_power_reduced = True
        else:
            self.power_factor = 1.0
            self.was_power_reduced = False
    
    def apply_power_reduction(self):
        """Applique une réduction de puissance temporaire."""
        self.power_reduction_frames = Config.REDUCTION_PUISSANCE_DUREE
    
    def get_effective_power(self) -> float:
        """Retourne la puissance effective du joueur."""
        return self.power_factor * Config.VITESSE_JEU
    
    def add_score(self, points: int):
        """Ajoute des points au score du joueur."""
        self.score += points
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Dessine le joueur sur l'écran."""
        # Taille dynamique selon l'état
        radius = int(self.radius) if not self.was_power_reduced else int(self.radius * 0.8)
        
        # Cercle principal du joueur
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            radius
        )
        
        # Contour plus foncé
        pygame.draw.circle(
            screen,
            (max(0, self.color[0] - 50), max(0, self.color[1] - 50), max(0, self.color[2] - 50)),
            (int(self.x), int(self.y)),
            radius,
            2
        )
        
        # Indicateur de vélocité (petite flèche)
        if abs(self.vx) > 10 or abs(self.vy) > 10:
            end_x = int(self.x + self.vx * 0.3)
            end_y = int(self.y + self.vy * 0.3)
            pygame.draw.line(
                screen,
                (255, 255, 255),
                (int(self.x), int(self.y)),
                (end_x, end_y),
                2
            )
        
        # Indicateur de puissance réduite
        if self.was_power_reduced:
            pygame.draw.circle(
                screen,
                (255, 100, 100),
                (int(self.x), int(self.y)),
                radius + 3,
                1
            )


class Target:
    """Classe représentant une cible sur le périmètre du cercle."""
    
    def __init__(self, target_id: int, angle: float, center_x: float, center_y: float, radius: float):
        """
        Initialise une cible.
        
        Args:
            target_id: Identifiant unique de la cible
            angle: Angle en radians sur le cercle
            center_x, center_y: Centre du cercle
            radius: Rayon du cercle
        """
        self.id = target_id
        self.angle = angle
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        
        # Position calculée
        self.x = center_x + radius * math.cos(angle)
        self.y = center_y + radius * math.sin(angle)
        
        # État
        self.owner_id: Optional[int] = None
        self.previous_owner_id: Optional[int] = None
        
        # Effets visuels de contre-attaque
        self.counter_attack_frames = 0
        self.is_blinking = False
    
    def set_owner(self, player_id: int):
        """Définit le propriétaire de la cible."""
        self.previous_owner_id = self.owner_id
        self.owner_id = player_id
        
        # Si la cible change de propriétaire, activer l'effet visuel
        if self.previous_owner_id is not None and self.previous_owner_id != player_id:
            self.counter_attack_frames = Config.DUREE_CLIGNOTEMENT
    
    def update_visual_effects(self):
        """Met à jour les effets visuels."""
        if self.counter_attack_frames > 0:
            self.counter_attack_frames -= 1
            self.is_blinking = True
        else:
            self.is_blinking = False
    
    def get_angle_degrees(self) -> float:
        """Retourne l'angle en degrés."""
        return math.degrees(self.angle) % 360
    
    def draw(self, screen: pygame.Surface, players: Dict[int, Player]):
        """Dessine la cible sur l'écran."""
        # Couleur de base
        if self.owner_id is None:
            color = Config.COULEUR_CIBLE_LIBRE
            radius = 4
        else:
            color = players[self.owner_id].color
            radius = 5
        
        # Effet de clignotement pour les contre-attaques
        if self.is_blinking and (pygame.time.get_ticks() // 100) % 2 == 0:
            color = Config.COULEUR_CONTRE_ATTAQUE
            radius += 1
        
        # Dessiner la cible
        pygame.draw.circle(
            screen,
            color,
            (int(self.x), int(self.y)),
            radius
        )
        
        # Contour
        pygame.draw.circle(
            screen,
            Config.COULEUR_TEXTE,
            (int(self.x), int(self.y)),
            radius,
            1
        )


class BattleGame:
    """Classe principale du jeu de bataille de lignes sur cercle."""
    
    def __init__(self):
        """Initialise le jeu et pygame."""
        pygame.init()
        pygame.font.init()
        
        # Configuration de la fenêtre
        self.screen = pygame.display.set_mode((Config.LARGEUR, Config.HAUTEUR))
        pygame.display.set_caption("Bataille de Lignes sur Cercle")
        
        # Configuration du framerate
        self.clock = pygame.time.Clock()
        
        # Police pour l'affichage du texte
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Variables de jeu
        self.running = True
        self.frame_count = 0
        self.last_fps_update = time.time()
        self.current_fps = 0
        
        # Centre du cercle
        self.center_x = Config.get_center_x()
        self.center_y = Config.get_center_y()
        
        # Initialisation des joueurs et cibles
        self.players: Dict[int, Player] = {}
        self.targets: Dict[int, Target] = {}
        self.game_time = 0.0
        
        # Optimisations de performance
        self.background_surface = None
        self.ui_surface = None
        self.ui_needs_update = True
        self.target_update_counter = 0  # Pour réduire la fréquence de mise à jour
        
        self.init_players()
        self.init_targets()
        self.create_background_surface()
        
        print("Jeu initialisé avec succès !")
    
    def create_background_surface(self):
        """Crée une surface d'arrière-plan précalculée pour optimiser les performances."""
        self.background_surface = pygame.Surface((Config.LARGEUR, Config.HAUTEUR))
        self.background_surface.fill(Config.COULEUR_FOND)
        
        # Dessiner le cercle principal sur l'arrière-plan
        pygame.draw.circle(
            self.background_surface,
            Config.COULEUR_CERCLE,
            (int(self.center_x), int(self.center_y)),
            Config.TAILLE_CERCLE,
            2
        )
    
    def init_players(self):
        """Initialise les joueurs."""
        for i in range(Config.NOMBRE_PARTICIPANTS):
            color = Config.COULEURS_JOUEURS[i % len(Config.COULEURS_JOUEURS)]
            player = Player(i, color, self.center_x, self.center_y, Config.TAILLE_CERCLE)
            self.players[i] = player
    
    def init_targets(self):
        """Initialise les cibles sur le périmètre du cercle."""
        # Nombre de cibles proportionnel à la taille du cercle
        num_targets = max(20, Config.TAILLE_CERCLE // 15)
        
        for i in range(num_targets):
            angle = (2 * math.pi * i) / num_targets
            target = Target(i, angle, self.center_x, self.center_y, Config.TAILLE_CERCLE)
            self.targets[i] = target
    
    def get_closest_player_to_target(self, target: Target) -> Optional[int]:
        """Trouve le joueur le plus proche d'une cible donnée (optimisé)."""
        min_distance_sq = float('inf')  # Utiliser le carré de la distance pour éviter sqrt
        closest_player_id = None
        
        for player_id, player in self.players.items():
            # Calcul du carré de la distance (plus rapide)
            distance_sq = (player.x - target.x) ** 2 + (player.y - target.y) ** 2
            
            if distance_sq < min_distance_sq:
                min_distance_sq = distance_sq
                closest_player_id = player_id
        
        return closest_player_id
    
    def check_interference_zone(self, target: Target, new_owner_id: int) -> bool:
        """
        Vérifie si une cible est dans la zone d'interférence d'une cible récemment perdue.
        Retourne True si la cible doit être redistribuée à cause de l'interférence.
        """
        target_angle = target.get_angle_degrees()
        
        # Chercher les joueurs avec une réduction de puissance active
        for player_id, player in self.players.items():
            if player.was_power_reduced and player_id != new_owner_id:
                # Chercher les cibles récemment perdues par ce joueur
                for other_target in self.targets.values():
                    if (other_target.previous_owner_id == player_id and 
                        other_target.owner_id != player_id and
                        other_target.id != target.id):
                        
                        # Calculer la différence d'angle
                        other_angle = other_target.get_angle_degrees()
                        angle_diff = abs(target_angle - other_angle)
                        
                        # Gérer le cas où l'angle traverse 0°/360°
                        if angle_diff > 180:
                            angle_diff = 360 - angle_diff
                        
                        # Si dans la zone d'interférence, appliquer la probabilité
                        if angle_diff <= Config.ZONE_INTERFERENCE_ANGLE:
                            if random.random() < Config.PROBABILITE_INTERFERENCE:
                                return True
        
        return False
    
    def handle_player_collisions(self):
        """Gère les collisions directes entre joueurs."""
        players_list = list(self.players.values())
        
        for i in range(len(players_list)):
            for j in range(i + 1, len(players_list)):
                player1 = players_list[i]
                player2 = players_list[j]
                
                # Calculer la distance entre les joueurs
                dx = player2.x - player1.x
                dy = player2.y - player1.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                min_distance = player1.radius + player2.radius
                
                if distance < min_distance and distance > 0:
                    # Collision détectée - rebond élastique
                    
                    # Vecteur de collision normalisé
                    nx = dx / distance
                    ny = dy / distance
                    
                    # Vitesses relatives
                    dvx = player2.vx - player1.vx
                    dvy = player2.vy - player1.vy
                    
                    # Vitesse relative dans la direction de collision
                    dvn = dvx * nx + dvy * ny
                    
                    # Ne pas résoudre si les objets s'éloignent déjà
                    if dvn > 0:
                        continue
                    
                    # Coefficient de restitution (rebond)
                    e = Config.COEFFICIENT_REBOND
                    
                    # Impulsion de collision
                    impulse = 2 * dvn / 2  # masses égales
                    
                    # Mettre à jour les vitesses
                    player1.vx += impulse * nx * e
                    player1.vy += impulse * ny * e
                    player2.vx -= impulse * nx * e
                    player2.vy -= impulse * ny * e
                    
                    # Séparer les joueurs pour éviter l'interpénétration
                    overlap = min_distance - distance
                    separation = overlap / 2
                    
                    player1.x -= nx * separation
                    player1.y -= ny * separation
                    player2.x += nx * separation
                    player2.y += ny * separation
    
    def update_target_ownership(self):
        """Met à jour la propriété des cibles selon la logique du jeu."""
        for target in self.targets.values():
            closest_player_id = self.get_closest_player_to_target(target)
            
            if closest_player_id is not None:
                current_owner = target.owner_id
                
                # Si la cible change de propriétaire
                if current_owner != closest_player_id:
                    # Vérifier les zones d'interférence
                    if not self.check_interference_zone(target, closest_player_id):
                        # Appliquer la réduction de puissance à l'ancien propriétaire
                        if current_owner is not None:
                            self.players[current_owner].apply_power_reduction()
                        
                        # Changer de propriétaire
                        target.set_owner(closest_player_id)
                        
                        # Ajouter des points au nouveau propriétaire
                        self.players[closest_player_id].add_score(1)
                        
                        # Forcer la mise à jour de l'UI
                        self.ui_needs_update = True
    
    def handle_events(self):
        """Gère les événements pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update(self):
        """Met à jour la logique du jeu."""
        self.frame_count += 1
        self.game_time += 1.0 / Config.FPS
        
        # Calcul du FPS réel
        current_time = time.time()
        if current_time - self.last_fps_update >= 1.0:
            self.current_fps = self.frame_count
            self.frame_count = 0
            self.last_fps_update = current_time
        
        # Mise à jour des joueurs avec interactions
        players_list = list(self.players.values())
        for player in players_list:
            player.update_position(1.0 / Config.FPS, players_list)
            player.update_power_reduction()
        
        # Gestion des collisions directes entre joueurs
        self.handle_player_collisions()
        
        # Mise à jour des cibles
        for target in self.targets.values():
            target.update_visual_effects()
        
        # Mise à jour de la propriété des cibles (moins fréquente pour les performances)
        self.target_update_counter += 1
        if self.target_update_counter >= 2:  # Mise à jour tous les 2 frames
            self.update_target_ownership()
            self.target_update_counter = 0
        
        # Vérifier la condition de victoire
        self.check_victory_condition()
    
    def check_victory_condition(self):
        """Vérifie si un joueur a atteint la condition de victoire."""
        for player in self.players.values():
            if player.score >= Config.CONDITION_VICTOIRE:
                print(f"Joueur {player.id} remporte la partie avec {player.score} points !")
                self.ui_needs_update = True  # Forcer la mise à jour de l'UI
                # Pour l'instant, on continue le jeu
                # self.running = False
    
    def draw_background(self):
        """Dessine l'arrière-plan optimisé."""
        # Utiliser la surface précalculée
        self.screen.blit(self.background_surface, (0, 0))
    
    def create_ui_surface(self):
        """Crée la surface d'UI mise en cache."""
        ui_height = Config.get_ui_area_height()
        self.ui_surface = pygame.Surface((Config.LARGEUR, ui_height))
        
        # Zone d'interface
        self.ui_surface.fill((20, 20, 40))
        
        # Ligne de séparation
        pygame.draw.line(
            self.ui_surface,
            Config.COULEUR_CERCLE,
            (0, ui_height - 2),
            (Config.LARGEUR, ui_height - 2),
            2
        )
        
        # Titre
        title_text = self.font_large.render("Bataille de Lignes", True, Config.COULEUR_TEXTE)
        title_rect = title_text.get_rect(center=(Config.LARGEUR // 2, 30))
        self.ui_surface.blit(title_text, title_rect)
        
        # Scores des joueurs
        score_y = 70
        for i, (player_id, player) in enumerate(self.players.items()):
            # Couleur du joueur
            color_rect = pygame.Rect(20, score_y + i * 35, 20, 20)
            pygame.draw.rect(self.ui_surface, player.color, color_rect)
            pygame.draw.rect(self.ui_surface, Config.COULEUR_TEXTE, color_rect, 1)
            
            # Score et informations
            score_text = f"Joueur {player_id + 1}: {player.score}"
            if player.was_power_reduced:
                score_text += " [AFFAIBLI]"
            
            power_text = f"Puissance: {player.power_factor:.1f}"
            
            score_surface = self.font_medium.render(score_text, True, Config.COULEUR_TEXTE)
            power_surface = self.font_small.render(power_text, True, Config.COULEUR_TEXTE)
            
            self.ui_surface.blit(score_surface, (50, score_y + i * 35))
            self.ui_surface.blit(power_surface, (50, score_y + i * 35 + 18))
        
        # Informations de configuration
        config_y = ui_height - 80
        config_texts = [
            f"Objectif: {Config.CONDITION_VICTOIRE} | Mode: {Config.MODE_BATAILLE}",
            f"FPS: {self.current_fps} | Cibles: {len(self.targets)}"
        ]
        
        for i, text in enumerate(config_texts):
            rendered_text = self.font_small.render(text, True, Config.COULEUR_TEXTE)
            self.ui_surface.blit(rendered_text, (20, config_y + i * 20))
    
    def draw_ui(self):
        """Dessine l'interface utilisateur optimisée."""
        # Recréer l'UI seulement si nécessaire
        if self.ui_needs_update or self.ui_surface is None:
            self.create_ui_surface()
            self.ui_needs_update = False
        
        # Dessiner la surface UI mise en cache
        self.screen.blit(self.ui_surface, (0, 0))
    
    def draw(self):
        """Dessine tous les éléments du jeu."""
        self.draw_background()
        
        # Dessiner les lignes entre joueurs et leurs cibles
        self.draw_connections()
        
        # Dessiner les cibles
        for target in self.targets.values():
            target.draw(self.screen, self.players)
        
        # Dessiner les joueurs
        for player in self.players.values():
            player.draw(self.screen, self.font_small)
        
        # Dessiner l'interface utilisateur par-dessus
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_connections(self):
        """Dessine les lignes de connexion entre joueurs et leurs cibles."""
        for target in self.targets.values():
            if target.owner_id is not None:
                player = self.players[target.owner_id]
                
                # Épaisseur de ligne selon l'état
                thickness = Config.EPAISSEUR_LIGNE_NORMALE
                if target.is_blinking:
                    thickness = Config.EPAISSEUR_LIGNE_CONTRE_ATTAQUE
                
                # Couleur de la ligne
                color = player.color
                if target.is_blinking and (pygame.time.get_ticks() // 100) % 2 == 0:
                    color = Config.COULEUR_CONTRE_ATTAQUE
                
                # Dessiner la ligne
                pygame.draw.line(
                    self.screen,
                    color,
                    (int(player.x), int(player.y)),
                    (int(target.x), int(target.y)),
                    thickness
                )
    
    def run(self):
        """Boucle principale du jeu."""
        print("Démarrage de la boucle de jeu...")
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            
            # Maintenir 60 FPS
            self.clock.tick(Config.FPS)
        
        pygame.quit()
        print("Jeu terminé.")


def main():
    """Point d'entrée principal de l'application."""
    print("=== Bataille de Lignes sur Cercle ===")
    print(f"Configuration actuelle :")
    print(f"- Participants : {Config.NOMBRE_PARTICIPANTS}")
    print(f"- Condition de victoire : {Config.CONDITION_VICTOIRE}")
    print(f"- Vitesse de jeu : {Config.VITESSE_JEU}")
    print(f"- Taille du cercle : {Config.TAILLE_CERCLE}")
    print(f"- Mode de bataille : {Config.MODE_BATAILLE}")
    print(f"- Résolution : {Config.LARGEUR}x{Config.HAUTEUR}")
    print(f"- FPS cible : {Config.FPS}")
    print()
    
    try:
        game = BattleGame()
        game.run()
    except Exception as e:
        print(f"Erreur lors de l'exécution du jeu : {e}")
        pygame.quit()


if __name__ == "__main__":
    main()