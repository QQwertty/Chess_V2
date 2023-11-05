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


""" class Board(piece_bitboards, empty_board):
    
    def __init__(self):
        self.piece_bitboards = piece_bitboards
        self.turn = True # Player turn true = white false = black
        self.start_pos = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" # Fen board representing starting position """
        



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
        self.board = np.array([[None, None, None, None, None, None, None, None], 
                               [None, None, None, None, None, None, None, None], 
                               [None, None, None, None, None, None, None, None],
                               [None, None, None, None, None, None, None, None],
                               [None, None, None, None, None, None, None, None], 
                               [None, None, None, None, None, None, None, None], 
                               [None, None, None, None, None, None, None, None],
                               [None, None, None, None, None, None, None, None]])
        self.white_to_move = True
        self.last_move = None # stored as [(x,y), piece_type, (x,y)]
        self.can_castle = "KQkq" # K means white can kingside castle, Q means black can queenside castle, etc.
        self.starting_pos = "4k3/PR6/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.white_promote = False
        self.black_promote = False
        self.positions = {"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR KQkq": 1} # Used to check for 3-fold repetition


    # Input FEN -> place pieces in the chess board
    def place_pieces_from_fen(self):

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
        # Takes piece position and tells if that piece is white or not
        piece_type = self.board[rank][file]
        white = True if piece_type.isupper() else False

        # If both pieces are white or both pieces are not white (black) return true
        if self.white_to_move == white:
            return True
        
        return False



    def make_move(self, old_pos, new_pos):
        old_rank, old_file = old_pos
        old_square = self.board[old_rank][old_file]
        new_rank, new_file = new_pos
        
        white = True if self.board[old_rank][old_file].isupper() else False

        # If pawn took with en passant or can promote
        if self.board[old_rank][old_file] == "P" or self.board[old_rank][old_file] == "p":
            if self.board[new_rank][new_file] == None and new_file != old_file:
                self.board[old_rank][new_file] = None

            # If piece can promote
            elif new_rank == 0:
                self.board[old_rank][old_file] = None
                self.white_promote = True
            elif new_rank == 7:
                self.board[old_rank][old_file] = None
                self.black_promote = True

        if white and "K" in self.can_castle:
            if self.board[old_rank][old_file] == "K":
                self.castling_move(old_rank, old_file, new_file)
                self.can_castle = self.can_castle.replace("K", "")
        if white and "Q" in self.can_castle:
            if self.board[old_rank][old_file] == "K":
                self.castling_move(old_rank, old_file, new_file)
                self.can_castle = self.can_castle.replace("Q", "")
        if not white and "k" in self.can_castle:
            if self.board[old_rank][old_file] == "k":
                self.castling_move(old_rank, old_file, new_file)
                self.can_castle = self.can_castle.replace("k", "")
        if not white and "q" in self.can_castle:
            if self.board[old_rank][old_file] == "k":
                self.castling_move(old_rank, old_file, new_file)
                self.can_castle = self.can_castle.replace("q", "")

        
        # If rook moved (cannot castle on that side)
        if (white and ("K" in self.can_castle or "Q" in self.can_castle)) or (not white and ("k" in self.can_castle or "q" in self.can_castle)):
            if self.board[old_rank][old_file] == "R" or self.board[old_rank][old_file] == "r":
                if old_pos == (0, 0):
                    self.can_castle = self.can_castle.replace("q", '')
                elif old_pos == (0, 7):
                    self.can_castle = self.can_castle.replace("k", '')
                elif old_pos == (7, 0):
                    self.can_castle = self.can_castle.replace("Q", '')  
                elif old_pos == (7, 7):
                    self.can_castle = self.can_castle.replace("K", '')
        
        self.board[new_rank][new_file] = self.board[old_rank][old_file]
        self.board[old_rank][old_file] = None

        if self.king_in_check(white):
            self.board[old_rank][old_file] = old_square
            self.board[old_rank][old_file] = self.board[new_rank][new_file]
            self.board[new_rank][new_file] = None
            return
        
        # Add position to the positions dict
        fen_pos = self.board_to_fen()
        if fen_pos not in self.positions:
            self.positions[self.board_to_fen()] = 1
        else:
            self.positions[self.board_to_fen()] += 1

        # Toggle the turn
        self.white_to_move = not self.white_to_move
    

    def castling_move(self, old_rank, old_file, new_file):
        if old_file - new_file == -2:
            self.board[old_rank][old_file + 1] = self.board[old_rank][7]
            self.board[old_rank][7] = None
        # If king castled queen side
        if old_file - new_file == 2:
            self.board[old_rank][old_file - 1] = self.board[old_rank][0]
            self.board[old_rank][0] = None

    
    def generate_moves(self, piece_pos, danger=False):

        rank, file = piece_pos
        piece_type = self.board[rank][file]
        moves = []

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
        rank, file = piece_pos
        moves = []
        last_move = self.last_move # stored as [(x,y), piece_type, (x,y)]

        # Generate white pawn moves
        # If danger is false, normal pawn moves are calculated
        if not danger:
            if piece_type.isupper():
                # Pawn can move 1 square forward if it is empty and inbounds
                if rank - 1 >= 0:
                    if self.board[rank - 1][file] == None:
                        moves.append((rank - 1, file))

                # Pawn can move 2 squares forward if it hasn't moved and 2 squares infront are empty
                if rank == 6:
                    if self.board[rank - 1][file] == None and self.board[rank - 2][file] == None:
                        moves.append((rank - 2, file))

                # Pawn can take on diagonals if it is inbounds
                if rank - 1 >= 0 and file - 1 >= 0:
                    if self.board[rank - 1][file - 1] is not None and self.board[rank - 1][file - 1].islower():
                        moves.append((rank - 1, file - 1))
                        
                if rank - 1 >= 0 and file + 1 <= 7:
                    if self.board[rank - 1][file + 1] is not None and self.board[rank - 1][file + 1].islower():
                        moves.append((rank - 1, file + 1))

                # Can en-passant if: last move was made by a pawn
                if last_move is not None:
                    if last_move[1] == 'p':
                        old_rank, old_file = last_move[0]
                        new_rank, new_file = last_move[2]

                        # If the pawn moved 2 square
                        if old_rank - new_rank == -2:
                            # If the pawn moving is on the right of that pawn
                            if file + 1 <= 7:
                                if self.board[rank][file + 1] == self.board[new_rank][new_file]:
                                    moves.append((rank - 1, new_file))

                            # If the pawn moving is on the left of that pawn
                            if file - 1 >= 0:
                                if self.board[rank][file - 1] == self.board[new_rank][new_file]:
                                    moves.append((rank - 1, new_file))


            # Generate black pawn moves
            else:
                # Pawn can move 1 square forward if it is empty and inbounds
                if rank + 1 <= 7:
                    if self.board[rank + 1][file] == None:
                        moves.append((rank + 1, file))

                # Pawn can move 2 squares forward if it hasn't moved and 2 squares infront are empty
                if rank == 1:
                    if self.board[rank + 1][file] == None and self.board[rank + 2][file] == None:
                        moves.append((rank + 2, file))

                # Pawn can take on diagonals if it is inbounds
                if rank + 1 <= 7 and file - 1 >= 0:
                    if self.board[rank + 1][file - 1] is not None and self.board[rank + 1][file - 1].isupper():
                        moves.append((rank + 1, file - 1))
                        
                if rank + 1 <= 7 and file + 1 <= 7:
                    if self.board[rank  +1][file + 1] is not None and self.board[rank + 1][file + 1].isupper():
                        moves.append((rank + 1, file + 1))

                # Can en-passant if: last move was made by a pawn
                if last_move is not None:
                    if last_move[1] == 'P':
                        old_rank, old_file = last_move[0]
                        new_rank, new_file = last_move[2]

                        # If the pawn moved 2 square
                        if old_rank - new_rank == 2:
                            # If the pawn moving is on the right of that pawn
                            if file + 1 <= 7:
                                if self.board[rank][file + 1] == self.board[new_rank][new_file]:
                                    moves.append((rank + 1, file + 1))

                            # If the pawn moving is on the left of that pawn
                            if file - 1 >= 0:
                                if self.board[rank][file - 1] == self.board[new_rank][new_file]:
                                    moves.append((rank + 1, file - 1))

        # Calculates pawn attacking moves
        # Danger is true
        # Used to check for danger squares for the opposing king                        
        else:
            # Pawn can take on diagonals if it is inbounds
            if piece_type.isupper():
                if rank - 1 >= 0 and file - 1 >= 0:
                    moves.append((rank - 1, file - 1))
                        
                if rank - 1 >= 0 and file + 1 <= 7:
                    moves.append((rank - 1, file + 1))

                # Can en-passant if: last move was made by a pawn
                if last_move is not None:
                    if last_move[1] == 'p':
                        old_rank, old_file = last_move[0]
                        new_rank, new_file = last_move[2]

                        # If the pawn moved 2 square
                        if old_rank - new_rank == -2:
                            # If the pawn moving is on the right of that pawn
                            if file + 1 <= 7:
                                if self.board[rank][file + 1] == self.board[new_rank][new_file]:
                                    moves.append((rank - 1, new_file))

                            # If the pawn moving is on the left of that pawn
                            if file - 1 >= 0:
                                if self.board[rank][file - 1] == self.board[new_rank][new_file]:
                                    moves.append((rank - 1, new_file))
            if piece_type.islower():
                # Pawn can take on diagonals if it is inbounds
                if rank + 1 <= 7 and file - 1 >= 0:
                    moves.append((rank + 1, file - 1))
                        
                if rank + 1 <= 7 and file + 1 <= 7:
                    moves.append((rank + 1, file + 1))

                # Can en-passant if: last move was made by a pawn
                if last_move is not None:
                    if last_move[1] == 'P':
                        old_rank, old_file = last_move[0]
                        new_rank, new_file = last_move[2]

                        # If the pawn moved 2 square
                        if old_rank - new_rank == 2:
                            # If the pawn moving is on the right of that pawn
                            if file + 1 <= 7:
                                if self.board[rank][file + 1] == self.board[new_rank][new_file]:
                                    moves.append((rank + 1, file + 1))

                            # If the pawn moving is on the left of that pawn
                            if file - 1 >= 0:
                                if self.board[rank][file - 1] == self.board[new_rank][new_file]:
                                    moves.append((rank + 1, file - 1))

        return moves
    

    def generate_rook_moves(self, piece_pos, piece_type):
        
            """ Rook's Moves:
            Check column/row until an obstruction is encountered.
            If the obstruction is an opponent's piece, include it as a valid move (capture).
            """
            moves = []
            # Possible standard rook moves
            possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            # Rook is white if variable is true, else black
            white = True if piece_type.isupper() else False

            # Loop through possible moves until an enemy or boundry is found
            for i, j in possible_moves:
                rank, file = piece_pos
                while True:
                    rank += i
                    file += j
                    if 0 <= rank < 8 and 0 <= file < 8:

                        # If a piece is in the way
                        if self.board[rank][file] is not None:
                            
                            # Add move if piece is opposite color
                            if white and self.board[rank][file].islower():
                                moves.append((rank, file))
                            elif not white and self.board[rank][file].isupper():
                                moves.append((rank, file))
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
        # Knight is white if variable is true, else black
        white = True if piece_type.isupper() else False

        # Loop through possible moves
        # If destination is empty or an enemy piece, add move
        for i, j in possible_moves:
            rank, file = piece_pos
            rank += i
            file += j
            if 0 <= rank < 8 and 0 <= file < 8:
                if self.board[rank][file] is None:
                    moves.append((rank, file))
                elif (white and self.board[rank][file].islower()) or (not white and self.board[rank][file].isupper()):
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
        # Bishop is white if variable is true, else black
        white = True if piece_type.isupper() else False

        # Loop through possible moves until an enemy or boundry is found
        for i, j in possible_moves:
            rank, file = piece_pos
            while True:
                rank += i
                file += j
                if 0 <= rank < 8 and 0 <= file < 8:
                    if self.board[rank][file] is not None:

                        # Add move if piece is opposite color
                        if white and self.board[rank][file].islower():
                            moves.append((rank, file))
                        elif not white and self.board[rank][file].isupper():
                            moves.append((rank, file))

                        break

                    else:
                        moves.append((rank, file))

                else:
                    break

        return moves
    
    
    def generate_queen_moves(self, piece_pos, piece_type):
        """ 
        Check position after move is in bounds and is not occupied by another piece
        """
        moves = []

        # Possible standard queen moves
        possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        # Queen is white if variable is true, else black
        white = True if piece_type.isupper() else False

        # Loop through possible moves until an enemy or boundry is found
        for i, j in possible_moves:
            rank, file = piece_pos
            while True:
                rank += i
                file += j
                if 0 <= rank < 8 and 0 <= file < 8:
                    if self.board[rank][file] is not None:

                        # Add move if piece is opposite color
                        if white and self.board[rank][file].islower():
                            moves.append((rank, file))
                        elif not white and self.board[rank][file].isupper():
                            moves.append((rank, file))

                        break

                    else:
                        moves.append((rank, file))

                else:
                    break

        return moves
    
    def generate_king_moves(self, piece_pos, piece_type):
        """ 
        Check position after move is in bounds and is not occupied by another piece
        """
        moves = []

        # Possible standard queen moves
        possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        white = True if piece_type.isupper() else False

        danger_squares = self.find_danger_squares(white)

        for i, j in possible_moves:
            rank, file = piece_pos
            rank += i
            file += j

            if 0 <= rank < 8 and 0 <= file < 8:
                if self.board[rank][file] is not None:
                    # Add move if piece is opposite color
                    if white and self.board[rank][file].islower():
                        if (rank, file) not in danger_squares:
                            moves.append((rank, file))

                    elif not white and self.board[rank][file].isupper():
                        if (rank, file) not in danger_squares:
                            moves.append((rank, file))

                else:
                    if (rank, file) not in danger_squares:
                        moves.append((rank, file))

            rank, file = piece_pos

        if white and "K" in self.can_castle:
            if self.board[rank][file + 1] == None and self.board[rank][file + 2] == None:
                if (rank, file + 2) not in danger_squares and (rank, file + 1) not in danger_squares:
                    moves.append((rank, file + 2))

        if white and "Q" in self.can_castle:
            if self.board[rank][file - 1] == None and self.board[rank][file - 2] == None and self.board[rank][file - 3] == None:
                if (rank, file - 2) not in danger_squares and (rank, file - 1) not in danger_squares:
                    moves.append((rank, file - 2))

        if not white and "k" in self.can_castle:
            if self.board[rank][file + 1] == None and self.board[rank][file + 2] == None:
                if (rank, file + 2) not in danger_squares and (rank, file + 1) not in danger_squares:
                    moves.append((rank, file + 2))

        if not white and "q" in self.can_castle:
            if self.board[rank][file - 1] == None and self.board[rank][file - 2] == None and self.board[rank][file - 3] == None:
                if (rank, file - 2) not in danger_squares and (rank, file - 1) not in danger_squares:
                    moves.append((rank, file - 2))

        
        return moves


    def find_danger_squares(self, white, save_king=False):
        
        # Find all squares that are under attack
        danger_squares = []

        king_pos = self.find_king(white)
        king_r, king_f = king_pos
        king = self.board[king_r][king_f]
        self.board[king_r][king_f] = None

        for r, rank in enumerate(self.board):
            for f, piece in enumerate(rank):
                if self.board[r][f] is not None:
                    if (white and piece.islower()) or (not white and piece.isupper()):
                        if piece != "K" and piece != "k":

                            danger_moves = self.generate_moves((r,f), True)

                            for ele in danger_moves:
                                if ele not in danger_squares:
                                    danger_squares.append(ele)

        self.board[king_r][king_f] = king

        if save_king:
            return danger_squares, king_pos
        
        return danger_squares



    def king_in_check(self, white):

        # Find all squares that are under attack
        is_check = False

        danger_squares, king_pos = self.find_danger_squares(white, True)

        # If king is under attack return True
        if king_pos in danger_squares:
            is_check = True

        return is_check
    
    def king_in_checkmate(self, white):
        is_checkmate = True

        king = self.find_king(white)

        # Create a temporary board and loop through pieces
        for r, rank in enumerate(self.board):
            for f, piece in enumerate(rank):
                if self.board[r][f] is not None:
                    """ For every piece that is not the king and the correct color,
                    Generate their moves, make that move in the temporary board
                    If the move takes the king out of check, it is not checkmate
                    If no moves take the king out of check, it is checkmate
                    """
                    if (white and piece.isupper()) or (not white and piece.islower()):
                        moves = self.generate_moves((r,f))
                        for move in moves:
                            temp_game_state = cp.deepcopy(self)
                            temp_game_state.make_move((r, f), move)
                            if not temp_game_state.king_in_check(white):
                                is_checkmate = False
                                break

        return is_checkmate
        
    
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

        for r in range(8):
            if white:
                    r = -1 - r
            for f, piece in enumerate(self.board[r]):
                if piece is not None:
                    if (white and piece.isupper()) or (not white and piece.islower()):
                        if self.generate_moves((r, f), white):
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