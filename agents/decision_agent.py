import time
import google.generativeai as genai

def make_decision(literature_data, patent_data, clinical_data, api_key=None):
    """
    Aggregates insights from all agents to form a final recommendation.
    Uses LLM (Gemini) if available for a professional summary.
    """
    time.sleep(1.0)
    
    lit_score = literature_data['relevance_score'] * 100
    pat_risk = patent_data['patent_risk']
    clin_risk = clinical_data['clinical_risk_score']
    
    # Base confidence starts with literature signal
    confidence = lit_score
    
    # Penalize for Patent Risk
    if pat_risk == "High":
        confidence -= 50 # Severe penalty for EY demo ("Legal is a blocker")
    elif pat_risk == "Medium":
        confidence -= 20
        
    # Penalize for Clinical Risk
    if clin_risk > 50: # Risk score > 30 is bad
        confidence -= 30
    elif clin_risk > 20:
        confidence -= 10
        
    # Cap confidence
    confidence = max(0, min(100, confidence))
    
    if confidence > 80:
        recommendation = "GO"
        summary_fallback = "Strong candidate for repurposing. High literature support and manageable risks."
    elif confidence > 40:
        recommendation = "AMBER"
        summary_fallback = "Potential candidate. Requires further patent strategy or safety validation."
    else:
        recommendation = "NO-GO"
        summary_fallback = "Low feasibility. Significant patent or clinical barriers detected."

    final_summary = summary_fallback
    final_rationale = [
        f"Literature supports mechanism of action ({int(lit_score)}% relevance).",
        f"Patent risk assessed as {pat_risk}.",
        f"Clinical risk score is {clin_risk} (Lower is better)."
    ]

    # --- GEMINI INTEGRATION ---
    # Hackathon: Use hardcoded key if provided, else fall back to UI input
    # Hackathon: Use key from args, then environment
    import os
    system_key = os.getenv("GEMINI_API_KEY")
    effective_key = api_key if api_key else system_key


    if effective_key:
        try:
            genai.configure(api_key=effective_key)
            # Using the explicit versioned model name to avoid alias issues
            model = genai.GenerativeModel('gemini-1.5-flash-001')
            
            prompt = f"""
            Act as a Senior Pharmaceutical Executive. Summarize the following drug repurposing analysis for a "Go/No-Go" decision.
            
            Data:
            - Drug: Metformin (Example)
            - Literature Relevance: {int(lit_score)}% (Insights: {literature_data.get('key_insights', [])})
            - Patent Risk: {pat_risk}
            - Clinical Safety Score: {100-clin_risk}/100
            
            Calculated Confidence: {round(confidence, 1)}%
            Recommendation: {recommendation}
            
            Task:
            1. Write a 2-sentence executive summary justifying the {recommendation}.
            2. Provide 3 bullet points of rationale (Business, Legal, Clinical).
            
            Output strictly in JSON format: {{ "summary": "...", "rationale": ["...", "...", "..."] }}
            """
            
            response = model.generate_content(prompt)
            # Simple parsing (assuming model follows instructions, fallback if not)
            import json
            text = response.text.replace("```json", "").replace("```", "")
            parsed = json.loads(text)
            
            final_summary = parsed.get("summary", summary_fallback)
            final_rationale = parsed.get("rationale", final_rationale)
            
        except Exception as e:
            print(f"Gemini Error: {e}")
            final_summary += " (LLM unavailable, running heuristic mode)"

    return {
        "agent_name": "Decision & Report Agent",
        "final_confidence_score": round(confidence, 1),
        "recommendation": recommendation,
        "summary": final_summary,
        "rationale": final_rationale
    }
