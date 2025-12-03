import streamlit as st
import os
import sqlite3

st.set_page_config(page_title="ניהול מערכת", page_icon="⛔", layout="wide")

# --- הגדרת המנהל ---
ADMIN_USER = "Ranchok" # ⚠️ שנה את זה לשם המשתמש המדויק שלך!

# --- 🛡️ שומר הסף (The Bouncer) ---
# 1. בדיקה אם מחובר בכלל
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("עליך להתחבר קודם!")
    st.switch_page("Home.py")
    st.stop()

# 2. בדיקה אם המשתמש הוא המנהל
if st.session_state['username'] != ADMIN_USER:
    st.error("⛔ אין לך הרשאה להיכנס לכאן. דף זה מיועד למנהלים בלבד.")
    # אופציה: להעיף אותו חזרה לדף הבית או להשאיר אותו מול הודעת השגיאה
    if st.button("חזור לדף הבית"):
        st.switch_page("Home.py")
    st.stop() # הפקודה הזו עוצרת את הקוד כאן! שום דבר למטה לא ירוץ.

# ========================================================
# מכאן והלאה - רק המנהל רואה את הקוד!
# ========================================================

st.title("ממשק ניהול (Admin Only) 🕵️‍♂️")
st.write(f"ברוך הבא, {st.session_state['username']}. כאן נמצאים הכלים הרגישים.")
st.divider()

# --- כלי 1: הורדת גיבוי (Backup) ---
st.subheader("💾 גיבוי נתונים")
st.write("הורד את כל המידע (משתמשים + סיפורים) למחשב שלך.")

db_file = 'stories_v3.db' # וודא שזה השם הנכון של הקובץ שלך

if os.path.exists(db_file):
    with open(db_file, "rb") as fp:
        st.download_button(
            label="📥 הורד קובץ מסד נתונים מלא (Full DB)",
            data=fp,
            file_name="stories_backup.db",
            mime="application/octet-stream",
            type="primary"
        )
else:
    st.warning("לא נמצא קובץ נתונים.")

st.divider()

# --- כלי 2: שחזור מגיבוי (Restore) ---
st.subheader("♻️ שחזור מערכת")
st.warning("זהירות! פעולה זו תמחק את כל המידע הקיים באתר ותחליף אותו בקובץ שתעלה.")

uploaded_file = st.file_uploader("העלה קובץ גיבוי לשחזור", type="db")

if uploaded_file is not None:
    if st.button("⚠️ דרוס נתונים ושחזר"):
        with open(db_file, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("השחזור הצליח! המערכת חזרה אחורה בזמן.")
        st.balloons()

st.divider()

# --- כלי 3: הצצה לנתונים (View Users) ---
st.subheader("👥 רשימת משתמשים רשומים")
if st.checkbox("הצג טבלת משתמשים"):
    conn = sqlite3.connect(db_file)
    # שולף רק שמות ואימיילים (בלי סיסמאות!)
    users = conn.execute("SELECT username, email, name FROM usersTable").fetchall()
    conn.close()
    
    # מציג בטבלה יפה
    st.table(users)ד
