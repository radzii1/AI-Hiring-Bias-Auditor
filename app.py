
import streamlit as st
from openai import OpenAI
import json

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SYSTEM_PROMPT = """You are an expert in inclusive hiring practices and linguistic bias analysis.
Audit job descriptions for hidden bias across five dimensions: gender, age, disability, cultural, socioeconomic.

Scoring rubric (0-10):
0-2: Clean. 3-5: Moderate. 6-8: High. 9-10: Severe.

For each dimension return:
- score (0-10)
- flagged_phrases (list of exact phrases from the text)
- explanations (list of strings explaining why each phrase is biased, one per flagged phrase)
- suggestion (one sentence on how to improve this dimension)

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
        if data["score"] >= 3:
            phrases = ", ".join([f'"{p}"' for p in data["flagged_phrases"]])
            issues.append(f"- {dimension}: fix these phrases: {phrases}")
    issues_text = "\n".join(issues) if issues else "No major issues found."

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """You rewrite job descriptions to be inclusive and bias-free.
Rules:
- Keep all actual job requirements intact
- Only fix the language, not the substance
- Keep it engaging and professional
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

def get_overall_score(result):
    scores = [data["score"] for data in result.values()]
    return round(sum(scores) / len(scores))

def score_color(score):
    if score <= 2:
        return "🟢", "#1D9E75", "Low bias"
    elif score <= 5:
        return "🟡", "#BA7517", "Moderate bias"
    else:
        return "🔴", "#A32D2D", "High bias"

# ── PAGE CONFIG ──
st.set_page_config(page_title="AI Hiring Bias Auditor", page_icon="🔍", layout="wide")

st.title("🔍 AI Hiring Bias Auditor")
st.write("Paste any job description to detect hidden bias and get an inclusive rewrite — powered by GPT-4o.")

st.divider()

jd_input = st.text_area("Paste job description here", height=250, placeholder="Paste your job description...")

if st.button("Audit this JD", type="primary", use_container_width=True):
    if not jd_input.strip():
        st.warning("Please paste a job description first.")
    else:
        with st.spinner("Analysing for bias..."):
            result = audit_jd(jd_input)

        # ── OVERALL SCORE ──
        overall = get_overall_score(result)
        emoji, color, label = score_color(overall)
        st.divider()
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown(f"""
            <div style='text-align:center; padding: 20px; border-radius: 12px; border: 2px solid {color};'>
                <div style='font-size: 48px;'>{emoji}</div>
                <div style='font-size: 36px; font-weight: bold; color: {color};'>{overall}/10</div>
                <div style='font-size: 18px; color: {color};'>{label}</div>
                <div style='font-size: 14px; color: gray; margin-top: 4px;'>Overall Bias Score</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # ── DIMENSION SCORES ──
        st.subheader("Breakdown by dimension")
        cols = st.columns(5)
        for i, (dim, data) in enumerate(result.items()):
            score = data["score"]
            emoji, color, label = score_color(score)
            cols[i].markdown(f"""
            <div style='text-align:center; padding:12px; border-radius:8px; border: 1px solid {color};'>
                <div style='font-size:22px;'>{emoji}</div>
                <div style='font-weight:500; font-size:15px;'>{score}/10</div>
                <div style='font-size:12px; color:gray;'>{dim.replace("_"," ").title()}</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # ── FLAGGED PHRASES WITH EXPLANATIONS ──
        st.subheader("Flagged phrases")
        has_flags = False
        for dim, data in result.items():
            if data["flagged_phrases"]:
                has_flags = True
                emoji, color, _ = score_color(data["score"])
                with st.expander(f"{emoji} {dim.replace('_',' ').title()} — {data['score']}/10  |  {data.get('suggestion','')}"):
                    for j, phrase in enumerate(data["flagged_phrases"]):
                        explanation = data.get("explanations", [])[j] if j < len(data.get("explanations", [])) else ""
                        st.markdown(f"**⚠️ \"{phrase}\"**")
                        if explanation:
                            st.markdown(f"*{explanation}*")
                        st.markdown("---")
        if not has_flags:
            st.success("No significant bias detected in this job description!")

        st.divider()

        # ── SIDE BY SIDE REWRITE ──
        st.subheader("Original vs Inclusive Rewrite")
        with st.spinner("Generating inclusive rewrite..."):
            rewritten = rewrite_jd(jd_input, result)

        col_orig, col_new = st.columns(2)
        with col_orig:
            st.markdown("**Original**")
            st.text_area("", value=jd_input, height=400, disabled=True, label_visibility="collapsed")
        with col_new:
            st.markdown("**Inclusive Rewrite**")
            st.text_area("", value=rewritten, height=400, label_visibility="collapsed")
            st.button("📋 Copy rewrite", on_click=lambda: st.write("Copied!"))

        st.success("✅ Audit complete. Copy the rewritten JD on the right.")
