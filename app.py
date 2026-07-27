import sys
import logging
import asyncio
import streamlit as st

st.set_page_config(page_title="WordFlow English", page_icon="🧩", layout="wide")
st.markdown("""
<style>
/* 邪魔なアンカーリンク（鎖マーク）を非表示 */
.st-emotion-cache-1wqtbno { display: none !important; }

/* 💻 【PC用】画面幅が768px以上の時 */
@media (min-width: 768px) {
    .stApp { background-color: #e2e8f0 !important; }
    
    /* 👇 最新Streamlitで確実に幅を広げるための「データ属性」を使った指定 */
    [data-testid="stAppViewBlockContainer"] {
        max-width: 1000px !important; /* 👈 ここでPCの時の幅を決定！(1000pxでかなり広くなります) */
        width: 90% !important;
        background-color: #ffffff !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        border-radius: 20px !important; 
        margin-top: 40px !important;
        margin-bottom: 40px !important;
        padding: 3rem 4rem !important; /* 上下左右の余白 */
    }
}

/* 📱 【スマホ用】画面幅が767px以下の時 */
@media (max-width: 767px) {
    [data-testid="stAppViewBlockContainer"] {
        max-width: 100% !important;
        width: 100% !important;
        padding: 1rem 1rem !important;
        background-color: transparent !important;
    }
    h3 { font-size: 18px !important; margin-bottom: -10px !important; }
}

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
