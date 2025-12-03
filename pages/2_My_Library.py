import streamlit as st
import sqlite3
import os

st.set_page_config(page_title="הספרייה שלי", page_icon="📚", layout="wide")

# --- 🛡️ הגנה ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("עליך להתחבר קודם!")
    st.switch_page("Home.py")
    st.stop()

# --- פונקציה לשליפת הספרים (רק של המשתמש המחובר!) ---
def get_my_stories():
    conn = sqlite3.connect('stories_v2.db')
    c = conn.cursor()
    # בודק אם הטבלה קיימת בכלל
    try:
        current_user = st.session_state['username']
        # ה-WHERE username=? זה הסינון הקריטי
        c.execute("SELECT rowid, * FROM stories WHERE username=? ORDER BY rowid DESC", (current_user,))
        data = c.fetchall()
    except:
        data = []
    conn.close()
    return data

# --- כותרת ---
st.title(f"הספרייה של {st.session_state['username']} 📚")
st.divider()

# --- הצגת הספרים ---
stories = get_my_stories()

if not stories:
    st.info("עדיין לא כתבת ספרים. זה הזמן ליצור!")
    if st.button("עבור ליצירת ספר"):
        st.switch_page("pages/1_Create_Book.py")

else:
    cols = st.columns(3)
    for index, story in enumerate(stories):
        with cols[index % 3]:
            with st.container(border=True):
                # מבנה הטבלה עכשיו: (username, hero, genre, content, created_at)
                # story[2] זה הגיבור/כותרת
                st.subheader(f"📘 {story[2]}") 
                st.caption(f"ז'אנר: {story[3]} | {story[5]}")
                st.write("---")
                st.write(story[4][:100] + "...")
                
                if st.button("קרא ספר", key=f"read_{index}"):
                    @st.dialog(f"{story[2]}")
                    def show_story():
                        st.markdown(story[4])
                    show_story()

# --- 👮 אזור גיבוי למנהל ---
st.divider()
with st.expander("ניהול וגיבוי (למנהלים בלבד)"):
    password = st.text_input("סיסמת מנהל:", type="password")
    if password == "BookCraft2026": 
        if os.path.exists("stories_v2.db"):
            with open("stories_v2.db", "rb") as fp:
                st.download_button(
                    label="📥 הורד גיבוי מלא (stories_v2.db)",
                    data=fp,
                    file_name="stories_backup.db",
                    mime="application/octet-stream"
                )
        else:
            st.warning("אין עדיין קובץ נתונים.")
