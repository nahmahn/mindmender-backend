from fastapi import FastAPI, HTTPException, Form
import json
import os
from langchain_together import Together
from langchain_community.llms import Cohere
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set API Keys
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "1e7a5e10482ad3bce271180e403c1b4e9a785a00ec66c9821621d036d354ae72")
COHERE_API_KEY = "sWmE1lyhhw4XomK8LVSW58LlX0fe4ke89B1fxFvz"

# In-memory storage for serverless environment
memory_storage = []
user_profiles_storage = {}

# Load mental health dataset
@app.on_event("startup")
async def startup_event():
    global dataset
    try:
        with open("MentalHealthChatbotDataset.json", "r") as file:
            dataset = json.load(file)
    except:
        # Fallback if file can't be loaded
        dataset = {}

# AI Models
models = {
    "Mistral AI": Together(model="mistralai/Mistral-7B-Instruct-v0.3", together_api_key=TOGETHER_API_KEY),
    "LLaMA 3.3 Turbo": Together(model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", together_api_key=TOGETHER_API_KEY),
    "DeepSeek R1": Together(model="deepseek-ai/deepseek-r1-distill-llama-70b-free", together_api_key=TOGETHER_API_KEY),
    "Cohere Command": Cohere(model="command-xlarge", cohere_api_key=COHERE_API_KEY)
}

@app.get("/chat_memory")
def get_chat_memory(user_id: str = "default"):
    # Return empty array if no memory exists for this user
    return {"memory": memory_storage}

@app.post("/save_chat_memory")
async def update_chat_memory(user_id: str = Form(...), memory: str = Form(...)):
    # Parse memory from form data
    try:
        memory_data = json.loads(memory)
        global memory_storage
        memory_storage = memory_data
        return {"message": "Chat memory updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid memory format: {str(e)}")

@app.get("/user_profile")
def get_user_profile(user_id: str = "default"):
    if user_id not in user_profiles_storage:
        user_profiles_storage[user_id] = {"concerns": [], "coping_strategies": []}
    return user_profiles_storage[user_id]

@app.post("/save_user_profile")
async def update_user_profile(profile: dict):
    user_id = profile.get("user_id", "default")
    user_profiles_storage[user_id] = profile
    return {"message": "User profile updated successfully."}

@app.post("/chat")
async def chat(user_id: str, user_query: str):
    if user_id not in user_profiles_storage:
        user_profiles_storage[user_id] = {"concerns": [], "coping_strategies": []}
    user_profile = user_profiles_storage[user_id]

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
    
    # Only use dataset if it was loaded successfully
    for keyword, advice in dataset.items() if 'dataset' in globals() else {}:
        if keyword in user_query.lower():
            user_query += f"\n[Additional Context: {advice}]"

    history = "\n".join([
        f"User: {m['text']}" if m["role"] == "user" else f"AI: {m['text']}"
        for m in memory_storage[-5:] if memory_storage
    ])

    user_context = f"User concerns: {', '.join(user_profile.get('concerns', []))}\n"
    user_context += f"Past coping strategies: {', '.join(user_profile.get('coping_strategies', []))}\n"

    modified_query = f"{user_context}\n{history}\nUser: {user_query}\nAI:"

    try:
        response = selected_model.invoke(modified_query, max_tokens=1024).strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    global memory_storage
    if not isinstance(memory_storage, list):
        memory_storage = []
    
    memory_storage.append({"role": "user", "text": user_query})
    memory_storage.append({"role": "ai", "text": response})
    
    # No need to save to file in serverless environment
    
    return {"user_query": user_query, "response": response}
