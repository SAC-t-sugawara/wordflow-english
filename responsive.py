# -*- coding: utf-8 -*-
"""
WordFlow English - レスポンシブCSSモジュール（縦積みを止める決定版）
=================================================================
app.py の st.set_page_config() の直後に

    from responsive import inject_responsive_css, container_with_key
    inject_responsive_css()

と呼び出すだけ。レイアウト用のCSSは全部このファイルに集約。

--- はみ出しの原因（前々回に修正）--------------------------------
(1) box-sizing が content-box だった
      max-width:450px + padding 48px = 実幅 498px → 375px で 123px はみ出し
(2) ハッシュ付きクラス(.st-emotion-cache-xxxx)でツールバーを隠していた
      → クラス名はビルドごとに変わる。data-testid + config.toml に変更。

--- 縦長（候補ボタンが1列）の原因と対策（今回）-------------------
Streamlit は画面幅 640px 未満で st.columns を「1行1列」に折り返す
（＝ボタンが縦に1列で並ぶ）。止め方は2段構え:

  【本命】st.columns(..., wrap=False)
      これは Streamlit 公式のAPI。wrap=False で「積み重ね(substacking)を
      無効化し、必ず1行に収める」とドキュメントに明記されている。
      → puzzle_ui.py 側で _columns_nowrap() ヘルパー経由で使用。
        古いバージョンには引数が無いので TypeError を拾って退避する。

  【保険】CSS で min-width を戻す
      本体は 640px 未満で列に min-width: calc(100% - 2rem) を当てて
      折り返させている（親は flex-wrap: wrap）。つまり折り返しの原因は
      flex-direction ではなく min-width。よって min-width:0 に戻せば
      狭くても横並びのまま収まる。CSSが効かない環境でも wrap=False が効き、
      wrap=False が無い環境でもこのCSSが効く（二重の安全網）。

  ※前版にあった「:has(iframe) → 縦積み」のような例外ルールは撤去した。
    ブラウザやビルド差で :has() が無効だと通常行まで壊れるリスクがあるため、
    例外指定は一切使わない方針にした。

--- 方針 -------------------------------------------------------
・箱の計算を border-box に統一。カードは width:100% + max-width:450px。
・行は「原則1行。物理的に入らない時だけ折り返す」＝ flex-wrap: wrap。
・縦積みにしたい行（言語セレクトなど）は Streamlit 既定のまま置いておく
  （横幅いっぱいの部品は flex-basis 100% で自然に全幅になる）。
"""

import streamlit as st

CSS = """
<style>
/* ============================================================
   0. すべての箱を border-box で計算する
   ============================================================ */
*, *::before, *::after { box-sizing: border-box; }

html {
    -webkit-text-size-adjust: 100%;
    text-size-adjust: 100%;
}
html, body, .stApp { max-width: 100%; overflow-x: hidden; }
.stApp { background-color: #e2e8f0 !important; }

/* ============================================================
   1. メインのカード（PCは中央450px / スマホは全幅）
   ============================================================ */
[data-testid="stMain"] { padding: 0 !important; }

.stMainBlockContainer,
[data-testid="stMainBlockContainer"],
.block-container {
    width: 100% !important;
    max-width: 450px !important;
    margin: 2rem auto !important;
    padding: clamp(0.9rem, 3.5vw, 2rem) clamp(0.9rem, 4vw, 1.5rem) 2rem !important;
    padding-left:  max(clamp(0.9rem, 4vw, 1.5rem), env(safe-area-inset-left))  !important;
    padding-right: max(clamp(0.9rem, 4vw, 1.5rem), env(safe-area-inset-right)) !important;
    padding-bottom: max(2rem, env(safe-area-inset-bottom)) !important;
    background-color: #ffffff !important;
    border-radius: 20px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
}

/* ============================================================
   2. 右上のツールバーを消す（ハッシュクラスは使わない）
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
   3. 行（st.columns）は「原則1行」にする  ★ここが縦長対策の本丸
   ------------------------------------------------------------
   ・st.columns(..., wrap=False) が最優先の手段（puzzle_ui.py 側）。
   ・その保険として、640px未満でも min-width を 0 に戻して
     折り返しを発生させない（flex-wrap: wrap は残すので、
     物理的に入らない極小画面では溢れずに折り返す）。
   ・flex-direction を column に固定する行は一切作らない。
   ============================================================ */
[data-testid="stHorizontalBlock"] {
    flex-wrap: wrap !important;
    flex-direction: row !important;
    align-items: stretch !important;
    gap: 0.5rem !important;
}

[data-testid="stColumn"],
[data-testid="column"],
[data-testid="stHorizontalBlock"] > div {
    max-width: 100% !important;
}

@media (max-width: 640px) {
    /* 本体の「min-width: calc(100% - 2rem)」を打ち消す＝縦積み解除 */
    [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: wrap !important;
    }
    [data-testid="stColumn"],
    [data-testid="column"],
    [data-testid="stHorizontalBlock"] > div,
    [data-testid="stHorizontalBlock"] > div > div {
        min-width: 0 !important;
        width: auto !important;
    }
}

/* ============================================================
   4. 候補ボタン / 操作ボタンの行は幅を均等割りに（key付きコンテナ用）
   ------------------------------------------------------------
   st.container(key="...") は .st-key-<key> を付ける（1.39以降）。
   無いバージョンでは、このブロックは黙って無視されるだけ。
   ============================================================ */
.st-key-candidates [data-testid="stHorizontalBlock"] > div,
.st-key-actions    [data-testid="stHorizontalBlock"] > div,
.st-key-candidates [data-testid="stColumn"],
.st-key-actions    [data-testid="stColumn"],
.st-key-candidates [data-testid="column"],
.st-key-actions    [data-testid="column"] {
    flex: 1 1 0 !important;
    min-width: 0 !important;
}

/* ============================================================
   5. ボタン・部品が横に伸びて溢れないようにする
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

.wf-sentence, .wf-final-sentence {
    overflow-wrap: anywhere;
    word-break: break-word;
    line-height: 1.45;
}

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
    padding-top: 26px;
}

/* ============================================================
   7. スマホ幅のときの見た目（カード枠を外してアプリ画面にする）
   ============================================================ */
@media (max-width: 640px) {
    .stApp { background-color: #ffffff !important; }

    .stMainBlockContainer,
    [data-testid="stMainBlockContainer"],
    .block-container {
        margin: 0 !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        min-height: 100dvh !important;
    }
    .lang-arrow { transform: rotate(90deg); padding-top: 0; margin: 0.15rem 0; }
}

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
    """
    try:
        return st.container(key=key, **kwargs)
    except TypeError:
        return st.container(**kwargs)


def columns_nowrap(n: int, **kwargs):
    """
    スマホでも縦積みにしない行を作るための薄いラッパー。

    st.columns(n, wrap=False) は Streamlit 公式のAPIで、
    「横並びを維持し、積み重ね(640px未満の1行1列化)を無効化する」。
    古いバージョンには wrap 引数が無いので TypeError を拾って退避する。
    """
    try:
        return st.columns(n, wrap=False, **kwargs)
    except TypeError:
        return st.columns(n, **kwargs)
