import streamlit as st
import google.generativeai as genai
import sqlite3
import datetime

# --- הגדרות ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ שגיאה במפתח API.")
    st.stop()

# --- מסד נתונים ---
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

init_db()

# --- עיצוב ---
st.set_page_config(page_title="BookCraft AI", page_icon="📚", layout="centered")
st.title("📚 BookCraft AI")

# --- כפתור טכנאי לבדיקת מודלים (החלק החדש!) ---
with st.sidebar:
    st.header("⚙️ הגדרות")
    if st.button("🛠️ בדוק אילו מודלים זמינים"):
        st.write("בודק מודלים...")
        try:
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            st.success(f"נמצאו {len(available_models)} מודלים:")
            st.code(available_models) # זה ידפיס את הרשימה המדויקת!
        except Exception as e:
            st.error(f"שגיאה בבדיקה: {e}")

# --- האפליקציה הרגילה ---
tab1, tab2 = st.tabs(["✍️ יצירה", "📖 ספרייה"])

with tab1:
    with st.form("story_form"):
        hero_name = st.text_input("גיבור", "דני")
        genre = st.selectbox("ז'אנר", ["הרפתקאות", "מדע בדיוני", "פנטזיה"])
        user_idea = st.text_area("רעיון", "ילד שמוצא רובוט")
        submitted = st.form_submit_button("צור סיפור! 🚀", type="primary")

        if submitted:
            with st.spinner('כותב...'):
                try:
                    # ניסיון ראשון: המודל החדש
                    model_name = 'gemini-1.5-flash'
                    
                    # אם הרשימה למעלה תראה שצריך 'models/gemini-pro', נחליף את זה
                    model = genai.GenerativeModel(model_name)
                    
                    prompt = f"כתוב סיפור על {hero_name} בסגנון {genre}. רעיון: {user_idea}"
                    response = model.generate_content(prompt)
                    
                    st.success("מוכן!")
                    st.write(response.text)
                    save_story_to_db(hero_name, genre, response.text)
                    
                except Exception as e:
                    st.error(f"שגיאה במודל {model_name}:")
                    st.warning(str(e))
                    st.info("טיפ: תשתמש בכפתור בצד ימין כדי לראות איזה מודל זמין ולשנות את השם בקוד בהתאם.")

with tab2:
    st.write("הספרייה")
    stories = get_all_stories()
    for s in stories:
        with st.expander(f"{s[0]} - {s[3]}"):
            st.write(s[2])
