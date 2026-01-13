import streamlit as st
import numpy as np
import random

# --- 設定 ---
BOARD_SIZE = 8
BLACK = 1
WHITE = -1
EMPTY = 0

# カスタムCSS: ボタンのスタイルを調整して「置ける場所」を強調
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 50px;
        font-size: 24px !important;
        border-radius: 5px;
    }
    /* 置ける場所（有効な手）のスタイル */
    div.stButton > button[kind="primary"] {
        background-color: #e1f5fe; /* 薄い青色 */
        border: 2px solid #03a9f4;
        color: #03a9f4;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #b3e5fc;
        border: 2px solid #0288d1;
    }
    /* すでに石がある場所の表示用ボックス */
    .cell-box {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        background-color: #2e7d32; /* オセロ盤の緑色 */
        border: 1px solid #1b5e20;
        height: 50px;
        border-radius: 5px;
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
st.sidebar.subheader(f"手番: {turn_color}")
st.sidebar.write(f"スコア: 黒 {black_score} - {white_score} 白")

probs = [p for p, count in state["inventory"][state["turn"]].items() if count > 0]
selected_prob = None
if probs:
    selected_prob = st.sidebar.radio(
        "使用する石（成功確率）:",
        probs,
        format_func=lambda x: f"{x}% (残り{state['inventory'][state['turn']][x]}枚)",
        horizontal=True
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
        with cols[c]:
            if cell_value == BLACK:
                st.markdown('<div class="cell-box">⚫</div>', unsafe_allow_html=True)
            elif cell_value == WHITE:
                st.markdown('<div class="cell-box">⚪</div>', unsafe_allow_html=True)
            elif (r, c) in valid_moves and not state["game_over"]:
                # 置ける場所を「primary」ボタンとして表示
                if st.button("・", key=f"btn_{r}_{c}", type="primary"):
                    if selected_prob is not None:
                        roll = random.randint(1, 100)
                        is_success = roll <= selected_prob
                        actual_color = state["turn"] if is_success else -state["turn"]
                        
                        res_msg = "成功！" if is_success else "失敗...相手の色になりました！"
                        state["history"].append(f"{turn_color}: ({r+1},{c+1}) に{selected_prob}%を配置 -> {res_msg}")
                        
                        state["board"] = flip_pieces(state["board"], r, c, actual_color)
                        state["inventory"][state["turn"]][selected_prob] -= 1
                        state["turn"] = -state["turn"]
                        st.rerun()
            else:
                # 置けない空き地
                st.markdown('<div class="cell-box"> </div>', unsafe_allow_html=True)

# ゲーム終了処理
if not valid_moves and not state["game_over"]:
    next_turn = -state["turn"]
    if not get_valid_moves(state["board"], next_turn):
        state["game_over"] = True
        st.rerun()
    else:
        st.warning(f"{turn_color} は置ける場所がないためパスします。")
        if st.button("パスする"):
            state["turn"] = next_turn
            st.rerun()

if state["game_over"]:
    st.success("対局終了！")
    if black_score > white_score:
        st.header(f"🏆 黒の勝ち！ ({black_score} vs {white_score})")
    elif white_score > black_score:
        st.header(f"🏆 白の勝ち！ ({white_score} vs {black_score})")
    else:
        st.header("引き分け！")

with st.expander("ログを表示"):
    for log in reversed(state["history"]):
        st.text(log)
