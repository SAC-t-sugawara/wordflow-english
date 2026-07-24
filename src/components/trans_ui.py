import streamlit as st

def render_translation_area():
    """現在組み立てている文のリアルタイム翻訳を描画する"""
    st.markdown("### 📍 現在の日本語訳")
    st.success(f"**{st.session_state.translation}**")