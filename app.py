import streamlit as st
import requests
import uuid

# ================= CONFIGURATION =================
# Your deployed API URL
API_URL = "https://chatbotmaram.onrender.com/query"

st.set_page_config(
    page_title="Recruiter Assistant - Maram's Profile",
    page_icon="👩‍💻",
    layout="wide"
)

# ================= SESSION MANAGEMENT =================
# Create a unique ID for the chat session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Message history for display
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am the virtual assistant specialized in Maram's profile. I can answer questions about her projects, skills, and background. How can I help you today?"}
    ]

# ================= SIDEBAR =================
with st.sidebar:
    st.title("👩‍💻 Recruiter Portal")
    st.markdown("---")
    st.caption("This assistant uses a RAG (Retrieval-Augmented Generation) system to analyze Maram's CV, portfolio, and academic documents.")
    
    # Option to set research depth
    max_iter = st.slider("Reasoning Depth", 1, 5, 3, help="Higher values allow the AI to search longer and deeper.")
    
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
    
    st.markdown("---")
    
    # API Status Indicator
    try:
        # Check root to see if server responds
        health = requests.get("https://chatbotmaram.onrender.com/", timeout=2)
        if health.status_code == 200:
            st.success("🟢 API Connected")
        else:
            st.warning("🟠 API Unstable")
    except:
        st.error("🔴 API Unreachable")

    # Disclaimer in Sidebar (Optional position, also in main area)
    st.markdown("---")
    st.markdown("**Contact:**")
    st.markdown("📧 [maram.elouni@supcom.tn](mailto:maram.elouni@supcom.tn)")
    st.markdown("🔗 [LinkedIn Profile](https://www.linkedin.com/)") # Remplacez par le vrai lien si vous l'avez

# ================= API CALL FUNCTION =================
def query_api(question):
    payload = {
        "question": question,
        "max_iterations": max_iter,
        "session_id": st.session_state.session_id
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "answer": f"⚠️ Server Error ({response.status_code}). Please try again.",
                "sources": None
            }
    except requests.exceptions.ConnectionError:
        return {
            "answer": "⚠️ Unable to contact the server. Please check your internet connection.",
            "sources": None
        }
    except Exception as e:
        return {
            "answer": f"⚠️ An unexpected error occurred: {e}",
            "sources": None
        }

# ================= CHAT INTERFACE =================
st.title("💬 Chat with Maram's Profile")

# --- DISCLAIMER / AVERTISSEMENT ---
st.info(
    "⚠️ **Disclaimer:** Like any generative AI, this chatbot may not provide 100% correct answers. "
    "Please verify critical information directly with **Maram El Ouni** via email at "
    "[maram.elouni@supcom.tn](mailto:maram.elouni@supcom.tn) or on LinkedIn.",
    icon="ℹ️"
)

# 1. Display message history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If message has sources, display them in an expander
        if "sources" in message and message["sources"] and message["sources"] != "None":
            with st.expander("📚 Sources & Details"):
                st.markdown(message["sources"])
                if "score" in message:
                    st.caption(f"Relevance Score: {message['score']}/100 | Confidence: {message.get('confidence', 'N/A')}")

# 2. User Input Area
if prompt := st.chat_input("Ask a question (e.g., What are Maram's technical projects?)"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("🧠 Analyzing documents..."):
            # Call your Render API
            api_data = query_api(prompt)
            
            answer = api_data.get("answer", "No answer provided.")
            sources = api_data.get("sources", None)
            score = api_data.get("score", None)
            confidence = api_data.get("confidence", None)

            # Display answer
            st.markdown(answer)
            
            # Display sources if available
            if sources and sources != "None":
                with st.expander("📚 View Sources Used"):
                    st.markdown(sources)
                    if score:
                        st.caption(f"Score: {score}/100 | Confidence: {confidence}")

    # Save assistant response to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "score": score,
        "confidence": confidence
    })
