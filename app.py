import streamlit as st
import time
import backend_logic  

st.set_page_config(page_title="ReguFlow AEGIS", page_icon="🛡️", layout="wide")

# --- STYLING  ---
st.markdown("""
<style>
    /* 1. Force Dark Background */
    .stApp { background-color: #0e0e0e; color: white; }
    
    /* 2. TARGET ALL BUTTONS SPECIFICALLY */
    div[data-testid="stButton"] > button {
        background-color: #FF444F !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        opacity: 1 !important;
    }
    
    /* 3. Hover State */
    div[data-testid="stButton"] > button:hover {
        background-color: #d3363e !important;
        color: white !important;
        border: 1px solid white !important;
    }

    /* 4. Chat Bubbles */
    .chat-container { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px;}
    .bubble { padding: 10px 15px; border-radius: 10px; max-width: 80%; font-size: 16px; line-height: 1.5; }
    .agent { align-self: flex-end; background-color: #FF444F; color: white; margin-left: auto; text-align: right; }
    .customer { align-self: flex-start; background-color: #333; color: white; margin-right: auto; text-align: left; }
    
    /* 5. Expander (Admin Evidence Locker) */
    .streamlit-expanderHeader {
        background-color: #222 !important;
        color: white !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "user" not in st.session_state:
    st.session_state.user = None

# ================= VIEWS =================

def login_view():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/2/2d/Deriv-logo.png", width=150)
        st.title("ReguFlow Login")
        
        email = st.text_input("Email", placeholder="agent@deriv.com")
        password = st.text_input("Password", type="password", placeholder="agent123")
        
        if st.button("AUTHENTICATE"):
            with st.spinner("Verifying Credentials..."):
                # DIRECT LOGIC CALL
                res = backend_logic.login_logic(email, password)
                
                if res["status"] == "success":
                    st.session_state.user = res
                    st.rerun()
                else:
                    st.error("Invalid Credentials")

def agent_dashboard():
    user = st.session_state.user
    
    # 1. FETCH LATEST DATA DIRECTLY
    try:
        all_agents = backend_logic.get_agents_logic()
        my_data = all_agents.get(user["id"])
    except Exception as e:
        st.error(f"Data Sync Error: {e}")
        return

    # Check Lock Status
    if my_data["status"] == "LOCKED":
        st.error("⛔ ACCOUNT SUSPENDED. PLEASE CONTACT SUPERVISOR.")
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()
        return

    # 2. LAYOUT: Sidebar (Tickets) vs Main (Chat)
    st.subheader(f"🎧 Workspace: {user['name']}")
    
    col_list, col_chat = st.columns([1, 3])
    
    # --- LEFT COLUMN: TICKET LIST ---
    with col_list:
        st.markdown("### 📥 Active Tickets")
        tickets = my_data.get("tickets", {})
        
        # Create a selection list
        ticket_options = list(tickets.keys())
        # Helper to show nice names in the radio button
        def format_ticket(tid):
            t = tickets[tid]
            return f"{t['customer_name']} (Risk: {t['risk_score']})"
            
        selected_tid = st.radio("Select Chat:", ticket_options, format_func=format_ticket)
        
        st.divider()
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()

    # --- RIGHT COLUMN: CHAT WINDOW ---
    with col_chat:
        if selected_tid:
            current_ticket = tickets[selected_tid]
            
            # Header
            st.info(f"Talking to: **{current_ticket['customer_name']}**")
            
            # Chat Container
            chat_html = '<div class="chat-container">'
            for msg in current_ticket["history"]:
                role_class = "agent" if msg["role"] == "agent" else "customer"
                
                # If message was blocked, show it differently
                if msg.get("blocked"):
                    chat_html += f'<div class="bubble agent" style="background-color: #444; color: #ff444f; border: 1px solid red;">🚫 BLOCKED: {msg["text"]}</div>'
                else:
                    chat_html += f'<div class="bubble {role_class}">{msg["text"]}</div>'
            chat_html += '</div>'
            st.markdown(chat_html, unsafe_allow_html=True)

            # Input Area
            with st.form("chat_form", clear_on_submit=True):
                user_msg = st.text_input("Reply...")
                submitted = st.form_submit_button("Send")
                
                if submitted and user_msg:
                    with st.spinner("Sending..."):
                        # DIRECT LOGIC CALL
                        res = backend_logic.send_message_logic(
                            agent_id=user["id"], 
                            ticket_id=selected_tid, 
                            message=user_msg
                        )
                        
                        if res["status"] == "VIOLATION":
                            st.toast(f"❌ BLOCKED: {res['reason']}")
                        elif res["status"] == "LOCKED":
                            st.error("LOCKED")
                        
                        st.rerun() 

def admin_dashboard():
    st.title("👮 Supervisor HQ - AEGIS Core")
    
    tab1, tab2 = st.tabs(["⚠️ Live Risk Feed", "👥 Team Overwatch"])
    
    # --- TAB 1: THE INTELLIGENT FEED ---
    with tab1:
        st.subheader("Detected Financial Crime Patterns")
        
        with st.spinner("AEGIS AI scanning transaction vectors..."):
            try:
                # DIRECT DATA FETCH
                customers = backend_logic.get_customers_logic()
                
                # Filter out banned users
                customers = {uid: u for uid, u in customers.items() if u["status"] != "BANNED"}
                detected_threats = []

                # --- DETECTION 1: IP SYNDICATE ---
                ip_counts = {}
                for uid, u in customers.items():
                    ip_counts[u["ip"]] = ip_counts.get(u["ip"], []) + [u]
                
                for ip, users in ip_counts.items():
                    if len(users) > 3: 
                        detected_threats.append({
                            "title": f"Syndicate Ring (Shared IP)",
                            "desc": f"IP: {ip}",
                            "users": users,
                            "severity": "High",
                            "color": "red"
                        })

                # --- DETECTION 2: SMURFING / STRUCTURING ---
                smurfs = [u for uid, u in customers.items() if 9800 <= u["deposit_amount"] < 10000]
                if len(smurfs) > 2:
                    detected_threats.append({
                        "title": "Structuring / Smurfing Ring",
                        "desc": "Pattern: Multiple deposits just under $10k threshold.",
                        "users": smurfs,
                        "severity": "Medium",
                        "color": "orange"
                    })

                # --- DETECTION 3: IMPOSSIBLE TRAVEL ---
                travelers = [u for uid, u in customers.items() if "->" in u.get("last_login_location", "")]
                if travelers:
                    detected_threats.append({
                        "title": "Impossible Travel Event",
                        "desc": "User logged in from two distant countries in < 5 mins.",
                        "users": travelers,
                        "severity": "Critical",
                        "color": "red"
                    })

                # --- DETECTION 4: BOT SWARM ---
                time_counts = {}
                for uid, u in customers.items():
                    t = u.get("last_login_time")
                    time_counts[t] = time_counts.get(t, []) + [u]
                
                for t, users in time_counts.items():
                    if len(users) > 4: 
                        detected_threats.append({
                            "title": "High-Frequency Botnet",
                            "desc": f"Timestamp Match: {t} (Precision: 1ms)",
                            "users": users,
                            "severity": "High",
                            "color": "red"
                        })

                # --- RENDER CARDS ---
                if not detected_threats:
                    st.success("No threats detected.")
                else:
                    for threat in detected_threats:
                        c = threat["color"]
                        with st.container():
                            st.markdown(f"""
                            <div style="border-left: 5px solid {c}; background-color: #1e1e1e; padding: 15px; margin-bottom: 10px; border-radius: 5px;">
                                <h3 style="margin:0; color: white;">⚠️ {threat['title']}</h3>
                                <p style="margin:0; color: #aaa;">{threat['desc']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            with st.expander(f"View {len(threat['users'])} Linked Accounts"):
                                for u in threat['users']:
                                    st.code(f"USER: {u['name']} | DEPOSIT: ${u['deposit_amount']} | LOC: {u.get('last_login_location', 'N/A')}")
                                
                                ids_to_ban = [u["id"] for u in threat['users']]
                                
                                if st.button(f"🚨 NEUTRALIZE THREAT", key=f"ban_{threat['title']}"):
                                    with st.spinner("Executing Kill Chain..."):
                                        # DIRECT LOGIC CALL
                                        backend_logic.ban_users_logic(ids_to_ban)
                                        
                                        st.toast(f"🚫 {len(ids_to_ban)} Accounts Frozen.", icon="❄️")
                                        time.sleep(1.0) 
                                        st.rerun()

            except Exception as e:
                st.error(f"Scan Error: {e}")

    # --- TAB 2: TEAM OVERWATCH ---
    with tab2:
        st.subheader("Live Agent Governance")
        try:
            # DIRECT DATA FETCH
            agents = backend_logic.get_agents_logic()
            
            for aid, data in agents.items():
                status_icon = "🔒" if data["status"] == "LOCKED" else "🟢"
                with st.expander(f"{status_icon} {data['name']}", expanded=(data["status"] == "LOCKED")):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.markdown("**📜 Full Chat Transcript:**")
                        chat_log = "\n".join(data.get("transcript", ["No chat history yet."]))
                        st.text_area("Logs", chat_log, height=150, disabled=True, key=f"log_{aid}")
                    with c2:
                        st.markdown("**Action Panel:**")
                        if data.get("history"): st.error(f"Last Violation: {data['history'][-1]}")
                        if data["status"] == "LOCKED":
                            if st.button("🔓 UNLOCK AGENT", key=f"btn_{aid}"):
                                # DIRECT LOGIC CALL
                                backend_logic.unlock_agent_logic(aid)
                                
                                st.success("Unlocked!")
                                time.sleep(0.5) 
                                st.rerun()
        except Exception as e:
            st.error(f"Sync Error: {e}")

    st.divider()
    if st.button("Logout", key="logout_admin"):
        st.session_state.user = None
        st.rerun()

# ================= ROUTER =================
if st.session_state.user is None:
    login_view()
elif st.session_state.user["role"] == "agent":
    agent_dashboard()
elif st.session_state.user["role"] == "admin":
    admin_dashboard()