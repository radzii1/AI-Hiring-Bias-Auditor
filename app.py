
import streamlit as st
from openai import OpenAI
import json

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SYSTEM_PROMPT = """You are an expert in inclusive hiring practices and linguistic bias analysis.
Audit job descriptions for hidden bias across five dimensions: gender, age, disability, cultural, socioeconomic.

Scoring rubric (0-10):
0-2: Clean. 3-5: Moderate. 6-8: High. 9-10: Severe.

Only flag phrases that actually appear in the text. Quote them exactly.
Return your response as valid JSON only."""

def audit_jd(jd_text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Audit this job description and return JSON:\n\n{jd_text}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    return json.loads(response.choices[0].message.content)

def rewrite_jd(jd_text, audit_result):
    issues = []
    for dimension, data in audit_result.items():
        if data["score"] >= 5:
            phrases = ", ".join([f'"{p}"' for p in data["flagged_phrases"]])
            issues.append(f"- {dimension}: fix these phrases: {phrases}")
    issues_text = "\n".join(issues)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """You rewrite job descriptions to be inclusive and bias-free.
Rules:
- Keep all the actual job requirements intact
- Only fix the language, not the substance
- Don't make it bland — keep it engaging
- Return only the rewritten JD, nothing else"""},
            {"role": "user", "content": f"""Rewrite this job description to fix all bias issues.

ORIGINAL JD:
{jd_text}

ISSUES TO FIX:
{issues_text}

Return only the rewritten JD."""}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

# ── UI ──
st.set_page_config(page_title="AI Hiring Bias Auditor", page_icon="🔍")

st.title("🔍 AI Hiring Bias Auditor")
st.write("Paste any job description below to detect hidden bias and get an inclusive rewrite.")

jd_input = st.text_area("Paste job description here", height=300, placeholder="Paste your job description...")

if st.button("Audit this JD"):
    if not jd_input.strip():
        st.warning("Please paste a job description first.")
    else:
        with st.spinner("Analysing for bias..."):
            result = audit_jd(jd_input)

        st.subheader("Bias Scores")
        cols = st.columns(5)
        dimensions = list(result.keys())
        for i, dim in enumerate(dimensions):
            score = result[dim]["score"]
            if score <= 2:
                color = "🟢"
            elif score <= 5:
                color = "🟡"
            else:
                color = "🔴"
            cols[i].metric(label=dim.replace("_", " ").title(), value=f"{color} {score}/10")

        st.subheader("Flagged Phrases")
        for dim, data in result.items():
            if data["flagged_phrases"]:
                st.markdown(f"**{dim.replace('_', ' ').title()}** (score: {data['score']}/10)")
                for phrase in data["flagged_phrases"]:
                    st.markdown(f"- ⚠️ *\"{phrase}\"*")

        st.subheader("Inclusive Rewrite")
        with st.spinner("Rewriting..."):
            rewritten = rewrite_jd(jd_input, result)
        st.text_area("Rewritten JD", value=rewritten, height=300)
        st.success("Done! Copy the rewritten JD above.")
