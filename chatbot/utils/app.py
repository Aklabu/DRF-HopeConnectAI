import streamlit as st
import pandas as pd
from prompt import OpenAIConfig
from file_uploder import file_uploder
from dotenv import load_dotenv
import os
from pipeline import HopePipeline
 
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("API key not found. Please set the OPENAI_API_KEY environment variable.")
openai_config = OpenAIConfig(api_key=api_key)
pipeline = HopePipeline(api_key=api_key)
 
def handle_file_upload():
    st.sidebar.title("Upload a File")
    uploaded_file = st.sidebar.file_uploader("Choose a file (CSV only)", type=["csv"])
 
    # Location selector
    st.sidebar.markdown("### Select Your Location")
    locations = [
        "11111 W Flamingo Rd, Las Vegas, NV 89135",
        "525 E Bonanza Rd, Las Vegas, NV 89101",
        "2000 S Maryland Pkwy, Las Vegas, NV 89104",
        "Custom location"
    ]
    selected_location = st.sidebar.selectbox("Choose a location", locations)
 
    if selected_location == "Custom location":
        custom_location = st.sidebar.text_input("Enter your location")
        if custom_location:
            st.session_state['user_location'] = custom_location
    else:
        st.session_state['user_location'] = selected_location
 
    # CSV upload
    if uploaded_file:
        st.sidebar.success(f"Uploaded: {uploaded_file.name}")
        df = pd.read_csv(uploaded_file)
        df_clean = file_uploder.preprocess_csv(df)
        st.session_state['csv_data'] = df_clean
 
 
def talk_with_AI():
    st.title("Hope AI 🤖")
    st.write("Feel free to ask anything about your need!")
 
    if 'messages' not in st.session_state:
        st.session_state.messages = []
 
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
 
    user_input = st.chat_input("Ask about your need...", key="input")
 
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
 
        location = st.session_state.get('user_location', '')
        csv_data = st.session_state.get('csv_data', None)
        history = st.session_state.messages
 
        response = pipeline.run(user_input, location, csv_data, history)
 
        with st.chat_message("assistant"):
            st.markdown(response)
 
 
 
def main():
    st.set_page_config(page_title="Hope AI", page_icon="🤖")
    handle_file_upload()
    talk_with_AI()
 
main()