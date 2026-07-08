"""
LLM SQL Generation Module.
Generates SQL queries from natural language requests and performs AI analytics summaries.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()


def call_gemini_text(prompt: str, system_instruction: str = None) -> str:
    """Generate raw text response from Gemini API."""
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY not found in environment.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
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
    return content


def call_gemini_json(prompt: str, system_instruction: str = None) -> dict:
    """Generate structured JSON response from Gemini API."""
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
        # Fallback parsing regex
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1:
            return json.loads(content[start:end + 1])
        raise ValueError("Gemini did not return valid JSON content.")


def generate_sql(natural_language_prompt: str) -> str:
    """Translate natural language user request into SQL SELECT statement using LLM."""
    model_name = os.getenv("LLM_MODEL", "openai/gpt-oss-20b:free")
    api_key = os.getenv("OPENROUTER_API_KEY")

    system_instruction = """
    You are an expert SQL assistant. Your task is to translate natural language user requests into safe, read-only SQL queries.
    
    Database Context:
    There is exactly ONE table named `incidents`.
    
    Available Table Schema and Columns:
    - incident_id (string): Unique identifier (e.g. INC-2026-00001)
    - description (string): Symptom details
    - application (string): Name of affected system
    - affected_users (integer): Count of affected users
    - impact_scope (string): single_user, department, site, enterprise
    - environment (string): Production, UAT, Development
    - category (string): Operational category (e.g. Network, Database)
    - teams (string): Assigned resolver group (comma-separated, e.g. Network or Database, Middleware)
    - priority (string): P1, P2, P3, P4
    - status (string): Open, Assigned, In Progress, Resolved, Closed, Cancelled
    - root_cause (string): Documented actual root cause
    - resolution_time (integer): Duration to resolve in minutes
    - created_at (datetime): Creation timestamp (e.g. 2026-06-15 14:30:00)
    - resolved_at (datetime): Resolution timestamp
    - sla_breached (boolean): True if SLA target was breached, False if met
    - assigned_at, in_progress_at, closed_at (datetime): Operations timestamps
    - l3_escalation_risk (integer): 0-100 score of SLA breach or complexity
    - l3_escalation_recommended (boolean): True if recommended, False otherwise
    - l3_escalation_reasons (string): JSON list of reasons
    - l3_escalation_team (string): Target L3 team name
    - rca_generated (boolean): True if RCA document exists
    - rca_content (string): JSON text of RCA details
    - rca_generated_at (datetime): RCA creation timestamp
    - rca_pdf_url (string): File store path to PDF
    
    Rules:
    1. The SQL query must use standard PostgreSQL syntax.
    2. Write ONLY a read-only SELECT statement. No INSERT, UPDATE, DELETE, DROP, CREATE, etc.
    3. Do NOT include any explanations, introduction, markdown code block fences (like ```sql), or other text.
    4. Return ONLY the raw SQL query.
    5. For partial/contains string matches on comma-separated list like `teams`, use `ILIKE` (e.g., `teams ILIKE '%Network%'`).
    6. Always assume current year is 2026 for relative date queries (e.g. June means 2026-06-01 to 2026-06-30).
    """

    if not api_key:
        print("OPENROUTER_API_KEY not found. Calling Gemini API fallback directly...")
        sql = call_gemini_text(natural_language_prompt, system_instruction)
    else:
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
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": natural_language_prompt}
                    ]
                },
                timeout=(3.05, 30.0)
            )
            response.raise_for_status()
            res_json = response.json()
            sql = res_json["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"OpenRouter generation failed ({e}). Falling back to Gemini...")
            sql = call_gemini_text(natural_language_prompt, system_instruction)

    # Clean code blocks/markdown returned by the LLM
    if sql.startswith("```"):
        # Remove starting ```sql or ```
        sql = re.sub(r"^```[a-zA-Z]*\s*", "", sql)
        # Remove trailing ```
        sql = re.sub(r"\s*```$", "", sql)

    return sql.strip()


def generate_summary_and_chart(prompt: str, sql_query: str, df_summary: dict) -> dict:
    """Generate concise executive summary and chart suggestion in a single JSON payload."""
    model_name = os.getenv("LLM_MODEL", "openai/gpt-oss-20b:free")
    api_key = os.getenv("OPENROUTER_API_KEY")

    prompt_data = {
        "user_request": prompt,
        "executed_sql": sql_query,
        "result_data_summary": df_summary
    }

    system_instruction = """
    You are an expert IT Operations Data Analyst. Review the executed query and the statistics of the returned dataset.
    
    You MUST respond with a single valid JSON object containing:
    1. "summary": A string containing a concise bulleted executive summary of the query results (max 4 bullets). Focus on key metrics (e.g. breach rates, counts, top applications).
    2. "chart_recommendation": A JSON object suggesting a chart to visualize this data, or null if no visualization makes sense.
       The "chart_recommendation" object must follow this strict schema:
       {
         "chart": "bar" | "line" | "pie" | "histogram" | "none",
         "title": "High level descriptive title",
         "x": "name of column to map on X-axis (must exist in result columns list)",
         "y": "name of column to map on Y-axis (must exist in result columns list, e.g. a count, sum, or aggregate value)"
       }
       Note: If "chart" is "pie", "x" is the category column name and "y" is the value/count column name.
    
    JSON format constraint:
    Output ONLY valid JSON. Do not include markdown code block fences (no ```json or ```).
    """

    payload_text = json.dumps(prompt_data, indent=2)

    if not api_key:
        print("OPENROUTER_API_KEY not found. Calling Gemini API fallback for summary...")
        return call_gemini_json(payload_text, system_instruction)

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
                "model": model_name,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": payload_text}
                ]
            },
            timeout=(3.05, 30.0)
        )
        response.raise_for_status()
        res_json = response.json()
        content = res_json["choices"][0]["message"]["content"].strip()
        
        try:
            return json.loads(content)
        except Exception:
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1:
                return json.loads(content[start:end + 1])
            raise ValueError("OpenRouter did not return valid JSON for summary.")
    except Exception as e:
        print(f"OpenRouter summary failed ({e}). Falling back to Gemini...")
        return call_gemini_json(payload_text, system_instruction)
