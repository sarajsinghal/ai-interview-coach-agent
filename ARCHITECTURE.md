# AI Interview Coach Agent — Architecture

## User journey
Streamlit accepts resume text, job description, target role, level and practice focus.
The LangGraph role-analysis workflow calls Gemini and returns a grounded role/resume analysis.
The user generates a tailored set of questions, answers interactively, and requests feedback.
A final report consolidates practice observations and is saved to SQLite.

## Components
- `app.py`: Streamlit interface and session state.
- `agent.py`: Gemini calls, LangGraph workflow, question generation and answer feedback.
- `storage.py`: SQLite session persistence and history.
- `.env`: local API configuration (not committed).

## Trust and quality controls
- Prompt instructs the model not to invent candidate experience or achievements.
- Gaps are described as requirements not evidenced in the supplied resume.
- The user controls which resume/JD text is submitted.
- The application is a preparation aid, not a recruiter, hiring authority or factual verifier.
