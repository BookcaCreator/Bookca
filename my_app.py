import streamlit as st
import google.generativeai as genai
import sqlite3
import datetime

# --- שלב 1: הגדרות וחיבור ל-Secrets ---
# כאן התיקון הגדול! אנחנו מושכים את המפתח מהכספת של Streamlit
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ שגיאה בטעינת המפתח! וודא שהגדרת את GOOGLE_API_KEY ב-Secrets באתר של Streamlit.")
    st.stop() # עוצר את האפליקציה אם אין מפתח

# --- פונקציות SQL (שמירת סיפורים) ---
def init_db():
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stories
                 (hero TEXT, genre TEXT, content TEXT, created_at TEXT)''')
    conn.commit()
    conn.close()

def save_story_to_db(hero, genre, content):
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    c.execute("INSERT INTO stories VALUES (?, ?, ?, ?)", (hero, genre, content, date))
    conn.commit()
    conn.close()

def get_all_stories():
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    c.execute("SELECT * FROM stories ORDER BY rowid DESC")
    data = c.fetchall()
    conn.close()
    return data

# אתחול מסד הנתונים
init_db()

# --- עיצוב האתר ---
st.set_page_config(page_title="BookCraft AI", page_icon="📚", layout="centered")

st.title("📚 BookCraft AI")
st.caption("הסופר המלאכותי - מיזם כיתת ממר''ם")

# --- לשוניות ---
tab1, tab2 = st.tabs(["✍️ יצירת סיפור", "📖 הספרייה המשותפת"])

# --- טאב 1: יצירה ---
with tab1:
    with st.form("story_form"): # הוספתי טופס כדי שזה יראה מסודר
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.info("הגדרות")
            hero_name = st.text_input("שם הגיבור:", "דני")
            genre = st.selectbox("ז'אנר:", ["הרפתקאות", "מדע בדיוני", "מתח", "פנטזיה", "קומדיה"])
        
        with col2:
            st.write("על מה הסיפור?")
            user_idea = st.text_area("תאר את הרעיון בכמה מילים:", "ילד שמוצא רובוט בחצר ומגלה שהוא בא מהעתיד")
        
        submitted = st.form_submit_button("צור סיפור! 🚀", type="primary")

        if submitted:
            with st.spinner('הבינה המלאכותית כותבת את הסיפור שלך...'):
                try:
                    # שימוש במודל החדש והמהיר
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""
                    כתוב סיפור קצר ומרתק בעברית.
                    הגיבור: {hero_name}
                    הסגנון
