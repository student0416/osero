import streamlit as st
import numpy as np
import random

# --- Game Logic Functions (Copied from previous steps) ---

def count_pieces(board):
    black_count = np.sum(board == 1)
    white_count = np.sum(board == -1)
    return black_count, white_count

def is_board_full(board):
    return np.all(board != 0)

def get_valid_moves(board, player):
    valid_moves = []
    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1),  # Horizontal and Vertical
        (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonals
    ]

    for r in range(8):
        for c in range(8):
            if board[r, c] == 0:
                for dr, dc in directions:
                    r_temp, c_temp = r + dr, c + dc
                    pieces_to_flip = []

                    if 0 <= r_temp < 8 and 0 <= c_temp < 8 and board[r_temp, c_temp] == -player:
                        while 0 <= r_temp < 8 and 0 <= c_temp < 8 and board[r_temp, c_temp] == -player:
                            pieces_to_flip.append((r_temp, c_temp))
                            r_temp += dr
                            c_temp += dc

                        if 0 <= r_temp < 8 and 0 <= c_temp < 8 and board[r_temp, c_temp] == player and pieces_to_flip:
                            valid_moves.append((r, c))
                            break
    return valid_moves

def determine_piece_color(probability, player):
    random_roll = np.random.rand()
    if random_roll <= probability:
        return player
    else:
        return -player

def apply_move(board, row, col, determined_color):
    new_board = board.copy()
    new_board[row, col] = determined_color

    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1)
    ]

    for dr, dc in directions:
        r_temp, c_temp = row + dr, col + dc
        pieces_to_flip_in_direction = []

        while 0 <= r_temp < 8 and 0 <= c_temp < 8 and new_board[r_temp, c_temp] == -determined_color:
            pieces_to_flip_in_direction.append((r_temp, c_temp))
            r_temp += dr
            c_temp += dc

        if 0 <= r_temp < 8 and 0 <= c_temp < 8 and new_board[r_temp, c_temp] == determined_color and pieces_to_flip_in_direction:
            for flip_r, flip_c in pieces_to_flip_in_direction:
                new_board[flip_r, flip_c] = determined_color
    return new_board

# --- Streamlit アプリケーション ---
st.set_page_config(layout="wide")
st.title("量子オセロゲーム")

st.write("""
このゲームは通常のオセロに「量子駒」の要素を導入したものです。
駒を置く際、選択した量子駒の確率に基づいて、その駒が自分の色になるか相手の色になるかが確率的に決定されます。
""")

# ゲーム状態の初期化 (セッションステート) - Robust initialization
if 'board' not in st.session_state:
    st.session_state.board = np.zeros((8, 8), dtype=int)
    st.session_state.board[3, 3] = -1  # White
    st.session_state.board[3, 4] = 1   # Black
    st.session_state.board[4, 3] = 1   # Black
    st.session_state.board[4, 4] = -1  # White

if 'quantum_pieces_black' not in st.session_state:
    st.session_state.quantum_pieces_black = [
        0.9, 0.9, 0.8, 0.8, 0.7, 0.7, 0.6, 0.6
    ]
if 'quantum_pieces_white' not in st.session_state:
    st.session_state.quantum_pieces_white = [
        0.9, 0.9, 0.8, 0.8, 0.7, 0.7, 0.6, 0.6
    ]
if 'current_player' not in st.session_state:
    st.session_state.current_player = 1 # 1 for Black, -1 for White
if 'pass_count' not in st.session_state:
    st.session_state.pass_count = 0
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'game_message' not in st.session_state:
    st.session_state.game_message = "ゲーム開始！黒のターンです。"

def reset_game():
    st.session_state.board = np.zeros((8, 8), dtype=int)
    st.session_state.board[3, 3] = -1
    st.session_state.board[3, 4] = 1
    st.session_state.board[4, 3] = 1
    st.session_state.board[4, 4] = -1
    st.session_state.quantum_pieces_black = [
        0.9, 0.9, 0.8, 0.8, 0.7, 0.7, 0.6, 0.6
    ]
    st.session_state.quantum_pieces_white = [
        0.9, 0.9, 0.8, 0.8, 0.7, 0.7, 0.6, 0.6
    ]
    st.session_state.current_player = 1
    st.session_state.pass_count = 0
    st.session_state.game_over = False
    st.session_state.game_message = "ゲーム開始！黒のターンです。"

# --- 盤面の表示 ---
st.header("ゲーム盤")

# CSS for better board display
st.markdown("""
<style>
.board-container {
    display: grid;
    grid-template-columns: repeat(8, 50px);
    grid-template-rows: repeat(8, 50px);
    width: 400px; /* 8 * 50px */
    height: 400px; /* 8 * 50px */
    border: 2px solid #333;
    margin-bottom: 20px;
}
.cell {
    width: 50px;
    height: 50px;
    border: 1px solid #999;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #006400; /* Dark green */
    box-sizing: border-box;
}
.piece-black {
    width: 40px;
    height: 40px;
    background-color: black;
    border-radius: 50%;
    border: 2px solid #555;
}
.piece-white {
    width: 40px;
    height: 40px;
    background-color: white;
    border-radius: 50%;
    border: 2px solid #555;
}
.valid-move {
    background-color: rgba(255, 255, 0, 0.3); /* Yellowish overlay for valid moves */
}
</style>
""", unsafe_allow_html=True)

# Generate board HTML
board_html = '<div class="board-container">'
valid_moves = []
if not st.session_state.game_over:
    valid_moves = get_valid_moves(st.session_state.board, st.session_state.current_player)

for r in range(8):
    for c in range(8):
        cell_class = "cell"
        piece_html = ""
        if (r, c) in valid_moves and st.session_state.board[r, c] == 0:
            cell_class += " valid-move"

        if st.session_state.board[r, c] == 1:
            piece_html = '<div class="piece-black"></div>'
        elif st.session_state.board[r, c] == -1:
            piece_html = '<div class="piece-white"></div>'
        board_html += f'<div class="{cell_class}">{piece_html}</div>'
board_html += '</div>'
st.markdown(board_html, unsafe_allow_html=True)


# --- ゲーム情報とプレイヤー入力 ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("現在の状況")
    black_score, white_score = count_pieces(st.session_state.board)
    st.metric("黒の駒数", black_score)
    st.metric("白の駒数", white_score)
    st.write(f"現在のプレイヤー: {'<span style="color: black; font-weight: bold;">黒</span>' if st.session_state.current_player == 1 else '<span style="color: white; background-color: black; font-weight: bold;">白</span>'}", unsafe_allow_html=True)
    st.write(f"メッセージ: **{st.session_state.game_message}**")

    if st.session_state.game_over:
        st.success(st.session_state.game_message)
        st.button("新しいゲームを開始", on_click=reset_game)

with col2:
    st.subheader("量子駒と手番")

    if st.session_state.game_over:
        st.write("ゲームは終了しました。新しいゲームを開始してください。")
    else:
        current_player_pieces = st.session_state.quantum_pieces_black if st.session_state.current_player == 1 else st.session_state.quantum_pieces_white

        st.write(f"{'黒' if st.session_state.current_player == 1 else '白'}の残りの量子駒 (確率):")
        # Display quantum pieces with indices
        piece_options = [f"[{i}] {prob*100:.0f}%" for i, prob in enumerate(current_player_pieces)]
        if not piece_options:
            st.write("利用可能な量子駒がありません。")
        else:
            selected_piece_idx = st.selectbox(
                "使用する量子駒を選んでください:",
                options=list(range(len(current_player_pieces))),
                format_func=lambda x: piece_options[x],
                key=f"piece_select_{st.session_state.current_player}"
            )

        valid_moves = get_valid_moves(st.session_state.board, st.session_state.current_player)

        if not valid_moves:
            st.warning("有効な手がありません。パスします。")
            if st.button("パス", key="pass_button"):
                st.session_state.pass_count += 1
                if st.session_state.pass_count == 2:
                    st.session_state.game_over = True
                    black_score, white_score = count_pieces(st.session_state.board)
                    if black_score > white_score:
                        st.session_state.game_message = "両者パス！ゲーム終了！黒の勝利！"
                    elif white_score > black_score:
                        st.session_state.game_message = "両者パス！ゲーム終了！白の勝利！"
                    else:
                        st.session_state.game_message = "両者パス！ゲーム終了！引き分け！"
                else:
                    st.session_state.game_message = f"{'黒' if st.session_state.current_player == 1 else '白'}はパスしました。"
                    st.session_state.current_player *= -1 # ターン交代
                st.rerun()
        elif not current_player_pieces:
            st.warning("利用可能な量子駒がありません。パスします。")
            if st.button("パス (駒なし)", key="pass_button_no_pieces"):
                st.session_state.pass_count += 1
                if st.session_state.pass_count == 2:
                    st.session_state.game_over = True
                    black_score, white_score = count_pieces(st.session_state.board)
                    if black_score > white_score:
                        st.session_state.game_message = "両者パス！ゲーム終了！黒の勝利！"
                    elif white_score > black_score:
                        st.session_state.game_message = "両者パス！ゲーム終了！白の勝利！"
                    else:
                        st.session_state.game_message = "両者パス！ゲーム終了！引き分け！"
                else:
                    st.session_state.game_message = f"{'黒' if st.session_state.current_player == 1 else '白'}はパスしました。"
                    st.session_state.current_player *= -1 # ターン交代
                st.rerun()
        else:
            st.session_state.pass_count = 0 # パス状況をリセット

            st.write(f"利用可能な手 (行, 列): {valid_moves}")
            col_r, col_c = st.columns(2)
            with col_r:
                row_input = st.number_input("行 (0-7)", min_value=0, max_value=7, key=f"row_input_{st.session_state.current_player}")
            with col_c:
                col_input = st.number_input("列 (0-7)", min_value=0, max_value=7, key=f"col_input_{st.session_state.current_player}")

            if st.button("駒を置く", key="place_piece_button"):
                if (row_input, col_input) in valid_moves:
                    chosen_piece_probability = current_player_pieces[selected_piece_idx]
                    determined_color = determine_piece_color(chosen_piece_probability, st.session_state.current_player)

                    st.session_state.board = apply_move(st.session_state.board, row_input, col_input, determined_color)

                    # 使用した量子駒をリストから削除
                    if st.session_state.current_player == 1:
                        st.session_state.quantum_pieces_black.pop(selected_piece_idx)
                    else:
                        st.session_state.quantum_pieces_white.pop(selected_piece_idx)

                    st.session_state.game_message = (
                        f"({row_input},{col_input})に駒を置きました。"
                        f"量子駒({chosen_piece_probability*100:.0f}%)は"
                        f"{'黒' if determined_color == 1 else '白'}になりました。"
                    )

                    # ゲーム終了条件のチェック
                    if is_board_full(st.session_state.board):
                        st.session_state.game_over = True
                        black_score, white_score = count_pieces(st.session_state.board)
                        if black_score > white_score:
                            st.session_state.game_message = "盤面が埋まりました！ゲーム終了！黒の勝利！"
                        elif white_score > black_score:
                            st.session_state.game_message = "盤面が埋まりました！ゲーム終了！白の勝利！"
                        else:
                            st.session_state.game_message = "盤面が埋まりました！ゲーム終了！引き分け！"
                    else:
                        st.session_state.current_player *= -1 # ターン交代
                        st.session_state.game_message += f" 次のターンは{'黒' if st.session_state.current_player == 1 else '白'}です。"
                    st.rerun()
                else:
                    st.error("その場所には駒を置けません。有効な手の中から選んでください。")

# --- 実行方法とプレイ手順 ---
st.sidebar.header("ゲームの実行方法とプレイ手順")
st.sidebar.markdown("""
### 1. コードの保存
上記のコードを`quantum_othello.py`という名前でファイルに保存します。

### 2. Streamlitのインストール
まだStreamlitをインストールしていない場合は、ターミナルで以下のコマンドを実行します。
```bash
pip install streamlit numpy
```

### 3. ゲームの実行
ターミナルで、`quantum_othello.py`を保存したディレクトリに移動し、以下のコマンドを実行します。
```bash
streamlit run quantum_othello.py
```
これにより、Webブラウザでゲームが起動します。

### 4. 基本的なプレイ手順
1.  **ゲーム開始**: アプリケーションを起動すると、初期盤面が表示され、黒（Black）のターンから始まります。
2.  **状況確認**: 盤面、現在の駒数、現在のプレイヤーを確認します。
3.  **量子駒の選択**: 「使用する量子駒を選んでください」のドロップダウンメニューから、使用したい量子駒（確率）を選択します。
4.  **手の選択**: 盤面上の薄い黄色のマスが有効な手です。これらの中から、駒を置きたいマスの「行」と「列」を入力します。
5.  **駒を置く**: 「駒を置く」ボタンをクリックします。
    *   選択した量子駒の確率に基づき、駒の色が決定されます。
    *   決定された色の駒が置かれ、通常のオセロルールに従って挟まれた相手の駒が反転します。
    *   使用した量子駒は利用可能なリストから削除されます。
6.  **ターン交代**: 駒を置くと、自動的に次のプレイヤーにターンが交代します。
7.  **パス**: 有効な手がない場合、または利用可能な量子駒がない場合、プレイヤーはパスします。「パス」ボタンが表示されるので、クリックしてパスします。
    *   両方のプレイヤーが連続してパスすると、ゲームは終了します。
8.  **ゲーム終了**: 以下のいずれかの条件でゲームが終了します。
    *   盤面上の全てのマスが駒で埋まった場合。
    *   両方のプレイヤーが連続してパスした場合。
9.  **勝敗判定**: ゲーム終了時、駒の数が多いプレイヤーが勝者となります。同数の場合は引き分けです。
10. **新しいゲーム**: ゲーム終了後、「新しいゲームを開始」ボタンをクリックすると、最初からゲームをやり直せます。
""")
