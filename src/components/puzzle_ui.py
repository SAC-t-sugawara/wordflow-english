import streamlit as st
import urllib.parse
from src.llm_engine import ask_local_llm, generate_feedback, recalculate_correct_sentence
from src.state_manager import reset_session_state

def _update_state(llm):
    current_sentence = st.session_state.current_sentence
    correct_words = st.session_state.get("correct_words", [])

    # 🚗 1. ルートチェック（ユーザーの入力が正解レールから外れていないか？）
    is_on_route = True
    for i, word in enumerate(current_sentence):
        # 1単語ずつ比較し、大文字小文字の違いを無視してチェック
        if i >= len(correct_words) or word.lower() != correct_words[i].lower():
            is_on_route = False
            break

    # 🔄 2. ルートを外れたらカーナビ発動！（自動リルート）
    if not is_on_route and len(current_sentence) > 0:
        with st.spinner("AIがルートを再計算中... 🔄"):
            new_correct_words = recalculate_correct_sentence(llm, st.session_state.japanese_goal, current_sentence)
            st.session_state.correct_words = new_correct_words
            correct_words = new_correct_words
            st.toast("ルートが再計算されました！🔄", icon="🤖") # 画面右下に小さく通知を出す

    # 🎯 3. 次の正解単語の取得
    next_index = len(current_sentence)
    if next_index < len(correct_words):
        next_correct = correct_words[next_index]
    else:
        next_correct = None 

    # 🧩 4. 通常の翻訳とダミー生成
    with st.spinner("AIが翻訳・準備中..."):
        res = ask_local_llm(
            llm,
            current_sentence,
            st.session_state.japanese_goal,
            correct_next_word=next_correct
        )
        st.session_state.candidates = res.get("candidates", [])
        st.session_state.ghost_text = res.get("ghost_text", "")
        st.session_state.translation = res.get("translation", "")

def render_puzzle_area(llm):
    # パズルボタン用のCSS
    st.markdown("""
    <style>
    div[data-testid="stButton"] > button[kind="secondary"] {
        border-radius: 12px; border: 2px solid #CBD5E1; background-color: white; color: #334155;
        font-size: 16px !important; font-weight: bold; box-shadow: 0 4px 0px #CBD5E1; transition: all 0.1s ease;
        padding-top: 8px; padding-bottom: 8px;
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

    current_str = " ".join(st.session_state.current_sentence)
    ghost_display = st.session_state.ghost_text if st.session_state.show_ghost else ""

    # 💡 枠のパディングとマージンを小さくしてスリム化
    sentence_html = f"""
    <div style="font-size: 24px; padding: 12px; background-color: #f8fafc;
                border-radius: 12px; border: 2px solid #cbd5e1; margin-bottom: 10px;
                min-height: 60px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <span style="color: #0f172a; font-weight: 800;">{current_str}</span>
        <span style="color: #94a3b8; font-style: italic; opacity: 0.7;"> {ghost_display}</span>
    </div>
    """
    st.markdown(sentence_html, unsafe_allow_html=True)

    if st.session_state.candidates:
        candidates = st.session_state.candidates
        n_cands = len(candidates)
        
        if n_cands <= 4:
            cols_per_row = 2
        else:
            cols_per_row = 3
            
        for i in range(0, n_cands, cols_per_row):
            cols = st.columns(cols_per_row)
            row_cands = candidates[i:i+cols_per_row]
            for j, word in enumerate(row_cands):
                with cols[j]:
                    if st.button(word, key=f"btn_{word}_{i+j}", use_container_width=True):
                        st.session_state.current_sentence.append(word)
                        _update_state(llm)
                        st.rerun()

    # 🌟 アクションボタンを3列に整理（戻る / ヒント / 完成）
    col_undo, col_hint, col_complete = st.columns(3)
    
    with col_undo:
        disabled_undo = len(st.session_state.current_sentence) == 0
        if st.button("⏪ 戻る", use_container_width=True, disabled=disabled_undo):
            st.session_state.current_sentence.pop()
            _update_state(llm)
            st.rerun()
            
    with col_hint:
        hint_label = "💡 隠す" if st.session_state.show_ghost else "💡 ヒント"
        if st.button(hint_label, use_container_width=True):
            st.session_state.show_ghost = not st.session_state.show_ghost
            st.rerun()

    with col_complete:
        disabled_complete = len(st.session_state.current_sentence) == 0
        if st.button("🏁 完成！", type="primary", use_container_width=True, disabled=disabled_complete):
            with st.spinner("AI先生が採点中..."):
                feedback = generate_feedback(llm, st.session_state.japanese_goal, st.session_state.current_sentence)
                st.session_state.feedback = feedback
            st.session_state.step = 2
            st.rerun()

    # 手動追加ポップオーバー
    with st.popover("➕ 自由に単語を追加", use_container_width=True):
        with st.form("manual_input_form", clear_on_submit=True):
            cols_form = st.columns([3, 1]) 
            with cols_form[0]:
                manual_word = st.text_input("追加", placeholder="例: very", label_visibility="collapsed")
            with cols_form[1]:
                submit_btn = st.form_submit_button("追加", use_container_width=True)
            if submit_btn and manual_word.strip():
                st.session_state.current_sentence.extend(manual_word.strip().split())
                _update_state(llm)
                st.rerun()

def render_completion_screen():
    # 🌟 シェアボタンの高さを赤ボタンに合わせるCSS
    st.markdown("""
    <style>
    a[data-testid="stLinkButton"] {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 42px;
        border-radius: 12px;
        border: 2px solid #CBD5E1;
        font-weight: bold;
        text-decoration: none;
        color: #334155;
    }
    a[data-testid="stLinkButton"]:hover {
        border-color: #1E88E5;
        color: #1E88E5;
    }
    </style>
    """, unsafe_allow_html=True)

    st.balloons()
    st.success("🎉 お疲れ様でした！パズル完了です。")
    
    st.markdown("### 🎯 言いたいこと (目標)")
    st.markdown(f"> {st.session_state.japanese_goal}")
    
    final_sentence = ' '.join(st.session_state.current_sentence)
    
    st.markdown("### ✍️ あなたが作った英文")
    st.markdown(f"<div style='font-size: 28px; font-weight: bold; color: #1E88E5; padding: 10px 0;'>{final_sentence}</div>", unsafe_allow_html=True)
    
    st.markdown("### 👩‍🏫 AI先生からの講評")
    formatted_feedback = st.session_state.feedback.replace("【", "\n\n【").strip()
    st.info(formatted_feedback)

    st.write("---")
    
    app_url = "https://wordflow-english.streamlit.app/" 
    tweet_text = f"🧩 WordFlow Englishでパズルを完成させたよ！\n\n🎯 {st.session_state.japanese_goal}\n✍️ {final_sentence}\n\n#WordFlowEnglish #英語学習\n"
    encoded_text = urllib.parse.quote(tweet_text)
    encoded_url = urllib.parse.quote(app_url)
    twitter_share_url = f"https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}"
    
    col_reset, col_share = st.columns(2)
    
    with col_reset:
        if st.button("🔄 新しく文を作る", type="primary", use_container_width=True):
            reset_session_state()
            keys_to_clear = ["input_text_key", "stt_goal_output", "random_preset"]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
            
    with col_share:
        st.link_button("𝕏 でシェアする", url=twitter_share_url, use_container_width=True)
