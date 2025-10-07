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
    EPAISSEUR_LIGNE_NORMALE: int = 1  # Lignes plus fines
    EPAISSEUR_LIGNE_CONTRE_ATTAQUE: int = 2
    
    # Paramètres de mouvement
    VITESSE_MOUVEMENT_JOUEUR: float = 4.0  # Vitesse augmentée
    AMPLITUDE_BRUIT_POSITION: float = 8.0  # Bruit réduit pour maintenir la direction
    VITESSE_MAX_JOUEUR: float = 200.0  # Vitesse max augmentée
    RAYON_JOUEUR: float = 20.0  # Taille augmentée pour plus de visibilité
    COEFFICIENT_REBOND: float = 0.9  # Rebond plus énergique
    FORCE_REPULSION_JOUEURS: float = 500.0
    
    # Paramètres visuels
    DENSITE_CIBLES_PAR_PIXEL: float = 0.06  # Une cible tous les 16-17 pixels (environ 130 cibles)
    NOMBRE_MIN_CIBLES: int = 40
    
    @classmethod
    def get_center_x(cls) -> float:
        """Retourne le centre X de l'écran."""
        return cls.LARGEUR // 2
    
    @classmethod
    def get_center_y(cls) -> float:
        """Retourne le centre Y de l'écran pour voir l'ensemble du cercle."""
        # Calculer la position pour que le cercle entier soit visible
        # En tenant compte de l'espace UI réduit en haut
        ui_height = cls.get_ui_area_height()
        available_height = cls.HAUTEUR - ui_height
        return ui_height + available_height // 2
    
    @classmethod
    def get_ui_area_height(cls) -> float:
        """Retourne la hauteur réduite de la zone d'interface utilisateur."""
        return 200  # Zone UI plus compacte au lieu de HAUTEUR // 3 (427px)


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
        
        # Position initiale sur le périmètre du cercle, calculée selon l'ID du joueur
        # Les joueurs sont espacés de manière égale sur le cercle
        angle = (2 * math.pi * player_id) / Config.NOMBRE_PARTICIPANTS
        distance = circle_radius * 0.85  # Près du bord mais pas sur le périmètre exact
        self.x = center_x + distance * math.cos(angle)
        self.y = center_y + distance * math.sin(angle)
        
        # Vélocité initiale dirigée vers le centre du cercle
        # Calculer le vecteur vers le centre
        dx_to_center = center_x - self.x
        dy_to_center = center_y - self.y
        distance_to_center = math.sqrt(dx_to_center * dx_to_center + dy_to_center * dy_to_center)
        
        # Normaliser et appliquer une vitesse initiale vers le centre
        initial_speed = 100.0  # Vitesse initiale fixe
        if distance_to_center > 0:
            self.vx = (dx_to_center / distance_to_center) * initial_speed
            self.vy = (dy_to_center / distance_to_center) * initial_speed
        else:
            self.vx = 0
            self.vy = 0
        
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
        
        # Position précédente pour détecter le franchissement des lignes
        self.prev_x = self.x
        self.prev_y = self.y
        
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
        
        # Appliquer les forces de bruit à la vélocité (plus subtiles pour maintenir la direction)
        force_x = noise_x * Config.AMPLITUDE_BRUIT_POSITION
        force_y = noise_y * Config.AMPLITUDE_BRUIT_POSITION
        
        self.vx += force_x * time_factor * 0.2  # Influence très réduite du bruit
        self.vy += force_y * time_factor * 0.2
        
        # Maintenir une vitesse minimale pour éviter l'arrêt complet
        current_speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        min_speed = 30.0  # Vitesse minimale
        
        if current_speed < min_speed and current_speed > 0:
            # Normaliser et appliquer la vitesse minimale
            self.vx = (self.vx / current_speed) * min_speed
            self.vy = (self.vy / current_speed) * min_speed
        elif current_speed == 0:
            # Si complètement arrêté, donner une direction aléatoire
            angle = random.uniform(0, 2 * math.pi)
            self.vx = math.cos(angle) * min_speed
            self.vy = math.sin(angle) * min_speed
        
        # Répulsion entre joueurs avec accélération plus forte
        for other in other_players:
            if other.id != self.id:
                dx = self.x - other.x
                dy = self.y - other.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                min_distance = (self.radius + other.radius) * 2.5
                if distance < min_distance and distance > 0:
                    # Force de répulsion beaucoup plus forte lors des collisions entre joueurs
                    force_magnitude = (Config.FORCE_REPULSION_JOUEURS * 3) / (distance * distance)  # 3x plus forte
                    force_x = (dx / distance) * force_magnitude
                    force_y = (dy / distance) * force_magnitude
                    
                    # Accélération plus importante lors des collisions entre joueurs
                    acceleration_factor = 2.5  # Accélération supplémentaire
                    self.vx += force_x * time_factor * acceleration_factor
                    self.vy += force_y * time_factor * acceleration_factor
        

        
        # Limiter la vitesse maximum
        speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        if speed > Config.VITESSE_MAX_JOUEUR:
            factor = Config.VITESSE_MAX_JOUEUR / speed
            self.vx *= factor
            self.vy *= factor
        
        # Mettre à jour la position
        new_x = self.x + self.vx * time_factor
        new_y = self.y + self.vy * time_factor
        
        # Collision avec les parois du cercle (rebond plus fréquent)
        dx = new_x - self.center_x
        dy = new_y - self.center_y
        distance_from_center = math.sqrt(dx * dx + dy * dy)
        
        # Réduire la marge pour des rebonds plus fréquents
        max_distance = self.circle_radius - self.radius * 0.5  # Rebond plus tôt
        if distance_from_center > max_distance:
            # Rebond sur la paroi avec variabilité réaliste
            # Normaliser le vecteur de position
            nx = dx / distance_from_center
            ny = dy / distance_from_center
            
            # Calculer l'angle actuel de la vitesse
            current_angle = math.atan2(self.vy, self.vx)
            current_speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
            
            # Ajouter de la variabilité à l'angle de rebond (entre 160° et 200° au lieu de 180°)
            angle_variation = random.uniform(-20, 20)  # ±20° de variation
            target_angle = current_angle + math.pi + math.radians(angle_variation)  # ~180° ± 20°
            
            # Appliquer le nouveau vecteur de vitesse avec rebond énergique mais variable
            bounce_coefficient = Config.COEFFICIENT_REBOND * random.uniform(0.85, 1.1)  # Variabilité dans le rebond
            self.vx = math.cos(target_angle) * current_speed * bounce_coefficient
            self.vy = math.sin(target_angle) * current_speed * bounce_coefficient
            
            # Repositionner le joueur à la limite
            factor = max_distance / distance_from_center
            new_x = self.center_x + dx * factor
            new_y = self.center_y + dy * factor
        
        # Sauvegarder la position précédente avant la mise à jour
        self.prev_x = self.x
        self.prev_y = self.y
        
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
        # Taille adaptée au nombre de cibles (plus petites si plus nombreuses)
        # On utilise un dict global pour compter les cibles, approximation avec players pour l'instant
        base_radius = 3 if len(players) > 3 else 4  # Simple heuristique
        
        # Couleur de base
        if self.owner_id is None:
            color = Config.COULEUR_CIBLE_LIBRE
            radius = base_radius
        else:
            color = players[self.owner_id].color
            radius = base_radius + 1
        
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
        
        # Contour seulement pour les cibles possédées ou en cours de clignotement
        if self.owner_id is not None or self.is_blinking:
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
        
        # Attribution initiale des cibles
        self.update_target_ownership()
        
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
        # Calcul du nombre de cibles basé sur la circonférence et la densité configurée
        circumference = 2 * math.pi * Config.TAILLE_CERCLE
        num_targets = int(circumference * Config.DENSITE_CIBLES_PAR_PIXEL)
        num_targets = max(Config.NOMBRE_MIN_CIBLES, num_targets)
        
        print(f"Création de {num_targets} cibles sur le cercle (circonférence: {circumference:.0f}px)")
        
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
    
    def check_target_collisions(self):
        """Vérifie si une cible touche l'extérieur du joueur (pas son centre)."""
        for player in self.players.values():
            # Vérifier la collision avec chaque cible
            for target in self.targets.values():
                # Calculer la distance entre le centre du joueur et la cible
                dx = player.x - target.x
                dy = player.y - target.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # La cible est capturée si elle touche l'extérieur du joueur
                # Distance doit être <= rayon du joueur pour que la cible soit "à l'intérieur" du cercle du joueur
                if distance <= player.radius:
                    # Le joueur touche cette cible
                    if target.owner_id != player.id:  # Si ce n'est pas déjà sa cible
                        old_owner = target.owner_id
                        target.set_owner(player.id)
                        
                        # Ajouter des points au joueur qui a touché la cible
                        player.add_score(1)
                        
                        # Appliquer une réduction de puissance à l'ancien propriétaire (si il y en avait un)
                        if old_owner is not None:
                            self.players[old_owner].apply_power_reduction()
                        
                        # Forcer la mise à jour de l'UI
                        self.ui_needs_update = True
                        
                        if old_owner is not None:
                            print(f"Joueur {player.id + 1} touche une cible du joueur {old_owner + 1} !")
                        else:
                            print(f"Joueur {player.id + 1} touche une cible libre !")
    
    def check_line_crossings(self):
        """Vérifie si un joueur a franchi une ligne appartenant à un autre joueur."""
        for player in self.players.values():
            # Vérifier le franchissement de chaque ligne (cible possédée par d'autres)
            for target in self.targets.values():
                if target.owner_id is not None and target.owner_id != player.id:
                    # Vérifier si le joueur a traversé cette ligne
                    if self.has_crossed_line(player, target):
                        # Le joueur franchit une ligne ennemie - il gagne la ligne
                        old_owner = target.owner_id
                        target.set_owner(player.id)
                        
                        # Ajouter des points au joueur qui a franchi
                        player.add_score(1)
                        
                        # Appliquer une réduction de puissance à l'ancien propriétaire
                        if old_owner is not None:
                            self.players[old_owner].apply_power_reduction()
                        
                        # Forcer la mise à jour de l'UI
                        self.ui_needs_update = True
                        
                        print(f"Joueur {player.id + 1} franchit une ligne du joueur {old_owner + 1} !")
    
    def has_crossed_line(self, player: Player, target: Target) -> bool:
        """Vérifie si le joueur (avec son rayon) a traversé une ligne."""
        # Position actuelle et précédente du joueur
        px1, py1 = player.prev_x, player.prev_y
        px2, py2 = player.x, player.y
        
        # Position du propriétaire de la ligne et de la cible (ligne à traverser)
        owner = self.players[target.owner_id]
        ox, oy = owner.x, owner.y
        tx, ty = target.x, target.y
        
        # Vérifier l'intersection entre le trajet du joueur et la ligne
        # En tenant compte du rayon du joueur pour une détection plus sensible
        if self.segments_intersect(px1, py1, px2, py2, ox, oy, tx, ty):
            return True
            
        # Vérifier aussi si le joueur est maintenant assez proche de la ligne pour la "toucher"
        # Distance du centre du joueur à la ligne
        distance_to_line = self.point_to_line_distance(px2, py2, ox, oy, tx, ty)
        return distance_to_line <= player.radius
    
    def segments_intersect(self, x1, y1, x2, y2, x3, y3, x4, y4) -> bool:
        """Vérifie si deux segments de droite s'intersectent."""
        # Calcul des déterminants pour l'intersection de segments
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        
        if abs(denom) < 1e-10:  # Segments parallèles
            return False
        
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        
        # Intersection si les deux paramètres sont entre 0 et 1
        return 0 <= t <= 1 and 0 <= u <= 1
    
    def point_to_line_distance(self, px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
        """Calcule la distance d'un point à un segment de ligne."""
        # Vecteur de la ligne
        dx = x2 - x1
        dy = y2 - y1
        
        # Si la ligne est un point
        if dx == 0 and dy == 0:
            return math.sqrt((px - x1)**2 + (py - y1)**2)
        
        # Paramètre t pour la projection du point sur la ligne
        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        
        # Limiter t entre 0 et 1 pour rester sur le segment
        t = max(0, min(1, t))
        
        # Point le plus proche sur le segment
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        # Distance du point au point le plus proche
        return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)
    
    def update_target_ownership(self):
        """Attribution initiale d'une seule cible par joueur (seulement au début)."""
        # Chaque joueur commence avec seulement une ligne - la cible la plus proche
        for player_id, player in self.players.items():
            closest_target = None
            min_distance_sq = float('inf')
            
            # Trouver la cible la plus proche de ce joueur
            for target in self.targets.values():
                if target.owner_id is None:  # Seulement les cibles non attribuées
                    distance_sq = (player.x - target.x) ** 2 + (player.y - target.y) ** 2
                    if distance_sq < min_distance_sq:
                        min_distance_sq = distance_sq
                        closest_target = target
            
            # Attribuer cette cible au joueur
            if closest_target is not None:
                closest_target.set_owner(player_id)
                print(f"Joueur {player_id + 1} commence avec 1 ligne")
    
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
        
        # Vérification des collisions avec les cibles à chaque frame
        self.check_target_collisions()
        
        # Vérification du franchissement des lignes à chaque frame
        self.check_line_crossings()
        
        # Vérifier la condition de victoire
        self.check_victory_condition()
    
    def check_victory_condition(self):
        """Vérifie si un joueur a atteint la condition de victoire."""
        for player in self.players.values():
            if player.score >= Config.CONDITION_VICTOIRE:
                if not hasattr(self, 'victory_announced'):
                    print(f"Joueur {player.id + 1} remporte la partie avec {player.score} points !")
                    print("Appuyez sur Échap pour quitter ou fermez la fenêtre.")
                    self.victory_announced = True
                self.ui_needs_update = True  # Forcer la mise à jour de l'UI
                # Le jeu continue pour l'affichage, mais la victoire est annoncée
    
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
        
        # Titre plus compact
        title_text = self.font_medium.render("Bataille de Lignes", True, Config.COULEUR_TEXTE)
        title_rect = title_text.get_rect(center=(Config.LARGEUR // 2, 20))
        self.ui_surface.blit(title_text, title_rect)
        
        # Scores des joueurs plus compacts
        score_y = 45
        for i, (player_id, player) in enumerate(self.players.items()):
            # Couleur du joueur (plus petite)
            color_rect = pygame.Rect(15, score_y + i * 28, 15, 15)
            pygame.draw.rect(self.ui_surface, player.color, color_rect)
            pygame.draw.rect(self.ui_surface, Config.COULEUR_TEXTE, color_rect, 1)
            
            # Score et informations sur une seule ligne
            score_text = f"J{player_id + 1}: {player.score}"
            if player.was_power_reduced:
                score_text += " [AFFAIBLI]"
            
            score_surface = self.font_small.render(score_text, True, Config.COULEUR_TEXTE)
            self.ui_surface.blit(score_surface, (35, score_y + i * 28 + 2))
        
        # Informations de configuration plus compactes
        config_y = ui_height - 50
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
        
        # Ne plus dessiner les cibles (ronds) - seulement les lignes
        # for target in self.targets.values():
        #     target.draw(self.screen, self.players)
        
        # Dessiner les joueurs
        for player in self.players.values():
            player.draw(self.screen, self.font_small)
        
        # Dessiner l'interface utilisateur par-dessus
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_connections(self):
        """Dessine les lignes de connexion entre les joueurs et leurs cibles."""
        for target in self.targets.values():
            if target.owner_id is not None:
                player = self.players[target.owner_id]
                
                # Lignes très fines pour un effet visuel propre
                thickness = Config.EPAISSEUR_LIGNE_NORMALE
                if target.is_blinking:
                    thickness = Config.EPAISSEUR_LIGNE_CONTRE_ATTAQUE
                
                # Couleur de la ligne
                color = player.color
                if target.is_blinking and (pygame.time.get_ticks() // 100) % 2 == 0:
                    color = Config.COULEUR_CONTRE_ATTAQUE
                
                # Dessiner la ligne du joueur vers sa cible
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