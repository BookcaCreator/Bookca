# --- הגנה: אם לא מחובר, זרוק אותו לדף הבית ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("עליך להתחבר קודם!")
    st.switch_page("Home.py") # מעיף אותו חזרה ללוגין
    st.stop()
import streamlit as st
import sqlite3
import os

st.set_page_config(page_title="הספרייה שלי", page_icon="📚", layout="wide")

# --- וידוא שהמסד קיים ---
def init_db():
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stories
                 (hero TEXT, genre TEXT, content TEXT, created_at TEXT)''')
    conn.commit()
    conn.close()

# --- פונקציה לשליפת הספרים ---
def get_all_stories():
    init_db() # קוראים לזה לפני הכל
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    try:
        c.execute("SELECT rowid, * FROM stories ORDER BY rowid DESC")
        data = c.fetchall()
    except:
        data = []
    conn.close()
    return data

# --- כותרת ---
st.title("📚 הספרייה שלי")
st.divider()

# --- הצגת הספרים ---
stories = get_all_stories()

if not stories:
    st.info("הספרייה ריקה עדיין... רוץ ליצור את הספר הראשון שלך!")
    if st.button("עבור ליצירת ספר"):
        st.switch_page("pages/1_Create_Book.py")

else:
    cols = st.columns(3)
    for index, story in enumerate(stories):
        with cols[index % 3]:
            with st.container(border=True):
                # story = (id, hero, genre, content, date)
                st.subheader(f"📘 {story[1]}")
                st.caption(f"ז'אנר: {story[2]} | {story[4]}")
                st.write("---")
                st.write(story[3][:100] + "...")
                
                if st.button("קרא ספר מלא", key=f"read_{index}"):
                    @st.dialog(f"הסיפור על {story[1]}")
                    def show_story():
                        st.markdown(story[3])
                    show_story()
st.divider()
st.subheader("👮 אזור מנהלים (גיבוי)")

# סיסמה פשוטה כדי שסתם אנשים לא יורידו את המידע
password = st.text_input("הכנס סיסמת מנהל להורדת הגיבוי:", type="password")

if password == "9806": # תשנה לסיסמה שרק אתה יודע
    
    # בודק אם הקובץ בכלל קיים
    if os.path.exists("stories.db"):
        with open("stories.db", "rb") as fp:
            st.download_button(
                label="📥 הורד את קובץ הנתונים (stories.db) למחשב שלי",
                data=fp,
                file_name="stories_backup.db",
                mime="application/octet-stream"
            )
        st.success("יש קובץ נתונים מוכן להורדה! הורד אותו כדי לשמור את הסיפורים של כולם.")
    else:
        st.warning("עדיין לא נוצרו סיפורים, אז אין קובץ להורדה.")
