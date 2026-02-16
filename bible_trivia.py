import streamlit as st
import json, time, os, random

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz", layout="centered")

# --- ADVANCED CSS ---
st.markdown("""
    <style>
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; 
        font-size: 18px; font-weight: bold; 
        background-color: #1e5631; color: white; border: none;
    }
    .rank-card { 
        padding: 20px; border-radius: 15px; margin: 10px 0; 
        text-align: center; font-size: 22px; font-weight: bold;
        position: relative; z-index: 5;
    }
    .gold { background: linear-gradient(90deg, #FFD700, #FFFACD); color: #8B4513; border: 3px solid #DAA520; }
    .silver { background: linear-gradient(90deg, #C0C0C0, #F5F5F5); color: #4F4F4F; border: 3px solid #A9A9A9; }
    .bronze { background: linear-gradient(90deg, #CD7F32, #FAEBD7); color: #5D2906; border: 3px solid #8B4513; }

    @keyframes floatUp {
        0% { transform: translateY(110vh); opacity: 1; }
        100% { transform: translateY(-20vh); opacity: 0; }
    }
    .balloon {
        position: fixed; bottom: -15%; font-size: 50px;
        animation: floatUp 7s linear infinite;
        z-index: 9999 !important; pointer-events: none;
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

# --- TIMER FRAGMENT (Fixes Lagging) ---
@st.fragment(run_every=1)
def sync_timer():
    if st.session_state.page == 'quiz' and 'start_time' in st.session_state:
        elapsed = time.time() - st.session_state.start_time
        remaining = int(st.session_state.time_limit - elapsed)
        if remaining <= 0:
            st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
            st.session_state.page = 'summary'
            st.rerun()
        st.markdown(f"<h3 style='text-align:center; color:red;'>⏱️ {remaining}s Remaining</h3>", unsafe_allow_html=True)

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
    st.markdown("<h2 style='text-align: center;'>Player Entry</h2>", unsafe_allow_html=True)
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
    sync_timer() # Updates every second without lagging the whole app
    
    all_qs = json.load(open('questions.json'))
    step = st.session_state.current_step
    if step < len(st.session_state.shuffled_indices):
        q = all_qs[st.session_state.shuffled_indices[step]]
        st.markdown(f"## {q['question']}")
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
    st.markdown(f"<h2 style='text-align: center;'>Score: {st.session_state.score}</h2>", unsafe_allow_html=True)
    
    if st.button("NEXT PLAYER"):
        st.session_state.page = 'register'
        st.rerun()
    if st.button("PROCEED TO LEADERSHIP BOARD"):
        st.session_state.page = 'final'
        st.rerun()
    if st.button("QUIT GAME"):
        st.session_state.clear()
        st.session_state.page = 'welcome'
        st.rerun()

elif st.session_state.page == 'final':
    play_audio("winner_sound.mp3.mp3", loop=False)
    # Balloons
    balloons_html = "".join([f'<div class="balloon" style="left:{random.randint(5,90)}%; animation-delay:{random.uniform(0,5)}s;">🎈</div>' for _ in range(25)])
    st.markdown(balloons_html, unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: #1e5631;'>🏆 TOURNAMENT STANDINGS 🏆</h1>", unsafe_allow_html=True)
    scores = sorted(st.session_state.leaderboard, key=lambda x: x[1], reverse=True)
    for i, (n, s) in enumerate(scores):
        rank = "gold" if i == 0 else "silver" if i == 1 else "bronze" if i == 2 else ""
        st.markdown(f"<div class='rank-card {rank}'>{i+1}. {n.upper()} — {s} PTS</div>", unsafe_allow_html=True)
        
    if st.button("NEXT PLAYER"):
        st.session_state.page = 'register'
        st.rerun()
    if st.button("NEW TOURNAMENT (RESET ALL)"):
        st.session_state.clear()
        st.rerun()
