import streamlit as st
import openai
import tempfile
import cv2
import yt_dlp
from pathlib import Path
from PIL import Image
import base64
import mediapipe as mp
import time
import math
from fpdf import FPDF
import unicodedata

# ===== Inject External CSS =====
with open("style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 1. Load API Key
api_key_path = Path("C:/Users/manne/OneDrive/Desktop/CoachlessAI/openai_key.txt")
if not api_key_path.exists():
    st.error("API key file not found. Ensure openai_key.txt exists in the specified path.")
    st.stop()
openai.api_key = api_key_path.read_text().strip()

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)
mp_draw = mp.solutions.drawing_utils

st.set_page_config(page_title="CoachlessAI Video Coach", layout="wide")
st.markdown("<h1 style='text-align: center; color: #b20000;'>COACHLESSAI</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #b20000;'>AI Video Form Analyzer</h3>", unsafe_allow_html=True)

SPORTS = ["Football", "Cricket", "Rugby", "Tennis", "Athletics"]
SPORT_OPTIONS = {
    "Football": {"Roles": ["Attacking Midfielder", "Defender", "Goalkeeper", "Striker", "Winger"],
                 "Skills": {"Attacking Midfielder": ["Creative passing", "Through balls"],
                             "Defender": ["1-on-1 defending", "Heading", "Interceptions"],
                             "Goalkeeper": ["Distribution", "Positioning", "Shot-stopping"],
                             "Striker": ["Finishing", "Off-the-ball runs", "Positioning"],
                             "Winger": ["Crossing", "Cutting inside", "Dribbling"]}},
    "Cricket": {"Disciplines": ["Batting", "Bowling", "Fielding"],
                 "Skills": {"Batting": ["Cover drive", "Hook", "Pull shot", "Reverse sweep", "Straight drive"],
                             "Bowling": ["Leg-spin", "Off-spin", "Pace", "Swing"],
                             "Fielding": ["Ground fielding", "Slip catching", "Wicketkeeping"]}},
    "Rugby": {"Positions": ["Backs", "Forwards"],
               "Skills": {"Backs": ["Defensive reads", "Kicking", "Passing accuracy"],
                          "Forwards": ["Line-out throwing", "Scrum technique", "Tackling"]}},
    "Tennis": {"Aspects": ["Groundstroke", "Return", "Serve", "Volley"],
                "Skills": {"Groundstroke": ["Backhand", "Forehand"],
                           "Return": ["Block return", "Drive return"],
                           "Serve": ["Flat serve", "Kick serve", "Slice serve"],
                           "Volley": ["Drop volley", "Half-volley"]}},
    "Athletics": {"Categories": ["Combined", "Field", "Road & Cross-Country", "Track"],
                   "Events": {"Combined": ["Decathlon", "Heptathlon"],
                              "Field": ["High Jump", "Javelin", "Long Jump", "Shot Put"],
                              "Road & Cross-Country": ["5K", "10K", "Marathon"],
                              "Track": ["100m", "200m", "400m", "Hurdles", "Relay"]}}
}

from prompts import DEFAULT_PROMPTS

def normalize_text(txt: str) -> str:
    nfkd = unicodedata.normalize("NFKD", txt)
    return nfkd.encode("latin-1", "ignore").decode("latin-1")

def generate_pdf(summary, flagged, sport, category, sub, goal, concerns):
    pdf = FPDF()
    pdf.set_auto_page_break(True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, normalize_text("CoachlessAI Feedback Report"), ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    header = (
        f"Sport: {sport} | Category: {category} | Focus: {sub}\n"
        f"Goal: {goal}\nConcerns: {concerns}\n\n"
    )
    pdf.multi_cell(0, 10, normalize_text(header))
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, normalize_text("Summary"), ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, normalize_text(summary))
    for i, (fp, cm) in enumerate(flagged, start=1):
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, normalize_text(f"Frame {i} Feedback"), ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, normalize_text(cm))
        try:
            pdf.image(str(fp), x=10, w=pdf.w - 20)
        except:
            pass
    out = Path(tempfile.gettempdir()) / "CoachlessAI_Report.pdf"
    pdf.output(str(out))
    return out

def extract_frames(path, s, e, sample_n=50, select_n=20):
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    start_f, end_f = int(s*fps), int(e*fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_f)
    step = max((end_f-start_f)//sample_n, 1)
    sampled, lms = [], []
    idx = count = 0
    while count < sample_n and cap.get(cv2.CAP_PROP_POS_FRAMES) < end_f:
        ret, frame = cap.read()
        idx += 1
        if not ret: break
        if idx % step == 0:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = pose.process(rgb)
            lm = []
            if res.pose_landmarks:
                for p in res.pose_landmarks.landmark:
                    lm.append((p.x, p.y, p.z))
                mp_draw.draw_landmarks(rgb, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            fp = Path(tempfile.gettempdir()) / f"frame_{count}.jpg"
            Image.fromarray(rgb).save(fp)
            sampled.append(fp); lms.append(lm); count += 1
    cap.release()
    scores=[]
    for i in range(1, len(lms)):
        d = sum(math.dist(lms[i-1][j], lms[i][j]) for j in range(len(lms[i-1]))) if lms[i-1] and lms[i] else 0
        scores.append((i,d))
    top = sorted(scores, key=lambda x:-x[1])[:select_n]
    idxs = sorted(i for i,_ in top)
    return [sampled[i] for i in idxs]

def run_analysis(frames, sport, category, sub, goal_text, concerns):
    notes, flagged = [], []
    action_status = st.empty()
    progress_bar = st.progress(0)
    for i, fp in enumerate(frames, start=1):
        pct = int(i/len(frames)*100)
        action_status.text(f"Analyzing {i}/{len(frames)}...")
        progress_bar.progress(pct)
        img_b64 = base64.b64encode(fp.read_bytes()).decode()
        msgs=[
            {
                "role":"system",
                "content":
                    "You are an elite, world-class technical sports coach. "
                    "Be ultra-specific, objective, and never generic. "
                    "If you spot technical errors or bad form, critique them directly and explain why they're a problem. "
                    "If a frame shows exceptional/elite form, say what exactly is world-class about it, otherwise be bluntly honest. "
                    "Never use generic praise. Always provide highly actionable, technical feedback."
            },
            {
                "role":"user",
                "content":[
                    {"type":"text",
                     "text":f"Sport:{sport} | Category:{category} | Focus:{sub}\n"
                            f"User Goal: {goal_text}\n"
                            f"User Concerns: {concerns}\n"
                            "Analyze the athlete's technique, body alignment, movement quality, and effort in this frame. "
                            "If any aspect of form is exceptional or broken, explain why. "
                            "List practical, specific improvements—no vague statements."
                    },
                    {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img_b64}"}}
                ]
            }
        ]
        try:
            res = openai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=350, temperature=0.25)
            fb = res.choices[0].message.content.strip()
        except Exception as e:
            fb = None
        if fb and "no issues" not in fb.lower():
            flagged.append((fp,fb)); notes.append(fb)
    action_status.text("Generating summary...")
    note_blob = (
        "You are an elite performance coach. Below are expert technical notes and frame feedback:\n"
        + "\n".join(notes) +
        "\nSummarize the overall athlete's strengths, most urgent areas to fix, and actionable training priorities. "
        "Make this direct, specific, and suitable for high-performance training. "
        "No generic advice or empty praise—be blunt and technical. "
        f"Always answer the user's stated concerns directly: {concerns}"
    )
    summ_msgs=[
        {"role":"system", "content":
            "You are an elite coach known for concise, practical advice. Be highly critical and objective. "
            "Give specific corrections, not encouragement. Prioritize technical mastery. Address user concerns directly."
        },
        {"role":"user","content":note_blob}
    ]
    try:
        r2 = openai.chat.completions.create(model="gpt-3.5-turbo", messages=summ_msgs, max_tokens=600, temperature=0.25)
        summary = r2.choices[0].message.content.strip()
    except Exception as e:
        summary = f"❌ Summary failed: {e}"
    st.subheader("📋 Coaching Summary")
    st.write(summary)
    st.download_button("💾 Download Summary", summary, file_name="feedback.txt")
    if flagged:
        pdf = generate_pdf(summary, flagged, sport, category, sub, goal_text, concerns)
        with open(pdf,"rb") as f:
            st.download_button("📄 Download PDF", f, file_name="report.pdf")
        cols=st.columns(5)
        for idx,(fp,cm) in enumerate(flagged):
            with cols[idx%5]:
                st.image(str(fp),width=120, use_container_width=True)
                st.caption(cm[:80]+"...")
                with st.expander("Details"):
                    st.write(cm)
    progress_bar.empty(); action_status.success("Analysis complete.")

# --------- SIDEBAR: Setup ---------
with st.sidebar:
    st.header("🎯 Setup")
    sport = st.selectbox("Sport:", sorted(SPORTS))
    if sport=="Football":
        category = st.selectbox("Role:", sorted(SPORT_OPTIONS[sport]["Roles"]))
        sub = st.selectbox("Skill:", sorted(SPORT_OPTIONS[sport]["Skills"][category]))
    elif sport=="Cricket":
        category = st.selectbox("Discipline:", sorted(SPORT_OPTIONS[sport]["Disciplines"]))
        sub = st.selectbox("Skill:", sorted(SPORT_OPTIONS[sport]["Skills"][category]))
    elif sport=="Rugby":
        category = st.selectbox("Position Group:", sorted(SPORT_OPTIONS[sport]["Positions"]))
        sub = st.selectbox("Skill:", sorted(SPORT_OPTIONS[sport]["Skills"][category]))
    elif sport=="Tennis":
        category = st.selectbox("Aspect:", sorted(SPORT_OPTIONS[sport]["Aspects"]))
        sub = st.selectbox("Skill:", sorted(SPORT_OPTIONS[sport]["Skills"][category]))
    else:
        category = st.selectbox("Category:", sorted(SPORT_OPTIONS[sport]["Categories"]))
        sub = st.selectbox("Event:", sorted(SPORT_OPTIONS[sport]["Events"][category]))
    st.markdown("---")
    default_prompt = DEFAULT_PROMPTS.get((sport,sub), "Describe what you'd like analyzed.")
    st.subheader("✏️ Prompt")
    st.caption(default_prompt)
    goal_text = st.text_area("What to analyze?", default_prompt, height=120)
    concerns = st.text_area("Any concerns?", "")
    st.markdown("---")
    st.subheader("🎥 Video")
    video_file = st.file_uploader("Upload file", type=["mp4","mov","avi"])
    video_url  = st.text_input("Or URL")
    load_btn = st.button("📥 Load Video")

# --------- MAIN: Video, Thumbnails, Preview ---------
col_left, col_right = st.columns([1.2, 2])
with col_left:
    action_status = st.empty()
    progress_bar = st.progress(0)

    # Load video on button press
    if load_btn:
        if not goal_text: st.warning("Add analysis prompt."); st.stop()
        tmp = Path(tempfile.gettempdir())/"input.mp4"
        if tmp.exists(): tmp.unlink(missing_ok=True)
        if video_file: tmp.write_bytes(video_file.read_bytes())
        elif video_url:
            with yt_dlp.YoutubeDL({'format':'mp4','outtmpl':str(tmp),'quiet':True}) as ydl:
                ydl.download([video_url])
        else: st.warning("Upload or enter URL."); st.stop()
        st.session_state.video_path = tmp
        st.success("Video loaded.")

    # Segment/frames logic
    if 'video_path' in st.session_state:
        cap = cv2.VideoCapture(str(st.session_state.video_path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        dur = cap.get(cv2.CAP_PROP_FRAME_COUNT)/fps; cap.release()
        s, e = st.slider("Segment (s):", 0.0, float(dur), (0.0, min(5.0,dur)),step=0.1)
        extract_btn = st.button("🎞️ Extract")
        if extract_btn:
            frames = extract_frames(st.session_state.video_path, s, e)
            st.session_state.frames = frames
            st.session_state.preview_idx = 0  # default to first
            st.success(f"{len(frames)} frames extracted.")

        # --- Thumbnail grid & click-to-preview ---
        if st.session_state.get("frames"):
            thumbs = st.session_state.frames
            preview_idx = st.session_state.get("preview_idx", 0)
            cols = st.columns(5)
            for idx, fp in enumerate(thumbs):
                with cols[idx % 5]:
                    if st.button("", key=f"thumb_{idx}"):
                        st.session_state.preview_idx = idx
                    st.image(str(fp), width=110, use_container_width=True)

with col_right:
    st.subheader("Preview")
    if 'video_path' in st.session_state:
        # If thumbnails, show selected, else show video
        if st.session_state.get("frames") and len(st.session_state.frames) > 0:
            idx = st.session_state.get("preview_idx", 0)
            st.image(str(st.session_state.frames[idx]), width=540, caption="Selected Frame Preview", use_container_width=True)
        else:
            st.video(str(st.session_state.video_path), format="video/mp4", width=540)

# --------- Analyze & Feedback Button and Section ---------
if st.session_state.get("frames"):
    st.markdown("---")
    if st.button("🧠 Analyze & Feedback"):
        run_analysis(st.session_state.frames, sport, category, sub, goal_text, concerns)
