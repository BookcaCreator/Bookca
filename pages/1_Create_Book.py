import streamlit as st
import google.generativeai as genai
import sqlite3
import datetime

# --- הגדרות עמוד ---
st.set_page_config(page_title="יצירת ספר", page_icon="✍️", layout="wide")

# --- 🛡️ הגנה: בדיקה אם המשתמש מחובר ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("עליך להתחבר קודם!")
    st.switch_page("Home.py") 
    st.stop()

# --- חיבור למוח (Gemini) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("חסר מפתח API ב-Secrets")
    st.stop()

MODEL_NAME = 'models/gemini-2.0-flash' 

# --- שמירת נתונים (SQL) - הגרסה החדשה עם שם משתמש! ---
def save_story_to_db(title, genre, content):
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    # יוצר טבלה עם עמודת username אם לא קיימת
    c.execute("CREATE TABLE IF NOT EXISTS stories (username TEXT, hero TEXT, genre TEXT, content TEXT, created_at TEXT)")
    date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # לוקח את המשתמש הנוכחי מהזיכרון
    current_user = st.session_state['username']
    
    # שומר את הסיפור יחד עם שם המשתמש
    c.execute("INSERT INTO stories VALUES (?, ?, ?, ?, ?)", (current_user, title, genre, content, date))
    conn.commit()
    conn.close()

# --- ניהול זיכרון לצ'אט ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "manual_text" not in st.session_state:
    st.session_state.manual_text = ""

# ==========================================
# 🤖 הצ'אט החכם (Sidebar)
# ==========================================
with st.sidebar:
    st.header(f"שלום, {st.session_state['username']} 👋")
    st.divider()
    st.header("🤖 העוזר החכם")
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_question = st.chat_input("התייעץ איתי...")
    
    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.write(user_question)
            
        with st.chat_message("assistant"):
            with st.spinner("..."):
                model = genai.GenerativeModel(MODEL_NAME)
                response = model.generate_content(f"ענה קצר ולעניין כעוזר כתיבה: {user_question}")
                st.write(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})

# ==========================================
# 📝 המסך הראשי
# ==========================================
st.title("Create New Book ✍️")

mode = st.radio("בחר מצב:", ["✨ כתיבה אוטומטית מלאה", "✍️ כתיבה ידנית עם עוזר"], horizontal=True)
st.divider()

if mode == "✨ כתיבה אוטומטית מלאה":
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("הגדרות")
        title = st.text_input("שם הספר")
        genre = st.selectbox("ז'אנר", ["מדע בדיוני", "פנטזיה", "מתח", "רומן היסטורי", "ילדים"])
        word_count = st.number_input("כמות מילים רצויה:", min_value=100, max_value=50000, value=1500, step=100)
    with col2:
        st.subheader("העלילה")
        idea = st.text_area("על מה הסיפור?", height=150)
        
        if st.button("צור את הספר! 🚀", type="primary"):
            if not title or not idea:
                st.warning("חסרים פרטים")
            else:
                with st.spinner(f'כותב ספר...'):
                    try:
                        model = genai.GenerativeModel(MODEL_NAME)
                        prompt = f"""
                        כתוב ספר מלא בעברית. שם: {title}. ז'אנר: {genre}. רעיון: {idea}. אורך: כ-{word_count} מילים.
                        חלק לפרקים עם כותרות.
                        """
                        response = model.generate_content(prompt)
                        save_story_to_db(title, genre, response.text)
                        st.success("הספר נשמר בחשבון שלך!")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"שגיאה: {e}")

else: # כתיבה ידנית
    st.subheader("הסדנה שלך")
    manual_title = st.text_input("כותרת הספר")
    txt = st.text_area("הסיפור שלך...", value=st.session_state.manual_text, height=400)
    
    c1, c2 = st.columns([1, 4])
    with c1:
        if st.button("💾 שמור"):
            if manual_title and txt:
                save_story_to_db(manual_title, "ידני", txt)
                st.toast("נשמר בהצלחה!")
            else:
                st.error("חסר שם או תוכן")
    with c2:
        if st.button("✨ תן לי רעיון להמשך"):
            if len(txt) > 5:
                model = genai.GenerativeModel(MODEL_NAME)
                res = model.generate_content(f"המשך את הטקסט בפסקה אחת: {txt}")
                st.info(res.text)
