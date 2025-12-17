import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time

# Import Agents
from agents.literature_agent import analyze_literature
from agents.patent_agent import analyze_patents
from agents.clinical_trial_agent import evaluate_clinical_trials
from agents.decision_agent import make_decision
from dotenv import load_dotenv
import os

load_dotenv()


# -----------------------------------------------------------------------------
# 1. Page Config & Styling
# -----------------------------------------------------------------------------
from streamlit_agraph import agraph, Node, Edge, Config

# -----------------------------------------------------------------------------
# 1. Page Config & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="BioForge AI | Drug Repurposing",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Hackathon" Aesthetics
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    h1, h2, h3 {
        color: #00e0ff !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stButton>button {
        color: white;
        background-color: #0078D7;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #00c3ff;
        color: black;
        transform: scale(1.02);
    }
    .metric-card {
        background-color: #1f252e;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #2d3748;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .agent-box {
        background-color: #262730;
        border-left: 5px solid #00e0ff;
        padding: 1em;
        margin-bottom: 1em;
        border-radius: 4px;
    }
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #0e1117;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Sidebar - Inputs
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# 2. Sidebar - Inputs
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3004/3004458.png", width=60)
    st.title("BioForge AI")
    st.markdown("### Agentic Drug Repurposing")
    st.divider()
    
    therapeutic_area = st.selectbox(
        "Target Therapeutic Area",
        ["Oncology - Solid Tumors", "Neurodegenerative Diseases", "Rare Genetic Disorders", "Cardiovascular", "Infectious Diseases"]
    )
    
    drug_name = st.text_input("Candidate Drug Name", value="Metformin")
    
    # API Key Input (Optional override)
    with st.expander("⚙️ Advanced Settings"):
        gemini_key = st.text_input("Gemini API Key (Optional)", type="password", help="Leave empty to use the system key from .env")

    
    st.markdown("---")
    st.info("💡 **Tip**: Try 'Metformin' for Oncology or 'Sildenafil' for Cardiovascular.")
    
    run_btn = st.button("🚀 IGNITE AGENT SWARM")

# Initialize Session State
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------------------------------------------------------------
# 3. Main Analysis Flow
# -----------------------------------------------------------------------------
if run_btn:
    # Reset state on new run
    st.session_state.chat_history = [] 
    
    st.markdown(f"## 🔍 Analyzing **{'Hidden Candidate' if not drug_name else drug_name}** for **{therapeutic_area}**")
    
    # Grid for real-time agent feedback
    col1, col2, col3 = st.columns(3)
    
    lit_box = col1.empty()
    pat_box = col2.empty()
    clin_box = col3.empty()
    
    # Stage 1: Literature
    with lit_box.container():
        st.markdown("<div class='agent-box'><h4>📚 Literature Agent</h4><p>Scanning PubMed via BioPython...</p></div>", unsafe_allow_html=True)
    lit_results = analyze_literature(drug_name, therapeutic_area)
    with lit_box.container():
        st.markdown(f"<div class='agent-box'><h4>✅ Literature Agent</h4><p>Found <b>{lit_results['data']['publication_count']}</b> papers.</p></div>", unsafe_allow_html=True)
    
    # Stage 2: Patent
    with pat_box.container():
        st.markdown("<div class='agent-box'><h4>⚖️ Patent Agent</h4><p>Checking legal risks...</p></div>", unsafe_allow_html=True)
    pat_results = analyze_patents(drug_name)
    risk_color = "#ff4b4b" if pat_results['data']['patent_risk'] == "High" else "#21c354"
    with pat_box.container():
        st.markdown(f"<div class='agent-box' style='border-left: 5px solid {risk_color};'><h4>✅ Patent Agent</h4><p>Risk: <b style='color:{risk_color}'>{pat_results['data']['patent_risk']}</b></p></div>", unsafe_allow_html=True)

    # Stage 3: Clinical
    with clin_box.container():
        st.markdown("<div class='agent-box'><h4>🏥 Clinical Agent</h4><p>Querying OpenFDA...</p></div>", unsafe_allow_html=True)
    clin_results = evaluate_clinical_trials(drug_name, therapeutic_area)
    with clin_box.container():
        st.markdown(f"<div class='agent-box'><h4>✅ Clinical Agent</h4><p>Safety Score: <b>{clin_results['data']['safety_profile_score']}/100</b></p></div>", unsafe_allow_html=True)

    # Decision (Pass API Key)
    decision = make_decision(lit_results['data'], pat_results['data'], clin_results['data'], api_key=gemini_key)
    
    # Store in Session State
    st.session_state.analysis_results = {
        "lit": lit_results,
        "pat": pat_results,
        "clin": clin_results,
        "decision": decision,
        "drug": drug_name,
        "area": therapeutic_area
    }
    st.session_state.analysis_complete = True
    st.rerun() # Rerun to refresh the layout for Tabs

# -----------------------------------------------------------------------------
# 4. Display Results (Tabs)
# -----------------------------------------------------------------------------
if st.session_state.analysis_complete:
    res = st.session_state.analysis_results
    
    st.markdown(f"## 🧬 Analysis Result: **{res['drug']}**")
    
    tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "🕸️ Knowledge Graph", "💬 Swarm Chat"])
    
    # --- TAB 1: DASHBOARD ---
    with tab1:
        c_left, c_right = st.columns([1, 1])
        
        with c_left:
            st.subheader("Feasibility Score")
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = res['decision']['final_confidence_score'],
                title = {'text': "Confidence"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#00e0ff"},
                    'steps': [{'range': [0, 50], 'color': "#3d405b"}, {'range': [50, 75], 'color': "#5e6472"}],
                    'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': res['decision']['final_confidence_score']}
                }
            ))
            fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # ROI Metric Card
            if res['decision']['recommendation'] == "GO":
                roi_val = "$850M" 
                roi_text = "Est. R&D Savings"
                roi_color = "#21c354"
            elif res['decision']['recommendation'] == "AMBER":
                roi_val = "$120M"
                roi_text = "Est. R&D Savings"
                roi_color = "#ffa421"
            else:
                roi_val = "$15M"
                roi_text = "Cost Avoidance"
                roi_color = "#ff4b4b"
                
            st.markdown(f"""
            <div class="metric-card" style="border-left: 5px solid {roi_color}; text-align: center;">
                <h2 style="color: white !important; margin:0;">{roi_val}</h2>
                <p style="color: #a0a0a0; margin:0;">{roi_text}</p>
            </div>
            """, unsafe_allow_html=True)

        with c_right:
            rec = res['decision']['recommendation']
            rec_color = "green" if rec == "GO" else "orange" if rec == "AMBER" else "red"
            
            st.markdown(f"""
            <div style="background-color: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; border: 1px solid {rec_color};">
                <h1 style="text-align: center; color: {rec_color}; margin: 0;">{rec}</h1>
                <p style="text-align: center; font-style: italic;">{res['decision']['summary']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### Strategic Rationale")
            for r in res['decision']['rationale']:
                st.write(f"- {r}")

    # --- TAB 2: KNOWLEDGE GRAPH ---
    with tab2:
        st.subheader("Interactive 3D Knowledge Network")
        
        # Build Graph
        nodes = []
        edges = []
        
        # Central Node
        nodes.append(Node(id="DRUG", label=res['drug'], size=25, color="#00e0ff"))
        nodes.append(Node(id="DISEASE", label=res['area'], size=20, color="#ff00e0"))
        
        edges.append(Edge(source="DRUG", target="DISEASE", label="Treats?"))
        
        # Literature Nodes
        nodes.append(Node(id="LIT", label=f"Papers ({res['lit']['data']['publication_count']})", size=15, color="#f1f1f1"))
        edges.append(Edge(source="DRUG", target="LIT", label="Mentions"))
        
        # Patent Node
        nodes.append(Node(id="PAT", label="Patent Risk", size=15, color="#ff4b4b" if res['pat']['data']['patent_risk'] =="High" else "#21c354"))
        edges.append(Edge(source="DRUG", target="PAT", label="Legal Status"))
        
        # Clinical Node
        nodes.append(Node(id="CLIN", label=f"Safety ({res['clin']['data']['safety_profile_score']})", size=15, color="#eca400"))
        edges.append(Edge(source="DRUG", target="CLIN", label="Profile"))
        
        config = Config(width=700, height=500, directed=True, nodeHighlightBehavior=True, highlightColor="#F7A7A6", collapsible=False)
        
        # Render Graph
        agraph(nodes=nodes, edges=edges, config=config)

    # --- TAB 3: SWARM CHAT ---
    with tab3:
        st.subheader("💬 Chat with BioForge Swarm")
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Ask about the analysis (e.g., 'Why is the risk high?')..."):
            st.chat_message("user").markdown(prompt)
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # --- GEMINI SMART CHAT ---
            # Use the hardcoded key from decision_agent or the input
            # Use the key from input or environment
            system_key = os.getenv("GEMINI_API_KEY")
            effective_key = gemini_key if gemini_key else system_key


            if effective_key:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=effective_key)
                    model = genai.GenerativeModel('gemini-1.5-flash-001')
                    
                    # specific context for the bot
                    context_prompt = f"""
                    You are the BioForge AI Swarm Orchestrator. You have just analyzed a drug.
                    
                    Analysis Context:
                    - Drug: {res['drug']}
                    - Target Disease: {res['area']}
                    - Decision: {res['decision']['recommendation']} (Confidence: {res['decision']['final_confidence_score']}%)
                    - Literature: Found {res['lit']['data']['publication_count']} papers. Insight: {res['lit']['data']['key_insights'][0]}
                    - Patent Risk: {res['pat']['data']['patent_risk']}. Context: {res['pat']['data']['analysis_context']}
                    - Clinical Safety: Score {res['clin']['data']['safety_profile_score']}/100. Note: {res['clin']['data'].get('source', 'Mock data')}
                    
                    User Question: "{prompt}"
                    
                    Answer concisely as the AI Orchestrator. Be professional but helpful.
                    """
                    
                    response_obj = model.generate_content(context_prompt)
                    response = response_obj.text
                    
                except Exception as e:
                    response = f"I am having trouble connecting to my cognitive brain (Gemini). Error: {e}"
            else:
                # Fallback to dumb logic if no key
                response = "I am running in offline mode. Please add a Gemini Key to chat intelligently."
            
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})

else:
    # Landing State
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h1>Welcome to BioForge AI</h1>
        <p style="font-size: 1.2em; color: #a0a0a0;">
            The world's first multi-agent autonomous framework for pharmaceutical drug repurposing.
            <br>Ignite the swarm to analyze millions of data points in seconds.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.info("🤖 **Autonomous Agents**\n\nIndependent modules analyzing literature, patents, and clinical history.")
    c2.warning("⚡ **Real-time Insights**\n\nSimulated high-performance generation of drug validity scores.")
    c3.success("🧬 **Cross-Domain Logic**\n\nSynthesizes biological plausibility with commercial viability.")
