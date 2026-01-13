import streamlit as st
import numpy as np
import random

# --- 設定 ---
BOARD_SIZE = 8
BLACK = 1
WHITE = -1
EMPTY = 0

# カスタムCSS
st.markdown("""
    <style>
    /* 盤面の各列の隙間をなくす */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 calc(12.5% - 2px) !important;
        min-width: calc(12.5% - 2px) !important;
        padding: 1px !important;
    }

    /* ボタンを正方形に強制し、オセロのマスにする */
    .stButton > button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important; /* 正方形を維持 */
        height: auto !important;
        background-color: #2e7d32 !important;
        color: transparent !important;
        border: 1px solid #1b5e20 !important;
        border-radius: 0px !important;
        padding: 0px !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .stButton > button:hover {
        background-color: #388e3c !important;
        border: 1px solid #ffffff !important;
    }

    /* 石のスタイル（レスポンシブ） */
    .piece-container {
        width: 100%;
        aspect-ratio: 1 / 1;
        background-color: #2e7d32;
        border: 1px solid #1b5e20;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .piece {
        width: 85%;
        height: 85%;
        border-radius: 50%;
    }
    .black-piece {
        background: radial-gradient(circle at 30% 30%, #444, #000);
        box-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }
    .white-piece {
        background: radial-gradient(circle at 30% 30%, #fff, #ccc);
        border: 1px solid #bbb;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }

    /* 置ける場所のドット */
    .hint-dot {
        width: 20%;
        height: 20%;
        background-color: rgba(0, 0, 0, 0.2);
        border-radius: 50%;
        position: absolute;
        pointer-events: none; /* クリックを邪魔しない */
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
    ri, ci = r + dr, c + dc
    count = 0
    while 0 <= ri < BOARD_SIZE and 0 <= ci < BOARD_SIZE:
        if board[ri, ci] == -player:
            count += 1
        elif board[ri, ci] == player:
            return count > 0
        else:
            break
        ri += dr
        ci += dc
    return False

def flip_pieces(board, r, c, player):
    new_board = board.copy()
    new_board[r, c] = player
    for dr, dc in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
        if check_direction(new_board, r, c, dr, dc, player):
            ri, ci = r + dr, c + dc
            while new_board[ri, ci] == -player:
                new_board[ri, ci] = player
                ri += dr
                ci += dc
    return new_board

# アプリ
st.title("🌌 量子オセロ")

if "state" not in st.session_state:
    st.session_state.state = init_game()

state = st.session_state.state
black_score = np.sum(state["board"] == BLACK)
white_score = np.sum(state["board"] == WHITE)

# サイドバー
st.sidebar.header("対局ステータス")
turn_str = "黒" if state["turn"] == BLACK else "白"
st.sidebar.subheader(f"現在の手番: {turn_str}")
st.sidebar.markdown(f"**スコア**")
st.sidebar.write(f"⚫ 黒: {black_score} 枚")
st.sidebar.write(f"⚪ 白: {white_score} 枚")

probs = [p for p, count in state["inventory"][state["turn"]].items() if count > 0]
selected_prob = st.sidebar.selectbox(
    "使用する石の成功率:",
    probs if probs else [0],
    format_func=lambda x: f"{x}% (残り{state['inventory'][state['turn']].get(x, 0)}枚)"
)

if st.sidebar.button("リセット"):
    st.session_state.state = init_game()
    st.rerun()

valid_moves = get_valid_moves(state["board"], state["turn"])

# 盤面
for r in range(BOARD_SIZE):
    cols = st.columns(BOARD_SIZE)
    for c in range(BOARD_SIZE):
        cell_value = state["board"][r, c]
        with cols[c]:
            if cell_value == BLACK:
                st.markdown('<div class="piece-container"><div class="piece black-piece"></div></div>', unsafe_allow_html=True)
            elif cell_value == WHITE:
                st.markdown('<div class="piece-container"><div class="piece white-piece"></div></div>', unsafe_allow_html=True)
            elif (r, c) in valid_moves and not state["game_over"]:
                # コンテナの中にドットとボタンを配置
                # ボタン自体を正方形にし、その上にドットを重ねる
                if st.button(" ", key=f"cell_{r}_{c}"):
                    roll = random.randint(1, 100)
                    is_success = roll <= selected_prob
                    actual_color = state["turn"] if is_success else -state["turn"]
                    
                    msg = "成功！" if is_success else "失敗（相手の色）"
                    state["history"].append(f"{turn_str}: ({r+1},{c+1}) {selected_prob}% -> {msg}")
                    
                    state["board"] = flip_pieces(state["board"], r, c, actual_color)
                    state["inventory"][state["turn"]][selected_prob] -= 1
                    
                    next_turn = -state["turn"]
                    if not get_valid_moves(state["board"], next_turn) and not get_valid_moves(state["board"], state["turn"]):
                        state["game_over"] = True
                    else:
                        state["turn"] = next_turn
                    st.rerun()
                # ドットの表示（ボタンの直下にマイナスマージンで重ねる）
                st.markdown('<div style="display:flex; justify-content:center; margin-top:-60%; pointer-events:none;"><div class="hint-dot"></div></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="piece-container"></div>', unsafe_allow_html=True)

# 終了判定
if state["game_over"]:
    st.success("対局終了！")
    st.header(f"黒 {black_score} - {white_score} 白")
    if black_score > white_score: st.balloons()

with st.expander("履歴"):
    for log in reversed(state["history"]):
        st.text(log)
