# ♟ Chess App - Moteur d'échec en Python

Bienvenue dans **Chess App** : une application d'échecs développée en Python avec Tkinter !  
Une interface moderne, simple et élégante pour jouer aux échecs en solo.

## 🌐 Badges

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)

---


## 🎯 Fonctionnalités principales

- Interface Tkinter propre et réactive
- Plusieurs skins pour l'échiquier (Classique, Coloré, Bois)
- Mode de contrôle personnalisé : **Click Only**, **Drag Only**, **Click + Drag**
- Gestion complète des règles d'échecs : Roque, Prise en passant, Promotion, Échec, Échec et Mat, Pat
- Contrôle du temps (Bullet, Blitz, Rapide, Personnalisé)
- Historique de parties enregistré
- Possibilité de dessiner des flèches sur l'échiquier (clic droit)
- Fenêtre d'explication des règles du jeu
- Sauvegarde automatique des préférences utilisateur

> ⚠️ **Important :** Cette application est conçue pour un usage solo local. Pas de mode en ligne présent pour l'instant.

> ⚠️ **Astuce : Ajouter vos propres skins**
>
> Vous pouvez facilement ajouter de nouveaux skins à l'application !
>
> 1. Créez un nouveau dossier dans `skins/` (exemple : `skins/monstyle/`).
> 2. Ajoutez vos images de pièces dans ce dossier avec les noms suivants :
>     - `blanc_pion.png`, `noir_pion.png`
>     - `blanc_tour.png`, `noir_tour.png`
>     - `blanc_cavalier.png`, `noir_cavalier.png`
>     - `blanc_fou.png`, `noir_fou.png`
>     - `blanc_reine.png`, `noir_reine.png`
>     - `blanc_roi.png`, `noir_roi.png`
> 3. Ajoutez votre skin dans la variable `SKINS` de `ChessHMI.py` en suivant l'exemple des skins existants.

---

## 🚧 Version Exécutable (.exe)

Si vous ne souhaitez pas installer Python, une version **exécutable** est disponible :

- Rendez-vous dans la section [Releases](https://github.com/ton_pseudo/chess-game/releases)
- Téléchargez le fichier `ChessGame.exe`
- Lancez directement l'application sans installation préalable de Python

*(Packagé avec PyInstaller pour Windows)*

---

## 🚀 Lancer depuis les sources

1. Clonez le projet :

```bash
git clone https://github.com/ton_pseudo/chess-game.git
```

2. Lancez le jeu avec Python :

```bash
python MainMenu.py
```

---

## 📚 Structure du projet

```
Chess App/
├── ChessHMI.py
├── ChessRules.py
├── MainMenu.py
├── RulesWindow.py
├── selectionTemps.py
├── pieceEchec.py
├── plateau.py
├── theme_ihm.py
├── skins/
│   ├── classique/
│   ├── colore/
│   └── bois/
├── config.json (automatique)
├── README.md
```

---

## 💡 Prochaines évolutions possibles

- Ajouter un mode 2 joueurs local ou en ligne
- Ajouter un systeme elo 
- Ajouter une analyse de partie
- Ajouter un historique de partie
- Ajouter un systeme de compte 
- Ajouter une IA simple pour jouer contre l'ordinateur

---

## 💬 Contributions

Contributions bienvenues !
- Proposez des idées
- Signalez des bugs

---

---

## 🙌 Feedback bienvenu !

Vous aimez Chess App ou vous avez des idées pour l'améliorer ?

- ⭐ Laissez une star ⭐ sur le projet si vous l'appréciez !
- 🐛 Signalez un bug via les Issues GitHub
- 💬 Proposez des suggestions ou fonctionnalités via Issues ou Discussions

Merci d'utiliser **Chess App** ! Bonne partie ♟️.

