🧠 SentiHack - Mental Health Support Chatbot

SentiHack is a sophisticated mental health support chatbot designed to provide empathetic, intelligent, and context-aware conversations. It combines state-of-the-art emotion detection, crisis monitoring, and advanced conversational AI to support users experiencing emotional distress.

---

## 🚀 Overview

SentiHack uses multiple AI models to:

- Understand and respond empathetically to user inputs
- Detect 28 distinct emotions
- Identify crisis situations in real-time
- Maintain contextual, memory-based conversations

---

## ✨ Key Features

### 🤖 AI Models
- **Mental Health Chatbot**  
  Uses [`tanusrich/Mental_Health_Chatbot`](https://huggingface.co/tanusrich/Mental_Health_Chatbot) for empathetic dialogue generation

- **Emotion Detection**  
  Implements [`joeddav/distilbert-base-uncased-go-emotions-student`](https://huggingface.co/joeddav/distilbert-base-uncased-go-emotions-student) to classify 28 emotions

- **Crisis Detection**  
  Uses [`facebook/bart-large-mnli`](https://huggingface.co/facebook/bart-large-mnli) for multi-label crisis identification

### 🎯 Core Capabilities
- **Emotion Recognition**: Identifies complex emotions like pride, gratitude, and more
- **Crisis Monitoring**: Real-time crisis detection and escalation support
- **Conversation Memory**: Redis-based chat history for contextual awareness
- **REST API**: Exposes a Flask-based API with CORS enabled for frontend integration

---

## 🧱 Technical Stack

### 🛠 Backend Components
- **Framework**: Flask + Flask-CORS
- **Database**: Redis for memory storage
- **AI/ML**: PyTorch, Hugging Face Transformers

### 📦 Python Dependencies
```bash
transformers
torch
redis
flask
flask-cors
````

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/sentihack.git
cd sentihack
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Redis Setup

* Install Redis: [https://redis.io/docs/getting-started/installation/](https://redis.io/docs/getting-started/installation/)
* Start Redis server (default port: 6379)

### 5. Launch the Application

```bash
python app.py
```

---

## 🧪 API Documentation

### `POST /chat`

#### Request:

```json
{
  "user_id": "user123",
  "message": "I feel really anxious lately..."
}
```

#### Response:

```json
{
  "response": "I'm really sorry you're feeling this way. Can you tell me more about what's been making you anxious?",
  "emotion": "anxiety",
  "crisis": false
}
```

---

## 🧪 Testing

Run the test script to simulate conversation:

```bash
python test.py
```

---

## 📁 Project Structure

```
.
├── app.py              # Flask API server
├── chatbot.py          # Chatbot logic and response generation
├── emotion.py          # Emotion detection module
├── crisis.py           # Crisis detection module
├── memory.py           # Redis memory handler
├── test.py             # Testing interface
├── requirements.txt    # Dependency list
└── README.md           # Project documentation
```

---

## 📜 License

\[Choose a License and update here, e.g., MIT License]

---

## 🤝 Contributing

Contributions are welcome!
Please open an issue or submit a pull request with improvements, fixes, or new features.

---

## ⚠️ Disclaimer

SentiHack is designed to provide **supportive and empathetic conversation**, but it is **not a substitute for professional mental health care**. If you or someone you know is in crisis, please contact a mental health professional or crisis helpline.

---

### 📫 Contact

For questions or suggestions, reach out via [GitHub Issues](https://github.com/your-username/sentihack/issues).

---

> Built with care to support mental well-being 💙

