import streamlit as st
import random
from streamlit_mic_recorder import speech_to_text
from src.llm_engine import ask_local_llm, generate_correct_sentence

# 🌐 グローバル対応の言語リスト
LANGUAGES = ["Japanese (日本語)", "English (英語)", "Chinese (中国語)", "Korean (韓国語)"]

# 各言語ごとのランダム例文辞書（ハードコードで爆速表示）
PRESETS = {
    "Japanese (日本語)": [
        "今日映画を見に行きたいな", "新しいイヤホンが欲しいです", "明日は晴れるといいな", 
        "週末は友達とランチに行きます", "昨日はたくさん寝ました", "おすすめのレストランを教えてください",
        "これを試着してもいいですか？", "お会計を別々にできますか？", "道に迷ってしまいました"
    ],
    "English (英語)": [
        "I want to go see a movie today.", "I want new earphones.", "I hope it's sunny tomorrow.",
        "I'm going to have lunch with my friend this weekend.", "I slept a lot yesterday.",
        "Could you recommend a good restaurant?", "Can I try this on?", "Can we pay separately?",
        "I got lost."
    ],
    "Chinese (中国語)": [
        "今天想去看电影。", "我想要新耳机。", "希望明天是晴天。",
        "周末要和朋友去吃午饭。", "昨天睡了很久。", "请推荐一家好餐厅。",
        "我可以试穿这个吗？", "可以分开结账吗？", "我迷路了。"
    ],
    "Korean (韓国語)": [
        "오늘 영화 보러 가고 싶어.", "새 이어폰을 갖고 싶어요.", "내일은 맑았으면 좋겠다.",
        "주말에 친구랑 점심 먹으러 가요.", "어제는 많이 잤어요.", "추천할 만한 식당이 있나요?",
        "이거 입어봐도 되나요?", "계산 따로 할 수 있나요?", "길을 잃었어요."
    ]
}

def render_input_form(llm):
    st.markdown("<h3 style='text-align: center;'>🎯 What do you want to say?</h3>", unsafe_allow_html=True)
    
    # 🌟 言語選択プルダウン
    col_src, col_arrow, col_tgt = st.columns([3, 1, 3])
    with col_src:
        source_lang = st.selectbox("Input Language", LANGUAGES, index=0)
    with col_arrow:
        st.markdown("<div style='text-align: center; font-size: 24px; padding-top: 25px;'>➡️</div>", unsafe_allow_html=True)
    with col_tgt:
        target_lang = st.selectbox("Puzzle Language", LANGUAGES, index=1)

    if source_lang == target_lang:
        st.warning("⚠️ Input and Puzzle languages are the same. Please select different languages.")

    # 選択された言語をセッションに保存（llm_engineに渡す用）
    st.session_state.source_lang = source_lang
    st.session_state.target_lang = target_lang

    # 選択された入力言語に合わせてランダム例文をセット
    if "current_preset_lang" not in st.session_state or st.session_state.current_preset_lang != source_lang:
        st.session_state.random_preset = random.choice(PRESETS[source_lang])
        st.session_state.current_preset_lang = source_lang # 言語が変わった時だけ再抽選

    with st.container(border=True):
        default_text = st.session_state.stt_goal_output if 'stt_goal_output' in st.session_state else st.session_state.random_preset
            
        st.text_area(
            "Text Input", 
            value=default_text, 
            height=100,
            label_visibility="collapsed",
            placeholder=f"Please enter {source_lang.split(' ')[0]} here...",
            key="input_text_key"
        )

        col_mic, col_btn = st.columns(2)
        with col_mic:
            # マイクの言語コードを判定
            mic_lang = 'ja'
            if "English" in source_lang: mic_lang = 'en'
            elif "Chinese" in source_lang: mic_lang = 'zh'
            elif "Korean" in source_lang: mic_lang = 'ko'

            text_from_mic = speech_to_text(
                language=mic_lang,
                start_prompt="🎤 Voice Input", 
                stop_prompt="⏹️ Recording...", 
                just_once=True, 
                key='stt_goal'
            )
        with col_btn:
            submit_btn = st.button("Create Puzzle 🧩", type="primary", use_container_width=True, disabled=(source_lang == target_lang))

    if text_from_mic:
        st.session_state.stt_goal_output = text_from_mic
        st.rerun()

    if submit_btn:
        latest_goal = st.session_state.input_text_key
        if not latest_goal.strip():
            st.warning("⚠️ Please enter some text!")
            st.stop()

        # 変数名は「japanese_goal」のまま使いますが、中身は英語や中国語が入ります
        st.session_state.japanese_goal = latest_goal 
        st.session_state.current_sentence = []
        st.session_state.show_ghost = False

        tgt_short = target_lang.split(' ')[0] # "English" などを取り出す
        with st.spinner(f"AI is preparing the {tgt_short} puzzle..."):
            
            # ⚠️ 注意: ここはまだ修正前の関数呼び出しです。後で llm_engine.py 側を多言語対応させます。
            correct_words = generate_correct_sentence(llm, latest_goal)
            st.session_state.correct_words = correct_words

            first_correct = correct_words[0] if correct_words else None
            res = ask_local_llm(llm, [], latest_goal, correct_next_word=first_correct)
            
            st.session_state.candidates = res.get("candidates", [])
            st.session_state.ghost_text = res.get("ghost_text", "")
            st.session_state.translation = "(Start Here)"

        st.session_state.step = 1
        st.rerun()

def render_current_goal():
    st.markdown("### 🎯 Goal")
    st.info(f"**{st.session_state.japanese_goal}**")
