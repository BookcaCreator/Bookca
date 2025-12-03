import streamlit as st
import sqlite3

st.set_page_config(page_title="הספרייה שלי", page_icon="📚", layout="wide")

# --- 🛡️ הגנה: בדיקה אם המשתמש מחובר ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("עליך להתחבר קודם!")
    st.switch_page("Home.py")
    st.stop()

# --- הגדרת מסד הנתונים ---
DB_NAME = 'stories_v3.db'

# --- פונקציה לשינוי סטטוס פרסום (ציבורי/פרטי) ---
def toggle_publish_status(story_id, current_status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # הופך את הסטטוס (אם היה 0 נהיה 1, אם היה 1 נהיה 0)
    new_status = not current_status
    c.execute("UPDATE stories SET is_public=? WHERE rowid=?", (new_status, story_id))
    conn.commit()
    conn.close()
    st.rerun() # מרענן את הדף מיד כדי שנראה את השינוי

# --- פונקציה לשליפת הספרים של המשתמש בלבד ---
def get_my_stories():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        user = st.session_state['username']
        # שולף את הספרים + ה-ID שלהם (rowid)
        # הסינון WHERE username=? מבטיח שכל אחד רואה רק את שלו
        c.execute("SELECT rowid, * FROM stories WHERE username=? ORDER BY rowid DESC", (user,))
        data = c.fetchall()
    except:
        data = []
    conn.close()
    return data

# ==========================================
# 📚 ממשק הספרייה
# ==========================================

st.title(f"הספרייה של {st.session_state['username']}")
st.caption("כאן נמצאים כל הספרים שכתבת. אתה מחליט מה לשתף עם הקהילה!")
st.divider()

stories = get_my_stories()

if not stories:
    st.info("המדפים ריקים... זה הזמן ליצור את יצירת המופת הראשונה שלך!")
    if st.button("✍️ עבור ליצירת ספר"):
        st.switch_page("pages/1_Create_Book.py")

else:
    # תצוגת גריד (3 ספרים בשורה)
    cols = st.columns(3)
    
    for index, story in enumerate(stories):
        # מיפוי העמודות בטבלה:
        # [0]rowid, [1]username, [2]hero, [3]genre, [4]content, [5]date, [6]is_public, [7]likes
        
        story_id = story[0]
        hero_title = story[2]
        genre = story[3]
        content = story[4]
        date = story[5]
        is_public = story[6]
        likes = story[7]

        # חלוקה לעמודות בצורה מחזורית
        with cols[index % 3]:
            
            # מסגרת לכל ספר
            with st.container(border=True):
                st.subheader(f"📘 {hero_title}")
                st.caption(f"{genre} | {date}")
                
                # תצוגת סטטוס (האם מפורסם?)
                if is_public:
                    st.success(f"🌐 מפורסם בקהילה ({likes} ❤️)")
                    if st.button("הסתר מהקהילה 🔒", key=f"hide_{story_id}"):
                        toggle_publish_status(story_id, True)
                else:
                    st.warning("🔒 פרטי (רק אתה רואה)")
                    if st.button("פרסם לכולם 📢", key=f"pub_{story_id}"):
                        toggle_publish_status(story_id, False)

                st.markdown("---")
                
                # תקציר הטקסט
                st.write(content[:100] + "...")
                
                # כפתור קריאה מלאה
                if st.button("קרא ספר מלא 📖", key=f"read_{story_id}"):
                    @st.dialog(f"{hero_title}")
                    def show_story():
                        st.markdown(content)
                    show_story()
