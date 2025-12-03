import streamlit as st
import sqlite3

st.set_page_config(page_title="קהילת הסופרים", page_icon="🌎", layout="wide")

# --- הגנה ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.switch_page("Home.py")

DB_NAME = 'stories_v3.db'

def get_public_stories():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # שולף רק ספרים שסומנו כציבוריים (is_public=1)
    c.execute("SELECT rowid, * FROM stories WHERE is_public=1 ORDER BY rowid DESC")
    data = c.fetchall()
    conn.close()
    return data

def add_like(story_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # מוסיף 1 לכמות הלייקים
    c.execute("UPDATE stories SET likes = likes + 1 WHERE rowid=?", (story_id,))
    conn.commit()
    conn.close()
    st.toast("נתת לייק! ❤️")
    # אנחנו לא עושים rerun כדי לא להציק למשתמש, המספר יתעדכן בפעם הבאה

st.title("🌎 קהילת הסופרים")
st.subheader("גלה ספרים שכתבו משתמשים אחרים")
st.divider()

stories = get_public_stories()

if not stories:
    st.info("עדיין אין ספרים בקהילה. היה הראשון לפרסם!")
else:
    cols = st.columns(3)
    for index, story in enumerate(stories):
        # [0]rowid, [1]user, [2]hero, [3]genre, [4]content, [5]date, [6]is_public, [7]likes
        
        with cols[index % 3]:
            with st.container(border=True):
                st.subheader(f"📖 {story[2]}")
                # מציג מי הסופר!
                st.markdown(f"**נכתב ע'':** {story[1]}")
                st.caption(f"{story[3]} | {story[5]}")
                
                st.write(story[4][:150] + "...")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"❤️ {story[7]}", key=f"like_{story[0]}"):
                        add_like(story[0])
                with col_b:
                    if st.button("קרא עוד", key=f"community_read_{story[0]}"):
                        @st.dialog(f"{story[2]} / {story[1]}")
                        def show_story():
                            st.markdown(story[4])
                        show_story()
