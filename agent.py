
import os
import json
import re

from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from openai import OpenAI


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# PARALLEL API CONNECTION
# --------------------------------------------------

def ask_parallel(prompt, model=None):

    api_key = os.getenv("PARALLEL_API_KEY")

    if not api_key:
        raise RuntimeError(
            "PARALLEL_API_KEY is missing. "
            "Check your .env file."
        )

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.parallel.ai/v1",
        timeout=120.0
    )

    try:

        response = client.responses.create(
            model=os.getenv("PARALLEL_MODEL", "parallel"),
            input=prompt,
            reasoning={"effort": "low"}
        )

        result = response.output_text

        if not result:
            raise RuntimeError(
                "Parallel returned an empty response."
            )

        return result

    except Exception as error:

        raise RuntimeError(
            f"Parallel API request failed: {error}"
        ) from error

    finally:

        client.close()


# --------------------------------------------------
# LANGGRAPH JOB ANALYSIS
# --------------------------------------------------

class JobState(TypedDict, total=False):

    resume: str
    jd: str
    job_title: str
    company: str
    level: str
    model: str
    analysis: str


def role_analysis_node(s):

    prompt = f"""
You are a careful and evidence-based interview preparation analyst.

Analyse the supplied resume and job description.

IMPORTANT INSTRUCTIONS:

- Use only the supplied resume and job description.
- Do not invent qualifications, experience, achievements, metrics,
  tools, certifications or projects.
- Clearly distinguish documented experience from transferable skills.
- Identify missing evidence as preparation gaps, not candidate failures.
- Do not claim that an applicant has a skill unless supported by the
  supplied information.
- Do not conduct web research on the candidate or search for private
  resume information.

Prepare the following sections:

1. Role summary and likely interview priorities.
2. Matching evidence explicitly present in the resume.
3. Requirements not evidenced in the resume.
4. Transferable skills supported by evidence.
5. Areas requiring honest explanations.
6. Five likely interview themes.

Keep the language clear, practical and professional.

TARGET ROLE:
{s['job_title']}

COMPANY:
{s.get('company', 'Not specified')}

LEVEL:
{s['level']}

RESUME:
{s['resume'][:14000]}

JOB DESCRIPTION:
{s['jd'][:14000]}
"""

    return {
        "analysis": ask_parallel(prompt)
    }


# --------------------------------------------------
# LANGGRAPH WORKFLOW
# --------------------------------------------------

builder = StateGraph(JobState)

builder.add_node(
    "role_analysis",
    role_analysis_node
)

builder.add_edge(
    START,
    "role_analysis"
)

builder.add_edge(
    "role_analysis",
    END
)

job_graph = builder.compile()


# --------------------------------------------------
# RESUME AND JOB ANALYSIS
# --------------------------------------------------

def analyze_job(
    resume,
    jd,
    job_title,
    company,
    level,
    model=None
):

    result = job_graph.invoke({

        "resume": resume,
        "jd": jd,
        "job_title": job_title,
        "company": company,
        "level": level

    })

    return result["analysis"]


# --------------------------------------------------
# JSON EXTRACTION
# --------------------------------------------------

def extract_json(text):

    text = text.strip()

    # Remove Markdown code fences if returned.
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    try:

        return json.loads(text)

    except json.JSONDecodeError:

        # Attempt to extract a JSON array or object.
        match = re.search(
            r"\[[\s\S]*\]|\{[\s\S]*\}",
            text
        )

        if not match:

            raise ValueError(
                "Parallel did not return valid JSON. "
                "Please try again."
            )

        try:

            return json.loads(match.group(0))

        except json.JSONDecodeError as error:

            raise ValueError(
                "The returned JSON could not be parsed. "
                "Please try again."
            ) from error


# --------------------------------------------------
# INTERVIEW QUESTION GENERATION
# --------------------------------------------------

def generate_questions(profile, model=None):

    p = profile

    prompt = f"""
You are an experienced professional interview question designer.

Create exactly 10 interview questions based on the candidate's
resume and the supplied job description.

Return ONLY a valid JSON array.

Each item must contain these four keys:

- question
- type
- skill
- why_asked

Include a balanced mix based on these requested focus areas:

{", ".join(p['focus'])}

Requirements:

- Include relevant HR and behavioural questions.
- Include role-specific technical questions.
- Include situational and problem-solving questions where relevant.
- Do not assume experience that is absent from the resume.
- Include questions about documented skill gaps where appropriate.
- Avoid repetitive questions.
- Do not invent candidate achievements.

Role: {p['job_title']}

Level: {p['level']}

Resume:
{p['resume'][:10000]}

Job description:
{p['jd'][:10000]}

Role analysis:
{p['analysis'][:6000]}
"""

    result = extract_json(
        ask_parallel(prompt)
    )

    if not isinstance(result, list):

        raise ValueError(
            "Expected a JSON list of interview questions."
        )

    questions = []

    for item in result:

        if not isinstance(item, dict):
            continue

        required_keys = [
            "question",
            "type",
            "skill",
            "why_asked"
        ]

        if all(key in item for key in required_keys):
            questions.append(item)

    if not questions:

        raise ValueError(
            "No valid interview questions were returned."
        )

    return questions[:10]


# --------------------------------------------------
# INTERVIEW ANSWER EVALUATION
# --------------------------------------------------

def evaluate_answer(
    profile,
    question,
    answer,
    model=None
):

    prompt = f"""
Act as a rigorous but constructive professional interview coach.

Evaluate only the answer supplied by the candidate.

IMPORTANT:

- Never invent experience, facts or achievements.
- Do not rewrite the answer using unsupported claims.
- Identify missing evidence honestly.
- Distinguish factual correctness from presentation quality.
- If a technical claim cannot be verified, say so rather than guessing.
- Do not assume the candidate has professional experience simply
  because a question asks for it.

Return feedback using these headings:

1. Overall assessment
2. What worked
3. What is missing
4. Evidence and credibility check
5. Structure and communication
6. Suggested improvement
7. One follow-up question

For behavioural answers:
Assess Situation, Task, Action and Result (STAR) where applicable.

For technical answers:
Assess correctness, reasoning and clarity.

Role:
{profile['job_title']}

Question:
{question['question']}

Answer:
{answer}

Resume context:
{profile['resume'][:5000]}
"""

    return ask_parallel(prompt)


# --------------------------------------------------
# INTERVIEW READINESS REPORT
# --------------------------------------------------

def create_readiness_report(
    profile,
    answers,
    model=None
):

    condensed = "\n\n".join(

        f"""
QUESTION: {a['question']}

ANSWER: {a['answer']}

FEEDBACK: {a['feedback']}
"""

        for a in answers
    )

    prompt = f"""
You are an evidence-based interview preparation coach.

Create an interview practice report using only the supplied material.

Include these sections:

1. Preparation strengths.
2. Recurring improvement areas.
3. Unanswered skill gaps.
4. Communication observations.
5. Three priorities before the interview.
6. A practical interview preparation plan.

Important instructions:

- Do not invent achievements or experience.
- Do not create unsupported numeric scores.
- Do not claim that the candidate is job-ready without evidence.
- Distinguish observed strengths from areas requiring more practice.
- Give practical recommendations based on the actual answers.

Role:
{profile['job_title']}

Role analysis:
{profile['analysis'][:5000]}

Practice records:
{condensed[:16000]}
"""

    return ask_parallel(prompt)
