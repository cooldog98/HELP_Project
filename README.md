# HELP_PROJECT

## Overview

HELP_PROJECT is a 2D platformer built using Python and the Pygame library. Players navigate through levels, encounter and defeat enemies, and aim to progress within the game world.
---
## 📂 Project Structure

```bash
palace_game/
├── bullet.py          # Defines the Bullet class for projectiles.
├── enemy.py           # Defines the Enemy_1 class for enemy characters.
├── game_platform.py   # Defines the GamePlatform class for handling the game environment.
├── game.py            # Contains the main Game class, managing game state and logic.
├── health.py          # Defines the HealthBar class for displaying player health.
├── main.py            # The primary script to launch the Palace Game.
├── make_graph.py      # A utility script for analyzing game data and generating visualizations.
├── player.py          # Defines the Player class, handling player movement and actions.
└── start_screen.py    # Defines the StartScreen class for the initial game menu.
```
---
## 📦 Installation Guide

To run Palace Game on your system, follow these steps:

**Prerequisites:**

**Python 3.13.0** installed:

If you don't have Python installed, download it from the official Python website (https://www.python.org/downloads/) and follow the installation instructions.

Install Dependencies:

Palace Game relies on the Pygame library. To install it, open your terminal or command prompt, navigate to the directory containing the game files (where main.py is located), and run:

 ```bash
pip install pygame
 ```
This command will download and install Pygame.

🚀 Getting Started
Navigate to the Project Directory: Open your terminal or command prompt and go to the directory where you have saved the game files (including main.py).

Run the Game: Execute the main script using Python:

 ```bash
python3 main.py
 ```
 Press Enter after typing the command. The Palace Game window should open, and you can start playing.
---
Game Controls (Inferred from Code - May Vary)

Movement: Likely uses A to Left and D to Right.
Jump: Likely uses Spacebar.
Shoot: Based on the Player and Bullet classes, there is likely a key to trigger shooting (use enter).
Out: use esc to quit the game.

To conquer each level, you have to arrive at this destination.
To triumph in each phase, you're required to make it to this location.
![chack point.png](chack%20point.png)

Refer to in-game instructions or experiment to confirm the exact controls.
---
Data Analysis (make_graph.py)
The make_graph.py script is a separate tool for analyzing game data, assuming the game collects and stores data in a data_record.csv file.

To Use the Data Analysis Tool:

Ensure that a data_record.csv file exists in the same directory as make_graph.py (or the script is configured to find it). This file should contain game data, including columns like Level, Player Name, Time (s), Enemies Defeated, HP, and Distance.

Run the script from your terminal:

 ```bash
python3 make_graph.py
 ```
---
The script will:
Load the data from data_record.csv.
Perform analysis on level completion.
Generate and save several plots (distribution of levels completed, distance traveled per level, time vs. enemies defeated, completion rate per level, and a correlation matrix of Avg_Time, Enemies Defeated, Distance, HP, and Completions - note: Avg_Time and Completions need to be present or derivable from your data).
Save the raw data and analysis results to CSV files in a data directory.
