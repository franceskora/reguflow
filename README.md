# 🛡️ ReguFlow AEGIS: AI-Powered Financial Compliance System

![Python](https://img.shields.io/badge/Python-3.9-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green) ![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red) ![OpenAI](https://img.shields.io/badge/AI-GPT--4o-orange)

## 🚀 The Problem

Financial institutions lose **$4.2 Billion** annually to fraud and fines.

1.  **Human Error:** Support agents accidentally leak PII (passwords/cards) or violate compliance rules.
2.  **Organized Crime:** Syndicates use "Smurfing" and "Bot Swarms" to wash money, often faster than human analysts can detect.

## 💡 The Solution: AEGIS

AEGIS (Automated Enforcement & Governance Intelligence System) is a dual-layer defense engine:

1.  **The Guardrail (Real-time NLP):** Intercepts agent messages _before_ they are sent. It uses LLMs to detect PII leakage or non-compliant promises (e.g., "Guaranteed Returns") and blocks the message instantly.
2.  **The Hunter (Graph Analysis):** Scans the ledger for behavioral patterns (Shared IPs, Velocity checks, Structuring) to identify and ban fraud rings automatically.

## 🛠️ Tech Stack

- **Backend:** FastAPI (High-performance API handling chat streams and fraud detection logic).
- **Frontend:** Streamlit (Reactive dashboard for Agents and Supervisors).
- **AI Engine:** OpenAI GPT-4o (Zero-shot classification for compliance violations).
- **Data Simulation:** Faker (Generates realistic synthetic "Smurfing" and "Bot" attack patterns for demo).

## ⚙️ How It Works (The Logic)

### 1. The Compliance Guardrail

Every message passes through a `pydantic` validation layer and an AI compliance judge.

```python
# Logic: If Severity is HIGH, instant BAN. If LOW, add strike.
if decision["severity"] == "HIGH":
    agent["status"] = "LOCKED"
    return {"status": "VIOLATION", "reason": "PII Leakage Detected"}
```
