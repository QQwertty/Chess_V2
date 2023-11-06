import numpy as np
import copy as cp
import io
import time

# Create bitboards for each type of piece for both colors
# These bitboards will represent the position of each piece type
piece_bitboards = [
# w_pawn 0
int("0000000000000000000000000000000000000000000000001111111100000000", 2),
#b_pawn 1
int("0000000011111111000000000000000000000000000000000000000000000000", 2),

#w_rook 2
int("0000000000000000000000000000000000000000000000000000000010000001", 2),
#b_rook 3
int("1000000100000000000000000000000000000000000000000000000000000000", 2),

#w_knight 4
int("0000000000000000000000000000000000000000000000000000000001000010", 2),
#b_knight 5
int("0100001000000000000000000000000000000000000000000000000000000000", 2),

#w_bishop 6
int("0000000000000000000000000000000000000000000000000000000000100100", 2),
#b_bishop 7
int("0010010000000000000000000000000000000000000000000000000000000000", 2),

#w_queen 8
int("0000000000000000000000000000000000000000000000000000000000010000", 2),
#b_queen 9
int("0001000000000000000000000000000000000000000000000000000000000000", 2),

#w_king 10
int("0000000000000000000000000000000000000000000000000000000000001000", 2),
#b_king 11
int("0000100000000000000000000000000000000000000000000000000000000000", 2)
]

# Create an empty bitboard 1: empty 0: piece present
empty_board = int("0000000000000000111111111111111111111111111111110000000000000000", 2)


# Define function that prints a bitboard
def print_bitboard(bitboard):
    board = '{:064b}'.format(bitboard)
    for i in range(7, -1, -1):
        row = board[i * 8:(i + 1) * 8]
        print(" ".join(row))
    

""" 
This class will store the information about the current game state. It will determine legal moves.
It will take an optional starting pos in fen notation. If start_pos is empty, it will use standard starting pos.
"""
class GameState():

    def __init__(self, start_pos=None):
        
        # Board is represented by 2D numpy array
        # White Pieces will be capital chars: P, R, N, B, K, Q
        # Black Pieces will be lowercase chars: p, r, n, b, k, q
        self.board = np.array([[None] * 8 for _ in range(8)])
        self.white_to_move = True # White's move -> True, Black's move -> False
        self.last_move = None # stored as [(x,y), piece_type, (x,y)]
        self.can_castle = "KQkq" # K means white can kingside castle, Q means black can queenside castle, etc.
        self.starting_pos = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.white_promote = False # Used to tell ChessMain to display options for promotion
        self.black_promote = False
        self.positions = {"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR KQkq": 1} # Used to check for 3-fold repetition


    def place_pieces_from_fen(self):
        """
        Takes an string representation of the chessboard in FEN notation and 
        sets up the chess board array accordingly
        """
        fen_board = self.starting_pos.split(" ")[0]
        file = 0
        rank = 0

        for symbol in fen_board:

            if symbol == '/':
                file = 0
                rank += 1
            else:
                if symbol.isnumeric():
                    file += int(symbol)
                else:
                    # Add pieces to 2D array representation of the board
                    self.board[rank][file] = symbol

                    file += 1


    def piece_matches_turn(self, rank, file):
        """
        Takes in the position (rank, file) of a piece
        outputs if that piece's color matches the turn to move (piece is white and it is white to move -> returns True)
        """

        # If both pieces are white or both pieces are not white (black) return true
        return self.white_to_move == self.board[rank][file].isupper()


    def make_move(self, old_pos, new_pos):
        # Unpack the piece's old and new position
        old_rank, old_file = old_pos
        new_rank, new_file = new_pos

        # Symbol representing the piece that is moving
        old_square = self.board[old_rank][old_file]
        # Symbol representing the square that is being moved to
        new_square = self.board[new_rank][new_file]
        

        # Check if move is en passant or a promotion
        if self.board[old_rank][old_file] == "P" or self.board[old_rank][old_file] == "p":

            # If new position is empty and the file pawn is in is different, move is an en passant
            if self.board[new_rank][new_file] == None and new_file != old_file:
                self.board[old_rank][new_file] = None

            # Check for promotion
            elif new_rank == 0:
                self.board[old_rank][old_file] = None
                self.white_promote = True # Used in ChessMain to update the display and give selection
            elif new_rank == 7:
                self.board[old_rank][old_file] = None
                self.black_promote = True # Used in ChessMain to update the display and give selection
        
        # Check if move is castling
        elif self.board[old_rank][old_file] == "K":

            if "K" in self.can_castle:
                # updates the rooks position
                self.castling_move(old_rank, old_file, new_file)
                self.can_castle = self.can_castle.replace("KQ", "")

            elif "Q" in self.can_castle:
                # updates the rooks position
                self.castling_move(old_rank, old_file, new_file)
                self.can_castle = self.can_castle.replace("KQ", "")

        elif self.board[old_rank][old_file] == "k":
            # Checks if black king can kingside castle
            if "k" in self.can_castle:
                # updates the rooks position
                self.castling_move(old_rank, old_file, new_file)
                self.can_castle = self.can_castle.replace("kq", "")
            elif "q" in self.can_castle:
                # updates the rooks position
                self.castling_move(old_rank, old_file, new_file)
                self.can_castle = self.can_castle.replace("kq", "")
       
        # Checks if rook moved (cannot castle on that side)
        if (self.white_to_move and ("K" in self.can_castle or "Q" in self.can_castle)) or (not self.white_to_move and ("k" in self.can_castle or "q" in self.can_castle)):
            if self.board[old_rank][old_file] == "R" or self.board[old_rank][old_file] == "r":
                if old_pos == (0, 0):
                    self.can_castle = self.can_castle.replace("q", '')
                elif old_pos == (0, 7):
                    self.can_castle = self.can_castle.replace("k", '')
                elif old_pos == (7, 0):
                    self.can_castle = self.can_castle.replace("Q", '')  
                elif old_pos == (7, 7):
                    self.can_castle = self.can_castle.replace("K", '')
        
        # Makes the given move
        self.board[new_rank][new_file] = self.board[old_rank][old_file]
        self.board[old_rank][old_file] = None

        # If player's king is in check after that player moved, undo the move and ask for a new move
        if self.king_in_check(self.white_to_move):
            self.board[old_rank][old_file] = old_square
            self.board[old_rank][old_file] = self.board[new_rank][new_file]
            self.board[new_rank][new_file] = new_square
            return
        
        # Add position to the positions dictionary
        fen_pos = self.board_to_fen()
        if fen_pos not in self.positions:
            self.positions[self.board_to_fen()] = 1
        else:
            self.positions[self.board_to_fen()] += 1

        # Toggle the turn
        self.white_to_move = not self.white_to_move
    

    def castling_move(self, old_rank, old_file, new_file):
        # If king castled king side
        if old_file - new_file == -2:
            self.board[old_rank][old_file + 1] = self.board[old_rank][7]
            self.board[old_rank][7] = None
        # If king castled queen side
        if old_file - new_file == 2:
            self.board[old_rank][old_file - 1] = self.board[old_rank][0]
            self.board[old_rank][0] = None

    
    def generate_moves(self, piece_pos, danger=False):
        """
        Generates the moves for a given piece
        if danger is True, the function is being called to check for squares under attack, so forward pawn moves should be excluded
        """
        rank, file = piece_pos
        piece_type = self.board[rank][file]

        if piece_type == "p" or piece_type == "P":
            moves = self.generate_pawn_moves(piece_pos, piece_type, danger)

        elif piece_type == "r" or piece_type == "R":
            moves = self.generate_rook_moves(piece_pos, piece_type)

        elif piece_type == "n" or piece_type == "N":
            moves = self.generate_knight_moves(piece_pos, piece_type)

        elif piece_type == "b" or piece_type == "B":
            moves = self.generate_bishop_moves(piece_pos, piece_type)

        elif piece_type == "q" or piece_type == "Q":
            moves = self.generate_queen_moves(piece_pos, piece_type)

        elif piece_type == "k" or piece_type == "K":
            moves = self.generate_king_moves(piece_pos, piece_type)

        return moves
    

    def generate_pawn_moves(self, piece_pos, piece_type, danger=False):
        """ Pawn's Moves:
        1 square forward if it is empty and 2 squares forward if the 2 squares infront are empty and it is the pawns first move
        Pawns can capture on diagonals and canpture with en passant (diagonally if the enemy pawn moved 2 squares in the last move)
        If danger is True, the function is being called to check for squares under attack, so forward pawn moves should be excluded
        """
        rank, file = piece_pos
        moves = [] # Store the piece's possible moves
        last_move = self.last_move # stored as [(x,y), piece_type, (x,y)]

        # White moves -1 squares, black moves 1 square
        i = -1 if self.white_to_move else 1

        # If danger is false, normal pawn moves are calculated
        # Pawn can move 1 square forward if it is empty and inbounds
        if not danger:
            if 7 >= rank + i >= 0:
                if self.board[rank + i][file] == None:
                    moves.append((rank + i, file))

        # Pawn can move 2 squares forward if it hasn't moved and 2 squares infront are empty
        if not danger:
            if (self.white_to_move and rank == 6) or (not self.white_to_move and rank == 1):
                if self.board[rank + i][file] == None and self.board[rank + i * 2][file] == None:
                    moves.append((rank + i * 2, file))

        # Pawn can take on diagonals if it is inbounds
        for j in [-1, 1]:
            if 7 >= rank + i >= 0 and 7 >= file + j >= 0:
                if self.board[rank + i][file + j] is not None and not self.piece_matches_turn(rank + i, file + j):
                    moves.append((rank + i, file + j))

        # Can en-passant if: 
        # last move was made by a pawn
        if last_move is not None:
            if last_move[1] in 'Pp':
                old_rank, old_file = last_move[0]
                new_rank, new_file = last_move[2]

                # If the pawn moved 2 square
                if (old_rank - new_rank) ** 2 == 4:

                    # If the pawn moving is on the right of that pawn
                    if file + 1 <= 7:
                        if self.board[rank][file + 1] == self.board[new_rank][new_file]:
                            moves.append((rank + i, new_file))

                    # If the pawn moving is on the left of that pawn
                    if file - 1 >= 0:
                        if self.board[rank][file - 1] == self.board[new_rank][new_file]:
                            moves.append((rank + i, new_file))

        return moves
    

    def generate_rook_moves(self, piece_pos, piece_type):
        
        """ Rook's Moves:
        Check column/row until an obstruction is encountered.
        If the obstruction is an opponent's piece, include it as a valid move (capture).
        """
        moves = []
        possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1)] # Possible standard rook moves
        # Rook is white if variable is true, else black
        white = True if piece_type.isupper() else False

        # For each standard move, increment by the move until an enemy, ally, or boundry is reached
        # Add the move to the moves list (including capture if piece is an enemy) then reset the peice's position
        for i, j in possible_moves:
            rank, file = piece_pos
            while True:
                rank += i
                file += j
                if 0 <= rank < 8 and 0 <= file < 8:

                    # If a piece is in the way
                    if self.board[rank][file] is not None:
                        
                        # Add move if piece is an enemy piece
                        if not self.piece_matches_turn(rank, file):
                            moves.append((rank, file))
                        # Enemy/ally piece is reached
                        break

                    # If no piece is in the way append move
                    else:
                        moves.append((rank, file))

                # Edge of the board is reached
                else:
                    break

        return moves        
    
    def generate_knight_moves(self, piece_pos, piece_type):
        """ 
        Knight can move and take in an L shape and can jump over pieces
        """
        moves = []
        # Possible standard horse moves
        possible_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

        # Loop through possible moves
        # If destination is empty or an enemy piece, add move
        for i, j in possible_moves:
            rank, file = piece_pos
            rank += i
            file += j
            if 0 <= rank < 8 and 0 <= file < 8:
                # If square is empty, append move
                if self.board[rank][file] is None:
                    moves.append((rank, file))
                # If enemy on square, append move
                elif not self.piece_matches_turn(rank, file):
                    moves.append((rank, file))

        return moves
    
    def generate_bishop_moves(self, piece_pos, piece_type):
        """Bishop's Moves:
        Check diagonal positions until an obstruction is encountered.
        If the obstruction is an opponent's piece, include it as a valid move (capture).
        """

        moves = []
        # Possible standard bishop moves
        possible_moves = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        # For each standard move, increment by the move until an enemy, ally, or boundry is reached
        # Add the move to the moves list (including capture if piece is an enemy) then reset the peice's position
        for i, j in possible_moves:
            rank, file = piece_pos
            while True:
                rank += i
                file += j
                if 0 <= rank < 8 and 0 <= file < 8:
                    if self.board[rank][file] is not None:

                        # Add move if piece is opposite color
                        if not self.piece_matches_turn(rank, file):
                            moves.append((rank, file))
                        # Enemy/ally piece is reached
                        break

                    # If no piece is in the way append move        
                    else:
                        moves.append((rank, file))

                # Edge of the board is reached
                else:
                    break

        return moves
    
    
    def generate_queen_moves(self, piece_pos, piece_type):
        """ 
        Calculates and returns all possible moves for a queen on the chessboard.
        ueens can move in any direction (horizontally, vertically, or diagonally) until they
        encounter an obstacle (another piece or the edge of the board)
        """
        moves = []

        # Possible standard queen moves
        possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        # For each standard move, increment by the move until an enemy, ally, or boundry is reached
        # Add the move to the moves list (including capture if piece is an enemy) then reset the peice's position
        for i, j in possible_moves:
            rank, file = piece_pos
            while True:
                rank += i
                file += j
                if 0 <= rank < 8 and 0 <= file < 8:
                    if self.board[rank][file] is not None:

                        # Add move if piece is opposite color
                        if not self.piece_matches_turn(rank, file):
                            moves.append((rank, file))
                        # Enemy/ally piece is reached
                        break
                    
                    # Square is empty
                    else:
                        moves.append((rank, file))

                # Boundry is reached
                else:
                    break

        return moves
    
    def generate_king_moves(self, piece_pos, piece_type):
        """ 
        King can move 1 square in any direction if they are not under attack
        King can castle (move 2 square either direction and the rook jumps to the opposite side of the king)
        """
        moves = []

        # Possible standard queen moves
        possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        tic = time.perf_counter()
        danger_squares = self.find_danger_squares(self.white_to_move, piece_pos)
        toc = time.perf_counter()
        print(f"Found danger squares in {toc - tic:0.6f} seconds")

        # Make each standard move and append it if square is an enemy or empty
        for i, j in possible_moves:
            rank, file = piece_pos
            rank += i
            file += j

            if 0 <= rank < 8 and 0 <= file < 8:
                # If square is an enemy or is empty, append move
                if self.board[rank][file] is None or not self.piece_matches_turn(rank, file):
                    if (rank, file) not in danger_squares:
                        moves.append((rank, file)) 

        rank, file = piece_pos

        # Check if king can king side castle
        if (self.white_to_move and "K" in self.can_castle) or (not self.white_to_move and "k" in self.can_castle):

            if self.board[rank][file + 1] == None and self.board[rank][file + 2] == None:

                # Cannot castle if either of the 2 squares on the right are under attack
                if (rank, file + 2) not in danger_squares and (rank, file + 1) not in danger_squares:
                    moves.append((rank, file + 2))

        # Check if king can queen side castle
        if (self.white_to_move and "Q" in self.can_castle) or (not self.white_to_move and "q" in self.can_castle):

            if self.board[rank][file - 1] == None and self.board[rank][file - 2] == None and self.board[rank][file - 3] == None:

                # Check if king can kingside castle
                if (rank, file - 2) not in danger_squares and (rank, file - 1) not in danger_squares:
                    moves.append((rank, file - 2))

        return moves


    def find_danger_squares(self, white, king_pos, save_king=False):
        # Find all squares that are under attack
        danger_squares = []

        king_r, king_f = king_pos

        # Removes the king when generating moves to accurately caputure danger squares
        king = self.board[king_r][king_f]
        self.board[king_r][king_f] = None

        # Loops through every square in the board
        for r, rank in enumerate(self.board):
            for f, piece in enumerate(rank):
                # Generate only enemy and non-king moves
                if piece is not None:
                    if (white and piece.islower()) or (not white and piece.isupper()):
                        if piece != "K" and piece != "k":

                            danger_moves = self.generate_moves((r,f), True)

                            # Add unique enemy moves to danger squares
                            for ele in danger_moves:
                                if ele not in danger_squares:
                                    danger_squares.append(ele)

        # Place the king back on the board
        self.board[king_r][king_f] = king

        # If save_king is true, return the king position to help with efficiency
        if save_king:
            return danger_squares, king_pos
        
        return danger_squares


    def king_in_check(self, white):
        king_pos = self.find_king(white)

        danger_squares = self.find_danger_squares(white, king_pos)

        # If king is in a square that is under attack return True
        if king_pos in danger_squares:
            return True

        return False
    

    def king_in_checkmate(self, white):
        """
        For every piece that is the correct color and not the king,
        Generate their moves, make that move in the temporary board
        If the move takes the king out of check, it is not checkmate
        If no moves take the king out of check, it is checkmate
        """

        # Create a temporary board and loop through pieces
        for r, rank in enumerate(self.board):
            for f, piece in enumerate(rank):
                if self.board[r][f] is not None:
                    if self.piece_matches_turn(r,f):
                        # Generate the ally piece's moves
                        moves = self.generate_moves((r,f))

                        for move in moves:
                            # Make a deep copy of the game state
                            temp_game_state = cp.deepcopy(self)
                            temp_game_state.make_move((r, f), move)

                            # If the king is not in check after the move in the temp game state, it is not checkmate
                            if not temp_game_state.king_in_check(white):
                                return False

        return True
        
    
    def find_king(self, white):

        # search for white king from the bottom up
        if white:
            for r in range(7, -1, -1):
                for f in range(8):
                    if self.board[r][f] == 'K':
                        return (r, f)
        # search for the black king form the top down
        else:
            for r in range(8):
                for f in range(8):
                    if self.board[r][f] == 'k':
                        return (r, f)
                                        

    def is_stalemate(self, white):
        # Loop through the board
        for r in range(8):    
            for f, piece in enumerate(self.board[r]):
                if piece is not None:
                    if self.piece_matches_turn(r,f):
                        # If any ally has moves, it is not stalemate
                        if self.generate_moves((r, f)):
                            return False

        return True
    

    def board_to_fen(self):
        # Use StringIO to build string more efficiently than concatenating
        with io.StringIO() as s:
            for row in self.board:
                empty = 0
                for cell in row:
                    if cell:
                        if empty > 0:
                            s.write(str(empty))
                            empty = 0
                        s.write(cell)
                    else:
                        empty += 1
                if empty > 0:
                    s.write(str(empty))
                s.write('/')
            # Move one position back to overwrite last '/'
            s.seek(s.tell() - 1)
            # If you do not have the additional information choose what to put
            if self.white_to_move:
                s.write(' {}'.format(self.can_castle))
            else:
                s.write(' {}'.format(self.can_castle))
            return s.getvalue()

                
    def is_threefold_repetition(self):
        fen_pos = self.board_to_fen()

        # Check if the FEN position is in the dictionary
        if fen_pos in self.positions:
            # If it's been reached 3 or more times, it's threefold repetition
            if self.positions[fen_pos] >= 3:
                return True

        return False