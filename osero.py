import streamlit as st
import numpy as np
import random

# --- 設定 ---
BOARD_SIZE = 8
BLACK = 1
WHITE = -1
EMPTY = 0

def init_game():
    """ゲーム状態の初期化"""
    board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
    # 初期配置
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
    """配置可能な場所を取得"""
    moves = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r, c] == EMPTY:
                if can_flip(board, r, c, player):
                    moves.append((r, c))
    return moves

def can_flip(board, r, c, player):
    """(r, c)に置いた時に裏返せる石があるかチェック"""
    for dr, dc in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
        if check_direction(board, r, c, dr, dc, player):
            return True
    return False

def check_direction(board, r, c, dr, dc, player):
    """特定の方向に対して裏返し可能か判定"""
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
    """石を裏返す処理"""
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

# --- Streamlit UI ---
st.set_page_config(page_title="量子オセロ", layout="centered")
st.title("🌌 量子オセロ (Quantum Othello)")

if "state" not in st.session_state:
    st.session_state.state = init_game()

state = st.session_state.state

# スコア計算
black_score = np.sum(state["board"] == BLACK)
white_score = np.sum(state["board"] == WHITE)

# サイドバー: 状態表示と操作
st.sidebar.header("ゲーム情報")
turn_label = "黒 (BLACK)" if state["turn"] == BLACK else "白 (WHITE)"
st.sidebar.subheader(f"現在の手番: {turn_label}")
st.sidebar.write(f"スコア - 黒: {black_score} | 白: {white_score}")

# 確率の選択
probs = [p for p, count in state["inventory"][state["turn"]].items() if count > 0]
if not probs:
    selected_prob = None
else:
    selected_prob = st.sidebar.selectbox(
        "使用する石の確率を選択してください",
        probs,
        format_func=lambda x: f"{x}% で自分の色になる (残り{state['inventory'][state['turn']][x]}枚)"
    )

if st.sidebar.button("ゲームをリセット"):
    st.session_state.state = init_game()
    st.rerun()

# 有効な手の取得
valid_moves = get_valid_moves(state["board"], state["turn"])

if not valid_moves and not state["game_over"]:
    # パス処理
    next_turn = -state["turn"]
    if not get_valid_moves(state["board"], next_turn):
        state["game_over"] = True
    else:
        state["turn"] = next_turn
        st.info(f"{turn_label} は置ける場所がないためパスします。")
        st.rerun()

# 盤面の描画
for r in range(BOARD_SIZE):
    cols = st.columns(BOARD_SIZE)
    for c in range(BOARD_SIZE):
        cell_value = state["board"][r, c]
        
        # ボタンのラベルとスタイリング
        label = ""
        if cell_value == BLACK:
            label = "⚫"
        elif cell_value == WHITE:
            label = "⚪"
        
        # クリック時の処理
        if (r, c) in valid_moves and not state["game_over"]:
            if cols[c].button(label if label else " ", key=f"btn_{r}_{c}"):
                if selected_prob is not None:
                    # 量子的な判定
                    roll = random.randint(1, 100)
                    actual_color = state["turn"] if roll <= selected_prob else -state["turn"]
                    
                    # ログの記録
                    res_msg = "成功！" if actual_color == state["turn"] else "失敗...相手の色になりました。"
                    state["history"].append(f"{turn_label}: {r+1}行{c+1}列に{selected_prob}%を選択 -> {res_msg}")
                    
                    # 盤面更新
                    state["board"] = flip_pieces(state["board"], r, c, actual_color)
                    state["inventory"][state["turn"]][selected_prob] -= 1
                    state["turn"] = -state["turn"]
                    st.rerun()
        else:
            cols[c].write(f"<div style='text-align:center; font-size:24px; border:1px solid #ccc; height:40px;'>{label}</div>", unsafe_allow_html=True)

# ゲーム終了判定
if state["game_over"] or (np.sum(state["board"] == EMPTY) == 0):
    st.success("ゲーム終了！")
    if black_score > white_score:
        st.header("🏆 黒の勝ち！")
    elif white_score > black_score:
        st.header("🏆 白の勝ち！")
    else:
        st.header("引き分け！")

# 履歴の表示
with st.expander("対局履歴"):
    for log in reversed(state["history"]):
        st.text(log)
