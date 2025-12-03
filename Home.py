import streamlit as st
import sqlite3

# --- הגדרות עמוד ---
st.set_page_config(
    page_title="BookCraft AI",
    page_icon="📚",
    layout="wide"
)

# --- פונקציה ליצירת המסד (התיקון החשוב!) ---
def init_db():
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    # אנחנו מוודאים שהטבלה קיימת לפני שמנסים לקרוא ממנה
    c.execute('''CREATE TABLE IF NOT EXISTS stories
                 (hero TEXT, genre TEXT, content TEXT, created_at TEXT)''')
    conn.commit()
    conn.close()

# --- פונקציה לשליפת נתונים ---
def get_stats():
    init_db() # קוראים לזה קודם כל!
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    try:
        c.execute("SELECT COUNT(*) FROM stories")
        result = c.fetchone()
        total_books = result[0] if result else 0
    except:
        total_books = 0
    conn.close()
    return total_books

# --- כותרת ראשית ---
st.title("📚 מרכז השליטה שלך")
st.caption("ברוך הבא ל-BookCraft AI")

# --- סטטיסטיקות ---
col1, col2, col3, col4 = st.columns(4)

total_books = get_stats()

with col1:
    st.metric(label="ספרים בספרייה", value=total_books)
with col2:
    st.metric(label="מילים שנכתבו", value=total_books * 500)
with col3:
    st.metric(label="בתהליך כתיבה", value="0")
with col4:
    st.metric(label="ספרים שהושלמו", value=total_books)

st.divider()

# --- כפתורים ---
st.subheader("מה תרצה לעשות היום?")

c1, c2 = st.columns(2)
with c1:
    st.info("✍️ **כתוב ספר חדש**")
    if st.button("עבור ליצירת ספר"):
        st.switch_page("pages/1_Create_Book.py")

with c2:
    st.info("📖 **הספרייה שלי**")
    if st.button("עבור לספרייה"):
        st.switch_page("pages/2_My_Library.py")
