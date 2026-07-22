import os
import json
from openai import OpenAI

# Read API key from environment variable
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def analyze_resume(resume_text):

    prompt = f"""
You are an expert HR recruiter.

Analyze the following resume.

Return ONLY JSON.

Format:

{{
    "summary":"",
    "skills":[],
    "domain":"",
    "strengths":[],
    "weaknesses":[],
    "missing_skills":[],
    "recommended_roles":[]
}}

Resume:

{resume_text}

"""

    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.3

    )

    return json.loads(response.choices[0].message.content)