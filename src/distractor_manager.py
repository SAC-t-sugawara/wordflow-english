import random

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📖 ダミー単語ルックアップテーブル（超拡充版）
# ※常に5つ以上のダミーを返すため、各リストには多めに単語を用意しています
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DISTRACTOR_MAP = {
    # 主格・人称代名詞
    "i": ["he", "she", "we", "they", "you", "it", "this"],
    "we": ["i", "he", "she", "they", "you", "us", "our"],
    "he": ["i", "she", "we", "they", "you", "his", "him"],
    "she": ["i", "he", "we", "they", "you", "her", "hers"],
    "they": ["i", "he", "she", "we", "you", "them", "their"],
    "you": ["i", "he", "she", "they", "we", "your", "yours"],
    
    # 所有格・目的格
    "my": ["your", "his", "her", "their", "our", "mine", "me"],
    "your": ["my", "his", "her", "our", "their", "yours", "you"],
    "me": ["him", "her", "us", "them", "you", "my"],
    "him": ["me", "her", "us", "them", "you", "his"],
    "her": ["me", "him", "us", "them", "you", "hers"],
    
    # 指示代名詞
    "it": ["he", "she", "they", "this", "that", "those", "these"],
    "this": ["that", "the", "a", "it", "these", "those"],
    "that": ["this", "the", "a", "it", "which", "what"],
    
    # be動詞・助動詞
    "am": ["is", "are", "was", "be", "were", "been"],
    "is": ["am", "are", "was", "be", "were", "does"],
    "are": ["am", "is", "was", "be", "were", "do"],
    "was": ["am", "is", "are", "were", "been", "did"],
    "were": ["was", "are", "is", "am", "been", "did"],
    
    "can": ["will", "should", "must", "may", "could", "might"],
    "will": ["can", "should", "must", "may", "would", "shall"],
    "would": ["could", "should", "might", "will", "must", "can"],
    "could": ["would", "should", "might", "will", "can", "may"],
    "should": ["can", "will", "must", "may", "could", "would"],
    
    # 一般動詞（よく使うもの）
    "want": ["like", "have", "love", "need", "wish", "hope", "try"],
    "like": ["want", "have", "love", "enjoy", "prefer", "need", "feel"],
    "go": ["come", "get", "run", "stay", "walk", "move", "leave"],
    "see": ["watch", "look", "find", "meet", "hear", "notice"],
    "watch": ["see", "look", "find", "check", "notice", "view"],
    "have": ["get", "take", "hold", "keep", "make", "find"],
    "get": ["have", "take", "find", "make", "catch", "bring"],
    "do": ["make", "have", "try", "use", "play", "work"],
    "make": ["do", "have", "take", "build", "create", "let"],
    "take": ["get", "have", "make", "bring", "hold", "keep"],
    "think": ["know", "believe", "guess", "feel", "say"],
    
    # 前置詞・冠詞・接続詞
    "to": ["for", "in", "at", "of", "on", "from", "with"],
    "for": ["to", "in", "at", "of", "about", "with", "since"],
    "in": ["on", "at", "of", "to", "into", "inside", "during"],
    "on": ["in", "at", "of", "to", "over", "above", "upon"],
    "at": ["in", "on", "of", "to", "by", "around", "near"],
    "of": ["in", "at", "for", "to", "from", "about", "with"],
    "with": ["for", "to", "in", "by", "without", "from"],
    "from": ["to", "in", "at", "of", "since", "until", "by"],
    "about": ["for", "of", "on", "to", "with", "around"],
    
    "a": ["the", "an", "this", "that", "some", "any"],
    "an": ["a", "the", "this", "those", "some", "any"],
    "the": ["a", "an", "this", "these", "those", "that"],
    
    "and": ["or", "but", "so", "yet", "because", "if"],
    "but": ["and", "or", "so", "yet", "although", "though"],
    "because": ["so", "and", "but", "since", "as", "for"],
    "if": ["when", "while", "but", "so", "unless", "whether"],
    
    # 時間・疑問詞・その他副詞
    "today": ["tomorrow", "yesterday", "tonight", "now", "soon", "later"],
    "now": ["then", "today", "soon", "later", "already", "still"],
    "here": ["there", "where", "everywhere", "somewhere", "anywhere"],
    "what": ["where", "when", "how", "why", "who", "which"],
    "where": ["what", "when", "how", "who", "why", "which"],
    "when": ["what", "where", "how", "why", "who", "while"],
    "how": ["what", "where", "when", "why", "who", "much"],
    "very": ["really", "so", "too", "quite", "extremely", "much"],
}

def get_distractors(correct_word: str) -> list:
    """ルックアップテーブルと語尾・チャンク推測からダミー5語を取得する関数"""
    # エラー回避：空っぽの場合は汎用ダミーを5つ返す
    if not correct_word:
        return ["the", "a", "in", "go", "is"]

    key = correct_word.lower().rstrip('.!?,;:\'"')

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 1. 基本辞書をチェック
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if key in DISTRACTOR_MAP:
        result = DISTRACTOR_MAP[key].copy()
        random.shuffle(result)
        return result[:5] # 👈 ここを 5 に変更

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 2. チャンク（2語以上のまとまり）の場合の賢いダミー生成
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if " " in key:
        words = key.split()
        last_word = words[-1]
        
        # パターン①: "to" で終わる不定詞チャンク
        if last_word == "to":
            pool = ["like to", "need to", "try to", "have to", "plan to", "going to", "used to", "want to", "hope to", "decide to"]
        
        # パターン②: "the", "a", "an" で終わる前置詞＋冠詞チャンク
        elif last_word in ["the", "a", "an"]:
            pool = [f"in {last_word}", f"on {last_word}", f"at {last_word}", f"for {last_word}", f"to {last_word}", f"with {last_word}", f"from {last_word}", f"about {last_word}"]
        
        # パターン③: "of" で終わるチャンク
        elif last_word == "of":
            pool = ["a lot of", "some of", "out of", "part of", "most of", "kind of", "all of", "lots of", "one of"]
            
        # パターン④: その他の汎用チャンク
        else:
            pool = ["very much", "a little", "so that", "such a", "as well", "even if", "over there", "at all", "of course", "by the way"]

        pool = [w for w in pool if w.lower() != key]
        random.shuffle(pool)
        return pool[:5] # 👈 ここを 5 に変更

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 3. 辞書に無い未知の「1語」に対する推測ロジック
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pool = []

    # パターンA：進行形・動名詞 (-ing)
    if key.endswith("ing") and len(key) > 4:
        pool = ["playing", "running", "going", "making", "eating", "watching", "doing", "talking", "thinking", "looking"]
    
    # パターンB：過去形・過去分詞 (-ed)
    elif key.endswith("ed") and len(key) > 3:
        pool = ["played", "wanted", "looked", "used", "worked", "tried", "called", "asked", "needed", "started"]
    
    # パターンC：副詞 (-ly)
    elif key.endswith("ly") and len(key) > 3:
        pool = ["really", "slowly", "quickly", "usually", "hardly", "suddenly", "exactly", "finally", "actually", "probably"]
    
    # パターンD：複数形・三単現のs (-s)
    elif key.endswith("s") and len(key) > 3:
        pool = ["apples", "cars", "books", "days", "things", "friends", "places", "times", "people", "years"]
    
    # パターンE：形容詞・名詞など（汎用フォールバック）
    else:
        pool = [
            "beautiful", "great", "small", "book", "water", "find", "always", "much", "time", "people",
            "way", "good", "new", "first", "last", "long", "own", "other", "old", "right"
        ]

    # 自分がダミーに入らないように除外
    pool = [w for w in pool if w.lower() != key]

    # シャッフルして5つ選ぶ
    random.shuffle(pool)
    return pool[:5] 
