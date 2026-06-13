"""
Root Cause Agent module.
Uses Gemini model to dynamically analyze the current incident
against similar historical incidents and determine the root cause,
confidence score, investigation steps, and explanation.
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure the generative AI client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def normalize_keys(data: dict) -> dict:
    """Normalize response keys to ensure consistency regardless of model variation."""
    normalized = {}
    
    # Normalize root_cause
    rc_keys = ["root_cause", "rootcause", "rootCause", "cause", "predicted_root_cause"]
    for k in rc_keys:
        if k in data:
            normalized["root_cause"] = data[k]
            break
    if "root_cause" not in normalized:
        normalized["root_cause"] = "Unknown"
        
    # Normalize confidence
    conf_keys = ["confidence", "confidence_score", "confidenceScore", "score"]
    for k in conf_keys:
        if k in data:
            try:
                normalized["confidence"] = int(float(str(data[k]).replace("%", "").strip()))
            except (ValueError, TypeError):
                normalized["confidence"] = 50
            break
    if "confidence" not in normalized:
        normalized["confidence"] = 50
        
    # Normalize explanation
    exp_keys = ["explanation", "explanation_text", "reason", "reasoning", "details"]
    for k in exp_keys:
        if k in data:
            normalized["explanation"] = data[k]
            break
    if "explanation" not in normalized:
        normalized["explanation"] = ""
        
    # Normalize investigation_steps
    steps_keys = ["investigation_steps", "investigationsteps", "investigationSteps", "steps", "recommended_steps", "action_items"]
    for k in steps_keys:
        if k in data:
            normalized["investigation_steps"] = data[k]
            break
    if "investigation_steps" not in normalized:
        normalized["investigation_steps"] = []
        
    # Validate types
    if isinstance(normalized["investigation_steps"], str):
        normalized["investigation_steps"] = [normalized["investigation_steps"]]
    elif not isinstance(normalized["investigation_steps"], list):
        normalized["investigation_steps"] = []
        
    return normalized


def analyze_root_cause(current_incident: dict, similar_incidents: list) -> dict:
    """Analyze root cause for an incident using Gemini and similar historical records.

    Parameters
    ----------
    current_incident : dict
        Details of the incident currently being reviewed.
    similar_incidents : list
        List of similar historical incidents with verified root causes and categories.

    Returns
    -------
    dict
        Contains 'root_cause', 'confidence', 'investigation_steps', 'explanation'.
    """
    try:
        # 1. Clean current incident data for optimum token usage
        cleaned_current = {
            "incident_id": current_incident.get("incident_id"),
            "description": current_incident.get("description"),
            "application": current_incident.get("application"),
            "category": current_incident.get("category"),
            "impact_scope": current_incident.get("impact_scope"),
            "affected_users": current_incident.get("affected_users")
        }

        # 2. Clean similar incidents for optimum token usage
        cleaned_similar = []
        if isinstance(similar_incidents, list):
            for inc in similar_incidents:
                if not isinstance(inc, dict):
                    continue
                try:
                    sim_val = float(inc.get("similarity", 0.0))
                except (ValueError, TypeError):
                    sim_val = 0.0
                cleaned_similar.append({
                    "similarity": round(sim_val, 3),
                    "description": inc.get("description", ""),
                    "root_cause": inc.get("root_cause", ""),
                    "resolution_time": inc.get("resolution_time", "")
                })

        # Prepare concise historical text block
        similar_text = ""
        for idx, inc in enumerate(cleaned_similar, 1):
            similar_text += (
                f"Incident #{idx}:\n"
                f"  Similarity: {inc['similarity']}\n"
                f"  Description: {inc['description']}\n"
                f"  Root Cause: {inc['root_cause']}\n"
                f"  Resolution Time: {inc['resolution_time']} min\n\n"
            )

        # 3. Formulate the prompt for Gemini
        prompt = f"""You are a senior NOC engineer.
Analyze the current incident using the provided historical incidents as clues to find the root cause, determine confidence level, and recommend next-step investigation procedures.

Current Incident:
ID: {cleaned_current['incident_id']}
Application: {cleaned_current['application']}
Category: {cleaned_current['category']}
Impact Scope: {cleaned_current['impact_scope']}
Affected Users: {cleaned_current['affected_users']}
Description: {cleaned_current['description']}

Similar Historical Incidents:
{similar_text.strip()}

Return ONLY a valid JSON object matching the following structure exactly:
{{
  "root_cause": "VPN Tunnel Failure",
  "confidence": 87,
  "investigation_steps": [
    "Check VPN tunnel status",
    "Verify peer connectivity",
    "Review VPN gateway logs",
    "Validate routing paths",
    "Inspect firewall rules"
  ],
  "explanation": "Historical incidents indicate VPN tunnel instability as the most likely cause."
}}"""

        model = genai.GenerativeModel("gemini-2.5-flash")
        # Ensure json response format is used
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Parse the JSON response
        result = json.loads(response.text.strip())
        normalized = normalize_keys(result)
        return normalized
        
    except Exception as e:
        import traceback
        print("ERROR in analyze_root_cause:")
        traceback.print_exc()
        # Fallback dictionary in case of API failure or parsing issues
        return {
            "root_cause": "Pending Analysis",
            "confidence": 50,
            "investigation_steps": [
                "Investigate application and server logs.",
                "Verify network paths and database connection state.",
                "Review recent system and package deployments."
            ],
            "explanation": f"Unable to fetch generative analysis: {str(e)}"
        }
