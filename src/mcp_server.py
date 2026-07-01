import sys
import os

# Add the src directory to the path so we can import our database modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
from database.connection import get_ro_db
from sqlalchemy import text
import traceback
import json
import services.analytics as analytics

# Initialize the MCP Server
mcp = FastMCP("SQL Analytics Agent")

@mcp.tool()
def get_database_schema() -> str:
    """Returns the database schema (tables and their columns) so the AI knows what to query."""
    try:
        db = next(get_ro_db())
        # Query SQLite for all tables
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in result.fetchall() if row[0] != 'sqlite_sequence']
        
        schema_info = []
        for table in tables:
            # Get columns for each table
            col_result = db.execute(text(f"PRAGMA table_info({table});"))
            columns = [f"{row[1]} ({row[2]})" for row in col_result.fetchall()]
            schema_info.append(f"Table: {table}\nColumns: {', '.join(columns)}")
            
        return "\n\n".join(schema_info)
    except Exception as e:
        return f"Error fetching schema: {str(e)}\n\nTraceback: {traceback.format_exc()}"

@mcp.tool()
def execute_sql_query(query: str) -> str:
    """Executes a raw SQL query on the SQLite database and returns the result."""
    try:
        query_upper = query.strip().upper()
        if not query_upper.startswith(("SELECT", "PRAGMA")):
            return "Error: Security Violation. Only SELECT and PRAGMA queries are allowed."
        
        # Additional blacklist check
        if any(keyword in query_upper for keyword in ["INSERT ", "UPDATE ", "DELETE ", "DROP ", "ALTER ", "CREATE "]):
             return "Error: Security Violation. Data modification keywords are forbidden."

        db = next(get_ro_db())
        result = db.execute(text(query))
        
        rows = [dict(row._mapping) for row in result.fetchall()]
        return json.dumps(rows, indent=2)
    except Exception as e:
        return f"Failed to execute query: {str(e)}\n[SQL: {query}]"

@mcp.tool()
def get_metadata() -> str:
    """Returns available metrics, regions, industries, and stages for AI context."""
    return json.dumps(analytics.get_metadata(), indent=2)

@mcp.tool()
def get_pipeline_summary(period: str = None, region: str = None, industry: str = None) -> str:
    """Returns pipeline summary grouped by stage, filtering by optional dimensions."""
    return json.dumps(analytics.get_pipeline_summary(period, region, industry), indent=2)

@mcp.tool()
def get_top_accounts(limit: int = 5, industry: str = None, region: str = None) -> str:
    """Returns top accounts ordered by annual revenue."""
    return json.dumps(analytics.get_top_accounts(limit, industry, region), indent=2)

@mcp.tool()
def get_interaction_metrics(account_name: str = None, interaction_type: str = None) -> str:
    """Returns total interactions grouped by type, optionally filtered by account."""
    return json.dumps(analytics.get_interaction_metrics(account_name, interaction_type), indent=2)

@mcp.tool()
def get_sales_trends() -> str:
    """Returns aggregated opportunity amounts grouped by month."""
    return json.dumps(analytics.get_sales_trends(), indent=2)

@mcp.tool()
def get_dashboard_kpis() -> str:
    """Returns high-level business KPIs (total revenue, pipeline, win rate)."""
    return json.dumps(analytics.get_dashboard_kpis(), indent=2)

@mcp.tool()
def get_hr_headcount(department_name: str = None) -> str:
    """Returns active employee counts grouped by department."""
    return json.dumps(analytics.get_hr_headcount(department_name), indent=2)

@mcp.tool()
def get_hr_payroll_summary(department_name: str = None) -> str:
    """Returns total payroll salary grouped by department."""
    return json.dumps(analytics.get_hr_payroll_summary(department_name), indent=2)

@mcp.tool()
def get_hr_pto_summary(status: str = None, department_name: str = None) -> str:
    """Returns PTO summary grouped by time off type."""
    return json.dumps(analytics.get_hr_pto_summary(status, department_name), indent=2)

@mcp.tool()
def get_employee_directory(department_name: str = None, role: str = None) -> str:
    """Returns a directory of employees including their names, emails, roles, and departments."""
    return json.dumps(analytics.get_employee_directory(department_name, role), indent=2)

if __name__ == "__main__":
    # Start the MCP server using Streamable HTTP transport
    # This allows Copilot Studio to connect to it directly via its native MCP Integration
    import uvicorn
    import sys
    print("Starting SQL Analytics MCP Server on http://localhost:5001 ...", file=sys.stderr)
    
    # We expose the ASGI app directly so uvicorn can serve it on our chosen port
    # Copilot Studio explicitly requires Streamable HTTP (not SSE)
    app = mcp.streamable_http_app()
    uvicorn.run(app, host="0.0.0.0", port=5001)
