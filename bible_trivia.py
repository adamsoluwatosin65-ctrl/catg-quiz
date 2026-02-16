import streamlit as st
import json, random, time, os

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; background-color: #1e5631; color: white; }
    .main-text { color: #1e5631; text-align: center; }
    .rank-card { padding: 15px; border-radius: 10px; margin: 10px 0; text-align: center; font-weight: bold; color: #1e5631; }
    .gold { background-color: #FFD700; border: 2px solid #b8860b; }
    .silver { background-color: #C0C0C0; border: 2px solid #808080; }
    .bronze { background-color: #CD7F32; border: 2px solid #8B4513; }
    .timer-text { font-size: 24px; font-weight: bold; color: #cc0000; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.update({
        'page': 'welcome', 
        'leaderboard': [], 
        'used_q': [], 
        'score': 0, 
        'muted': False
    })

def load_data():
    # Example data structure if file is missing
    if os.path.exists('questions.json'):
        with open('questions.json', 'r') as f: 
            return json.load(f)
    return [{"question": "What is the capital of France?", "options": ["Paris", "London", "Berlin"], "answer": "Paris"}]

def play_audio(file_path):
    if not st.session_state.muted and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            # Note: loop=True and autoplay=True are great for background ambiance
            st.audio(f.read(), format="audio/mp3", loop=True, autoplay=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("Settings")
    if st.button("🔊 Unmute" if st.session_state.muted else "🔇 Mute"):
        st.session_state.muted = not st.session_state.muted
        st.rerun()

# --- PAGE LOGIC ---
if st.session_state.page == 'welcome':
    st.title("CATG Quiz")
    st.markdown("<h1 class='main-text'>Ready to Start?</h1>", unsafe_allow_html=True)
    if st.button("CONTINUE"):
        st.session_state.page = 'register'
        st.rerun()

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
            'used_q': []
        })
        st.rerun()

elif st.session_state.page == 'quiz':
    # Corrected filename reference
    if 'audio_played' not in st.session_state:
        play_audio("background_music.mp3")
        st.session_state.audio_played = True
    
    timer_placeholder = st.empty()
    
    # Calculate elapsed time
    elapsed = time.time() - st.session_state.start_time
    remaining = int(st.session_state.time_limit - elapsed)

    if remaining <= 0:
        st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
        if 'audio_played' in st.session_state: del st.session_state.audio_played
        st.session_state.page = 'summary'
        st.rerun()

    timer_placeholder.markdown(f"<div class='timer-text'>⏱️ Time Remaining: {remaining}s | Score: {st.session_state.score}</div>", unsafe_allow_html=True)

    all_qs = load_data()
    # Filter out questions already used in this round
    qs = [q for q in all_qs if q['question'] not in st.session_state.used_q]
    
    if not qs:
        st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
        st.session_state.page = 'summary'
        st.rerun()
    else:
        q = qs[0]
        st.write(f"### {q['question']}")
        # Using columns for a cleaner button layout
        cols = st.columns(len(q['options']))
        for i, opt in enumerate(q['options']):
            if cols[i].button(opt, key=f"btn_{opt}_{len(st.session_state.used_q)}"):
                st.session_state.used_q.append(q['question'])
                if opt == q['answer']:
                    st.session_state.score += 1
                st.rerun()

    # Refresh every second to update timer
    time.sleep(1)
    st.rerun()

elif st.session_state.page == 'summary':
    st.markdown("<h2 class='main-text'>Round Results</h2>", unsafe_allow_html=True)
    st.success(f"Final Score for {st.session_state.p_name}: {st.session_state.score}")
    
    col1, col2 = st.columns(2)
    if col1.button("NEXT PLAYER"): 
        st.session_state.page = 'register'
        st.rerun()
    if col2.button("FINAL RANKINGS"): 
        st.session_state.page = 'final'
        st.rerun()

elif st.session_state.page == 'final':
    play_audio("winner_sound.mp3.mp3")
    st.markdown("<h1 class='main-text'>🏆 Leaderboard 🏆</h1>", unsafe_allow_html=True)
    
    # Sort leaderboard by score descending
    lb = sorted(st.session_state.leaderboard, key=lambda x: x[1], reverse=True)
    
    for i, (n, s) in enumerate(lb):
        rank_class = "gold" if i == 0 else "silver" if i == 1 else "bronze" if i == 2 else ""
        st.markdown(f"<div class='rank-card {rank_class}'>{i+1}. {n.upper()} — {s} Points</div>", unsafe_allow_html=True)
    
    if st.button("NEW TOURNAMENT"):
        # Reset but keep the leaderboard or clear entirely based on preference
        st.session_state.clear()
        st.rerun()