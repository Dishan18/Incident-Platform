"""
RCA Generator module.
Uses Gemini model via OpenRouter to dynamically generate a concise RCA report.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()


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
    system_inst = "You are a senior incident manager. Return ONLY valid JSON. Do not include markdown code fences."
    
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
                "response_format": {
                    "type": "json_object"
                },
                "messages": [
                    {
                        "role": "system",
                        "content": """
You are a senior incident manager.

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


def generate_rca_report(incident_data: dict) -> dict:
    """
    Generate a concise professional Root Cause Analysis report based on the provided
    incident details, pre-computed variables, and questionnaire responses.
    """
    prompt = f"""You are a senior incident manager.

Generate a concise professional Root Cause Analysis report.

Requirements:
- Maximum 200 words.
- Use accurate technical terminology.
- Avoid unnecessary technical jargon.
- The report must be understandable by engineers, managers, and business stakeholders.
- Explain technical failures in simple language.
- Do not invent facts.
- Use only information provided.
- Focus on:
  1. What happened
  2. Why it happened
  3. How it was resolved
  4. How recurrence will be prevented

Incident Details:
- Incident ID: {incident_data.get('incident_id')}
- Description: {incident_data.get('description')}
- Application: {incident_data.get('application')}
- Category: {incident_data.get('category')}
- Priority: {incident_data.get('priority')}
- Status: {incident_data.get('status')}
- Assigned Team: {incident_data.get('assigned_team')}
- Created At: {incident_data.get('created_at')}
- Resolved At: {incident_data.get('resolved_at')}
- Resolution Time: {incident_data.get('resolution_time')} minutes
- Affected Users: {incident_data.get('affected_users')}
- Impact Scope: {incident_data.get('impact_scope')}
- SLA Breached: {incident_data.get('sla_breached')}
- L3 Escalation Risk: {incident_data.get('l3_escalation_risk')}
- L3 Escalation Recommended: {incident_data.get('l3_escalation_recommended')}
- Predicted Root Cause (Agent): {incident_data.get('root_cause_prediction')} (Confidence: {incident_data.get('root_cause_confidence')}%)
- Similar Incidents: {incident_data.get('similar_incidents')}

Questionnaire Responses:
- Actual Root Cause Identified: {incident_data.get('actual_root_cause')}
- Action That Resolved Incident: {incident_data.get('resolution_action')}
- Preventive Measure: {incident_data.get('preventive_measure')}
- Additional Notes: {incident_data.get('additional_notes', 'None')}

Return ONLY valid JSON:
{{
  "summary": "",
  "root_cause": "",
  "resolution": "",
  "preventive_action": ""
}}"""

    try:
        res = call_openrouter(prompt)
        # Normalize and validate keys
        normalized = {}
        for k, default_key in [("summary", "summary"), ("root_cause", "root_cause"), ("resolution", "resolution"), ("preventive_action", "preventive_action")]:
            # Look for exact or case-insensitive matches
            match_found = False
            for rk in res.keys():
                if rk.lower().replace("_", "") == k.lower().replace("_", ""):
                    normalized[default_key] = res[rk]
                    match_found = True
                    break
            if not match_found:
                normalized[default_key] = ""
        return normalized
    except Exception as e:
        print(f"Error in generate_rca_report: {e}")
        # Fallback dictionary
        return {
            "summary": f"Incident {incident_data.get('incident_id')} caused an outage affecting {incident_data.get('affected_users')} users.",
            "root_cause": incident_data.get('actual_root_cause', 'Unknown root cause.'),
            "resolution": incident_data.get('resolution_action', 'Incident resolved.'),
            "preventive_action": incident_data.get('preventive_measure', 'Implement preventive measures.')
        }
