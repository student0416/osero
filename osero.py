import streamlit as st
import numpy as np
import random

# --- 設定 ---
BOARD_SIZE = 8
BLACK = 1
WHITE = -1
EMPTY = 0

# カスタムCSS: 現実のオセロ盤を再現
st.markdown("""
    <style>
    /* 盤面全体のコンテナ */
    .othello-board {
        background-color: #2e7d32;
        padding: 10px;
        border-radius: 5px;
        border: 4px solid #1b5e20;
        display: inline-block;
    }
    
    /* マスのスタイル */
    .cell-container {
        position: relative;
        width: 100%;
        padding-top: 100%; /* 正方形を維持 */
        background-color: #2e7d32;
        border: 1px solid #1b5e20;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* 石のスタイル */
    .piece {
        position: absolute;
        top: 10%;
        left: 10%;
        width: 80%;
        height: 80%;
        border-radius: 50%;
        box-shadow: 2px 2px 4px rgba(0,0,0,0.4);
    }
    .black-piece {
        background: radial-gradient(circle at 30% 30%, #444, #000);
    }
    .white-piece {
        background: radial-gradient(circle at 30% 30%, #fff, #ccc);
        border: 1px solid #bbb;
    }

    /* 置ける場所のヒント（小さなドット） */
    .hint-dot {
        position: absolute;
        top: 40%;
        left: 40%;
        width: 20%;
        height: 20%;
        background-color: rgba(0, 0, 0, 0.2);
        border-radius: 50%;
    }

    /* Streamlitのボタンを透明にしてマスに重ねる */
    .stButton > button {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        z-index: 10;
    }
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

def init_game():
    board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
    board[3, 3] = WHITE
    board[3, 4] = BLACK
    board[4, 3] = BLACK
    board[4, 4] = WHITE
    return {
        "board": board,
        "turn": BLACK,
        "inventory": {
            BLACK: {90: 8, 80: 8, 70: 8, 60: 8},
            WHITE: {90: 8, 80: 8, 70: 8, 60: 8}
        },
        "history": [],
        "game_over": False
    }

def get_valid_moves(board, player):
    moves = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r, c] == EMPTY:
                if can_flip(board, r, c, player):
                    moves.append((r, c))
    return moves

def can_flip(board, r, c, player):
    for dr, dc in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
        if check_direction(board, r, c, dr, dc, player):
            return True
    return False

def check_direction(board, r, c, dr, dc, player):
    r += dr
    c += dc
    count = 0
    while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
        if board[r, c] == -player:
            count += 1
        elif board[r, c] == player:
            return count > 0
        else:
            break
        r += dr
        c += dc
    return False

def flip_pieces(board, r, c, player):
    new_board = board.copy()
    new_board[r, c] = player
    for dr, dc in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
        if check_direction(new_board, r, c, dr, dc, player):
            nr, nc = r + dr, c + dc
            while new_board[nr, nc] == -player:
                new_board[nr, nc] = player
                nr += dr
                nc += dc
    return new_board

# --- ゲーム実行 ---
if "state" not in st.session_state:
    st.session_state.state = init_game()

state = st.session_state.state
black_score = np.sum(state["board"] == BLACK)
white_score = np.sum(state["board"] == WHITE)

st.title("🌌 量子オセロ")

# サイドバー設定
st.sidebar.header("対局情報")
turn_color = "黒" if state["turn"] == BLACK else "白"
st.sidebar.subheader(f"現在の手番: {turn_color}")
st.sidebar.write(f"スコア: 黒 {black_score} - {white_score} 白")

probs = [p for p, count in state["inventory"][state["turn"]].items() if count > 0]
selected_prob = None
if probs:
    selected_prob = st.sidebar.selectbox(
        "使用する石（成功確率）を選択:",
        probs,
        format_func=lambda x: f"{x}% (残り{state['inventory'][state['turn']][x]}枚)"
    )

if st.sidebar.button("ゲームリセット"):
    st.session_state.state = init_game()
    st.rerun()

valid_moves = get_valid_moves(state["board"], state["turn"])

# 盤面描画
board_container = st.container()
with board_container:
    for r in range(BOARD_SIZE):
        cols = st.columns(BOARD_SIZE)
        for c in range(BOARD_SIZE):
            cell_value = state["board"][r, c]
            with cols[c]:
                # マスのベースHTML
                html_content = '<div class="cell-container">'
                if cell_value == BLACK:
                    html_content += '<div class="piece black-piece"></div>'
                elif cell_value == WHITE:
                    html_content += '<div class="piece white-piece"></div>'
                elif (r, c) in valid_moves and not state["game_over"]:
                    html_content += '<div class="hint-dot"></div>'
                html_content += '</div>'
                
                st.markdown(html_content, unsafe_allow_html=True)
                
                # 透明ボタンを重ねる
                if (r, c) in valid_moves and not state["game_over"]:
                    if st.button("", key=f"btn_{r}_{c}"):
                        if selected_prob is not None:
                            roll = random.randint(1, 100)
                            is_success = roll <= selected_prob
                            actual_color = state["turn"] if is_success else -state["turn"]
                            
                            res_msg = "成功！" if is_success else "失敗...相手の色になりました"
                            state["history"].append(f"{turn_color}: ({r+1},{c+1}) {selected_prob}% -> {res_msg}")
                            
                            state["board"] = flip_pieces(state["board"], r, c, actual_color)
                            state["inventory"][state["turn"]][selected_prob] -= 1
                            state["turn"] = -state["turn"]
                            st.rerun()

# パス判定
if not valid_moves and not state["game_over"]:
    next_turn = -state["turn"]
    if not get_valid_moves(state["board"], next_turn):
        state["game_over"] = True
    else:
        st.warning(f"{turn_color} は置ける場所がないためパスします。")
        if st.button("パスを確定する"):
            state["turn"] = next_turn
            st.rerun()

if state["game_over"]:
    st.success("対局終了！")
    st.header(f"結果: 黒 {black_score} - {white_score} 白")
    if black_score > white_score:
        st.balloons()
        st.subheader("🏆 黒の勝利！")
    elif white_score > black_score:
        st.balloons()
        st.subheader("🏆 白の勝利！")

with st.expander("対局ログ"):
    for log in reversed(state["history"]):
        st.text(log)
