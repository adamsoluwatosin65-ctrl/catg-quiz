import streamlit as st
import json, time, os, random

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz", layout="centered")

# --- HIGH-END CREATIVE DESIGN ---
st.markdown("""
    <style>
    audio { display: none; }

    /* Animated Mesh Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #f0f4f1 0%, #e1eedb 50%, #d1e2d4 100%);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        background-attachment: fixed;
    }

    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Glassmorphism Question Box with Glow */
    .question-box {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 40px;
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-left: 12px solid #1e5631;
        box-shadow: 0 20px 40px rgba(0,0,0,0.08);
        margin-bottom: 30px;
        transition: transform 0.3s ease;
    }

    /* Floating Effect for Cards */
    .question-box:hover {
        transform: translateY(-5px);
    }

    /* Premium Button Styling */
    .stButton>button { 
        width: 100%; border-radius: 18px; height: 4.2em; 
        font-size: 19px; font-weight: 800; 
        background: rgba(255, 255, 255, 0.9);
        color: #1e5631; border: 2px solid #1e5631; 
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 20px rgba(30,86,49,0.1);
    }

    .stButton>button:hover { 
        background-color: #1e5631 !important; color: #ffffff !important;
        box-shadow: 0 12px 25px rgba(30,86,49,0.3);
    }

    /* Leaderboard Rank Cards */
    .rank-card { 
        padding: 22px; border-radius: 20px; margin: 12px 0; 
        text-align: center; font-size: 24px; font-weight: 900;
        position: relative; z-index: 5;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
    }
    .gold { background: linear-gradient(135deg, #FFD700 0%, #FFF9C4 100%); color: #7B5E00; border: 2px solid #FFD700; }
    .silver { background: linear-gradient(135deg, #E0E0E0 0%, #FFFFFF 100%); color: #424242; border: 2px solid #BDBDBD; }
    .bronze { background: linear-gradient(135deg, #D7A977 0%, #F5E6D3 100%); color: #5D4037; border: 2px solid #D7A977; }

    /* Spread Balloons Animation */
    @keyframes spreadFloat {
        0% { transform: translateY(110vh) translateX(0) rotate(0deg); opacity: 0; }
        15% { opacity: 1; }
        85% { opacity: 1; }
        100% { transform: translateY(-30vh) translateX(40px) rotate(15deg); opacity: 0; }
    }
    .balloon {
        position: fixed; font-size: 60px; animation: spreadFloat 12s linear infinite;
        z-index: 99999 !important; pointer-events: none;
        filter: drop-shadow(0 0 10px rgba(255,255,255,0.5));
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'leaderboard' not in st.session_state:
    st.session_state.leaderboard = []
if 'muted' not in st.session_state:
    st.session_state.muted = False
if 'wrong_answers' not in st.session_state:
    st.session_state.wrong_answers = []

def play_audio(file_path, loop=True):
    if not st.session_state.muted and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            st.audio(f.read(), format="audio/mp3", loop=loop, autoplay=True)

# --- HIGH SPEED TIMER ---
@st.fragment(run_every=1)
def high_speed_timer():
    if st.session_state.page == 'quiz' and 'start_time' in st.session_state:
        elapsed = time.time() - st.session_state.start_time
        remaining = int(st.session_state.time_limit - elapsed)
        if remaining <= 0:
            st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
            st.session_state.page = 'summary'
            st.rerun()
        st.markdown(f"<div style='text-align:right; font-weight:900; color:#d32f2f; font-size:24px; letter-spacing:1px;'>⏱️ {remaining}s</div>", unsafe_allow_html=True)

# --- NAVIGATION LOGIC ---

if st.session_state.page == 'welcome':
    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        if os.path.exists('logo.png'): st.image('logo.png', use_container_width=True)
    st.markdown("<h1 style='text-align: center; color: #1e5631; font-size: 50px; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);'>WELCOME TO CATG QUIZ</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #2a7a45; font-weight: 600;'>Win to get to leadership board</h3>", unsafe_allow_html=True)
    if st.button("GET STARTED"):
        st.session_state.page = 'register'
        st.rerun()

elif st.session_state.page == 'register':
    st.markdown("<h2 style='text-align: center; color: #1e5631;'>Player Entry</h2>", unsafe_allow_html=True)
    with st.container(border=True):
        name = st.text_input("Enter Your Name")
        limit = st.selectbox("Choose Your Challenge Time (Seconds)", [30, 60, 120, 300], index=1)
    
    col1, col2 = st.columns(2)
    if col1.button("START QUIZ"):
        if name:
            all_qs = json.load(open('questions.json')) if os.path.exists('questions.json') else []
            indices = list(range(len(all_qs))); random.shuffle(indices)
            st.session_state.update({'page': 'quiz', 'p_name': name, 'time_limit': limit, 'start_time': time.time(), 'score': 0, 'shuffled_indices': indices, 'current_step': 0, 'wrong_answers': []})
            st.rerun()
    if col2.button("QUIT"):
        st.session_state.clear(); st.rerun()

elif st.session_state.page == 'quiz':
    play_audio("background_music.mp3")
    high_speed_timer()
    
    all_qs = json.load(open('questions.json'))
    step = st.session_state.current_step
    
    if step < len(st.session_state.shuffled_indices):
        q = all_qs[st.session_state.shuffled_indices[step]]
        st.markdown(f"""<div class="question-box"><p style="color: #1e5631; font-weight: 900; text-transform: uppercase; font-size: 14px; letter-spacing: 2px; opacity: 0.5;">Question {step+1}</p>
        <h2 style="color: #1e5631; margin-top: 10px; font-size: 32px; line-height: 1.2;">{q['question']}</h2></div>""", unsafe_allow_html=True)
        
        for opt in q['options']:
            if st.button(opt, key=f"q{step}_{opt}"):
                if opt == q['answer']: st.session_state.score += 1
                else: st.session_state.wrong_answers.append({'question': q['question'], 'correct': q['answer'], 'yours': opt})
                st.session_state.current_step += 1
                st.rerun()
    else:
        st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
        st.session_state.page = 'summary'
        st.rerun()

elif st.session_state.page == 'summary':
    st.markdown(f"<h1 style='text-align: center; color: #1e5631;'>Round Complete, {st.session_state.p_name}!</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='question-box' style='text-align:center;'><h3>Round Score</h3><h1 style='font-size: 80px; color: #1e5631; margin: 0;'>{st.session_state.score}</h1></div>", unsafe_allow_html=True)
    
    if st.session_state.wrong_answers:
        with st.expander("🔍 REVIEW YOUR MISTAKES"):
            for item in st.session_state.wrong_answers:
                st.markdown(f"""<div style="background: rgba(255,255,255,0.5); padding: 15px; border-radius: 15px; border-left: 5px solid red; margin-bottom: 10px;">
                <p style="margin: 0;"><b>Q: {item['question']}</b></p>
                <p style="color: #d32f2f; margin: 5px 0 0 0;">❌ {item['yours']}</p>
                <p style="color: #2e7d32; margin: 0;">✅ {item['correct']}</p></div>""", unsafe_allow_html=True)

    cA, cB, cC = st.columns(3)
    if cA.button("NEXT PLAYER"): st.session_state.page = 'register'; st.rerun()
    if cB.button("LEADERBOARD"): st.session_state.page = 'final'; st.rerun()
    if cC.button("QUIT"): st.session_state.clear(); st.rerun()

elif st.session_state.page == 'final':
    play_audio("winner_sound.mp3.mp3", loop=False)
    
    # Random Spread Balloons
    balloon_list = ["🎈", "🎊", "✨", "⭐", "🎈", "🍀"]
    balloons_html = "".join([f'<div class="balloon" style="left:{random.randint(0,95)}%; bottom:{random.randint(-20, 40)}vh; animation-delay:{random.uniform(0,10)}s;">{random.choice(balloon_list)}</div>' for _ in range(45)])
    st.markdown(balloons_html, unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: #1e5631; font-size: 45px;'>🏆 HALL OF FAME 🏆</h1>", unsafe_allow_html=True)
    scores = sorted(st.session_state.leaderboard, key=lambda x: x[1], reverse=True)
    for i, (n, s) in enumerate(scores):
        rank = "gold" if i == 0 else "silver" if i == 1 else "bronze" if i == 2 else ""
        st.markdown(f"<div class='rank-card {rank}'>{i+1}. {n.upper()} — {s} PTS</div>", unsafe_allow_html=True)
        
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    if c1.button("NEXT PLAYER"): st.session_state.page = 'register'; st.rerun()
    if c2.button("RESET ALL"): st.session_state.clear(); st.rerun()
    if c3.button("QUIT"): st.session_state.clear(); st.rerun()
