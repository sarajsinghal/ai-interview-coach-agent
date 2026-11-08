# AI Interview Coach Agent — MVP

A local Streamlit app for resume/job-description analysis, tailored interview questions,
answer evaluation and a practice-readiness report. Gemini provides the language-model
capabilities; LangGraph orchestrates the role-analysis workflow. SQLite stores session history.

## Requirements
- Python 3.10+
- Gemini API key

## Windows setup
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
```
Edit `.env` and add your Gemini API key. Then run:
```powershell
streamlit run app.py
```
Open the local address Streamlit displays (usually http://localhost:8501).

## Use
1. Paste your resume text and the target job description.
2. Enter the role title and choose the interview level and focus areas.
3. Analyse the profile.
4. Generate ten tailored questions.
5. Answer questions one at a time and request feedback.
6. Generate a readiness report and review saved session history.

## Privacy and accuracy
- Resume and job description text is sent to the configured Gemini API when AI actions are run.
- Remove personal contact details before pasting if you do not want to send them.
- Do not paste passwords, identity numbers, confidential employer information or other sensitive data.
- The coach must not invent experience or achievements. Treat all suggested improvements as drafts and verify them.
- This MVP stores session summaries and reports locally in SQLite. It does not store API keys in the database.

## Limitations
- Resume and job description are pasted as text; direct PDF/DOCX upload is not included in this MVP.
- Session history stores report metadata, not a full searchable transcript archive.
- Feedback quality depends on the supplied context and Gemini model output. Review technical guidance.
- No automated hiring decision or guarantee of interview success is provided.
