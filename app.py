
import os
import streamlit as st
from dotenv import load_dotenv

from agent import (
    analyze_job,
    generate_questions,
    evaluate_answer,
    create_readiness_report
)

from storage import init_db, save_session, load_sessions
from research import research_company_and_role


# ==========================================
# APPLICATION SETUP
# ==========================================

load_dotenv()

# Streamlit Community Cloud stores deployment credentials in st.secrets.
# Keep environment variables (including local .env values) as the first choice.
try:
    _parallel_secret = st.secrets["PARALLEL_API_KEY"]
except (KeyError, FileNotFoundError):
    pass
else:
    os.environ.setdefault("PARALLEL_API_KEY", str(_parallel_secret))

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎯",
    layout="wide"
)

init_db()

st.title("AI Interview Coach")

st.caption(
    "Resume analysis • Interview preparation • "
    "Answer evaluation • Company research"
)


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.header("Setup")

    if os.getenv("PARALLEL_API_KEY"):

        st.success("Parallel API key detected.")

    else:

        st.error("Parallel API key missing. Check your .env file.")

    st.caption(
        "Parallel powers all AI features in this application."
    )

    st.divider()

    st.markdown("**How to use**")

    st.write(
        "1. Add your resume and job description.\n"
        "2. Generate a tailored interview plan.\n"
        "3. Practise interview questions.\n"
        "4. Evaluate your answers.\n"
        "5. Generate your readiness report.\n"
        "6. Research companies and job roles."
    )


# ==========================================
# SESSION STATE
# ==========================================

defaults = {
    "profile": {},
    "questions": [],
    "answers": [],
    "question_index": 0,
    "parallel_research_result": "",
    "last_feedback": "",
    "report": ""
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================
# DASHBOARD TABS
# ==========================================

tab1, tab2, tab3, tab4 = st.tabs([
    "Prepare my interview",
    "Mock interview",
    "History & guidance",
    "Company & Job Research"
])


# ==========================================
# TAB 1: PREPARE INTERVIEW
# ==========================================

with tab1:

    st.subheader("Build your interview profile")

    col1, col2 = st.columns(2)

    with col1:

        candidate = st.text_input(
            "Candidate name (optional)"
        )

        resume = st.text_area(
            "Paste your resume text",
            height=260,
            placeholder="Paste your resume text here."
        )

    with col2:

        job_title = st.text_input(
            "Target job title"
        )

        company = st.text_input(
            "Company (optional)"
        )

        jd = st.text_area(
            "Paste the job description",
            height=220,
            placeholder="Paste the complete job description here."
        )

        level = st.selectbox(
            "Interview level",
            [
                "Entry-level",
                "Junior",
                "Mid-level",
                "Senior"
            ]
        )

    focus = st.multiselect(
        "Practice focus",
        [
            "HR and behavioural",
            "Role-specific technical",
            "Problem solving",
            "Communication",
            "Situational judgement"
        ],
        default=[
            "HR and behavioural",
            "Role-specific technical"
        ]
    )

    if st.button(
        "Analyse profile and create interview plan",
        type="primary"
    ):

        if not os.getenv("PARALLEL_API_KEY"):

            st.error("Parallel API key is missing.")

        elif not resume.strip() or not jd.strip() or not job_title.strip():

            st.warning(
                "Please provide your resume, job title and job description."
            )

        else:

            try:

                with st.spinner(
                    "Analysing your resume and job description..."
                ):

                    result = analyze_job(
                        resume,
                        jd,
                        job_title,
                        company,
                        level
                    )

                st.session_state.profile = {
                    "candidate": candidate,
                    "resume": resume,
                    "jd": jd,
                    "job_title": job_title,
                    "company": company,
                    "level": level,
                    "focus": focus,
                    "analysis": result
                }

                st.session_state.answers = []
                st.session_state.questions = []
                st.session_state.question_index = 0
                st.session_state.last_feedback = ""
                st.session_state.report = ""

                st.success("Profile analysis completed.")

            except Exception as error:

                st.error("Profile analysis failed.")
                st.exception(error)

    if st.session_state.profile:

        prof = st.session_state.profile

        st.divider()

        st.subheader("Role and resume analysis")

        st.markdown(prof["analysis"])

        if st.button("Generate tailored interview questions"):

            try:

                with st.spinner("Generating interview questions..."):

                    questions = generate_questions(prof)

                st.session_state.questions = questions
                st.session_state.question_index = 0

                st.success(
                    f"Generated {len(questions)} interview questions."
                )

            except Exception as error:

                st.error("Question generation failed.")
                st.exception(error)


# ==========================================
# TAB 2: MOCK INTERVIEW
# ==========================================

with tab2:

    st.subheader("Interactive mock interview")

    if not st.session_state.profile:

        st.info("Complete your profile analysis first.")

    elif not st.session_state.questions:

        st.info(
            "Generate interview questions in the Prepare my interview tab."
        )

    else:

        questions = st.session_state.questions

        idx = min(
            st.session_state.question_index,
            len(questions) - 1
        )

        current_question = questions[idx]

        st.progress(
            (idx + 1) / len(questions),
            text=f"Question {idx + 1} of {len(questions)}"
        )

        st.markdown(
            f"### {current_question.get('question', '')}"
        )

        st.caption(
            f"Type: {current_question.get('type', 'General')} | "
            f"Skill: {current_question.get('skill', 'Not specified')}"
        )

        answer = st.text_area(
            "Your answer",
            height=180,
            key=f"answer_{idx}",
            placeholder="Write your interview answer here."
        )

        if st.button(
            "Evaluate my answer",
            type="primary",
            key=f"evaluate_{idx}"
        ):

            if not answer.strip():

                st.warning("Enter your answer first.")

            else:

                try:

                    with st.spinner("Evaluating your answer..."):

                        feedback = evaluate_answer(
                            st.session_state.profile,
                            current_question,
                            answer
                        )

                    record = {
                        "question": current_question["question"],
                        "type": current_question.get("type", ""),
                        "skill": current_question.get("skill", ""),
                        "answer": answer,
                        "feedback": feedback
                    }

                    if len(st.session_state.answers) > idx:

                        st.session_state.answers[idx] = record

                    else:

                        st.session_state.answers.append(record)

                    st.session_state.last_feedback = feedback

                except Exception as error:

                    st.error("Answer evaluation failed.")
                    st.exception(error)

        if (
            st.session_state.last_feedback
            and len(st.session_state.answers) > idx
        ):

            st.divider()

            st.subheader("Answer feedback")

            st.markdown(st.session_state.last_feedback)

        left, right = st.columns(2)

        with left:

            if st.button(
                "Previous question",
                disabled=(idx == 0)
            ):

                st.session_state.question_index -= 1
                st.rerun()

        with right:

            if st.button(
                "Next question",
                disabled=(idx >= len(questions) - 1)
            ):

                st.session_state.question_index += 1
                st.rerun()

        st.divider()

        if st.button("Create interview readiness report"):

            if not st.session_state.answers:

                st.warning(
                    "Evaluate at least one answer first."
                )

            else:

                try:

                    with st.spinner("Preparing your readiness report..."):

                        report = create_readiness_report(
                            st.session_state.profile,
                            st.session_state.answers
                        )

                    st.session_state.report = report

                    save_session(
                        st.session_state.profile,
                        st.session_state.answers,
                        report
                    )

                    st.success("Readiness report created.")

                except Exception as error:

                    st.error("Readiness report failed.")
                    st.exception(error)

        if st.session_state.report:

            st.subheader("Interview readiness report")

            st.markdown(st.session_state.report)


# ==========================================
# TAB 3: HISTORY AND GUIDANCE
# ==========================================

with tab3:

    st.subheader("Previous practice sessions")

    history = load_sessions()

    if history.empty:

        st.info("No saved sessions yet.")

    else:

        st.dataframe(
            history,
            use_container_width=True
        )

        st.download_button(
            "Download session history CSV",
            history.to_csv(index=False).encode("utf-8"),
            "interview_coach_history.csv",
            "text/csv"
        )

    st.divider()

    st.markdown(
        """
### Coaching principles

- Feedback is based on the submitted answer.
- Unsupported experience and achievements are not invented.
- STAR is used for relevant behavioural questions.
- Technical answers are evaluated for reasoning and clarity.
- Suggested improvements must remain truthful.
"""
    )


# ==========================================
# TAB 4: COMPANY AND JOB RESEARCH
# ==========================================

with tab4:

    st.subheader("Company & Job Research")

    st.caption(
        "Research companies, job roles and current industry developments."
    )

    st.info(
        "This feature uses Parallel Responses API independently."
    )

    research_company = st.text_input(
        "Company name",
        placeholder="e.g. Mercor, Turing, Microsoft",
        key="research_company"
    )

    research_job_title = st.text_input(
        "Job title",
        placeholder="e.g. AI Trainer, Hindi AI Trainer",
        key="research_job_title"
    )

    research_jd = st.text_area(
        "Job description (optional)",
        height=180,
        placeholder="Paste the job description here.",
        key="research_jd"
    )

    if st.button(
        "Research company and job",
        type="primary"
    ):

        if not os.getenv("PARALLEL_API_KEY"):

            st.error("Parallel API key is missing.")

        elif not research_company.strip() and not research_job_title.strip():

            st.warning(
                "Enter a company name or job title."
            )

        else:

            try:

                with st.spinner(
                    "Researching company and job information..."
                ):

                    result = research_company_and_role(
                        company=research_company.strip() or "Not specified",
                        job_title=research_job_title.strip() or "Not specified",
                        job_description=research_jd.strip()
                    )

                st.session_state.parallel_research_result = result

                st.success("Research completed successfully.")

            except Exception as error:

                st.error("Research request failed.")
                st.exception(error)

    if st.session_state.parallel_research_result:

        st.divider()

        st.subheader("Research Report")

        st.markdown(
            st.session_state.parallel_research_result
        )

        st.download_button(
            "Download research report",
            data=st.session_state.parallel_research_result,
            file_name="company_job_research.txt",
            mime="text/plain"
        )
