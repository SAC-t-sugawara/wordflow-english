import streamlit as st
import random
from streamlit_mic_recorder import speech_to_text
from src.llm_engine import ask_local_llm, generate_correct_sentence

def render_input_form(llm):
    st.markdown("### 🎯 何を英語で伝えたいですか？")
    
    if "random_preset" not in st.session_state:
        presets = [
            "今日映画を見に行きたいな", "新しいイヤホンが欲しいです", 
            "明日は晴れるといいな", "週末は友達とランチに行きます", 
            "昨日はたくさん寝ました", "おすすめのレストランを教えてください"
        ]
        st.session_state.random_preset = random.choice(presets)

    with st.container(border=True):
        default_text = st.session_state.stt_goal_output if 'stt_goal_output' in st.session_state else st.session_state.random_preset
            
        st.text_area(
            "テキストで入力", 
            value=default_text, 
            height=100,
            label_visibility="collapsed",
            placeholder="ここに日本語を入力してください...",
            key="input_text_key"
        )

        st.write("<br>", unsafe_allow_html=True)

        # 📱 スマホ対応: [1, 3, 1]のような極端な比率をやめ、均等2列で押しやすく
        col_mic, col_btn = st.columns(2)
        
        with col_mic:
            text_from_mic = speech_to_text(
                language='ja',
                start_prompt="🎤 音声で入力",
                stop_prompt="⏹️ 録音中...",
                just_once=True,
                key='stt_goal'
            )

        with col_btn:
            submit_btn = st.button("パズルを作成 🧩", type="primary", use_container_width=True)

    if text_from_mic:
        st.session_state.stt_goal_output = text_from_mic
        st.rerun()

    if submit_btn:
        latest_goal = st.session_state.input_text_key
        if not latest_goal.strip():
            st.warning("⚠️ 日本語の文章を入力するか、音声で入力してください！")
            st.stop()

        st.session_state.japanese_goal = latest_goal
        st.session_state.current_sentence = []
        st.session_state.show_ghost = False

        with st.spinner("AIがパズルを準備中..."):
            correct_words = generate_correct_sentence(llm, latest_goal)
            st.session_state.correct_words = correct_words

            first_correct = correct_words[0] if correct_words else None
            res = ask_local_llm(llm, [], latest_goal, correct_next_word=first_correct)
            st.session_state.candidates = res.get("candidates", [])
            st.session_state.ghost_text = res.get("ghost_text", "")
            st.session_state.translation = "（ここからスタート）"

        st.session_state.step = 1
        st.rerun()

def render_current_goal():
    st.markdown("### 🎯 言いたいこと")
    st.info(f"**{st.session_state.japanese_goal}**")