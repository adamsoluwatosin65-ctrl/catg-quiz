import streamlit as st
import json, time, os, random

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz Pro", layout="centered")

# --- HIGH-END ANIMATED DESIGN ---
st.markdown("""
    <style>
    audio { display: none; }
    .stApp {
        background: linear-gradient(-45deg, #1e5631, #2a7a45, #a8e063, #f0f4f1);
        background-size: 400% 400%;
        animation: activeGradient 12s ease infinite;
        background-attachment: fixed;
    }
    @keyframes activeGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .question-box {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(15px);
        padding: 40px;
        border-radius: 30px;
        border-left: 12px solid #1e5631;
        box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        margin-bottom: 30px;
        color: #1e5631;
    }
    .podium-card {
        padding: 20px; border-radius: 15px; margin: 10px 0;
        text-align: center; font-weight: 900; font-size: 22px;
    }
    .gold { background: linear-gradient(90deg, #FFD700, #FFFACD); color: #8B4513; border: 3px solid #DAA520; }
    .silver { background: linear-gradient(90deg, #C0C0C0, #F5F5F5); color: #4F4F4F; border: 3px solid #A9A9A9; }
    .bronze { background: linear-gradient(90deg, #CD7F32, #FAEBD7); color: #5D2906; border: 3px solid #8B4513; }
    .standard { background: white; color: #1e5631; border: 1px solid #ddd; }
    .stButton>button { 
        width: 100%; border-radius: 20px; height: 3.5em; 
        font-size: 18px; font-weight: 800; transition: all 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'page' not in st.session_state: st.session_state.page = 'welcome'
if 'leaderboard' not in st.session_state: st.session_state.leaderboard = []
if 'muted' not in st.session_state: st.session_state.muted = False

def play_audio(file_path, loop=True):
    if not st.session_state.muted and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            st.audio(f.read(), format="audio/mp3", loop=loop, autoplay=True)

@st.fragment(run_every=1)
def high_speed_timer():
    if st.session_state.page == 'quiz' and 'start_time' in st.session_state:
        elapsed = time.time() - st.session_state.start_time
        remaining = int(st.session_state.time_limit - elapsed)
        if remaining <= 0:
            st.session_state.page = 'summary'
            st.rerun()
        st.markdown(f"<div style='text-align:right; font-weight:900; color:white; font-size:24px;'>⏱️ {remaining}s</div>", unsafe_allow_html=True)

# --- APP PAGES ---
if st.session_state.page == 'welcome':
    st.markdown("<h1 style='text-align: center; color: white;'>WELCOME TO CATG QUIZ</h1>", unsafe_allow_html=True)
    if st.button("GET STARTED"): 
        st.session_state.page = 'mode_selection'
        st.rerun()

elif st.session_state.page == 'mode_selection':
    col1, col2 = st.columns(2)
    with col1:
        if st.button("SINGLE PLAYER"):
            st.session_state.game_mode = 'single'
            st.session_state.page = 'register'
            st.rerun()
    with col2:
        if st.button("MULTIPLAYER"):
            st.session_state.game_mode = 'multi'
            st.session_state.page = 'register'
            st.rerun()

elif st.session_state.page == 'register':
    player_names = []
    if st.session_state.game_mode == 'single':
        name = st.text_input("Player Name", key="reg_single")
        if name: player_names.append(name)
    else:
        num_players = st.number_input("Number of Players", 2, 50, 2)
        for i in range(num_players):
            n = st.text_input(f"Player {i+1}", key=f"reg_p{i}")
            if n: player_names.append(n)

    limit = st.selectbox("Time Limit", [30, 60, 120, 300], index=1)
    if st.button("START"):
        if player_names:
            # Load questions once
            qs = []
            if os.path.exists('questions.json'):
                with open('questions.json', 'r') as f:
                    qs = json.load(f)
            
            st.session_state.update({
                'multi_players': player_names,
                'current_player_idx': 0,
                'time_limit': limit,
                'questions_data': qs,
                'page': 'quiz_init'
            })
            st.rerun()

elif st.session_state.page == 'quiz_init':
    idx = st.session_state.current_player_idx
    current_name = st.session_state.multi_players[idx]
    
    # Create indices and shuffle
    indices = list(range(len(st.session_state.questions_data)))
    random.shuffle(indices)
    
    st.session_state.update({
        'p_name': current_name,
        'start_time': time.time(),
        'score': 0,
        'shuffled_indices': indices,
        'current_step': 0,
        'wrong_answers': [],
        'page': 'quiz'
    })
    st.rerun()

elif st.session_state.page == 'quiz':
    high_speed_timer()
    
    # Logic to handle question fetching
    indices = st.session_state.get('shuffled_indices', [])
    step = st.session_state.get('current_step', 0)
    
    if step < len(indices):
        q_idx = indices[step]
        q = st.session_state.questions_data[q_idx]
        
        # Display Question
        st.markdown(f"""<div class="question-box">
            <p style="opacity:0.6; font-size:14px; margin:0;">PLAYER: {st.session_state.p_name.upper()} | {step+1}/{len(indices)}</p>
            <h2 style="margin-top:10px;">{q['question']}</h2>
        </div>""", unsafe_allow_html=True)
        
        # Display Options
        for opt in q['options']:
            if st.button(opt, key=f"btn_{step}_{opt}"):
                if opt == q['answer']: 
                    st.session_state.score += 1
                else: 
                    st.session_state.wrong_answers.append({'question': q['question'], 'correct': q['answer'], 'yours': opt})
                st.session_state.current_step += 1
                st.rerun()
    else:
        # No more questions
        st.session_state.page = 'summary'
        st.rerun()

elif st.session_state.page == 'summary':
    # Add to leaderboard only once when arriving here
    entry = (st.session_state.p_name, st.session_state.score)
    if entry not in st.session_state.leaderboard:
        st.session_state.leaderboard.append(entry)

    st.markdown(f"<div class='question-box' style='text-align:center;'><h1>Score: {st.session_state.score}</h1></div>", unsafe_allow_html=True)
    
    has_next = st.session_state.game_mode == 'multi' and (st.session_state.current_player_idx + 1 < len(st.session_state.multi_players))
    
    if has_next:
        if st.button("NEXT PLAYER"):
            st.session_state.current_player_idx += 1
            st.session_state.page = 'quiz_init'
            st.rerun()
    
    if st.button("VIEW LEADERBOARD"):
        st.session_state.page = 'final'
        st.rerun()

elif st.session_state.page == 'final':
    st.markdown("<h1 style='text-align: center; color: white;'>🏆 LEADERBOARD 🏆</h1>", unsafe_allow_html=True)
    scores = sorted(st.session_state.leaderboard, key=lambda x: x[1], reverse=True)
    for i, (n, s) in enumerate(scores):
        cls = "gold" if i==0 else "silver" if i==1 else "bronze" if i==2 else "standard"
        st.markdown(f"<div class='podium-card {cls}'>{i+1}. {n} - {s} PTS</div>", unsafe_allow_html=True)
    
    if st.button("RESTART"):
        st.session_state.clear()
        st.rerun()
