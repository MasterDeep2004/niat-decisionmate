# NIAT DecisionMate — Layer 3 Prototype

A small AI-assisted lead-to-counselling prototype for the NxtWave Growth Hack Challenge.

## What it demonstrates
1. Captures a prospective student's goal and main concern.
2. Uses Gemini to create a family-friendly decision brief.
3. Saves the lead and brief to Supabase when configured.
4. Prepares a WhatsApp follow-up draft for human review. It never sends messages automatically.

This is a challenge prototype, not an official NIAT admissions service. It does not confirm programme facts, eligibility, fees, scholarships, placements or admission outcomes.

## Run locally
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Configure API keys
Create `.streamlit/secrets.toml` locally (do not commit it):
```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_SUPABASE_SERVICE_ROLE_KEY"
```

For Streamlit Community Cloud, open the app's Settings → Secrets and add the same values there.

Get a Gemini key at https://aistudio.google.com/apikey.
Create a Supabase project at https://supabase.com, open SQL Editor, and run `supabase_schema.sql`.

## Deploy on Streamlit Community Cloud
1. Create a GitHub repository and upload `app.py`, `requirements.txt`, and `supabase_schema.sql`.
2. Go to https://share.streamlit.io/ and sign in with GitHub.
3. Choose **Create app**, select your repository and branch, and set the main file to `app.py`.
4. Open **Advanced settings / Secrets** and add the API credentials. Never put keys in the repository.
5. Deploy, then test with fictional details only.
6. Copy the deployed `*.streamlit.app` URL for the Layer 3 field.

## Demo checklist
- Enter fictional student details.
- Generate a brief and check that unknown facts are referred to a counsellor.
- Confirm the WhatsApp draft opens for review and is not auto-sent.
- If Supabase is connected, confirm the lead row is saved.
- Do not use real student personal data in the challenge demo.

## Security notes
- Do not commit API keys, `.env`, or `secrets.toml`.
- The Supabase service-role key bypasses Row Level Security. Keep it only in Streamlit server-side Secrets.
- This prototype does not implement user authentication or production-grade access control. Do not use it with real student records.
