# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'welcome'
if 'leaderboard' not in st.session_state: st.session_state.leaderboard = []
if 'muted' not in st.session_state: st.session_state.muted = False
# New states for Multiplayer
if 'game_mode' not in st.session_state: st.session_state.game_mode = 'single'
if 'multi_players' not in st.session_state: st.session_state.multi_players = []
if 'current_player_idx' not in st.session_state: st.session_state.current_player_idx = 0

# ... (keep your existing play_audio and high_speed_timer functions) ...

# --- APP PAGES ---

if st.session_state.page == 'welcome':
    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        if os.path.exists('logo.png'): st.image('logo.png', use_container_width=True)
    st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 10px rgba(0,0,0,0.3);'>WELCOME TO CATG QUIZ</h1>", unsafe_allow_html=True)
    if st.button("GET STARTED"): 
        st.session_state.page = 'mode_selection'
        st.rerun()

elif st.session_state.page == 'mode_selection':
    st.markdown("<h2 style='text-align: center; color: white;'>Choose Your Mode</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div style='text-align:center; font-size:60px;'>👤</div>", unsafe_allow_html=True)
        if st.button("SINGLE PLAYER"):
            st.session_state.game_mode = 'single'
            st.session_state.page = 'register'
            st.rerun()
            
    with col2:
        st.markdown("<div style='text-align:center; font-size:60px;'>👥</div>", unsafe_allow_html=True)
        if st.button("MULTIPLAYER"):
            st.session_state.game_mode = 'multi'
            st.session_state.page = 'register'
            st.rerun()

elif st.session_state.page == 'register':
    st.markdown(f"<h2 style='text-align: center; color: white;'>{'Multiplayer' if st.session_state.game_mode == 'multi' else 'Single Player'} Entry</h2>", unsafe_allow_html=True)
    
    if st.session_state.game_mode == 'single':
        name = st.text_input("Player Name")
        names = [name] if name else []
    else:
        num_players = st.number_input("Number of Players (2-50)", min_value=2, max_value=50, value=2)
        names = []
        cols = st.columns(2)
        for i in range(num_players):
            with cols[i % 2]:
                n = st.text_input(f"Player {i+1} Name", key=f"pname_{i}")
                if n: names.append(n)

    limit = st.selectbox("Time Limit (Seconds)", [30, 60, 120, 300], index=1)
    
    col1, col2 = st.columns(2)
    if col1.button("START QUIZ"):
        if len(names) > 0:
            all_qs = json.load(open('questions.json')) if os.path.exists('questions.json') else []
            st.session_state.update({
                'multi_players': names,
                'current_player_idx': 0,
                'time_limit': limit,
                'questions_data': all_qs,
                'page': 'quiz_init' # Helper state to set up each player
            })
            st.rerun()
    if col2.button("BACK"): st.session_state.page = 'mode_selection'; st.rerun()

# --- Helper logic to reset session for the next player in the list ---
elif st.session_state.page == 'quiz_init':
    idx = st.session_state.current_player_idx
    current_name = st.session_state.multi_players[idx]
    
    shuffled_indices = list(range(len(st.session_state.questions_data)))
    random.shuffle(shuffled_indices)
    
    st.session_state.update({
        'p_name': current_name,
        'start_time': time.time(),
        'score': 0,
        'shuffled_indices': shuffled_indices,
        'current_step': 0,
        'wrong_answers': [],
        'page': 'quiz'
    })
    st.rerun()

# ... (Keep your existing 'quiz' page logic exactly as is) ...

elif st.session_state.page == 'summary':
    # Add score to leaderboard immediately
    if (st.session_state.p_name, st.session_state.score) not in st.session_state.leaderboard:
        st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
        
    st.markdown(f"<h1 style='text-align: center; color: white;'>Round Over, {st.session_state.p_name}!</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='question-box' style='text-align:center;'><h2>Final Score: {st.session_state.score}</h2></div>", unsafe_allow_html=True)
    
    # Check if there are more players in multiplayer
    has_next = st.session_state.game_mode == 'multi' and (st.session_state.current_player_idx + 1 < len(st.session_state.multi_players))
    
    cA, cB, cC = st.columns(3)
    
    if has_next:
        if cA.button("NEXT PLAYER'S TURN"):
            st.session_state.current_player_idx += 1
            st.session_state.page = 'quiz_init'
            st.rerun()
    else:
        if cA.button("NEW GAME"): st.session_state.page = 'mode_selection'; st.rerun()
        
    if cB.button("LEADERBOARD"): st.session_state.page = 'final'; st.rerun()
    if cC.button("QUIT"): st.session_state.clear(); st.session_state.page = 'welcome'; st.rerun()

# ... (Keep your existing 'final' page logic exactly as is) ...
