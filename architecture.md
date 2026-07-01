# AI SQL Analytics Agent Architecture

This diagram illustrates the complete, end-to-end architecture of your enterprise-grade AI SQL Analytics Agent. It highlights the flow of data from the end-user in Microsoft Teams, through the AI and API layers, down to the governed SQL views we implemented.

```mermaid
graph TD
    %% Define Styling
    classDef user fill:#3b82f6,stroke:#1d4ed8,color:white,stroke-width:2px,rx:10px,ry:10px;
    classDef cloud fill:#8b5cf6,stroke:#6d28d9,color:white,stroke-width:2px,rx:10px,ry:10px;
    classDef api fill:#10b981,stroke:#047857,color:white,stroke-width:2px,rx:10px,ry:10px;
    classDef db fill:#f59e0b,stroke:#b45309,color:white,stroke-width:2px,rx:10px,ry:10px;
    classDef view fill:#ef4444,stroke:#b91c1c,color:white,stroke-width:2px,rx:10px,ry:10px;

    %% Nodes
    User["👤 Microsoft Teams<br/>(End User)"]:::user
    
    subgraph "Cloud Layer (Microsoft)"
        AzureBot["🤖 Azure Bot Framework"]:::cloud
        PowerAutomate["⚡ Power Automate<br/>(Webhook)"]:::cloud
        Copilot["🧠 Copilot Studio<br/>(AI Brain)"]:::cloud
    end

    subgraph "Local Python Backend"
        FastAPI["🚀 FastAPI Server<br/>(app.py - Port 5000)"]:::api
        MCPServer["🔌 MCP Server<br/>(mcp_server.py - Port 5001)"]:::api
        Analytics["⚙️ Analytics Service<br/>(Layer 3: Abstraction)"]:::api
        Engine["🔒 SQLAlchemy Engine<br/>(mode=ro)"]:::api
    end

    subgraph "Local Database Layer"
        Views["🛡️ Layer 2: Governed Views<br/>(v_accounts, v_opportunities...)"]:::view
        RawDB["🗄️ Layer 1: Raw Tables<br/>(enterprise_crm.db)"]:::db
    end

    %% Chat Flow
    User -- "1. Asks Natural Language Question" --> AzureBot
    AzureBot -- "2. Forwards Payload" --> FastAPI
    FastAPI -- "3. HTTP POST Message" --> PowerAutomate
    PowerAutomate -- "4. Triggers Agent" --> Copilot

    %% Tool Execution Flow
    Copilot -- "5. Identifies Intent &<br/>Calls OpenAPI Tool" --> MCPServer
    MCPServer -- "6. Triggers Python Function" --> Analytics
    Analytics -- "7. Executes Parameterized SQL" --> Engine
    
    %% Database Flow
    Engine -- "8. Read-Only Query" --> Views
    Views -. "9. Pre-Joined Data" .-> RawDB

    %% Return Flow
    Views -- "10. Returns JSON Data" --> Analytics
    Analytics -- "11. Returns Structured Result" --> MCPServer
    MCPServer -- "12. Returns HTTP 200" --> Copilot
    Copilot -- "13. Generates Text Answer" --> PowerAutomate
    PowerAutomate -- "14. Returns HTTP Response" --> FastAPI
    FastAPI -- "15. Sends Adaptive Card/Text" --> AzureBot
    AzureBot -- "16. Displays Final Answer" --> User
```

## Key Architectural Highlights

1. **Perfect Abstraction (Layer 3)**: Copilot Studio never writes raw SQL. It simply calls predefined OpenAPI endpoints (e.g., `/api/tools/top_accounts`), passing safe parameters like `industry="Healthcare"`.
2. **Strict Data Governance (Layer 2)**: The Python code only queries explicitly allowed SQL Views (e.g., `v_opportunities_enriched`), completely isolating the AI from your raw production tables.
3. **Physical Security Lock**: Even if an unauthorized query was somehow injected, the SQLAlchemy Engine is physically locked in Read-Only mode (`?mode=ro`). The database will aggressively reject any modification attempts.
