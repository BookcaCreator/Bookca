# --- הגנה: אם לא מחובר, זרוק אותו לדף הבית ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("עליך להתחבר קודם!")
    st.switch_page("Home.py") # מעיף אותו חזרה ללוגין
    st.stop()
    
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

# --- הגדרת המודל ---
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
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "manual_text" not in st.session_state:
    st.session_state.manual_text = ""

# ==========================================
# 🤖 הצ'אט החכם (Sidebar)
# ==========================================
with st.sidebar:
    st.header("🤖 העוזר החכם")
    st.caption("התייעץ עם ה-AI תוך כדי עבודה")
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_question = st.chat_input("שאל אותי משהו על הסיפור...")
    
    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.write(user_question)
            
        with st.chat_message("assistant"):
            with st.spinner("חושב..."):
                model = genai.GenerativeModel(MODEL_NAME)
                response = model.generate_content(f"אתה עוזר כתיבה חכם. ענה קצר ולעניין על השאלה: {user_question}")
                st.write(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})

# ==========================================
# 📝 המסך הראשי
# ==========================================
st.title("Create New Book ✍️")

mode = st.radio("בחר מצב כתיבה:", ["✨ כתיבה אוטומטית מלאה", "✍️ כתיבה ידנית עם עוזר"], horizontal=True)
st.divider()

# ------------------------------------------
# מצב 1: כתיבה אוטומטית
# ------------------------------------------
if mode == "✨ כתיבה אוטומטית מלאה":
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("הגדרות הספר")
        title = st.text_input("שם הספר")
        genre = st.selectbox("ז'אנר", ["מדע בדיוני", "פנטזיה", "מתח", "רומן היסטורי", "ילדים"])
        
        # --- השינוי שעשינו: תיבת מספרים במקום סליידר ---
        # min_value=100 (מינימום מילים)
        # value=1500 (ברירת מחדל)
        # step=100 (קפיצות של 100 כשלוחצים על הפלוס)
        word_count = st.number_input("כמות מילים רצויה:", min_value=100, max_value=50000, value=1500, step=100)
        st.caption("הערה: ה-AI ינסה להתקרב לכמות זו, אך זה לא יהיה מדויק על המילה.")
        
    with col2:
        st.subheader("העלילה")
        idea = st.text_area("על מה הסיפור?", height=150)
        
        if st.button("צור את הספר! 🚀", type="primary"):
            if not title or not idea:
                st.warning("נא למלא שם ספר ורעיון לעלילה")
            else:
                with st.spinner(f'כותב ספר באורך של כ-{word_count} מילים...'):
                    try:
                        model = genai.GenerativeModel(MODEL_NAME)
                        prompt = f"""
                        כתוב ספר מלא בעברית.
                        שם הספר: {title}
                        ז'אנר: {genre}
                        רעיון מרכזי: {idea}
                        אורך יעד: כ-{word_count} מילים.
                        
                        הוראות חשובות:
                        1. חלק את הסיפור לפרקים עם כותרות.
                        2. כתוב בצורה עשירה ומעניינת.
                        3. השתדל להגיע ליעד המילים שהוגדר.
                        """
                        response = model.generate_content(prompt)
                        
                        save_story_to_db(title, genre, response.text)
                        st.success("הספר נכתב ונשמר!")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"שגיאה: {e}")

# ------------------------------------------
# מצב 2: כתיבה ידנית + עזרה
# ------------------------------------------
else:
    st.subheader("סדנת הכתיבה שלך")
    
    manual_title = st.text_input("כותרת הספר שלך")
    
    txt = st.text_area(
        "כתוב כאן את הסיפור שלך...",
        value=st.session_state.manual_text,
        height=400,
        key="editor_area"
    )
    
    c1, c2, c3 = st.columns([1, 1, 3])
    
    with c1:
        if st.button("✨ תן לי רעיון להמשך"):
            if len(txt) < 10:
                st.warning("כתוב לפחות משפט אחד!")
            else:
                with st.spinner("מייצר רעיון..."):
                    model = genai.GenerativeModel(MODEL_NAME)
                    prompt = f"הנה התחלה של סיפור: '{txt}'. כתוב רק פסקה אחת שממשיכה את הסיפור הזה בצורה מעניינת."
                    response = model.generate_content(prompt)
                    st.info("💡 הצעה להמשך:")
                    st.code(response.text, language="text")

    with c2:
        if st.button("💾 שמור לספרייה"):
            if manual_title and txt:
                save_story_to_db(manual_title, "ידני", txt)
                st.toast("הסיפור נשמר!", icon="✅")
            else:
                st.error("חסר שם או תוכן")
