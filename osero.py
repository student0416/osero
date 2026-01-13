import streamlit as st
import numpy as np
import random

# --- 設定 ---
BOARD_SIZE = 8
BLACK = 1
WHITE = -1
EMPTY = 0

# カスタムCSS: リアルなオセロ盤を再現
st.markdown("""
    <style>
    /* 盤面全体のコンテナ */
    .stColumn {
        padding: 0px !important;
    }
    
    /* セルの基本スタイル */
    .othello-cell {
        width: 100%;
        height: 60px;
        line-height: 60px;
        background-color: #2e7d32; /* 盤面の緑 */
        border: 1px solid #1b5e20; /* グリッド線 */
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 35px;
        cursor: default;
    }

    /* 石の見た目 */
    .stone-black {
        color: black;
        text-shadow: 0px 0px 5px rgba(255,255,255,0.2);
    }
    .stone-white {
        color: white;
        text-shadow: 0px 0px 5px rgba(0,0,0,0.5);
    }

    /* 置ける場所のボタン用スタイル */
    div.stButton > button {
        width: 100%;
        height: 60px;
        border-radius: 0px;
        border: 1px solid #1b5e20 !important;
        margin: 0px !important;
        padding: 0px !important;
        font-size: 0px !important; /* 文字は隠す */
    }

    /* 通常の空き地（置けない場所） */
    div.stButton > button[kind="secondary"] {
        background-color: #2e7d32 !important;
        pointer-events: none; /* クリック無効 */
    }

    /* 置ける場所（明るい緑で強調） */
    div.stButton > button[kind="primary"] {
        background-color: #4caf50 !important; /* 明るい緑 */
        border: 1px solid #1b5e20 !important;
        transition: 0.3s;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #81c784 !important; /* ホバーでさらに明るく */
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

# --- メインロジック ---
if "state" not in st.session_state:
    st.session_state.state = init_game()

state = st.session_state.state
black_score = np.sum(state["board"] == BLACK)
white_score = np.sum(state["board"] == WHITE)

st.title("🌌 量子オセロ")

# サイドバー
st.sidebar.markdown(f"### 現在の手番: {'⚫ 黒' if state['turn'] == BLACK else '⚪ 白'}")
st.sidebar.write(f"**スコア**")
st.sidebar.code(f"黒: {black_score:02d} | 白: {white_score:02d}")

probs = [p for p, count in state["inventory"][state["turn"]].items() if count > 0]
selected_prob = None
if probs:
    selected_prob = st.sidebar.select_slider(
        "使用する石の確率 (%)",
        options=sorted(probs, reverse=True),
        value=max(probs)
    )
    st.sidebar.info(f"残り枚数: {state['inventory'][state['turn']][selected_prob]}枚")

if st.sidebar.button("盤面をリセット"):
    st.session_state.state = init_game()
    st.rerun()

valid_moves = get_valid_moves(state["board"], state["turn"])

# 盤面描画
# コンテナの幅を固定するための中央寄せ
main_col1, main_col2, main_col3 = st.columns([1, 10, 1])
with main_col2:
    for r in range(BOARD_SIZE):
        cols = st.columns(BOARD_SIZE)
        for c in range(BOARD_SIZE):
            cell_value = state["board"][r, c]
            with cols[c]:
                if cell_value == BLACK:
                    st.markdown('<div class="othello-cell stone-black">●</div>', unsafe_allow_html=True)
                elif cell_value == WHITE:
                    st.markdown('<div class="othello-cell stone-white">●</div>', unsafe_allow_html=True)
                elif (r, c) in valid_moves and not state["game_over"]:
                    # 置ける場所を明るい緑のボタンで表現
                    if st.button(f"{r}-{c}", key=f"btn_{r}_{c}", type="primary"):
                        if selected_prob is not None:
                            roll = random.randint(1, 100)
                            is_success = roll <= selected_prob
                            actual_color = state["turn"] if is_success else -state["turn"]
                            
                            res_msg = "成功！" if is_success else "失敗（相手の色）"
                            state["history"].append(f"{'黒' if state['turn']==1 else '白'}: ({r+1},{c+1}) {selected_prob}% -> {res_msg}")
                            
                            state["board"] = flip_pieces(state["board"], r, c, actual_color)
                            state["inventory"][state["turn"]][selected_prob] -= 1
                            state["turn"] = -state["turn"]
                            st.rerun()
                else:
                    # 置けない場所はただの盤面
                    st.button("", key=f"empty_{r}_{c}", type="secondary", disabled=True)

# ゲーム終了・パス判定
if not valid_moves and not state["game_over"]:
    next_turn = -state["turn"]
    if not get_valid_moves(state["board"], next_turn):
        state["game_over"] = True
        st.rerun()
    else:
        st.warning(f"{'黒' if state['turn']==BLACK else '白'} はパスになります。")
        if st.button("パスを確定して交代"):
            state["turn"] = next_turn
            st.rerun()

if state["game_over"]:
    st.balloons()
    st.success("対局終了！")
    if black_score > white_score:
        st.header(f"🏆 黒の勝利！ ({black_score} vs {white_score})")
    elif white_score > black_score:
        st.header(f"🏆 白の勝利！ ({white_score} vs {black_score})")
    else:
        st.header("引き分け！")

with st.expander("対局ログ"):
    for log in reversed(state["history"]):
        st.text(log)
