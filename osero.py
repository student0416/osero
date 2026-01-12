import streamlit as st
import numpy as np

# 1. Initialize the 8x8 game board
# 0: Empty, 1: Black, -1: White
board = np.zeros((8, 8), dtype=int)

# Place initial pieces
board[3, 3] = -1  # White
board[3, 4] = 1   # Black
board[4, 3] = 1   # Black
board[4, 4] = -1  # White

print("Initialized 8x8 Othello Board:")
print(board)

# 2. Define quantum pieces for each player
# Each player gets 2 pieces for each probability (90%, 80%, 70%, 60%)
# Probabilities are represented as floats (e.g., 0.9 for 90%)

quantum_pieces_black = [
    0.9, 0.9,  # Two 90% probability pieces
    0.8, 0.8,  # Two 80% probability pieces
    0.7, 0.7,  # Two 70% probability pieces
    0.6, 0.6   # Two 60% probability pieces
]

quantum_pieces_white = [
    0.9, 0.9,  # Two 90% probability pieces
    0.8, 0.8,  # Two 80% probability pieces
    0.7, 0.7,  # Two 70% probability pieces
    0.6, 0.6   # Two 60% probability pieces
]

print("\nBlack player's quantum pieces (probabilities):")
print(quantum_pieces_black)
print("\nWhite player's quantum pieces (probabilities):")
print(quantum_pieces_white)
def get_valid_moves(board, player):
    valid_moves = []
    # Directions to check: (dr, dc) for (row_change, col_change)
    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1),  # Horizontal and Vertical
        (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonals
    ]

    for r in range(8):
        for c in range(8):
            # Check only empty cells
            if board[r, c] == 0:
                for dr, dc in directions:
                    r_temp, c_temp = r + dr, c + dc
                    pieces_to_flip = []

                    # Check if the next cell is within bounds and contains an opponent's piece
                    if 0 <= r_temp < 8 and 0 <= c_temp < 8 and board[r_temp, c_temp] == -player:
                        # Move in this direction as long as we find opponent's pieces
                        while 0 <= r_temp < 8 and 0 <= c_temp < 8 and board[r_temp, c_temp] == -player:
                            pieces_to_flip.append((r_temp, c_temp))
                            r_temp += dr
                            c_temp += dc

                        # If we found at least one opponent's piece and then found our own piece,
                        # then this is a valid move.
                        if 0 <= r_temp < 8 and 0 <= c_temp < 8 and board[r_temp, c_temp] == player and pieces_to_flip:
                            valid_moves.append((r, c))
                            break  # Found a valid direction, no need to check other directions for this cell
    return valid_moves

# Test the function with the initial board state
current_player = 1 # Black
valid_moves_black = get_valid_moves(board, current_player)
print(f"Valid moves for Black (player {current_player}): {valid_moves_black}")

current_player = -1 # White
valid_moves_white = get_valid_moves(board, current_player)
print(f"Valid moves for White (player {current_player}): {valid_moves_white}")
import numpy as np

def determine_piece_color(probability, player):
    """
    量子駒の確率に基づいて、実際にその駒がプレイヤーの色になるか相手の色になるかを決定します。

    Args:
        probability (float): 駒がプレイヤーの色になる確率 (0.0 から 1.0)。
        player (int): 現在のプレイヤー (1 for Black, -1 for White)。

    Returns:
        int: 決定された駒の色 (player または -player)。
    """
    random_roll = np.random.rand()
    if random_roll <= probability:
        return player  # 駒はプレイヤーの色になる
    else:
        return -player # 駒は相手の色になる

# Test the function
print("Testing determine_piece_color function:")
current_player = 1 # Black player

# Test with 90% probability piece for Black
probability_90 = 0.9
print(f"\nBlack player (probability {probability_90*100}%):")
for _ in range(5):
    determined_color = determine_piece_color(probability_90, current_player)
    print(f"  Random roll vs {probability_90}: Determined color = {'Black' if determined_color == 1 else 'White'}")

# Test with 60% probability piece for Black
probability_60 = 0.6
print(f"\nBlack player (probability {probability_60*100}%):")
for _ in range(5):
    determined_color = determine_piece_color(probability_60, current_player)
    print(f"  Random roll vs {probability_60}: Determined color = {'Black' if determined_color == 1 else 'White'}")
def apply_move(board, row, col, determined_color):
    # Create a copy of the board to modify
    new_board = board.copy()
    
    # Place the new piece
    new_board[row, col] = determined_color

    # Directions to check: (dr, dc) for (row_change, col_change)
    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1),  # Horizontal and Vertical
        (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonals
    ]

    # Check all 8 directions to flip opponent's pieces
    for dr, dc in directions:
        r_temp, c_temp = row + dr, col + dc
        pieces_to_flip_in_direction = []

        # Collect opponent's pieces in this direction
        while 0 <= r_temp < 8 and 0 <= c_temp < 8 and new_board[r_temp, c_temp] == -determined_color:
            pieces_to_flip_in_direction.append((r_temp, c_temp))
            r_temp += dr
            c_temp += dc
        
        # If we found at least one opponent's piece and then found our own piece,
        # then flip the collected pieces.
        if 0 <= r_temp < 8 and 0 <= c_temp < 8 and new_board[r_temp, c_temp] == determined_color and pieces_to_flip_in_direction:
            for flip_r, flip_c in pieces_to_flip_in_direction:
                new_board[flip_r, flip_c] = determined_color
                
    return new_board

# --- Test the function ---
print("Original Board:")
print(board)

# Example: Black player places a piece (determined as Black) at a valid move
# Let's pick the first valid move for Black: (2, 3)
chosen_move_row, chosen_move_col = valid_moves_black[0] # (2, 3)
player_to_move = 1 # Black

# For testing, let's assume the piece determined to be player's own color (Black)
# In a real game, this would come from determine_piece_color(chosen_probability, player_to_move)
determined_color_for_test = player_to_move

print(f"\nApplying move: Player {player_to_move} (Black) places a piece at ({chosen_move_row}, {chosen_move_col}), determined color is Black.")
updated_board = apply_move(board, chosen_move_row, chosen_move_col, determined_color_for_test)

print("\nUpdated Board after move:")
print(updated_board)

# Test with a different scenario, e.g., White's move
# Let's pick the first valid move for White: (2, 4)
chosen_move_row_white, chosen_move_col_white = valid_moves_white[0] # (2, 4)
player_to_move_white = -1 # White
determined_color_for_test_white = player_to_move_white

print(f"\nApplying move: Player {player_to_move_white} (White) places a piece at ({chosen_move_row_white}, {chosen_move_col_white}), determined color is White.")
updated_board_white_move = apply_move(board, chosen_move_row_white, chosen_move_col_white, determined_color_for_test_white)

print("\nUpdated Board after White's move:")
print(updated_board_white_move)
import numpy as np # Ensure numpy is imported for array operations and random numbers

# Helper function to count pieces on the board
def count_pieces(board):
    black_count = np.sum(board == 1)
    white_count = np.sum(board == -1)
    return black_count, white_count

# Helper function to check if the board is completely full
def is_board_full(board):
    return np.all(board != 0)

def play_quantum_othello(initial_board, black_pieces_initial, white_pieces_initial):
    board = initial_board.copy()
    quantum_pieces_black_available = list(black_pieces_initial)  # Create mutable copies for the game
    quantum_pieces_white_available = list(white_pieces_initial)  # Create mutable copies for the game
    current_player = 1  # 1 for Black, -1 for White
    pass_count = 0      # Tracks consecutive passes

    print("Quantum Othello Game Start!")

    while True:
        print("\n" + "="*40)
        print(f"Current Board State (Player {'Black' if current_player == 1 else 'White'}'s Turn):")
        print(board)

        black_score, white_score = count_pieces(board)
        print(f"Scores: Black = {black_score}, White = {white_score}")
        print(f"Black's remaining quantum pieces: {quantum_pieces_black_available}")
        print(f"White's remaining quantum pieces: {quantum_pieces_white_available}")

        # Get valid moves for the current player using the previously defined function
        valid_moves = get_valid_moves(board, current_player)

        # Determine which quantum pieces are available for the current player
        current_player_pieces = quantum_pieces_black_available if current_player == 1 else quantum_pieces_white_available

        # Check if the current player has any valid moves or pieces left
        if not valid_moves or not current_player_pieces:
            print(f"Player {'Black' if current_player == 1 else 'White'} has no valid moves or no pieces left and passes.")
            pass_count += 1
            if pass_count == 2:
                print("\nBoth players passed consecutively. Game Over!")
                break  # End game if both players pass
        else:
            pass_count = 0  # Reset pass count if a move is made

            # --- Player Input Loop for choosing a move and a quantum piece ---
            chosen_row, chosen_col, chosen_piece_idx = -1, -1, -1
            while True:
                try:
                    print(f"\nPlayer {'Black' if current_player == 1 else 'White'}'s turn.")
                    print(f"Available moves (row, col): {valid_moves}")
                    print(f"Available quantum pieces (probabilities with index): {list(enumerate(current_player_pieces))}")

                    move_input = input("Enter your move (row, col) and piece index (e.g., 2,3,0 for 0th piece): ")
                    parts = move_input.split(',')
                    r, c, piece_idx = int(parts[0].strip()), int(parts[1].strip()), int(parts[2].strip())

                    if (r, c) not in valid_moves:
                        print("Invalid move: Not a valid position on the board. Please try again.")
                        continue
                    if not (0 <= piece_idx < len(current_player_pieces)):
                        print("Invalid piece index: Please choose an available piece by its index.")
                        continue

                    chosen_row, chosen_col, chosen_piece_idx = r, c, piece_idx
                    break  # Exit loop if input is valid

                except (ValueError, IndexError):
                    print("Invalid input format. Please enter row, col, and piece index separated by commas (e.g., 2,3,0).")
                except Exception as e:
                    print(f"An unexpected error occurred during input: {e}")

            # Get the probability of the chosen quantum piece
            chosen_piece_probability = current_player_pieces[chosen_piece_idx]

            # Determine the actual color of the piece using the previously defined function
            determined_color = determine_piece_color(chosen_piece_probability, current_player)
            print(f"Quantum piece (probability {chosen_piece_probability*100:.1f}%) determined to be: {'Black' if determined_color == 1 else 'White'}")

            # Apply the move and update the board using the previously defined function
            board = apply_move(board, chosen_row, chosen_col, determined_color)

            # Remove the used piece from the player's available pieces
            if current_player == 1:
                quantum_pieces_black_available.pop(chosen_piece_idx)
            else:
                quantum_pieces_white_available.pop(chosen_piece_idx)

        # Check for game end conditions after a move or a pass
        if is_board_full(board):
            print("\nBoard is full. Game Over!")
            break

        # Switch player for the next turn
        current_player *= -1

    # --- Game End ---
    print("\n" + "#"*40)
    print("Final Board:")
    print(board)
    final_black_score, final_white_score = count_pieces(board)
    print(f"Final Scores: Black = {final_black_score}, White = {final_white_score}")

    if final_black_score > final_white_score:
        print("Black Wins!")
    elif final_white_score > final_black_score:
        print("White Wins!")
    else:
        print("It's a Tie!")

    return board # Return the final board state
import numpy as np # Ensure numpy is imported for array operations and random numbers

# Helper function to count pieces on the board
def count_pieces(board):
    black_count = np.sum(board == 1)
    white_count = np.sum(board == -1)
    return black_count, white_count

# Helper function to check if the board is completely full
def is_board_full(board):
    return np.all(board != 0)

def play_quantum_othello(initial_board, black_pieces_initial, white_pieces_initial):
    board = initial_board.copy()
    quantum_pieces_black_available = list(black_pieces_initial)  # Create mutable copies for the game
    quantum_pieces_white_available = list(white_pieces_initial)  # Create mutable copies for the game
    current_player = 1  # 1 for Black, -1 for White
    pass_count = 0      # Tracks consecutive passes

    print("Quantum Othello Game Start!")

    while True:
        print("\n" + "="*40)
        print(f"Current Board State (Player {'Black' if current_player == 1 else 'White'}'s Turn):")
        print(board)

        black_score, white_score = count_pieces(board)
        print(f"Scores: Black = {black_score}, White = {white_score}")
        print(f"Black's remaining quantum pieces: {quantum_pieces_black_available}")
        print(f"White's remaining quantum pieces: {quantum_pieces_white_available}")

        # Get valid moves for the current player using the previously defined function
        valid_moves = get_valid_moves(board, current_player)

        # Determine which quantum pieces are available for the current player
        current_player_pieces = quantum_pieces_black_available if current_player == 1 else quantum_pieces_white_available

        # Check if the current player has any valid moves or pieces left
        if not valid_moves or not current_player_pieces:
            print(f"Player {'Black' if current_player == 1 else 'White'} has no valid moves or no pieces left and passes.")
            pass_count += 1
            if pass_count == 2:
                print("\nBoth players passed consecutively. Game Over!")
                break  # End game if both players pass
        else:
            pass_count = 0  # Reset pass count if a move is made

            # --- Player Input Loop for choosing a move and a quantum piece ---
            chosen_row, chosen_col, chosen_piece_idx = -1, -1, -1
            while True:
                try:
                    print(f"\nPlayer {'Black' if current_player == 1 else 'White'}'s turn.")
                    print(f"Available moves (row, col): {valid_moves}")
                    print(f"Available quantum pieces (probabilities with index): {list(enumerate(current_player_pieces))}")

                    move_input = input("Enter your move (row, col) and piece index (e.g., 2,3,0 for 0th piece): ")
                    parts = move_input.split(',')
                    r, c, piece_idx = int(parts[0].strip()), int(parts[1].strip()), int(parts[2].strip())

                    if (r, c) not in valid_moves:
                        print("Invalid move: Not a valid position on the board. Please try again.")
                        continue
                    if not (0 <= piece_idx < len(current_player_pieces)):
                        print("Invalid piece index: Please choose an available piece by its index.")
                        continue

                    chosen_row, chosen_col, chosen_piece_idx = r, c, piece_idx
                    break  # Exit loop if input is valid

                except (ValueError, IndexError):
                    print("Invalid input format. Please enter row, col, and piece index separated by commas (e.g., 2,3,0).")
                except Exception as e:
                    print(f"An unexpected error occurred during input: {e}")

            # Get the probability of the chosen quantum piece
            chosen_piece_probability = current_player_pieces[chosen_piece_idx]

            # Determine the actual color of the piece using the previously defined function
            determined_color = determine_piece_color(chosen_piece_probability, current_player)
            print(f"Quantum piece (probability {chosen_piece_probability*100:.1f}%) determined to be: {'Black' if determined_color == 1 else 'White'}")

            # Apply the move and update the board using the previously defined function
            board = apply_move(board, chosen_row, chosen_col, determined_color)

            # Remove the used piece from the player's available pieces
            if current_player == 1:
                quantum_pieces_black_available.pop(chosen_piece_idx)
            else:
                quantum_pieces_white_available.pop(chosen_piece_idx)

        # Check for game end conditions after a move or a pass
        if is_board_full(board):
            print("\nBoard is full. Game Over!")
            break

        # Switch player for the next turn
        current_player *= -1

    # --- Game End ---
    print("\n" + "#"*40)
    print("Final Board:")
    print(board)
    final_black_score, final_white_score = count_pieces(board)
    print(f"Final Scores: Black = {final_black_score}, White = {final_white_score}")

    if final_black_score > final_white_score:
        print("Black Wins!")
    elif final_white_score > final_black_score:
        print("White Wins!")
    else:
        print("It's a Tie!")

    return board # Return the final board state
