import os
import httpx
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)
# Enable CORS so your React frontend (port 5173) can talk to Flask (port 5000)
CORS(app)

# Initialize the Gemini Client
client = genai.Client()

KAPRUKA_MCP_URL = "https://mcp.kapruka.com/mcp"
SESSION_ID = None

def initialize_kapruka_session():
    """
    Executes the mandatory MCP HTTP lifecycle handshake to claim a stateful session ID.
    """
    global SESSION_ID
    print("Connecting to Kapruka's Live MCP Infrastructure...")
    
    payload = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "kapruka-shopping-agent",
                "version": "1.0.0"
            }
        },
        "id": 1
    }
    
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        with httpx.Client() as sync_client:
            response = sync_client.post(KAPRUKA_MCP_URL, json=payload, headers=headers, timeout=10.0)
            session_id_header = response.headers.get("mcp-session-id")
            
            if session_id_header:
                SESSION_ID = session_id_header
                print(f"[SYSTEM] Stateful MCP Handshake Complete! Session ID locked: {SESSION_ID}")
                return True
            else:
                print(f"[SYSTEM] Handshake failed. Status: {response.status_code}")
                return False
    except Exception as e:
        print(f"[SYSTEM] Network error during initialization: {str(e)}")
        return False


def kapruka_search_products(
    q: str, 
    category: str = None, 
    min_price: float = None, 
    max_price: float = None, 
    in_stock_only: bool = True, 
    sort: str = None, 
    limit: int = 5, 
    currency: str = "LKR"
) -> str:
    """
    Search the live Kapruka product catalog by keyword.
    """
    global SESSION_ID
    print(f"\n[SYSTEM] Gemini invoked tool: kapruka_search_products for query: '{q}'...")
    
    if not SESSION_ID:
        return "Error: Local backend failed to establish an active session handshake with Kapruka."

    arguments_payload = {
        "q": str(q),
        "category": category,
        "min_price": int(min_price) if min_price is not None else None,
        "max_price": int(max_price) if max_price is not None else None,
        "in_stock_only": in_stock_only,
        "sort": sort,
        "limit": int(limit),
        "currency": str(currency)
    }

    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "kapruka_search_products",
            "arguments": arguments_payload
        },
        "id": 2
    }
    
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "mcp-session-id": SESSION_ID,
        "mcp-protocol-version": "2024-11-05",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        with httpx.Client() as sync_client:
            response = sync_client.post(KAPRUKA_MCP_URL, json=payload, headers=headers, timeout=12.0)
            raw_text = response.text
            
            if "data: " in raw_text:
                clean_json_str = raw_text.split("data: ", 1)[1].strip()
                data = json.loads(clean_json_str)
            else:
                data = response.json()
                
            if "error" in data:
                return f"Kapruka MCP internal error: {data['error'].get('message')}"
                
            if "result" in data and "content" in data["result"]:
                content_blocks = data["result"]["content"]
                text_results = "\n".join([block["text"] for block in content_blocks if block.get("type") == "text"])
                print("[SYSTEM] Successfully extracted tool response string!")
                return text_results
            else:
                return f"Kapruka system returned message feedback: {str(data)}"
                
    except Exception as e:
        print(f"[SYSTEM EXCEPTION] Caught crash in extraction logic: {str(e)}")
        return f"Tool execution pipeline encountered an unexpected error: {str(e)}"


# -------------------------------------------------------------
# Core Server & Session Initialization
# -------------------------------------------------------------
print("Initializing Kapruka AI Assistant...")
initialize_kapruka_session()

system_prompt = (
    "You are 'Kapruka Podi Aiyya', an energetic, warm, and highly resourceful personal "
    "shopping concierge for Kapruka Sri Lanka. "
    "You speak English, fluent Sinhala (සිංහල), or casual Tanglish based exactly on how the user types. "
    "Use the tools provided to find actual live data. Do not make up product names or prices. "
    "When summarizing products, present their names, prices, and IDs clearly so the user can see options. "
    "Always suggest adding a card or flowers if they buy cakes."
)

# Instantiate a single, persistent global chat session context
chat_session = client.chats.create(
    model="gemini-3.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=[kapruka_search_products],
        temperature=0.7
    )
)

@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    """
    Receives incoming prompts from your React frontend, feeds them to Gemini, 
    and handles automatic tool execution behind the scenes.
    """
    data = request.json or {}
    user_message = data.get("message", "").strip()
    
    if not user_message:
        return jsonify({"error": "Empty message parameter"}), 400
        
    try:
        # Pass the message into our ongoing persistent global session
        response = chat_session.send_message(user_message)
        return jsonify({"reply": response.text})
        
    except Exception as e:
        print(f"[API ERROR] Chat generation loop fault: {str(e)}")
        return jsonify({
            "reply": "Ayiyoo, Podi Aiyya hit a quick system spike! Give me a second and ask again, macho."
        })


if __name__ == "__main__":
    # Listen universally on port 5000
    print("\nPodi Aiyya is live on the local web socket channel!")
    app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=False)