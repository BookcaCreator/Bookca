import streamlit as st
import sqlite3
import hashlib # הספרייה לאבטחת סיסמאות

# --- הגדרות עמוד ---
st.set_page_config(page_title="BookCraft AI", page_icon="📚", layout="wide")

# --- פונקציות אבטחה (Hashing) ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# --- ניהול מסד נתונים (משתמשים + סיפורים) ---
def init_db():
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    
    # טבלת משתמשים (חדש!)
    c.execute('''CREATE TABLE IF NOT EXISTS usersTable
                 (username TEXT PRIMARY KEY, password TEXT, email TEXT, name TEXT)''')
    
    # טבלת סיפורים (מעודכנת - הוספנו עמודת username)
    c.execute('''CREATE TABLE IF NOT EXISTS stories
                 (username TEXT, hero TEXT, genre TEXT, content TEXT, created_at TEXT)''')
                 
    conn.commit()
    conn.close()

def add_user(username, password, email, name):
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    c.execute('INSERT INTO usersTable(username,password,email,name) VALUES (?,?,?,?)', 
              (username, password, email, name))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    c.execute('SELECT * FROM usersTable WHERE username =? AND password = ?', (username,password))
    data = c.fetchall()
    conn.close()
    return data

# אתחול ה-DB
init_db()

# --- ניהול מצב התחברות (Session State) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

# ==========================================
# 🔒 מסך התחברות / הרשמה (אם לא מחובר)
# ==========================================
if not st.session_state['logged_in']:
    st.title("ברוכים הבאים ל-BookCraft AI 🔐")
    
    tab1, tab2 = st.tabs(["כניסה (Login)", "הרשמה (Sign Up)"])

    with tab1: # התחברות
        st.subheader("התחבר למערכת")
        username = st.text_input("שם משתמש")
        password = st.text_input("סיסמה", type='password')
        
        if st.button("התחבר"):
            hashed_pswd = make_hashes(password)
            result = login_user(username, hashed_pswd)
            if result:
                st.success(f"התחברת בהצלחה כ-{username}!")
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.rerun() # מרענן את הדף כדי להכניס אותו פנימה
            else:
                st.error("שם משתמש או סיסמה שגויים")

    with tab2: # הרשמה
        st.subheader("צור משתמש חדש")
        new_user = st.text_input("בחר שם משתמש (באנגלית)")
        new_name = st.text_input("השם המלא שלך")
        new_email = st.text_input("כתובת אימייל")
        new_password = st.text_input("בחר סיסמה", type='password')
        
        if st.button("הרשם"):
            if new_user and new_password:
                try:
                    add_user(new_user, make_hashes(new_password), new_email, new_name)
                    st.success("נרשמת בהצלחה! עכשיו עבור ללשונית 'כניסה' והתחבר.")
                except:
                    st.warning("שם המשתמש הזה כבר תפוס, נסה אחר.")
            else:
                st.error("נא למלא את כל השדות")

# ==========================================
# 🔓 האפליקציה עצמה (רק אם מחובר!)
# ==========================================
else:
    st.sidebar.success(f"מחובר כ: {st.session_state['username']}")
    if st.sidebar.button("התנתק (Logout)"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.rerun()

    # --- כאן מתחיל הדשבורד הרגיל שלך ---
    st.title(f"שלום, {st.session_state['username']}! 👋")
    st.subheader("מרכז השליטה שלך")
    
    # (כאן תדביק את הקוד של הסטטיסטיקות והכפתורים הגדולים שנתתי לך קודם...)
    # ...
    
    st.info("👈 בחר פעולה מהתפריט בצד: 'Create Book' או 'My Library'")
