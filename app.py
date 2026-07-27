import sys
import logging
import asyncio
import streamlit as st

# 🌟 layout="wide" に変更して、CSS側で幅を完全コントロールする
st.set_page_config(page_title="WordFlow English", page_icon="🧩", layout="wide")

st.markdown("""
<style>
/* 邪魔なアンカーリンク（鎖マーク）を非表示 */
.st-emotion-cache-1wqtbno { display: none !important; }

/* 📱 共通設定 */
div.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    background-color: #ffffff;
}

/* 💻 【PC用】画面幅が768px以上の時 */
@media (min-width: 768px) {
    .stApp { background-color: #e2e8f0; }
    
    /* 👇 ここを強制的に広げるように強化！ */
    div.block-container {
        width: 100% !important;
        max-width: 800px !important; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-radius: 20px; 
        margin-top: 30px;
        margin-bottom: 30px;
        padding-left: 4rem !important;
        padding-right: 4rem !important;
    }
}

/* 📱 【スマホ用】画面幅が767px以下の時 */
@media (max-width: 767px) {
    div.block-container {
        width: 100% !important;
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
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
