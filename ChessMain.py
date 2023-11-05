import pygame
import time
import numpy as np

from ChessEngine import *
from helper import *

# Global Variables
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
SQUARE_SIZE = (WINDOW_WIDTH) // 8
piece_type_from_symbol = {
    "K": "w_king", "k": "b_king", "Q": "w_queen", "q": "b_queen", "B": "w_bishop", "b": "b_bishop", "N": "w_knight", "n": "b_knight",
    "R": "w_rook", "r": "b_rook", "P": "w_pawn", "p": "b_pawn"
}


class graphicalBoard():
    def __init__(self):
        self.selected_piece = None
        self.highlighted_piece = None
        self.font = pygame.font.Font('freesansbold.ttf', 64)

    
    # Draws chess board 
    def draw_graphical_board(self, special_squares=None):

        for file in range(8):
            for rank in range(8):
                
                # Alternate square color based on file and rank
                square_color = (162, 119, 98) if (file + rank) % 2 else (241, 218, 193)

                # Special squares are select pieces
                if special_squares is not None:
                    if (rank, file) in special_squares:
                        square_color = (0, 204, 204)

                # Draw rectangles, creating the 8x8 grid
                pygame.draw.rect(screen, square_color, [SQUARE_SIZE * file, SQUARE_SIZE * rank, SQUARE_SIZE, SQUARE_SIZE], 0)


    # Function to center the piece within the square
    def center_piece(self, row, col, piece_width, piece_height, square_size):
        x_offset = (square_size - piece_width) // 2
        y_offset = (square_size - piece_height) // 2
        return col * square_size, row * square_size
    

    # Input FEN -> place pieces on the graphical chess board
    def place_pieces_from_fen(self, fen_board):

        fen_board = fen_board.split(" ")[0]
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
                    #fLoad images of chess pieces
                    piece_type = piece_type_from_symbol[symbol]
                    piece_img = pygame.image.load("chesspieces\{}.png".format(piece_type)).convert_alpha()

                    # Create a sprite for each chess piece and add it to the group
                    sprite = Sprite(piece_img, SQUARE_SIZE * file, SQUARE_SIZE * rank)
                    chess_sprites_list.add(sprite)

                    file += 1

    def place_pieces_from_board(self, board):

        chess_sprites_list.empty

        for rank in range(8):
            for file in range(8):

                symbol = board[rank][file]
                
                if symbol:
                    piece_type = piece_type_from_symbol[symbol]
                    piece_img = pygame.image.load("chesspieces\{}.png".format(piece_type)).convert_alpha()

                    sprite = Sprite(piece_img, SQUARE_SIZE * file, SQUARE_SIZE * rank)
                    chess_sprites_list.add(sprite)

        pygame.display.update()


    def remove_sprites(self):

        for sprite in chess_sprites_list:
            chess_sprites_list.remove(sprite)


    # Map the pygame coordinates to squares on board
    def map_coordinates_to_chessboard(self, x, y):
        file = (x) // SQUARE_SIZE
        rank = (y) // SQUARE_SIZE

        return rank, file
    

    def pawn_promote_selection(self, color):

        color = 'w' if color else 'b'

        # Load image pieces and put them in an array
        queen_img = pygame.image.load("chesspieces\{}_queen.png".format(color)).convert_alpha()
        rook_img = pygame.image.load("chesspieces\{}_rook.png".format(color)).convert_alpha()
        bishop_img = pygame.image.load("chesspieces\{}_bishop.png".format(color)).convert_alpha()
        knight_img = pygame.image.load("chesspieces\{}_knight.png".format(color)).convert_alpha()
        images = np.array([queen_img, rook_img, bishop_img, knight_img])

        # Background to piece selection
        pygame.draw.rect(screen, (32, 32, 32), [SQUARE_SIZE * 1.9, SQUARE_SIZE * 3.1, SQUARE_SIZE * 4.2, SQUARE_SIZE * 1.8], 0)

        # Background to individual pieces in selection screen
        pygame.draw.rect(screen, (74, 74, 74), [SQUARE_SIZE * 2, SQUARE_SIZE * 3.5, SQUARE_SIZE, SQUARE_SIZE], 0)
        pygame.draw.rect(screen, (74, 74, 74), [SQUARE_SIZE * 3, SQUARE_SIZE * 3.5, SQUARE_SIZE, SQUARE_SIZE], 0)
        pygame.draw.rect(screen, (74, 74, 74), [SQUARE_SIZE * 4, SQUARE_SIZE * 3.5, SQUARE_SIZE, SQUARE_SIZE], 0)
        pygame.draw.rect(screen, (74, 74, 74), [SQUARE_SIZE * 5, SQUARE_SIZE * 3.5, SQUARE_SIZE, SQUARE_SIZE], 0)

        for num, image in enumerate(images):

            sprite = Sprite(image, SQUARE_SIZE * (num + 2), SQUARE_SIZE * 3.7)
            promotion_selection_list.add(sprite)

        promotion_selection_list.update(events)
        promotion_selection_list.draw(screen)


    def promotion_loop(self, chess_game, new_rank, new_file, color):
        selection = True
        while selection:
            events = pygame.event.get()
            for event in events:
                # Clicked position is mapped to a chess board square
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos_x, pos_y = event.pos

                    if 300 >= pos_x >= 200 and 450 >= pos_y >= 350:
                        piece = "Q" if color else "q"
                        chess_game.board[new_rank][new_file] = piece
                        selection = False
                        break

                    elif 400 >= pos_x > 300 and 450 >= pos_y >= 350:
                        piece = "R" if color else "r"
                        chess_game.board[new_rank][new_file] = piece
                        selection = False
                        break

                    elif 500 >= pos_x > 400 and 450 >= pos_y >= 350:
                        piece = "B" if color else "b"
                        chess_game.board[new_rank][new_file] = piece
                        selection = False
                        break

                    elif 600 >= pos_x > 500 and 450 >= pos_y >= 350:
                        piece = "N" if color else "n"
                        chess_game.board[new_rank][new_file] = piece
                        selection = False
                        break

        if color == 'w':
            chess_game.white_promote = False 
        elif color == 'b':
            chess_game.black_promote = False


    def end(self, color, screen, end_type):

        if end_type == 1:
            if color:
                text = self.font.render('White Wins', True, (255,255,255), (32,32,32))
            else:
                text = self.font.render('Black Wins', True, (32,32,32), (255,255,255))
        elif end_type == 2:
            text = self.font.render('Stalemate', True, (255,255,255), (32,32,32))
        else:
            print("ERROR")

        textRect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        textRect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        screen.blit(text, textRect)
        
        pygame.display.update()


# Chess piece sprite class
class Sprite(pygame.sprite.Sprite): 

    def __init__(self, image, pos_x, pos_y): 
        super().__init__() 

        # Creates chess piece sprite and surrounds with rect
        self.image = image
        self.rect = self.image.get_rect() 

        # Create a larger rect while keeping the image centered within it
        self.rect.width = SQUARE_SIZE
        self.rect.height = SQUARE_SIZE
        self.rect.topleft = [pos_x + 15, pos_y]



# Initialize Pygame
pygame.init()

# Initialize Pygame window 
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Chess")

# Create game state
chess_game = GameState()
chess_game.place_pieces_from_fen()
graphical_board = graphicalBoard()

# Chess piece sprites list
chess_sprites_list = pygame.sprite.Group()
promotion_selection_list = pygame.sprite.Group()

# Draw the initial board
tic = time.perf_counter()
graphical_board.draw_graphical_board()
graphical_board.place_pieces_from_fen(chess_game.starting_pos)
pygame.display.update()
toc = time.perf_counter()
print(f"Generated board in {toc - tic:0.4f} seconds")


# Main game loop
end = False
running = True
while running:
        
    events = pygame.event.get()

    chess_sprites_list.update(events)
    chess_sprites_list.draw(screen) 
    pygame.display.update()

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # Clicked position is mapped to a chess board square
            pos_x, pos_y = event.pos
            rank, file = graphical_board.map_coordinates_to_chessboard(pos_x, pos_y)
            clicked_square = (rank, file)


            # Deselects piece if clicked twice
            if graphical_board.selected_piece == clicked_square:
                graphical_board.selected_piece = None
                graphical_board.draw_graphical_board()


            # If a piece is clicked, that piece is highlighted and selected
            elif not graphical_board.selected_piece and chess_game.board[rank][file] and chess_game.piece_matches_turn(rank, file) and not end:
                # Highlights the square
                moves = chess_game.generate_moves(clicked_square)
                graphical_board.draw_graphical_board(moves)

                # Selects the pieces as the chosen piece to move
                graphical_board.selected_piece = clicked_square


            # Makes a move and updates the board accordingly
            elif graphical_board.selected_piece and not end:

                # Makes the move on the chess_game board if it is legal and updates the game state
                tic = time.perf_counter()
                moves = chess_game.generate_moves(graphical_board.selected_piece)
                toc = time.perf_counter()
                print(f"Generated moves in {toc - tic:0.6f} seconds")
                if clicked_square in moves:

                    # Save last move in the chess_game object
                    new_rank, new_file = clicked_square
                    piece_rank, piece_file = graphical_board.selected_piece
                    piece_type = chess_game.board[piece_rank][piece_file]
                    chess_game.last_move = [graphical_board.selected_piece, piece_type, clicked_square]

                    color = True if piece_type.isupper() else False

                    # Makes the move in the board array
                    chess_game.make_move(graphical_board.selected_piece, clicked_square)
                    if chess_game.white_promote or chess_game.black_promote:

                        # Redraws the updated board
                        graphical_board.remove_sprites()
                        graphical_board.place_pieces_from_board(chess_game.board)
                        graphical_board.pawn_promote_selection(color)
                        pygame.display.update()

                        graphical_board.promotion_loop(chess_game, new_rank, new_file, color)
                    if chess_game.king_in_check(not color):
                        if chess_game.king_in_checkmate(not color):
                            end = 1
                    elif chess_game.is_stalemate(not color):
                        end = 2

                    elif chess_game.is_threefold_repetition():
                        end = 2                                      
                
                    # Redraws the updated board
                    graphical_board.remove_sprites()
                    graphical_board.place_pieces_from_board(chess_game.board)

                graphical_board.selected_piece = None

                graphical_board.draw_graphical_board()

                if end == 1: 
                    graphical_board.end(color, screen, 1)
                elif end == 2:
                    graphical_board.end(color, screen, 2)


        # End loop if user exits
        if event.type == pygame.QUIT:
            running = False