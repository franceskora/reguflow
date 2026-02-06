import json
import random
import os
from faker import Faker

fake = Faker()
Faker.seed(42)

def generate_data():
    print("--- 🔄 Starting Advanced Data Generation ---")

    customers = {}
    print("... Creating 300 Synthetic Customers")

    # 1. HONEST USERS (The Noise)
    for _ in range(250):
        user_id = fake.uuid4()[:8]
        customers[user_id] = {
            "id": user_id,
            "name": fake.name(),
            "email": fake.email(),
            "ip": fake.ipv4(),
            "wallet": f"0x{fake.sha256()[:10]}",
            "risk_score": random.randint(1, 20),
            "status": "ACTIVE",
            "last_login_location": "London, UK",
            "last_login_time": "10:00 AM",
            "deposit_amount": round(random.uniform(100, 5000), 2)
        }

    # --- CRIME SCENARIO 1: THE IP SYNDICATE ---
    print("... Injecting IP Syndicate")
    suspicious_ip = "192.168.10.5"
    for i in range(5):
        uid = f"bad_ip_{i}"
        customers[uid] = {
            "id": uid, "name": f"Syndicate Mbr {i}", "email": fake.email(),
            "ip": suspicious_ip, # SHARED IP
            "wallet": f"0x{fake.sha256()[:10]}", "risk_score": 95, "status": "FLAGGED",
            "last_login_location": "Lagos, NG", "last_login_time": "09:00 AM",
            "deposit_amount": 500.00
        }

    # --- CRIME SCENARIO 2: THE SMURFS (Structuring) ---
    print("... Injecting Smurfing Ring")
    for i in range(4):
        uid = f"smurf_{i}"
        customers[uid] = {
            "id": uid, "name": f"Smurf Acct {i}", "email": fake.email(),
            "ip": fake.ipv4(), # Different IPs (smart!)
            "wallet": f"0x{fake.sha256()[:10]}", "risk_score": 88, "status": "FLAGGED",
            "last_login_location": "Berlin, DE", "last_login_time": "11:00 AM",
            "deposit_amount": random.randint(9800, 9990) # SUSPICIOUS AMOUNT
        }

    # --- CRIME SCENARIO 3: IMPOSSIBLE TRAVEL ---
    print("... Injecting Impossible Traveler")
    uid = "travel_hacker"
    customers[uid] = {
        "id": uid, "name": "Hacked Account (Travel)", "email": fake.email(),
        "ip": fake.ipv4(), "wallet": f"0x{fake.sha256()[:10]}", 
        "risk_score": 99, "status": "FLAGGED",
        "last_login_location": "Lagos -> London (5min)", # THE EVIDENCE
        "last_login_time": "09:05 AM",
        "deposit_amount": 2000.00
    }

    # --- CRIME SCENARIO 4: BOT SWARM ---
    print("... Injecting Bot Swarm")
    bot_time = "12:00:01.005 PM"
    for i in range(6):
        uid = f"bot_{i}"
        customers[uid] = {
            "id": uid, "name": f"Bot {i}", "email": fake.email(),
            "ip": fake.ipv4(), 
            "wallet": f"0x{fake.sha256()[:10]}", "risk_score": 92, "status": "FLAGGED",
            "last_login_location": "Unknown Proxy",
            "last_login_time": bot_time, # EXACT MATCH
            "deposit_amount": 100.00
        }

    # --- SAVE AGENTS  ---
    agents = {
        "agent_007": {
            "name": "Frances (Agent)", "status": "ACTIVE", "strikes": 0, "history": [],
            "tickets": {
                "ticket_101": {"customer_name": "Alice (VIP)", "risk_score": 10, "history": []},
                "ticket_102": {"customer_name": "Bob (Smurf)", "risk_score": 88, "history": []},
                "ticket_103": {"customer_name": "Charlie (Hacked)", "risk_score": 99, "history": []}
            }
        }
    }

    # SAVE
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, "customers.json"), "w") as f: json.dump(customers, f, indent=2)
    with open(os.path.join(base_dir, "agents.json"), "w") as f: json.dump(agents, f, indent=2)

    print("✅ Advanced Data Generated.")

if __name__ == "__main__":
    generate_data()