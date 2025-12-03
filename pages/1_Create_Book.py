import streamlit as st
import google.generativeai as genai
import sqlite3
import datetime

# --- הגדרות עמוד ---
st.set_page_config(page_title="יצירת ספר", page_icon="✍️", layout="wide")

# --- חיבור למוח (Gemini) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("חסר מפתח API ב-Secrets")
    st.stop()

# --- הגדרת המודל (הגרסה החדשה שמצאנו) ---
MODEL_NAME = 'models/gemini-2.0-flash' 

# --- שמירת נתונים (SQL) ---
def save_story_to_db(title, genre, content):
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS stories (hero TEXT, genre TEXT, content TEXT, created_at TEXT)")
    date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    c.execute("INSERT INTO stories VALUES (?, ?, ?, ?)", (title, genre, content, date))
    conn.commit()
    conn.close()

# --- ניהול זיכרון (Session State) ---
# זה נועד כדי שהצ'אט והטקסט לא יימחקו כשלוחצים על כפתורים
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "manual_text" not in st.session_state:
    st.session_state.manual_text = ""

# ==========================================
# 🤖 הצ'אט החכם (נמצא בצד ימין תמיד)
# ==========================================
with st.sidebar:
    st.header("🤖 העוזר החכם")
    st.caption("התייעץ עם ה-AI תוך כדי עבודה")
    
    # הצגת היסטוריית הצ'אט
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # תיבת קלט לצ'אט
    user_question = st.chat_input("שאל אותי משהו על הסיפור...")
    
    if user_question:
        # 1. מציגים את השאלה של המשתמש
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.write(user_question)
            
        # 2. ה-AI עונה
        with st.chat_message("assistant"):
            with st.spinner("חושב..."):
                model = genai.GenerativeModel(MODEL_NAME)
                # אנחנו שולחים לו הקשר כללי שהוא עוזר כתיבה
                response = model.generate_content(f"אתה עוזר כתיבה חכם. ענה קצר ולעניין על השאלה: {user_question}")
                st.write(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})

# ==========================================
# 📝 המסך הראשי
# ==========================================
st.title("Create New Book ✍️")

# בחירת מצב עבודה
mode = st.radio("בחר מצב כתיבה:", ["✨ כתיבה אוטומטית מלאה", "✍️ כתיבה ידנית עם עוזר"], horizontal=True)
st.divider()

# ------------------------------------------
# מצב 1: כתיבה אוטומטית (כמו קודם + אורך מילים)
# ------------------------------------------
if mode == "✨ כתיבה אוטומטית מלאה":
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("הגדרות הספר")
        title = st.text_input("שם הספר")
        genre = st.selectbox("ז'אנר", ["מדע בדיוני", "פנטזיה", "מתח", "רומן היסטורי", "ילדים"])
        # --- התוספת החדשה: אורך מילים ---
        word_count = st.select_slider("אורך משוער (במילים):", options=[500, 1000, 2000, 5000])
        
    with col2:
        st.subheader("העלילה")
        idea = st.text_area("על מה הסיפור?", height=150)
        
        if st.button("צור את הספר! 🚀", type="primary"):
            with st.spinner(f'כותב ספר באורך {word_count} מילים...'):
                try:
                    model = genai.GenerativeModel(MODEL_NAME)
                    prompt = f"""
                    כתוב ספר מלא בעברית.
                    שם הספר: {title}
                    ז'אנר: {genre}
                    רעיון מרכזי: {idea}
                    אורך יעד: כ-{word_count} מילים.
                    
                    חשוב מאוד: חלק את הסיפור לפרקים עם כותרות ברורות.
                    """
                    response = model.generate_content(prompt)
                    
                    # שמירה והצגה
                    save_story_to_db(title, genre, response.text)
                    st.success("הספר נכתב ונשמר!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# ------------------------------------------
# מצב 2: כתיבה ידנית + עזרה (הפיצ'ר החדש!)
# ------------------------------------------
else:
    st.subheader("סדנת הכתיבה שלך")
    
    manual_title = st.text_input("כותרת הספר שלך")
    
    # אזור הכתיבה הגדול
    txt = st.text_area(
        "כתוב כאן את הסיפור שלך...",
        value=st.session_state.manual_text,
        height=400,
        key="editor_area"
    )
    
    # כפתורי פעולה
    c1, c2, c3 = st.columns([1, 1, 3])
    
    with c1:
        # --- פיצ'ר השלמה אוטומטית ---
        if st.button("✨ תן לי רעיון להמשך"):
            if len(txt) < 10:
                st.warning("כתוב לפחות משפט אחד כדי שאדע איך להמשיך!")
            else:
                with st.spinner("ה-AI קורא את מה שכתבת ומציע המשך..."):
                    model = genai.GenerativeModel(MODEL_NAME)
                    prompt = f"הנה התחלה של סיפור: '{txt}'. כתוב רק פסקה אחת שממשיכה את הסיפור הזה בצורה מעניינת."
                    response = model.generate_content(prompt)
                    st.info("💡 הצעה להמשך (תוכל להעתיק ולהדביק):")
                    st.code(response.text, language="text")

    with c2:
        if st.button("💾 שמור לספרייה"):
            if manual_title and txt:
                save_story_to_db(manual_title, "ידני", txt)
                st.toast("הסיפור נשמר!", icon="✅")
            else:
                st.error("חסר שם או תוכן")
