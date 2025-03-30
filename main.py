from fastapi import FastAPI, HTTPException
import json
import os
from langchain_together import Together
from langchain_community.llms import Cohere
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],  # Allows all origins, change this to specific domains for security
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Set API Keys
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "1e7a5e10482ad3bce271180e403c1b4e9a785a00ec66c9821621d036d354ae72")
COHERE_API_KEY = "sWmE1lyhhw4XomK8LVSW58LlX0fe4ke89B1fxFvz"

# Memory files
MEMORY_FILE = "chat_memory.json"
USER_PROFILE_FILE = "user_profiles.json"
DATASET_FILE = "MentalHealthChatbotDataset.json"

# Load mental health dataset
def load_mental_health_data():
    with open(DATASET_FILE, "r") as file:
        return json.load(file)

dataset = load_mental_health_data()

# Load chat memory
def load_chat_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)
    return {'response' : "loda lele"}

# Save chat memory
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

@app.get("/chat_memory")
def get_chat_memory():
    return load_chat_memory()

@app.post("/save_chat_memory")
def update_chat_memory(memory: list):
    save_chat_memory(memory)
    return {"message": "Chat memory updated successfully."}

@app.get("/user_profile")
def get_user_profile():
    return load_user_profile()

@app.post("/save_user_profile")
def update_user_profile(profile: dict):
    save_user_profile(profile)
    return {"message": "User profile updated successfully."}

@app.post("/chat")
def chat(user_id: str, user_query: str):
    chat_memory = load_chat_memory()
    user_profiles = load_user_profile()

    if user_id not in user_profiles:
        user_profiles[user_id] = {"concerns": [], "coping_strategies": []}
    user_profile = user_profiles[user_id]

    crisis_keywords = ["suicide", "end my life", "self-harm", "hopeless", "kill myself"]
    deep_emotion_keywords = ["anxious", "overwhelmed", "panic attack", "lonely", "heartbroken"]
    casual_keywords = ["motivate me", "how to be happy", "mental health tips", "relaxation"]

    selected_model = models["Mistral AI"]

    if any(word in user_query.lower() for word in crisis_keywords):
        selected_model = models["Cohere Command"]
        return {"response": "🚨 URGENT: If you are in crisis, seek help immediately. India helpline: 1860 266 2345"}
    
    if any(word in user_query.lower() for word in deep_emotion_keywords):
        selected_model = models["DeepSeek R1"]
    elif any(word in user_query.lower() for word in casual_keywords):
        selected_model = models["LLaMA 3.3 Turbo"]
    
    for keyword, advice in dataset.items():
        if keyword in user_query.lower():
            user_query += f"\n[Additional Context: {advice}]"

    history = "\n".join([
        f"User: {m['text']}" if m["role"] == "user" else f"AI: {m['text']}"
        for m in chat_memory[-5:]
    ])

    user_context = f"User concerns: {', '.join(user_profile['concerns'])}\n"
    user_context += f"Past coping strategies: {', '.join(user_profile['coping_strategies'])}\n"

    modified_query = f"{user_context}\n{history}\nUser: {user_query}\nAI:"

    try:
        response = selected_model.invoke(modified_query, max_tokens=1024).strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    chat_memory.append({"role": "user", "text": user_query})
    chat_memory.append({"role": "ai", "text": response})
    save_chat_memory(chat_memory)
    save_user_profile(user_profiles)

    return {"user_query": user_query, "response": response}