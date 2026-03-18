"""
QEXORA – Free AI-Powered Academic Mapping Service
==================================================
Uses FREE AI APIs in priority order:

1. Groq API (FREE)  – Llama 3.3 70B  – https://console.groq.com
2. Google Gemini (FREE) – Gemini 1.5 Flash – https://aistudio.google.com
3. Keyword Fallback – always works offline, no key needed

Both Groq and Gemini are 100% free with no credit card required.

Setup:
  Add to your .env file:
    GROQ_API_KEY=your-groq-key-here
  OR
    GEMINI_API_KEY=your-gemini-key-here

PI Code Framework (NBA / NAAC standard):
  PI 1.x → Knowledge & Comprehension (BL: Remember, Understand)
  PI 2.x → Application & Analysis     (BL: Apply, Analyse)
  PI 3.x → Synthesis & Evaluation     (BL: Evaluate, Create)
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY   = os.environ.get("GROQ_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

GROQ_API_URL   = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL     = "llama-3.3-70b-versatile"

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# ── PI Code Reference Table ──────────────────────────────────────────────────
PI_CODES = {
    "PI1.1": "Recall and reproduce core disciplinary facts, definitions, and concepts",
    "PI1.2": "Demonstrate understanding of principles, theories, and relationships",
    "PI1.3": "Classify and organise domain knowledge into structured frameworks",
    "PI1.4": "Interpret and explain technical information in own words",
    "PI2.1": "Apply learned concepts and procedures to solve standard problems",
    "PI2.2": "Use mathematical or computational methods to solve domain problems",
    "PI2.3": "Analyse systems, processes, or data to identify patterns and causes",
    "PI2.4": "Decompose complex problems into components and examine relationships",
    "PI3.1": "Design and construct systems, models, or solutions to complex problems",
    "PI3.2": "Synthesise knowledge from multiple domains to create novel solutions",
    "PI3.3": "Critically evaluate solutions, methods, or theories with justification",
    "PI3.4": "Demonstrate professional judgment and ethical reasoning in decisions",
}

# ── Shared system prompt ─────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are QEXORA's expert academic mapping engine trained in Outcome-Based Education (OBE) standards.

Analyse the given exam question and return a PRECISE academic mapping as a JSON object.

=== BLOOM'S TAXONOMY LEVELS (bl) ===
Use EXACTLY one of: remember, understand, apply, analyse, evaluate, create

- remember   → Define, List, Name, State, Identify, Label, Recall, Recognise
- understand → Explain, Describe, Summarise, Classify, Discuss, Interpret
- apply      → Apply, Solve, Use, Demonstrate, Calculate, Compute, Implement
- analyse    → Analyse, Compare, Contrast, Differentiate, Examine, Investigate
- evaluate   → Evaluate, Justify, Judge, Assess, Critique, Recommend, Defend
- create     → Design, Develop, Create, Construct, Build, Formulate, Generate, Plan

=== KNOWLEDGE CATEGORY (kc) ===
- factual        → Isolated facts, terminology, definitions, specific details
- conceptual     → Theories, models, principles, structures, classifications
- procedural     → Methods, algorithms, techniques, step-by-step processes
- metacognitive  → Strategic knowledge, self-regulation, critical reflection

=== COURSE OUTCOME (co) ===
- CO1 → remember level  (basic facts and definitions)
- CO2 → understand level (concepts and principles)
- CO3 → apply level     (procedures and computations)
- CO4 → analyse level   (comparison and investigation)
- CO5 → evaluate level  (critical evaluation)
- CO6 → create level    (complex design and innovation)

=== PROGRAM INDICATOR (pi) ===
- PI1.1 → Recall core facts and definitions          [remember]
- PI1.2 → Understand principles and theories         [understand]
- PI1.3 → Classify and organise knowledge            [understand]
- PI1.4 → Interpret and explain technical information [understand]
- PI2.1 → Apply concepts to standard problems        [apply]
- PI2.2 → Solve mathematical/computational problems   [apply]
- PI2.3 → Analyse systems and identify patterns      [analyse]
- PI2.4 → Decompose complex problems                 [analyse]
- PI3.1 → Design and construct solutions             [create]
- PI3.2 → Synthesise knowledge for novel solutions   [create]
- PI3.3 → Critically evaluate methods and theories   [evaluate]
- PI3.4 → Professional judgment and ethical reasoning [evaluate]

PI SELECTION RULES:
- remember   → PI1.1 (if pure recall) or PI1.3 (if classification)
- understand → PI1.2 (if principles) or PI1.4 (if interpretation)
- apply      → PI2.1 (if concept application) or PI2.2 (if math/computation)
- analyse    → PI2.3 (if systems/patterns) or PI2.4 (if decomposition)
- evaluate   → PI3.3 (if critique/evaluate) or PI3.4 (if ethical/professional)
- create     → PI3.1 (if design/construct) or PI3.2 (if synthesise/novel)

=== DIFFICULTY ===
- easy   → Single concept, direct recall, no computation
- medium → Multiple concepts, explanation or computation needed
- hard   → Complex analysis, design, multi-step problems, evaluation

=== MARKS ===
- easy → 2, medium → 5 or 6, hard → 10

=== OUTPUT ===
Return ONLY a valid JSON object. No markdown, no explanation, no extra text.

{
  "bl": "<level>",
  "kc": "<category>",
  "co": "<CO1-CO6>",
  "pi": "<PIx.x>",
  "pi_description": "<full PI description>",
  "difficulty": "<easy|medium|hard>",
  "marks": <number>,
  "reasoning": {
    "bl_reason": "<why this BL>",
    "kc_reason": "<why this KC>",
    "co_reason": "<why this CO>",
    "pi_reason": "<why this PI>"
  }
}"""


def _parse_json_response(text: str) -> dict:
    """Safely parse JSON from model response, stripping markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text  = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
    text = text.strip()
    return json.loads(text)


# ── Provider 1: Groq (FREE – Llama 3.3 70B) ─────────────────────────────────
def _call_groq(question_text: str, institution_type: str) -> dict:
    """Call Groq free API."""
    user_msg = (
        f"Institution Type: {institution_type.replace('_', ' ').title()}\n"
        f"Question: \"{question_text}\"\n\n"
        "Return only the JSON mapping."
    )

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_msg}
        ],
        "temperature": 0.1,
        "max_tokens":  800,
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json"
    }

    resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)

    if resp.status_code != 200:
        raise Exception(f"Groq error {resp.status_code}: {resp.text}")

    content = resp.json()["choices"][0]["message"]["content"]
    result  = _parse_json_response(content)
    result["source"] = "groq_llama3"
    return result


# ── Provider 2: Google Gemini (FREE – Gemini 1.5 Flash) ─────────────────────
def _call_gemini(question_text: str, institution_type: str) -> dict:
    """Call Google Gemini free API."""
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Institution Type: {institution_type.replace('_', ' ').title()}\n"
        f"Question: \"{question_text}\"\n\n"
        "Return only the JSON mapping."
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 800}
    }

    url  = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    resp = requests.post(url, json=payload, timeout=30)

    if resp.status_code != 200:
        raise Exception(f"Gemini error {resp.status_code}: {resp.text}")

    content = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    result  = _parse_json_response(content)
    result["source"] = "gemini_flash"
    return result


# ── Provider 3: Keyword Fallback (always works, no key needed) ───────────────
def _keyword_fallback(question_text: str) -> dict:
    text = question_text.lower()

    bl_rules = [
        ("create",    ["design","develop","create","construct","build","formulate","generate","plan","produce","compose"]),
        ("evaluate",  ["evaluate","justify","judge","assess","critique","argue","defend","recommend","rate","support"]),
        ("analyse",   ["analyse","analyze","compare","contrast","differentiate","examine","break down","investigate","test"]),
        ("apply",     ["apply","solve","use","demonstrate","calculate","compute","implement","execute","operate","illustrate"]),
        ("understand",["explain","describe","summarize","summarise","classify","discuss","interpret","outline","review","translate"]),
        ("remember",  ["define","list","name","recall","state","identify","label","memorize","recognise","recognize","repeat"]),
    ]
    bl = "understand"
    for level, keywords in bl_rules:
        if any(kw in text for kw in keywords):
            bl = level
            break

    kc_rules = [
        ("metacognitive", ["evaluate","reflect","assess","judge","design","develop","create","plan","construct"]),
        ("procedural",    ["apply","solve","calculate","demonstrate","use","implement","execute","compute","operate"]),
        ("conceptual",    ["explain","describe","classify","summarize","summarise","discuss","interpret"]),
        ("factual",       ["define","list","state","name","identify","recall","label","recognise"]),
    ]
    kc = "conceptual"
    for cat, keywords in kc_rules:
        if any(kw in text for kw in keywords):
            kc = cat
            break

    bl_map = {
        "remember":   ("CO1", "PI1.1", "easy",   2),
        "understand": ("CO2", "PI1.2", "easy",   2),
        "apply":      ("CO3", "PI2.1", "medium", 6),
        "analyse":    ("CO4", "PI2.3", "medium", 6),
        "evaluate":   ("CO5", "PI3.3", "hard",  10),
        "create":     ("CO6", "PI3.1", "hard",  10),
    }
    co, pi, difficulty, marks = bl_map.get(bl, ("CO2", "PI1.2", "medium", 6))

    # Refine PI for computational questions
    if any(kw in text for kw in ["calculate","compute","solve","formula","equation","circuit","current","resistance"]):
        if bl == "apply":
            pi = "PI2.2"

    return {
        "bl":             bl,
        "kc":             kc,
        "co":             co,
        "pi":             pi,
        "pi_description": PI_CODES.get(pi, ""),
        "difficulty":     difficulty,
        "marks":          marks,
        "reasoning": {
            "bl_reason":  f"Action keyword detected in question → '{bl}' level",
            "kc_reason":  f"Question verb pattern indicates '{kc}' knowledge",
            "co_reason":  f"Mapped from Bloom's level '{bl}' → {co}",
            "pi_reason":  f"Mapped from Bloom's level '{bl}' → {pi}"
        },
        "source": "keyword_fallback"
    }


# ── Main entry point ─────────────────────────────────────────────────────────
def suggest_mapping(question_text: str, institution_type: str = "engineering") -> dict:
    """
    Try AI providers in order: Groq → Gemini → Keyword fallback.
    Always returns a valid mapping dict.
    """
    if not question_text or not question_text.strip():
        return {"error": "Empty question text"}

    # 1. Try Groq (free)
    if GROQ_API_KEY:
        try:
            result = _call_groq(question_text, institution_type)
            if "pi" in result and "pi_description" not in result:
                result["pi_description"] = PI_CODES.get(result.get("pi", ""), "")
            print(f"[AI Mapping] ✓ Groq Llama 3.3 used")
            return result
        except Exception as e:
            print(f"[AI Mapping] Groq error: {e} — trying Gemini")

    # 2. Try Google Gemini (free)
    if GEMINI_API_KEY:
        try:
            result = _call_gemini(question_text, institution_type)
            if "pi" in result and "pi_description" not in result:
                result["pi_description"] = PI_CODES.get(result.get("pi", ""), "")
            print(f"[AI Mapping] ✓ Google Gemini used")
            return result
        except Exception as e:
            print(f"[AI Mapping] Gemini error: {e} — using keyword fallback")

    # 3. Keyword fallback
    print("[AI Mapping] Using keyword fallback (no API key found)")
    return _keyword_fallback(question_text)


def get_pi_codes() -> dict:
    """Return the full PI code reference table."""
    return PI_CODES
