import streamlit as st

def init_session_state():
    defaults = {
        "step": 0,
        "japanese_goal": "",
        "current_sentence": [],
        "candidates": [],
        "ghost_text": "",
        "translation": "",
        "show_ghost": False,
        "correct_words": [],
        "feedback": "",  
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_session_state():
    st.session_state.step = 0
    st.session_state.japanese_goal = ""
    st.session_state.current_sentence = []
    st.session_state.candidates = []
    st.session_state.ghost_text = ""
    st.session_state.translation = ""
    st.session_state.show_ghost = False
    st.session_state.correct_words = []
    st.session_state.feedback = ""  