import sys
import logging
import asyncio
import streamlit as st

# 📱 スマホ対応: layout="centered" に変更（スマホでは全幅、PCでは適度な中央寄せになる）
st.set_page_config(page_title="WordFlow English", page_icon="🧩", layout="centered")

from src.state_manager import init_session_state
from src.llm_engine import load_model
from src.components import goal_ui, puzzle_ui, trans_ui

if sys.platform == "win32":
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)
    logging.getLogger("tornado.application").setLevel(logging.CRITICAL)

init_session_state()
llm = load_model()

# 📱 スマホ対応: タイトルはCSSで中央寄せに
st.markdown("<h1 style='text-align: center;'>🧩 WordFlow English</h1>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)

if st.session_state.step == 0:
    # そのままレンダリング
    goal_ui.render_input_form(llm)

elif st.session_state.step == 1:
    # 📱 スマホ対応: 縦長シングルカラムレイアウト
    # 上から下へ「目標」→「今の翻訳」→「パズル」の順で並べる
    goal_ui.render_current_goal()
    
    st.write("<br>", unsafe_allow_html=True)
    trans_ui.render_translation_area()
    
    st.divider() # 視覚的な区切り線
    
    puzzle_ui.render_puzzle_area(llm)

elif st.session_state.step == 2:
    puzzle_ui.render_completion_screen()