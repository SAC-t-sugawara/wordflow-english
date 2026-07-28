import streamlit as st
import random
from streamlit_mic_recorder import speech_to_text
from src.llm_engine import ask_local_llm, generate_correct_sentence

# 🌐 グローバル対応の言語リスト
LANGUAGES = ["Japanese (日本語)", "English (英語)", "Chinese (中国語)", "Korean (韓国語)"]

# 各言語ごとのランダム例文辞書（35個に拡充）
PRESETS = {
    "Japanese (日本語)": [
        "今日映画を見に行きたいな", "新しいイヤホンが欲しいです", "明日は晴れるといいな", 
        "週末は友達とランチに行きます", "昨日はたくさん寝ました", "おすすめのレストランを教えてください",
        "これを試着してもいいですか？", "お会計を別々にできますか？", "道に迷ってしまいました",
        "コーヒーを一杯ください", "お腹が空きました", "今は何時ですか？",
        "日本語を勉強しています", "趣味は何ですか？", "ちょっと手伝ってもらえますか？",
        "ここに座ってもいいですか？", "名前を教えてください", "少し疲れました",
        "気分が悪いです", "駅はどこにありますか？", "写真を撮ってもいいですか？",
        "これを買いたいです", "クレジットカードは使えますか？", "安くしてもらえますか？",
        "予約をしたいのですが", "空港までどのくらいかかりますか？", "パスポートを失くしました",
        "助けてください！", "今日はとても暑いですね", "週末は何をしますか？",
        "家族は元気ですか？", "音楽を聞くのが好きです", "仕事を探しています",
        "また会いましょう", "お誕生日おめでとう！"
    ],
    "English (英語)": [
        "I want to go see a movie today.", "I want new earphones.", "I hope it's sunny tomorrow.",
        "I'm going to have lunch with my friend this weekend.", "I slept a lot yesterday.",
        "Could you recommend a good restaurant?", "Can I try this on?", "Can we pay separately?",
        "I got lost.", "A cup of coffee, please.", "I'm hungry.", "What time is it now?",
        "I'm studying Japanese.", "What are your hobbies?", "Could you help me for a moment?",
        "Can I sit here?", "Please tell me your name.", "I'm a little tired.",
        "I feel sick.", "Where is the station?", "Can I take a photo?",
        "I want to buy this.", "Can I use a credit card?", "Can you give me a discount?",
        "I'd like to make a reservation.", "How long does it take to the airport?", "I lost my passport.",
        "Help me!", "It's very hot today, isn't it?", "What are you doing this weekend?",
        "How is your family?", "I like listening to music.", "I'm looking for a job.",
        "See you again.", "Happy birthday!"
    ],
    "Chinese (中国語)": [
        "今天想去看电影。", "我想要新耳机。", "希望明天是晴天。",
        "周末要和朋友去吃午饭。", "昨天睡了很久。", "请推荐一家好餐厅。",
        "我可以试穿这个吗？", "可以分开结账吗？", "我迷路了。",
        "请给我一杯咖啡。", "我饿了。", "现在几点？",
        "我正在学习日语。", "你的爱好是什么？", "你能帮我一下吗？",
        "我可以坐在这里吗？", "请告诉我你的名字。", "我有点累了。",
        "我感觉不舒服。", "车站在哪里？", "可以拍照吗？",
        "我想买这个。", "可以使用信用卡吗？", "能便宜一点吗？",
        "我想预订。", "去机场要多长时间？", "我的护照丢了。",
        "救命！", "今天天气很热，不是吗？", "这周末你做什么？",
        "你的家人好吗？", "我喜欢听音乐。", "我正在找工作。",
        "再见。", "生日快乐！"
    ],
    "Korean (韓国語)": [
        "오늘 영화 보러 가고 싶어.", "새 이어폰을 갖고 싶어요.", "내일은 맑았으면 좋겠다.",
        "주말에 친구랑 점심 먹으러 가요.", "어제는 많이 잤어요.", "추천할 만한 식당이 있나요?",
        "이거 입어봐도 되나요?", "계산 따로 할 수 있나요?", "길을 잃었어요.",
        "커피 한 잔 주세요.", "배고파요.", "지금 몇 시예요?",
        "일본어를 공부하고 있어요.", "취미가 뭐예요?", "잠시만 도와주실 수 있나요?",
        "여기 앉아도 될까요?", "이름을 알려주세요.", "조금 피곤해요.",
        "몸 상태가 안 좋아요.", "역이 어디에 있나요?", "사진 찍어도 될까요?",
        "이거 사고 싶어요.", "신용카드 되나요?", "깎아주실 수 있나요?",
        "예약하고 싶습니다만.", "공항까지 얼마나 걸려요?", "여권을 잃어버렸어요.",
        "도와주세요!", "오늘은 정말 덥네요.", "이번 주말에 뭐 해요?",
        "가족들은 잘 지내나요?", "음악 듣는 것을 좋아해요.", "일자리를 찾고 있어요.",
        "다음에 또 봐요.", "생일 축하해요!"
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

    # === (上のプルダウン設定のコードはそのまま) ===

    # 選択された言語をセッションに保存（llm_engineで使います）
    st.session_state.source_lang = source_lang

    # 選択された入力言語に合わせてランダム例文をセット
    if "current_preset_lang" not in st.session_state or st.session_state.current_preset_lang != source_lang:
        # 言語が変わったので新しい例文を抽選
        new_preset = random.choice(PRESETS[source_lang])
        st.session_state.random_preset = new_preset
        st.session_state.current_preset_lang = source_lang 
        
        # テキストエリアの「記憶」を強制的に新しい例文で上書きする！
        st.session_state.input_text_key = new_preset
        
        # マイク入力の記憶が残っていればそれも消す
        if 'stt_goal_output' in st.session_state:
            del st.session_state['stt_goal_output']

    with st.container(border=True):
        # value の指定を少しシンプルにします
        st.text_area(
            "Text Input", 
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

    # 🎤 マイク入力の結果をテキストエリアに反映する
    if st.session_state.get('stt_goal_output'):
        st.session_state.input_text_key = st.session_state.stt_goal_output
        del st.session_state['stt_goal_output']

    with st.container(border=True):
        st.text_area(
            "Text Input", 
            height=100,
            label_visibility="collapsed",
            placeholder=f"Please enter {source_lang.split(' ')[0]} here...",
            key="input_text_key"  
        )

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
