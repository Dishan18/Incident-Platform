"""
Root Cause Agent module.
Uses Gemini model to dynamically analyze the current incident
against similar historical incidents and determine the root cause,
confidence score, investigation steps, and explanation.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()


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

def call_gemini_fallback(prompt: str, system_instruction: str = None) -> dict:
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY not found in environment.")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
        
    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=(3.05, 30.0)
    )
    response.raise_for_status()
    res_json = response.json()
    content = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
    
    try:
        return json.loads(content)
    except Exception:
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1:
            return json.loads(content[start:end + 1])
        raise ValueError("Gemini fallback did not return valid JSON.")


def call_openrouter(prompt: str) -> dict:
    api_key = os.getenv("OPENROUTER_API_KEY")
    system_inst = "You are a senior NOC engineer. Return ONLY valid JSON. Do not include markdown code fences."
    
    if not api_key:
        print("OPENROUTER_API_KEY not found. Trying Gemini API fallback...")
        return call_gemini_fallback(prompt, system_inst)

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "Incident Intelligence Platform"
            },
            json={
                "model": "openrouter/free",
                "messages": [
                    {
                        "role": "system",
                        "content": """
                        You are a senior NOC engineer.

                        Return ONLY valid JSON.

                        Do not use markdown.
                        Do not use code fences.
                        Do not add explanations.
                        Do not add text before or after the JSON.
                        """
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            timeout=(3.05, 60.0)
        )

        response.raise_for_status()

        result = response.json()
        content = (
            result["choices"][0]
            ["message"]
            ["content"]
            .strip()
        )

        try:
            return json.loads(content)
        except Exception:
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1:
                return json.loads(content[start:end + 1])
            raise ValueError("Model did not return JSON")
            
    except Exception as e:
        print(f"OpenRouter call failed or rate limited ({e}). Trying Gemini API fallback...")
        return call_gemini_fallback(prompt, system_inst)

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

        result = call_openrouter(prompt)
        normalized = normalize_keys(result)
        return normalized
        
    except Exception as e:
        import traceback
        print("ERROR in analyze_root_cause:")
        try:
            traceback.print_exc()
        except Exception:
            pass
        # Fallback dictionary in case of API failure or parsing issues
        return {
            "root_cause": "Pending Analysis",
            "confidence": 50,
            "investigation_steps": [
                "Investigate application and server logs.",
                "Verify network paths and database connection state.",
                "Review recent system and package deployments."
            ],
            "explanation": (
                "AI analysis temporarily unavailable. "
                "Fallback investigation guidance has been provided."
            )
        }
