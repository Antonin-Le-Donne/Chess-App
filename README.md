# ♟ Chess App - Application d'Échecs en Python

Bienvenue dans **Chess Game** : une application d'échecs développée en Python avec Tkinter !  
Une interface moderne, simple et élégante pour jouer aux échecs en solo.

## 🌐 Badges

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)

## 🎯 Fonctionnalités principales

- Interface Tkinter propre et réactive
- Plusieurs skins pour l'échiquier (Classique, Coloré, Bois)
- Mode de contrôle personnalisé : **Click Only**, **Drag Only**, **Click + Drag**
- Gestion complète des règles d'échecs : Roque, Prise en passant, Promotion, Échec, Échec et Mat, Pat
- Contrôle du temps (Bullet, Blitz, Rapide, Personnalisé)
- Historique de parties enregistré
- Fenêtre d'explication des règles du jeu
- Sauvegarde automatique des préférences utilisateur

---

## 🚧 Version Exécutable (.exe)

Si vous ne souhaitez pas installer Python, une version **exécutable** est disponible :

- Rendez-vous dans la section [Releases](https://github.com/ton_pseudo/chess-game/releases)
- Téléchargez le fichier `ChessApp.exe`
- Lancez directement l'application sans installation préalable de Python

*(Packagé avec PyInstaller pour Windows)*

---

## 🚀 Lancer depuis les sources

1.1 Clonez le projet :

```bash
git clone https://github.com/ton_pseudo/chess-game.git
cd chess-game
```

ou

1.2 Télécharge le zip 

2. Lancez le jeu avec Python :

```bash
python MainMenu.py
```

---

## 📚 Structure du projet

```
chess-game/
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

Merci d'utiliser **Chess App** ! Bonne partie ♟️.

