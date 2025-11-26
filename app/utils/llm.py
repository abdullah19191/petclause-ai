# utils/llm.py
import os
import requests
import json
import time
import re
from typing import Dict, Any, Optional
import streamlit as st

# OPENROUTER_KEY = os.getenv("api_key")
def load_api_key():

    try:
        if "api_key" in st.secrets:
            return st.secrets["api_key"]
    except Exception:
        pass

    # 2. Try environment variable (Netlify/Vercel)
    if "OPENROUTER_API_KEY" in os.environ:
        return os.environ["OPENROUTER_API_KEY"]

    # 3. No key found
    return None

OPENROUTER_KEY = load_api_key()

# OPENROUTER_KEY = st.secrets.get("api_key")
MODEL = os.getenv("MODEL", "x-ai/grok-4.1-fast:free")
MODEL_FALLBACK = os.getenv("MODEL_FALLBACK", "meta-llama/llama-3-8b-instruct")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

TIMEOUT = 30
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.5

SYSTEM_PROMPT = (
    "You are a cautious compliance-checking assistant. You are NOT a lawyer. "
    "You compare rental listings against ordinances. Output JSON only."
)

EMPTY_RESULT = {
    "risky_phrases": [],
    "fixed_listing": "",
    "confidence": 0,
    "citations": [],
    "notes": "parse_error_or_empty_response"
}

def _extract_json_from_text(text: str) -> Optional[str]:
    m = re.search(r'(\{(?:[^{}]|(?R))*\})', text, re.S)
    if m:
        return m.group(1)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    return None

def _safe_load_json(text: str) -> Dict[str, Any]:
    if not text or not text.strip():
        return dict(EMPTY_RESULT)
    try:
        return json.loads(text)
    except Exception:
        jblk = _extract_json_from_text(text)
        if jblk:
            try:
                return json.loads(jblk)
            except Exception:
                return dict(EMPTY_RESULT)
    return dict(EMPTY_RESULT)

def _call_openrouter(payload: Dict[str, Any], timeout: int = TIMEOUT) -> Dict[str, Any]:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_KEY}"
    }
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            if attempt == MAX_RETRIES:
                return {"error": str(e)}
            time.sleep(BACKOFF_FACTOR ** attempt)
    return {"error": "unknown_error"}

###########################################
# SECOND PASS JSON NORMALIZER (CRITICAL)
###########################################
def enforce_json_structure(bad_output: str) -> dict:
    payload = {
        "model": "meta-llama/llama-3.1-70b-instruct:free",
        "messages": [
            {"role": "system",
             "content": "You convert invalid or messy AI output into VALID JSON ONLY. No explanations."},
            {"role": "user",
             "content": f"Convert the following into valid JSON. Only output JSON:\n\n{bad_output}"}
        ],
        "temperature": 0.0
    }

    resp = _call_openrouter(payload)
    try:
        txt = resp["choices"][0]["message"]["content"]
        return json.loads(txt)
    except Exception:
        return dict(EMPTY_RESULT)

###########################################
# MAIN ANALYSIS FUNCTION
###########################################
def analyze_listing(listing: str, ordinance: str, *,
                    model: Optional[str] = None,
                    enable_reasoning: bool = False) -> Dict[str, Any]:

    if not OPENROUTER_KEY:
        return {"error": "OPENROUTER_API_KEY missing", **EMPTY_RESULT}

    model = model or MODEL

    user_prompt = (
        "You MUST identify ANY illegal clauses based on the ordinance.\n"
        "You MUST output JSON only.\n"
        "JSON KEYS:\n"
        "{\n"
        "  \"risky_phrases\": [...],\n"
        "  \"fixed_listing\": \"...\",\n"
        "  \"confidence\": 0-100,\n"
        "  \"citations\": [...],\n"
        "  \"notes\": \"...\"\n"
        "}\n\n"
        "Listing:\n"
        f"{listing}\n\n"
        "Ordinance:\n"
        f"{ordinance}\n"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 900
    }

    if enable_reasoning and ("grok" in model):
        payload["extra_body"] = {"reasoning": {"enabled": True}}

    response = _call_openrouter(payload)

    if "error" in response:
        if model != MODEL_FALLBACK:
            return analyze_listing(listing, ordinance, model=MODEL_FALLBACK)
        return {"error": response["error"], **EMPTY_RESULT}

    try:
        content = response["choices"][0]["message"]["content"]

        ############################
        # FIRST ATTEMPT PARSE
        ############################
        parsed = _safe_load_json(content)

        ############################
        # SECOND PASS (ENFORCER)
        ############################
        if parsed["confidence"] == 0 and not parsed["risky_phrases"]:
            parsed = enforce_json_structure(content)

        ############################
        # FINAL SANITY CLEANING
        ############################
        parsed.setdefault("risky_phrases", [])
        parsed.setdefault("citations", [])
        parsed.setdefault("fixed_listing", listing)
        parsed.setdefault("confidence", 50)

        parsed["_meta"] = {
            "model_used": model,
            "raw_preview": content[:200] + "..."
        }

        return parsed

    except Exception as e:
        if model != MODEL_FALLBACK:
            return analyze_listing(listing, ordinance, model=MODEL_FALLBACK)
        return {"error": f"parse_error: {str(e)}", **EMPTY_RESULT}
