import streamlit as st
from utils.api import ask_question
from config import API_URL

def render_chat():
    st.subheader("💬 Chat with your assistant")

    # # show which backend the client is calling (debug)
    st.info(f"Using API_URL: {API_URL}")

    if "message" not in st.session_state:
        st.session_state.messages = []

    # render existing chat history
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).markdown(msg["content"])
    
    # input and response
    user_input = st.chat_input("Type your question")
    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role":"user", "content":user_input})

        response = ask_question(user_input)
        if response.status_code == 200:
            data = response.json()
            answer = data["response"]
            sources = data.get("sources", [])
            st.chat_message("assistant").markdown(answer)
            # if sources:
            #     st.markdown("📄 **Source : **")
            #     for src in sources:
            #         st.markdown(f"- {src}")
            st.session_state.messages.append({"role":"assistant", "content":answer})
        else:
            st.error(f"Error : {response.text}")
            # try:
            #     st.info(f"Status code: {response.status_code}")
            #     st.text(response.text)
            # except Exception:
            #     pass