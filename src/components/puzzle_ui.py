import streamlit as st
import urllib.parse
from src.llm_engine import ask_local_llm, generate_feedback
from src.state_manager import reset_session_state

def _update_state(llm):
    # (既存のまま変更なし)
    next_index = len(st.session_state.current_sentence)
    correct_words = st.session_state.get("correct_words", [])

    if next_index < len(correct_words):
        next_correct = correct_words[next_index]
    else:
        next_correct = None 

    with st.spinner("AIが翻訳・準備中..."):
        res = ask_local_llm(
            llm,
            st.session_state.current_sentence,
            st.session_state.japanese_goal,
            correct_next_word=next_correct
        )
        st.session_state.candidates = res.get("candidates", [])
        st.session_state.ghost_text = res.get("ghost_text", "")
        st.session_state.translation = res.get("translation", "")

def render_puzzle_area(llm):
    # CSSはそのまま（スマホでも綺麗に適用されます）
    st.markdown("""
    <style>
    div[data-testid="stButton"] > button[kind="secondary"] {
        border-radius: 12px; border: 2px solid #CBD5E1; background-color: white; color: #334155;
        font-size: 18px !important; font-weight: bold; box-shadow: 0 4px 0px #CBD5E1; transition: all 0.1s ease;
        padding-top: 10px; padding-bottom: 10px;
    }
    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        border-color: #1E88E5; color: #1E88E5; box-shadow: 0 4px 0px #1E88E5; transform: translateY(-2px);
    }
    div[data-testid="stButton"] > button[kind="secondary"]:active {
        box-shadow: 0 0px 0px #1E88E5; transform: translateY(2px);
    }
    div[data-testid="stButton"] > button[kind="primary"] {
        border-radius: 12px; border: none; background-color: #1E88E5; color: white;
        font-weight: bold; box-shadow: 0 4px 0px #1565C0; transition: all 0.1s ease;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background-color: #1976D2; box-shadow: 0 4px 0px #0D47A1; transform: translateY(-2px);
    }
    div[data-testid="stButton"] > button[kind="primary"]:active {
        box-shadow: 0 0px 0px #0D47A1; transform: translateY(2px);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### 🧩 英文を組み立てる")

    current_str = " ".join(st.session_state.current_sentence)
    ghost_display = st.session_state.ghost_text if st.session_state.show_ghost else ""

    sentence_html = f"""
    <div style="font-size: 26px; padding: 20px; background-color: #f8fafc;
                border-radius: 12px; border: 2px solid #cbd5e1; margin-bottom: 20px;
                min-height: 80px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <span style="color: #0f172a; font-weight: 800;">{current_str}</span>
        <span style="color: #94a3b8; font-style: italic; opacity: 0.7;"> {ghost_display}</span>
    </div>
    """
    st.markdown(sentence_html, unsafe_allow_html=True)

    if st.session_state.candidates:
        candidates = st.session_state.candidates
        n_cands = len(candidates)
        
        # 📱 スマホ対応: 5列だと文字がはみ出すので、最大3列に制限
        if n_cands <= 4:
            cols_per_row = 2  # 4個なら 2列 × 2行
        else:
            cols_per_row = 3  # 5個以上なら 3列ベース (例: 3列 + 2列)
            
        for i in range(0, n_cands, cols_per_row):
            cols = st.columns(cols_per_row)
            row_cands = candidates[i:i+cols_per_row]
            for j, word in enumerate(row_cands):
                with cols[j]:
                    if st.button(word, key=f"btn_{word}_{i+j}", use_container_width=True):
                        st.session_state.current_sentence.append(word)
                        _update_state(llm)
                        st.rerun()

    st.write("<br>", unsafe_allow_html=True)

    # 📱 スマホ対応: アクションボタンを整理。UndoとHintを並べ、手動追加は単独に。
    col_undo, col_hint = st.columns(2)
    with col_undo:
        disabled_undo = len(st.session_state.current_sentence) == 0
        if st.button("⏪ 1つ戻る", use_container_width=True, disabled=disabled_undo):
            st.session_state.current_sentence.pop()
            _update_state(llm)
            st.rerun()
            
    with col_hint:
        hint_label = "💡 ヒントを隠す" if st.session_state.show_ghost else "💡 ヒントを見る"
        if st.button(hint_label, use_container_width=True):
            st.session_state.show_ghost = not st.session_state.show_ghost
            st.rerun()

    with st.popover("➕ 自由に単語を追加する", use_container_width=True):
        with st.form("manual_input_form", clear_on_submit=True):
            # スマホでも入力欄を大きく確保
            cols_form = st.columns([3, 1]) 
            with cols_form[0]:
                manual_word = st.text_input("自由に単語を追加", placeholder="例: very", label_visibility="collapsed")
            with cols_form[1]:
                submit_btn = st.form_submit_button("追加", use_container_width=True)
            
            if submit_btn and manual_word.strip():
                words = manual_word.strip().split()
                st.session_state.current_sentence.extend(words)
                _update_state(llm)
                st.rerun()

    st.write("<br><br>", unsafe_allow_html=True)

    # 📱 スマホ対応: 完成ボタンは一番下で「全幅」にして押しやすくする
    disabled_complete = len(st.session_state.current_sentence) == 0
    if st.button("🏁 完成して講評を見る", type="primary", use_container_width=True, disabled=disabled_complete):
        with st.spinner("AI先生があなたの英文を採点中..."):
            feedback = generate_feedback(
                llm, 
                st.session_state.japanese_goal, 
                st.session_state.current_sentence
            )
            st.session_state.feedback = feedback
        st.session_state.step = 2
        st.rerun()

def render_completion_screen():
    st.balloons()
    st.success("🎉 お疲れ様でした！パズル完了です。")
    
    st.markdown("### 🎯 言いたいこと (目標)")
    st.markdown(f"> {st.session_state.japanese_goal}")
    
    final_sentence = ' '.join(st.session_state.current_sentence)
    
    st.markdown("### ✍️ あなたが作った英文")
    st.markdown(f"<div style='font-size: 28px; font-weight: bold; color: #1E88E5; padding: 10px 0;'>{final_sentence}</div>", unsafe_allow_html=True)
    
    st.markdown("### 👩‍🏫 AI先生からの講評")
    st.info(f"{st.session_state.feedback}")

    st.write("---")
    
    # 🌐 アプリのURL（本番環境に公開したら、ここにそのURLを入れます）
    app_url = "https://wordflow-english.streamlit.app/" 
    
    # SNSシェア用のテキストを作成
    tweet_text = (
        f"🧩 WordFlow Englishでパズルを完成させたよ！\n\n"
        f"🎯 {st.session_state.japanese_goal}\n"
        f"✍️ {final_sentence}\n\n"
        f"#WordFlowEnglish #英語学習\n"
    )
    
    # URLエンコード（日本語や記号をURLで送れる形式に変換）
    encoded_text = urllib.parse.quote(tweet_text)
    encoded_url = urllib.parse.quote(app_url)
    
    # 🔗 Xのシェア用URLを生成
    twitter_share_url = f"https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}"
    
    # 📱 スマホ対応: 均等2列にして「新しく作る」と「シェア」を並べる
    col_reset, col_share = st.columns(2)
    
    with col_reset:
        if st.button("🔄 新しく文を作る", type="primary", use_container_width=True):
            reset_session_state()
            
            # テキストエリアの「前回の記憶」を強制的に消去し、例文を再抽選させる
            keys_to_clear = ["input_text_key", "stt_goal_output", "random_preset"]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
                    
            st.rerun()
            
    with col_share:
        st.link_button("𝕏 でシェアする", url=twitter_share_url, use_container_width=True)
