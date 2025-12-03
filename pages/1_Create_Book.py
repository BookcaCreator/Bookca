import streamlit as st
import google.generativeai as genai
import sqlite3
import datetime

# --- הגדרות ---
st.set_page_config(page_title="יצירת ספר חדש", page_icon="✍️")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("חסר מפתח API")

# --- פונקציית שמירה (אותה אחת מקודם) ---
def save_story_to_db(hero, genre, content):
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS stories (hero TEXT, genre TEXT, content TEXT, created_at TEXT)")
    date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    c.execute("INSERT INTO stories VALUES (?, ?, ?, ?)", (hero, genre, content, date))
    conn.commit()
    conn.close()

# --- עיצוב הכותרת ---
st.title("Create New Book")
st.progress(25) # פס התקדמות כמו בתמונה!

st.subheader("פרטים בסיסיים")

with st.form("new_book_form"):
    # שדות קלט כמו בתמונה שלך
    book_title = st.text_input("שם הספר (Book Title)", placeholder="הכנס את שם הספר...")
    
    col1, col2 = st.columns(2)
    with col1:
        genre = st.selectbox("ז'אנר", ["מדע בדיוני", "פנטזיה", "מתח", "רומן היסטורי"])
    with col2:
        language = st.selectbox("שפה", ["עברית", "English", "Español"])
    
    description = st.text_area("תיאור הספר (Description)", height=150, placeholder="על מה הספר מספר?")
    
    submitted = st.form_submit_button("התחל כתיבה אוטומטית ✨", type="primary")

    if submitted:
        if not book_title or not description:
            st.warning("נא למלא את כל השדות")
        else:
            with st.spinner('Gemini 2.0 בונה את העלילה...'):
                try:
                    model = genai.GenerativeModel('models/gemini-2.0-flash')
                    prompt = f"כתוב פרק ראשון לספר בשם '{book_title}'. ז'אנר: {genre}. תקציר: {description}. שפה: {language}."
                    
                    response = model.generate_content(prompt)
                    
                    # שמירה והצגה
                    save_story_to_db(book_title, genre, response.text)
                    st.success("הספר נוצר בהצלחה!")
                    st.balloons()
                    
                    # הצגת התוצאה בתוך "Expandable" כדי שיראה נקי
                    with st.expander("קרא את הפרק הראשון", expanded=True):
                        st.markdown(response.text)
                        
                except Exception as e:
                    st.error(f"שגיאה: {e}")
