from fastapi import FastAPI
from pydantic import BaseModel
import requests
import re

# ---- Ollama config ----
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "tinyllama"

# ---- Mitigation #2: safety prompt ----
SAFETY_INSTRUCTION = (
    "You are a coding assistant that must never invent or guess software "
    "package names. Only recommend packages that are confirmed to exist in "
    "official registries (e.g., PyPI, npm, RubyGems, Crates.io, CPAN, etc.). "
    "If you are not sure that a package exists, explicitly say that you are "
    "unsure and do NOT make up a name."
)

app = FastAPI()


class PromptRequest(BaseModel):
    text: str


# ---- Helpers for calling Ollama ----
def call_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=300)
    r.raise_for_status()
    data = r.json()
    return data.get("response", "")


# ---- Mitigation #1: registry checks (very simple) ----
def extract_candidate_packages(text: str):
    """
    Very simple heuristics:
    - names after 'pip install'
    - names after 'npm install'
    Extend if you want more ecosystems.
    """
    candidates = set()
    patterns = [
        r"pip install ([a-zA-Z0-9_\-]+)",
        r"npm install ([a-zA-Z0-9_\-@/]+)",
    ]
    for pat in patterns:
        for match in re.findall(pat, text):
            candidates.add(match.strip())
    return list(candidates)


def pypi_exists(name: str) -> bool:
    try:
        r = requests.get(f"https://pypi.org/pypi/{name}/json", timeout=5)
        return r.status_code == 200
    except Exception:
        # On network failure, don't over-block; assume exists
        return True


def npm_exists(name: str) -> bool:
    try:
        r = requests.get(f"https://registry.npmjs.org/{name}", timeout=5)
        return r.status_code == 200
    except Exception:
        return True


def all_packages_exist(candidates):
    for pkg in candidates:
        if not (pypi_exists(pkg) or npm_exists(pkg)):
            return False
    return True


@app.post("/generate")
def generate(req: PromptRequest):
    # Build full prompt with safety instruction
    full_prompt = SAFETY_INSTRUCTION + "\n\nUser:\n" + req.text + "\n\nAssistant:\n"
    raw = call_ollama(full_prompt)

    # Try to strip any prompt echo
    marker = "Assistant:"
    if marker in raw:
        out = raw.split(marker, 1)[-1].strip()
    else:
        # Best-effort: drop the safety + user prefix
        if full_prompt in raw:
            out = raw.split(full_prompt, 1)[-1].strip()
        else:
            out = raw.strip()

    # Check for hallucinated package names
    candidates = extract_candidate_packages(out)
    if candidates and not all_packages_exist(candidates):
        safe_msg = (
            "I cannot confidently identify any existing package that matches this "
            "description in public registries. Please search directly on the "
            "official registry website (e.g., PyPI, npm) instead of trusting this suggestion."
        )
        return {"text": safe_msg}

    return {"text": out}
