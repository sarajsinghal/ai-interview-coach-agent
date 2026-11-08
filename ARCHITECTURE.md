# AI Interview Coach Agent — Architecture

## User journey
Streamlit accepts resume text, job description, target role, level and practice focus.
The LangGraph role-analysis workflow sends a prompt to Parallel through its
OpenAI-compatible Responses API and returns a role/resume analysis. The user generates
tailored questions, answers interactively, and requests feedback. A final report
consolidates practice observations and is saved to SQLite.

## Components
- `app.py`: Streamlit interface, session state, and loading the Parallel key from environment variables or Streamlit Secrets.
- `agent.py`: Parallel Responses API calls through the OpenAI Python SDK, LangGraph workflow, question generation and answer feedback.
- `research.py`: Company and role research using the Parallel Responses API.
- `storage.py`: SQLite session persistence and history.
- `.env`: local API configuration (not committed); Streamlit deployments can use app Secrets.

## Trust and quality controls
- Prompts instruct the model not to invent candidate experience or achievements.
- Gaps are described as requirements not evidenced in the supplied resume.
- The user controls which resume and job-description text is submitted.
- The application is a preparation aid, not a recruiter, hiring authority or factual verifier.
