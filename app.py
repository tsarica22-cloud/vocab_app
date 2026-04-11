import streamlit as st
import sqlite3
import random

# ======================
# DB
# ======================
def init_db():
    conn = sqlite3.connect("vocab.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS vocab (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT,
        meaning TEXT,
        level INTEGER DEFAULT 0,
        wrong_count INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ======================
# FUNCTIONS
# ======================
def add_word(word, meaning):
    conn = sqlite3.connect("vocab.db")
    c = conn.cursor()
    c.execute("INSERT INTO vocab (word, meaning) VALUES (?, ?)", (word, meaning))
    conn.commit()
    conn.close()

def get_words():
    conn = sqlite3.connect("vocab.db")
    c = conn.cursor()
    c.execute("SELECT word, meaning, level, wrong_count FROM vocab")
    data = c.fetchall()
    conn.close()
    return data

def update(word, correct):
    conn = sqlite3.connect("vocab.db")
    c = conn.cursor()

    if correct:
        c.execute("UPDATE vocab SET level = level + 1 WHERE word=?", (word,))
    else:
        c.execute("UPDATE vocab SET wrong_count = wrong_count + 1 WHERE word=?", (word,))

    conn.commit()
    conn.close()

# ======================
# UI STATE (IMPORTANT FIX)
# ======================
if "quiz" not in st.session_state:
    st.session_state.quiz = None

# ======================
# UI
# ======================
st.title("📚 AI Vocabulary Trainer (Stable Version)")

menu = st.sidebar.selectbox("Menu", ["Add", "Quiz"])

# ======================
# ADD
# ======================
if menu == "Add":
    st.subheader("➕ Add Word")

    w = st.text_input("Word")
    m = st.text_input("Meaning")

    if st.button("Add Word"):
        if w and m:
            add_word(w, m)
            st.success("Added ✔")

    st.subheader("📖 Words")
    for i in get_words():
        st.write(f"{i[0]} → {i[1]} | L:{i[2]} | W:{i[3]}")

# ======================
# QUIZ (FIXED ENGINE)
# ======================
elif menu == "Quiz":
    st.subheader("🧠 Quiz Mode")

    words = get_words()

    if len(words) < 4:
        st.warning("Add at least 4 words")
    else:

        # NEW QUIZ ONLY WHEN NULL
        if st.session_state.quiz is None:
            q = random.choice(words)
            correct = q[1]

            options = [correct]
            while len(options) < 4:
                options.append(random.choice(words)[1])

            random.shuffle(options)

            st.session_state.quiz = {
                "word": q[0],
                "correct": correct,
                "options": options
            }

        quiz = st.session_state.quiz

        st.write("What is the meaning of:")
        st.subheader(quiz["word"])

        answer = st.radio("Choose", quiz["options"])

        if st.button("Check Answer"):
            if answer == quiz["correct"]:
                st.success("Correct 🎉")
                update(quiz["word"], True)
            else:
                st.error(f"Wrong 😢 Correct: {quiz['correct']}")
                update(quiz["word"], False)

        if st.button("Next Question"):
            st.session_state.quiz = None