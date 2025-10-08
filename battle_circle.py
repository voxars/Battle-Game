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


class SoundManager:
    """Gestionnaire de sons synthétiques pour le jeu."""
    
    def __init__(self, sample_rate: int = 22050):
        """Initialise le gestionnaire de sons."""
        pygame.mixer.pre_init(frequency=sample_rate, size=-16, channels=2, buffer=512)
        self.sample_rate = sample_rate
        self.sounds = {}
        self._generate_sounds()
    
    def _generate_sounds(self):
        """Génère tous les sons synthétiques du jeu."""
        # Son de collision avec les bords (grave/métallique)
        self.sounds['border_collision'] = self._create_border_collision_sound()
        
        # Son de collision entre joueurs (plus aigu)
        self.sounds['player_collision'] = self._create_player_collision_sound()
        
        # Son d'élimination (dramatique)
        self.sounds['elimination'] = self._create_elimination_sound()
        
        # Son de vol de ligne (cristallin)
        self.sounds['line_steal'] = self._create_line_steal_sound()
        
        # Son d'alerte fin de jeu (prioritaire)
        self.sounds['end_game_alert'] = self._create_end_game_alert_sound()
    
    def _create_border_collision_sound(self) -> pygame.mixer.Sound:
        """Crée un son de collision avec les bords (métallique)."""
        duration = 0.3  # 300ms
        frames = int(duration * self.sample_rate)
        
        # Génération d'un son métallique avec harmoniques
        t = np.linspace(0, duration, frames, False)
        
        # Fréquence de base grave
        freq = 150
        wave = np.sin(2 * np.pi * freq * t)
        
        # Ajout d'harmoniques pour effet métallique
        wave += 0.3 * np.sin(2 * np.pi * freq * 2 * t)
        wave += 0.2 * np.sin(2 * np.pi * freq * 3 * t)
        
        # Enveloppe d'attaque rapide et décroissance
        envelope = np.exp(-5 * t)
        wave = wave * envelope
        
        # Normalisation et conversion stéréo
        wave = np.clip(wave * 0.3, -1, 1)
        stereo_wave = np.column_stack([wave, wave])
        
        # Conversion en format pygame
        wave_array = (stereo_wave * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(wave_array)
    
    def _create_player_collision_sound(self) -> pygame.mixer.Sound:
        """Crée un son de collision entre joueurs (plus aigu)."""
        duration = 0.2  # 200ms
        frames = int(duration * self.sample_rate)
        
        # Son plus aigu et brillant
        t = np.linspace(0, duration, frames, False)
        
        # Fréquence plus haute
        freq = 400
        wave = np.sin(2 * np.pi * freq * t)
        
        # Modulation de fréquence pour effet "choc"
        modulation = 1 + 0.5 * np.sin(2 * np.pi * 20 * t)
        wave = wave * modulation
        
        # Enveloppe rapide
        envelope = np.exp(-10 * t)
        wave = wave * envelope
        
        # Normalisation et conversion stéréo
        wave = np.clip(wave * 0.25, -1, 1)
        stereo_wave = np.column_stack([wave, wave])
        
        # Conversion en format pygame
        wave_array = (stereo_wave * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(wave_array)
    
    def _create_elimination_sound(self) -> pygame.mixer.Sound:
        """Crée un son d'élimination dramatique (1.5 sec)."""
        duration = 1.5  # 1.5 secondes
        frames = int(duration * self.sample_rate)
        
        t = np.linspace(0, duration, frames, False)
        
        # Descente de fréquence dramatique
        start_freq = 800
        end_freq = 60
        freq = start_freq * np.exp(-2 * t)  # Descente exponentielle
        
        # Génération de l'onde avec fréquence variable
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        wave = np.sin(phase)
        
        # Ajout d'harmoniques pour richesse
        wave += 0.3 * np.sin(2 * phase)
        wave += 0.1 * np.sin(3 * phase)
        
        # Enveloppe avec sustain puis fade out
        envelope = np.ones_like(t)
        fade_start = int(0.8 * frames)
        envelope[fade_start:] = np.linspace(1, 0, frames - fade_start)
        wave = wave * envelope
        
        # Ajout d'un effet de réverbération simple
        reverb_delay = int(0.05 * self.sample_rate)  # 50ms
        reverb_wave = np.zeros_like(wave)
        reverb_wave[reverb_delay:] = wave[:-reverb_delay] * 0.3
        wave = wave + reverb_wave
        
        # Normalisation et conversion stéréo
        wave = np.clip(wave * 0.4, -1, 1)
        stereo_wave = np.column_stack([wave, wave])
        
        # Conversion en format pygame
        wave_array = (stereo_wave * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(wave_array)
    
    def _create_line_steal_sound(self) -> pygame.mixer.Sound:
        """Crée un son doux et mélodieux pour le vol de ligne."""
        duration = 0.3  # 300ms (plus court)
        frames = int(duration * self.sample_rate)
        
        t = np.linspace(0, duration, frames, False)
        
        # Son plus doux avec fréquences moins aiguës
        start_freq = 400  # Plus grave
        end_freq = 800   # Moins aigu
        # Montée progressive plus douce
        freq = start_freq + (end_freq - start_freq) * np.sqrt(t / duration)  # Courbe adoucie
        
        # Génération de l'onde avec fréquence variable
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        wave = np.sin(phase)
        
        # Harmoniques plus douces et moins nombreuses
        wave += 0.2 * np.sin(2 * phase)  # Octave réduite
        wave += 0.1 * np.sin(3 * phase)  # Quinte très réduite
        
        # Pas de trémolo pour un son plus lisse
        
        # Enveloppe plus douce avec attaque et decay plus longs
        attack_time = 0.08  # 80ms d'attaque plus douce
        decay_start = int(0.4 * frames)  # Decay plus tardif
        
        envelope = np.ones_like(t)
        # Attaque douce
        attack_frames = int(attack_time * self.sample_rate)
        envelope[:attack_frames] = np.sin(np.pi * 0.5 * np.linspace(0, 1, attack_frames))  # Courbe sinusoïdale
        # Decay progressif et doux
        envelope[decay_start:] = np.cos(np.pi * 0.5 * np.linspace(0, 1, frames - decay_start))
        
        wave = wave * envelope
        
        # Normalisation avec volume encore plus réduit
        wave = np.clip(wave * 0.15, -1, 1)  # Volume réduit de moitié
        stereo_wave = np.column_stack([wave, wave])
        
        # Conversion en format pygame
        wave_array = (stereo_wave * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(wave_array)
    
    def _create_end_game_alert_sound(self) -> pygame.mixer.Sound:
        """Crée un son d'alerte adouci pour la fin de jeu."""
        duration = 1.0  # 1 seconde
        frames = int(duration * self.sample_rate)
        
        t = np.linspace(0, duration, frames, False)
        
        # Son d'alerte plus doux avec fréquence réduite
        base_freq = 500  # Fréquence plus grave (était 800)
        
        # Pulsations plus douces à 2 Hz (2 battements par seconde)
        pulsation = 0.6 + 0.4 * np.sin(2 * np.pi * 2 * t)  # Moins contrasté
        
        # Onde principale plus douce
        wave = np.sin(2 * np.pi * base_freq * t)
        
        # Harmoniques réduites pour moins de stridence
        wave += 0.3 * np.sin(2 * np.pi * base_freq * 2 * t)  # Octave réduite
        wave += 0.1 * np.sin(2 * np.pi * base_freq * 3 * t)  # Quinte très réduite
        
        # Application des pulsations
        wave = wave * pulsation
        
        # Modulation de fréquence plus subtile
        freq_mod = 1 + 0.05 * np.sin(2 * np.pi * 4 * t)  # Vibrato plus doux et lent
        phase_mod = 2 * np.pi * base_freq * np.cumsum(freq_mod) / self.sample_rate
        wave_mod = np.sin(phase_mod) * pulsation
        
        # Mélange plus équilibré
        wave = 0.8 * wave + 0.2 * wave_mod
        
        # Enveloppe plus douce
        envelope = np.minimum(1.0, t * 3)  # Montée plus lente sur 0.33 secondes
        envelope = np.minimum(envelope, np.linspace(1, 0.7, frames))  # Diminution plus douce
        
        wave = wave * envelope
        
        # Volume réduit pour moins d'agression
        wave = np.clip(wave * 0.5, -1, 1)  # Volume réduit de 0.8 à 0.5
        stereo_wave = np.column_stack([wave, wave])
        
        # Conversion en format pygame
        wave_array = (stereo_wave * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(wave_array)
    
    def play_sound(self, sound_name: str, volume: float = 1.0):
        """Joue un son avec le volume spécifié."""
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(volume)
            sound.play()
    
    def play_border_collision(self, volume: float = 0.4):
        """Joue le son de collision avec les bords."""
        self.play_sound('border_collision', volume)
    
    def play_player_collision(self, volume: float = 0.5):
        """Joue le son de collision entre joueurs."""
        self.play_sound('player_collision', volume)
    
    def play_elimination(self, volume: float = 0.6):
        """Joue le son d'élimination."""
        self.play_sound('elimination', volume)
    
    def play_line_steal(self, volume: float = 0.2):
        """Joue le son de vol de ligne."""
        self.play_sound('line_steal', volume)
    
    def play_end_game_alert(self, volume: float = 0.8):
        """Joue le son d'alerte de fin de jeu (prioritaire)."""
        # Arrêter tous les autres sons avant de jouer l'alerte
        pygame.mixer.stop()
        self.play_sound('end_game_alert', volume)


class Confetti:
    """Classe pour un confetti individuel."""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        """Initialise un confetti."""
        self.x = x
        self.y = y
        self.color = color
        
        # Vitesse aléatoire
        self.vx = random.uniform(-150, 150)
        self.vy = random.uniform(-300, -100)
        
        # Gravité et friction
        self.gravity = 500
        self.friction = 0.98
        
        # Propriétés visuelles
        self.size = random.randint(3, 8)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-360, 360)
        
        # Durée de vie
        self.life = 1.0
        self.fade_speed = random.uniform(0.3, 0.8)
        
    def update(self, dt: float):
        """Met à jour la position et l'état du confetti."""
        # Physique
        self.vx *= self.friction
        self.vy += self.gravity * dt
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Rotation
        self.rotation += self.rotation_speed * dt
        
        # Durée de vie
        self.life -= self.fade_speed * dt
        
    def draw(self, screen: pygame.Surface):
        """Dessine le confetti."""
        if self.life <= 0:
            return
            
        # Calculer l'alpha basé sur la durée de vie
        alpha = max(0, min(255, int(self.life * 255)))
        
        # Créer une surface avec transparence
        size = max(1, int(self.size * self.life))
        
        # Dessiner un petit rectangle coloré
        color_with_alpha = (*self.color, alpha)
        
        # Simple rectangle pour représenter le confetti
        rect = pygame.Rect(int(self.x - size/2), int(self.y - size/2), size, size)
        
        # Appliquer une couleur légèrement variée
        varied_color = (
            max(0, min(255, self.color[0] + random.randint(-20, 20))),
            max(0, min(255, self.color[1] + random.randint(-20, 20))),
            max(0, min(255, self.color[2] + random.randint(-20, 20)))
        )
        
        pygame.draw.rect(screen, varied_color, rect)
        
    def is_alive(self) -> bool:
        """Vérifie si le confetti est encore vivant."""
        return self.life > 0 and self.y < Config.HAUTEUR + 50


class ConfettiSystem:
    """Système de gestion des confettis."""
    
    def __init__(self):
        """Initialise le système de confettis."""
        self.confettis: List[Confetti] = []
        self.is_active = False
        
    def start_celebration(self, winner_color: Tuple[int, int, int], center_x: float, center_y: float):
        """Lance la célébration avec confettis."""
        self.is_active = True
        self.confettis.clear()
        
        # Créer plusieurs vagues de confettis
        for wave in range(3):
            for i in range(30):  # 30 confettis par vague
                # Position légèrement aléatoire autour du centre
                x = center_x + random.uniform(-100, 100)
                y = center_y + random.uniform(-50, 50)
                
                # Variations de couleur basées sur la couleur du gagnant
                color_variations = [
                    winner_color,
                    (min(255, winner_color[0] + 50), min(255, winner_color[1] + 50), min(255, winner_color[2] + 50)),
                    (max(0, winner_color[0] - 50), max(0, winner_color[1] - 50), max(0, winner_color[2] - 50)),
                    (255, 255, 255),  # Blanc
                    (255, 255, 100)   # Jaune doré
                ]
                
                color = random.choice(color_variations)
                confetti = Confetti(x, y, color)
                
                # Délai pour les vagues
                confetti.delay = wave * 0.3
                self.confettis.append(confetti)
    
    def update(self, dt: float):
        """Met à jour tous les confettis."""
        if not self.is_active:
            return
            
        # Mettre à jour les confettis existants
        for confetti in self.confettis[:]:
            if hasattr(confetti, 'delay') and confetti.delay > 0:
                confetti.delay -= dt
                continue
                
            confetti.update(dt)
            
            # Supprimer les confettis morts
            if not confetti.is_alive():
                self.confettis.remove(confetti)
        
        # Arrêter le système si plus de confettis
        if not self.confettis:
            self.is_active = False
    
    def draw(self, screen: pygame.Surface):
        """Dessine tous les confettis."""
        if not self.is_active:
            return
            
        for confetti in self.confettis:
            if not hasattr(confetti, 'delay') or confetti.delay <= 0:
                confetti.draw(screen)


class Config:
    """Classe de configuration centralisée pour tous les paramètres du jeu."""
    
    # Paramètres de jeu modifiables
    NOMBRE_PARTICIPANTS: int = 6
    CONDITION_VICTOIRE: int = 200
    DUREE_PARTIE: int = 60  # Durée de la partie en secondes (1 minute)
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
        (100, 255, 255),  # Cyan
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
    DENSITE_CIBLES_PAR_PIXEL: float = 0.035  # Une cible tous les 35 pixels (environ 55 cibles)
    NOMBRE_MIN_CIBLES: int = 30
    
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
        return 80  # Zone UI très compacte - juste titre et timer


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
    
    def __init__(self, player_id: int, color: Tuple[int, int, int], center_x: float, center_y: float, circle_radius: float, total_players: int = Config.NOMBRE_PARTICIPANTS, sound_manager=None):
        """
        Initialise un joueur.
        
        Args:
            player_id: Identifiant unique du joueur
            color: Couleur RGB du joueur
            center_x, center_y: Centre du cercle de jeu
            circle_radius: Rayon du cercle de jeu
            total_players: Nombre total de joueurs (pour le calcul d'angle)
            sound_manager: Gestionnaire de sons pour les effets audio
        """
        self.id = player_id
        self.color = color
        self.name = f"Joueur {player_id + 1}"  # Nom par défaut
        self.score = 0
        self.power_factor = 1.0  # Facteur de puissance normal
        self.is_eliminated = False  # État d'élimination
        self.sound_manager = sound_manager  # Gestionnaire de sons
        
        # Positions et mouvement
        self.center_x = center_x
        self.center_y = center_y
        self.circle_radius = circle_radius
        
        # Position initiale sur le cercle avec légère variabilité
        # Les joueurs sont espacés de manière égale sur le cercle avec petite variation d'angle
        base_angle = (2 * math.pi * player_id) / total_players
        angle_variation = random.uniform(-0.1, 0.1)  # ±0.1 radian de variation (~6°)
        angle = base_angle + angle_variation
        distance_variation = random.uniform(0.7, 0.8)  # Distance légèrement variable
        distance = circle_radius * distance_variation
        self.x = center_x + distance * math.cos(angle)
        self.y = center_y + distance * math.sin(angle)
        
        # Vélocité initiale dirigée exactement vers le centre du cercle
        # Chaque joueur part de sa position initiale directement vers le centre exact
        dx_to_center = center_x - self.x  # Composante X vers le centre
        dy_to_center = center_y - self.y  # Composante Y vers le centre
        distance_to_center = math.sqrt(dx_to_center * dx_to_center + dy_to_center * dy_to_center)
        
        # Normaliser le vecteur et appliquer la vitesse initiale vers le centre exact
        initial_speed = 150.0  # Vitesse initiale augmentée pour éviter l'élimination précoce
        if distance_to_center > 0:
            # Direction normalisée vers le centre exact du cercle
            self.vx = (dx_to_center / distance_to_center) * initial_speed
            self.vy = (dy_to_center / distance_to_center) * initial_speed
        else:
            # Cas improbable où le joueur serait déjà au centre - vitesse aléatoire élevée
            angle = random.uniform(0, 2 * math.pi)
            self.vx = math.cos(angle) * initial_speed
            self.vy = math.sin(angle) * initial_speed
        
        # Base pour le bruit de Perlin (force d'attraction/répulsion)
        # Créer un générateur de bruit unique pour chaque joueur avec seed très variable
        base_seed = random.randint(1, 100000)  # Seed aléatoire de base
        self.noise_generator = SimplexNoise(seed=player_id * 1000 + base_seed)  # Seed très variable
        self.noise_offset_x = random.uniform(0, 5000)  # Offset beaucoup plus variable
        self.noise_offset_y = random.uniform(0, 5000)  # Offset beaucoup plus variable
        self.noise_time = random.uniform(0, 100)  # Démarrer à des temps différents
        
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
        # Ne pas mettre à jour les joueurs éliminés
        if self.is_eliminated:
            return
            
        self.noise_time += time_factor * Config.VITESSE_MOUVEMENT_JOUEUR
        
        # Forces de bruit de Perlin (plus subtiles maintenant)
        # Utiliser le générateur de bruit individuel du joueur
        noise_x = self.noise_generator.noise(
            self.noise_offset_x + self.noise_time,
            self.noise_offset_y
        )
        noise_y = self.noise_generator.noise(
            self.noise_offset_x,
            self.noise_offset_y + self.noise_time
        )
        
        # Appliquer les forces de bruit à la vélocité (encore plus subtiles au début)
        force_x = noise_x * Config.AMPLITUDE_BRUIT_POSITION
        force_y = noise_y * Config.AMPLITUDE_BRUIT_POSITION
        
        # Réduire l'influence du bruit au début du jeu pour éviter les ralentissements
        noise_influence = 0.05 if self.noise_time < 20 else 0.15  # Très faible au début
        self.vx += force_x * time_factor * noise_influence
        self.vy += force_y * time_factor * noise_influence
        
        # Empêcher le ralentissement - les joueurs accélèrent constamment
        current_speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        
        # Vitesse minimale qui augmente avec le temps pour éviter tout ralentissement
        base_min_speed = 120.0  # Vitesse de base cohérente avec la vitesse initiale
        acceleration_bonus = self.noise_time * 3.0  # Accélération progressive plus rapide
        min_speed = base_min_speed + acceleration_bonus
        
        if current_speed < min_speed:
            if current_speed > 0:
                # Normaliser et appliquer la vitesse minimale croissante
                self.vx = (self.vx / current_speed) * min_speed
                self.vy = (self.vy / current_speed) * min_speed
            else:
                # Si complètement arrêté, utiliser la direction initiale vers le centre
                dx_to_center = self.center_x - self.x
                dy_to_center = self.center_y - self.y
                distance_to_center = math.sqrt(dx_to_center * dx_to_center + dy_to_center * dy_to_center)
                
                if distance_to_center > 0:
                    self.vx = (dx_to_center / distance_to_center) * min_speed
                    self.vy = (dy_to_center / distance_to_center) * min_speed
                else:
                    # Dernière option : direction aléatoire
                    angle = random.uniform(0, 2 * math.pi)
                    self.vx = math.cos(angle) * min_speed
                    self.vy = math.sin(angle) * min_speed
        else:
            # Même si la vitesse est suffisante, ajouter une micro-accélération constante
            speed_boost = 1.001  # Augmentation de 0.1% à chaque frame
            self.vx *= speed_boost
            self.vy *= speed_boost
        
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
            # Rebond vers le centre avec variation d'angle
            
            # Jouer le son de collision avec les bords
            if self.sound_manager:
                self.sound_manager.play_border_collision()
            # Calculer la direction vers le centre du cercle
            center_direction_x = self.center_x - new_x
            center_direction_y = self.center_y - new_y
            center_distance = math.sqrt(center_direction_x * center_direction_x + center_direction_y * center_direction_y)
            
            # Normaliser la direction vers le centre
            if center_distance > 0:
                center_direction_x /= center_distance
                center_direction_y /= center_distance
            
            # Calculer l'angle vers le centre
            center_angle = math.atan2(center_direction_y, center_direction_x)
            
            # Ajouter une variation de ±20° autour de la direction vers le centre
            angle_variation = random.uniform(-20, 20)  # ±20° de variation
            target_angle = center_angle + math.radians(angle_variation)

            # Calculer la vitesse actuelle pour maintenir l'énergie
            current_speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
            
            # Appliquer le nouveau vecteur de vitesse vers le centre avec variation ET accélération
            bounce_coefficient = Config.COEFFICIENT_REBOND * random.uniform(1.0, 1.4)  # Jamais de ralentissement
            speed_boost = 1.3  # Accélération de 30% lors du rebond sur les bords
            boosted_speed = current_speed * bounce_coefficient * speed_boost
            self.vx = math.cos(target_angle) * boosted_speed
            self.vy = math.sin(target_angle) * boosted_speed
            
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
    
    def check_elimination(self, targets: Dict[int, 'Target']):
        """Vérifie si le joueur doit être éliminé (plus de lignes)."""
        owned_count = sum(1 for target in targets.values() if target.owner_id == self.id)
        if owned_count == 0 and not self.is_eliminated:
            self.is_eliminated = True
            print(f"Joueur {self.id + 1} éliminé - plus de lignes !")
            
            # Jouer le son d'élimination
            if self.sound_manager:
                self.sound_manager.play_elimination()
        return self.is_eliminated
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Dessine le joueur sur l'écran."""
        # Ne pas dessiner les joueurs éliminés
        if self.is_eliminated:
            return
            
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


class ConfigScreen:
    """Interface de configuration avant le jeu."""
    
    def __init__(self, screen):
        """Initialise l'écran de configuration."""
        self.screen = screen
        
        # Polices
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # État de l'interface
        self.running = True
        self.game_ready = False
        self.user_interacted = False  # Pour s'assurer que l'utilisateur a interagi avant de démarrer
        
        # Configuration modifiable
        self.num_players = 3
        self.game_duration = 60
        self.player_names = ["Joueur 1", "Joueur 2", "Joueur 3", "Joueur 4", "Joueur 5", "Joueur 6"]
        self.player_colors = [
            (255, 100, 100),  # Rouge
            (100, 255, 100),  # Vert
            (100, 100, 255),  # Bleu
            (255, 255, 100),  # Jaune
            (255, 100, 255),  # Magenta
            (100, 255, 255),  # Cyan
        ]
        
        # Couleurs disponibles pour sélection
        self.available_colors = [
            (255, 100, 100), (255, 200, 100), (255, 255, 100),  # Rouges/Oranges/Jaunes
            (100, 255, 100), (100, 255, 200), (100, 255, 255),  # Verts/Cyans
            (100, 100, 255), (200, 100, 255), (255, 100, 255),  # Bleus/Violets/Magentas
            (255, 255, 255), (200, 200, 200), (150, 150, 150),  # Blancs/Gris
        ]
        
        # Interface interactive
        self.input_active = None  # Quel champ est en cours d'édition
        self.input_text = ""
        
        # Boutons avec positions ajustées pour éviter les superpositions
        self.buttons = {
            'start': pygame.Rect(Config.LARGEUR // 2 - 100, Config.HAUTEUR - 100, 200, 40),
            'players_minus': pygame.Rect(350, 115, 35, 35),
            'players_plus': pygame.Rect(400, 115, 35, 35),
            'time_minus': pygame.Rect(350, 165, 35, 35),
            'time_plus': pygame.Rect(400, 165, 35, 35),
        }
        
        # Boutons pour les noms de joueurs (positions ajustées)
        for i in range(5):
            self.buttons[f'name_{i}'] = pygame.Rect(100, 280 + i * 50, 200, 30)
            self.buttons[f'color_{i}'] = pygame.Rect(320, 280 + i * 50, 30, 30)
    
    def handle_events(self):
        """Gère les événements de l'interface."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
                
                # Gestion de la saisie de texte
                if self.input_active is not None:
                    if event.key == pygame.K_RETURN:
                        # Valider la saisie
                        if self.input_active.startswith('name_'):
                            player_idx = int(self.input_active.split('_')[1])
                            if self.input_text.strip():
                                self.player_names[player_idx] = self.input_text.strip()
                        self.input_active = None
                        self.input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        # Gestion des caractères tapés
                        if len(self.input_text) < 20:  # Limite de caractères
                            # Utiliser event.unicode si disponible, sinon convertir depuis event.key
                            if hasattr(event, 'unicode') and event.unicode and event.unicode.isprintable():
                                self.input_text += event.unicode
                            elif event.key >= 32 and event.key <= 126:  # Caractères ASCII imprimables
                                # Conversion basique pour les lettres et chiffres
                                if event.key >= pygame.K_a and event.key <= pygame.K_z:
                                    char = chr(event.key)
                                    if pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]:
                                        char = char.upper()
                                    self.input_text += char
                                elif event.key >= pygame.K_0 and event.key <= pygame.K_9:
                                    self.input_text += chr(event.key)
                                elif event.key == pygame.K_SPACE:
                                    self.input_text += " "
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    mouse_pos = pygame.mouse.get_pos()
                    self.handle_click(mouse_pos)
    
    def handle_click(self, pos):
        """Gère les clics de souris."""
        # Bouton Start
        if self.buttons['start'].collidepoint(pos):
            self.game_ready = True
            return
        
        # Contrôles nombre de joueurs
        if self.buttons['players_minus'].collidepoint(pos):
            self.num_players = max(2, self.num_players - 1)
            self.user_interacted = True
        elif self.buttons['players_plus'].collidepoint(pos):
            self.num_players = min(6, self.num_players + 1)
            self.user_interacted = True
        
        # Contrôles durée
        elif self.buttons['time_minus'].collidepoint(pos):
            self.game_duration = max(30, self.game_duration - 30)
            self.user_interacted = True
        elif self.buttons['time_plus'].collidepoint(pos):
            self.game_duration = min(300, self.game_duration + 30)
            self.user_interacted = True
        
        # Noms et couleurs des joueurs
        for i in range(5):
            if self.buttons[f'name_{i}'].collidepoint(pos) and i < self.num_players:
                self.input_active = f'name_{i}'
                self.input_text = self.player_names[i]
                self.user_interacted = True
            elif self.buttons[f'color_{i}'].collidepoint(pos) and i < self.num_players:
                # Changer la couleur du joueur
                current_color_idx = self.available_colors.index(self.player_colors[i]) if self.player_colors[i] in self.available_colors else 0
                next_color_idx = (current_color_idx + 1) % len(self.available_colors)
                self.player_colors[i] = self.available_colors[next_color_idx]
                self.user_interacted = True
    
    def draw(self):
        """Dessine l'interface de configuration."""
        # Fond simple et uniforme
        self.screen.fill((25, 30, 45))
        
        # Titre simple
        title = self.font_large.render("Configuration", True, (255, 255, 255))
        title_rect = title.get_rect(center=(Config.LARGEUR // 2, 60))
        self.screen.blit(title, title_rect)
        
        # Nombre de joueurs
        players_label = self.font_medium.render("Nombre de joueurs:", True, (255, 255, 255))
        self.screen.blit(players_label, (50, 120))
        
        # Boutons +/-
        minus_btn = self.buttons['players_minus']
        plus_btn = self.buttons['players_plus']
        
        pygame.draw.rect(self.screen, (70, 70, 90), minus_btn)
        pygame.draw.rect(self.screen, (120, 120, 140), minus_btn, 2)
        minus_text = self.font_medium.render("-", True, (255, 255, 255))
        minus_rect = minus_text.get_rect(center=minus_btn.center)
        self.screen.blit(minus_text, minus_rect)
        
        pygame.draw.rect(self.screen, (70, 70, 90), plus_btn)
        pygame.draw.rect(self.screen, (120, 120, 140), plus_btn, 2)
        plus_text = self.font_medium.render("+", True, (255, 255, 255))
        plus_rect = plus_text.get_rect(center=plus_btn.center)
        self.screen.blit(plus_text, plus_rect)
        
        # Affichage du nombre séparé des boutons
        num_text = self.font_medium.render(str(self.num_players), True, (255, 255, 255))
        self.screen.blit(num_text, (310, 125))
        
        # Durée de partie
        time_label = self.font_medium.render("Durée (secondes):", True, (255, 255, 255))
        self.screen.blit(time_label, (50, 170))
        
        # Boutons +/- pour le temps
        time_minus_btn = self.buttons['time_minus']
        time_plus_btn = self.buttons['time_plus']
        
        pygame.draw.rect(self.screen, (70, 70, 90), time_minus_btn)
        pygame.draw.rect(self.screen, (120, 120, 140), time_minus_btn, 2)
        minus_text = self.font_medium.render("-", True, (255, 255, 255))
        minus_rect = minus_text.get_rect(center=time_minus_btn.center)
        self.screen.blit(minus_text, minus_rect)
        
        pygame.draw.rect(self.screen, (70, 70, 90), time_plus_btn)
        pygame.draw.rect(self.screen, (120, 120, 140), time_plus_btn, 2)
        plus_text = self.font_medium.render("+", True, (255, 255, 255))
        plus_rect = plus_text.get_rect(center=time_plus_btn.center)
        self.screen.blit(plus_text, plus_rect)
        
        # Affichage du temps séparé des boutons
        time_text = self.font_medium.render(f"{self.game_duration}s", True, (255, 255, 255))
        self.screen.blit(time_text, (310, 175))
        
        # Configuration des joueurs
        players_title = self.font_medium.render("Configuration des joueurs:", True, (255, 255, 255))
        self.screen.blit(players_title, (50, 240))
        
        for i in range(self.num_players):
            y_pos = 280 + i * 50
            
            # Cercle de couleur simple
            pygame.draw.circle(self.screen, self.player_colors[i], (70, y_pos + 15), 12)
            pygame.draw.circle(self.screen, (255, 255, 255), (70, y_pos + 15), 12, 2)
            
            # Numéro du joueur
            num_text = self.font_small.render(str(i + 1), True, (255, 255, 255))
            num_rect = num_text.get_rect(center=(70, y_pos + 15))
            self.screen.blit(num_text, num_rect)
            
            # Nom du joueur
            is_active = self.input_active == f'name_{i}'
            name_color = (255, 255, 100) if is_active else (255, 255, 255)
            bg_color = (60, 65, 80) if is_active else (50, 55, 70)
            
            name_rect = pygame.Rect(100, y_pos, 200, 30)
            pygame.draw.rect(self.screen, bg_color, name_rect)
            pygame.draw.rect(self.screen, name_color, name_rect, 2)
            
            # Afficher le texte
            display_name = self.input_text if is_active else self.player_names[i]
            if is_active and (pygame.time.get_ticks() // 500) % 2 == 0:
                display_name += "|"
            
            name_surface = self.font_small.render(display_name[:25], True, name_color)
            self.screen.blit(name_surface, (name_rect.x + 5, name_rect.y + 6))
            
            # Bouton couleur simple
            color_rect = pygame.Rect(320, y_pos, 30, 30)
            pygame.draw.rect(self.screen, self.player_colors[i], color_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), color_rect, 2)
            
            # Mise à jour des boutons
            self.buttons[f'name_{i}'] = name_rect
            self.buttons[f'color_{i}'] = color_rect
        
        # Bouton Start simple
        start_btn = self.buttons['start']
        pygame.draw.rect(self.screen, (60, 150, 60), start_btn)
        pygame.draw.rect(self.screen, (255, 255, 255), start_btn, 2)
        
        start_text = self.font_medium.render("COMMENCER", True, (255, 255, 255))
        start_rect = start_text.get_rect(center=start_btn.center)
        self.screen.blit(start_text, start_rect)
        
        # Instructions simples
        instructions = [
            "Cliquez sur un nom pour le modifier",
            "Cliquez sur le carré de couleur pour la changer"
        ]
        
        y = Config.HAUTEUR - 160
        for instruction in instructions:
            text = self.font_small.render(instruction, True, (200, 200, 200))
            self.screen.blit(text, (50, y))
            y += 25
        
        pygame.display.flip()
    
    def run(self):
        """Boucle principale de l'interface de configuration."""
        clock = pygame.time.Clock()
        
        while self.running and not self.game_ready:
            self.handle_events()
            self.draw()
            clock.tick(60)
        if self.game_ready:
            return self.get_config()
        else:
            return None
    
    def get_config(self):
        """Retourne la configuration choisie."""
        return {
            'num_players': self.num_players,
            'duration': self.game_duration,
            'player_names': self.player_names[:self.num_players],
            'player_colors': self.player_colors[:self.num_players]
        }


class CountdownScreen:
    """Écran de décompte avant le jeu."""
    
    def __init__(self, screen):
        self.screen = screen
        self.font_huge = pygame.font.Font(None, 120)
        self.font_large = pygame.font.Font(None, 48)
    
    def show_countdown(self):
        """Affiche le décompte de 3 secondes."""
        for count in [3, 2, 1]:
            # Effacer l'écran
            self.screen.fill((25, 25, 45))
            
            # Afficher le nombre
            count_text = self.font_huge.render(str(count), True, (255, 255, 100))
            count_rect = count_text.get_rect(center=(Config.LARGEUR // 2, Config.HAUTEUR // 2))
            self.screen.blit(count_text, count_rect)
            
            # Afficher "Préparez-vous !"
            ready_text = self.font_large.render("Préparez-vous !", True, (255, 255, 255))
            ready_rect = ready_text.get_rect(center=(Config.LARGEUR // 2, Config.HAUTEUR // 2 + 100))
            self.screen.blit(ready_text, ready_rect)
            
            pygame.display.flip()
            pygame.time.wait(1000)  # Attendre 1 seconde
        
        # Afficher "GO!"
        self.screen.fill((25, 25, 45))
        go_text = self.font_huge.render("GO!", True, (100, 255, 100))
        go_rect = go_text.get_rect(center=(Config.LARGEUR // 2, Config.HAUTEUR // 2))
        self.screen.blit(go_text, go_rect)
        pygame.display.flip()
        pygame.time.wait(500)  # Attendre 0.5 seconde
    
    def run(self):
        """Lance le décompte."""
        self.show_countdown()


class BattleGame:
    """Classe principale du jeu de bataille de lignes sur cercle."""
    
    def __init__(self, config=None):
        """Initialise le jeu et pygame."""
        pygame.init()
        pygame.font.init()
        
        # Configuration personnalisée ou par défaut
        if config:
            self.num_players = config['num_players']
            self.game_duration = config['duration']
            self.player_names = config['player_names']
            self.player_colors = config['player_colors']
        else:
            self.num_players = Config.NOMBRE_PARTICIPANTS
            self.game_duration = Config.DUREE_PARTIE
            self.player_names = [f"Joueur {i+1}" for i in range(Config.NOMBRE_PARTICIPANTS)]
            self.player_colors = Config.COULEURS_JOUEURS[:Config.NOMBRE_PARTICIPANTS]
        
        # Configuration de la fenêtre
        self.screen = pygame.display.set_mode((Config.LARGEUR, Config.HAUTEUR))
        pygame.display.set_caption("Bataille de Lignes sur Cercle")
        
        # Configuration du framerate
        self.clock = pygame.time.Clock()
        
        # Police pour l'affichage du texte
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Système audio
        self.sound_manager = SoundManager()
        
        # Variables de jeu
        self.running = True
        self.frame_count = 0
        self.last_fps_update = time.time()
        self.current_fps = 0
        
        # Timer de partie
        self.game_start_time = time.time()
        self.remaining_time = self.game_duration
        self.game_ended = False
        self.winner_by_time = None
        self.end_game_alert_played = False  # Pour éviter de jouer l'alerte plusieurs fois
        
        # Système d'accélération progressive
        self.last_acceleration_time = 0
        self.acceleration_interval = 5  # 5 secondes
        self.speed_boost_factor = 1.2  # Facteur d'accélération initial
        
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
        self.last_ui_update = 0
        
        # Système de confettis
        self.confetti_system = ConfettiSystem()
        
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
        for i in range(self.num_players):
            color = self.player_colors[i] if i < len(self.player_colors) else Config.COULEURS_JOUEURS[i % len(Config.COULEURS_JOUEURS)]
            player = Player(i, color, self.center_x, self.center_y, Config.TAILLE_CERCLE, self.num_players, self.sound_manager)
            if i < len(self.player_names):
                player.name = self.player_names[i]
            else:
                player.name = f"Joueur {i+1}"
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
                
                # Ignorer les collisions avec les joueurs éliminés
                if player1.is_eliminated or player2.is_eliminated:
                    continue
                
                # Calculer la distance entre les joueurs
                dx = player2.x - player1.x
                dy = player2.y - player1.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                min_distance = player1.radius + player2.radius
                
                if distance < min_distance and distance > 0:
                    # Collision détectée - rebond avec directions divergentes
                    
                    # Jouer le son de collision entre joueurs
                    self.sound_manager.play_player_collision()
                    
                    # Calculer l'angle de collision
                    collision_angle = math.atan2(dy, dx)
                    
                    # Vitesses actuelles des joueurs
                    speed1 = math.sqrt(player1.vx * player1.vx + player1.vy * player1.vy)
                    speed2 = math.sqrt(player2.vx * player2.vx + player2.vy * player2.vy)
                    
                    # Vitesse moyenne pour maintenir l'énergie
                    avg_speed = (speed1 + speed2) / 2
                    
                    # Force de rebond énergique
                    bounce_speed = avg_speed * 1.4  # 40% d'augmentation
                    
                    # Calculer les angles de rebond avec divergence minimale de 90°
                    # Player1 rebondit à ~135° de l'angle de collision
                    # Player2 rebondit à ~45° de l'angle de collision
                    # Cela garantit 90° minimum entre leurs trajectoires
                    
                    # Ajouter de la variabilité tout en maintenant la divergence
                    angle_variation1 = random.uniform(-25, 25)  # ±25° de variation
                    angle_variation2 = random.uniform(-25, 25)  # ±25° de variation
                    
                    # Angles de rebond divergents
                    rebound_angle1 = collision_angle + math.pi * 0.75 + math.radians(angle_variation1)  # ~135° + variation
                    rebound_angle2 = collision_angle + math.pi * 0.25 + math.radians(angle_variation2)  # ~45° + variation
                    
                    # Appliquer les nouvelles vitesses avec directions divergentes
                    player1.vx = math.cos(rebound_angle1) * bounce_speed
                    player1.vy = math.sin(rebound_angle1) * bounce_speed
                    player2.vx = math.cos(rebound_angle2) * bounce_speed
                    player2.vy = math.sin(rebound_angle2) * bounce_speed
                    
                    # Séparer les joueurs pour éviter l'interpénétration
                    # Vecteur de collision normalisé
                    nx = dx / distance
                    ny = dy / distance
                    
                    overlap = min_distance - distance
                    separation = overlap / 2
                    
                    player1.x -= nx * separation
                    player1.y -= ny * separation
                    player2.x += nx * separation
                    player2.y += ny * separation
    
    def check_target_collisions(self):
        """Vérifie si une cible touche l'extérieur du joueur (pas son centre)."""
        for player in self.players.values():
            # Ignorer les joueurs éliminés
            if player.is_eliminated:
                continue
                
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
                        
                        # Jouer le son de vol de ligne
                        self.sound_manager.play_line_steal()
                        
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
            # Ignorer les joueurs éliminés
            if player.is_eliminated:
                continue
                
            # Vérifier le franchissement de chaque ligne (cible possédée par d'autres joueurs actifs)
            for target in self.targets.values():
                if (target.owner_id is not None and 
                    target.owner_id != player.id and 
                    not self.players[target.owner_id].is_eliminated):
                    # Vérifier si le joueur a traversé cette ligne
                    if self.has_crossed_line(player, target):
                        # Le joueur franchit une ligne ennemie - il gagne la ligne
                        old_owner = target.owner_id
                        target.set_owner(player.id)
                        
                        # Jouer le son de vol de ligne
                        self.sound_manager.play_line_steal()
                        
                        # Ajouter des points au joueur qui a franchi
                        player.add_score(1)
                        
                        # Appliquer une réduction de puissance à l'ancien propriétaire (seulement s'il n'est pas éliminé)
                        if old_owner is not None and not self.players[old_owner].is_eliminated:
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
        
        # Mise à jour du timer
        if not self.game_ended:
            self.remaining_time = self.game_duration - (current_time - self.game_start_time)
            
            # Système d'accélération progressive toutes les 20 secondes
            elapsed_time = current_time - self.game_start_time
            acceleration_intervals_passed = int(elapsed_time // self.acceleration_interval)
            
            if acceleration_intervals_passed > self.last_acceleration_time:
                self.last_acceleration_time = acceleration_intervals_passed
                # Augmenter la vitesse de 15% à chaque intervalle
                self.speed_boost_factor += 0.15
                
                # Appliquer l'accélération à tous les joueurs actifs
                active_players = [p for p in self.players.values() if not p.is_eliminated]
                if active_players:
                    print(f"🚀 Accélération activée ! (x{self.speed_boost_factor:.1f}) - {len(active_players)} joueurs restants")
                    
                    for player in active_players:
                        # Augmenter la vitesse actuelle du joueur
                        current_speed = math.sqrt(player.vx * player.vx + player.vy * player.vy)
                        if current_speed > 0:
                            # Appliquer le boost de vitesse
                            boost_factor = 1.15  # 15% d'augmentation
                            player.vx *= boost_factor
                            player.vy *= boost_factor
                
                # Forcer la mise à jour de l'UI pour montrer l'accélération
                self.ui_needs_update = True
            
            # Alerte sonore pour les 3 dernières secondes
            if self.remaining_time <= 3.0 and self.remaining_time > 0 and not self.end_game_alert_played:
                self.sound_manager.play_end_game_alert()
                self.end_game_alert_played = True
                print("⚠️ ALERTE : 3 dernières secondes !")
            
            if self.remaining_time <= 0:
                self.remaining_time = 0
                self.game_ended = True
                self.determine_winner_by_time()
                self.ui_needs_update = True
        
        # Mise à jour des joueurs avec interactions (seulement si le jeu n'est pas terminé)
        if not self.game_ended:
            players_list = list(self.players.values())
            for player in players_list:
                player.update_position(1.0 / Config.FPS, players_list)
                player.update_power_reduction()
            
            # Gestion des collisions directes entre joueurs
            self.handle_player_collisions()
            
            # Vérification des collisions avec les cibles à chaque frame
            self.check_target_collisions()
            
            # Vérification du franchissement des lignes à chaque frame
            self.check_line_crossings()
        
        # Mise à jour des cibles (pour les effets visuels même quand le jeu est fini)
        for target in self.targets.values():
            target.update_visual_effects()
        
        # Mise à jour du système de confettis
        self.confetti_system.update(1.0 / Config.FPS)
        
        # Vérifier l'élimination des joueurs
        self.check_player_elimination()
        
        # Vérifier la condition de victoire
        self.check_victory_condition()
    
    def check_player_elimination(self):
        """Vérifie et élimine les joueurs qui n'ont plus de lignes."""
        for player in self.players.values():
            if not player.is_eliminated:
                if player.check_elimination(self.targets):
                    # Forcer la mise à jour de l'UI quand un joueur est éliminé
                    self.ui_needs_update = True
    
    def check_victory_condition(self):
        """Vérifie si un joueur a atteint la condition de victoire."""
        for player in self.players.values():
            if player.score >= Config.CONDITION_VICTOIRE:
                if not hasattr(self, 'victory_announced'):
                    print(f"Joueur {player.id + 1} remporte la partie avec {player.score} points !")
                    print("Appuyez sur Échap pour quitter ou fermez la fenêtre.")
                    self.victory_announced = True
                    self.game_ended = True  # Arrêter complètement le jeu
                    # Lancer les confettis de la couleur du gagnant
                    self.confetti_system.start_celebration(player.color, self.center_x, self.center_y)
                self.ui_needs_update = True  # Forcer la mise à jour de l'UI
    
    def determine_winner_by_time(self):
        """Détermine le gagnant quand le temps est écoulé."""
        if not hasattr(self, 'victory_announced'):
            # Trouver le joueur avec le score le plus élevé
            active_players = [p for p in self.players.values() if not p.is_eliminated]
            if active_players:
                winner = max(active_players, key=lambda p: p.score)
                self.winner_by_time = winner.id
                print(f"Temps écoulé ! Joueur {winner.id + 1} remporte la partie avec {winner.score} points !")
                print("Appuyez sur Échap pour quitter ou fermez la fenêtre.")
                # Lancer les confettis de la couleur du gagnant
                self.confetti_system.start_celebration(winner.color, self.center_x, self.center_y)
            else:
                print("Temps écoulé ! Aucun joueur actif.")
            self.victory_announced = True
    
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
        
        # Titre simple
        title_text = self.font_medium.render("BATAILLE", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(Config.LARGEUR // 2, 18))
        self.ui_surface.blit(title_text, title_rect)
        
        # Affichage du timer simple
        if hasattr(self, 'remaining_time'):
            minutes = int(self.remaining_time // 60)
            seconds = int(self.remaining_time % 60)
            
            if self.game_ended and hasattr(self, 'winner_by_time'):
                timer_text = "TEMPS ÉCOULÉ"
                timer_color = (255, 100, 100)
            else:
                timer_text = f"{minutes:02d}:{seconds:02d}"
                timer_color = (255, 255, 100) if self.remaining_time < 30 else (200, 200, 200)
            
            timer_surface = self.font_small.render(timer_text, True, timer_color)
            timer_rect = timer_surface.get_rect(center=(Config.LARGEUR // 2, 38))
            self.ui_surface.blit(timer_surface, timer_rect)
            

        
        # Les scores sont maintenant affichés près du cercle
    
    def draw_circle_side_scores(self):
        """Affiche les scores dans le coin supérieur gauche avec des points colorés."""
        # Position dans le coin supérieur gauche
        base_x = 30
        start_y = 100  # Juste sous la zone UI
        spacing = 35
        
        # Trier les joueurs par score (ordre décroissant)
        sorted_players = sorted(self.players.items(), key=lambda x: x[1].score, reverse=True)
        
        for i, (player_id, player) in enumerate(sorted_players):
            y_pos = start_y + i * spacing
            
            # Dessiner un point de couleur du joueur
            point_radius = 8
            point_color = player.color if not player.is_eliminated else (100, 100, 100)
            pygame.draw.circle(self.screen, point_color, (base_x, y_pos), point_radius)
            
            # Contour blanc pour une meilleure visibilité
            pygame.draw.circle(self.screen, (255, 255, 255), (base_x, y_pos), point_radius, 1)
            
            # Score avec la même couleur que le point
            score_text = str(player.score)
            text_color = player.color if not player.is_eliminated else (100, 100, 100)
            
            # Rendu et affichage du texte à côté du point
            score_surface = self.font_medium.render(score_text, True, text_color)
            self.screen.blit(score_surface, (base_x + 20, y_pos - 10))
    
    def draw_ui(self):
        """Dessine l'interface utilisateur optimisée."""
        # Recréer l'UI seulement si nécessaire ou toutes les secondes pour le timer
        current_time = time.time()
        if (self.ui_needs_update or self.ui_surface is None or 
            (hasattr(self, 'last_ui_update') and current_time - self.last_ui_update >= 1.0)):
            self.create_ui_surface()
            self.ui_needs_update = False
            self.last_ui_update = current_time
        
        # Dessiner la surface UI mise en cache (titre et timer seulement)
        self.screen.blit(self.ui_surface, (0, 0))
        
        # Dessiner les scores près du cercle
        self.draw_circle_side_scores()
    
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
        
        # Dessiner les confettis
        self.confetti_system.draw(self.screen)
        
        # Dessiner la popup du vainqueur si le jeu est terminé
        if self.game_ended:
            self.draw_winner_popup()
        
        # Dessiner l'interface utilisateur par-dessus
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_winner_popup(self):
        """Dessine la popup du vainqueur au centre du cercle."""
        # Déterminer le message du vainqueur
        winner_text = ""
        if hasattr(self, 'winner_by_time') and self.winner_by_time is not None:
            # Victoire par temps
            winner_player = self.players[self.winner_by_time]
            winner_text = f"VAINQUEUR: {winner_player.name.upper()}"
            score_text = f"Score: {winner_player.score}"
        else:
            # Victoire par score ou élimination
            active_players = [p for p in self.players.values() if not p.is_eliminated]
            if active_players:
                winner = max(active_players, key=lambda p: p.score)
                winner_text = f"VAINQUEUR: {winner.name.upper()}"
                score_text = f"Score: {winner.score}"
            else:
                winner_text = "PARTIE TERMINÉE"
                score_text = ""
        
        # Calculer la position de la popup (centre du cercle)
        popup_center_x = self.center_x
        popup_center_y = self.center_y
        
        # Dimensions de la popup
        popup_width = 300
        popup_height = 120
        popup_x = popup_center_x - popup_width // 2
        popup_y = popup_center_y - popup_height // 2
        
        # Dessiner le fond de la popup avec transparence
        popup_surface = pygame.Surface((popup_width, popup_height))
        popup_surface.set_alpha(220)  # Transparence
        popup_surface.fill((40, 40, 60))  # Fond sombre
        
        # Bordure
        pygame.draw.rect(popup_surface, (255, 255, 255), (0, 0, popup_width, popup_height), 3)
        
        # Texte du vainqueur
        winner_surface = self.font_medium.render(winner_text, True, (255, 255, 100))  # Jaune
        winner_rect = winner_surface.get_rect(center=(popup_width // 2, 30))
        popup_surface.blit(winner_surface, winner_rect)
        
        # Texte du score (si disponible)
        if score_text:
            score_surface = self.font_small.render(score_text, True, (255, 255, 255))
            score_rect = score_surface.get_rect(center=(popup_width // 2, 60))
            popup_surface.blit(score_surface, score_rect)
        
        # Instructions
        instruction_text = "Appuyez sur Échap pour quitter"
        instruction_surface = self.font_small.render(instruction_text, True, (200, 200, 200))
        instruction_rect = instruction_surface.get_rect(center=(popup_width // 2, 90))
        popup_surface.blit(instruction_surface, instruction_rect)
        
        # Dessiner la popup sur l'écran
        self.screen.blit(popup_surface, (popup_x, popup_y))
    
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
    print("Lancement de l'interface de configuration...")
    print()
    
    try:
        # Initialiser Pygame
        pygame.init()
        pygame.mixer.init()
        screen = pygame.display.set_mode((Config.LARGEUR, Config.HAUTEUR))
        pygame.display.set_caption("Battle Circle - Configuration")
        
        # Afficher l'écran de configuration
        config_screen = ConfigScreen(screen)
        game_config = config_screen.run()
        
        if game_config is None:
            # L'utilisateur a fermé la fenêtre pendant la configuration
            pygame.quit()
            return
        
        # Afficher le compte à rebours
        pygame.display.set_caption("Battle Circle - Préparez-vous!")
        countdown_screen = CountdownScreen(screen)
        countdown_screen.run()
        
        # Lancer le jeu avec la configuration personnalisée
        pygame.display.set_caption("Battle Circle - En cours...")
        game = BattleGame(config=game_config)
        game.run()
        
    except Exception as e:
        print(f"Erreur lors de l'exécution du jeu : {e}")
        pygame.quit()


if __name__ == "__main__":
    main()