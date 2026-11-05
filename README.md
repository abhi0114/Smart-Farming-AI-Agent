# 🌾 Smart Farming AI Agent
### *AI-Powered Agricultural Advisory — Powered by IBM Granite + RAG*

> **AICTE Problem Statement #9** — An AI Agent for Smart Farming Advice using IBM Cloud Lite services / IBM Granite (mandatory).

---

## 📋 Overview

A **Retrieval-Augmented Generation (RAG)** AI agent that delivers real-time, localized farming advice to small-scale Indian farmers. The system combines:

| Layer | Technology |
|---|---|
| **LLM** | IBM Granite (`ibm/granite-13b-instruct-v2`) via watsonx.ai |
| **RAG** | FAISS vector store + sentence-transformers embeddings |
| **Translation** | IBM Watson Language Translator + deep-translator fallback |
| **Weather** | OpenWeatherMap API |
| **Market Prices** | Agmarknet / data.gov.in API |
| **Backend** | FastAPI (Python) |
| **Frontend** | Vanilla HTML/CSS/JS — mobile-responsive |

---

## 🚀 Features

- 🌱 **Crop Recommendations** — Season-specific crop advice for Kharif, Rabi, Zaid
- 🌤 **Live Weather Integration** — Real-time weather from OpenWeatherMap
- 💰 **Mandi Price Tracking** — Live prices from Agmarknet (data.gov.in)
- 🐛 **Pest & Disease Control** — IPM-based pest management advice
- 🌿 **Soil & Fertilizer Guidance** — NPK recommendations, soil health
- 💧 **Irrigation Planning** — Drip, sprinkler, critical stage guidance
- 🏛 **Government Schemes** — PM-KISAN, PMFBY, KCC, e-NAM
- 🌐 **10 Indian Languages** — Hindi, Marathi, Punjabi, Telugu, Tamil, Kannada, Gujarati, Bengali, Odia, English

---

## 📁 Project Structure

```
AICTE- AI AGENT FOR FARMING/
│
├── .env                          # Environment variables (IBM credentials)
├── env.example                   # Template for .env
├── requirements.txt              # Python dependencies
├── run.py                        # Application entry point
│
├── app/
│   ├── main.py                   # FastAPI app + lifespan
│   ├── config.py                 # Pydantic settings from .env
│   ├── granite_llm.py            # IBM Granite / watsonx.ai integration
│   │
│   ├── rag/
│   │   └── engine.py             # RAG pipeline: ingest → embed → FAISS → retrieve
│   │
│   ├── agents/
│   │   └── farming_agent.py      # Main agent: detect → translate → RAG → Granite → translate
│   │
│   ├── services/
│   │   ├── translator.py         # IBM Watson Translator + Google fallback
│   │   ├── weather.py            # OpenWeatherMap integration
│   │   └── market.py             # Agmarknet mandi price integration
│   │
│   └── api/
│       └── routes.py             # All API endpoints
│
├── data/
│   ├── knowledge_base/           # JSON farming knowledge docs (RAG corpus)
│   │   ├── crops_and_soil.json
│   │   ├── pest_control.json
│   │   └── weather_and_market.json
│   └── vector_store/             # FAISS index (auto-generated on first run)
│
├── templates/
│   └── index.html                # Farmer UI (HTML)
│
└── static/
    ├── css/style.css             # Stylesheet
    └── js/app.js                 # Frontend JavaScript
```

---

## ⚙️ Setup Guide

### 1. Prerequisites

- Python 3.10+
- IBM Cloud account (free Lite tier): https://cloud.ibm.com/registration
- watsonx.ai project created in IBM Cloud

### 2. Clone & Install

```bash
# Install dependencies
pip install -r requirements.txt
```

### 3. Configure IBM Granite (Mandatory)

Edit the `.env` file:

```env
# IBM watsonx.ai — MANDATORY
WATSONX_API_KEY=your_ibm_cloud_api_key_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_PROJECT_ID=your_watsonx_project_id_here
GRANITE_MODEL_ID=ibm/granite-13b-instruct-v2
```

**How to get IBM credentials:**
1. Go to https://cloud.ibm.com → Create account (free Lite)
2. Navigate to **watsonx.ai** → Create a project
3. Go to **Project Settings** → Copy your **Project ID**
4. Go to **Manage** → **Access (IAM)** → **API Keys** → Create API Key

### 4. Optional API Keys

```env
# Free weather data
OPENWEATHER_API_KEY=your_key_from_openweathermap.org

# Live mandi prices
AGMARKNET_API_KEY=your_key_from_data.gov.in

# Multilingual support (IBM Watson)
WATSON_TRANSLATOR_API_KEY=your_watson_translator_key
```

> ⚡ **The app works without optional API keys** — it uses realistic demo/mock data for development.

### 5. Run the Application

```bash
python run.py
```

Open your browser at: **http://localhost:8000**

---

## 🌐 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/chat` | Main AI agent chat endpoint |
| `GET` | `/api/v1/weather/{location}` | Current weather |
| `GET` | `/api/v1/weather/{location}/forecast` | 5-day forecast |
| `GET` | `/api/v1/market/prices` | Mandi prices (optional crop filter) |
| `GET` | `/api/v1/crops/calendar` | Kharif/Rabi/Zaid crop calendar |
| `GET` | `/api/v1/languages` | Supported languages |
| `GET` | `/health` | Health check |

### Chat API Example

```json
POST /api/v1/chat
{
  "query": "टमाटर का आज का मंडी भाव क्या है?",
  "location": "Pune",
  "language": "hi",
  "crop": "Tomato"
}
```

**Response:**
```json
{
  "answer": "आज पुणे मंडी में टमाटर का भाव ₹1,200/क्विंटल है...",
  "detected_language": "hi",
  "language_name": "हिंदी (Hindi)",
  "intent": "market",
  "sources": ["market_selling_strategies"],
  "weather_data": { ... },
  "market_data": { "Tomato": { "modal": 1200 } }
}
```

---

## 🤖 How It Works (RAG Pipeline)

```
Farmer Question (any language)
        │
        ▼
[Language Detection] ──► IBM Watson Translator / langdetect
        │
        ▼
[English Query]
        │
        ├──► [Intent Classifier] → weather / market / pest / crop / soil
        │
        ├──► [Live Data Fetch] → OpenWeatherMap + Agmarknet API
        │
        ├──► [RAG Retrieval] → FAISS vector search over farming knowledge base
        │            └─ Top-5 relevant document chunks
        │
        ▼
[IBM Granite Prompt] = System prompt + RAG context + live data + query
        │
        ▼
[IBM Granite LLM] → watsonx.ai inference
        │
        ▼
[Translate Answer] ──► back to farmer's language
        │
        ▼
[Farmer receives actionable advice]
```

---

## 📊 Supported Crops

| Season | Crops |
|---|---|
| **Kharif** (Jun–Nov) | Paddy, Cotton, Soybean, Maize, Bajra, Groundnut, Sugarcane, Turmeric |
| **Rabi** (Oct–Mar) | Wheat, Mustard, Chickpea, Potato, Onion, Garlic, Tomato |
| **Zaid** (Mar–Jun) | Watermelon, Cucumber, Moong, Pumpkin |

---

## 🌐 Supported Languages

Hindi (हिंदी) · Marathi (मराठी) · Punjabi (ਪੰਜਾਬੀ) · Telugu (తెలుగు) · Tamil (தமிழ்) · Kannada (ಕನ್ನಡ) · Gujarati (ગુજરાતી) · Bengali (বাংলা) · Odia (ଓଡ଼ିଆ) · English

---

## 🏗 Technology Stack

- **IBM Granite** (`ibm/granite-13b-instruct-v2`) — Core LLM reasoning
- **IBM watsonx.ai** — IBM Cloud Lite compatible inference platform
- **IBM Watson Language Translator** — Primary multilingual support
- **FAISS** — Facebook AI Similarity Search for vector retrieval
- **sentence-transformers** — Local embedding model (no API cost)
- **FastAPI** — High-performance async Python web framework
- **LangChain** — RAG orchestration framework

---

## 📜 License

MIT License — AICTE Academic Project

---

*Made with ❤️ for India's 120 million small-scale farmers*
