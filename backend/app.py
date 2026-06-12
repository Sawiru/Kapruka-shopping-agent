import os
import httpx
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

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
    limit: int = 10, 
    currency: str = "LKR"
) -> str:
    """
    Search the live Kapruka product catalog by keyword.
    
    Args:
        q: The search keyword or product name (e.g., 'cake', 'flowers').
        category: Optional category filter name.
        min_price: Optional minimum price boundary.
        max_price: Optional maximum price filter.
        in_stock_only: Filter only items in stock. Defaults to True.
        sort: Sort order profile.
        limit: Max integer pagination length. Defaults to 10.
        currency: Pricing currency scale. Defaults to 'LKR'.
    """
    global SESSION_ID
    print(f"\n[SYSTEM] Gemini invoked tool: kapruka_search_products for query: '{q}'...")
    
    if not SESSION_ID:
        return "Error: Local backend failed to establish an active session handshake with Kapruka."

    # Pre-populate all fields comprehensively to satisfy Kapruka's validation models
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
            
            # PARSING STRATEGY: Safely isolate the data block out of the raw text stream chunk
            if "data: " in raw_text:
                # Split at data: and grab everything following it
                clean_json_str = raw_text.split("data: ", 1)[1].strip()
                data = json.loads(clean_json_str)
            else:
                # Fallback if a clean JSON payload arrived directly
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


def run_shopping_assistant():
    print("Initializing Kapruka AI Assistant...")
    
    if not initialize_kapruka_session():
        print("Initialization failed. Terminating engine setup.")
        return

    available_tools = [kapruka_search_products]
    
    system_prompt = (
        "You are 'Kapruka Podi Aiyya', an energetic, warm, and highly resourceful personal "
        "shopping concierge for Kapruka Sri Lanka. "
        "You speak English, fluent Sinhala (සිංහල), or casual Tanglish based exactly on how the user types. "
        "Use the tools provided to find actual live data. Do not make up product names or prices. "
        "When summarizing products, present their names, prices, and IDs clearly so the user can see options. "
        "Always suggest adding a card or flowers if they buy cakes."
    )
    
    chat = client.chats.create(
        model="gemini-3.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=available_tools,
            temperature=0.7
        )
    )
    
    print("\nPodi Aiyya is fully initialized and operational! (Type 'exit' to quit)")
    
    from google.genai.errors import APIError

    while True:
        user_message = input("\nYou: ")
        if user_message.lower() == 'exit':
            break
            
        try:
            response = chat.send_message(user_message)
            print(f"\nAgent: {response.text}")
        except APIError as e:
            if "503" in str(e) or "demand" in str(e).lower():
                print("\n[SYSTEM] Gemini servers are highly occupied right now. Retrying in 2 seconds...")
                time.sleep(2)
                try:
                    response = chat.send_message(user_message)
                    print(f"\nAgent: {response.text}")
                except Exception:
                    print(f"\nAgent: Server load persists. Please try re-typing your prompt!")
            else:
                print(f"\n[SYSTEM] Gemini API Error: {str(e)}")
        except Exception as general_err:
            print(f"\n[SYSTEM] Unexpected Loop Exception: {str(general_err)}")


if __name__ == "__main__":
    run_shopping_assistant()