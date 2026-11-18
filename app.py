import os
import json
import streamlit as st
from google import genai
from supabase import create_client, Client

st.set_page_config(page_title="NIAT DecisionMate", page_icon="🎓", layout="centered")

st.title("NIAT DecisionMate")
st.caption("A student-first enquiry experience that helps families prepare for a useful counselling conversation.")

st.info(
    "Prototype for the NxtWave Growth Hack Challenge. This is not an official NIAT admissions service. "
    "It does not provide admission decisions, fee quotes, placement promises or eligibility confirmation."
)

def get_secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name, default)
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv(name, default)

def get_gemini_client():
    key = get_secret("GEMINI_API_KEY")
    if not key:
        return None
    return genai.Client(api_key=key)

def get_supabase_client():
    url = get_secret("SUPABASE_URL")
    key = get_secret("SUPABASE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)

with st.form("lead_form"):
    st.subheader("Tell us what you are trying to figure out")
    student_name = st.text_input("Your first name")
    city = st.text_input("Your city")
    interest = st.text_input("What are you interested in studying or learning?")
    goal = st.text_area("What are you hoping to achieve?", placeholder="For example: build practical tech skills, explore a career path, understand the programme...")
    concern = st.selectbox(
        "What is your biggest question right now?",
        [
            "I want to understand the programme better",
            "I am unsure whether this is right for me",
            "My parent/family needs more information",
            "I want to understand fees and affordability",
            "I want to understand career outcomes",
            "I am comparing different options",
            "Something else"
        ]
    )
    other_concern = ""
    if concern == "Something else":
        other_concern = st.text_input("Tell us your question")
    family_involvement = st.radio(
        "Who is part of this decision?",
        ["Mainly me", "Me and my parent/family", "My parent/family is researching first"],
        horizontal=False
    )
    language = st.selectbox("Preferred language for the brief", ["English", "Hindi", "Bengali"])
    consent = st.checkbox(
        "I understand this is a challenge prototype and agree to use these details to generate this brief."
    )
    submitted = st.form_submit_button("Create my decision brief", type="primary", use_container_width=True)

if submitted:
    if not student_name.strip() or not interest.strip() or not goal.strip():
        st.error("Please add your first name, area of interest and goal.")
    elif not consent:
        st.warning("Please confirm the consent checkbox to continue.")
    else:
        actual_concern = other_concern.strip() if concern == "Something else" else concern
        lead = {
            "student_name": student_name.strip(),
            "city": city.strip(),
            "interest": interest.strip(),
            "goal": goal.strip(),
            "concern": actual_concern,
            "family_involvement": family_involvement,
            "language": language,
        }

        client = get_gemini_client()
        if client is None:
            st.error("The AI service is not configured yet. Add GEMINI_API_KEY in Streamlit Secrets and redeploy.")
        else:
            prompt = f"""
You are helping create a neutral preparation brief for a prospective student and their family.
Use the user's information below. Do not claim to represent NIAT or make admissions decisions.
Do not invent programme facts, fees, scholarships, eligibility rules, partner-university details,
placement statistics, salaries, guarantees, deadlines or campus information. No external facts have
been provided, so do not state any such facts. If the user asks about these topics, clearly say
"Please confirm this directly with an authorised NIAT counsellor."
Write in {language}, in a warm, clear, natural tone. Avoid sales pressure.

Student context:
{json.dumps(lead, ensure_ascii=False)}

Return these sections:
1. "What I am looking for" — summarise the student's goal in 2-3 sentences.
2. "Questions worth discussing" — give 4 specific questions based on their concern.
3. "For my family" — a short paragraph they can share with a parent/family member.
4. "What to confirm with a counsellor" — list facts that should be verified directly.
5. "Suggested next step" — invite them to have a conversation; do not imply urgency or guarantee outcomes.
Keep the full brief concise (around 250-350 words).
"""
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                brief = response.text or "The AI response was empty. Please try again."
                st.session_state["decision_brief"] = brief
                st.session_state["lead_data"] = lead

                supabase = get_supabase_client()
                if supabase:
                    try:
                        supabase.table("leads").insert({
                            **lead,
                            "decision_brief": brief,
                            "stage": "New"
                        }).execute()
                        st.session_state["saved_to_db"] = True
                    except Exception as db_error:
                        st.session_state["saved_to_db"] = False
                        st.session_state["db_error"] = str(db_error)
                else:
                    st.session_state["saved_to_db"] = False
            except Exception as error:
                st.error(f"Could not generate the brief: {error}")

if "decision_brief" in st.session_state:
    st.divider()
    st.subheader("Your decision brief")
    st.markdown(st.session_state["decision_brief"])
    st.download_button(
        "Download brief as text",
        data=st.session_state["decision_brief"],
        file_name="niat_decision_brief.txt",
        mime="text/plain",
        use_container_width=True
    )

    lead = st.session_state.get("lead_data", {})
    follow_up = (
        f"Hi, I have been exploring my options and would like to understand the programme better. "
        f"My main interest is {lead.get('interest', 'the programme')}. "
        f"My biggest question is: {lead.get('concern', 'understanding the programme')}. "
        f"Could we schedule a conversation to clarify this?"
    )
    st.subheader("Suggested WhatsApp follow-up")
    st.caption("Review and edit this message before sending. The prototype does not send messages automatically.")
    st.text_area("Message draft", value=follow_up, height=120)
    wa_url = "https://wa.me/?text=" + __import__("urllib.parse").parse.quote(follow_up)
    st.markdown(f"[Open WhatsApp with this draft]({wa_url})")

    if st.session_state.get("saved_to_db"):
        st.success("Lead and brief saved to the connected Supabase table.")
    else:
        st.caption("Database storage is not connected. The brief was generated in this session only.")

st.divider()
st.subheader("For the counselling team")
st.write(
    "The intended workflow is: review the student's concern, use the brief to prepare a more relevant conversation, "
    "update the lead stage in the CRM, and confirm any programme-specific facts directly."
)
st.caption("Prototype only. Do not enter sensitive personal information or real student records.")
