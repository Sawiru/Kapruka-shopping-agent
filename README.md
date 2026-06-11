# Kapruka Shopping Agent

## Overview

A multi-agent system designed to revolutionize the online shopping experience on Kapruka. This project implements a team of specialized AI agents working collaboratively to understand user needs, browse products, manage carts, and complete purchases autonomously.

## Features

### 🔍 **Smart Search & Discovery**
- **Multi-Criteria Search**: Supports natural language queries including product type, price range, brand, and occasion.
- **Contextual Understanding**: Filters products based on event context (e.g., birthdays, anniversaries).

### 🛒 **Cart Management**
- **Add/Remove Items**: Add new items to the cart or remove existing ones.
- **Update Quantities**: Adjust the number of items in the cart.
- **Cart Review**: View the current cart contents, including item details and subtotals.

### 💳 **Checkout Process**
- **One-Click Purchase**: Complete the checkout process with a single command.
- **Recipient Management**: Supports purchasing for the user or a designated recipient.
- **Secure Handling**: Secure collection of necessary information for order processing.

### 🎨 **User Experience**
- **Interactive Chat Interface**: Natural and intuitive conversation flow.
- **Proactive Assistance**: Agents offer suggestions and ask clarifying questions when needed.

## Architecture

The system uses a **Multi-Agent Architecture** with four specialized agents:

1.  **🛍️ Search Agent**:
    - **Role**: Scans the Kapruka website for relevant products.
    - **Function**: Interprets user search queries and finds matching items.

2.  **🛒 Cart Agent**:
    - **Role**: Manages the user's shopping cart.
    - **Function**: Adds, removes, and updates items; provides cart summaries.

3.  **🎁 Purchaser Agent**:
    - **Role**: Handles the checkout process.
    - **Function**: Collects recipient information and finalizes the purchase.

4.  **✨ Orchestrator Agent**:
    - **Role**: The central controller of the system.
    - **Function**: Analyzes user intent, coordinates other agents, and maintains conversation flow.

## Getting Started

### Prerequisites
- Python 3.8+

### Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd Kapruka-shopping-agent
    ```

2.  (Optional) Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Usage

Run the application:
```bash`
python main.py
```

Start interacting with the agent via the chat interface.

## Sample Interactions

### Adding an Item
```
User: I want to buy a birthday gift for my mom, maybe a cake
Orchestrator: Searching for birthday cakes on Kapruka... Found 5 options.
Search Agent: [Lists available cakes with prices]
Orchestrator: Which one would you like to add to your cart?
User: The chocolate fudge cake for Rs. 4000
Cart Agent: Added 'Chocolate Fudge Cake' to cart. Total: Rs. 4000
```

### Purchasing an Item
```
User: Buy the cake for me
Purchaser Agent: Okay! I'll proceed with the purchase. Is this for you or someone else?
User: For my mom
Purchaser Agent: What's her name and contact number?
... (collects details) ...
Purchaser Agent: Order complete! Your mom will receive the cake tomorrow.
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
