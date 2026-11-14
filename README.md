# 🎮 Tetris – Python

A classic **Tetris game** built with Python and Pygame. The game features seven standard Tetromino shapes, real-time movement and rotation, collision detection, line clearing, dynamic difficulty progression, player score tracking, and an all-time leaderboard visualization.

## ✨ Features

- **Classic Tetris Gameplay:** Play with all seven standard Tetromino shapes (I, O, T, S, Z, J, L).
- **Movement & Rotation:** Move pieces horizontally, accelerate their descent, and rotate them.
- **Collision Detection:** Pieces interact with the game boundaries and previously placed blocks.
- **Line Clearing:** Complete horizontal rows to clear them and earn points.
- **Dynamic Difficulty:** The falling speed increases as your score grows.
- **Hard Drop:** Instantly drop the current piece to its lowest available position.
- **Pause System:** Pause and resume the game whenever needed.
- **Player Identification:** Enter a player name before starting.
- **Persistent Score Records:** Save game results locally in a JSON file.
- **Leaderboard Visualization:** Display the highest recorded score for each player using Matplotlib.

## 🕹️ Controls

| Key | Action |
|---|---|
| ← Left Arrow | Move piece left |
| → Right Arrow | Move piece right |
| ↓ Down Arrow | Move piece down |
| ↑ Up Arrow | Rotate piece clockwise |
| Space | Hard drop |
| P | Pause / Resume |
| Enter | Confirm player name |

## 🏆 Scoring System

Points are awarded according to the number of rows cleared simultaneously.

| Lines Cleared | Points |
|---|---:|
| 1 Line | 100 |
| 2 Lines | 300 |
| 3 Lines | 500 |
| 4 Lines | 800 |

The falling speed increases as the player's score increases, making the game progressively more challenging.

## 🛠️ Technologies Used

- **Python** – Core programming language
- **Pygame** – Game window, rendering, input handling, and game loop
- **Matplotlib** – Leaderboard visualization
- **JSON** – Persistent score storage
- **Random** – Random Tetromino generation
- **Datetime** – Timestamping game records

## 📂 Project Structure

```text
Tetris/
│
├── main.py
├── tetris-records.json   # Generated after the first game
└── README.md
```

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd Tetris
```

### 2. Install dependencies

```bash
pip install pygame matplotlib
```

### 3. Run the game

```bash
python main.py
```

Enter your player name and start playing!

## 📊 Score Records

Game results are stored in `tetris-records.json`.

Each record contains:
- The date and time of the game.
- The player's name.
- The score achieved.

After the game ends, the program processes the saved records, sorts the scores, identifies each player's highest score, and generates a leaderboard chart.

## 🧠 Implementation Highlights

Some of the programming concepts used in this project include:

- Object-oriented programming through the `Tetromino` class.
- Two-dimensional lists for representing the game grid.
- Dictionaries for tracking locked block positions.
- Matrix transformations for piece rotation.
- Collision detection and position validation.
- File handling and JSON serialization.
- Sorting algorithms, including a manually implemented Bubble Sort.
- Data visualization using Matplotlib.

---

**Built with Python 🐍**

A personal implementation of the classic Tetris game.