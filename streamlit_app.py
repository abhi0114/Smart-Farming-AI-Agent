"""
Smart Farming AI Agent — Streamlit UI
IBM Granite + RAG | AICTE Problem Statement #9
Run: streamlit run streamlit_app.py
"""

import asyncio
import sys
import os

# ── ensure project root is on path ──────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

# ── page config (must be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="🌾 Smart Farming AI Agent",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── lazy imports (avoid crashing if optional deps missing) ───────────────────
@st.cache_resource(show_spinner="Loading AI models…")
def load_agent():
    from app.rag.engine import rag_engine
    from app.agents.farming_agent import farming_agent
    rag_engine.initialize()
    return farming_agent

@st.cache_resource(show_spinner=False)
def load_services():
    from app.services.weather import weather_service
    from app.services.market import market_service
    from app.services.translator import LANGUAGE_NAMES
    return weather_service, market_service, LANGUAGE_NAMES

# ── helper: run async in sync context ────────────────────────────────────────
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Global */
[data-testid="stAppViewContainer"] {background:#f4f7f0}
[data-testid="stSidebar"] {background:#1a5c2e !important}
[data-testid="stSidebar"] * {color:#fff !important}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] select,
[data-testid="stSidebar"] textarea {background:#154d27 !important; color:#fff !important; border:1px solid #2e7d32 !important}

/* Header */
.farm-header {
  background: linear-gradient(135deg,#1a5c2e,#2e7d32);
  color:#fff; padding:18px 24px; border-radius:12px;
  margin-bottom:18px; display:flex; align-items:center; gap:14px;
}
.farm-header h1 {font-size:1.5rem; font-weight:800; margin:0}
.farm-header p  {font-size:.83rem; opacity:.85; margin:0}
.ibm-badge {background:#0f62fe; color:#fff; border-radius:20px;
  font-size:.68rem; font-weight:700; padding:2px 10px; display:inline-block; margin-right:6px}
.rag-badge {background:#d97706; color:#fff; border-radius:20px;
  font-size:.68rem; font-weight:700; padding:2px 10px; display:inline-block}

/* Chat messages */
.chat-user {
  background:#1a5c2e; color:#fff; border-radius:14px 14px 3px 14px;
  padding:12px 16px; margin:6px 0; max-width:80%; margin-left:auto;
  font-size:.9rem;
}
.chat-bot {
  background:#fff; border:1px solid #d1d5db; border-radius:14px 14px 14px 3px;
  padding:12px 16px; margin:6px 0; max-width:85%;
  font-size:.9rem; line-height:1.6;
}
.chat-meta {font-size:.72rem; color:#6b7280; margin-top:4px}
.intent-chip {
  display:inline-block; font-size:.67rem; font-weight:700;
  padding:1px 8px; border-radius:20px; margin-right:6px; text-transform:uppercase;
}
.ic-weather    {background:#dbeafe;color:#1e40af}
.ic-market     {background:#fef3c7;color:#92400e}
.ic-pest       {background:#fee2e2;color:#b91c1c}
.ic-crop       {background:#e8f5e9;color:#1a5c2e}
.ic-soil       {background:#fef9c3;color:#713f12}
.ic-irrigation {background:#e0f2fe;color:#0369a1}
.ic-general    {background:#f3f4f6;color:#374151}

/* Weather / market cards */
.info-card {
  background:#fff; border:1px solid #e5e7eb; border-radius:10px;
  padding:12px 16px; margin-top:10px; font-size:.83rem;
}
.info-card h4 {font-size:.78rem; font-weight:700; color:#1a5c2e;
  text-transform:uppercase; letter-spacing:.5px; margin-bottom:8px}
.info-row {display:flex; justify-content:space-between; padding:3px 0;
  border-bottom:1px solid #f0f0f0; font-size:.8rem}
.info-row:last-child {border-bottom:none}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="farm-header">
  <div style="font-size:2.5rem">🌾</div>
  <div>
    <h1>Smart Farming AI Agent</h1>
    <p>
      <span class="ibm-badge">IBM Granite</span>
      <span class="rag-badge">RAG</span>
      &nbsp; Real-time farming advice in your language
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Load resources ────────────────────────────────────────────────────────────
farming_agent = load_agent()
weather_service, market_service, LANGUAGE_NAMES = load_services()

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "weather_data" not in st.session_state:
    st.session_state.weather_data = None
if "market_data" not in st.session_state:
    st.session_state.market_data = None

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🗺 Your Farm Context")

    location = st.text_input("📍 Location / Village", placeholder="e.g. Pune, Nagpur, Nashik")
    crop     = st.text_input("🌱 Crop (optional)", placeholder="e.g. Tomato, Wheat, Cotton")
    language = st.selectbox("🌐 Language", ["Auto-detect","en","hi","mr","pa","te","ta","kn","gu","bn"],
                            format_func=lambda x: "Auto-detect" if x=="Auto-detect" else LANGUAGE_NAMES.get(x, x))
    lang_val = None if language == "Auto-detect" else language

    st.markdown("---")
    st.markdown("## ⚡ Quick Questions")

    quick_questions = [
        ("🌱", "Best crop this season?",            "What crop is best for this season?"),
        ("💰", "Mandi rates today",                  "What is today's mandi rate for tomatoes?"),
        ("🐛", "Pest control for paddy",             "How do I control pests in my paddy field?"),
        ("🌿", "Fertilizer for wheat",               "What fertilizer should I use for wheat?"),
        ("💧", "Water for cotton",                   "How much water does cotton need?"),
        ("🏛", "Govt schemes",                       "What government schemes are available for farmers?"),
        ("🌤", "मौसम जानकारी",                       "मेरी फसल के लिए आज का मौसम कैसा है?"),
        ("🌾", "पीक शिफारस (Marathi)",               "माझ्या शेतासाठी कोणते पीक योग्य आहे?"),
    ]

    for icon, label, query in quick_questions:
        if st.button(f"{icon} {label}", use_container_width=True):
            st.session_state["quick_query"] = query

    st.markdown("---")

    # Weather widget
    if st.session_state.weather_data:
        w = st.session_state.weather_data
        st.markdown("## 🌤 Weather Update")
        st.markdown(f"""
        <div class="info-card">
          <h4>🌤 Weather Update</h4>
          <div class="info-row"><span>📍 Location</span><span>{w.get('location','')}, {w.get('country','')}</span></div>
          <div class="info-row"><span>🌡 Temperature</span><span>{w.get('temp','N/A')}°C</span></div>
          <div class="info-row"><span>💧 Humidity</span><span>{w.get('humidity','N/A')}%</span></div>
          <div class="info-row"><span>☁ Condition</span><span>{w.get('description','N/A')}</span></div>
          <div class="info-row"><span>🌧 Rainfall</span><span>{w.get('rainfall',0)} mm</span></div>
        </div>
        """, unsafe_allow_html=True)

    # Market widget
    if st.session_state.market_data:
        m = st.session_state.market_data
        prices = {k: v for k, v in m.items() if k not in ("timestamp","_note") and isinstance(v, dict)}
        if prices:
            st.markdown("## 📊 Mandi Prices")
            for crop_name, info in list(prices.items())[:8]:
                st.markdown(f"**{crop_name}** — ₹{info.get('modal','N/A')}/qtl")

    st.markdown("---")
    st.markdown("<small style='opacity:.6'>Smart Farming AI Agent<br/>AICTE Problem Statement #9</small>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# MAIN CHAT AREA
# ══════════════════════════════════════════════════════════════
col_chat, col_info = st.columns([2, 1])

with col_chat:
    # Welcome message
    if not st.session_state.messages:
        st.markdown("""
        <div class="chat-bot">
          <b>Namaste! 🙏</b><br/>
          I am your <b>Smart Farming AI Assistant</b>, powered by <b>IBM Granite</b>.<br/><br/>
          Ask me about:<br/>
          🌱 Crop recommendations &nbsp;|&nbsp; 🌤 Weather advice<br/>
          💰 Mandi prices &nbsp;|&nbsp; 🐛 Pest control<br/>
          🌿 Fertilizers &nbsp;|&nbsp; 💧 Irrigation<br/><br/>
          <i>Ask in Hindi, Marathi, Punjabi, Telugu, Tamil or English!</i>
        </div>
        """, unsafe_allow_html=True)

    # Render chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">👨‍🌾 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            intent = msg.get("intent", "general")
            lang   = msg.get("lang", "en")
            srcs   = msg.get("sources", [])
            src_txt = f" | 📚 {', '.join(srcs[:3])}" if srcs else ""
            lang_txt = f" | 🌐 {LANGUAGE_NAMES.get(lang, lang)}" if lang != "en" else ""
            st.markdown(f"""
            <div class="chat-bot">
              🤖 {msg["content"]}
              <div class="chat-meta">
                <span class="intent-chip ic-{intent}">{intent}</span>
                IBM Granite{lang_txt}{src_txt}
              </div>
            </div>
            """, unsafe_allow_html=True)

    # Handle quick question injection
    prefill = st.session_state.pop("quick_query", "")

    # Input box
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Your question",
            value=prefill,
            placeholder="Ask your farming question in any language…",
            height=80,
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("➤ Send", use_container_width=True)

    # Process submission
    if submitted and user_input.strip():
        query = user_input.strip()
        st.session_state.messages.append({"role": "user", "content": query})

        with st.spinner("🌾 IBM Granite is thinking…"):
            try:
                from app.agents.farming_agent import AgentRequest
                req = AgentRequest(
                    query=query,
                    location=location or None,
                    language=lang_val,
                    crop=crop or None,
                )
                response = run_async(farming_agent.run(req))

                # Store weather/market for sidebar
                if response.weather_data:
                    st.session_state.weather_data = response.weather_data
                if response.market_data:
                    st.session_state.market_data = response.market_data

                st.session_state.messages.append({
                    "role":    "assistant",
                    "content": response.answer,
                    "intent":  response.intent,
                    "lang":    response.detected_language,
                    "sources": response.sources,
                })
            except Exception as e:
                st.session_state.messages.append({
                    "role":    "assistant",
                    "content": f"⚠️ Error: {e}",
                    "intent":  "general",
                    "lang":    "en",
                    "sources": [],
                })

        st.rerun()

# ── Right info column ─────────────────────────────────────────
with col_info:
    st.markdown("### 📅 Crop Calendar")
    st.markdown("""
    | Season | Months | Key Crops |
    |---|---|---|
    | **Kharif** | Jun–Nov | Paddy, Cotton, Soybean |
    | **Rabi** | Oct–Mar | Wheat, Mustard, Potato |
    | **Zaid** | Mar–Jun | Watermelon, Moong |
    """)

    st.markdown("### 🏛 Key Schemes")
    schemes = [
        ("PM-KISAN", "₹6,000/year direct income"),
        ("PMFBY", "Crop insurance @ 2% premium"),
        ("KCC", "Crop loan @ 4% interest"),
        ("e-NAM", "Online market price discovery"),
        ("PM-KUSUM", "Solar pump subsidy 60–90%"),
    ]
    for name, desc in schemes:
        st.markdown(f"**{name}** — {desc}")

    st.markdown("### 💊 MSP 2024–25")
    msp = {"Paddy": "₹2,300", "Wheat": "₹2,275", "Cotton": "₹7,121",
           "Soybean": "₹4,892", "Maize": "₹2,225", "Groundnut": "₹6,783"}
    for crop_n, price in msp.items():
        st.markdown(f"**{crop_n}** — {price}/qtl")
