import random
import sqlite3
import streamlit as st

# ======================
# DB
# ======================
def init_db():
    conn = sqlite3.connect("vocab.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS vocab (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT UNIQUE,
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
    c.execute(
        "INSERT OR REPLACE INTO vocab (word, meaning) VALUES (?, ?)",
        (word.strip(), meaning.strip())
    )
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
# UI STATE
# ======================
if "quiz" not in st.session_state:
    st.session_state.quiz = None
if "answered" not in st.session_state:
    st.session_state.answered = False

# ======================
# UI
# ======================
st.title("📚 AI Vocabulary Trainer (Fixed Version)")

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
            st.rerun()

    st.subheader("📖 Words")
    words = get_words()
    if words:
        for i in words:
            st.write(f"**{i[0]}** → {i[1]} | Level: {i[2]} | Wrongs: {i[3]}")
    else:
        st.info("No words added yet.")

# ======================
# QUIZ
# ======================
elif menu == "Quiz":
    st.subheader("🧠 Quiz Mode")

    words = get_words()

    if len(words) < 4:
        st.warning("Please add at least 4 words to start the quiz.")
    else:
        # Yeni soru oluştur
        if st.session_state.quiz is None:
            q = random.choice(words)
            correct_meaning = q[1]

            # Benzersiz (unique) seçenek kümesi oluşturma
            all_meanings = list(set([w[1] for w in words]))
            wrong_options = [m for m in all_meanings if m != correct_meaning]

            # Eğer yeterli farklı anlam varsa 3 yanlış seç, yoksa mevcut kadarını al
            sampled_wrongs = random.sample(wrong_options, min(3, len(wrong_options)))
            
            options = [correct_meaning] + sampled_wrongs
            random.shuffle(options)

            st.session_state.quiz = {
                "word": q[0],
                "correct": correct_meaning,
                "options": options
            }
            st.session_state.answered = False

        quiz = st.session_state.quiz

        st.write("What is the meaning of:")
        st.subheader(f"👉 **{quiz['word']}**")

        # Otomatik işaretlemeyi ve kafa karışıklığını önlemek için None index seçeneği
        user_choice = st.radio(
            "Choose option:",
            quiz["options"],
            index=None,
            disabled=st.session_state.answered
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Check Answer", disabled=st.session_state.answered):
                if user_choice is None:
                    st.warning("Please select an answer first!")
                else:
                    st.session_state.answered = True
                    if user_choice == quiz["correct"]:
                        st.success("Correct 🎉")
                        update(quiz["word"], True)
                    else:
                        st.error(f"Wrong 😢 Correct answer: {quiz['correct']}")
                        update(quiz["word"], False)

        with col2:
            if st.button("Next Question"):
                st.session_state.quiz = None
                st.session_state.answered = False
                st.rerun()
