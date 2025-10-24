import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh
import os


# --- Helper function to ensure numeric sorting ---
def sort_players():
    """Ensure players and starters stay numerically sorted."""
    st.session_state.players = sorted([int(p) for p in st.session_state.players])
    st.session_state.starters = sorted([int(p) for p in st.session_state.starters])


# --- Require setup before access ---
if "setup_done" not in st.session_state or not st.session_state.setup_done:
    st.warning("⚠️ Please set up the roster first on the Home page.")
    st.stop()

# --- Retrieve team name ---
team_name = st.session_state.get("team_name", "Unnamed Team")



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
        width: 100px !important;
        margin: 10px !important;
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
    st.session_state.players = []
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

# 🔹 Keep player order sorted initially
sort_players()



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

    

    # Create main row of columns
    col_left, col_mid, col_right = st.columns([1, 1, 1])

    # Render top row (corner + wing 3s)
    for zone in zone_list:
        if zone == "Top of the Arc 3":
            continue  # skip for now, will render later

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

    # Render “Top of the Arc 3” in its own centered row below
    if "Top of the Arc 3" in zone_list:
        st.write("")  # spacing
        bottom_col = st.columns([1, 1, 1])[1]  # center column
        if bottom_col.button("Top of the Arc 3", key=f"zone-{player}-TopArc3"):
            st.session_state.stats.append(
                [player, f"{action} (Top of the Arc 3)", act_time, f"Q{st.session_state.quarter}"]
            )
            st.session_state.pending_action = None
            st.rerun()

    # === Cancel button below all zones ===
    st.write("")  # spacing
    if st.button("❌ Cancel"):
        st.session_state.pending_action = None
        st.rerun()


    st.stop()


# --- Bench UI (buttons inside bordered container) ---
#st.title("Bench")

MAX_COLS = 10

# 🔹 NEW: Always keep bench sorted before displaying

sort_players()


for row_start in range(0, len(st.session_state.players), MAX_COLS):
    row_players = st.session_state.players[row_start:row_start+MAX_COLS]
    cols = st.columns(MAX_COLS)
    for i, p in enumerate(row_players):
        with cols[i]:
            if st.button(str(p), key=f"player-{p}"):
                if len(st.session_state.starters) < 5:
                    st.session_state.starters.append(p)
                    st.session_state.players.remove(p)
                    current_time = st.session_state.get("current_game_time", "00:00")
                    st.session_state.stats.append([p, "SUB_IN", current_time, f"Q{st.session_state.quarter}"])


                    # 🔹 NEW: Keep both lists sorted after substitution
                    sort_players()

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

# --- Calculate total score ---
if "stats" in st.session_state and st.session_state.stats:
    df = pd.DataFrame(st.session_state.stats, columns=["Player", "Action", "Time", "Quarter"])

    # Count made shots
    df["PTS"] = 0
    df.loc[df["Action"].str.startswith("2PT"), "PTS"] = 2
    df.loc[df["Action"].str.startswith("3PT"), "PTS"] = 3
    df.loc[df["Action"].str.startswith("FT"), "PTS"] = 1

    total_score = int(df["PTS"].sum())
else:
    total_score = 0


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

    <div style="display:flex; align-items:center; gap:20px;">
    <div id="clock">⏱ {minutes:02d}:{seconds:02d}</div>
    <div id="score" style="
        font-size: 50px;
        font-weight: bold;
        padding: 8px 16px;
        border-radius: 10px;
    ">
        Score: {total_score}
    </div>
</div>

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
    """, height=100, width=600)

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
    if st.button("Start Clock", key="start"):
        if not st.session_state.clock_running:
            st.session_state.clock_running = True
            st.session_state.start_time = time.time()
        st.rerun()

#with colB:
 #   if st.button("Pause", key="pause"):
  #      if st.session_state.clock_running:
   #         st.session_state.elapsed += time.time() - st.session_state.start_time
    #        st.session_state.clock_running = False
     #   st.rerun()

#with colC:
 #   if st.button("Reset", key="reset"):
  #      st.session_state.clock_running = False
   #     st.session_state.elapsed = 0
    #    st.session_state.start_time = None
     #   st.rerun()


with col_quarter:
    st.markdown(
        """
        <style>
        .quarter-box {
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 100%;
            padding-top: 35px;  /* adjust this to fine-tune alignment */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='quarter-box'>", unsafe_allow_html=True)
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
            
    with q_col2:
            if st.button("🏁 End Quarter", key="end_quarter"):
                # Get current time from game clock
                current_time = st.session_state.get("current_game_time", "00:00")
                current_quarter = f"Q{st.session_state.quarter}"

                # Log the "END" action
                st.session_state.stats.append([12345, "END", current_time, current_quarter])
                st.success(f"✅ Logged quarter end: {current_quarter} at {current_time}")

                # Pause clock for consistency
                if st.session_state.clock_running:
                    st.session_state.elapsed += time.time() - st.session_state.start_time
                    st.session_state.clock_running = False

                st.rerun()

    # --- Undo Quarter ---
    with q_col3:
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
   #with q_col3:
    #    if st.button("🔄 Reset Game", key="reset_game"):
    #        st.session_state.quarter = 1
    #        st.session_state.max_quarters = 4
    #        st.session_state.stats = []
    #        st.session_state.starters = []
    #        st.session_state.players = []
    #        st.session_state.clock_running = False
    #        st.session_state.elapsed = 0
    #        st.session_state.start_time = None
    #        st.session_state.pending_action = None
    #        st.session_state.previous_quarter = None
    #        st.session_state.previous_elapsed = 0
    #        st.rerun()

        # --- End Quarter Button ---
    



# Three main columns: Players | Actions | Logged Stats
col_players, col_actions, col_stats = st.columns([1, 3, 2], gap="small")

# --- Players on Court ---
with col_players:
    st.subheader("Players")

    if "selected_player" not in st.session_state:
        st.session_state.selected_player = None

    # 🔹 NEW: Always show starters in ascending order
    sort_players()

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
    if st.session_state.selected_player is not None:
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

                                # 🔹 NEW: Keep order consistent after substitution
                                sort_players()

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
from streamlit.components.v1 import html
import pandas as pd
import os

with col_stats:
    st.markdown("<h3 style='margin-top:0;'>📊 Logged Stats</h3>", unsafe_allow_html=True)

    if st.session_state.stats:
        df = pd.DataFrame(st.session_state.stats, columns=["Player", "Action", "Time", "Quarter"])

        # --- Create an HTML table with auto-scroll container ---
        table_html = df.to_html(index=False, classes="stats-table")

        html(f"""
        <style>
        .stats-container {{
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px;
            background-color: #fff;
        }}
        .stats-table {{
            width: 100%;
            border-collapse: collapse;
            font-family: monospace;
            font-size: 14px;
        }}
        .stats-table th {{
            position: sticky;
            top: 0;
            background-color: #f5f5f5;
            border-bottom: 2px solid #999;
            text-align: left;
            padding: 6px;
        }}
        .stats-table td {{
            padding: 4px 6px;
            border-bottom: 1px solid #eee;
        }}
        .stats-table tr:last-child {{
            animation: flash 1s ease-out;
        }}
        @keyframes flash {{
            from {{ background-color: #ffff99; }}
            to {{ background-color: transparent; }}
        }}
        </style>

        <!-- preload scroll position using inline JS before paint -->
        <div id="scroll-container" class="stats-container"
            onscroll="sessionStorage.setItem('scrollPos', this.scrollTop)">
            {table_html}
        </div>

        <script>
        (() => {{
            const container = document.getElementById('scroll-container');
            if (!container) return;

            // read stored scroll position before first paint
            const saved = sessionStorage.getItem('scrollPos');
            if (saved !== null) {{
                container.scrollTop = parseFloat(saved);
            }}

            // decide if user was near bottom (within 80px)
            const nearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 80;

            // slight delay to ensure full height known, then adjust
            requestAnimationFrame(() => {{
                if (nearBottom) {{
                    container.scrollTop = container.scrollHeight;
                }}
            }});
        }})();
        </script>
        """, height=430)

        # --- Undo + Export buttons ---
        undo_col, dl_col = st.columns(2, gap="small")

        with undo_col:
            if st.button("↩️ Undo"):
                st.session_state.stats.pop()
                st.rerun()

        with dl_col:
            team_name = st.session_state.get("team_name", "Unnamed_Team").replace(" ", "_")

            if st.button("💾 Export CSV to Local Folder"):
                raw_data_path = "../data_preprocessing/raw_data"
                gameids = [f for f in os.listdir(raw_data_path)
                           if os.path.isdir(os.path.join(raw_data_path, f)) and f.isdigit()]
                gameids = [int(f) for f in gameids]

                if gameids:
                    latest_gameid = max(gameids)
                    latest_game_dir = os.path.join(raw_data_path, f"{latest_gameid:03d}")

                    # Count how many team folders exist inside latest game id
                    team_folders = [f for f in os.listdir(latest_game_dir)
                                    if os.path.isdir(os.path.join(latest_game_dir, f))]

                    if len(team_folders) >= 2:
                        gameid = latest_gameid + 1
                    else:
                        gameid = latest_gameid
                else:
                    gameid = 1

                gameid = f"{gameid:03d}"
                export_dir = f"{raw_data_path}/{gameid}/{team_name}"
                os.makedirs(export_dir, exist_ok=True)

                file_path = os.path.join(export_dir, "game_stats.csv")
                df.to_csv(file_path, index=False, encoding="utf-8")

                st.success(f"✅ CSV exported successfully to: `{os.path.abspath(file_path)}`")

    else:
        st.info("No stats logged yet.")
