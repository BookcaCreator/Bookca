import streamlit as st
import os
import sqlite3

st.set_page_config(page_title="ניהול מערכת", page_icon="⛔", layout="wide")

# --- הגדרת המנהל ---
# כאן אתה קובע מי המנהל. וודא שהשם הזה קיים במערכת (שנרשמת איתו)!
ADMIN_USER = "Ranchok" 

# --- 🛡️ שומר הסף (The Bouncer) ---
# 1. בדיקה אם מחובר בכלל
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("עליך להתחבר קודם!")
    st.switch_page("Home.py")
    st.stop()

# 2. בדיקה אם המשתמש הוא המנהל
if st.session_state['username'] != ADMIN_USER:
    st.error("⛔ אין לך הרשאה להיכנס לכאן.")
    if st.button("חזור לדף הבית"):
        st.switch_page("Home.py")
    st.stop()

# ========================================================
# מכאן והלאה - רק המנהל רואה את הקוד!
# ========================================================

st.title("ממשק ניהול (Admin Only) 🕵️‍♂️")
st.write(f"מחובר כ: {st.session_state['username']}")
st.divider()

# שם קובץ הנתונים (וודא שזה תואם למה שיש ב-Home.py)
db_file = 'stories_v3.db'

# --- כלי 1: הורדת גיבוי (Backup) ---
st.subheader("💾 גיבוי נתונים")
st.caption("הורד את כל המידע למחשב שלך לשמירה")

if os.path.exists(db_file):
    with open(db_file, "rb") as fp:
        st.download_button(
            label="📥 הורד גיבוי (stories_v3.db)",
            data=fp,
            file_name="stories_backup.db",
            mime="application/octet-stream",
            type="primary"
        )
else:
    st.warning("לא נמצא קובץ נתונים פעיל.")

st.divider()

# --- כלי 2: שחזור מגיבוי (Restore) ---
st.subheader("♻️ שחזור מערכת")
st.caption("העלה קובץ גיבוי כדי להחזיר נתונים שנמחקו")

uploaded_file = st.file_uploader("בחר קובץ .db מהמחשב", type="db")

if uploaded_file is not None:
    if st.button("⚠️ דרוס נתונים ושחזר"):
        try:
            with open(db_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("השחזור הצליח! הנתונים חזרו.")
            st.balloons()
        except Exception as e:
            st.error(f"שגיאה בשחזור: {e}")

st.divider()

# --- כלי 3: הצצה לנתונים (View Users) ---
st.subheader("👥 משתמשים רשומים")
if st.checkbox("הצג טבלת משתמשים"):
    try:
        conn = sqlite3.connect(db_file)
        # שולף שם ואימייל בלבד
        users = conn.execute("SELECT username, email, name FROM usersTable").fetchall()
        conn.close()
        st.table(users)
    except Exception as e:
        st.error("לא ניתן לקרוא את טבלת המשתמשים (אולי הקובץ ריק?)")
