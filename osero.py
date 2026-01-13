import streamlit as st
import numpy as np
import random

# --- 設定 ---
BOARD_SIZE = 8
BLACK = 1
WHITE = -1
EMPTY = 0

# カスタムCSS: ボタンそのものをオセロのマスとしてスタイリング
st.markdown("""
    <style>
    /* 盤面の緑色のベース */
    .stButton > button {
        width: 100%;
        height: 60px;
        background-color: #2e7d32 !important;
        color: transparent !important;
        border: 1px solid #1b5e20 !important;
        border-radius: 0px !important;
        padding: 0px !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* ホバー時の色 */
    .stButton > button:hover {
        background-color: #388e3c !important;
        border: 1px solid #ffffff !important;
    }

    /* 石の共通スタイル */
    .piece {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        display: block;
        margin: auto;
    }
    .black-piece {
        background: radial-gradient(circle at 30% 30%, #444, #000);
        box-shadow: 2px 2px 4px rgba(0,0,0,0.4);
    }
    .white-piece {
        background: radial-gradient(circle at 30% 30%, #fff, #ccc);
        border: 1px solid #bbb;
        box-shadow: 2px 2px 4px rgba(0,0,0,0.4);
    }

    /* 置ける場所のヒント（小さな丸） */
    .hint-dot {
        width: 12px;
        height: 12px;
        background-color: rgba(0, 0, 0, 0.2);
        border-radius: 50%;
        margin: auto;
    }

    /* 石が置かれた場所（ボタンとしての機能を無効化した見た目） */
    .static-cell {
        width: 100%;
        height: 60px;
        background-color: #2e7d32;
        border: 1px solid #1b5e20;
        display: flex;
        align-items: center;
        justify-content: center;
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
    r_idx, c_idx = r + dr, c + dc
    count = 0
    while 0 <= r_idx < BOARD_SIZE and 0 <= c_idx < BOARD_SIZE:
        if board[r_idx, c_idx] == -player:
            count += 1
        elif board[r_idx, c_idx] == player:
            return count > 0
        else:
            break
        r_idx += dr
        c_idx += dc
    return False

def flip_pieces(board, r, c, player):
    new_board = board.copy()
    new_board[r, c] = player
    for dr, dc in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
        if check_direction(board, r, c, dr, dc, player):
            nr, nc = r + dr, c + dc
            while new_board[nr, nc] == -player:
                new_board[nr, nc] = player
                nr += dr
                nc += dc
    return new_board

# --- アプリケーション開始 ---
st.title("🌌 量子オセロ")

if "state" not in st.session_state:
    st.session_state.state = init_game()

state = st.session_state.state
black_score = np.sum(state["board"] == BLACK)
white_score = np.sum(state["board"] == WHITE)

# サイドバー
st.sidebar.header("対局ステータス")
turn_str = "黒 (BLACK)" if state["turn"] == BLACK else "白 (WHITE)"
st.sidebar.subheader(f"手番: {turn_str}")
st.sidebar.write(f"スコア: 黒 {black_score} - {white_score} 白")

# 確率選択
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

# 盤面描画
for r in range(BOARD_SIZE):
    cols = st.columns(BOARD_SIZE)
    for c in range(BOARD_SIZE):
        cell_value = state["board"][r, c]
        with cols[c]:
            if cell_value == BLACK:
                st.markdown('<div class="static-cell"><div class="piece black-piece"></div></div>', unsafe_allow_html=True)
            elif cell_value == WHITE:
                st.markdown('<div class="static-cell"><div class="piece white-piece"></div></div>', unsafe_allow_html=True)
            elif (r, c) in valid_moves and not state["game_over"]:
                # 置ける場所をボタンとして配置
                if st.button(" ", key=f"cell_{r}_{c}"):
                    # 量子的判定
                    roll = random.randint(1, 100)
                    is_success = roll <= selected_prob
                    actual_color = state["turn"] if is_success else -state["turn"]
                    
                    # ログと更新
                    msg = "成功！" if is_success else "失敗（相手の色）"
                    state["history"].append(f"{turn_str}: ({r+1},{c+1}) {selected_prob}% -> {msg}")
                    
                    state["board"] = flip_pieces(state["board"], r, c, actual_color)
                    state["inventory"][state["turn"]][selected_prob] -= 1
                    
                    # 次のターンの準備
                    next_turn = -state["turn"]
                    if not get_valid_moves(state["board"], next_turn) and not get_valid_moves(state["board"], state["turn"]):
                        state["game_over"] = True
                    else:
                        state["turn"] = next_turn
                    st.rerun()
                # ボタンの上にヒントのドットを重ねる（視覚のみ）
                st.markdown('<div style="margin-top:-35px; pointer-events:none;"><div class="hint-dot"></div></div>', unsafe_allow_html=True)
            else:
                # 何も置けない空マス
                st.markdown('<div class="static-cell"></div>', unsafe_allow_html=True)

# ゲーム終了処理
if state["game_over"]:
    st.success("対局終了！")
    if black_score > white_score:
        st.header(f"🏆 黒の勝ち！ ({black_score} vs {white_score})")
        st.balloons()
    elif white_score > black_score:
        st.header(f"🏆 白の勝ち！ ({white_score} vs {black_score})")
        st.balloons()
    else:
        st.header("引き分け！")

# 履歴
with st.expander("対局履歴"):
    for log in reversed(state["history"]):
        st.text(log)
