# 🎮 Bataille de Lignes sur Cercle - Exécutable v1.0

## 📋 Informations sur l'Exécutable

- **Nom** : `Bataille-Cercle-v1.0.exe`
- **Version** : 1.0
- **Taille** : ~50-60 MB (inclut Python + Pygame + NumPy)
- **Compatibilité** : Windows 10/11 (64-bit)
- **Dépendances** : Aucune (tout est inclus)

## 🚀 Utilisation

1. **Double-cliquez** sur `Bataille-Cercle-v1.0.exe`
2. Le jeu se lance directement avec l'interface de configuration
3. Aucune installation ni dépendance requise !

## ⚡ Performance

- **Démarrage** : 2-3 secondes (chargement initial)
- **Gameplay** : 60 FPS constants
- **Mémoire** : ~100-150 MB pendant l'exécution

## 🔧 Recréation de l'Exécutable

Si vous voulez recréer l'exécutable à partir du code source :

### Option 1 : Script Automatique
```batch
create_executable.bat
```

### Option 2 : Commande Manuelle
```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name "Bataille-Cercle-v1.0" battle_circle.py
```

L'exécutable sera créé dans le dossier `dist/`

## 📁 Structure des Fichiers

```
Battle-Game/
├── battle_circle.py          # Code source principal
├── README.md                 # Documentation complète
├── create_executable.bat     # Script de création d'exécutable
├── .gitignore               # Fichiers Git à ignorer
├── build/                   # Fichiers temporaires (ignorés)
├── dist/                    # Exécutable généré (ignoré)
└── *.spec                   # Configuration PyInstaller (ignoré)
```

## ⚠️ Notes

- L'exécutable est autonome et portable
- Première exécution peut être plus lente (initialisation)
- Antivirus peuvent analyser le fichier (normal pour les exécutables Python)
- Compatible uniquement Windows 64-bit

## 🎮 Profitez du Jeu !

L'exécutable contient exactement les mêmes fonctionnalités que la version Python :
- Interface de configuration complète
- Système audio synthétique
- Physique de collision avancée
- Animations et effets visuels
- Support multi-joueurs (2-4)
- Optimisé pour enregistrement vidéo 9:16