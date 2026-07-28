import sys
import logging
import asyncio
import streamlit as st

st.set_page_config(page_title="WordFlow English", page_icon="🧩", layout="wide")

st.markdown("""
<style>
.st-emotion-cache-1wqtbno { display: none !important; }
.stApp { background-color: #e2e8f0 !important; }

.block-container {
    max-width: 450px !important;
    margin: 30px auto !important;
    background-color: #ffffff !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    border-radius: 20px !important; 
    padding: 2rem 1.5rem !important;
}

h3 { font-size: 18px !important; margin-bottom: -10px !important; }
div[data-testid="stVerticalBlock"] > div { gap: 0.5rem !important; }

/* 📱 columnsを常に横並びに固定（flex-direction上書きが核心） */
div[data-testid="stHorizontalBlock"] {
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: 0.4rem !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="stVerticalBlock"] {
    min-width: 0 !important;
    width: 100% !important;
    flex: 1 1 0px !important;
}
div[data-testid="stSelectbox"] label,
div[data-testid="stSelectbox"] div {
    font-size: 13px !important;
}
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
