# AI Interview Coach Agent

A Streamlit app for resume and job-description analysis, tailored interview questions, answer evaluation, a practice-readiness report, and company research.

**Live app:** https://ai-interview-coach-agent-9w644sdvgt2pr9pfd582tw.streamlit.app/

Parallel provides the language-model responses through its OpenAI-compatible Responses API; LangGraph orchestrates the role-analysis workflow. SQLite stores session history locally.

## Requirements
- Python 3.10+
- A Parallel API key

## Local setup (Windows)
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
```

Add your Parallel key to `.env`:
```env
PARALLEL_API_KEY=your_parallel_api_key
PARALLEL_MODEL=parallel
```

Run the app:
```powershell
streamlit run app.py
```
Open the local address Streamlit displays (usually http://localhost:8501).

## Streamlit Community Cloud
In the app's **Settings → Secrets**, add:
```toml
PARALLEL_API_KEY = "your_parallel_api_key"
PARALLEL_MODEL = "parallel"
```
The model setting is optional; the application defaults to `parallel`. Keep secrets in Streamlit's secret settings or your local `.env`; never commit a real key.

## Use
1. Paste your resume text and the target job description.
2. Enter the role title and choose the interview level and focus areas.
3. Analyse the profile.
4. Generate ten tailored questions.
5. Answer questions one at a time and request feedback.
6. Generate a readiness report and review saved session history.
7. Optionally research the company and role.

## Privacy and accuracy
- Resume, job-description, answer, and research prompt text is sent to Parallel when the corresponding AI action is run.
- Remove personal contact details before pasting if you do not want to send them.
- Do not paste passwords, identity numbers, confidential employer information or other sensitive data.
- The coach must not invent candidate experience or achievements. Treat suggested improvements as drafts and verify them.
- This MVP stores session summaries and reports locally in SQLite. It does not store API keys in the database.

## Limitations
- Resume and job description are pasted as text; direct PDF/DOCX upload is not included in this MVP.
- Session history stores report metadata, not a full searchable transcript archive.
- Feedback quality depends on the supplied context and model output. Review technical guidance.
- No automated hiring decision or guarantee of interview success is provided.
