import json
from sqlalchemy import text
from database.connection import get_ro_db

def _execute_query(query: str, params: dict = None):
    db = next(get_ro_db())
    try:
        result = db.execute(text(query), params or {})
        return [dict(row._mapping) for row in result.fetchall()]
    finally:
        db.close()

def get_metadata():
    """Returns available metrics, regions, industries, and stages for AI context."""
    industries = _execute_query("SELECT DISTINCT industry FROM v_accounts WHERE industry IS NOT NULL")
    regions = _execute_query("SELECT DISTINCT region FROM v_accounts WHERE region IS NOT NULL")
    stages = _execute_query("SELECT DISTINCT stage FROM v_opportunities_enriched WHERE stage IS NOT NULL")
    
    return {
        "industries": [r['industry'] for r in industries],
        "regions": [r['region'] for r in regions],
        "stages": [r['stage'] for r in stages],
        "metrics": ["Revenue", "Pipeline Amount", "Win Rate", "Interaction Count"]
    }

def get_pipeline_summary(period: str = None, region: str = None, industry: str = None):
    """Returns pipeline summary grouped by stage, filtering by optional dimensions."""
    query = """
    SELECT stage, COUNT(id) as deal_count, SUM(amount) as total_amount 
    FROM v_opportunities_enriched
    WHERE 1=1
    """
    params = {}
    if industry:
        query += " AND industry = :industry"
        params['industry'] = industry
    if region:
        query += " AND region = :region"
        params['region'] = region
        
    query += " GROUP BY stage ORDER BY total_amount DESC"
    return _execute_query(query, params)

def get_top_accounts(limit: int = 5, industry: str = None, region: str = None):
    """Returns top accounts ordered by annual revenue."""
    query = "SELECT id, name, industry, region, annual_revenue FROM v_accounts WHERE 1=1"
    params = {}
    if industry:
        query += " AND industry = :industry"
        params['industry'] = industry
    if region:
        query += " AND region = :region"
        params['region'] = region
        
    query += " ORDER BY annual_revenue DESC LIMIT :limit"
    params['limit'] = limit
    return _execute_query(query, params)

def get_interaction_metrics(account_name: str = None, interaction_type: str = None):
    """Returns total interactions grouped by type, optionally filtered by account."""
    query = """
    SELECT type, COUNT(id) as interaction_count 
    FROM v_interactions_enriched
    WHERE 1=1
    """
    params = {}
    if account_name:
        query += " AND account_name LIKE :account_name"
        params['account_name'] = f"%{account_name}%"
    if interaction_type:
        query += " AND type = :type"
        params['type'] = interaction_type
        
    query += " GROUP BY type ORDER BY interaction_count DESC"
    return _execute_query(query, params)

def get_sales_trends():
    """Returns aggregated opportunity amounts grouped by month/year."""
    # SQLite datetime functions for month-over-month trend
    query = """
    SELECT strftime('%Y-%m', close_date) as month, SUM(amount) as total_revenue
    FROM v_opportunities_enriched
    WHERE stage = 'Closed Won'
    GROUP BY month
    ORDER BY month DESC
    LIMIT 12
    """
    return _execute_query(query)

def get_dashboard_kpis():
    """Returns high-level business KPIs."""
    total_revenue_query = "SELECT SUM(amount) as rev FROM v_opportunities_enriched WHERE stage = 'Closed Won'"
    pipeline_query = "SELECT SUM(amount) as pipe FROM v_opportunities_enriched WHERE stage NOT IN ('Closed Won', 'Closed Lost')"
    win_rate_query = """
    SELECT 
        CAST(SUM(CASE WHEN stage = 'Closed Won' THEN 1 ELSE 0 END) AS FLOAT) / 
        COUNT(*) * 100 as win_rate_percentage
    FROM v_opportunities_enriched
    """
    
    rev = _execute_query(total_revenue_query)[0]['rev']
    pipe = _execute_query(pipeline_query)[0]['pipe']
    win_rate = _execute_query(win_rate_query)[0]['win_rate_percentage']
    
    return {
        "total_revenue_won": round(rev or 0, 2) if rev else 0.0,
        "total_active_pipeline": round(pipe or 0, 2) if pipe else 0.0,
        "win_rate_percentage": round(win_rate or 0, 2) if win_rate else 0.0
    }

# --- HR ANALYTICS ---

def get_hr_headcount(department_name: str = None):
    """Returns active employee counts grouped by department."""
    query = """
    SELECT department_name, COUNT(id) as employee_count 
    FROM v_employees_enriched
    WHERE 1=1
    """
    params = {}
    if department_name:
        query += " AND department_name = :department_name"
        params['department_name'] = department_name
        
    query += " GROUP BY department_name ORDER BY employee_count DESC"
    return _execute_query(query, params)

def get_hr_payroll_summary(department_name: str = None):
    """Returns total payroll salary grouped by department."""
    query = """
    SELECT department_name, SUM(salary) as total_payroll, AVG(salary) as average_salary
    FROM v_employees_enriched
    WHERE 1=1
    """
    params = {}
    if department_name:
        query += " AND department_name = :department_name"
        params['department_name'] = department_name
        
    query += " GROUP BY department_name ORDER BY total_payroll DESC"
    return _execute_query(query, params)

def get_hr_pto_summary(status: str = None, department_name: str = None):
    """Returns PTO summary grouped by time off type."""
    query = """
    SELECT type as pto_type, SUM(days) as total_days_requested 
    FROM v_timeoff_enriched
    WHERE 1=1
    """
    params = {}
    if status:
        query += " AND status = :status"
        params['status'] = status
    if department_name:
        query += " AND department_name = :department_name"
        params['department_name'] = department_name
        
    query += " GROUP BY type ORDER BY total_days_requested DESC"
    return _execute_query(query, params)

def get_employee_directory(department_name: str = None, role: str = None):
    """Returns a directory of employees including their names, emails, roles, and departments."""
    query = """
    SELECT first_name, last_name, email, role, department_name
    FROM v_employees_enriched
    WHERE 1=1
    """
    params = {}
    if department_name:
        query += " AND department_name LIKE :department_name"
        params['department_name'] = f"%{department_name}%"
    if role:
        # Using LIKE to catch things like 'QA Tester' if they just type 'QA'
        query += " AND role LIKE :role"
        params['role'] = f"%{role}%"
        
    query += " ORDER BY department_name, last_name LIMIT 50"
    return _execute_query(query, params)
