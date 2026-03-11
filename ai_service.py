import os
import json
import re
import httpx
from typing import Any, Dict, List

INFERENCE_URL = "https://inference.do-ai.run/v1/chat/completions"
DEFAULT_MODEL = os.getenv("DO_INFERENCE_MODEL", "openai-gpt-oss-120b")
API_KEY = os.getenv("DIGITALOCEAN_INFERENCE_KEY")

def _extract_json(text: str) -> str:
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()

def _coerce_unstructured_payload(raw_text: str) -> Dict[str, Any]:
    compact = raw_text.strip()
    tags = [part.strip(" -•\t") for part in re.split(r",|\\n", compact) if part.strip(" -•\t")]
    return {
        "note": "Model returned plain text instead of JSON",
        "raw": compact,
        "text": compact,
        "summary": compact,
        "tags": tags[:6],
    }


async def _call_inference(messages: List[Dict[str, str]], max_tokens: int = 512) -> Dict[str, Any]:
    if not API_KEY:
        return {"note": "AI inference key not configured"}
    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "max_completion_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}
    async with httpx.AsyncClient(timeout=90.0) as client:
        try:
            resp = await client.post(INFERENCE_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            json_str = _extract_json(content)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return {"note": "Failed to parse AI response", "raw": content}
        except Exception as e:
            return {"note": "AI service unavailable", "error": str(e)}

async def generate_card(term: str) -> Dict[str, Any]:
    messages = [
        {"role": "system", "content": "You are a medical education assistant."},
        {
            "role": "user",
            "content": f"Provide a concise definition for the medical term '{term}'. Return a JSON object with keys 'term' and 'definition'."
        },
    ]
    return await _call_inference(messages)

async def recommend_decks() -> Dict[str, Any]:
    messages = [
        {"role": "system", "content": "You are a medical education assistant."},
        {
            "role": "user",
            "content": "Suggest three medical deck titles that would be most useful for a 2nd‑year medical student preparing for anatomy and pharmacology exams. Return a JSON array where each element has 'deck_id' (use a placeholder integer) and 'title'."
        },
    ]
    return await _call_inference(messages)
