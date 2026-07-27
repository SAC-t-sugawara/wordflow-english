import sys
import logging
import asyncio
import streamlit as st

st.set_page_config(page_title="WordFlow English", page_icon="🧩", layout="wide")
st.markdown("""
<style>
/* 邪魔なアンカーリンク（鎖マーク）を非表示 */
.st-emotion-cache-1wqtbno { display: none !important; }

/* 背景全体を少し暗いグレーにして、アプリを目立たせる */
.stApp { background-color: #e2e8f0 !important; }

/* 📱💻 【全端末共通】アプリのメイン画面（白い枠）の設定 */
[data-testid="stAppViewBlockContainer"] {
    /* 👇 🔧 ここで横幅を調整します！(400px〜500pxがお好みなら書き換えてください) */
    max-width: 450px !important; 
    
    width: 100% !important;
    background-color: #ffffff !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    border-radius: 20px !important; 
    margin-top: 20px !important;
    margin-bottom: 20px !important;
    padding: 1.5rem 1.5rem !important; /* 内側の余白 */
}

/* 見出しのサイズと余白の調整 */
h3 { font-size: 18px !important; margin-bottom: -10px !important; }

/* ボタンなどが縦に並ぶときの隙間をギュッと詰める */
div[data-testid="stVerticalBlock"] > div { gap: 0.5rem !important; }
</style>
""", unsafe_allow_html=True)

from src.state_manager import init_session_state
from src.llm_engine import load_model
from src.components import goal_ui, puzzle_ui, trans_ui

if sys.platform == "win32":
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)
    logging.getLogger("tornado.application").setLevel(logging.CRITICAL)

init_session_state()
llm = load_model()

# 最初の画面だけタイトルを表示（二重表示防止）
if st.session_state.step == 0:
    st.markdown("<h1 style='text-align: center; font-size: 32px;'>🧩 WordFlow English</h1>", unsafe_allow_html=True)
    goal_ui.render_input_form(llm)

elif st.session_state.step == 1:
    goal_ui.render_current_goal()
    trans_ui.render_translation_area()
    puzzle_ui.render_puzzle_area(llm)

elif st.session_state.step == 2:
    puzzle_ui.render_completion_screen()
