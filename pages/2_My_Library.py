import streamlit as st
import sqlite3

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
