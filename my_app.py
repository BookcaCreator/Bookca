import streamlit as st
import google.generativeai as genai

# ככה מושכים את הסיסמה מהכספת הסודית של Streamlit Cloud
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# מגדירים לתוכנה להשתמש במפתח הזה
genai.configure(api_key=GOOGLE_API_KEY)

# --- הגדרות עיצוב ---
st.set_page_config(page_title="הסופר המלאכותי", page_icon="📚", layout="centered")

st.title("📚 הסופר המלאכותי")
st.caption("מיזם כיתת ממר''ם - Education 2026")

# --- צד שמאל: הגדרות ---
with st.sidebar:
    st.header("⚙️ הגדרות הסיפור")
    hero_name = st.text_input("שם הגיבור:", "דני")
    genre = st.selectbox("ז'אנר:", ["הרפתקאות", "מדע בדיוני", "מתח", "פנטזיה", "סיפור מצחיק"])
    length = st.select_slider("אורך הסיפור:", options=["קצר", "בינוני", "ארוך"])

# --- המרכז: הרעיון ---
st.write("### על מה נכתוב היום?")
user_idea = st.text_area("תאר את הרעיון לסיפור:", "ילד שמוצא מפה עתיקה בדרך לבית הספר ומגלה עולם נסתר")

# --- הלוגיקה (המוח) ---
if st.button("צור ספר! 🚀", type="primary"):
    
    # בדיקה שהמפתח לא ריק
    if "הדבק_כאן" in GOOGLE_API_KEY:
        st.error("⚠️ שכחת להדביק את ה-API Key בקוד! (שורה 6)")
    else:
        # אנימציה בזמן שהמחשב חושב
        with st.spinner('הבינה המלאכותית כותבת את הסיפור...'):
            try:
                # בחירת המודל
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # הבקשה ל-AI
                my_prompt = f"""
                כתוב לי סיפור יצירתי ומרתק בעברית.
                הגיבור: {hero_name}
                הסגנון: {genre}
                אורך: {length}
                רעיון מרכזי: {user_idea}
                
                חלק את הסיפור לפסקאות וכותרות כדי שיהיה נעים לקריאה.
                """
                
                # יצירת הסיפור
                response = model.generate_content(my_prompt)
                
                # הצגת התוצאה
                st.success("הסיפור מוכן!")
                st.markdown("---")
                st.markdown(response.text) 
                st.balloons()
                
            except Exception as e:
                st.error(f"אופס, הייתה שגיאה: {e}")

                st.info("טיפ: בדוק אם המפתח שהעתקת נכון ומלא.")
