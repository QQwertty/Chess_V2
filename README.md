Chess engine works and all edge cases have been tested. Stalemate, check, and checkmate all work. Three-fold repetion is implemented.
Move generation for all the pieces works, but has room for improvement.
Readability, variable naming, efficiency, redundancy, and more can all be improved.
If a MinMax ai is to be implemented, the engine will have to be extremely efficient.

POSSIBLE IMPROVEMENTS:

Save and update danger_squares after each move instead of finding the squares after each move.
Look at previous move, undo it, find the squares that piece attack, remove them, then redo move, recalculate the attack squares and add them back.
If multiple pieces attack the same square and that piece's moves are undone, then a square that is under attack by a different piece will not be under attack.

Change the generation of pawn moves because it is bulky and has a lot of redundancy.

Replace lists with arrays where ever possible.