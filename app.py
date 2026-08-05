import os
import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from groq import Groq

load_dotenv()

st.set_page_config(
    page_title="PDF AI Analyst",
    page_icon="📄",
    layout="wide"
)

# CSS ile Arayüz Tasarımı
st.markdown("""
    <style>
    .main {
        background-color: #fafafa;
    }
    .stButton>button {
        width: 100%;
        background-color: #6c5ce7;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #a29bfe;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

def extract_pdf_text(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

# API Key Kontrolü
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("⚠️ Lütfen `.env` dosyanıza `GROQ_API_KEY` değişkenini ekleyin!")
else:
    client = Groq(api_key=api_key)

    with st.sidebar:
        st.title("📄 Dosya Paneli")
        st.caption("Analiz edilecek PDF belgenizi buraya yükleyin.")
        
        uploaded_file = st.file_uploader("PDF Yükle", type=["pdf"])
        
        st.divider()
        st.markdown("### 💡 Nasıl Kullanılır?")
        st.markdown("""
        1. Sol panelden bir PDF yükleyin.
        2. Metin okunduktan sonra sorunuzu yazın.
        3. **Soruyu Yanıtla** butonuna basarak sorun.
        """)

    st.title("✨ PDF AI Analyst")
    st.caption("Yapay zeka destekli akıllı belge analiz asistanı.")

    if uploaded_file is not None:

        if "pdf_text" not in st.session_state or st.session_state.get("current_file") != uploaded_file.name:
            with st.spinner("📄 Belge okunuyor ve analiz ediliyor..."):
                st.session_state.pdf_text = extract_pdf_text(uploaded_file)
                st.session_state.current_file = uploaded_file.name
                st.success("Belge başarıyla okundu!")

        st.divider()

        # Soru Sorma Formu
        with st.form("query_form"):
            user_question = st.text_input("💬 Belge hakkında soru sorun:", placeholder="Örn: Bu belgedeki ana konu nedir?")
            submit_button = st.form_submit_button("Soruyu Yanıtla")

        if submit_button and user_question:
            with st.chat_message("user"):
                st.write(user_question)
            
            with st.chat_message("assistant"):
                with st.spinner("Düşünüyor..."):
                    prompt = f"""
                    Sen profesyonel bir belge analiz uzmanısın. Aşağıdaki metne dayanarak kullanıcının sorusunu Türkçe olarak detaylı ve net bir şekilde yanıtla.
                    Eğer verilen metinde sorunun cevabı yoksa, cevabın belgede yer almadığını kibarca belirt.

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