import time
import random
import requests

def evaluate_clinical_trials(drug_name, therapeutic_area):
    """
    Queries OpenFDA to check for reported adverse events as a proxy for safety profile.
    """
    time.sleep(1.0)
    
    try:
        # OpenFDA Query for Adverse Events count
        url = f'https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:"{drug_name}"&limit=1'
        response = requests.get(url, timeout=5)
        
        data = response.json()
        
        total_reports = 0
        if "meta" in data:
            total_reports = data["meta"]["results"]["total"]
            
        # Heuristic scoring based on volume of reports (normalized by arbitrary factor for hackathon)
        # Assuming common drugs have many reports, but let's treat VERY high numbers as risky for repurposing 
        # (or implies well-known side effects).
        # Score 100 (Safe) -> 0 (Risky)
        # e.g., 0 reports -> 95, 1000 reports -> 80, 100,000 reports -> 50
        
        safety_score = max(50, 100 - int(total_reports / 5000))
        if safety_score < 40: safety_score = 40 # Cap floor
        
        return {
            "agent_name": "Clinical Trial Evaluation Agent",
            "status": "Success",
            "data": {
                "clinical_risk_score": 100 - safety_score,
                "safety_profile_score": safety_score,
                "max_phase_reached": "Approved" if total_reports > 100 else "Phase 2/3", 
                "common_adverse_events": ["Check OpenFDA for details" if total_reports > 0 else "None listed"],
                "total_patients_studied": total_reports if total_reports > 0 else 0,
                "source": "OpenFDA API"
            }
        }
        
    except Exception as e:
        # Fallback
        return {
            "agent_name": "Clinical Trial Evaluation Agent (Offline)",
            "status": "Simulated",
            "data": {
                "clinical_risk_score": 20,
                "safety_profile_score": 80,
                "max_phase_reached": "Simulated Phase 3",
                "common_adverse_events": ["Nausea (Simulated)", "Headache (Simulated)"],
                "total_patients_studied": random.randint(1000, 5000)
            }
        }
