import os
import random
import logging
import json
from datetime import datetime
import streamlit as st

from google import genai
from google.genai import types

# ダミー単語の生成ロジックを別ファイルから読み込む
from src.distractor_manager import get_distractors 

# ---------------------------------------------------------
# 📊 データ分析・運用に特化したログ設定
# ---------------------------------------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

error_logger = logging.getLogger("app_error")
error_logger.setLevel(logging.ERROR)
if not error_logger.handlers:
    eh = logging.FileHandler(os.path.join(LOG_DIR, "error.log"), encoding="utf-8")
    eh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    error_logger.addHandler(eh)

analytics_logger = logging.getLogger("analytics")
analytics_logger.setLevel(logging.INFO)
if not analytics_logger.handlers:
    ah = logging.FileHandler(os.path.join(LOG_DIR, "analytics.jsonl"), encoding="utf-8")
    ah.setFormatter(logging.Formatter('%(message)s'))
    analytics_logger.addHandler(ah)

def log_event(process_name: str, input_data: dict, output_data: dict | None = None):
    try:
        record = {
            "timestamp": datetime.now().isoformat(),
            "process": process_name,
            "input": input_data,
            "output": output_data or {}
        }
        analytics_logger.info(json.dumps(record, ensure_ascii=False))
    except Exception as e:
        error_logger.error(f"ログ記録中にエラー発生: {e}")
# ---------------------------------------------------------

# APIキーの安全な設定
API_KEY = None
try:
    API_KEY = st.secrets.get("GEMINI_API_KEY")
except Exception:
    pass

if not API_KEY:
    API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("Gemini APIキーが設定されていません。.streamlit/secrets.toml を確認してください。")
    st.stop()

# 最新のGenAIクライアントの初期化
client = genai.Client(api_key=API_KEY)

# 🌟 モデル名の安全な読み込み
MODEL_NAME = None
try:
    MODEL_NAME = st.secrets.get("GEMINI_MODEL_NAME")
except Exception:
    pass

if not MODEL_NAME:
    MODEL_NAME = os.environ.get("GEMINI_MODEL_NAME")

if not MODEL_NAME:
    MODEL_NAME = "gemini-3.5-flash"
    print(f"⚠️ モデル名が設定されていないため、デフォルト({MODEL_NAME})を使用します")


@st.cache_resource
def load_model():
    return client

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🤖 新規追加: LLMによる動的ダミー生成関数
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def generate_dynamic_distractors(client_obj, correct_word: str, japanese_goal: str) -> list:
    """LLMに文脈に合ったダミー単語(チャンク)を5つ考えさせる"""
    prompt = f"""
    あなたは英語学習アプリの優秀な問題作成者です。
    ユーザーは「{japanese_goal}」という日本語を英訳しようとしています。
    次に選ぶべき正解の単語（またはチャンク）は「{correct_word}」です。
    
    この正解と似た品詞、文法、文字数で、学習者が思わず間違えて選びそうな「ダミーの選択肢」を正確に5つ考えてください。
    ※必ず英語のみ、カンマ区切りで出力してください。説明は一切不要です。
    例: liked, wanting, have to, see, taking
    """
    try:
        response = client_obj.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7, max_output_tokens=30)
        )
        words = [w.strip() for w in response.text.split(",") if w.strip()]
        return words
    except Exception as e:
        error_logger.error(f"Gemini API Error (generate_dynamic_distractors): {e}")
        return []

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_correct_sentence(client_obj, japanese_goal):
    prompt = f"""Translate Japanese to English. Output the English sentence divided into natural chunks (1-3 words) using the pipe character '|'. Output ONLY the text with '|'. No explanation.

Example 1:
Japanese: おはようございます、元気ですか？
English: Good morning, | how are you?

Example 2:
Japanese: 私はピザが大好きです。
English: I love | pizza | very much.

Example 3:
Japanese: 今日映画を見に行きたいな。
English: I want to go | to see | a movie | today.

Japanese: {japanese_goal}
English: """
    
    try:
        response = client_obj.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=80)
        )
        sentence = response.text.strip().strip('"\'')
    except Exception as e:
        error_logger.error(f"Gemini API Error (generate_correct_sentence): {e}")
        sentence = "I want to | try this."

    if "|" in sentence:
        words = [chunk.strip() for chunk in sentence.split("|") if chunk.strip()]
    else:
        words = sentence.split()
        
    log_event(
        process_name="generate_correct_sentence",
        input_data={"japanese_goal": japanese_goal},
        output_data={"raw_sentence": sentence, "chunks": words}
    )
        
    return words if words else ["I want to", "try this."]

def _translate_current(client_obj, sentence_words: list) -> str:
    if not sentence_words:
        return "（まだ入力なし）"

    sentence = " ".join(sentence_words)
    prompt = f"""Translate English to Japanese. Output ONLY the Japanese translation. One line only.

Example 1:
English: Good morning
Japanese: おはようございます

Example 2:
English: I love pizza very much
Japanese: 私はピザが大好きです

English: {sentence}
Japanese: """

    try:
        response = client_obj.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=60)
        )
        result = response.text.strip()
    except Exception as e:
        error_logger.error(f"Gemini API Error (_translate_current): {e}")
        result = ""

    log_event(
        process_name="translate_current",
        input_data={"current_sentence": sentence},
        output_data={"translated_japanese": result}
    )

    if not result:
        return f"({sentence})"

    check = result.replace(" ", "").replace(".", "").replace(",", "").replace("'", "").replace("?","").replace("!","")
    if check.isascii() and len(check) > 0:
        return "（翻訳生成中...）"

    return result

def ask_local_llm(client_obj, sentence, japanese_goal, correct_next_word: str | None = None):
    """パズル画面で表示する候補（ダミー含む）とヒント、現在の翻訳を返す"""
    if correct_next_word:
        key = correct_next_word.lower()
        
        # 🌟 1. まずはLLMに「文脈に合ったダミー」を作らせてみる
        distractors = generate_dynamic_distractors(client_obj, key, japanese_goal)
        
        # 🌟 2. もしLLMが失敗した（または数が足りない）場合は、従来の辞書を使う
        if len(distractors) < 5:
            distractors = get_distractors(correct_next_word)
            
        # 自分がダミーに入らないように除外し、確実に5つにする
        distractors = [w for w in distractors if w.lower() != key]
        
        # もしそれでも足りなければ適当な単語を足す（フェイルセーフ）
        extras = ["the", "a", "is", "to", "in", "do", "have"]
        for w in extras:
            if len(distractors) >= 5:
                break
            if w.lower() != key and w not in distractors:
                distractors.append(w)
                
        candidates = distractors[:5] + [correct_next_word]
    else:
        candidates = get_distractors("")[:5] + ["(完成！)"]

    random.shuffle(candidates)

    correct_words = st.session_state.get("correct_words", [])
    current_len = len(sentence)

    if correct_words and current_len < len(correct_words):
        ghost_text = " ".join(correct_words[current_len:])
    elif correct_words and current_len >= len(correct_words):
        ghost_text = "🎉 完成！"
    else:
        ghost_text = "..."

    translation = _translate_current(client_obj, sentence)

    return {
        "candidates": candidates,
        "ghost_text": ghost_text,
        "translation": translation,
    }

def generate_feedback(client_obj, japanese_goal, sentence_words):
    user_sentence = " ".join(sentence_words)
    if not user_sentence:
        return "英文が入力されていません。次は単語を選んで文を作ってみましょう！"

    prompt = f"""You are a strict but friendly English teacher.
The user tried to translate the Japanese "Goal" into English, but their "Sentence" might be completely wrong or nonsense.
Score their sentence (0-100), explain the mistakes in Japanese, and MUST provide the correct translation in ENGLISH.
IMPORTANT: Start your response exactly with "【評価】".

Example 1:
Goal: 今日映画を見に行きたいな
Sentence: I want go to movie
Teacher:
【評価】70点！惜しいです。
【解説】「want go」ではなく間に「to」を入れて「want to go」にしましょう。また映画には「a movie」と冠詞をつけると自然です。
【模範解答】I want to go see a movie today.

Goal: {japanese_goal}
Sentence: {user_sentence}
Teacher: """
    
    try:
        response = client_obj.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3, max_output_tokens=250)
        )
        feedback = response.text.strip()
        if not feedback.startswith("【評価】"):
            feedback = "【評価】\n" + feedback
    except Exception as e:
        error_logger.error(f"Gemini API Error (generate_feedback): {e}")
        feedback = "【評価】通信エラーが発生しました。もう一度お試しください。"

    log_event(
        process_name="generate_feedback",
        input_data={"japanese_goal": japanese_goal, "user_sentence": user_sentence},
        output_data={"feedback": feedback}
    )

    return feedback
