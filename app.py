# -*- coding: utf-8 -*-
import sys
import logging
import streamlit as st

st.set_page_config(
    page_title="WordFlow English",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ★ レイアウト用CSSはここに集約（中身は responsive.py）。この2行が唯一の追加点。
from responsive import inject_responsive_css

inject_responsive_css()

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
    st.markdown(
        "<h1 style='text-align:center;font-size:clamp(24px,7vw,32px);margin-bottom:0.2rem;'>"
        "🧩 WordFlow English</h1>",
        unsafe_allow_html=True,
    )
    goal_ui.render_input_form(llm)

elif st.session_state.step == 1:
    goal_ui.render_current_goal()
    trans_ui.render_translation_area()
    puzzle_ui.render_puzzle_area(llm)

elif st.session_state.step == 2:
    puzzle_ui.render_completion_screen()
