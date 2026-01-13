import streamlit as st
import numpy as np
import random

# --- 設定 ---
BOARD_SIZE = 8
BLACK = 1
WHITE = -1
EMPTY = 0

# カスタムCSS: ボタンを石のデザインに書き換える
st.markdown("""
    <style>
    /* 盤面の土台 */
    .stApp {
        background-color: #1a1a1a;
    }
    
    /* ボタンの基本スタイル（マス目） */
    div.stButton > button {
        width: 100%;
        height: 50px;
        background-color: #2e7d32 !important; /* オセロの緑 */
        border: 1px solid #1b5e20 !important;
        color: transparent !important;
        border-radius: 0px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0px;
        padding: 0px;
    }

    /* 黒石のデザイン */
    div.stButton > button:disabled {
        opacity: 1.0 !important;
        color: transparent !important;
    }
    
    /* 擬似要素で石を描画（ボタンの中身を書き換えるのは難しいためラベル文字を利用） */
    /* 実際には、ラベルに特殊文字を入れてCSSで装飾します */
    
    /* 置ける場所のホバー効果 */
    div.stButton > button:hover {
        background-color: #388e3c !important;
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

# サイドバー
st.sidebar.header("対局情報")
turn_color = "黒" if state["turn"] == BLACK else "白"
st.sidebar.subheader(f"現在の手番: {turn_color}")
st.sidebar.write(f"スコア: 黒 {black_score} - {white_score} 白")

probs = [p for p, count in state["inventory"][state["turn"]].items() if count > 0]
selected_prob = None
if probs:
    selected_prob = st.sidebar.selectbox(
        "使用する石（成功確率）:",
        probs,
        format_func=lambda x: f"{x}% (残り{state['inventory'][state['turn']][x]}枚)"
    )

if st.sidebar.button("ゲームリセット"):
    st.session_state.state = init_game()
    st.rerun()

valid_moves = get_valid_moves(state["board"], state["turn"])

# 盤面描画
for r in range(BOARD_SIZE):
    cols = st.columns(BOARD_SIZE)
    for c in range(BOARD_SIZE):
        cell_value = state["board"][r, c]
        
        # セルの状態に応じてラベル（見た目）を変える
        if cell_value == BLACK:
            label = "⚫"
            is_disabled = True
        elif cell_value == WHITE:
            label = "⚪"
            is_disabled = True
        elif (r, c) in valid_moves and not state["game_over"]:
            label = "·" # 置ける場所のガイド
            is_disabled = False
        else:
            label = ""
            is_disabled = True
            
        with cols[c]:
            # ボタンを配置
            if st.button(label, key=f"btn_{r}_{c}", disabled=is_disabled):
                if selected_prob is not None:
                    roll = random.randint(1, 100)
                    is_success = roll <= selected_prob
                    actual_color = state["turn"] if is_success else -state["turn"]
                    
                    res_msg = "成功！" if is_success else "失敗..."
                    state["history"].append(f"{turn_color}: ({r+1},{c+1}) {selected_prob}% -> {res_msg}")
                    
                    state["board"] = flip_pieces(state["board"], r, c, actual_color)
                    state["inventory"][state["turn"]][selected_prob] -= 1
                    state["turn"] = -state["turn"]
                    st.rerun()

# パス・終了判定
if not valid_moves and not state["game_over"]:
    next_turn = -state["turn"]
    if not get_valid_moves(state["board"], next_turn):
        state["game_over"] = True
    else:
        st.warning(f"{turn_color} は置ける場所がないためパスします。")
        if st.button("パスを確定"):
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
