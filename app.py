import streamlit as st
import google.generativeai as genai
import os

# --- CONFIGURATION ---
# Fetch the key securely from Streamlit Secrets
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)

# --- UI SETUP ---
st.set_page_config(
    page_title="MACE Connect",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MATERIAL 3 CSS (WITH GOOGLE SANS LOOK) ---
st.markdown("""
<style>
    /* Import 'Outfit' - The closest open-source match to Google Sans */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');

    /* Global Font Settings */
    html, body, [class*="css"] {
        font-family: 'Google Sans', 'Outfit', sans-serif;
    }

    /* 1. BACKGROUND (Surface) */
    .stApp {
        background-color: #Fdfdf6;
    }

    /* 2. SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #F0F5F1;
        border-right: none;
    }
    
    /* 3. HEADERS */
    h1, h2, h3 {
        color: #1A1C19;
        font-weight: 600;
        letter-spacing: -0.5px;
    }

    /* 4. CHAT BUBBLES */
    
    /* USER: Primary Container (Subtle Green) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #C4EED0; 
        color: #072113;
        border-radius: 24px 24px 4px 24px;
        padding: 16px;
        border: none;
        margin-bottom: 12px;
    }
    
    /* AI: Surface Container High (White Card) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #FFFFFF;
        color: #1A1C19;
        border-radius: 24px 24px 24px 4px;
        padding: 16px;
        border: 1px solid #E3E3E3;
        margin-bottom: 12px;
        box-shadow: 0px 1px 2px rgba(0,0,0,0.05);
    }
    
    /* Avatar Styling */
    .stChatMessage .stAvatar {
        background-color: #006C4C;
        color: white;
    }

    /* 5. INPUT FIELD */
    .stChatInputContainer textarea {
        background-color: #F0F5F1;
        border-radius: 28px;
        border: 1px solid transparent;
        padding: 12px 20px;
        color: #1A1C19;
        font-family: 'Google Sans', 'Outfit', sans-serif;
    }
    .stChatInputContainer textarea:focus {
        border: 1px solid #006C4C;
        background-color: #FFFFFF;
        box-shadow: none;
    }

    /* 6. BUTTONS */
    .stButton button {
        background-color: #C4EED0;
        color: #072113;
        border-radius: 20px;
        border: none;
        font-weight: 500;
        padding: 0.5rem 1rem;
        font-family: 'Google Sans', 'Outfit', sans-serif;
    }
    .stButton button:hover {
        background-color: #B0DCC0;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- BRAIN FUNCTIONS ---
def get_files_from_folder(branch_name):
    folder_path = os.path.join("materials", branch_name)
    if not os.path.exists(folder_path):
        return []
    
    file_contents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "rb") as f:
                file_contents.append({
                    "mime_type": "application/pdf",
                    "data": f.read()
                })
    return file_contents

@st.cache_resource(show_spinner=False)
def initialize_ai(branch_name):
    files = get_files_from_folder(branch_name)
    if not files:
        return None
    
    # HARDCODED: The working model from your screenshots
    model = genai.GenerativeModel("gemini-flash-latest")
    
    return model.start_chat(history=[
        {
            "role": "user",
            "parts": ["You are an expert academic peer mentor for MACE (Mar Athanasius College of Engineering). "
                      f"Here are the official study materials for {branch_name}. "
                      "Answer strictly based on these documents. Keep answers clean, structured, and student-friendly.", 
                      *files]
        },
        {
            "role": "model",
            "parts": [f"Hello! I am MACE Connect. I have loaded the {branch_name} database."]
        }
    ])

# --- SIDEBAR ---
with st.sidebar:
    # Removed Image, Added Bold Text
    st.markdown("""
    <div style='margin-bottom: 20px; padding-top: 10px;'>
        <h1 style='color: #006C4C; margin:0; padding:0; font-family: "Google Sans", "Outfit", sans-serif; font-size: 28px;'>MACE Connect</h1>
        <p style='color: #414942; font-size: 14px; margin:0;'> </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("DEPARTMENT")
    selected_branch = st.selectbox(
        "Select Department",
        ["CSE", "ECE", "EEE", "ME", "CE", "DS", "AIML"],
        label_visibility="collapsed"
    )
    
    st.write("") 
    
    if st.button("Clear History"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown(f"<div style='color: #414942; font-size: 12px;'>Status: 🟢 <b>{selected_branch}</b> </div>", unsafe_allow_html=True)

# --- MAIN APP ---
st.markdown(f"""
<div style='background-color: white; padding: 20px; border-radius: 16px; margin-bottom: 25px; box-shadow: 0px 1px 2px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 15px;'>
    <div style='background-color: #C4EED0; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px;'>🎓</div>
    <div>
        <h3 style='margin:0; color: #1A1C19;'>{selected_branch} </h3>
        <p style='margin:0; font-size: 14px; color: #414942;'>Based on mace.ac.in </p>
    </div>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_branch" not in st.session_state:
    st.session_state.current_branch = selected_branch

if st.session_state.current_branch != selected_branch:
    st.session_state.messages = []
    st.session_state.current_branch = selected_branch
    st.cache_resource.clear()

try:
    with st.spinner(f"Syncing {selected_branch} Data..."):
        chat_session = initialize_ai(selected_branch)
        
    if chat_session is None:
        st.error(f"⚠️ No files found for {selected_branch}. Please add PDFs to the folder.")
        st.stop()
        
except Exception as e:
    st.error(f"Connection Error: {e}")
    st.stop()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(f"Ask about {selected_branch} syllabus, exams..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if chat_session:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                response = chat_session.send_message(prompt)
                message_placeholder.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                message_placeholder.error("I hit a snag. Please ask again.")
                message_placeholder.error("I hit a snag. Please ask again.")
