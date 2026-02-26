import os
import json
from google import genai
from google.genai import types

# Configure Gemini with the API key from environment
api_key = os.environ.get("GEMINI_API_KEY")

# We use gemini-2.5-flash as it is fast and cheap for this kind of logic task
client = None
if api_key:
    client = genai.Client(api_key=api_key)

def translate_findings(code_snippet: str, language: str, findings: list) -> dict:
    """
    Takes the raw Semgrep findings and original code, and asks Gemini to 
    translate it into a highly actionable, developer-friendly JSON format.
    """
    
    prompt = f"""
You are the VibeGuard DX Engine — the final quality gate before a security 
report reaches a developer. Your audience is "Vibe-Coders": solo founders, 
indie hackers, and creators who ship fast with AI tools but are NOT security experts.

Here is the original code snippet ({language}):
```
{code_snippet}
```

Here are the raw vulnerabilities found by the static analysis scanner (Semgrep):
```json
{json.dumps(findings, indent=2)}
```

=== YOUR TASK ===

1. SCORE
   Assign a VibeGuard Security Score from 0 to 100 using this exact rubric:
   - 95-100: Excellent (No real vulnerabilities)
   - 80-94: Good (Minor issues, low risk)
   - 60-79: Needs Work (Medium severity issues)
   - 30-59: Vulnerable (High severity issues, do not ship)
   - 0-29: Critical (Actively dangerous)

2. FORMAT
   For each confirmed issue, write:
   - title: A short, memorable name
   - severity: CRITICAL | HIGH | MEDIUM | LOW
   - description: Explain in 1-2 simple sentences WHY this is dangerous.
   - how_to_fix: Clear, conceptual steps on how to resolve the issue.
   - fixed_code_snippet: (OPTIONAL) Provide a corrected code snippet ONLY IF you are 100% confident it works. If unsure, leave null. Accurate detection is the most important goal.

Return ONLY a JSON object matching this exact structure:
{{
  "score": integer (0-100),
  "summary": "A 1-2 sentence friendly summary of the overall security state",
  "issues": [
    {{
      "title": "Short title",
      "severity": "CRITICAL",
      "description": "Explanation",
      "how_to_fix": "Fix instructions",
      "fixed_code_snippet": "Corrected code OR null"
    }}
  ]
}}
"""

    if not api_key:
        # Fallback if no API key is set for local testing without AI
        print("WARNING: GEMINI_API_KEY not set. Returning mock AI translation.")
        if not findings:
            return {
                "score": 100,
                "summary": "Looks good! No vulnerabilities found.",
                "issues": []
            }
        
        mock_issues = []
        for f in findings:
            mock_issues.append({
                "title": f.get("rule_id", "Security Issue"),
                "severity": f.get("severity", "HIGH").upper(),
                "description": f.get("message", "A vulnerability was found here."),
                "how_to_fix": "Please review the code and fix the issue according to best practices.",
                "fixed_code_snippet": "# AI Fix not available (No API Key set)\n" + f.get("code snippet", "")
            })
            
        return {
            "score": max(0, 100 - (len(findings) * 20)),
            "summary": "Vulnerabilities detected. Setup Gemini API key for detailed fixes.",
            "issues": mock_issues
        }

    if not client:
        return {
            "error": "Failed to translate findings using AI",
            "score": 0,
            "summary": "Internal API error: Gemini client is not initialized.",
            "issues": []
        }

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        text_response = response.text
        if text_response is None:
            text_response = "{}"
        
        # Strip potential markdown code blocks if the model wrapped the JSON
        if text_response.startswith("```json"):
            text_response = text_response.replace("```json\n", "").replace("```", "").strip()
            
        return json.loads(text_response)
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return {
            "error": "Failed to translate findings using AI",
            "score": 0,
            "summary": "Internal API error during translation layer processing.",
            "issues": []
        }

def translate_repo_findings(code_context: str, language: str, findings: list) -> dict:
    """
    Two-Stage LLM Pipeline for scanning entire repositories.
    Stage 1: gemini-2.5-pro (Deep Scan)
    Stage 2: gemini-2.5-flash (Filter & Format)
    """
    if not api_key or not client:
        # Re-use the fallback method for local testing
        return translate_findings(code_context, language, findings)
        
    try:
        # --- STAGE 1: Deep Scan with Gemini Pro ---
        stage1_prompt = f"""
You are VibeGuard Deep Scanner — an elite Application Security Architect 
specialized in reviewing code produced by AI coding assistants.

Your mission is to perform a Deep Security Analysis on the following codebase.
--- REPOSITORY CODE ({language}) ---
{code_context}
--- STATIC SCANNER (SEMGREP) FINDINGS ---
{json.dumps(findings, indent=2)}

=== YOUR TASK ===
1. VALIDATE SEMGREP FINDINGS (True positive vs False Positive).
2. HUNT FOR VIBE-FAILS: Actively search for specific categories, even if Semgrep reported nothing:
   - Auth & Authorization (Missing auth, Broken access control, JWT issues)
   - Injection & Input (SQLi, Command injection, Path traversal)
   - Secrets & Config (Hardcoded keys, CORS '*', Debug mode)
   - Data Protection (Plaintext passwords, PII leaks)
   - Architectural Weaknesses (No rate limiting, DoS vectors)
3. WRITE YOUR ANALYSIS: For each real vulnerability identify file, severity, and attack scenario. Do NOT suggest fixes yet.
Provide the analysis in plain text. Do not format as JSON.
"""
        
        print("Running Stage 1: Deep Scan (Gemini Flash as Pro Alternative)...")
        stage1_response = client.models.generate_content(
            model='gemini-2.5-flash', # Changed from pro to flash due to Free Tier Quotas
            contents=stage1_prompt,
        )
        deep_analysis = stage1_response.text or "No analysis provided."
        
        # Add a sleep to prevent hitting the RPM limit on the free tier (15 requests per minute)
        import time
        time.sleep(2)
        
        # --- STAGE 2: Filter & Format with Gemini Flash ---
        stage2_prompt = f"""
You are the VibeGuard DX Engine — the final quality gate before a security report reaches a developer.
Here is the Deep Security Analysis from our Architect:
--- ARCHITECT ANALYSIS ---
{deep_analysis}

=== YOUR TASK ===
1. FILTER: Keep only REAL, EXPLOITABLE risk from the analysis.
2. SCORE: Assign a Score (0-100).
   - 95-100: Excellent
   - 80-94: Good (Minor issues)
   - 60-79: Needs Work (Medium severity issues)
   - 30-59: Vulnerable (High severity issues)
   - 0-29: Critical
3. FORMAT:
   - title: A short name
   - severity: CRITICAL | HIGH | MEDIUM | LOW
   - file: The file where the issue lives
   - description: Explain in 1-2 simple sentences WHY this is dangerous.
   - how_to_fix: Clear conceptual steps on how to resolve the issue.
   - fixed_code_snippet: (OPTIONAL) Provide a corrected code snippet ONLY IF you are 100% confident it works. Otherwise return null. Accurate detection is the primary goal.

Return ONLY a JSON object matching this exact structure:
{{
  "score": <integer>,
  "summary": "<Friendly summary>",
  "issues": [
    {{
      "title": "<title>", "severity": "<severity>", "file": "<file>",
      "description": "<desc>", "how_to_fix": "<fix>", "fixed_code_snippet": "<code OR null>"
    }}
  ]
}}
Focus primarily on ACCURATE DETECTION. Return null for snippets if unsure.
"""
        
        print("Running Stage 2: Filter & Format (Gemini Flash)...")
        stage2_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=stage2_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        
        text_response = stage2_response.text
        if text_response is None:
            text_response = "{}"
            
        if text_response.startswith("```json"):
            text_response = text_response.replace("```json\n", "").replace("```", "").strip()
            
        return json.loads(text_response)
        
    except Exception as e:
        print(f"Error calling Gemini API in 2-Stage Pipeline: {e}")
        return {
            "error": "Failed to translate repository findings using AI",
            "score": 0,
            "summary": "Internal API error during Two-Stage LLM processing.",
            "issues": []
        }

