# JobGuard 🛡️

A tool I built after nearly wasting a week on a fake "AI/ML job assignment" that
turned out to be a scam pattern — asking me to build a full real-time trading
system and connect my personal broker/demat account, disguised as a technical
round.

I got suspicious, checked the company's registration status (turned out to be
struck off from the MCA registry), and realized I'd been manually running the
same checklist of red flags for every job posting I got. So I automated it.

**JobGuard does two things when you paste a job posting:**

1. **Skill-match score** — TF-IDF cosine similarity between the posting and
   your skill set, so you know at a glance whether a role is actually worth
   your time to apply to.
2. **Scam-risk score** — a weighted rule-based checker for the red flags I
   personally ran into: requests for broker/trading account access, real-money
   references, deliverables scoped like a full production system instead of a
   test task, unrealistic one-week deadlines for huge scope, screen-recorded
   demos, API key/secret handling, unpaid-work language, and free-email-domain
   contacts.

## Why I built it this way

Same TF-IDF approach as my Spam Email Detector project — turns out spam
filtering and scam-job filtering are the same underlying problem: is this text
statistically similar to known-bad patterns? The rule weights came directly
from analyzing the actual scam posting I received.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (free, Streamlit Community Cloud)

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), connect your GitHub,
   and point it at `app.py`.
3. Done — you get a public URL.

## Tech

- Python, Streamlit
- scikit-learn (TF-IDF + cosine similarity)
- Rule-based scam heuristics (regex pattern matching, weighted scoring)

## Ideas for next iteration

- Save/compare multiple postings over time
- Pull company registration status automatically (MCA API)
- Browser extension version so it works directly on LinkedIn/Naukri listings
