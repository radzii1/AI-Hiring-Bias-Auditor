# AI Hiring Bias Auditor

An AI-powered tool that analyses job descriptions for hidden language 
bias and automatically rewrites them to be more inclusive.

## What it does

Paste any job description and the tool will:
- Score it across 5 bias dimensions (0–10)
- Flag the exact phrases causing bias
- Automatically rewrite it in inclusive language

## Bias dimensions analysed

| Dimension | What it catches |
|-----------|----------------|
| Gender | Masculine/feminine coded words like "rockstar", "ninja", "guy" |
| Age | "Digital native", "young and hungry", "recent graduate" |
| Disability | Requirements not relevant to the job, no accommodation mention |
| Cultural | "Native English speaker", "culture fit", Western-centric language |
| Socioeconomic | "Prestigious university", "own transport required" |

## Why this matters

Research shows biased job description language reduces applications 
from women by up to 40%, deters older candidates, and excludes 
people from non-Western backgrounds — before a single person is 
even interviewed.

## Built with

- Python
- OpenAI GPT-4o API
- Streamlit
- Deployed on Streamlit Community Cloud

## How to run locally

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Add your OpenAI API key to `.streamlit/secrets.toml`:
