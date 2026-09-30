# -*- coding: utf-8 -*-
"""
WordFlow English - レスポンシブCSSモジュール
====================================================
app.py の st.set_page_config() の直後に

    from responsive import inject_responsive_css, container_with_key
    inject_responsive_css()

と呼び出すだけでOK。レイアウト用のCSSは全部このファイルに集約してあるので、
Streamlit のバージョンが上がってDOMが変わったときも、直すのはここだけになります。

--- 何が「はみ出し」の原因だったか ---------------------------------
(1) box-sizing が content-box のままだった
      max-width:450px + padding 左右 24px + 24px = 実幅 498px
      → 375px の画面では、カードの右端が 123px ぶん画面外に出る。
        選択ボックスもボタンも、右側が全部切れていたのはこれが理由。
(2) 列の縦積み（640px未満）を flex-direction:row で打ち消していた
      Streamlit は狭い画面で列を縦に積む。それを !important で
      横並びに固定したため、幅を持った部品（音声入力のカスタム
      コンポーネントなど）が縮められず、右へ押し出されていた。
(3) ハッシュ付きクラス(.st-emotion-cache-xxxx)でツールバーを隠していた
      このクラス名はビルドごとに変わるので、いまは効いていない。

--- 直し方の方針 -------------------------------------------------
・箱の計算を border-box に統一し、カードは width:100% + max-width:450px に。
・列の縦積み/横並びは CSS 側で明示的に分岐（PC=横並び / スマホ=縦積み）。
・「スマホでも横並びにしたい行」だけ、st.container(key=...) で
  目印を付けて .st-key-<key> を狙い撃ちする（候補ボタンと Undo/Hint/Finish）。
・ツールバーはハッシュではなく data-testid と config.toml で隠す。

対応: Streamlit 1.39 以降（st.container(key=...) を使うため）
      1.39 未満でも container_with_key() が自動でフォールバックします。
"""

import streamlit as st

CSS = """
<style>
/* ============================================================
   0. すべての箱を border-box で計算する
   ------------------------------------------------------------
   これが今回の「はみ出し」の一番の原因。
   content-box だと max-width + padding が加算されて
   450px + 48px = 498px となり、375px の画面では必ず溢れます。
   ============================================================ */
*, *::before, *::after { box-sizing: border-box; }

html {
    -webkit-text-size-adjust: 100%;   /* iOSの勝手な文字拡大を防ぐ */
    text-size-adjust: 100%;
}
html, body, .stApp {
    max-width: 100%;
    overflow-x: hidden;               /* 最後の安全網（できれば発動しない） */
}
.stApp { background-color: #e2e8f0 !important; }

/* ============================================================
   1. メインのカード
   PC     : 中央に最大450pxの「スマホ枠」
   スマホ : 画面幅いっぱい（下のメディアクエリで枠を外す）
   ============================================================ */
[data-testid="stMain"] { padding: 0 !important; }

.stMainBlockContainer,
[data-testid="stMainBlockContainer"],
.block-container {
    width: 100% !important;
    max-width: 450px !important;
    margin: 2rem auto !important;
    /* clamp(最小, 画面幅に応じた値, 最大) で余白が自動調整される */
    padding: clamp(0.9rem, 3.5vw, 2rem) clamp(0.9rem, 4vw, 1.5rem) 2rem !important;
    padding-left:  max(clamp(0.9rem, 4vw, 1.5rem), env(safe-area-inset-left))  !important;
    padding-right: max(clamp(0.9rem, 4vw, 1.5rem), env(safe-area-inset-right)) !important;
    padding-bottom: max(2rem, env(safe-area-inset-bottom)) !important;
    background-color: #ffffff !important;
    border-radius: 20px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
}

/* ============================================================
   2. 右上のツールバー（Share / ★ / 編集 / GitHub / ⋮）を消す
   ------------------------------------------------------------
   .st-emotion-cache-xxxxxx はビルドごとに変わるハッシュなので使わない。
   data-testid は安定して使えるフック。
   （.streamlit/config.toml の toolbarMode="minimal" と併用すると確実）
   ============================================================ */
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stAppDeployButton"],
[data-testid="stHeader"],
#MainMenu, footer {
    display: none !important;
}

/* ============================================================
   3. 行（st.columns）の並べ方を自分で決め直す
   ------------------------------------------------------------
   Streamlit は既定で「画面幅640px未満」だと列を縦積みにします。
     ・PC（641px以上）  : 横並び
     ・スマホ（640px以下）: 縦積み（＝固有幅を持つ部品でも絶対に溢れない）
   ============================================================ */
[data-testid="stHorizontalBlock"] {
    gap: 0.5rem !important;
    align-items: center !important;
}
/* 列は「中身より小さく縮める」ようにする（無いと押し出されて溢れる） */
[data-testid="stColumn"],
[data-testid="column"],
[data-testid="stHorizontalBlock"] > div {
    min-width: 0 !important;
    max-width: 100% !important;
}

@media (min-width: 641px) {
    [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }
}

@media (max-width: 640px) {
    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        flex-wrap: nowrap !important;
        align-items: stretch !important;   /* center のままだと中身の幅に縮む */
    }
    [data-testid="stColumn"],
    [data-testid="column"],
    [data-testid="stHorizontalBlock"] > div {
        width: 100% !important;
        flex: 0 0 auto !important;
    }
}

/* ============================================================
   4. 例外：パズルの候補ボタン行と操作ボタン行は、スマホでも横並びを維持
   ------------------------------------------------------------
   st.container(key="...") を付けると .st-key-<key> が付きます（1.39以降）。
   その中だけは縦積みにせず、列を均等割りにして文字を折り返して縮めます。
   ============================================================ */
.st-key-candidates [data-testid="stHorizontalBlock"],
.st-key-actions    [data-testid="stHorizontalBlock"] {
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: stretch !important;
}
.st-key-candidates [data-testid="stHorizontalBlock"] > div,
.st-key-actions    [data-testid="stHorizontalBlock"] > div,
.st-key-candidates [data-testid="stColumn"],
.st-key-actions    [data-testid="stColumn"],
.st-key-candidates [data-testid="column"],
.st-key-actions    [data-testid="column"] {
    flex: 1 1 0 !important;
    width: auto !important;
    min-width: 0 !important;
}

/* ============================================================
   5. ボタン・部品が横に伸びて溢れないようにする
   ------------------------------------------------------------
   「Create Puzzle 🧩」のような長いラベルは、折り返してOKにする。
   ============================================================ */
[data-testid="stButton"] button,
[data-testid="stFormSubmitButton"] button,
[data-testid="stPopover"] button {
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    word-break: break-word;
    min-width: 0 !important;
    max-width: 100% !important;
    font-size: 15px !important;
    line-height: 1.25 !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
}

/* 入力欄・カスタムコンポーネント・画像なども横幅を超えさせない */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"],
[data-testid="stCustomComponentV1"],
[data-testid="stCustomComponentV1"] > div,
[data-testid="stIFrame"],
iframe,
img, video, canvas, svg, table, pre {
    max-width: 100% !important;
}
[data-testid="stCustomComponentV1"] > div,
[data-testid="stCustomComponentV1"] iframe {
    width: 100% !important;
}

/* 長い文章（組み立て中の文・完成した文）が横に伸びないように */
.wf-sentence, .wf-final-sentence {
    overflow-wrap: anywhere;
    word-break: break-word;
    line-height: 1.45;
}

/* ポップオーバー（Add Word Manually）が画面外に出ないように */
div[data-baseweb="popover"],
[data-testid="stPopoverBody"] {
    max-width: min(92vw, 420px) !important;
}

/* ============================================================
   6. 文字サイズ・余白の微調整
   ============================================================ */
h3 { font-size: clamp(16px, 4.4vw, 18px) !important; margin-bottom: 0 !important; }
[data-testid="stSelectbox"] label,
[data-testid="stSelectbox"] div { font-size: 13px !important; }

.lang-arrow {
    text-align: center;
    font-size: 22px;
    line-height: 1;
    padding-top: 26px;      /* ラベルの分だけ下げて、セレクトボックスと高さを揃える */
}

/* ============================================================
   7. スマホ幅のときの見た目
   ------------------------------------------------------------
   カード枠（角丸・影・左右の余白）を外して「アプリ画面」にする。
   ============================================================ */
@media (max-width: 640px) {
    .stApp { background-color: #ffffff !important; }

    .stMainBlockContainer,
    [data-testid="stMainBlockContainer"],
    .block-container {
        margin: 0 !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        min-height: 100dvh !important;      /* dvh は URLバーを除いた実高さ */
    }
    /* 縦積みになるので、矢印は下向きに回す */
    .lang-arrow { transform: rotate(90deg); padding-top: 0; margin: 0.15rem 0; }
}

/* 横向きスマホ・タブレットの微調整 */
@media (max-width: 900px) and (orientation: landscape) {
    .stMainBlockContainer,
    [data-testid="stMainBlockContainer"],
    .block-container { max-width: 560px !important; }
}
</style>
"""


def inject_responsive_css() -> None:
    """レスポンシブ用CSSを注入する。app.py の set_page_config の直後に1回だけ呼ぶ。"""
    st.markdown(CSS, unsafe_allow_html=True)


def container_with_key(key: str, **kwargs):
    """
    st.container(key=...) が使えるバージョンなら key 付きで、
    古いバージョンなら key 無しでコンテナを返す（＝落ちない）。

    key が付くと CSS 側の .st-key-<key> が効くので、
    「スマホでも横並びにしたい行」だけを狙って制御できます。
    古いバージョンでは key が無視されるため、その行はスマホで縦積みになりますが、
    画面からはみ出すことはありません（縮退動作）。
    """
    try:
        return st.container(key=key, **kwargs)
    except TypeError:
        return st.container(**kwargs)
