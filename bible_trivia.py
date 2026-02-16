import streamlit as st
import json, time, os, random

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz", layout="centered")

# --- CUSTOM CSS & ANIMATIONS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold; background-color: #1e5631; color: white; border: none; }
    .stButton>button:hover { background-color: #2a7a45; border: none; }
    .main-text { color: #1e5631; text-align: center; }
    .logo-container { display: flex; justify-content: center; padding: 20px; }
    .big-logo { width: 500px; max-width: 100%; height: auto; border-radius: 15px; }
    .timer-container { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border: 2px solid #1e5631; margin-bottom: 20px; }
    .timer-text { font-size: 22px; font-weight: bold; color: #cc0000; text-align: center; }
    
    /* Infinite Balloon/Confetti Animation for Leaderboard */
    @keyframes move {
        0% { transform: translateY(100vh) translateX(0); opacity: 1; }
        100% { transform: translateY(-10vh) translateX(20px); opacity: 0; }
    }
    .balloon {
        position: fixed; bottom: -10%; font-size: 30px;
        animation: move 4s linear infinite; z-index: 999;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'

if 'leaderboard' not in st.session_state:
    st.session_state.update({
        'leaderboard': [], 
        'score': 0, 
        'muted': False,
        'start_time': None,
        'shuffled_indices': []
    })

def load_data():
    if os.path.exists('questions.json'):
        with open('questions.json', 'r') as f: 
            return json.load(f)
    return [{"question": "Error: questions.json not found!", "options": ["Check File"], "answer": "Check File"}]

def play_audio(file_path, loop=True):
    if not st.session_state.muted and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            st.audio(f.read(), format="audio/mp3", loop=loop, autoplay=True)

# --- TIMER FRAGMENT ---
@st.fragment(run_every=1)
def show_timer():
    if st.session_state.page == 'quiz' and st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
        remaining = int(st.session_state.time_limit - elapsed)
        
        if remaining <= 0:
            st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
            st.session_state.page = 'summary'
            st.rerun()
            
        st.markdown(f"<div class='timer-container'><div class='timer-text'>⏱️ {remaining}s Left | Score: {st.session_state.score}</div></div>", unsafe_allow_html=True)

# --- PAGE ROUTING ---

# 1. WELCOME PAGE
if st.session_state.page == 'welcome':
    st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
    if os.path.exists('logo.png'):
        st.image('logo.png', width=500) # Significantly bigger
    else:
        st.info("Place 'logo.png' in the folder to see your big logo here!")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<h1 class='main-text'>WELCOME TO CATG QUIZ</h1>", unsafe_allow_html=True)
    if st.button("GET STARTED"):
        st.session_state.page = 'register'
        st.rerun()

# 2. REGISTRATION PAGE
elif st.session_state.page == 'register':
    st.markdown("<h2 class='main-text'>Player Registration</h2>", unsafe_allow_html=True)
    name = st.text_input("Player Name", f"Player {len(st.session_state.leaderboard)+1}")
    limit = st.selectbox("Time Limit (Seconds)", [30, 60, 120, 300], index=1)
    
    if st.button("START QUIZ"):
        all_qs = load_data()
        indices = list(range(len(all_qs)))
        random.shuffle(indices) # Shuffle once at start of round
        
        st.session_state.update({
            'page': 'quiz', 
            'p_name': name, 
            'time_limit': limit, 
            'start_time': time.time(), 
            'score': 0,
            'shuffled_indices': indices,
            'current_step': 0
        })
        st.rerun()

# 3. QUIZ PAGE
elif st.session_state.page == 'quiz':
    play_audio("background_music.mp3") 
    show_timer()
    
    all_qs = load_data()
    step = st.session_state.current_step
    
    if step >= len(st.session_state.shuffled_indices):
        st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
        st.session_state.page = 'summary'
        st.rerun()
    else:
        q_idx = st.session_state.shuffled_indices[step]
        q = all_qs[q_idx]
        
        st.write(f"### Question {step + 1}")
        st.markdown(f"#### {q['question']}")
        
        # Display options
        for opt in q['options']:
            if st.button(opt, key=f"q{q_idx}_{opt}"):
                if opt == q['answer']:
                    st.session_state.score += 1
                st.session_state.current_step += 1
                st.rerun()

# 4. SUMMARY PAGE
elif st.session_state.page == 'summary':
    st.markdown("<h2 class='main-text'>Round Finished!</h2>", unsafe_allow_html=True)
    st.success(f"Great job, {st.session_state.p_name}! Your final score: {st.session_state.score}")
    
    if st.button("NEXT PLAYER"): 
        st.session_state.page = 'register'
        st.rerun()
    if st.button("GO TO FINAL LEADERBOARD"): 
        st.session_state.page = 'final'
        st.rerun()

# 5. FINAL LEADERBOARD (With Infinite Balloons)
elif st.session_state.page == 'final':
    play_audio("winner_sound.mp3.mp3", loop=False)
    
    # Custom Infinite Balloons (HTML/CSS injection)
    balloon_html = "".join([f'<div class="balloon" style="left:{random.randint(0,90)}%; animation-delay:{random.uniform(0,4)}s;">🎈</div>' for _ in range(15)])
    st.markdown(balloon_html, unsafe_allow_html=True)
    
    st.markdown("<h1 class='main-text'>🏆 GLOBAL LEADERBOARD 🏆</h1>", unsafe_allow_html=True)
    
    lb = sorted(st.session_state.leaderboard, key=lambda x: x[1], reverse=True)
    for i, (n, s) in enumerate(lb):
        style = "gold" if i == 0 else "silver" if i == 1 else "bronze" if i == 2 else ""
        st.markdown(f"<div class='rank-card {style}'>{i+1}. {n.upper()} — {s} Points</div>", unsafe_allow_html=True)
        
    if st.button("NEW TOURNAMENT"):
        # Reset everything but the leaderboard
        st.session_state.page = 'welcome'
        st.session_state.leaderboard = [] # Clear if starting a fresh tournament
        st.rerun()
