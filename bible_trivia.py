import streamlit as st
import json, time, os

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; background-color: #1e5631; color: white; }
    .main-text { color: #1e5631; text-align: center; }
    .timer-container { background-color: #f0f2f6; padding: 10px; border-radius: 10px; border: 1px solid #1e5631; }
    .timer-text { font-size: 20px; font-weight: bold; color: #cc0000; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'page' not in st.session_state:
    st.session_state.update({
        'page': 'welcome', 
        'leaderboard': [], 
        'used_q_indices': [], 
        'score': 0, 
        'muted': False,
        'start_time': None
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

# --- TIMER FRAGMENT (Prevents site-wide lag) ---
@st.fragment(run_every=1)
def show_timer():
    if st.session_state.page == 'quiz' and st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
        remaining = int(st.session_state.time_limit - elapsed)
        
        if remaining <= 0:
            st.session_state.page = 'summary'
            # Record score to leaderboard
            st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
            st.rerun()
            
        st.markdown(f"""
            <div class='timer-container'>
                <div class='timer-text'>⏱️ {remaining}s Left | Score: {st.session_state.score}</div>
            </div>
            """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("Settings")
    if st.button("🔊 Unmute" if st.session_state.muted else "🔇 Mute"):
        st.session_state.muted = not st.session_state.muted
        st.rerun()

# --- PAGE ROUTING ---

# 1. WELCOME PAGE
if st.session_state.page == 'welcome':
    # st.image("logo.png", width=200) # Uncomment this and add your logo path
    st.title("CATG Quiz")
    st.markdown("<h1 class='main-text'>Ready to Start?</h1>", unsafe_allow_html=True)
    if st.button("CONTINUE"):
        st.session_state.page = 'register'
        st.rerun()

# 2. REGISTRATION PAGE
elif st.session_state.page == 'register':
    st.markdown("<h2 class='main-text'>Player Registration</h2>", unsafe_allow_html=True)
    name = st.text_input("Player Name", f"Player {len(st.session_state.leaderboard)+1}")
    limit = st.selectbox("Time Limit (Seconds)", [30, 60, 120], index=1)
    
    if st.button("START QUIZ"):
        st.session_state.update({
            'page': 'quiz', 
            'p_name': name, 
            'time_limit': limit, 
            'start_time': time.time(), 
            'score': 0,
            'used_q_indices': []
        })
        st.rerun()

# 3. QUIZ PAGE
elif st.session_state.page == 'quiz':
    # Background music starts after user interaction (clicking 'Start Quiz')
    play_audio("background_music.mp3") 
    
    show_timer() # Runs independently via @st.fragment
    
    all_qs = load_data()
    # Find next question not in used list
    current_q_idx = len(st.session_state.used_q_indices)
    
    if current_q_idx >= len(all_qs):
        st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
        st.session_state.page = 'summary'
        st.rerun()
    else:
        q = all_qs[current_q_idx]
        st.subheader(f"Question {current_q_idx + 1}")
        st.write(f"### {q['question']}")
        
        # Unique keys (btn_idx_option) prevent button state from "sticking"
        for opt in q['options']:
            if st.button(opt, key=f"q{current_q_idx}_{opt}"):
                if opt == q['answer']:
                    st.session_state.score += 1
                st.session_state.used_q_indices.append(current_q_idx)
                st.rerun()

# 4. SUMMARY PAGE
elif st.session_state.page == 'summary':
    st.markdown("<h2 class='main-text'>Round Results</h2>", unsafe_allow_html=True)
    st.success(f"Final Score for {st.session_state.p_name}: {st.session_state.score}")
    
    if st.button("NEXT PLAYER"): 
        st.session_state.page = 'register'
        st.rerun()
    if st.button("FINAL RANKINGS"): 
        st.session_state.page = 'final'
        st.rerun()

# 5. LEADERBOARD PAGE
elif st.session_state.page == 'final':
    play_audio("winner_sound.mp3.mp3", loop=False) # Plays once
    st.markdown("<h1 class='main-text'>🏆 Leaderboard 🏆</h1>", unsafe_allow_html=True)
    
    lb = sorted(st.session_state.leaderboard, key=lambda x: x[1], reverse=True)
    for i, (n, s) in enumerate(lb):
        style = "gold" if i == 0 else "silver" if i == 1 else "bronze" if i == 2 else ""
        st.markdown(f"<div class='rank-card {style}'>{i+1}. {n.upper()} — {s} Points</div>", unsafe_allow_html=True)
        
    if st.button("NEW TOURNAMENT"):
        st.session_state.clear()
        st.rerun()
