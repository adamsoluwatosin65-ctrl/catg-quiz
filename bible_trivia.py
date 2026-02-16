import streamlit as st
import json, time, os, random

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz", layout="centered")

# --- ADVANCED DESIGN & BACKGROUND DECORATION ---
st.markdown("""
    <style>
    /* Gradient Background for the entire App */
    .stApp {
        background: linear-gradient(135deg, #f0f4f1 0%, #d9e8dd 100%);
        background-attachment: fixed;
    }

    /* Decorated Question Card (Glassmorphism) */
    .question-box {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 40px;
        border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-left: 10px solid #1e5631;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }

    /* Styled Answer Buttons */
    .stButton>button { 
        width: 100%; border-radius: 15px; height: 4em; 
        font-size: 18px; font-weight: 700; 
        background-color: white; color: #1e5631; 
        border: 2px solid #1e5631; 
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stButton>button:hover { 
        background-color: #1e5631 !important; color: white !important;
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(30,86,49,0.2);
    }

    /* Leaderboard Design */
    .rank-card { 
        padding: 20px; border-radius: 15px; margin: 10px 0; 
        text-align: center; font-size: 22px; font-weight: bold;
        position: relative; z-index: 5;
    }
    .gold { background: linear-gradient(90deg, #FFD700, #FFFACD); color: #8B4513; border: 3px solid #DAA520; }
    .silver { background: linear-gradient(90deg, #C0C0C0, #F5F5F5); color: #4F4F4F; border: 3px solid #A9A9A9; }
    .bronze { background: linear-gradient(90deg, #CD7F32, #FAEBD7); color: #5D2906; border: 3px solid #8B4513; }

    /* Floating Balloons Animation */
    @keyframes spreadFloat {
        0% { transform: translateY(110vh) translateX(0) rotate(0deg); opacity: 0; }
        10% { opacity: 1; }
        50% { transform: translateY(50vh) translateX(60px) rotate(20deg); }
        100% { transform: translateY(-20vh) translateX(-30px) rotate(-20deg); opacity: 0; }
    }
    .balloon {
        position: fixed; font-size: 55px;
        animation: spreadFloat 12s linear infinite;
        z-index: 99999 !important; pointer-events: none;
        text-shadow: 0 0 15px rgba(255,255,255,0.9);
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'leaderboard' not in st.session_state:
    st.session_state.leaderboard = []
if 'muted' not in st.session_state:
    st.session_state.muted = False

def play_audio(file_path, loop=True):
    if not st.session_state.muted and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            st.audio(f.read(), format="audio/mp3", loop=loop, autoplay=True)

# --- TIMER FRAGMENT ---
@st.fragment(run_every=1)
def high_speed_timer():
    if st.session_state.page == 'quiz' and 'start_time' in st.session_state:
        elapsed = time.time() - st.session_state.start_time
        remaining = int(st.session_state.time_limit - elapsed)
        if remaining <= 0:
            st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
            st.session_state.page = 'summary'
            st.rerun()
        st.markdown(f"<div style='text-align:right; font-weight:bold; color:#cc0000; font-size:20px;'>⏱️ {remaining}s</div>", unsafe_allow_html=True)

# --- PAGE ROUTING ---

if st.session_state.page == 'welcome':
    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        if os.path.exists('logo.png'): st.image('logo.png', use_container_width=True)
    st.markdown("<h1 style='text-align: center; color: #1e5631;'>WELCOME TO CATG QUIZ</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #2a7a45;'>Win to get to leadership board</h3>", unsafe_allow_html=True)
    if st.button("GET STARTED"):
        st.session_state.page = 'register'
        st.rerun()

elif st.session_state.page == 'register':
    st.markdown("<h2 style='text-align: center; color: #1e5631;'>Player Entry</h2>", unsafe_allow_html=True)
    name = st.text_input("Player Name")
    limit = st.selectbox("Time Limit (Seconds)", [30, 60, 120, 300], index=1)
    if st.button("START QUIZ"):
        if name:
            all_qs = json.load(open('questions.json')) if os.path.exists('questions.json') else []
            indices = list(range(len(all_qs)))
            random.shuffle(indices)
            st.session_state.update({
                'page': 'quiz', 'p_name': name, 'time_limit': limit,
                'start_time': time.time(), 'score': 0, 
                'shuffled_indices': indices, 'current_step': 0
            })
            st.rerun()

elif st.session_state.page == 'quiz':
    play_audio("background_music.mp3")
    high_speed_timer()
    
    all_qs = json.load(open('questions.json'))
    step = st.session_state.current_step
    
    if step < len(st.session_state.shuffled_indices):
        q = all_qs[st.session_state.shuffled_indices[step]]
        # Decorated Question UI
        st.markdown(f"""
            <div class="question-box">
                <p style="color: #1e5631; font-weight: bold; opacity: 0.6; margin-bottom: 5px;">QUESTION {step+1}</p>
                <h2 style="color: #1e5631; margin-top: 0; font-size: 28px;">{q['question']}</h2>
            </div>
        """, unsafe_allow_html=True)
        
        for opt in q['options']:
            if st.button(opt, key=f"q{step}_{opt}"):
                if opt == q['answer']: st.session_state.score += 1
                st.session_state.current_step += 1
                st.rerun()
    else:
        st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
        st.session_state.page = 'summary'
        st.rerun()

elif st.session_state.page == 'summary':
    st.markdown(f"<h1 style='text-align: center;'>Round Over, {st.session_state.p_name}!</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='question-box' style='text-align:center;'><h2>Your Score: {st.session_state.score}</h2></div>", unsafe_allow_html=True)
    
    colA, colB, colC = st.columns(3)
    if colA.button("NEXT PLAYER"):
        st.session_state.page = 'register'
        st.rerun()
    if colB.button("LEADERBOARD"):
        st.session_state.page = 'final'
        st.rerun()
    if colC.button("QUIT"):
        st.session_state.clear()
        st.session_state.page = 'welcome'
        st.rerun()

elif st.session_state.page == 'final':
    play_audio("winner_sound.mp3.mp3", loop=False)
    
    # Random Full-Screen Spread Balloons
    balloon_list = ["🎈", "🎊", "✨", "⭐", "🎈"]
    balloons_html = "".join([
        f'<div class="balloon" style="left:{random.randint(0,95)}%; bottom:{random.randint(-20, 50)}vh; animation-delay:{random.uniform(0,8)}s;">{random.choice(balloon_list)}</div>' 
        for _ in range(40) 
    ])
    st.markdown(balloons_html, unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: #1e5631;'>🏆 TOURNAMENT STANDINGS 🏆</h1>", unsafe_allow_html=True)
    scores = sorted(st.session_state.leaderboard, key=lambda x: x[1], reverse=True)
    for i, (n, s) in enumerate(scores):
        rank = "gold" if i == 0 else "silver" if i == 1 else "bronze" if i == 2 else ""
        st.markdown(f"<div class='rank-card {rank}'>{i+1}. {n.upper()} — {s} PTS</div>", unsafe_allow_html=True)
        
    st.markdown("---")
    c1, c2 = st.columns(2)
    if c1.button("NEXT PLAYER"):
        st.session_state.page = 'register'
        st.rerun()
    if c2.button("RESET ALL"):
        st.session_state.clear()
        st.rerun()
