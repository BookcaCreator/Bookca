import streamlit as st
import sqlite3
import hashlib
import extra_streamlit_components as stx # הספרייה החדשה לעוגיות 🍪
import datetime

# --- הגדרות עמוד ---
st.set_page_config(page_title="BookCraft AI", page_icon="📚", layout="wide")

# --- מנהל העוגיות (Cookies) ---
# הפונקציה הזו מפעילה את מנהל העוגיות
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

# --- פונקציות אבטחה ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# --- מסד נתונים ---
def init_db():
    conn = sqlite3.connect('stories_v3.db')
    c = conn.cursor()
    # הוספנו את עמודת role
    c.execute('''CREATE TABLE IF NOT EXISTS usersTable
                 (username TEXT PRIMARY KEY, password TEXT, email TEXT, name TEXT, role TEXT DEFAULT 'User')''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS stories
                 (username TEXT, hero TEXT, genre TEXT, content TEXT, created_at TEXT, 
                  is_public BOOLEAN DEFAULT 0, likes INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def add_user(username, password, email, name):
    conn = sqlite3.connect('stories_v3.db')
    c = conn.cursor()
    # כברירת מחדל, כל מי שנרשם הוא 'User' (ולא Admin)
    c.execute('INSERT INTO usersTable(username,password,email,name,role) VALUES (?,?,?,?,?)', 
              (username, password, email, name, 'User'))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('stories_v3.db')
    c = conn.cursor()
    c.execute('SELECT * FROM usersTable WHERE username =? AND password = ?', (username,password))
    data = c.fetchall()
    conn.close()
    return data

init_db()

# --- ניהול התחברות (לוגיקה משודרגת!) ---

# 1. בדיקה: האם יש עוגייה בדפדפן?
cookie_username = cookie_manager.get(cookie="bookcraft_user")

if 'logged_in' not in st.session_state:
    # אם מצאנו עוגייה - אנחנו מחברים אותו אוטומטית!
    if cookie_username:
        st.session_state['logged_in'] = True
        st.session_state['username'] = cookie_username
        st.success(f"התחברת אוטומטית כ-{cookie_username} 🍪")
    else:
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''

# ==========================================
# 🔒 מסך כניסה (אם לא מחובר)
# ==========================================
if not st.session_state['logged_in']:
    st.title("ברוכים הבאים ל-BookCraft AI 🔐")
    
    tab1, tab2 = st.tabs(["כניסה", "הרשמה"])

    with tab1:
        st.subheader("התחבר למערכת")
        username = st.text_input("שם משתמש")
        password = st.text_input("סיסמה", type='password')
        
        # --- הוספנו את הצ'קבוקס כאן ---
        remember_me = st.checkbox("זכור אותי במחשב זה")
        
        if st.button("התחבר"):
            hashed_pswd = make_hashes(password)
            result = login_user(username, hashed_pswd)
            if result:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                
                # אם הוא סימן "זכור אותי" - יוצרים עוגייה ל-30 יום
                if remember_me:
                    expires = datetime.datetime.now() + datetime.timedelta(days=30)
                    cookie_manager.set("bookcraft_user", username, expires=expires)
                
                st.success("התחברת בהצלחה!")
                st.rerun()
            else:
                st.error("שם משתמש או סיסמה שגויים")

    with tab2:
        st.subheader("הרשמה")
        new_user = st.text_input("בחר שם משתמש (באנגלית)")
        new_name = st.text_input("השם המלא שלך")
        new_email = st.text_input("כתובת אימייל")
        new_password = st.text_input("בחר סיסמה", type='password')
        
        if st.button("הרשם"):
            if new_user and new_password:
                try:
                    add_user(new_user, make_hashes(new_password), new_email, new_name)
                    st.success("נרשמת בהצלחה! כנס ללשונית 'כניסה'.")
                except:
                    st.warning("שם המשתמש תפוס.")
            else:
                st.error("מלא את כל השדות")

# ==========================================
# 🔓 האפליקציה (אם מחובר)
# ==========================================
else:
    st.sidebar.success(f"מחובר כ: {st.session_state['username']}")
    
    # כפתור התנתקות מוחק גם את העוגייה!
    if st.sidebar.button("התנתק (Logout)"):
        cookie_manager.delete("bookcraft_user") # מוחק את העוגייה
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.rerun()

    st.title(f"שלום, {st.session_state['username']}! 👋")
    st.subheader("מרכז השליטה")
    
    # סטטיסטיקות
    def get_stats():
        conn = sqlite3.connect('stories_v3.db')
        c = conn.cursor()
        try:
            c.execute("SELECT COUNT(*) FROM stories WHERE username=?", (st.session_state['username'],))
            total = c.fetchone()[0]
        except:
            total = 0
        conn.close()
        return total

    col1, col2, col3 = st.columns(3)
    total = get_stats()
    col1.metric("הספרים שלי", total)
    col2.metric("סטטוס", "סופר מתחיל" if total < 3 else "סופר מתקדם")
    col3.metric("מילים שנכתבו", total * 1000)

    st.divider()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("✍️ **כתוב ספר**")
        if st.button("ליצירה"): st.switch_page("pages/1_Create_Book.py")
    with c2:
        st.info("📖 **הספרייה שלי**")
        if st.button("לספרייה"): st.switch_page("pages/2_My_Library.py")
    with c3:
        st.info("🌎 **הקהילה**")
        if st.button("לקהילה"): st.switch_page("pages/3_Community.py")

