
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load credentials from the .env file
load_dotenv()

def research_company_and_role(company, job_title, job_description=""):
    """
    Research a company and job role using Parallel Responses API.
    Returns a web-researched answer with citations.
    """

    api_key = os.getenv("PARALLEL_API_KEY")

    if not api_key:
        raise RuntimeError(
            "Parallel API key is missing. Check your .env file."
        )

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.parallel.ai/v1",
        timeout=90.0
    )

    prompt = f"""
You are a professional career research assistant.

Research the following company and job opportunity using
reliable and current web sources.

Company: {company}
Job title: {job_title}

Job description:
{job_description}

Provide a structured report covering:

1. Company overview and main business activities.
2. Products, services and industry.
3. Recent relevant developments.
4. Skills and responsibilities likely to matter in this role.
5. Five relevant interview topics or questions.
6. Useful facts the candidate should know before the interview.

Use factual information, distinguish confirmed facts from
reasonable role-based suggestions, and include source citations.
If information cannot be verified, say so.
"""

    try:
        response = client.responses.create(
            model=os.getenv("PARALLEL_MODEL", "parallel"),
            input=prompt,
            reasoning={"effort": "low"}
        )

        return response.output_text

    except Exception as error:
        raise RuntimeError(
            f"Parallel research request failed: {error}"
        ) from error

    finally:
        client.close()
