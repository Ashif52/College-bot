# chatbot/question_generator.py
# ─────────────────────────────────────────────────────────────────────────────
# Uses Groq LLM to:
#   1. Summarise the chat conversation
#   2. Extract structured data (course, education, location)
#   3. Generate 4-5 personalised follow-up questions for the voicebot
# ─────────────────────────────────────────────────────────────────────────────

import json
from chatbot.config import GROQ_API_KEY, GROQ_MODEL


# Admission-relevant data points an admissions counsellor would collect
DESIRED_DATA_POINTS = [
    "Specific course or branch of interest (e.g. B.E. CSE, MBA, MCA, M.Tech)",
    "Current highest qualification (12th / Diploma / UG degree / PG degree)",
    "Percentage or CGPA scored in current/last qualification",
    "Year of passing or expected year of passing current qualification",
    "Home state (important for TN counselling vs management quota eligibility)",
    "Whether they have appeared or plan to appear for any entrance exams (TNEA, TANCET, CAT, MAT, etc.)",
    "Preferred mode of admission (Tamil Nadu counselling / Management quota / NRI quota)",
    "Whether they need hostel accommodation",
    "Current school or college name (for follow-up context)",
]


def _format_history(session) -> str:
    """Format the chat history as a readable transcript."""
    lines = []
    for msg in session.history:
        role = "Student" if msg.role == "user" else "Assistant"
        lines.append(f"{role}: {msg.content}")
    return "\n".join(lines)


def generate_followup_data(session) -> dict:
    """
    Analyse the conversation and return:
    {
        "chat_summary": str,
        "course_of_interest": str,
        "current_education": str,
        "location": str,
        "followup_questions": [str, str, str, str, str]  # 4-5 items
    }
    """
    from groq import Groq

    if not GROQ_API_KEY:
        return _empty_result()

    transcript = _format_history(session)
    name  = session.student_name or "the student"
    phone = session.phone_number or "(unknown)"

    system_prompt = (
        "You are a professional admissions counsellor at Nexus Institute of Technology. "
        "Your goal is to collect student details needed for the admissions process — "
        "academic background, course interest, eligibility, and admission mode. "
        "You speak like a helpful government college counsellor, not a salesperson."
    )

    user_prompt = f"""Analyse this student enquiry conversation and respond with ONLY a valid JSON object (no markdown, no explanation).

Student Name: {name}
Phone: {phone}

Conversation Transcript:
{transcript}

The college needs to collect the following data about every prospective student:
{chr(10).join(f"- {dp}" for dp in DESIRED_DATA_POINTS)}

Output exactly this JSON structure:
{{
  "chat_summary": "<2-3 sentence summary of what the student asked and what topics were discussed>",
  "course_of_interest": "<extracted course or department, or empty string if not mentioned>",
  "current_education": "<extracted qualification/percentage, or empty string if not mentioned>",
  "location": "<extracted city/state, or empty string if not mentioned>",
  "followup_questions": [
    "<question 1 — most important missing data point for this student>",
    "<question 2>",
    "<question 3>",
    "<question 4>",
    "<question 5 — optional but helpful>"
  ]
}}

Rules for follow-up questions:
- Phrase questions exactly as an admissions counsellor would say them on a call
- Do NOT ask for name or phone (already collected)
- Do NOT ask about fees, tuition cost, or budget — the admissions office does NOT ask this
- Do NOT ask whether the student has visited the campus or compared colleges
- Focus ONLY on academic eligibility, course preference, admission mode, and qualification details
- Focus on data NOT already gathered from the conversation above
- Keep each question conversational and under 20 words
- Generate 4 to 5 questions maximum
"""

    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=1024,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    if raw.endswith("```"):
        raw = raw[:-3].strip()

    try:
        result = json.loads(raw)
        # Ensure followup_questions is a list of strings, max 5
        fqs = result.get("followup_questions", [])
        if isinstance(fqs, list):
            result["followup_questions"] = [str(q) for q in fqs[:5]]
        else:
            result["followup_questions"] = []
        return result
    except json.JSONDecodeError as e:
        print(f"[question_generator] JSON parse error: {e}\nRaw: {raw}")
        return _empty_result()


def _empty_result() -> dict:
    return {
        "chat_summary": "",
        "course_of_interest": "",
        "current_education": "",
        "location": "",
        "followup_questions": [],
    }
