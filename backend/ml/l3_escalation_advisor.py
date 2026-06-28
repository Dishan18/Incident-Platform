"""
L3 Escalation Advisor module.
Uses Gemini model to analyze if an incident needs escalation to L3 support
based on SLA risk, severity, impact, history, and root cause analysis.
"""

import os
import json
from dotenv import load_dotenv
import requests
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
    system_inst = "You are a senior IT incident manager. Return ONLY valid JSON. Do not include markdown code fences."
    
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
                "model": "google/gemma-2-9b-it:free",
                "response_format": {
                    "type": "json_object"
                },
                "messages": [
                    {
                        "role": "system",
                        "content": """
You are a senior IT incident manager.

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

def calculate_risk_score(
    priority: str,
    affected_users: int,
    impact_scope: str,
    predicted_resolution_time: float,
) -> int:
    """Calculate the escalation risk score programmatically based on incident features."""
    risk = 0
    if priority == "P1":
        risk += 40
    elif priority == "P2":
        risk += 25

    if affected_users > 1000:
        risk += 25

    if impact_scope == "enterprise":
        risk += 20

    if predicted_resolution_time > 240:
        risk += 15

    return min(risk, 100)


def run_fallback_rules(
    priority: str,
    affected_users: int,
    impact_scope: str,
    predicted_resolution_time: float,
    predicted_team: str,
) -> dict:
    """Execute rule-based escalation fallback reasoning when Gemini is unavailable."""
    risk = calculate_risk_score(
        priority=priority,
        affected_users=affected_users,
        impact_scope=impact_scope,
        predicted_resolution_time=predicted_resolution_time,
    )
    reasons = []

    if priority == "P1":
        reasons.append("Priority is P1")
    elif priority == "P2":
        reasons.append("Priority is P2")

    if affected_users > 1000:
        reasons.append("High user count")

    if impact_scope == "enterprise":
        reasons.append("Enterprise impact")

    if predicted_resolution_time > 240:
        reasons.append("Elevated SLA breach risk")

    # Recommended team fallback
    recommended_team = predicted_team if predicted_team else "L2 Support"
    # Escalate if risk is 50 or higher
    escalate = risk >= 50

    return {
        "risk_score": risk,
        "escalate": escalate,
        "recommended_team": recommended_team,
        "reasons": reasons if reasons else ["Standard support criteria met"]
    }



def analyze_l3_escalation(
    incident: dict,
    similar_incidents: list,
    root_cause_analysis: dict | str,
) -> dict:
    """Analyze L3 escalation probability using Gemini API, or run fallback logic.

    Parameters
    ----------
    incident : dict
        Details of the incident currently being reviewed.
    similar_incidents : list
        List of similar historical incidents.
    root_cause_analysis : dict or str
        Result of the Root Cause Agent analysis.

    Returns
    -------
    dict
        Contains 'risk_score', 'escalate', 'recommended_team', 'reasons'.
    """
    # 1. Extract and sanitize input parameters
    description = incident.get("description") or ""
    application = incident.get("application") or ""
    affected_users = int(incident.get("affected_users") or 0)
    impact_scope = incident.get("impact_scope") or ""
    predicted_team = incident.get("predicted_team") or incident.get("ai_predicted_team") or incident.get("teams") or ""
    predicted_priority = incident.get("predicted_priority") or incident.get("ai_predicted_priority") or incident.get("priority") or "P4"
    
    pred_res_time_val = incident.get("predicted_resolution_time") or incident.get("ai_predicted_resolution_time") or incident.get("resolution_time")
    try:
        predicted_resolution_time = float(pred_res_time_val) if pred_res_time_val is not None else 0.0
    except (ValueError, TypeError):
        predicted_resolution_time = 0.0

    sla_risk_data = incident.get("sla_risk") or {}
    sla_breached = bool(sla_risk_data.get("sla_breached", False))
    sla_remaining_minutes = int(sla_risk_data.get("sla_remaining_minutes", 0))

    calculated_risk_score = calculate_risk_score(
        priority=predicted_priority,
        affected_users=affected_users,
        impact_scope=impact_scope,
        predicted_resolution_time=predicted_resolution_time,
    )

    try:
        # Prepare similar incidents summary for the prompt
        similar_text = ""
        if isinstance(similar_incidents, list):
            for idx, inc in enumerate(similar_incidents, 1):
                if isinstance(inc, dict):
                    similar_text += (
                        f"Incident #{idx}:\n"
                        f"  Description: {inc.get('description', '')}\n"
                        f"  Team: {inc.get('team', '')}\n"
                        f"  Priority: {inc.get('priority', '')}\n"
                        f"  Resolution Time: {inc.get('resolution_time', '')} min\n"
                        f"  Root Cause: {inc.get('root_cause', '')}\n\n"
                    )

        # Prepare Root Cause Summary
        rc_text = ""
        if isinstance(root_cause_analysis, dict):
            rc_text = (
                f"Predicted Root Cause: {root_cause_analysis.get('root_cause', 'Unknown')}\n"
                f"Confidence: {root_cause_analysis.get('confidence', 50)}%\n"
                f"Explanation: {root_cause_analysis.get('explanation', '')}\n"
                f"Investigation Steps: {', '.join(root_cause_analysis.get('investigation_steps', []))}"
            )
        else:
            rc_text = str(root_cause_analysis)

        prompt = f"""You are a senior IT incident manager.

Determine whether this incident should be escalated to L3 support.

Do not recommend escalation solely based on priority.

Consider:
- priority
- affected users
- impact scope
- predicted resolution time
- recommended support team
- root cause analysis
- historical similar incidents
- SLA risk
- historical incident outcomes
- predicted resolution complexity
- SLA breach likelihood
- business impact
- specialist expertise requirements

Current Incident:
- Description: {description}
- Application: {application}
- Affected Users: {affected_users}
- Impact Scope: {impact_scope}
- Recommended Support Team: {predicted_team}
- Priority: {predicted_priority}
- Calculated Risk Score: {calculated_risk_score}%
- Predicted Resolution Time: {predicted_resolution_time} minutes
- SLA Breached: {sla_breached}
- SLA Remaining Minutes: {sla_remaining_minutes}

Root Cause Analysis:
{rc_text}

Historical Similar Incidents:
{similar_text.strip()}

Return ONLY a valid JSON object matching the following structure exactly:
{{
  "escalate": false,
  "recommended_team": "",
  "reasons": [
    ""
  ]
}}"""

        result = call_openrouter(prompt)
        
        # Normalize and validate keys in output response
        normalized = {
            "risk_score": calculated_risk_score
        }
            
        # escalate (bool)
        escalate_keys = ["escalate", "should_escalate", "escalation", "recommended"]
        for k in escalate_keys:
            if k in result:
                normalized["escalate"] = bool(result[k])
                break
        if "escalate" not in normalized:
            # Fallback escalate determination
            normalized["escalate"] = normalized["risk_score"] >= 50
            
        # recommended_team
        team_keys = ["recommended_team", "team", "recommendedTeam", "escalate_to"]
        for k in team_keys:
            if k in result:
                normalized["recommended_team"] = str(result[k])
                break
        if "recommended_team" not in normalized:
            normalized["recommended_team"] = predicted_team
            
        # reasons (list of strings)
        reasons_keys = ["reasons", "reason", "justification"]
        for k in reasons_keys:
            if k in result:
                normalized["reasons"] = result[k]
                break
        if "reasons" not in normalized:
            normalized["reasons"] = []
        if isinstance(normalized["reasons"], str):
            normalized["reasons"] = [normalized["reasons"]]
        elif not isinstance(normalized["reasons"], list):
            normalized["reasons"] = []

        return normalized

    except Exception as e:
        print(f"L3 escalation advisor failed: {str(e)}")
        return run_fallback_rules(
            priority=predicted_priority,
            affected_users=affected_users,
            impact_scope=impact_scope,
            predicted_resolution_time=predicted_resolution_time,
            predicted_team=predicted_team,
        )
