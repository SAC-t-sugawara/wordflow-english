import random

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ダミー単語ルックアップテーブル（基本辞書）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DISTRACTOR_MAP = {
    # 人称代名詞
    "i": ["he", "she", "we", "they"], "we": ["i", "he", "she", "they"],
    "he": ["i", "she", "we", "they"], "she": ["i", "he", "we", "they"],
    "they": ["i", "he", "she", "we"], "you": ["i", "he", "she", "they"],
    "my": ["your", "his", "her", "their"], "your": ["my", "his", "her", "our"],
    "it": ["he", "she", "they", "this"], "this": ["that", "the", "a", "it"],
    "that": ["this", "the", "a", "it"],
    # be動詞・助動詞
    "am": ["is", "are", "was", "be"], "is": ["am", "are", "was", "be"],
    "are": ["am", "is", "was", "be"], "was": ["am", "is", "are", "were"],
    "can": ["will", "should", "must", "may"], "will": ["can", "should", "must", "may"],
    "would": ["could", "should", "might", "will"], "could": ["would", "should", "might", "will"],
    "should": ["can", "will", "must", "may"], "must": ["can", "will", "should", "may"],
    # 一般動詞
    "want": ["like", "have", "love", "need"], "like": ["want", "have", "love", "enjoy"],
    "love": ["like", "want", "hate", "enjoy"], "go": ["come", "get", "run", "stay"],
    "see": ["watch", "look", "find", "meet"], "watch": ["see", "look", "find", "check"],
    "have": ["get", "take", "hold", "keep"], "get": ["have", "take", "find", "make"],
    "do": ["make", "have", "try", "use"], "make": ["do", "have", "take", "build"],
    # 前置詞・冠詞・接続詞
    "to": ["for", "in", "at", "of"], "for": ["to", "in", "at", "of"],
    "in": ["on", "at", "of", "to"], "on": ["in", "at", "of", "to"],
    "at": ["in", "on", "of", "to"], "of": ["in", "at", "for", "to"],
    "with": ["for", "to", "in", "by"], "from": ["to", "in", "at", "of"],
    "a": ["the", "an", "this", "that"], "an": ["a", "the", "this", "those"],
    "the": ["a", "an", "this", "these"],
    "and": ["or", "but", "so", "yet"], "but": ["and", "or", "so", "yet"],
    "or": ["and", "but", "so", "nor"], "so": ["and", "but", "or", "yet"],
    "because": ["so", "and", "but", "since"], "if": ["when", "while", "but", "so"],
    # 時間・疑問詞
    "today": ["tomorrow", "yesterday", "tonight", "now"],
    "what": ["where", "when", "how", "why"], "where": ["what", "when", "how", "who"],
    "when": ["what", "where", "how", "why"], "how": ["what", "where", "when", "why"],
}

def get_distractors(correct_word: str) -> list:
    """ルックアップテーブルと語尾推測からダミー4語を取得する関数"""
    if not correct_word:
        return ["the", "a", "in", "go"]

    # 余計な記号を消して小文字にする
    key = correct_word.lower().rstrip('.!?,;:\'"')

    # 1. まずは基本辞書をチェック
    if key in DISTRACTOR_MAP:
        result = DISTRACTOR_MAP[key].copy()
        random.shuffle(result)
        return result[:4]

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 2. 辞書に無い未知の単語に対する「賢い推測ロジック」
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pool = []

    # パターンA：進行形・動名詞 (-ing)
    if key.endswith("ing") and len(key) > 4:
        pool = ["playing", "running", "going", "making", "eating", "watching", "doing"]
    
    # パターンB：過去形・過去分詞 (-ed)
    elif key.endswith("ed") and len(key) > 3:
        pool = ["played", "wanted", "looked", "used", "worked", "tried", "called"]
    
    # パターンC：副詞 (-ly)
    elif key.endswith("ly") and len(key) > 3:
        pool = ["really", "slowly", "quickly", "usually", "hardly", "suddenly"]
    
    # パターンD：複数形・三単現のs (-s)
    elif key.endswith("s") and len(key) > 3:
        pool = ["apples", "cars", "books", "days", "things", "friends", "places"]
    
    # パターンE：形容詞・名詞など（汎用フォールバック）
    else:
        pool = [
            "beautiful", "great", "small", "book", "water", 
            "find", "always", "much", "time", "people", "way"
        ]

    # 自分がダミーに入らないように除外
    pool = [w for w in pool if w.lower() != key]

    # シャッフルして4つ選ぶ
    random.shuffle(pool)
    return pool[:4]