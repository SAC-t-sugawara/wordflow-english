import os
import random
import logging
import json
from datetime import datetime
import streamlit as st

from google import genai
from google.genai import types

from src.distractor_manager import get_distractors 

# --- ログ設定などは変更なし ---
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

# --- API設定も変更なし ---
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

client = genai.Client(api_key=API_KEY)

MODEL_NAME = None
try:
    MODEL_NAME = st.secrets.get("GEMINI_MODEL_NAME")
except Exception:
    pass

if not MODEL_NAME:
    MODEL_NAME = os.environ.get("GEMINI_MODEL_NAME")

if not MODEL_NAME:
    MODEL_NAME = "gemini-3.5-flash"

@st.cache_resource
def load_model():
    return client

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌐 多言語対応された関数群（セッションから言語を取得）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _get_langs():
    """セッションから現在の言語の英語名（Japanese, English等）を取得する補助関数"""
    src = st.session_state.get("source_lang", "Japanese (日本語)").split(" ")[0]
    tgt = st.session_state.get("target_lang", "English (英語)").split(" ")[0]
    return src, tgt

def generate_dynamic_distractors(client_obj, correct_word: str, japanese_goal: str) -> list:
    src_lang, tgt_lang = _get_langs()
    
    prompt = f"""
    You are an excellent question creator for a language learning app.
    The user is trying to translate the {src_lang} sentence "{japanese_goal}" into {tgt_lang}.
    The correct next word (or chunk) they need to select is "{correct_word}".
    
    Think of exactly 5 "distractor" options in {tgt_lang} that a learner might mistakenly choose.
    They should have a similar part of speech, grammar, or length.
    * Output ONLY the 5 distractors separated by commas. No explanations.
    """
    try:
        response = client_obj.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7, max_output_tokens=40)
        )
        words = [w.strip() for w in response.text.split(",") if w.strip()]
        return words
    except Exception as e:
        error_logger.error(f"Gemini API Error (distractors): {e}")
        return []

def generate_correct_sentence(client_obj, japanese_goal):
    src_lang, tgt_lang = _get_langs()
    
    prompt = f"""Translate {src_lang} to {tgt_lang}. 
Output the {tgt_lang} sentence divided into natural chunks (1-3 words) using the pipe character '|'. 
Output ONLY the text with '|'. No explanation.

{src_lang}: {japanese_goal}
{tgt_lang}: """
    
    try:
        response = client_obj.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=80)
        )
        sentence = response.text.strip().strip('"\'')
    except Exception as e:
        error_logger.error(f"Gemini API Error (generate_correct): {e}")
        sentence = "Error | occurred."

    if "|" in sentence:
        words = [chunk.strip() for chunk in sentence.split("|") if chunk.strip()]
    else:
        words = sentence.split()
        
    log_event("generate_correct_sentence", {"goal": japanese_goal, "src": src_lang, "tgt": tgt_lang}, {"chunks": words})
    return words

def recalculate_correct_sentence(client_obj, japanese_goal, current_sentence_words):
    src_lang, tgt_lang = _get_langs()
    current_str = " ".join(current_sentence_words)
    
    prompt = f"""Translate {src_lang} to {tgt_lang}. 
The user is translating "{japanese_goal}".
They have already typed: "{current_str}"

Output the FULL {tgt_lang} sentence that naturally continues and completes their thought.
You MUST start your sentence exactly with "{current_str}".
Divide into natural chunks using '|'. Output ONLY the text with '|'. No explanation.

{src_lang}: {japanese_goal}
Typed: {current_str}
{tgt_lang}: """
    
    try:
        response = client_obj.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=80)
        )
        sentence = response.text.strip().strip('"\'')
    except Exception as e:
        error_logger.error(f"Gemini API Error (recalculate): {e}")
        return current_sentence_words + ["(Error)"]

    if "|" in sentence:
        words = [chunk.strip() for chunk in sentence.split("|") if chunk.strip()]
    else:
        words = sentence.split()
        
    log_event("recalculate_correct_sentence", {"goal": japanese_goal, "typed": current_str}, {"chunks": words})
    return words

def _translate_current(client_obj, sentence_words: list) -> str:
    if not sentence_words:
        return "(Not started yet)"

    src_lang, tgt_lang = _get_langs()
    sentence = " ".join(sentence_words)
    
    prompt = f"""Translate {tgt_lang} to {src_lang}. Output ONLY the {src_lang} translation. One line only.

{tgt_lang}: {sentence}
{src_lang}: """

    try:
        response = client_obj.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=60)
        )
        result = response.text.strip()
    except Exception as e:
        error_logger.error(f"Gemini API Error (translate_current): {e}")
        result = ""

    log_event("translate_current", {"current_sentence": sentence}, {"translation": result})

    if not result:
        return f"({sentence})"

    check = result.replace(" ", "").replace(".", "").replace(",", "").replace("'", "").replace("?","").replace("!","")
    if check.isascii() and len(check) > 0 and src_lang != "English":
        return "(Translating...)"

    return result

def ask_local_llm(client_obj, sentence, japanese_goal, correct_next_word: str | None = None):
    if correct_next_word:
        key = correct_next_word.lower()
        distractors = generate_dynamic_distractors(client_obj, key, japanese_goal)
        
        if len(distractors) < 5:
            distractors = get_distractors(correct_next_word)
            
        distractors = [w for w in distractors if w.lower() != key]
        
        extras = ["the", "a", "is", "to", "in", "do", "have", "of", "and", "that"]
        for w in extras:
            if len(distractors) >= 5:
                break
            if w.lower() != key and w not in distractors:
                distractors.append(w)
                
        candidates = distractors[:5] + [correct_next_word]
    else:
        candidates = get_distractors("")[:5] + ["(Complete!)"]

    random.shuffle(candidates)

    correct_words = st.session_state.get("correct_words", [])
    current_len = len(sentence)

    if correct_words and current_len < len(correct_words):
        ghost_text = " ".join(correct_words[current_len:])
    elif correct_words and current_len >= len(correct_words):
        ghost_text = "🎉 Complete!"
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
        return "No sentence created."

    src_lang, tgt_lang = _get_langs()

    prompt = f"""You are a strict but friendly language teacher.
The user tried to translate the {src_lang} "Goal" into {tgt_lang}, but their "Sentence" might be completely wrong.
Score their sentence (0-100), explain the mistakes clearly in {src_lang}, and MUST provide the correct translation in {tgt_lang}.
IMPORTANT: Start your response exactly with "【Score & Feedback】".

Goal ({src_lang}): {japanese_goal}
Sentence ({tgt_lang}): {user_sentence}
Teacher: """
    
    try:
        response = client_obj.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3, max_output_tokens=250)
        )
        feedback = response.text.strip()
    except Exception as e:
        error_logger.error(f"Gemini API Error (generate_feedback): {e}")
        feedback = "【Score & Feedback】\nCommunication error occurred."

    log_event("generate_feedback", {"goal": japanese_goal, "sentence": user_sentence}, {"feedback": feedback})
    return feedback
