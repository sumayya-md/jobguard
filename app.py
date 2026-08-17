"""
JobGuard — Skill-Match & Scam-Risk Checker for Job Postings
Paste any job posting. Get: (1) how well it matches your skills, and
(2) whether it shows red flags of a fake/exploitative "assignment" scam.

Built after personally running into a fake "AI/ML assignment" job posting
that asked for a full production trading system + broker account access
disguised as a technical round. This tool automates the checks I did by hand.
"""

import streamlit as st
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="JobGuard", page_icon="🛡️", layout="wide")

DEFAULT_SKILLS = """Python, SQL, Java, JavaScript, HTML, CSS, TensorFlow, PyTorch,
Scikit-learn, Pandas, NumPy, Matplotlib, Seaborn, Streamlit, Node.js, Express.js,
Machine Learning, Deep Learning, Natural Language Processing, Computer Vision,
CNN, Transfer Learning, XGBoost, Random Forest, LightGBM, TF-IDF, Naive Bayes,
LangChain, Gemini API, ChromaDB, RAG, Prompt Engineering, Data Preprocessing,
Model Evaluation, Git, GitHub, Jupyter Notebook, AWS, Data Analysis"""

# ---------- Scam red-flag rules ----------
# Each rule: (pattern(s), weight, human-readable reason)
RED_FLAGS = [
    (r"broker\s+account|demat\s+account|trading\s+account|live\s+broker",
     25, "Asks you to connect a personal broker/trading/demat account"),
    (r"real[- ]?money|real\s+funds|invest\s+your\s+own",
     20, "References real money / personal funds"),
    (r"working\s+\.?exe|deliver.{0,20}\.exe|production[- ]ready\s+system",
     15, "Wants a full production-ready deliverable (.exe / shipped system), not a scoped task"),
    (r"within\s+(one|1|two|2)\s+week|complete.{0,15}within\s+\d+\s+days?",
     10, "Very large scope compressed into a very short deadline"),
    (r"screen[- ]?recording|screen\s+record.{0,20}demonstrat",
     8, "Requires a full screen-recorded demo — unusual for a scoped take-home test"),
    (r"api\s+keys?.{0,30}(remove|mask|delete)|totp\s+secret|access\s+token",
     15, "Explicitly discusses handling API keys / TOTP secrets / access tokens"),
    (r"no\s+payment|unpaid|without\s+compensation",
     10, "Explicitly unpaid work"),
    (r"dashboard.{0,20}(live|real-?time)|real-?time\s+data\s+collection",
     8, "Requests a full live/real-time dashboard build"),
    (r"trained\s+model\s+files|collected\s+data\s+and\s+trained",
     10, "Wants your trained models and collected datasets handed over"),
    (r"gmail\.com|yahoo\.com|outlook\.com",
     12, "Contact email uses a free personal email domain instead of a company domain"),
]

SCOPE_WORDS = [
    "real-time", "live dashboard", "complete python source code",
    "working .exe", "trained model files", "performance report",
    "screen-recording", "next-day validation", "multiple models",
    "full deliverable", "production system"
]


def clean_text(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip()


def compute_skill_match(job_text: str, skills_text: str):
    skills_list = [s.strip() for s in re.split(r"[,\n]", skills_text) if s.strip()]
    job_lower = job_text.lower()

    matched = [s for s in skills_list if s.lower() in job_lower]
    missing_hint = [s for s in skills_list if s.lower() not in job_lower]

    # TF-IDF cosine similarity between job posting and your skills blob
    docs = [job_text, ", ".join(skills_list)]
    try:
        vec = TfidfVectorizer(stop_words="english")
        tfidf = vec.fit_transform(docs)
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    except ValueError:
        sim = 0.0

    score = round(sim * 100, 1)
    return score, matched, missing_hint[:8]


def compute_scam_risk(job_text: str):
    job_lower = job_text.lower()
    total = 0
    reasons = []
    for pattern, weight, reason in RED_FLAGS:
        if re.search(pattern, job_lower):
            total += weight
            reasons.append((weight, reason))

    scope_hits = sum(1 for w in SCOPE_WORDS if w in job_lower)
    if scope_hits >= 4:
        pts = min(20, scope_hits * 3)
        total += pts
        reasons.append((pts, f"Posting stacks {scope_hits} large-scope deliverables for a single 'assignment'"))

    total = min(total, 100)
    reasons.sort(key=lambda x: -x[0])
    return total, reasons


def risk_label(score):
    if score >= 50:
        return "🔴 High risk", "#d9534f"
    elif score >= 25:
        return "🟠 Medium risk", "#f0ad4e"
    else:
        return "🟢 Low risk", "#5cb85c"


# ---------- UI ----------
st.title("🛡️ JobGuard")
st.caption("Paste a job posting → get a skill-match score against your resume, and a scam-risk score with reasons.")

with st.sidebar:
    st.header("Your skills")
    skills_text = st.text_area("Comma-separated skills (edit to match your resume)",
                                value=DEFAULT_SKILLS, height=220)
    st.caption("Defaults are pre-filled from a sample AI/ML fresher resume — edit freely.")

job_text = st.text_area("Paste the job posting / assignment text here", height=280,
                         placeholder="Paste the full job description or assignment email...")

col1, col2 = st.columns(2)
run = st.button("🔍 Analyze posting", type="primary", use_container_width=True)

if run:
    if not job_text.strip():
        st.warning("Paste a job posting first.")
    else:
        job_text_clean = clean_text(job_text)
        match_score, matched, missing = compute_skill_match(job_text_clean, skills_text)
        risk_score, reasons = compute_scam_risk(job_text_clean)
        label, color = risk_label(risk_score)

        with col1:
            st.subheader("Skill Match")
            st.metric("Match score", f"{match_score}%")
            st.progress(min(int(match_score), 100))
            if matched:
                st.write("**Matched skills found in posting:**")
                st.write(", ".join(matched))
            else:
                st.write("No direct skill keyword overlap found — read the posting carefully.")

        with col2:
            st.subheader("Scam Risk")
            st.markdown(f"### {label}  ·  {risk_score}/100")
            st.progress(min(int(risk_score), 100))
            if reasons:
                st.write("**Why:**")
                for weight, reason in reasons:
                    st.write(f"- {reason}  _(+{weight})_")
            else:
                st.write("No major red flags detected — still verify the company independently.")

        st.divider()
        st.info(
            "This is a heuristic screening tool, not a verdict. Always independently verify "
            "a company (MCA registry, LinkedIn presence, Glassdoor) before sharing personal "
            "credentials or doing unpaid work.")

st.divider()
st.caption("Built by Mohammed Sumayya Bint Ansari · github.com/[your-username]/jobguard")
