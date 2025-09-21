import streamlit as st
import pandas as pd
import datetime, json, os
from notebook_gen import generate_notebook, safe_filename

st.set_page_config(page_title="MindMate.AI (Prototype)", layout="wide")

# Simple lexicon-based sentiment + red-flag detector
NEG_WORDS = set(["stressed","anxious","anxiety","depressed","depressed","sad","suicide","suicidal","hurt","kill myself","dont want to live","overwhelmed","hopeless"])
POS_WORDS = set(["happy","good","well","great","relieved","better","ok","okay","fine","improved"])
REDFLAG_PATTERNS = ["i want to die","i don't want to live","i want to kill myself","i will kill myself","i want to hurt myself","i want to end it all","suicide","kill myself","dont want to live"]

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
LOG_CSV = os.path.join(DATA_DIR, "mood_logs.csv")

def analyze_text(text):
    tx = text.lower()
    score = 0
    for w in NEG_WORDS:
        if w in tx:
            score -= 1
    for w in POS_WORDS:
        if w in tx:
            score += 1
    label = "neutral"
    if score < 0:
        label = "negative"
    elif score > 0:
        label = "positive"
    # red-flag detection (high priority)
    for p in REDFLAG_PATTERNS:
        if p in tx:
            return "red_flag", "If you are in immediate danger, please contact local emergency services or a crisis hotline. Here are some resources: https://www.opencounseling.com/suicide-hotlines", True
    # empathy reply (simple)
    if label == "negative":
        reply = "I'm sorry you're feeling this way. Would you like a quick grounding exercise or a breathing tip?"
    elif label == "positive":
        reply = "That's great to hear — keep it up!"
    else:
        reply = "Thanks for sharing — do you want to tell me more?"
    return label, reply, False

st.title("MindMate.AI — Prototype (Streamlit)")
st.markdown("Privacy-first, local demo. This prototype demonstrates: empathetic chat, mood detection, red-flag alerts, and notebook generation.")

col1, col2 = st.columns([2,1])

with col1:
    st.header("Check-in Chat")
    user_input = st.text_area("How are you feeling? Type your check-in here:", height=120)
    if st.button("Check in"):
        if not user_input.strip():
            st.warning("Please type something.")
        else:
            label, reply, is_red = analyze_text(user_input)
            st.subheader("Detected mood: " + label)
            if is_red:
                st.error("RED FLAG detected! " + reply)
            else:
                st.info(reply)
            # Save to local CSV
            entry = {"timestamp": datetime.datetime.utcnow().isoformat(), "text": user_input, "label": label}
            if os.path.exists(LOG_CSV):
                df = pd.read_csv(LOG_CSV)
                df = df.append(entry, ignore_index=True)
            else:
                df = pd.DataFrame([entry])
            df.to_csv(LOG_CSV, index=False)
            st.success("Saved locally to " + LOG_CSV)

    st.markdown("---")
    st.header("Export & Notebook")
    title = st.text_input("Project name (for notebook):", "student_stress_demo")
    if st.button("Generate starter notebook"):
        fname = safe_filename(title) + ".ipynb"
        nb_path = os.path.join(DATA_DIR, fname)
        generate_notebook(nb_path, title, LOG_CSV if os.path.exists(LOG_CSV) else None)
        st.success("Notebook generated: " + nb_path)
        st.markdown(f"[Download notebook]({nb_path})")

with col2:
    st.header("Mood Dashboard (local)")
    if os.path.exists(LOG_CSV):
        df = pd.read_csv(LOG_CSV)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        st.write("Recent entries:")
        st.dataframe(df.tail(20))
        # simple trend count
        counts = df.groupby('label').size().to_dict()
        st.write("Label counts:", counts)
        st.line_chart(df['label'].map(lambda x: {'negative':-1,'neutral':0,'positive':1}.get(x,0)))
        if st.button("Export logs as CSV"):
            st.download_button("Download CSV", data=open(LOG_CSV,"rb").read(), file_name="mood_logs.csv")
    else:
        st.info("No logs yet. Do a check-in to generate local logs.")

st.markdown("---")
st.markdown("**Safety notice:** This prototype is NOT a substitute for professional care. For emergencies, contact local services.")
