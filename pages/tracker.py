import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh


# --- Require setup before access ---
if "setup_done" not in st.session_state or not st.session_state.setup_done:
    st.warning("⚠️ Please set up the roster first on the Home page.")
    st.stop()


# --- Wide layout + big buttons CSS ---
st.markdown("""
    <style>
    
    
    .main .block-container {
        max-width: 100% !important;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    div.stButton > button {
        font-size: 30px !important;
        height: 80px !important;
        width: 120px !important;
    }
    /* Zone selection alert styling */
    .zone-alert {
        background-color: #ff4b4b;
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin: 2rem 0;
        border: 4px solid #ff0000;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    .zone-button {
        font-size: 20px !important;
        height: 70px !important;
        width: 100% !important;
    }

   
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(layout='wide')


# --- Zone categories ---
zones_2pt = [
    "Restricted Area",
    "In the Paint (Non-RA)",
    "Left corner Mid-Range",
    "Right corner Mid-Range",
    "Left wing Mid-Range",
    "Right wing Mid-Range",
    "Top of the Key Mid-Range"
]

zones_3pt = [
    "Left Corner 3",
    "Right Corner 3",
    "Left Wing 3",
    "Right Wing 3",
    "Top of the Arc 3"
]

# --- Init session state ---
if "starters" not in st.session_state:
    st.session_state.starters = []
if "players" not in st.session_state:
    st.session_state.players = [23,33,24,75,11,5,84,44,8,31,17]
if "stats" not in st.session_state:
    st.session_state.stats = []
if "pending_action" not in st.session_state:
    st.session_state.pending_action = None
if "quarter" not in st.session_state:
    st.session_state.quarter = 1
if "max_quarters" not in st.session_state:
    st.session_state.max_quarters = 4
if "clock_running" not in st.session_state:
    st.session_state.clock_running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "elapsed" not in st.session_state:
    st.session_state.elapsed = 0


# --- CHECK IF ZONE SELECTION IS PENDING ---
if st.session_state.pending_action:
    player, action, act_time = st.session_state.pending_action

    st.markdown(
        f"""
        <div class="zone-alert">
            🏀 Select Zone for Player {player}<br>
            <span style="font-size:20px;">Action: {action} at {act_time}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Pick zones based on action
    if action in ["2PT", "Miss2"]:
        zone_list = zones_2pt
    elif action in ["3PT", "Miss3"]:
        zone_list = zones_3pt
    else:
        zone_list = []

    col_left, col_mid, col_right = st.columns([1,1,1])

    for zone in zone_list:
        if "Left" in zone:
            col = col_left
        elif "Right" in zone:
            col = col_right
        else:
            col = col_mid

        if col.button(zone, key=f"zone-{player}-{zone}"):
            st.session_state.stats.append(
                [player, f"{action} ({zone})", act_time, f"Q{st.session_state.quarter}"]
            )
            st.session_state.pending_action = None
            st.rerun()

    if st.button("❌ Cancel"):
        st.session_state.pending_action = None
        st.rerun()

    st.stop()


# --- Bench UI (buttons inside bordered container) ---
#st.title("Bench")

MAX_COLS = 10


for row_start in range(0, len(st.session_state.players), MAX_COLS):
    row_players = st.session_state.players[row_start:row_start+MAX_COLS]
    cols = st.columns(MAX_COLS)
    for i, p in enumerate(row_players):
        with cols[i]:
            if st.button(str(p), key=f"player-{p}"):
                if len(st.session_state.starters) < 5:
                    st.session_state.starters.append(p)
                    st.session_state.players.remove(p)
                    st.session_state.stats.append([p, "SUB_IN", "0:00", f"Q{st.session_state.quarter}"])
                    st.rerun()

import streamlit as st
import time
from streamlit.components.v1 import html

# --- Initialize session state ---
if "clock_running" not in st.session_state:
    st.session_state.clock_running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "elapsed" not in st.session_state:
    st.session_state.elapsed = 0.0
if "quarter" not in st.session_state:
    st.session_state.quarter = 1
if "max_quarters" not in st.session_state:
    st.session_state.max_quarters = 4

# --- Backend timer ---
if st.session_state.clock_running:
    elapsed = st.session_state.elapsed + (time.time() - st.session_state.start_time)
else:
    elapsed = st.session_state.elapsed
minutes, seconds = divmod(int(elapsed), 60)
current_game_time = f"{minutes:02d}:{seconds:02d}"
st.session_state.current_game_time = current_game_time

# === TIMER + QUARTER SIDE BY SIDE ===
col_timer, col_quarter = st.columns([2, 1])

with col_timer:
    html(f"""
    <style>
    #clock {{
        font-size: 60px;
        font-weight: bold;
        text-align: left;
        color: #00BF96;
        
        border-radius: 10px;
        padding: 8px 16px;
        margin-bottom: 6px;
        
    }}
    .clock-btn {{
        font-size: 18px;
        padding: 8px 14px;
        margin: 3px;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        color: white;
    }}
    #start-btn {{ background-color: #28a745; }}
    #stop-btn {{ background-color: #dc3545; }}
    #reset-btn {{ background-color: #6c757d; }}
    </style>

    <div id="clock">⏱ {minutes:02d}:{seconds:02d}</div>
    <div>
        <button id="start-btn" class="clock-btn">▶️ Start</button>
        <button id="stop-btn" class="clock-btn">⏸ Pause</button>
        <button id="reset-btn" class="clock-btn">🔄 Reset</button>
    </div>

    <script>
    let running = {str(st.session_state.clock_running).lower()};
    let elapsed = {int(elapsed * 1000)};
    let startTime = Date.now();
    let timer = null;

    function updateClock() {{
        const now = Date.now();
        let total = elapsed;
        if (running) total += (now - startTime);
        const totalSec = Math.floor(total / 1000);
        const min = String(Math.floor(totalSec / 60)).padStart(2,'0');
        const sec = String(totalSec % 60).padStart(2,'0');
        document.getElementById('clock').textContent = `⏱ ${{min}}:${{sec}}`;
    }}

    function startClock() {{
        if (!running) {{
            running = true;
            startTime = Date.now();
            timer = setInterval(updateClock, 1000);
            updateClock();
            window.parent.postMessage({{type: 'clock', action: 'start'}}, '*');
        }}
    }}

    function stopClock() {{
        if (running) {{
            running = false;
            clearInterval(timer);
            elapsed += (Date.now() - startTime);
            window.parent.postMessage({{type: 'clock', action: 'stop', elapsed: elapsed}}, '*');
        }}
    }}

    function resetClock() {{
        running = false;
        elapsed = 0;
        clearInterval(timer);
        document.getElementById('clock').textContent = "⏱ 00:00";
        window.parent.postMessage({{type: 'clock', action: 'reset'}}, '*');
    }}

    document.getElementById('start-btn').addEventListener('click', startClock);
    document.getElementById('stop-btn').addEventListener('click', stopClock);
    document.getElementById('reset-btn').addEventListener('click', resetClock);

    updateClock();
    if (running) timer = setInterval(updateClock, 1000);
    </script>
    """, height=100, width=300)

    colA, colB, colC = st.columns([0.45,0.45,1.5], gap="small")

button_style = """
    <style>
    div.stButton > button {
        margin: 0px !important;
        padding: 0.4rem 0.8rem !important;
        font-size: 16px !important;
    }
    div[data-testid="column"] {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    </style>
"""
st.markdown(button_style, unsafe_allow_html=True)

with colA:
    if st.button("▶️ Start / Resume", key="start"):
        if not st.session_state.clock_running:
            st.session_state.clock_running = True
            st.session_state.start_time = time.time()
        st.rerun()

with colB:
    if st.button("⏸ Pause", key="pause"):
        if st.session_state.clock_running:
            st.session_state.elapsed += time.time() - st.session_state.start_time
            st.session_state.clock_running = False
        st.rerun()

with colC:
    if st.button("🔄 Reset", key="reset"):
        st.session_state.clock_running = False
        st.session_state.elapsed = 0
        st.session_state.start_time = None
        st.rerun()


with col_quarter:
    # --- Determine label ---
    if st.session_state.quarter <= 4:
        quarter_label = f"Quarter {st.session_state.quarter}"
    else:
        overtime_num = st.session_state.quarter - 4
        quarter_label = f"Overtime {overtime_num}"

    # --- Display heading ---
    st.markdown(f"### {quarter_label}")

    # --- Ensure we track last quarter + time ---
    if "previous_quarter" not in st.session_state:
        st.session_state.previous_quarter = None
    if "previous_elapsed" not in st.session_state:
        st.session_state.previous_elapsed = 0

    # --- 3 buttons in one row (side-by-side layout) ---
    q_col1, q_col2, q_col3 = st.columns([0.9, 0.9, 1.2], gap="small")

    q_button_style = """
        <style>
        div[data-testid="column"] {
            padding-left: 0 !important;
            padding-right: 0 !important;
        }
        
        </style>
    """
    st.markdown(q_button_style, unsafe_allow_html=True)

    # --- Next Quarter ---
    with q_col1:
        if st.button("➡️ Next Quarter", key="next_q"):
            # Save current quarter & elapsed before switching
            if st.session_state.clock_running:
                st.session_state.elapsed += time.time() - st.session_state.start_time

            st.session_state.previous_quarter = st.session_state.quarter
            st.session_state.previous_elapsed = st.session_state.elapsed

            # Move to next quarter
            st.session_state.quarter += 1
            if st.session_state.quarter > st.session_state.max_quarters:
                st.session_state.max_quarters = st.session_state.quarter

            # Reset clock
            st.session_state.clock_running = False
            st.session_state.elapsed = 0
            st.session_state.start_time = None

            st.rerun()

    # --- Undo Quarter ---
    with q_col2:
        if st.button("↩️ Undo Quarter", key="undo_q", disabled=not st.session_state.previous_quarter):
            if st.session_state.previous_quarter:
                st.session_state.quarter = st.session_state.previous_quarter
                st.session_state.elapsed = st.session_state.previous_elapsed
                st.session_state.clock_running = False
                st.session_state.start_time = None
                st.session_state.previous_quarter = None
                st.session_state.previous_elapsed = 0
                st.rerun()

    # --- Reset Game ---
    with q_col3:
        if st.button("🔄 Reset Game", key="reset_game"):
            st.session_state.quarter = 1
            st.session_state.max_quarters = 4
            st.session_state.stats = []
            st.session_state.starters = []
            st.session_state.players = []
            st.session_state.clock_running = False
            st.session_state.elapsed = 0
            st.session_state.start_time = None
            st.session_state.pending_action = None
            st.session_state.previous_quarter = None
            st.session_state.previous_elapsed = 0
            st.rerun()


# Three main columns: Players | Actions | Logged Stats
col_players, col_actions, col_stats = st.columns([1, 2, 1], gap="small")

# --- Players on Court ---
with col_players:
    st.subheader("Players")

    if "selected_player" not in st.session_state:
        st.session_state.selected_player = None

    for player in st.session_state.starters:
        is_selected = (st.session_state.selected_player == player)
        button_label = f"Player {player}"
        if is_selected:
            button_label = f"✅ {button_label}"
        if st.button(button_label, key=f"select-{player}"):
            st.session_state.selected_player = None if is_selected else player
            st.rerun()


# --- Actions for Selected Player ---
with col_actions:
    if st.session_state.selected_player:
        player = st.session_state.selected_player
        st.subheader(f"Actions for Player {player}")

        # Define all actions in a 5x3 grid
        actions_grid = [
            ["2PT", "3PT", "FT"],
            ["Miss2", "Miss3", "MissFT"],
            ["OREB", "DREB", "BLK"],
            ["STL", "TO", "Foul"],
            ["Ast", "SUB", ""],  # empty string to keep grid shape
        ]

        # Render grid
        for row in actions_grid:
            cols = st.columns(5, gap="small")
            for i, action in enumerate(row):
                if action:  # skip empty placeholders
                    with cols[i]:
                        if st.button(action, key=f"{player}-{action}"):
                            if action == "SUB":
                                st.session_state.players.append(player)
                                st.session_state.starters.remove(player)
                                st.session_state.stats.append(
                                    [player, "SUB_OUT", current_game_time, f"Q{st.session_state.quarter}"]
                                )
                                st.session_state.selected_player = None
                                st.rerun()
                            elif action in ["2PT", "3PT", "Miss2", "Miss3"]:
                                st.session_state.pending_action = (player, action, current_game_time)
                                st.rerun()
                            else:
                                st.session_state.stats.append(
                                    [player, action, current_game_time, f"Q{st.session_state.quarter}"]
                                )
                                st.rerun()
    else:
        st.info("👈 Select a player to log an action")


# --- Logged Stats (Right Side Panel) ---
with col_stats:
    st.markdown("<h3 style='margin-top:0;'>📊 Logged Stats</h3>", unsafe_allow_html=True)

    if st.session_state.stats:
        df = pd.DataFrame(st.session_state.stats, columns=["Player", "Action", "Time", "Quarter"])
        st.dataframe(df, use_container_width=True, height=400)

        # Undo + Download side-by-side
        undo_col, dl_col = st.columns(2, gap="small")
        with undo_col:
            if st.button("↩️ Undo"):
                st.session_state.stats.pop()
                st.rerun()
        with dl_col:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download",
                data=csv,
                file_name="game_stats.csv",
                mime="text/csv",
            )
    else:
        st.info("No stats logged yet.")

