import os
import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from groq import Groq

load_dotenv()

st.set_page_config(
    page_title="PDF AI Analyst 🐾",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

def extract_pdf_text(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("⚠️ Lütfen `.env` dosyanıza `GROQ_API_KEY` değişkenini ekleyin!")
else:
    client = Groq(api_key=api_key)

    with st.sidebar:
        st.markdown("## 🐾 Belge Paneli")
        st.caption("Analiz edilecek PDF belgenizi aşağıya yükleyin.")
        
        uploaded_file = st.file_uploader("PDF Yükle", type=["pdf"])
        
        st.divider()
        st.markdown("### 💡 Rehber")
        st.markdown("""
        1. **Dosya Yükle:** PDF belgenizi ekleyin.
        2. **Soru Sor:** Analiz etmek istediğiniz konuyu yazın.
        3. **Yanıt Al:** Yapay zekadan anında yanıt görün.
        """)
        
        st.divider()
        st.markdown("<div class='footer-text'>🐾</div>", unsafe_allow_html=True)

    st.title(" 🐱 PDF AI Analyst")
    st.caption("Yapay zeka destekli akıllı belge analiz asistanınız.")

    if uploaded_file is not None:

        if "pdf_text" not in st.session_state or st.session_state.get("current_file") != uploaded_file.name:
            with st.spinner("📄 Belge okunuyor ve analiz ediliyor..."):
                st.session_state.pdf_text = extract_pdf_text(uploaded_file)
                st.session_state.current_file = uploaded_file.name
                st.success("Belge başarıyla yüklendi ve hazır!")

        st.divider()

        with st.form("query_form"):
            user_question = st.text_input("💬 Belge hakkında bir soru sorun:", placeholder="Örn: Bu belgedeki ana konuları özetle.")
            submit_button = st.form_submit_button("Soruyu Yanıtla 🌸")

        if submit_button and user_question:
            with st.chat_message("user", avatar="💬"):
                st.write(user_question)
            
            with st.chat_message("assistant", avatar="🐾"):
                with st.spinner("Yanıt hazırlanıyor..."):
                    prompt = f"""
                    Sen profesyonel bir belge analiz uzmanısın. Aşağıdaki metne dayanarak kullanıcının sorusunu Türkçe olarak detaylı, anlaşılır ve kibar bir dille yanıtla.
                    Eğer verilen metinde sorunun cevabı yoksa, cevabın belgede yer almadığını nazikçe belirt.

                    METİN:
                    {st.session_state.pdf_text}

                    SORU:
                    {user_question}
                    """
                    
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.3,
                        )
                        st.write(response.choices[0].message.content)
                    except Exception as e:
                        st.error(f"Bir hata oluştu: {str(e)}")
    else:
        st.info("👈 Başlamak için lütfen sol menüden bir PDF dosyası yükleyin.")