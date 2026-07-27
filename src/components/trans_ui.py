import streamlit as st

def render_translation_area():
    """現在組み立てている文のリアルタイム翻訳を描画する"""
    st.markdown("### 📍 Translation（翻訳）")
    st.success(f"**{st.session_state.translation}**")
