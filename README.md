# Chess PNG Solver

Automatically plays chess for you, using basic image recognition to determine the position on the board, and determine the next best move.

- Implemented in Python3
- Chess Engine: Stockfish

### General Disclaimer

- This program is intended for educational purposes only. It should not be used to gain an unfair competitive advantage!

- I used this project to teach myself basic techniques of image recognition, 
and because I was curious how fast a computer could evaluate a chess position given only an image.


## Usage

```
This program uses basic PNG matching to evaluate your position on the board. 
I initially tested using the very popular chess.com standard board theme on a 13.3-inch (2560 x 1600).

To add support for additional skins you will need to build PNG equivalents in both the pieces/markers/boards directories.
```

1. Size the board on your screen as large as possible. With all positions set to standard start position. 
Run board.py, and check if the position is correctly printed out (Forsyth–Edwards Notation). Keep resizing the board until the below is displayed.

White orientation:

```
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -
```

2. Run game.py to start playing.

## Demo









