import streamlit as st
import sqlite3

st.set_page_config(page_title="הספרייה שלי", page_icon="📚", layout="wide")

# --- פונקציה לשליפת הספרים ---
def get_all_stories():
    # מתחבר למסד הנתונים ומושך את הכל
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    # אנחנו רוצים את הספרים החדשים למעלה
    c.execute("SELECT rowid, * FROM stories ORDER BY rowid DESC")
    data = c.fetchall()
    conn.close()
    return data

# --- כותרת ---
st.title("📚 הספרייה שלי")
st.caption("כל הספרים שיצרת בעזרת BookCraft AI")

st.divider()

# --- הצגת הספרים ---
stories = get_all_stories()

if not stories:
    st.info("הספרייה ריקה עדיין... רוץ ליצור את הספר הראשון שלך בדף 'Create Book'!")
    if st.button("עבור ליצירת ספר"):
        st.switch_page("pages/1_Create_Book.py")

else:
    # כאן אנחנו בונים את התצוגה היפה (כמו גריד)
    # נציג 3 ספרים בכל שורה
    cols = st.columns(3)
    
    for index, story in enumerate(stories):
        # story = (id, hero, genre, content, date)
        # אנחנו מחלקים את הספרים בין העמודות באופן מחזורי
        with cols[index % 3]:
            # מסגרת יפה לכל ספר
            with st.container(border=True):
                st.subheader(f"📘 {story[1]}") # שם הגיבור ככותרת (אפשר לשנות לשם הספר)
                st.caption(f"ז'אנר: {story[2]} | נכתב ב: {story[4]}")
                st.write("---")
                # הצצה לתחילת הסיפור (רק 100 תווים ראשונים)
                preview = story[3][:100] + "..."
                st.write(preview)
                
                # כפתור לקריאה מלאה
                # שימוש ב-key ייחודי לכל כפתור כדי שלא יתבלבלו
                if st.button("קרא ספר מלא 📖", key=f"read_{index}"):
                    # כשלוחצים, נפתח חלון קופץ (Dialog) עם הסיפור
                    @st.dialog(f"הסיפור על {story[1]}")
                    def show_story():
                        st.markdown(story[3])
                    show_story()
