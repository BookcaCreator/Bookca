import streamlit as st
import os
import sqlite3
import pandas as pd # ספרייה לטיפול בטבלאות בצורה נוחה

st.set_page_config(page_title="ניהול מערכת", page_icon="⛔", layout="wide")

ADMIN_USER = "Ranchok" # ⚠️ וודא שזה השם שלך!
DB_FILE = 'stories_v3.db'

# --- הגנה ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("עליך להתחבר קודם!")
    st.switch_page("Home.py")
    st.stop()

if st.session_state['username'] != ADMIN_USER:
    st.error("⛔ אין לך הרשאה להיכנס לכאן.")
    if st.button("חזור לדף הבית"):
        st.switch_page("Home.py")
    st.stop()

# ========================================================
# פונקציות עזר למנהל
# ========================================================

# פונקציה לתיקון המסד (הוספת עמודת Role אם חסרה)
def migrate_db_add_role():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        # מנסה להוסיף את העמודה. אם היא קיימת, זה ייכשל וזה בסדר.
        c.execute("ALTER TABLE usersTable ADD COLUMN role TEXT DEFAULT 'User'")
        conn.commit()
        st.success("עמודת Role נוספה למסד הנתונים בהצלחה!")
    except:
        pass # העמודה כנראה כבר קיימת
    conn.close()

# פונקציה לשינוי תפקיד
def update_user_role(username, new_role):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE usersTable SET role = ? WHERE username = ?", (new_role, username))
    conn.commit()
    conn.close()
    st.toast(f"התפקיד של {username} עודכן ל-{new_role}!", icon="✅")
    st.rerun()

# ========================================================
# ממשק הניהול
# ========================================================

st.title("ממשק ניהול (CRM) 🕵️‍♂️")

# --- כפתור טכני (חובה ללחוץ עליו פעם אחת!) ---
# זה נועד לשדרג את מסד הנתונים הישן לחדש עם ה-Roles
with st.expander("⚠️ פעולות תחזוקה (לחץ כאן אם הטבלה למטה עושה שגיאה)"):
    if st.button("תקן מסד נתונים (הוסף עמודת Role)"):
        migrate_db_add_role()

st.divider()

# --- טבלת המשתמשים המתוחכמת ---
st.subheader("👥 ניהול משתמשים")

try:
    conn = sqlite3.connect(DB_FILE)
    
    # שאילתה חכמה: מחברת את המשתמשים עם ספירה של הספרים שלהם
    query = """
    SELECT 
        u.rowid as "No' of user",
        u.username as "Username",
        u.role as "Role",
        (SELECT COUNT(*) FROM stories s WHERE s.username = u.username) as "No' of books",
        u.password as "password",
        u.email as "Email"
    FROM usersTable u
    """
    
    # שימוש ב-Pandas כדי להציג את זה יפה
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # הצגת הטבלה על כל המסך
    st.dataframe(df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("לא הצלחתי לטעון את הטבלה. נסה ללחוץ על 'תקן מסד נתונים' למעלה.")
    st.error(e)

st.divider()

# --- שינוי תפקידים ---
st.subheader("✏️ שינוי תפקיד למשתמש")

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    # בחירת משתמש מתוך רשימה (כדי לא לכתוב סתם שמות)
    try:
        user_list = df["Username"].tolist()
        selected_user = st.selectbox("בחר משתמש:", user_list)
    except:
        selected_user = None

with col2:
    new_role = st.selectbox("בחר תפקיד חדש:", ["User", "Admin", "VIP", "Editor"])

with col3:
    st.write("") # רווח לעיצוב
    st.write("") 
    if st.button("עדכן תפקיד"):
        if selected_user:
            update_user_role(selected_user, new_role)

st.divider()

# --- כלי גיבוי (השארנו אותם כי הם חשובים) ---
st.subheader("💾 גיבוי ושחזור")
if os.path.exists(DB_FILE):
    with open(DB_FILE, "rb") as fp:
        st.download_button("📥 הורד גיבוי מלא", fp, "stories_backup.db")

uploaded_file = st.file_uploader("שחזור מגיבוי", type="db")
if uploaded_file and st.button("⚠️ שחזר"):
    with open(DB_FILE, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("שוחזר!")
