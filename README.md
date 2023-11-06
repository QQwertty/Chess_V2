Chess engine works and all edge cases have been tested. Stalemate, check, and checkmate all work. Three-fold repetion is implemented and works.
Move generation for all the pieces works, but generates moves that are filtered out in the make_move method.
This is a flaw that will have to be addressed as an AI should not have the choice to make those moves.
If a MinMax ai is to be implemented, the engine will have to be extremely efficient.