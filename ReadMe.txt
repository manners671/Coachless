# 🏅 CoachlessAI: MVP Sports Video Analysis App

CoachlessAI is an AI-powered video analysis tool that helps athletes receive professional-quality coaching feedback from just a short clip. This MVP allows you to upload a sports video (e.g. football, cricket, tennis), extract key movement frames, and receive instant AI feedback using OpenAI’s GPT-4 Vision.

---

## 🚀 What This MVP Does

- Upload a sports video (MP4, MOV, AVI or YouTube URL)
- Select your sport, position, and skill focus (e.g. "Football – Striker – Finishing")
- Define your personal training goal or concern (e.g. "Improve shot accuracy under pressure")
- Trim the video to a short segment (e.g. 3–5 seconds)
- Automatically extract key movement frames using pose estimation (MediaPipe)
- Send selected frames to OpenAI for feedback
- Receive:
  - Frame-by-frame coaching comments
  - A summary of strengths, issues, and improvement tips
  - Optional downloadable PDF report with annotated frames

---

## 🧰 Requirements

- Python 3.8+
- `pip` package manager
- OpenAI API key (GPT-4 Vision access required)

---

## ⚙️ Installation

1. **Clone this repo** or [Download ZIP](https://github.com/your-repo-url)

2. Navigate into the project folder:

   ```bash
   cd CoachlessAI
