import streamlit as st
import sqlite3
import os

st.set_page_config(page_title="הספרייה שלי", page_icon="📚", layout="wide")

# --- הגנה ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("עליך להתחבר קודם!")
    st.switch_page("Home.py")
    st.stop()

# --- חיבור למסד החדש v3 ---
DB_NAME = 'stories_v3.db'

def get_my_stories():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        user = st.session_state['username']
        # שולף את הספרים + המצב שלהם (האם פורסמו?)
        c.execute("SELECT rowid, * FROM stories WHERE username=? ORDER BY rowid DESC", (user,))
        data = c.fetchall()
    except:
        data = []
    conn.close()
    return data

def toggle_publish_status(story_id, current_status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # הופך מ-0 ל-1 או להפך
    new_status = not current_status
    c.execute("UPDATE stories SET is_public=? WHERE rowid=?", (new_status, story_id))
    conn.commit()
    conn.close()
    st.rerun() # מרענן את הדף כדי לראות את השינוי

# --- כותרת ---
st.title(f"הספרייה של {st.session_state['username']} 📚")
st.caption("כאן אתה מנהל את הספרים שלך. בחר מה לשתף עם העולם!")
st.divider()

stories = get_my_stories()

if not stories:
    st.info("עדיין לא כתבת ספרים.")
else:
    cols = st.columns(3)
    for index, story in enumerate(stories):
        # המבנה של story עכשיו:
        # [0]rowid, [1]user, [2]hero, [3]genre, [4]content, [5]date, [6]is_public, [7]likes
        
        with cols[index % 3]:
            # מסגרת שמשתנה אם הספר מפורסם
            is_public = story[6]
            border_color = "red" if is_public else "grey"
            
            with st.container(border=True):
                st.subheader(f"📘 {story[2]}")
                st.caption(f"ז'אנר: {story[3]}")
                
                # סטטוס פרסום
                if is_public:
                    st.success(f"🌐 מפורסם בקהילה ({story[7]} לייקים)")
                    btn_label = "הסתר מהקהילה 🔒"
                else:
                    st.warning("🔒 פרטי (רק אתה רואה)")
                    btn_label = "פרסם לכולם 📢"
                
                # כפתור שינוי סטטוס
                if st.button(btn_label, key=f"pub_{index}"):
                    toggle_publish_status(story[0], is_public)

                st.write("---")
                # כפתור קריאה
                if st.button("קרא ספר", key=f"read_{index}"):
                    @st.dialog(f"{story[2]}")
                    def show_story():
                        st.markdown(story[4])
                    show_story()

# --- המשך אזור המנהלים ---
    st.divider()
    st.write("🔧 **שחזור מערכת (Restore):**")
    st.caption("העלה לכאן קובץ גיבוי כדי לשחזר את כל המשתמשים והסיפורים שנמחקו")
    
    uploaded_file = st.file_uploader("בחר קובץ stories_backup.db מהמחשב", type="db")
    
    if uploaded_file is not None:
        if st.button("⚠️ דרוס את הנתונים הקיימים ושחזר מהגיבוי"):
            # שומרים את הקובץ שהועלה בתור מסד הנתונים הפעיל
            with open("stories_v3.db", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("השחזור הצליח! כל המשתמשים והסיפורים חזרו.")
            st.balloons()
            st.rerun() # מרענן את הדף כדי לראות את הנתונים החדשים
