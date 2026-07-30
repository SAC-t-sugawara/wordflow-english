# 🧩 WordFlow English

WordFlow English is a puzzle-style English composition web application that delivers a new learning experience powered by the **Gemini API**.  
Users set a goal in Japanese (what they want to say), then build the sentence by selecting suggested English words—naturally developing an intuitive sense of English word order.

![WordFlow English Screenshot](https://via.placeholder.com/800x400.png?text=WordFlow+English+App)

## ✨ Key Features
* **Three-Layer UI:** A clean visual separation into "Goal," "Puzzle Building," and "Current Japanese Translation" reduces cognitive load for learners.
* **Real-Time Feedback:** Every time a word is selected (or manually entered), the Gemini API instantly translates the sentence-in-progress back into Japanese.
* **Undo & Manual Input:** A "Go Back One Step" feature encourages trial and error. Words not in the suggestion list can be freely added via a text input form.
* **Ultra-Fast & Lightweight:** No need to run a heavy AI model locally—achieves blazing-fast responses regardless of your PC specs.

---

## 🧠 Architectural Design Highlights

This app goes beyond simply calling an API—it incorporates design decisions aimed at balancing user experience (UX) with system robustness.

### 1. Task Separation to Suppress Hallucination and Improve Speed
Asking an LLM to simultaneously handle "correct answer inference," "distractor word generation," and "in-progress translation" in a single prompt tends to slow down processing and increase the risk of malformed output.  
**👉 [Solution]**  
We fully separated these responsibilities:
1. **Correct Sentence Generation**: The API is called only once at the start to generate the "goal" (the complete English sentence), which is then held as state.
2. **Non-LLM Distractor Generation**: Using the correct word as a key, four distractor words are instantly retrieved from a static lookup table (`distractor_manager.py`). This eliminates unnecessary API calls, dramatically improving both reliability and speed.
3. **Real-Time Translation**: Each time a word is added, a dedicated prompt is sent to the API, returning a highly accurate translation instantly.

### 2. Secure Configuration via Environment Variables and `secrets.toml`
Hardcoding API keys or model names (e.g., `gemini-2.0-flash`) directly into the codebase introduces security risks and reduces maintainability.  
**👉 [Solution]**  
We adopted a fallback design that securely loads configuration from Streamlit's built-in `st.secrets` and system environment variables (`os.environ`). This makes the app maintenance-free—when a model is updated in the future, a single line in the config file is all that needs to change.

### 3. Logging System Designed for Analysis and Operations
To avoid turning the AI's inference process into a black box, we implemented a dedicated logger.  
**👉 [Solution]**  
Communication errors and other issues are recorded in `error.log`, with a fail-safe mechanism that returns user-friendly error messages instead of crashing the app. Additionally, user inputs and AI outputs are logged as structured data in `analytics.jsonl`, providing a foundation for future prompt improvements.

---

## 📁 Directory Structure

The project follows a modern, component-oriented architecture with a clean separation between UI and logic.

```text
wordflow-english/
├── pyproject.toml         # Package and dependency management (uv)
├── README.md              # This document
├── .streamlit/
│   └── secrets.toml       # 🔐 Configuration file for API keys, etc. (excluded from Git)
├── logs/                  
│   ├── error.log          # [Auto-generated] Error log
│   └── analytics.jsonl    # [Auto-generated] Structured log of AI inference and translation data
├── src/
│   ├── state_manager.py   # Session state management
│   ├── llm_engine.py      # Gemini API client initialization and prompt handling
│   ├── distractor_manager.py # Lookup table for distractor words
│   └── components/        # UI parts
│       ├── goal_ui.py     # Goal input/display area
│       ├── puzzle_ui.py   # Puzzle, ghost text, and manual input area
│       └── trans_ui.py    # Real-time translation display area
└── app.py                 # Main file that manages screen routing
```

---

## 🛠️ Setup and Usage

This project uses `uv`, a fast Python package manager.

### 1. Install Dependencies
Run the following command in the project's root directory:
```bash
uv sync
```

### 2. Configure Your API Key
Create a `.streamlit` folder in the project's root directory, and inside it, create a `secrets.toml` file. Add the following content, replacing the placeholder with your own Gemini API key.

**`.streamlit/secrets.toml`**
```toml
GEMINI_API_KEY = "your-gemini-api-key-here"
GEMINI_MODEL_NAME = "gemini-2.0-flash"
```

### 3. Run the Application
Run the following command to start a local server and open the app in your browser:
```bash
uv run streamlit run app.py
```

---

## 📝 How to Use
1. Enter what you want to say (in Japanese) into the text box at the top of the screen, then click "Create Puzzle."
2. Click on the correct word from the 5 suggested English word buttons to build your sentence step by step.
3. If a needed word isn't among the suggestions, you can manually type and add it via the text input field.
4. If you're stuck, click "💡 Show Hint" or refer to the "Current Japanese Translation" shown at the bottom of the screen.
5. Use "⏪ Go Back" to undo as many times as needed. Once your sentence is complete, click the "🏁 Finish" button.

- READMEに「ライセンス」や「Contributing」セクションを追加したい場合はどう書けばいい？
- このアプリの技術スタック（Streamlit, Gemini API）について、README内で英語圏の読者向けにより詳しく紹介したい場合の書き方は？
- 実際にGitHubのリポジトリ設定（トピックタグ、Description欄）を最適化するにはどうすればいい？
