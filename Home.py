import streamlit as st
import sqlite3

# --- הגדרות עמוד ---
st.set_page_config(
    page_title="BookCraft AI",
    page_icon="📚",
    layout="wide"  # זה נותן לנו מסך רחב כמו בתמונות שלך!
)

# --- פונקציה לשליפת נתונים לסטטיסטיקה ---
def get_stats():
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    # סופר כמה ספרים יש סה"כ
    c.execute("SELECT COUNT(*) FROM stories")
    total_books = c.fetchone()[0]
    conn.close()
    return total_books

# --- כותרת ראשית ---
st.title("📚 מרכז השליטה שלך")
st.caption("ברוך הבא ל-BookCraft AI")

# --- סטטיסטיקות (כמו בתמונה!) ---
# אנחנו מחלקים את המסך ל-4 עמודות
col1, col2, col3, col4 = st.columns(4)

total_books = get_stats()

with col1:
    st.metric(label="ספרים בספרייה", value=total_books)
with col2:
    st.metric(label="מילים שנכתבו", value=total_books * 500) # הערכה גסה כרגע
with col3:
    st.metric(label="בתהליך כתיבה", value="1")
with col4:
    st.metric(label="ספרים שהושלמו", value=total_books)

st.divider()

# --- אזור מהיר לפעולה ---
st.subheader("מה תרצה לעשות היום?")

# כפתורים גדולים ויפים
c1, c2 = st.columns(2)
with c1:
    st.info("✍️ **כתוב ספר חדש**")
    st.write("התחל פרויקט חדש בעזרת Gemini 2.0")
    if st.button("עבור ליצירת ספר"):
        st.switch_page("pages/1_Create_Book.py") # מעביר אותך לדף אחר!

with c2:
    st.info("📖 **הספרייה שלי**")
    st.write("צפה בכל הספרים שיצרת עד כה")
    if st.button("עבור לספרייה"):
        st.switch_page("pages/2_My_Library.py")