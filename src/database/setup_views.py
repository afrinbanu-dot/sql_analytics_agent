import sqlite3
from config import config
from observability.logger import logger

def setup_views():
    if not config.DATABASE_URL.startswith("sqlite"):
        logger.warning("This script is currently designed for local SQLite testing.")
        return

    db_path = config.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    logger.info(f"Connected to {db_path}...")

    # 1. v_accounts (Governed view for accounts)
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS v_accounts AS
    SELECT 
        id, 
        name, 
        industry, 
        region, 
        annual_revenue
    FROM accounts;
    """)
    logger.info("Created view: v_accounts")

    # 2. v_opportunities_enriched (Pre-joins opportunities with accounts)
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS v_opportunities_enriched AS
    SELECT 
        o.id,
        o.name AS opportunity_name,
        o.amount,
        o.stage,
        o.close_date,
        a.id AS account_id,
        a.name AS account_name,
        a.industry,
        a.region
    FROM opportunities o
    LEFT JOIN accounts a ON o.account_id = a.id;
    """)
    logger.info("Created view: v_opportunities_enriched")

    # 3. v_interactions_enriched (Pre-joins interactions with opportunities and accounts)
    cursor.execute("DROP VIEW IF EXISTS v_interactions_enriched;")
    cursor.execute("""
    CREATE VIEW v_interactions_enriched AS
    SELECT 
        i.id,
        i.type,
        i.notes,
        i.date AS interaction_date,
        o.id AS opportunity_id,
        o.name AS opportunity_name,
        a.id AS account_id,
        a.name AS account_name,
        a.industry,
        a.region
    FROM interactions i
    LEFT JOIN opportunities o ON i.opportunity_id = o.id
    LEFT JOIN accounts a ON o.account_id = a.id;
    """)
    logger.info("Created view: v_interactions_enriched")

    # --- HR VIEWS ---
    
    # 4. v_departments (Governed view for departments)
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS v_departments AS
    SELECT id, name, budget FROM departments;
    """)
    logger.info("Created view: v_departments")

    # 5. v_employees_enriched (Pre-joins employees with departments)
    cursor.execute("DROP VIEW IF EXISTS v_employees_enriched;")
    cursor.execute("""
    CREATE VIEW v_employees_enriched AS
    SELECT 
        e.id,
        e.first_name,
        e.last_name,
        e.email,
        e.role,
        e.salary,
        e.hire_date,
        d.id AS department_id,
        d.name AS department_name
    FROM employees e
    LEFT JOIN departments d ON e.department_id = d.id;
    """)
    logger.info("Created view: v_employees_enriched")

    # 6. v_timeoff_enriched (Pre-joins time_off with employees and departments)
    cursor.execute("DROP VIEW IF EXISTS v_timeoff_enriched;")
    cursor.execute("""
    CREATE VIEW v_timeoff_enriched AS
    SELECT 
        t.id,
        t.type,
        t.days,
        t.status,
        e.id AS employee_id,
        e.first_name,
        e.last_name,
        d.id AS department_id,
        d.name AS department_name
    FROM time_off t
    LEFT JOIN employees e ON t.employee_id = e.id
    LEFT JOIN departments d ON e.department_id = d.id;
    """)
    logger.info("Created view: v_timeoff_enriched")

    conn.commit()
    conn.close()
    logger.info("All governed views created successfully!")

if __name__ == "__main__":
    setup_views()
