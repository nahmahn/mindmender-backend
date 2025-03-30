import streamlit as st
import json
import time
import os
from langchain_together import Together
from langchain_community.llms import Cohere
import datetime

# Set API Keys
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "1e7a5e10482ad3bce271180e403c1b4e9a785a00ec66c9821621d036d354ae72")
COHERE_API_KEY = "sWmE1lyhhw4XomK8LVSW58LlX0fe4ke89B1fxFvz"  # Replace with your actual Cohere API key
st.cache_data.clear()

# Memory file for storing past conversations
MEMORY_FILE = "chat_memory.json"
USER_PROFILE_FILE = "user_profiles.json"

# Load dataset function
@st.cache_data
def load_mental_health_data():
    with open("MentalHealthChatbotDataset.json", "r") as file:
        return json.load(file)

# Load chat memory from JSON
def load_chat_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)
    return []

# Save chat memory to JSON
def save_chat_memory(memory):
    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)

# Load user profile
def load_user_profile():
    if os.path.exists(USER_PROFILE_FILE):
        with open(USER_PROFILE_FILE, "r") as file:
            return json.load(file)
    return {}

# Save user profile
def save_user_profile(profile):
    with open(USER_PROFILE_FILE, "w") as file:
        json.dump(profile, file, indent=4)

# AI Models
models = {
    "Mistral AI": Together(model="mistralai/Mistral-7B-Instruct-v0.3", together_api_key=TOGETHER_API_KEY),
    "LLaMA 3.3 Turbo": Together(model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", together_api_key=TOGETHER_API_KEY),
    "DeepSeek R1": Together(model="deepseek-ai/deepseek-r1-distill-llama-70b-free", together_api_key=TOGETHER_API_KEY),
    "Cohere Command": Cohere(model="command-xlarge", cohere_api_key=COHERE_API_KEY)
}

# Function to get AI response (with Memory & Personalization)
def get_response(user_query, dataset, memory, user_profile):
    crisis_keywords = ["suicide", "end my life", "self-harm", "hopeless", "kill myself"]
    deep_emotion_keywords = ["anxious", "overwhelmed", "panic attack", "lonely", "heartbroken"]
    casual_keywords = ["motivate me", "how to be happy", "mental health tips", "relaxation"]

    selected_model = models["Mistral AI"]  # Default model

    if any(word in user_query.lower() for word in crisis_keywords):
        selected_model = models["Cohere Command"]
        hotline_message = (
            "**🚨 URGENT:** If you are in crisis, please seek help immediately. "
            "In **India**, you can contact Vandrevala Foundation Helpline at **1860 266 2345** "
            "or Snehi at **+91-9582208181**. You are **not alone**. 💚"
        )
        return hotline_message  

    elif any(word in user_query.lower() for word in deep_emotion_keywords):
        selected_model = models["DeepSeek R1"]

    elif any(word in user_query.lower() for word in casual_keywords):
        selected_model = models["LLaMA 3.3 Turbo"]

    for keyword, advice in dataset.items():
        if keyword in user_query.lower():
            user_query += f"\n[Additional Context: {advice}]"

    # Incorporate memory & user profile into the prompt
    history = "\n".join([
        f"User: {m['text']}" if m["role"] == "user" else f"AI: {m['text']}"
        for m in memory[-5:]  # Only include the last 5 messages
    ])

    user_context = f"User concerns: {', '.join(user_profile['concerns'])}\n"
    user_context += f"Past coping strategies: {', '.join(user_profile['coping_strategies'])}\n"

    modified_query = f"{user_context}\n{history}\nUser: {user_query}\nAI:"

    try:    
        response = selected_model.invoke(modified_query, max_tokens=1024)
        response_cleaned = response.split("How to Respond:")[0].strip()  # Remove instructions
        return response_cleaned

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# Streamlit UI Configuration
st.set_page_config(page_title="Mental Health Chatbot", layout="wide")
st.title("Mental Health Chatbot")

# Load chat memory & user profile
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_memory()
if "user_profile" not in st.session_state:
    st.session_state.user_profile = load_user_profile()

user_input = st.text_input("💬 Type your message here...")

dataset = load_mental_health_data()
if user_input:
    user_id = "default_user"
    if user_id not in st.session_state.user_profile:
        st.session_state.user_profile[user_id] = {"concerns": [], "coping_strategies": []}
    user_profile = st.session_state.user_profile[user_id]

    # Track user concerns
    if "stress" in user_input.lower() and "stress" not in user_profile["concerns"]:
        user_profile["concerns"].append("stress")
    if "anxiety" in user_input.lower() and "anxiety" not in user_profile["concerns"]:
        user_profile["concerns"].append("anxiety")

    # Get AI Response with personalization
    response = get_response(user_input, dataset, st.session_state.messages, user_profile)

    # Store coping strategies
    if "meditation" in response.lower() and "meditation" not in user_profile["coping_strategies"]:
        user_profile["coping_strategies"].append("meditation")
    if "breathing exercises" in response.lower() and "breathing exercises" not in user_profile["coping_strategies"]:
        user_profile["coping_strategies"].append("breathing exercises")

    # Update session memory
    st.session_state.messages.append({"role": "user", "text": user_input})
    st.session_state.messages.append({"role": "ai", "text": response})
    save_chat_memory(st.session_state.messages)
    save_user_profile(st.session_state.user_profile)

    # Display conversation
    st.markdown(f"**You:** {user_input}")  
    st.markdown(f"**AI:** {response}")

