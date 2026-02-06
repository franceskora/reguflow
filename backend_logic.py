import json
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# 1. SETUP THE BRAIN
load_dotenv() 

# Check if key exists
api_key = os.getenv("AIML_API_KEY")
if not api_key:
    
    try:
        import streamlit as st
        api_key = st.secrets["AIML_API_KEY"]
    except:
        print("⚠️ WARNING: AIML_API_KEY not found in .env or secrets!")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.aimlapi.com/v1",
)

# --- HELPER FUNCTIONS ---
def load_json(filename):
    # Get the folder where THIS script lives
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Combine it with the filename
    file_path = os.path.join(base_dir, filename)

    with open(file_path, "r") as f:
        return json.load(f)

# --- LOGIC FUNCTIONS (Formerly Endpoints) ---

def health_check():
    return {"status": "Active", "system": "ReguFlow Brain"}

# 1. LOGIN logic
def login_logic(email, password):
    # Agent Login
    if email == "agent@deriv.com" and password == "agent123":
        return {"status": "success", "role": "agent", "id": "agent_007", "name": "Frances (Agent)"}
    # Admin Login
    if email == "admin@deriv.com" and password == "admin123":
        return {"status": "success", "role": "admin", "id": "admin_01", "name": "Chief Compliance Officer"}
    
    return {"status": "error", "message": "Invalid Credentials"}

# 2. GET DATA logic
def get_customers_logic():
    return load_json("customers.json")

def get_agents_logic():
    return load_json("agents.json")

# 3. CHAT MONITOR logic
def send_message_logic(agent_id, ticket_id, message):
    agents = load_json("agents.json")
    agent = agents.get(agent_id)
    if not agent: 
        return {"status": "ERROR", "reason": "Agent not found"}
    
    # Ensure Transcript Exists (For Admin View)
    if "transcript" not in agent: agent["transcript"] = []

    # 1. GET SPECIFIC TICKET
    ticket = agent["tickets"].get(ticket_id)
    if not ticket: 
        return {"status": "ERROR", "reason": "Ticket not found"}

    # 2. CHECK LOCK STATUS
    if agent.get("status") == "LOCKED": 
        return {"status": "LOCKED", "reason": "Account Suspended"}

    # 3. AI JUDGE 
    system_prompt = """
    You are a strict Compliance Officer monitoring a financial support agent.
    Analyze the agent's message for the following violations:

    1. SECURITY (HIGH): Asking for passwords, 2FA codes, keys, or credit card details.
    2. GUARANTEES (HIGH): Promising profits, "risk-free" returns, or guaranteed gains.
    3. EVASION (HIGH): Suggesting VPNs to bypass geoblocking, helping hide funds, or bypassing KYC.
    4. ADVICE (LOW): Giving financial advice (e.g., "You should buy Bitcoin now") instead of technical support.
    5. TOXICITY (LOW): Swearing, insults, or extreme rudeness.

    If a violation is found, set "is_violation" to true.
    "HIGH" severity = Instant Lock. "LOW" severity = Strike.
    
    Output JSON only: {"is_violation": bool, "severity": "HIGH"|"LOW", "reason": "Short explanation (e.g. 'Promised guaranteed returns')"}
    """
    try:
        check = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": message}],
            temperature=0.0
        )
        decision = json.loads(check.choices[0].message.content.replace("```json", "").replace("```", ""))
    except:
        decision = {"is_violation": False}

    
    
    # A. Log to Master Transcript (For Supervisor)
    timestamp = time.strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] [Ticket: {ticket['customer_name']}] AGENT: {message}"
    agent["transcript"].append(log_entry)

    # 5. HANDLE VIOLATION
    if decision.get("is_violation"):
        # Log Violation details
        violation_entry = f"[{decision['severity']}] {decision['reason']} (Ticket: {ticket_id})"
        agent["history"].append(violation_entry)
        agent["transcript"].append(f"❌ BLOCKED: {decision['reason']}") # Show block in transcript
        
        # Log to Ticket (So Agent sees red bubble)
        ticket["history"].append({"role": "agent", "text": message, "blocked": True})
        
        if decision["severity"] == "HIGH":
            agent["status"] = "LOCKED"
        else:
            agent["strikes"] = agent.get("strikes", 0) + 1
            if agent["strikes"] >= 3: agent["status"] = "LOCKED"
        
        # Save
        base_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_dir, "agents.json"), "w") as f: json.dump(agents, f, indent=2)

        return {"status": "VIOLATION", "reason": decision["reason"]}

    # 6. IF SAFE -> REPLY
    # Log to Ticket History (For Agent View)
    ticket["history"].append({"role": "agent", "text": message})

    # Simulate Reply
    sim_res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"You are {ticket['customer_name']}. Reply to the agent naturally (under 15 words)."},
            {"role": "user", "content": message}
        ]
    )
    customer_reply = sim_res.choices[0].message.content
    
    # Log Customer Reply to Ticket & Transcript
    ticket["history"].append({"role": "customer", "text": customer_reply})
    agent["transcript"].append(f"[{timestamp}] CUSTOMER: {customer_reply}")
    
    # Save File
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, "agents.json"), "w") as f: json.dump(agents, f, indent=2)
    
    return {"status": "APPROVED", "customer_reply": customer_reply}

# 4. AEGIS INVESTIGATOR logic
def get_investigation_data_logic():
    customers = load_json("customers.json")
    
    nodes = []
    edges = []
    
    # 1. Create the "Suspicious Server"
    suspicious_ip = "192.168.10.5"
    nodes.append({
        "data": {
            "id": "bad_server", 
            "label": f"SUSPICIOUS: {suspicious_ip}", 
            "color": "#00FFFF", 
            "size": 40,         
            "symbolType": "square"
        }
    })

    # 2. Create the "Safe Gateway"
    nodes.append({
        "data": {
            "id": "safe_server", 
            "label": "Public Gateway (Safe)", 
            "color": "#00FF00", 
            "size": 40, 
            "symbolType": "triangle"
        }
    })
    
    # 3. Populate the Clusters
    count_safe = 0
    
    for uid, user in customers.items():
        # --- CLUSTER A: THE BAD GUYS ---
        if user["ip"] == suspicious_ip or user["status"] == "FLAGGED":
            nodes.append({
                "data": {
                    "id": uid, "label": f"⚠️ {user['name']}", 
                    "color": "#FF0000", "size": 25 
                }
            })
            edges.append({
                "data": {
                    "source": uid, "target": "bad_server", 
                    "color": "#FF444F", "label": "matches_ip"
                }
            })
            
        # --- CLUSTER B: THE NORMAL TRAFFIC ---
        elif count_safe < 30:
            nodes.append({
                "data": {
                    "id": uid, "label": user['name'], 
                    "color": "#555", "size": 10 
                }
            })
            edges.append({
                "data": {
                    "source": uid, "target": "safe_server", 
                    "color": "#333", "label": "verified"
                }
            })
            count_safe += 1

    return {"nodes": nodes, "edges": edges}

# 5. UNLOCK AGENT logic
def unlock_agent_logic(agent_id):
    agents = load_json("agents.json")
    
    if agent_id in agents:
        agents[agent_id]["status"] = "ACTIVE"
        agents[agent_id]["strikes"] = 0
        agents[agent_id]["history"].append("[ADMIN ACTION] Account Unlocked")
        
        # Save back to file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "agents.json")
        with open(file_path, "w") as f:
            json.dump(agents, f, indent=2)
            
        return {"status": "success", "message": f"{agent_id} Unlocked"}
    
    return {"status": "error", "message": "Agent not found"}

# 6. BAN CLUSTER logic
def ban_users_logic(user_ids_list):
    customers = load_json("customers.json")
    
    banned_count = 0
    for uid in user_ids_list:
        if uid in customers:
            customers[uid]["status"] = "BANNED"
            customers[uid]["risk_score"] = 100 
            banned_count += 1
            
    # Save changes
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, "customers.json"), "w") as f:
        json.dump(customers, f, indent=2)
        
    return {"status": "success", "banned": banned_count}