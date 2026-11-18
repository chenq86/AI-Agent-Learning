import streamlit as st
from agent.react_agent import ReactAgent
import time

#标题
st.title("ZhisaoTong Robot Customer Support")
st.divider()

if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "message" not in st.session_state:
    st.session_state["message"] = []

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])



#User input prompt
prompt = st.chat_input()

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role":"user", "content": prompt})

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Customer support assistant is thinking..."):
            response = st.write_stream(
                st.session_state["agent"].execute_stream(prompt)
            )

    # Save complete assistant response
    st.session_state["message"].append({
        "role": "assistant",
        "content": response
    })